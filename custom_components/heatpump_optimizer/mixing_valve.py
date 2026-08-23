"""The mixing valve: what actually lets a buffer tank store anything.

Backlog item 29. Kept free of Home Assistant imports so it can be unit-tested
directly, the same way `manual_plan` and `external_heat` are.

**Why this module exists.** The thermal model hard-wires the heat drawn from the
buffer tank to equal the heat the pump puts in -- `q_rad + q_floor` is
`rad_fraction * P` plus `(1 - rad_fraction) * P`, which is `P` exactly -- so the
tank can only ever cool. That is a fair model of a system with *no valve*, where
whatever the pump makes goes straight to the emitters.

A mixing valve is precisely the component that breaks it. The valve throttles
delivery to what the house is asking for, and the surplus has nowhere to go but
the tank.

Measured, this distinction is the whole feature. With the draw merely decoupled
from supply but no valve, emitter demand at a 40 C tank and 21 C rooms is around
23 kW against roughly 15 kW of pump output, so the tank drains no matter what the
optimizer does: in a spike it used 0.00 K of 30 K of available headroom and
produced a plan byte-identical to one that could not store at all.
"""
from __future__ import annotations

from dataclasses import dataclass

# --- Modes -----------------------------------------------------------------
#
# Four, not three. A "dumb" valve the user sets by hand behaves differently from
# one the integration can read, which behaves differently again from one it can
# command -- and the difference matters, because it decides whether the plan can
# rely on the valve position or merely observe it.
MODE_NONE = "none"
MODE_MANUAL = "manual"
MODE_SMART_READ = "smart_read"
MODE_SMART_WRITE = "smart_write"

MODES: tuple[str, ...] = (
    MODE_NONE,
    MODE_MANUAL,
    MODE_SMART_READ,
    MODE_SMART_WRITE,
)

#: The subset offered in the UI today. `smart_write` needs an actuation path --
#: commanding the valve's own controller -- and is added to this tuple when that
#: lands. Offering a mode that cannot do what its name says is worse than not
#: offering it, and adding an option later needs no migration because nobody can
#: have selected it.
SELECTABLE_MODES: tuple[str, ...] = (
    MODE_NONE,
    MODE_MANUAL,
    MODE_SMART_READ,
)

#: Modes in which a valve exists at all, and delivery is therefore throttled.
THROTTLING_MODES: frozenset[str] = frozenset(
    {MODE_MANUAL, MODE_SMART_READ, MODE_SMART_WRITE}
)

#: How much of the remaining gap to the target the valve closes in one step.
#: A real valve is a PI loop; this is the proportional part, and it is
#: deliberately less than 1 so the model does not pretend the house reaches its
#: target instantly.
DEFAULT_VALVE_GAIN = 0.5


def is_throttling(mode: str | None) -> bool:
    """Whether this mode has a valve that limits delivery."""
    return (mode or MODE_NONE) in THROTTLING_MODES


def delivery_demand(
    *,
    indoor_temp: float,
    target_temp: float,
    outdoor_temp: float,
    heat_loss_coefficient: float,
    thermal_mass: float,
    dt_hours: float,
    gain: float = DEFAULT_VALVE_GAIN,
) -> float:
    """Heat the valve will pass this step to hold `target_temp`, in kW.

    Two terms: replace what the house is losing, and close some of the gap to
    the target. Never negative -- a valve can shut, but it cannot cool a house.

    The behaviour that matters for storage is what happens *at* the target.
    Once the house is there the second term vanishes and delivery falls back to
    the standing loss, which is less than the pump is making. From that moment
    the surplus goes to the tank. That is why a dumb valve set at the maximum
    permitted temperature fills both stores in the right order: the slab first,
    because it stores at room temperature and costs no COP, and the tank only
    with what is left over.
    """
    if dt_hours <= 0.0:
        return 0.0
    steady = heat_loss_coefficient * (indoor_temp - outdoor_temp)
    gap = (target_temp - indoor_temp) * thermal_mass * max(gain, 0.0) / dt_hours
    return max(0.0, steady + gap)


@dataclass(frozen=True)
class TargetRecommendation:
    """A suggested valve target, and why."""

    target: float
    reason: str


def recommend_target(
    *,
    comfort_min: float,
    comfort_max: float,
    price_ratio: float | None = None,
    tank_is_useful: bool = False,
) -> TargetRecommendation:
    """What to set a dumb valve to.

    For most houses the answer is **high**, and the reasoning is worth stating
    because it is not obvious. A high target keeps the valve open until the house
    reaches its comfort ceiling, so the slab charges first -- roughly 15 kWh
    across a 3 K band, stored at room temperature with *no COP penalty at all*.
    Only then does the valve throttle and the tank take the overflow, and tank
    heat is stored hot and therefore costs COP. Slab first, tank second, is the
    cheap order; setting the target low inverts it.

    A narrow comfort band is the case where that reasoning weakens: there is
    little slab to charge, so the tank is doing most of the work either way.

    Note what a high target gives up. The valve was the thing preventing
    overshoot, and at the ceiling it is no longer doing that -- what stands
    between a solver mistake and an overheated house is the optimizer's comfort
    handling, which is a *soft penalty* and prices violations rather than
    refusing them. Hence the recommendation stays at the comfort ceiling and
    never above it.
    """
    band = max(comfort_max - comfort_min, 0.0)
    if band < 1.0:
        return TargetRecommendation(
            target=comfort_max,
            reason=(
                "Your comfort band is too narrow to store much in the building "
                "itself, so the tank does most of the work. The target still "
                "goes to the top of the band."
            ),
        )
    if price_ratio is not None and price_ratio > 0.9:
        return TargetRecommendation(
            target=comfort_max,
            reason=(
                "Prices are nearly flat, so there is little to gain from storing "
                "heat at all. The target is at the top of the band, which costs "
                "nothing and leaves the building free to coast."
            ),
        )
    return TargetRecommendation(
        target=comfort_max,
        reason=(
            "Set to the top of your comfort band. The building charges first, "
            "which is free, and the tank takes only the surplus, which is not. "
            "Note that the valve is then no longer limiting indoor temperature, "
            "so the optimizer's comfort limits are what hold the house down."
        ),
    )
