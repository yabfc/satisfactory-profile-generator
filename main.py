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
    Research,
    UnlockRecipe,
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


def removeAll(src: str, to_remove: list[str]) -> str:
    for rep in to_remove:
        src = src.replace(rep, "")
    return src


def purge_optional_fields(obj):
    # if name is not present, it's an implicit null
    # => we can delete the field when it's null
    if isinstance(obj, dict):
        return {
            k: purge_optional_fields(v)
            for k, v in obj.items()
            if not (k in ["name", "craftable"] and v is None)
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


def unclassname(src: str, classes: list[str]) -> str:
    for c in classes:
        src = re.sub(rf"{c}(.*?)_C$", r"\1", src)
    return uncamelcase(src).replace("_", "-").replace("--", "-")


def get_recipes(recipes: list[dict], items: list[Item]) -> list[Recipe]:
    itemtype = {}
    for i in items:
        itemtype[i.id] = i.type

    out = []
    for r in recipes:
        id = unclassname(r["ClassName"], ["Recipe_"])
        if (
            id in ["trading-post", "candy-cane", "snowball"]
            or "fireworks" in id
            or "foundation" in id
        ):
            continue
        if "FICSMAS" in r["mDisplayName"] or "Braided" in r["mDisplayName"]:
            continue
        if r["mProducedIn"] == "" or "FGBuildGun" in r["mProducedIn"]:
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
        if category[0] == "build-gun" and "beam" in id:
            continue

        if "alternate" in id:
            prio = 20
        elif "converter" in category:
            prio = 40
        elif "packager" in category:
            prio = 30
        else:
            prio = 10

        if category in [["equipment-workshop"], ["build-gun"]]:
            craftable = False
        else:
            craftable = None

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
                craftable,
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
        id = unclassname(i["ClassName"], ["Desc_", "BP_EquipmentDescriptor"])
        # print(i["ClassName"])
        name = i["mDisplayName"].replace("\u202f", "").replace("\u2122", "")
        if name == "":
            continue

        # maybe find a better way for the categorizing
        if "ore-" in id or id in ["coal", "sam", "quartz-crystal"]:
            category = "raw-resource"
        elif (
            "iron-" in id
            or "copper-" in id
            or "ingot" in id
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


def get_research(research: list) -> list[Research]:
    out = []
    for r in research:
        if r["mType"] in ["EST_ResourceSink", "EST_Custom"]:
            continue
        id = uncamelcase(r["ClassName"]).removesuffix("-c")
        name = r["mDisplayName"].replace(".", "").replace("\u00a0", "")
        match r["mType"]:
            case "EST_Milestone":
                name += f" (Tier {r['mTechTier']})"
            case "EST_Alternate":
                name += " Harddrive"
            case "EST_Tutorial":
                pass
            case _:
                name += " (MAM)"
        unlocks = []
        for u in r["mUnlocks"]:
            if u["Class"] == "BP_UnlockRecipe_C":
                unlocks += [
                    uncamelcase(
                        re.findall(r"/Recipe_(?P<name>[^\.]+).*$", a.split("'")[1])[0]
                    )
                    for a in u["mRecipes"].split(",")
                    if "Shared/Customization/" not in a
                ]
        deps = []
        for d in r["mSchematicDependencies"]:
            if d["Class"] == "BP_SchematicPurchasedDependency_C":
                deps += [
                    uncamelcase(a.split(".")[-1].split("_C'")[0])
                    for a in d["mSchematics"].split(",")
                ]
        if len(deps) == 0:
            deps = None
        if len(unlocks) == 0:
            continue
        out.append(Research(id, name, [UnlockRecipe("recipe", unlocks)], deps))
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
        if "ItemDescriptor" in k or k in ["ResourceDescriptor", "EquipmentDescriptor"]:
            items += get_items(v)
    recipes = get_recipes(r["Recipe"], items)

    effectmodules = []
    research = get_research(r["Schematic"])

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
