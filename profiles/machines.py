from profiles import Machine, MachineFeature, EffectModule, Modifier
import re
from profiles.utils import uncamelcase, unclassname

OVERCLOCKING = EffectModule(
    "overclocking",
    [
        Modifier("speed", 1.5, True, False, None),
        Modifier("power", 1.321929, False, False, "exponential"),
    ],
    True,
    True,
)
UNDERCLOCKING = EffectModule(
    "underclocking",
    [
        Modifier("speed", 0.5, True, False, None),
        Modifier("power", 1.321929, False, False, "exponential"),
    ],
    True,
    True,
)

SUMMERSLOOPING = EffectModule(
    "summerslooping",
    [Modifier("speed", 2, False, True, None), Modifier("power", 5, False, False, None)],
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
                    MachineFeature("crafting-speed", 0, [f"crafting-speed-{id}"])
                )
                modules.append(
                    EffectModule(
                        f"crafting-speed-{id}",
                        [Modifier("speed", int(1 // cycle), False, True, None)],
                        True,
                        True,
                    )
                )
        if machine.get("mProductionShardSlotSize", "") != "":
            sloops = int(machine["mProductionShardSlotSize"])
            features.append(
                MachineFeature("summerslooping", sloops, ["summerslooping"])
            )
        features.append(MachineFeature("overclocking", 3, ["overclocking"]))
        features.append(MachineFeature("underclocking", 0, ["underclocking"]))

        consumption = int(float(machine.get("mPowerConsumption", "0.0")) * 1000 * 1000)
        machines.append(Machine(id, categories, consumption, features, True, None))
    return (machines, modules)
