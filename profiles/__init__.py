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
    name: str | None
    inp: list[BaseItemIo] = dataclasses.field(metadata={"alias": "in"})
    out: list[BaseItemIo]
    duration: int
    category: str
    priority: int
    available: bool
    craftable: bool | None


@dataclasses.dataclass
class Item:
    id: str
    name: str | None
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
    valueScaling: None | Literal["exponential"]


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
    name: str
    unlocks: list[UnlockType]
    prerequisites: list[str] | None


StackSizeDict = {
    "SS_ONE": 1,
    "SS_SMALL": 50,
    "SS_MEDIUM": 100,
    "SS_BIG": 200,
    "SS_HUGE": 500,
    "SS_FLUID": 0,
}
