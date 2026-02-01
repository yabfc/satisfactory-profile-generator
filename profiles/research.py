from profiles import Research, UnlockRecipe
from profiles.utils import uncamelcase
import re


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
        deps = []
        for d in r["mSchematicDependencies"]:
            if d["Class"] == "BP_SchematicPurchasedDependency_C":
                deps += [
                    uncamelcase(a.split(".")[-1].split("_C'")[0])
                    for a in d["mSchematics"].split(",")
                ]
        unlocks = []
        if len(deps) == 0:
            deps = None
        if len(unlocks_recipes) != 0:
            unlocks.append(UnlockRecipe("recipe", unlocks_recipes))
        out.append(Research(id, name, False, unlocks, deps))
    return out
