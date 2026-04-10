from profiles.effects import get_effect_modules
from profiles.conveyors import get_conveyors
import argparse
import json
import os
import sys

from profiles import Settings, EffectNameOverride
from profiles.items import get_items, purge_items
from profiles.machines import (
    get_machines,
)
from profiles.recipes import (
    get_recipes,
    get_recipes_from_fluid_extractors,
    get_recipes_from_item_categories,
    get_recipes_from_nuclear_reactor,
    purge_recipes,
)
from profiles.research import get_research
from profiles.utils import dump, purge_optional_fields
from profiles.validate import validate_items, validate_machines, validate_recipes


def construct_profile(data: list) -> dict:
    r = {}
    for c in data:
        nc = (
            c["NativeClass"]
            .replace("/Script/CoreUObject.Class'/Script/FactoryGame.FG", "")
            .replace("'", "")
        )
        # print(nc)
        r[nc] = c["Classes"]

    items = []
    for k, v in r.items():
        if "Descriptor" in k or k in [
            "AmmoTypeProjectile",
            "AmmoTypeSpreadshot",
            "AmmoTypeInstantHit",
        ]:
            items += get_items(v)
    recipes = get_recipes(r["Recipe"], items)
    recipes += get_recipes_from_fluid_extractors(r["BuildableResourceExtractor"])
    recipes += get_recipes_from_fluid_extractors(r["BuildableFrackingExtractor"])
    recipes += get_recipes_from_item_categories(items)
    recipes += get_recipes_from_nuclear_reactor(
        r["BuildableGeneratorNuclear"], r["ItemDescriptorNuclearFuel"]
    )

    effectmodules = get_effect_modules()
    machines = []
    # BuildableManufacturerVariablePower
    for part in [
        "BuildableResourceExtractor",
        "BuildableManufacturer",
        "BuildableFrackingExtractor",
        "BuildableGeneratorNuclear",
        "BuildableManufacturerVariablePower",
    ]:
        tmpmachines, tmpem = get_machines(r.get(part, {}))
        machines += tmpmachines
        effectmodules += tmpem

    conveyors = get_conveyors(r["BuildableConveyorBelt"])

    recipes = purge_recipes(recipes, machines)
    items = purge_items(items, recipes)

    research = get_research(r["Schematic"], recipes)

    settings = Settings(
        defaultDuration=60,
        allRecipesUnlocked=True,
        limitations=None,
        effectNameOverride=EffectNameOverride(
            speed="Overclocking", productivity="Summerslooping"
        ),
    )

    validate_recipes(recipes)
    validate_items(items, recipes)
    validate_machines(machines, recipes)

    return purge_optional_fields(
        {
            "id": "satisfactory",
            "name": "Generated Satisfactory Profile",
            "items": dump(items),
            "recipes": dump(recipes),
            "machines": dump(machines),
            "machineEffects": dump(effectmodules),
            "research": dump(research),
            "conveyors": dump(conveyors),
            "settings": dump(settings),
        }
    )


def main():
    parser = argparse.ArgumentParser(
        description="YABFC Profile Generator for Satisfactory dumps"
    )
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="profile.json")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Could not open file at: '{args.input}'")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-16") as f:
        dump = json.load(f)
    profile = construct_profile(dump)
    with open(args.output, "w") as f:
        json.dump(profile, f, indent=4)


if __name__ == "__main__":
    main()
