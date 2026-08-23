"""Away / holiday mode with deadline-driven recovery.

A week away is the single largest saving a heating system can offer: a deep
setback plus hot water suppressed entirely, except for a legionella cycle timed
to complete before return.

What makes this more than an ``input_number`` is the **return time**. Knowing
when the house must be comfortable again lets the optimizer buy the recovery
heat in the cheapest hours beforehand instead of panic-heating on arrival at
whatever the spot price happens to be. That is exactly the machinery the DHW
planner already has for guaranteed slots, applied to the building.

Away state can come from a ``person``/``device_tracker``, a calendar entry, or
a plain ``input_boolean``, and the return time from a ``datetime`` helper or
the end of the calendar event.

**A wrong return time is a comfort failure the user will notice**, so recovery
is deliberately early: the ramp starts a full estimated recovery duration plus
a margin before the stated return, and the estimate itself is rounded up.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Extra margin on top of the estimated recovery time. Arriving to a house that
# is half a degree warm costs a little; arriving to a cold one is the failure
# the whole feature is judged on.
RECOVERY_MARGIN_HOURS = 1.0
# Recovery is never planned to take longer than this, regardless of what the
# thermal model says; beyond it the estimate is dominated by model error.
MAX_RECOVERY_HOURS = 24.0


@dataclass
class AwayConfig:
    """Configuration of away behaviour."""

    enabled: bool = False
    #: Entity whose state indicates absence (``input_boolean``, ``person``,
    #: ``device_tracker`` or ``calendar``).
    presence_entity: str | None = None
    #: Optional entity carrying the expected return time.
    return_entity: str | None = None
    #: Setback targets while away.
    away_temperature: float = 16.0
    away_dhw_min_temperature: float = 20.0
    #: Whether to keep the anti-legionella cycle running while away. Kept on by
    #: default: a tank sitting lukewarm for a week is exactly the condition the
    #: cycle exists for, and it is much cheaper to run it in a chosen cheap
    #: hour than to arrive home to an overdue one.
    legionella_before_return: bool = True


@dataclass
class AwayState:
    """Resolved away state for this update cycle."""

    active: bool = False
    source: str = "none"
    return_time: datetime | None = None
    hours_until_return: float | None = None
    #: True once the plan should be buying recovery heat rather than coasting.
    recovery_active: bool = False
    recovery_hours: float | None = None
    target_temperature: float | None = None
    dhw_min_temperature: float | None = None

    def as_dict(self) -> dict:
        return {
            "away_active": self.active,
            "away_source": self.source,
            "away_return_time": (
                self.return_time.isoformat() if self.return_time else None
            ),
            "away_hours_until_return": (
                round(self.hours_until_return, 2)
                if self.hours_until_return is not None
                else None
            ),
            "away_recovery_active": self.recovery_active,
            "away_recovery_hours": (
                round(self.recovery_hours, 2)
                if self.recovery_hours is not None
                else None
            ),
            "away_target_temperature": self.target_temperature,
            "away_dhw_min_temperature": self.dhw_min_temperature,
        }


# States that switch a toggle-style away entity OFF and ON respectively. Named
# for the *toggle*, not the person: "on" for an ``input_boolean.away_mode``
# means the house is empty.
_TOGGLE_OFF_STATES = ("off", "false", "no")
_TOGGLE_ON_STATES = ("on", "true", "yes")

# Binary sensor device classes whose ON means "somebody is home" — the inverse
# of a toggle. Motion is deliberately absent: a momentary motion sensor going
# quiet is far too weak a signal to deep-setback a house on.
_PRESENCE_DEVICE_CLASSES = ("presence", "occupancy")


def interpret_presence(
    raw: str | None,
    entity_id: str | None,
    attributes: dict | None = None,
) -> bool | None:
    """Map an entity state to "is the house empty?".

    The polarity depends on the domain, which is the whole reason this is not a
    one-liner at the call site: ``person.someone`` is ``not_home`` when away,
    an ``input_boolean.holiday_mode`` is ``on`` when away, and a
    ``binary_sensor`` with a presence device class is ``on`` when somebody is
    *home*. Getting any of these backwards deep-setbacks an occupied house.
    """
    if raw is None:
        return None
    value = str(raw).strip().lower()
    if value in ("unknown", "unavailable", ""):
        return None

    domain = (entity_id or "").split(".")[0]

    if domain in ("person", "device_tracker"):
        if value in ("not_home", "away"):
            return True
        if value == "home":
            return False
        # A named zone ("work", "school") is still not home.
        return True

    if domain == "calendar":
        # A calendar event named "holiday" being *on* means away.
        return value == "on"

    if domain == "binary_sensor":
        device_class = str((attributes or {}).get("device_class", "")).lower()
        if device_class in _PRESENCE_DEVICE_CLASSES:
            # Presence semantics: on = detected = home.
            if value in _TOGGLE_ON_STATES:
                return False
            if value in _TOGGLE_OFF_STATES:
                return True
            return None

    if value in _TOGGLE_ON_STATES:
        # An input_boolean called "away mode" is on when away.
        return True
    if value in _TOGGLE_OFF_STATES:
        return False
    # A textual sensor may speak the person vocabulary instead.
    if value in ("not_home", "away"):
        return True
    if value == "home":
        return False
    return None


def estimate_recovery_hours(
    model: Any,
    thermal_state: Any,
    target_temp: float,
    outdoor_temp: float,
    step_hours: float = 0.25,
) -> float:
    """How long full power takes to bring the house back up, in hours.

    Simulated through the real thermal model rather than a lumped formula.
    The heat has to pass through the slab — all of it in single-zone mode,
    most of it in two-zone — and the slab must overshoot the room to push
    heat into it at all. A lump over the room mass alone ignored both, and
    under-estimated recovery by more than half: measured with the default
    single-zone house, the lump said 4.4 h where the real ramp needs 10.3 h,
    leaving the house about 3 °C cold at the stated return.

    An underpowered pump never reaches the target and simply runs into the
    ``MAX_RECOVERY_HOURS`` cap, which preserves the old behaviour of starting
    as early as allowed and letting the comfort penalty do the rest.
    """
    if target_temp - float(thermal_state.room_temperature) <= 0.05:
        return 0.0
    sim = replace(thermal_state)
    max_power = float(model.params.max_electrical_power)
    steps = max(1, int(round(MAX_RECOVERY_HOURS / max(step_hours, 1e-3))))
    for i in range(steps):
        if sim.room_temperature >= target_temp:
            return i * step_hours
        sim = model.simulate_step(
            sim, max_power, outdoor_temp, dt_hours=step_hours
        )
    return MAX_RECOVERY_HOURS


def resolve(
    config: AwayConfig,
    *,
    now: datetime,
    presence_raw: str | None,
    presence_attributes: dict | None,
    return_raw: str | None,
    comfort_temp: float,
    model: Any,
    thermal_state: Any,
    outdoor_temp: float,
) -> AwayState:
    """Work out whether we are away, and whether recovery should start."""
    state = AwayState()
    if not config.enabled:
        return state

    away = interpret_presence(
        presence_raw, config.presence_entity, presence_attributes
    )
    if not away:
        return state

    state.active = True
    state.source = config.presence_entity or "manual"
    state.target_temperature = config.away_temperature
    state.dhw_min_temperature = config.away_dhw_min_temperature

    return_time = _parse_return_time(return_raw)
    if return_time is None and presence_attributes:
        # A calendar event carries its own end time, which is a better return
        # estimate than anything the user would type twice.
        for key in ("end_time", "end", "next_event_end"):
            candidate = presence_attributes.get(key)
            if candidate:
                return_time = _parse_return_time(str(candidate))
                if return_time is not None:
                    break

    if return_time is None:
        return state

    if return_time.tzinfo is None and now.tzinfo is not None:
        return_time = return_time.replace(tzinfo=now.tzinfo)

    state.return_time = return_time
    hours_left = (return_time - now).total_seconds() / 3600.0
    state.hours_until_return = hours_left

    recovery_hours = estimate_recovery_hours(
        model,
        thermal_state,
        target_temp=comfort_temp,
        outdoor_temp=outdoor_temp,
    )
    state.recovery_hours = recovery_hours

    if hours_left <= recovery_hours + RECOVERY_MARGIN_HOURS:
        state.recovery_active = True
        # During recovery the ordinary comfort target applies again; the
        # optimizer then buys the heat in the cheapest hours of the ramp.
        state.target_temperature = comfort_temp

    return state


def _parse_return_time(raw: str | None) -> datetime | None:
    if not raw:
        return None
    value = str(raw).strip()
    if value.lower() in ("unknown", "unavailable", ""):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
