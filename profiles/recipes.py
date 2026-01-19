from unicodedata import category
from profiles import BaseItemIo, Recipe, Item
from profiles.utils import uncamelcase, unclassname
import re

ItemIOPattern = re.compile(
    r"/(Parts|Resource/[^/]+|Equipment|Equipment/[^/]+|Buildable/[^/]+|Buildable/[^/]+/[^/]+)/[^/]+/(Desc_|BP_EquipmentDescriptor|BP_EqDesc|BP_ItemDescriptor)(?P<name>[^\.]+)[^']+'.*?Amount=(?P<amount>\d+)"
)
RessourcePattern = re.compile(r"/Resource/[^/]+/[^/]+/Desc_(?P<name>[^\.]+)[^']+'")


def get_base_item_io(iio: str, itemtype: dict) -> list[BaseItemIo]:
    return [
        # the fluid amount is for some reason multiplied by 100
        BaseItemIo(
            uncamelcase(match.group("name")),
            # switch default case here to building maybe
            itemtype.get(uncamelcase(match.group("name")), "item"),
            int(match.group("amount"))
            if itemtype.get(uncamelcase(match.group("name")), "item") == "item"
            else int(match.group("amount")) // 100,
        )
        for match in ItemIOPattern.finditer(iio)
    ]


def get_recipes_from_item_categories(items: list[Item]) -> list[Recipe]:
    out = []
    for item in items:
        if item.category not in ["raw-ressource", "organic"] and "waste" not in item.id:
            continue
        category = ""
        if item.category == "raw-ressource":
            category = "miner"
        elif item.category == "organic":
            category = "manual-harvest"
        else:
            category = "reactor-TODO"
        
        out.append(
            Recipe(
                item.id,
                item.name,
                [],
                [BaseItemIo(item.id, item.type, 1)],
                1,
                category,
                10,
                True,
                None,
            )
        )
    return out


def get_recipes_from_fluid_extractors(machines: list[dict]) -> list[Recipe]:
    out = []
    for machine in machines:
        if machine.get("mAllowedResources", "") == "":
            continue
        machine_id = unclassname(machine["ClassName"], ["Build_"])
        fluids = [
            uncamelcase(r.group("name"))
            for r in RessourcePattern.finditer(machine["mAllowedResources"])
        ]
        amount = int(machine.get("mItemsPerCycle", 0)) // 1000
        for fluid in fluids:
            out.append(
                Recipe(
                    f"{fluid}-{machine_id}",
                    None,
                    [],
                    [BaseItemIo(fluid, "fluid", amount)],
                    1,
                    machine_id,
                    10,
                    True,
                    None,
                )
            )
    return out


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
