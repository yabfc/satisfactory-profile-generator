from profiles import (
    Machine,
    MachineFeature,
    EffectModule,
    VariableModifier,
    FixedModifier,
)
from profiles.utils import unclassname

OVERCLOCKING = EffectModule(
    "overclocking",
    [
        VariableModifier("speed", 1, 2.5, True, None),
        FixedModifier("power", 1.321929, False, "exponential"),
    ],
    False,
    True,
    None,
)
UNDERCLOCKING = EffectModule(
    "underclocking",
    [
        VariableModifier("speed", 0, 1, True, None),
        FixedModifier("power", 1.321929, False, "exponential"),
    ],
    False,
    True,
    None,
)

OVERCLOCKING_LIN = EffectModule(
    "overclocking-lin",
    [
        VariableModifier("speed", 1, 2.5, True, None),
        FixedModifier("power", 2.5, False, None),
    ],
    False,
    True,
    True,
)

UNDERCLOCKING_LIN = EffectModule(
    "underclocking-lin",
    [
        VariableModifier("speed", 0, 1, True, None),
        FixedModifier("power", 1, False, None),
    ],
    False,
    True,
    True,
)

SUMMERSLOOPING = EffectModule(
    "summerslooping",
    [
        FixedModifier("productivity", 2, False, None),
        FixedModifier("power", 4, False, None),
    ],
    False,
    True,
    None,
)


def get_machines(old_machines: list[dict]) -> tuple[list[Machine], list[EffectModule]]:
    machines = []
    modules = []
    for machine in old_machines:
        id = unclassname(machine["ClassName"], ["Build_", "Desc_"])
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
                        "crafting-speed", 0, [f"crafting-speed-{id}"], None, True, None
                    )
                )
                modules.append(
                    EffectModule(
                        f"crafting-speed-{id}",
                        [FixedModifier("speed", int(1 // cycle), False, None)],
                        True,
                        True,
                        True,
                    )
                )
        if machine.get("mProductionShardSlotSize", "") != "":
            sloops = int(machine["mProductionShardSlotSize"])
            if sloops > 0:
                features.append(
                    MachineFeature(
                        "summerslooping", sloops, ["summerslooping"], None, None, None
                    )
                )
        underclock = "underclocking"
        overclock = "overclocking"

        # power scales linear with reactors
        if id == "generator-nuclear":
            underclock = "underclocking-lin"
            overclock = "overclocking-lin"

        features.append(
            MachineFeature(overclock, 0, [overclock], [underclock], None, True)
        )
        features.append(
            MachineFeature(underclock, 0, [underclock], [overclock], None, True)
        )

        consumption = int(float(machine.get("mPowerConsumption", "0.0")) * 1000 * 1000)
        machines.append(Machine(id, categories, consumption, features, True, None))
    return (machines, modules)
