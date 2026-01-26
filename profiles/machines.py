from profiles import (
    Machine,
    MachineFeature,
    EffectModule,
    VariableModifier,
    FixedModifier,
)
import re
from profiles.utils import uncamelcase, unclassname

OVERCLOCKING = EffectModule(
    "overclocking",
    [
        VariableModifier("speed", 1, 2.5, True, False, None),
        FixedModifier("power", 1.321929, False, False, "exponential"),
    ],
    False,
    True,
)
UNDERCLOCKING = EffectModule(
    "underclocking",
    [
        VariableModifier("speed", 0, 1, True, False, None),
        FixedModifier("power", 1.321929, False, False, "exponential"),
    ],
    False,
    True,
)

SUMMERSLOOPING = EffectModule(
    "summerslooping",
    [
        FixedModifier("speed", 2, False, True, None),
        FixedModifier("power", 4, False, False, None),
    ],
    False,
    True,
)


def get_machines(old_machines: list[dict]) -> tuple[list[Machine], list[EffectModule]]:
    machines = []
    modules = []
    for machine in old_machines:
        id = unclassname(machine["ClassName"], ["Build_"])
        categories = []
        if machine.get("mExtractorTypeName", "") == "Miner":
            categories = ["miner"]
        else:
            categories = [id]
        features = []

        # only relevant for miner mk.(>1)
        if machine.get("mExtractCycleTime", "") != "":
            cycle = float(machine["mExtractCycleTime"])
            if cycle != 1:
                features.append(
                    MachineFeature(
                        "crafting-speed", 0, [f"crafting-speed-{id}"], None, True
                    )
                )
                modules.append(
                    EffectModule(
                        f"crafting-speed-{id}",
                        [FixedModifier("speed", int(1 // cycle), False, True, None)],
                        True,
                        True,
                    )
                )
        if machine.get("mProductionShardSlotSize", "") != "":
            sloops = int(machine["mProductionShardSlotSize"])
            if sloops > 0:
                features.append(
                    MachineFeature(
                        "summerslooping", sloops, ["summerslooping"], None, None
                    )
                )
        features.append(
            MachineFeature("overclocking", 3, ["overclocking"], ["underclocking"], None)
        )
        features.append(
            MachineFeature(
                "underclocking", 0, ["underclocking"], ["overclocking"], None
            )
        )

        consumption = int(float(machine.get("mPowerConsumption", "0.0")) * 1000 * 1000)
        machines.append(Machine(id, categories, consumption, features, True, None))
    return (machines, modules)
