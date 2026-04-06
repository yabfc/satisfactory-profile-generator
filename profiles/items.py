from profiles.utils import unclassname
from profiles import Item, StackSizeDict, Recipe


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
        id = unclassname(
            i["ClassName"],
            ["Desc_", "BP_EquipmentDescriptor", "BP_ItemDescriptor", "BP_EqDesc"],
        )
        name = i["mDisplayName"].replace("\u202f", "").replace("\u2122", "")
        if name == "" and id == "":
            continue

        # maybe find a better way for the categorizing
        if "ore-" in id or id in ["coal", "sam", "raw-quartz", "sulfur", "stone"]:
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
            continue
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
            "berry",
            "wood",
            "alien-remains",
            "leaves",
            "somersloop",
            "mercer-sphere",
            "crystal-mk3",
            "crystal-mk2",
            "crystal",
            "shroom",
            "nut",
            "mycelia",
            "hog-parts",
            "stinger-parts",
            "hatcher-parts",
            "spitter-parts",
        ]:
            category = "organic"
        elif "packaged-" in id:
            category = "packaged-resource"
        else:
            category = "advanced-product"

        # special treatment for candy cane basher
        if name == "Candy Cane Basher":
            id = "candy-cane-basher"

        # we don't need to save the name if the id is the same
        if id == name.replace(" ", "-").lower() or name == "":
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


def purge_items(items: list[Item], recipes: list[Recipe]) -> list[Item]:
    item_io = set(
        [item.id for r in recipes for item in r.out]
        + [item.id for r in recipes for item in r.inp]
    )
    return [i for i in items if i.id in item_io]
