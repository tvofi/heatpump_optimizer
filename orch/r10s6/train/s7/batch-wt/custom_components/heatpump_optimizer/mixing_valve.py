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

#: All four modes are selectable. `smart_write` was withheld until its
#: actuation path existed -- a mode that cannot do what its name says is worse
#: than one that is absent -- and now commands the valve's own controller
#: through a configured number/input_number/climate entity: the coordinator
#: writes the recommended target after each optimization cycle.
SELECTABLE_MODES: tuple[str, ...] = (
    MODE_NONE,
    MODE_MANUAL,
    MODE_SMART_READ,
    MODE_SMART_WRITE,
)

#: Modes in which a valve exists at all, and delivery is therefore throttled.
THROTTLING_MODES: frozenset[str] = frozenset(
    {MODE_MANUAL, MODE_SMART_READ, MODE_SMART_WRITE}
)

# --- What kind of set-point `smart_write` commands (#398) -------------------
#
# The same commanded number, aimed at two different kinds of entity. An
# "indoor" set-point is a room-temperature target -- what has always been
# written. A "flow" set-point is a water temperature, unit-correct only after
# `flow_setpoint` below, the same conversion the two-zone model already
# applies to bound a dumb valve's delivery.
WRITE_TARGET_INDOOR = "indoor"
WRITE_TARGET_FLOW = "flow"
WRITE_TARGET_KINDS: tuple[str, ...] = (WRITE_TARGET_INDOOR, WRITE_TARGET_FLOW)

def is_throttling(mode: str | None) -> bool:
    """Whether this mode has a valve that limits delivery."""
    return (mode or MODE_NONE) in THROTTLING_MODES


def flow_setpoint(
    *,
    target_temp: float,
    outdoor_temp: float,
    heat_loss_coefficient: float,
    emitter_ua: float,
) -> float:
    """The flow temperature the valve regulates to, in °C.

    A real mixing valve does not regulate room temperature -- it regulates the
    *flow* temperature, following a weather-compensation curve. The curve here
    is derived rather than configured: the flow temperature that, in steady
    state, holds the house exactly at ``target_temp`` is the target plus the
    house's standing loss spread over the emitter UA.

    This is what bounds discharge. The valve mixes return water into the flow,
    so the emitters never see raw tank water while the tank runs above the
    curve -- stored heat leaves the tank at the rate the house actually needs,
    not at the 22-26 kW an open valve would dump. Below the curve the valve
    saturates wide open and delivery follows the tank temperature itself.

    The old model got both halves of this wrong: it computed emitter delivery
    from the raw tank temperature, capped by a controller demand whose
    gap-closing term divided by the step length -- so delivery changed with
    ``time_step_minutes`` and a charged tank drained within a step or two of
    the pump stopping. Every plan then relaxed to the same empty tank, the
    terminal credit had no gradient, and the optimizer correctly concluded
    that storage buys nothing. Delivery is now a pure function of
    temperatures; the effective proportional gain is the emitter UA itself,
    in kW/K, which no step length can distort.
    """
    q_hold = heat_loss_coefficient * max(0.0, target_temp - outdoor_temp)
    return target_temp + q_hold / max(emitter_ua, 1e-6)


def emitter_delivery(*, mix_temp: float, zone_temp: float, ua: float) -> float:
    """Heat one emitter circuit delivers at the mixed flow temperature, in kW.

    Never negative: a valve can shut, but it cannot cool a house.
    """
    return max(0.0, ua * (mix_temp - zone_temp))


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
