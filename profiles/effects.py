from profiles import (
    EffectModule,
    FixedModifier,
    ModifiableEffectModule,
    SteppedEffectModule,
)


CLOCKING = ModifiableEffectModule(
    "over-underclocking",
    [
        FixedModifier("speed", 1, False, None),
        FixedModifier("power", 1.321929, False, "exponential"),
    ],
    name="Over/Underclocking",
    minValue=0,
    maxValue=2.5,
)

# Used when overclocking generators
CLOCKING_LIN = ModifiableEffectModule(
    "over-underclocking-lin",
    [
        FixedModifier("speed", 1, False, None),
        FixedModifier("power", 1, False, None),
    ],
    name="Over/Underclocking (linear)",
    minValue=0,
    maxValue=2.5,
)


def get_summersloop_module(step: float) -> SteppedEffectModule:
    return SteppedEffectModule(
        f"summerslooping-{step}",
        [
            FixedModifier("productivity", 1, False, None),
            FixedModifier("power", 2, False, None),
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
