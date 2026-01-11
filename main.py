import json
import sys
import os
import dataclasses
import re

from models import (
    BaseItemIo,
    Recipe,
    Item,
    StackSizeDict,
    ItemIOPattern,
)


def dump(obj):
    if dataclasses.is_dataclass(obj):
        out = {}
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            if val is None:
                continue
            key = f.metadata.get("alias", f.name)
            out[key] = dump(val)
        return out
    if isinstance(obj, list):
        return [dump(e) for e in obj]
    if isinstance(obj, dict):
        return {k: dump(v) for k, v in obj.items()}
    return obj


def purge_optional_fields(obj):
    # if name is not present, it's an implicit null
    # => we can delete the field when it's null
    if isinstance(obj, dict):
        return {
            k: purge_optional_fields(v)
            for k, v in obj.items()
            if not (k == "name" and v is None)
        }
    elif isinstance(obj, list):
        return [purge_optional_fields(x) for x in obj]
    return obj


def get_base_item_io(iio: str, itemtype: dict) -> list[BaseItemIo]:
    return [
        # the fluid amount is for some reason multiplied by 100
        BaseItemIo(
            uncamelcase(match.group("name")),
            itemtype.get(uncamelcase(match.group("name")), "invalid-type"),
            int(match.group("amount"))
            if itemtype.get(uncamelcase(match.group("name")), "") == "item"
            else int(match.group("amount")) // 100,
        )
        for match in ItemIOPattern.finditer(iio)
    ]


def uncamelcase(src: str) -> str:
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", src)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", s)
    return s.lower().replace("_", "-")


def unclassname(src: str, c: str) -> str:
    return uncamelcase(re.sub(rf"{c}_(.*?)_C$", r"\1", src).replace("_", "-")).replace(
        "--", "-"
    )


def get_recipes(recipes: list[dict], items: list[Item]) -> list[Recipe]:
    itemtype = {}
    for i in items:
        itemtype[i.id] = i.type

    out = []
    for r in recipes:
        id = unclassname(r["ClassName"], "Recipe")
        if r["mProducedIn"] == "":
            category = ["build-gun"]
        elif "FGBuildGun" in r["mProducedIn"]:
            category = ["build-gun"]
        else:
            category = [
                uncamelcase(
                    p.rsplit("/", 1)[-1]
                    .split(".")[-1]
                    .replace("Build_", "")
                    .replace("BP_", "")
                    .replace("_C", "")
                )
                for p in re.findall(r'"([^"]+)"', r["mProducedIn"])
            ]

            category = [
                t
                for t in category
                if t
                not in [
                    "fgbuildable-automated-work-bench",
                    "workshop-component",
                    "work-bench-component",
                    "automated-work-bench",
                ]
            ]
        if len(category) == 0:
            category = ["equipment-workshop"]

        if "alternate" in id:
            prio = 20
        elif "converter" in category:
            prio = 40
        elif "packager" in category:
            prio = 30
        else:
            prio = 10

        out.append(
            Recipe(
                id,
                r["mDisplayName"].replace("\u202f", "").replace("\u2122", ""),
                get_base_item_io(r["mIngredients"], itemtype),
                get_base_item_io(r["mProduct"], itemtype),
                int(float(r["mManufactoringDuration"])),
                category[0],
                prio,
                True,
            )
        )
    return out


def get_items(items: list[dict]) -> list[Item]:
    out = []
    # RF_INVALID are mostly buildings, maybe change item to building
    forms = {
        "RF_GAS": "fluid",
        "RF_LIQUID": "fluid",
        "RF_SOLID": "item",
        "RF_INVALID": "item",
    }
    for i in items:
        if "mForm" not in i.keys():
            continue
        id = unclassname(i["ClassName"], "Desc")
        name = i["mDisplayName"].replace("\u202f", "").replace("\u2122", "")
        if name == "":
            continue

        # maybe find a better way for the categorizing
        if "-ore" in id or id in ["coal", "sam", "quartz-crystal"]:
            category = "raw-resource"
        elif (
            "iron-" in id
            or "copper-" in id
            or id
            in [
                "iron-rod",
                "iron-plate",
            ]
        ):
            category = "basic-product"
        elif id in [
            "zipline",
            "rifle",
            "rebar-gun",
            "object-scanner",
            "nobelisk-detonator",
            "medicinal-inhaler",
            "jetpack",
            "hoverpack",
            "hazmat-suit",
            "gas-mask",
            "cup",
            "color-cartridge",
            "blade-runners",
            "beacon",
            "boom-box",
        ]:
            category = "equipment"
        elif id in [
            "adaptive-control-unit",
            "versatile-framework",
            "thermal-propulsion-rocket",
            "magnetic-field-generator",
            "smart-plating",
            "assembly-director-system",
            "automated-wiring",
            "ballistic-warp-drive",
        ]:
            category = "space-elevator"
        elif id in [
            "biomass",
            "alien-protein",
            "paleberry",
            "wood",
            "alien-remains",
            "leaves",
            "somersloop",
            "mercer-sphere",
            "power-slug",
            "flower-petals",
            "beryl-nut",
        ]:
            category = "organic"
        elif "packaged-" in id:
            category = "packaged-ressource"
        else:
            category = "advanced-product"

        # we don't need to save the name if the id is the same
        if id == name.replace(" ", "-").lower():
            name = None

        out.append(
            Item(
                id,
                name,
                forms[i["mForm"]],
                category,
                StackSizeDict[i["mStackSize"]],
            )
        )
    return out


def construct_profile(data: list) -> dict:
    r = {}
    for c in data:
        if "Buildable" in c["NativeClass"]:
            continue
        nc = (
            c["NativeClass"]
            .replace("/Script/CoreUObject.Class'/Script/FactoryGame.FG", "")
            .replace("'", "")
        )
        r[nc] = c["Classes"]

    items = []
    for k, v in r.items():
        if "ItemDescriptor" in k or ["ResourceDescriptor" in k]:
            items += get_items(v)
    recipes = get_recipes(r["Recipe"], items)

    effectmodules = []
    research = []

    machines = []
    for part in ["furnace", "assembling-machine"]:
        if part not in r.keys():
            continue
        tmpmachines, tmpeffectmodules = []
        effectmodules += tmpeffectmodules
        machines += tmpmachines
    return purge_optional_fields(
        {
            "id": "satisfactory",
            "name": "Generated Satisfactory Profile",
            "items": dump(items),
            "recipes": dump(recipes),
            "machines": dump(machines),
            "machineEffects": dump(effectmodules),
            "research": dump(research),
        }
    )


def main():
    if len(sys.argv) < 2:
        print("Please specify a dump file")
        sys.exit(1)
    fp = sys.argv[1]
    if not os.path.exists(fp):
        print(f"Could not open file at: '{fp}'")
        sys.exit(1)
    with open(fp, "r", encoding="utf-16") as f:
        dump = json.load(f)
    profile = construct_profile(dump)
    with open("out.json", "w") as f:
        json.dump(profile, f, indent=4)


if __name__ == "__main__":
    main()
