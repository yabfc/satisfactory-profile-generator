from profiles import (
    EffectModule,
    Modifier,
    ModifiableEffectModule,
    SteppedEffectModule,
)


CLOCKING = ModifiableEffectModule(
    "over-underclocking",
    [
        Modifier("speed", 1, None),
        Modifier("power", 1.321929, "exponential"),
    ],
    name="Over/Underclocking",
    minValue=0,
    maxValue=2.5,
)

# Used when overclocking generators
CLOCKING_LIN = ModifiableEffectModule(
    "over-underclocking-lin",
    [
        Modifier("speed", 1, None),
        Modifier("power", 1, None),
    ],
    name="Over/Underclocking (linear)",
    minValue=0,
    maxValue=2.5,
)


def get_summersloop_module(step: float) -> SteppedEffectModule:
    return SteppedEffectModule(
        f"summerslooping-{step}",
        [
            Modifier("productivity", 1, None),
            Modifier("power", 2, None),
        ],
        name="Summerslooping",
        minValue=1,
        maxValue=2,
        step=1 / step,
    )


def get_effect_modules() -> list[EffectModule]:
    out = [CLOCKING, CLOCKING_LIN]
    for sloop_steps in [1, 2, 4]:
        out.append(get_summersloop_module(sloop_steps))

    return out
