from profiles import (
    Machine,
    MachineFeature,
    EffectModule,
    Modifier,
    FixedEffectModule,
)
from profiles.utils import unclassname


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
                        "crafting-speed", 0, [f"crafting-speed-{id}"], True, None
                    )
                )
                modules.append(
                    FixedEffectModule(
                        f"crafting-speed-{id}",
                        [Modifier("speed", int(1 // cycle), None)],
                        hidden=True,
                    )
                )
        if machine.get("mProductionShardSlotSize", "") != "":
            sloops = int(machine["mProductionShardSlotSize"])
            if sloops > 0:
                features.append(
                    MachineFeature(
                        "summerslooping",
                        1,
                        [f"summerslooping-{sloops}"],
                        None,
                        None,
                    )
                )
        clocking = "over-underclocking"

        # power scales linear with reactors
        if id == "generator-nuclear":
            clocking += "-lin"

        features.append(MachineFeature(clocking, 1, [clocking], None, True))

        consumption = int(float(machine.get("mPowerConsumption", "0.0")) * 1000 * 1000)
        machines.append(Machine(id, categories, consumption, features, True, None))
    return (machines, modules)
