import json
import sys
import os
import dataclasses
import re

from profiles.items import get_items
from profiles.recipes import (
    get_recipes,
    get_recipes_from_fluid_extractors,
    get_recipes_from_raw_minables,
)
from profiles.research import get_research
from profiles.utils import purge_optional_fields, dump
from profiles.machines import get_machines, OVERCLOCKING, UNDERCLOCKING, SUMMERSLOOPING


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
        if "ItemDescriptor" in k or k in ["ResourceDescriptor", "EquipmentDescriptor"]:
            items += get_items(v)
    recipes = get_recipes(r["Recipe"], items)
    recipes += get_recipes_from_fluid_extractors(r["BuildableResourceExtractor"])
    recipes += get_recipes_from_fluid_extractors(r["BuildableFrackingExtractor"])
    recipes += get_recipes_from_raw_minables(items)

    effectmodules = [OVERCLOCKING, UNDERCLOCKING, SUMMERSLOOPING]
    research = get_research(r["Schematic"])
    machines = []
    # BuildableManufacturerVariablePower
    for part in [
        "BuildableResourceExtractor",
        "BuildableManufacturer",
        "BuildableFrackingExtractor",
    ]:
        tmpmachines, tmpem = get_machines(r.get(part, {}))
        machines += tmpmachines
        effectmodules += tmpem

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
