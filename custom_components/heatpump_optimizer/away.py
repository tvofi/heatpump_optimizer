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

from homeassistant.helpers.storage import Store

from .const import (
    CONF_AWAY_DHW_MIN_TEMP,
    CONF_AWAY_ENABLED,
    CONF_AWAY_PRESENCE_ENTITY,
    CONF_AWAY_RETURN_ENTITY,
    CONF_AWAY_TEMPERATURE,
    DEFAULT_AWAY_DHW_MIN_TEMP,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_AWAY_TEMPERATURE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
AWAY_STORE_VERSION = 1
OMIT = object()

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

    #: Entity whose state indicates absence (``person``, ``device_tracker``,
    #: ``calendar`` or a class-less occupancy ``binary_sensor``).
    presence_entity: str | None = None
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
    override_active: bool = False
    override_return_iso: str | None = None
    migrated_helpers: bool = False

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
            "away_override_active": self.override_active,
            "away_override_return_time": self.override_return_iso,
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


def expire_override(active, return_time, now):
    """Turn the service override off once ``now`` reaches the return instant."""
    if active and return_time is not None and now >= return_time:
        return False, None
    return active, return_time


def migrate_helper_override(
    presence_entity, presence_raw, presence_attributes, return_raw
):
    """One-shot copy of the old helper pair into the service store."""
    drop_presence = bool(
        presence_entity and str(presence_entity).startswith("input_boolean.")
    )
    active = False
    if drop_presence:
        active = interpret_presence(
            presence_raw, presence_entity, presence_attributes
        ) is True
    parsed = _parse_return_time(return_raw)
    return {
        "active": active,
        "return_time": parsed.isoformat() if parsed else None,
        "drop_presence": drop_presence,
    }


def empty_override() -> dict[str, Any]:
    return {"active": False, "return_time": None, "migrated_helpers": False}


def config_from_mapping(config: dict) -> AwayConfig:
    return AwayConfig(
        presence_entity=config.get(CONF_AWAY_PRESENCE_ENTITY),
        away_temperature=_as_num(
            config.get(CONF_AWAY_TEMPERATURE), DEFAULT_AWAY_TEMPERATURE
        ),
        away_dhw_min_temperature=_as_num(
            config.get(CONF_AWAY_DHW_MIN_TEMP), DEFAULT_AWAY_DHW_MIN_TEMP
        ),
    )


def apply_setback(state, opt_config, thermal_params) -> dict[str, float]:
    """Temporarily lower comfort targets while away. Returns the originals."""
    original = {
        "target_temp": opt_config.target_temp,
        "min_temp": opt_config.min_temp,
        "comfort_temp_day": opt_config.comfort_temp_day,
        "comfort_temp_night": opt_config.comfort_temp_night,
        "dhw_min_temp": thermal_params.dhw_min_temp,
        "dhw_idle_min_temp": thermal_params.dhw_idle_min_temp,
    }
    if not state.active or state.recovery_active:
        return original
    target = state.target_temperature or DEFAULT_AWAY_TEMPERATURE
    opt_config.target_temp = min(original["target_temp"], target)
    opt_config.min_temp = min(original["min_temp"], target)
    opt_config.comfort_temp_day = target
    opt_config.comfort_temp_night = target
    dhw_floor = state.dhw_min_temperature or DEFAULT_AWAY_DHW_MIN_TEMP
    thermal_params.dhw_min_temp = min(original["dhw_min_temp"], dhw_floor)
    thermal_params.dhw_idle_min_temp = min(
        original["dhw_idle_min_temp"], dhw_floor
    )
    return original


def restore_setback(original: dict[str, float], opt_config, thermal_params) -> None:
    opt_config.target_temp = original["target_temp"]
    opt_config.min_temp = original["min_temp"]
    opt_config.comfort_temp_day = original["comfort_temp_day"]
    opt_config.comfort_temp_night = original["comfort_temp_night"]
    thermal_params.dhw_min_temp = original["dhw_min_temp"]
    thermal_params.dhw_idle_min_temp = original["dhw_idle_min_temp"]


def _away_store(coord) -> Store:
    return Store(
        coord.hass,
        AWAY_STORE_VERSION,
        f"{DOMAIN}_{coord.entry.entry_id}_away",
    )


def _override_payload(state: AwayState) -> dict[str, Any]:
    return {
        "active": bool(state.override_active),
        "return_time": state.override_return_iso,
        "migrated_helpers": bool(state.migrated_helpers),
    }


def apply_override_payload(state: AwayState, payload: dict[str, Any]) -> None:
    state.override_active = bool(payload.get("active"))
    parsed = _parse_return_time(payload.get("return_time"))
    state.override_return_iso = parsed.isoformat() if parsed else None
    state.migrated_helpers = bool(payload.get("migrated_helpers"))


async def persist_override(coord) -> None:
    try:
        await _away_store(coord).async_save(_override_payload(coord._away_state))
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not persist away override: %s", err)


async def restore_override(coord) -> None:
    try:
        raw = await _away_store(coord).async_load()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not load away override: %s", err)
        raw = None
    payload = empty_override()
    if isinstance(raw, dict):
        payload["active"] = bool(raw.get("active"))
        parsed = _parse_return_time(raw.get("return_time"))
        payload["return_time"] = parsed.isoformat() if parsed else None
        payload["migrated_helpers"] = bool(raw.get("migrated_helpers"))
    if not payload["migrated_helpers"]:
        payload = await _migrate_helpers(coord, payload)
        apply_override_payload(coord._away_state, payload)
        await persist_override(coord)
        return
    apply_override_payload(coord._away_state, payload)


async def _migrate_helpers(coord, payload: dict[str, Any]) -> dict[str, Any]:
    presence = coord._config.get(CONF_AWAY_PRESENCE_ENTITY)
    presence_raw, presence_attrs = coord._entity_state(presence)
    return_raw, _ = coord._entity_state(coord._config.get(CONF_AWAY_RETURN_ENTITY))
    mig = migrate_helper_override(
        presence, presence_raw, presence_attrs, return_raw
    )
    payload["active"] = mig["active"]
    payload["return_time"] = mig["return_time"]
    payload["migrated_helpers"] = True
    options = dict(getattr(coord.entry, "options", {}) or {})
    changed = False
    if CONF_AWAY_ENABLED in options or CONF_AWAY_RETURN_ENTITY in options:
        options.pop(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED)
        options.pop(CONF_AWAY_RETURN_ENTITY, None)
        changed = True
    if mig["drop_presence"] and CONF_AWAY_PRESENCE_ENTITY in options:
        options.pop(CONF_AWAY_PRESENCE_ENTITY, None)
        changed = True
    if changed:
        updater = getattr(coord.hass.config_entries, "async_update_entry", None)
        if updater is not None:
            updater(coord.entry, options=options)
    return payload


def _as_num(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _apply_return(
    state: AwayState,
    return_time: datetime | None,
    now: datetime,
    comfort_temp: float,
    model: Any,
    thermal_state: Any,
    outdoor_temp: float,
) -> None:
    if return_time is None:
        return
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
        state.target_temperature = comfort_temp


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
    override_active: bool = False,
    override_return_time: datetime | None = None,
) -> AwayState:
    """Work out whether we are away, and whether recovery should start."""
    state = AwayState(
        override_active=bool(override_active),
        override_return_iso=(
            override_return_time.isoformat() if override_return_time else None
        ),
    )
    if override_active:
        state.active = True
        state.source = "service"
        state.target_temperature = config.away_temperature
        state.dhw_min_temperature = config.away_dhw_min_temperature
        _apply_return(
            state, override_return_time, now, comfort_temp,
            model, thermal_state, outdoor_temp,
        )
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
        return_time = override_return_time
    _apply_return(
        state, return_time, now, comfort_temp, model, thermal_state, outdoor_temp
    )
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
