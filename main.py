from profiles import Settings
import json
import os
import sys
import argparse

from profiles.items import get_items
from profiles.machines import (
    OVERCLOCKING,
    OVERCLOCKING_LIN,
    SUMMERSLOOPING,
    UNDERCLOCKING,
    UNDERCLOCKING_LIN,
    get_machines,
)
from profiles.recipes import (
    get_recipes,
    get_recipes_from_fluid_extractors,
    get_recipes_from_item_categories,
    get_recipes_from_nuclear_reactor,
)
from profiles.research import get_research
from profiles.utils import dump, purge_optional_fields
from profiles.validate import validate_items, validate_machines, validate_recipes


def construct_profile(data: list, resource_costs: dict) -> dict:
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
    recipes = get_recipes(r["Recipe"], items, resource_costs)

    for t in ["BuildableResourceExtractor", "BuildableFrackingExtractor"]:
        recipes += get_recipes_from_fluid_extractors(r[t], resource_costs)

    recipes += get_recipes_from_item_categories(items, resource_costs)
    recipes += get_recipes_from_nuclear_reactor(
        r["BuildableGeneratorNuclear"], r["ItemDescriptorNuclearFuel"]
    )

    effectmodules = [
        OVERCLOCKING,
        UNDERCLOCKING,
        SUMMERSLOOPING,
        OVERCLOCKING_LIN,
        UNDERCLOCKING_LIN,
    ]
    research = get_research(r["Schematic"])
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

    settings = Settings(
        default_duration=60, all_recipes_unlocked=True, limitations=None
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
            "settings": dump(settings),
        }
    )


def main():
    parser = argparse.ArgumentParser(
        description="YABFC Profile Generator for Satisfactory dumps"
    )
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="profile.json")
    parser.add_argument("-r", "--resource-costs", default="resource-costs.json")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Could not open file at: '{args.input}'")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-16") as f:
        dump = json.load(f)
    with open(args.resource_costs, "r") as f:
        costs = json.load(f)
    profile = construct_profile(dump, costs)
    with open(args.output, "w") as f:
        json.dump(profile, f, indent=4)


if __name__ == "__main__":
    main()
