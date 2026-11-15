"""Whether a floor-return reading may seed the slab estimate (#3616).

The floor-return field seeds the slab every cycle
(``ThermalModel.update_slab_from_return_temp``), and a seed far above the
room tells the planner that heat is already stored, so it plans none. That is
what a heat-pump return on a buffer plant does when it is configured in that
field: the plan held 0 kWh of space heating with the rooms below target.

A refused reading is not replaced by a guess: the slab keeps the model's own
estimate, which the coordinator advances exactly as it does with no sensor.
Pure: no Home Assistant import; the coordinator passes the readings in.
"""
from __future__ import annotations

from typing import Any, Final

from .freq_control import defrost_interval

#: The warmest a floor-loop return may read above the room air it heats, K.
#: Floor-loop water runs 3-9 K above that air (the repository's working band,
#: see the ``lower_floor_modelled`` repair text), and EN 1264's surface limits,
#: 29 C in an occupied zone and 33 C in a bathroom over 20 and 24 C design
#: rooms, both put the floor 9 K above its room. The 3 K over that is margin
#: for a sensor on the manifold and a peripheral zone. A buffer or heat-pump
#: return, which runs at the heating curve's flow temperature, clears it.
SLAB_SEED_MAX_ABOVE_ROOM_K: Final = 12.0

#: The issue raised while a reading is refused for its level, naming the sensor.
ISSUE_FLOOR_RETURN_IMPLAUSIBLE: Final = "floor_return_implausible"

REFUSED_ABOVE_ROOM: Final = "above_room"
REFUSED_HOT_WATER: Final = "hot_water_run"
REFUSED_DEFROST: Final = "defrost"


def above_room(return_c: float, room_c: float) -> bool:
    """Whether ``return_c`` is too far above ``room_c`` to be a floor loop."""
    return return_c - room_c > SLAB_SEED_MAX_ABOVE_ROOM_K


def hot_water_run(signals: Any) -> bool:
    """Whether the pump's observed mode is hot water alone.

    A return probe then reads tank water. Only an observed mode counts: the
    unknown-mode fallback can do everything and so says nothing either way.
    """
    mode = signals.mode
    return bool(signals.mode_observed and mode.dhw and not mode.space_heat)


def refusal(return_c: float, room_c: float, signals: Any) -> str | None:
    """Why ``return_c`` may not seed the slab now, or ``None`` when it may."""
    if above_room(return_c, room_c):
        return REFUSED_ABOVE_ROOM
    if hot_water_run(signals):
        return REFUSED_HOT_WATER
    if defrost_interval(signals.defrosting):
        return REFUSED_DEFROST
    return None


def seed(model: Any, state: Any, return_c: float | None, signals: Any) -> None:
    """Advance ``state``'s slab from ``return_c`` unless the reading is refused.

    Called before this cycle's pump signals are read, so ``signals`` are last
    cycle's; :func:`judge` re-decides on this cycle's before the state publishes.
    """
    if return_c is not None and refusal(return_c, state.room_temperature, signals) is None:
        model.update_slab_from_return_temp(state, return_c)


def judge(notices: Any, hass: Any, reading: Any, room_c: float, signals: Any) -> bool:
    """Whether this cycle's floor-return ``reading`` seeds the slab.

    A refused reading leaves the slab to the model, as no sensor does. The
    repair naming the sensor is raised while its level is refused and cleared
    otherwise: judged on the level alone, since a hot-water run or a defrost
    refuses a reading for that cycle only, which is the plant working, not a
    wrong sensor.
    """
    value = reading.value if reading.ok else None
    high = value is not None and above_room(value, room_c)
    notices.report(
        hass, ISSUE_FLOOR_RETURN_IMPLAUSIBLE, reading.entity_id if high else None,
        {
            "entity": str(reading.entity_id),
            "reading": f"{value:.1f}",
            "room": f"{room_c:.1f}",
            "bound": f"{SLAB_SEED_MAX_ABOVE_ROOM_K:g}",
        } if high else None,
    )
    return value is not None and refusal(value, room_c, signals) is None
