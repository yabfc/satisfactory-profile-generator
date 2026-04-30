from profiles import Machine, Modifier, MachineFeature, FixedEffectModule

IMPURE = FixedEffectModule("node-impure", [Modifier("speed", 0.5)])
NORMAL = FixedEffectModule("node-normal", [Modifier("speed", 1)])
PURE = FixedEffectModule("node-pure", [Modifier("speed", 2)])


def add_node_purity_features(
    machines: list[Machine],
) -> tuple[list[Machine], list[FixedEffectModule]]:
    modules = [IMPURE, NORMAL, PURE]
    module_ids = [module.id for module in modules]
    for machine in machines:
        if (
            "miner" in machine.recipeCategories
            or "oil-pump" in machine.recipeCategories
            or "fracking-extractor" in machine.recipeCategories
        ):
            machine.features.append(
                MachineFeature("quality-tiers", 0, module_ids, hidden=True)
            )

    return (machines, modules)
