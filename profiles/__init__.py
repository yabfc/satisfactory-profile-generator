import dataclasses
from typing import Literal, Union


@dataclasses.dataclass
class EffectNameOverride:
    speed: str
    productivity: str


@dataclasses.dataclass
class Settings:
    defaultDuration: int
    allRecipesUnlocked: bool
    limitations: list[str] | None
    effectNameOverride: EffectNameOverride


@dataclasses.dataclass
class BaseItemIo:
    id: str
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
    hidden: bool | None
    modifiable: bool | None


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
    valueScaling: None | Literal["exponential"]


@dataclasses.dataclass
class BaseEffectModule:
    id: str
    modifiers: list[Modifier]
    available: bool = dataclasses.field(default=True, kw_only=True)
    hidden: bool | None = dataclasses.field(default=None, kw_only=True)
    name: str | None = dataclasses.field(default=None, kw_only=True)
    singleUse: bool | None = dataclasses.field(default=True, kw_only=True)


@dataclasses.dataclass
class FixedEffectModule(BaseEffectModule):
    type: Literal["fixed"] = "fixed"


@dataclasses.dataclass
class ModifiableEffectModule(BaseEffectModule):
    minValue: float
    maxValue: float
    type: Literal["modifiable"] = "modifiable"


@dataclasses.dataclass
class SteppedEffectModule(BaseEffectModule):
    minValue: float
    maxValue: float
    step: float
    type: Literal["stepped"] = "stepped"


EffectModule = Union[FixedEffectModule, ModifiableEffectModule, SteppedEffectModule]


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


@dataclasses.dataclass
class Logistic:
    id: str
    type: str
    speed: float


StackSizeDict = {
    "SS_ONE": 1,
    "SS_SMALL": 50,
    "SS_MEDIUM": 100,
    "SS_BIG": 200,
    "SS_HUGE": 500,
    "SS_FLUID": 0,
}
