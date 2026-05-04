from profiles import (
    EffectModule,
    Modifier,
    ModifiableEffectModule,
    SteppedEffectModule,
)


CLOCKING = ModifiableEffectModule(
    "over-underclocking",
    [
        Modifier("speed", 1),
        Modifier("power", 1.321929, valueScaling="exponential"),
    ],
    name="Over/Underclocking",
    minValue=-1,
    maxValue=1.5,
    displayOffset=1,
)

# Used when overclocking generators
CLOCKING_LIN = ModifiableEffectModule(
    "over-underclocking-lin",
    [
        Modifier("speed", 1),
        Modifier("power", 1),
    ],
    name="Over/Underclocking (linear)",
    minValue=-1,
    maxValue=1.5,
    displayOffset=1,
)


def get_summersloop_module(step: float) -> SteppedEffectModule:
    return SteppedEffectModule(
        f"summerslooping-{step}",
        [
            Modifier("productivity", 1),
            Modifier("power", 2),
        ],
        name="Summerslooping",
        minValue=0,
        maxValue=1,
        step=1 / step,
        displayOffset=1,
    )


def get_effect_modules() -> list[EffectModule]:
    out: list[EffectModule] = [CLOCKING, CLOCKING_LIN]
    for sloop_steps in [1, 2, 4]:
        out.append(get_summersloop_module(sloop_steps))

    return out
