from profiles import Research, UnlockRecipe, RessourcePattern
from profiles.utils import uncamelcase
import re


SE1 = Research(
    "space-elevator-1",
    "Space Elevator - Platform",
    False,
    [],
    ["schematic-tutorial5", "schematic-2-1"],
)
SE2 = Research(
    "space-elevator-2",
    "Space Elevator - Framework",
    False,
    [],
    ["space-elevator-1", "schematic-3-4", "schematic-4-1"],
)
SE3 = Research(
    "space-elevator-3",
    "Space Elevator - Systems",
    False,
    [],
    ["space-elevator-2", "schematic-5-2", "schematic-8-1"],
)
# SE4 only unlocks the employee of the month award in the awesome shop
SE4 = Research(
    "space-elevator-4",
    "Space Elevator - Propulsion",
    False,
    [],
    [
        "space-elevator-3",
        "schematic-7-5",
        "schematic-8-4",
        "schematic-8-5",
        "schematic-9-1",
    ],
)


def get_research(research: list) -> list[Research]:
    out = [SE1, SE2, SE3, SE4]
    for r in research:
        if r["mType"] in ["EST_ResourceSink"]:
            continue
        id = uncamelcase(r["ClassName"]).removesuffix("-c")

        # skip AWESOME shop unlockables
        if id.startswith("cbg-"):
            continue
        name = r["mDisplayName"].replace(".", "").replace("\u00a0", "")
        tier = None
        match r["mType"]:
            case "EST_Milestone":
                name += f" (Tier {r['mTechTier']})"
                tier = int(r["mTechTier"])
            case "EST_Alternate":
                name += " Harddrive"
            case "EST_Tutorial":
                pass
            case _:
                name += " (MAM)"
        unlocks_recipes = []
        for unlocks in r["mUnlocks"]:
            if unlocks["Class"] == "BP_UnlockRecipe_C":
                unlocks_recipes += [
                    uncamelcase(
                        re.findall(r"/Recipe_(?P<name>[^\.]+).*$", a.split("'")[1])[0]
                    )
                    for a in unlocks["mRecipes"].split(",")
                    if "Shared/Customization/" not in a
                ]
            if unlocks["Class"] == "BP_UnlockScannableResource_C":
                unlocks_recipes += [
                    uncamelcase(r.group("name"))
                    for r in RessourcePattern.finditer(
                        unlocks["mResourcesToAddToScanner"]
                    )
                ]
        deps = []
        for d in r["mSchematicDependencies"]:
            if d["Class"] == "BP_SchematicPurchasedDependency_C":
                deps += [
                    uncamelcase(a.split(".")[-1].split("_C'")[0])
                    for a in d["mSchematics"].split(",")
                ]
        # len(deps) => MAM depends on tech tier
        if tier or (len(deps) == 0 and r.get("mTechTier", "") != ""):
            tier = int(r["mTechTier"])
            if 2 < tier <= 4:
                deps.append("space-elevator-1")
            elif tier <= 6:
                deps.append("space-elevator-2")
            elif tier <= 8:
                deps.append("space-elevator-3")

        unlocks = []
        if len(deps) == 0:
            deps = None
        if len(unlocks_recipes) != 0:
            unlocks.append(UnlockRecipe("recipe", unlocks_recipes))
        out.append(Research(id, name, False, unlocks, deps))
    return out
