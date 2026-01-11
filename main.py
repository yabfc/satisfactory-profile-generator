import json
import sys
import os
import dataclasses
from typing import Union, Literal
import re


@dataclasses.dataclass
class BaseItemIo:
    id: str
    type: str
    amount: int


@dataclasses.dataclass
class Recipe:
    id: str
    inp: list[BaseItemIo] = dataclasses.field(metadata={"alias": "in"})
    out: list[BaseItemIo]
    duration: int
    category: str
    priority: int
    available: bool


@dataclasses.dataclass
class Item:
    id: str
    type: str
    category: str
    stackSize: int


@dataclasses.dataclass
class MachineFeature:
    id: str
    itemSlots: int
    effectPerSlot: list[str]


@dataclasses.dataclass
class Machine:
    id: str
    recipeCategories: list[str]
    requiredPower: int
    features: list[MachineFeature]
    available: bool
    limitations: list[str] | None


@dataclasses.dataclass
class Modifier:
    id: str
    value: float
    modifiable: bool
    onlyOutputScales: bool


@dataclasses.dataclass
class EffectModule:
    id: str
    modifiers: list[Modifier]
    perSlot: bool
    available: bool


@dataclasses.dataclass
class UnlockRecipe:
    type: Literal["recipe"]
    ids: list[str]


UnlockType = Union[UnlockRecipe]


@dataclasses.dataclass
class Research:
    id: str
    unlocks: list[UnlockType]
    prerequisites: list[str] | None


StackSizeDict = {
    "SS_ONE": 1,
    "SS_SMALL": 50,
    "SS_MEDIUM": 100,
    "SS_BIG": 200,
    "SS_HUGE": 500,
    "SS_FLUID": 0
}

ItemIOPattern = re.compile(
    r"/Parts/(?P<name>[^/]+)/Desc_[^']+'.*?Amount=(?P<amount>\d+)"
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


def get_base_item_io(iio: str) -> list[BaseItemIo]:
    return [
        BaseItemIo(
            uncamelcase(match.group("name")),
            "item",
            int(match.group("amount")),
        )
        for match in ItemIOPattern.finditer(iio)
    ]


def uncamelcase(src: str) -> str:
    return "-".join(re.sub("([A-Z]+)", r" \1", src).split()).lower()


def unclassname(src: str, c: str) -> str:
    return uncamelcase(re.sub(rf"{c}_(.*?)_C$", r"\1", src).replace("_", "-")).replace("--", "-")

def get_recipes(recipes: list[dict]) -> list[Recipe]:
    out = []
    for r in recipes:
        out.append(
            Recipe(
                unclassname(r["ClassName"], "Recipe"),
                get_base_item_io(r["mIngredients"]),
                get_base_item_io(r["mProduct"]),
                int(float(r["mManufactoringDuration"])),
                "bogus",
                10,
                True,
            )
        )
    return out


def get_items(items: list[dict]) -> list[Item]:
    out = []
    for i in items:
        out.append(Item(unclassname(i["ClassName"], "Desc"),"","",StackSizeDict[i["mStackSize"]]))
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

    for k, v in r.items():
        print(k)
    recipes = get_recipes(r["Recipe"])
    items = []
    for k, v in r.items():
        if "ItemDescriptor" in k:
            print(k)
            items += get_items(v)
    effectmodules = []
    research = []

    machines = []
    for part in ["furnace", "assembling-machine"]:
        if part not in r.keys():
            continue
        tmpmachines, tmpeffectmodules = []
        effectmodules += tmpeffectmodules
        machines += tmpmachines
    return {
        "id": "satisfactory",
        "name": "Generated Satisfactory Profile",
        "items": dump(items),
        "recipes": dump(recipes),
        "machines": dump(machines),
        "machineEffects": dump(effectmodules),
        "research": dump(research),
    }


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
