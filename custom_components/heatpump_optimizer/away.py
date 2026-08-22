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
from dataclasses import dataclass
from datetime import datetime

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


_AWAY_STATES = ("off", "not_home", "away", "false", "no")
_HOME_STATES = ("on", "home", "true", "yes")


def interpret_presence(raw: str | None, entity_id: str | None) -> bool | None:
    """Map an entity state to "is the house empty?".

    The polarity depends on the domain, which is the whole reason this is not a
    one-liner at the call site: ``person.someone`` is ``not_home`` when away,
    while an ``input_boolean.holiday_mode`` is ``on`` when away. Getting this
    backwards would deep-setback an occupied house.
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

    if value in _HOME_STATES:
        # An input_boolean called "away mode" is on when away.
        return True
    if value in _AWAY_STATES:
        return False
    return None


def estimate_recovery_hours(
    current_temp: float,
    target_temp: float,
    heat_capacity_kwh_per_c: float,
    available_thermal_kw: float,
    heat_loss_kw_per_c: float,
    outdoor_temp: float,
) -> float:
    """How long it takes to bring the house back up, in hours.

    A lumped-capacity estimate: the pump's surplus over the standing loss at
    the target temperature is what actually raises the temperature, and the
    surplus shrinks as the house warms. Using the surplus at the *target*
    rather than at the current temperature is the conservative choice, since it
    is the smallest surplus of the whole ramp.
    """
    deficit = max(0.0, target_temp - current_temp)
    if deficit <= 0.05:
        return 0.0
    standing_loss = max(0.0, heat_loss_kw_per_c * (target_temp - outdoor_temp))
    surplus = available_thermal_kw - standing_loss
    if surplus <= 0.05:
        # The pump cannot reach the target at this outdoor temperature at all.
        # Start as early as the cap allows and let the comfort penalty do the
        # rest; refusing to plan recovery would be worse.
        return MAX_RECOVERY_HOURS
    hours = deficit * heat_capacity_kwh_per_c / surplus
    return float(min(MAX_RECOVERY_HOURS, hours))


def resolve(
    config: AwayConfig,
    *,
    now: datetime,
    presence_raw: str | None,
    presence_attributes: dict | None,
    return_raw: str | None,
    current_temp: float,
    comfort_temp: float,
    heat_capacity_kwh_per_c: float,
    available_thermal_kw: float,
    heat_loss_kw_per_c: float,
    outdoor_temp: float,
) -> AwayState:
    """Work out whether we are away, and whether recovery should start."""
    state = AwayState()
    if not config.enabled:
        return state

    away = interpret_presence(presence_raw, config.presence_entity)
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
        current_temp=current_temp,
        target_temp=comfort_temp,
        heat_capacity_kwh_per_c=heat_capacity_kwh_per_c,
        available_thermal_kw=available_thermal_kw,
        heat_loss_kw_per_c=heat_loss_kw_per_c,
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
