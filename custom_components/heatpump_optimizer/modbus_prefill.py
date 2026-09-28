"""Option values read from a GCHV heat pump's Modbus package (#1067).

The Rotenso Windmi and the other GCHV-built monoblocks keep their own settings
in holding registers: the hot water setpoints, the hot water and night-mode
schedules, the anti-legionella days, whether the unit steers on water or room
temperature. ``tools/gen_gchv_package.py`` in tvofi/tuya_heat_pump turns those
registers into a Home Assistant package, so an install that has it already
holds, as entity states, answers several options pages ask for by hand. This
module reads them and proposes values; the options flow shows them as
suggestions the user edits before anything is saved.

Three rules are the contract, and ``tests/features.py`` pins each:

* **Suggest, never assume.** A register that is absent, unreadable or outside
  what its formula accepts suggests nothing for its key. Nothing is ever
  suggested as blank or ``None``.
* **Leave what is set.** An entity slot is suggested only while it is empty,
  and a value equal to the one in force is not suggested at all, so accepting
  every suggestion cannot rewrite a setting as itself.
* **Two spellings.** Home Assistant builds an entity id from the entity's
  name, and the package's raw register sensors are named ``HP GCHV R404
  (0194H)`` under a unique id of ``hp_gchv_r404``; an install may hold either
  ``sensor.hp_gchv_r404_0194h`` or ``sensor.hp_gchv_r404``. Both are tried,
  the unique id's spelling first, and the first that resolves wins.

Where an entity id comes from is an input, not part of the inference. A
*role* is a register (``r404``) or an entity slot the package fills
(``outdoor_temp_entity``); :func:`snapshot` takes, per role, the entity ids to
try in order, and :func:`candidates` is one resolver of them, the prefix and
its two spellings. A resolver that finds a pump's entities another way -- a
device's entity-registry entries -- hands :func:`snapshot` its own mapping,
and :func:`infer` suggests the same values from the same states. A role
also carries its *scale*, because the same setting arrives in different units
from different sources: the package's register 404 holds tenths of a degree,
while a Tuya entity for the same setpoint already reads degrees.

What no register says is anything about the house or the heating circuit:
the building, its emitters and its thermal model stay the user's to describe.

Kept free of Home Assistant imports so it can be unit-tested directly, like
``silent_mode`` and ``flow_lift``.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any, NamedTuple

from .const import (
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
    CONF_DHW_LEGIONELLA_TEMP,
    CONF_DHW_MIN_TEMP,
    CONF_DHW_SETPOINT,
    CONF_DHW_TEMP_ENTITY,
    CONF_DHW_WINDOWS,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_HEAT_PUMP_COP_NOMINAL,
    CONF_HEAT_PUMP_MAX_POWER,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
    CONF_MIXING_VALVE_WRITE_TARGET_KIND,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_SILENT_MODE_WINDOWS,
    CONF_SPACE_SETPOINT_UNIT,
    CONF_UPPER_FLOOR_THERMAL_MASS,
    DEFAULT_HEAT_PUMP_COP_NOMINAL,
)
from .mixing_valve import WRITE_TARGET_FLOW

class ResolvedRole(NamedTuple):
    """One role, resolved: the entity ids to try in order, and the scale that
    turns the first one's state into the role's unit."""

    entity_ids: tuple[str, ...]
    scale: float = 1.0


#: The raw registers whose value is tenths of a degree (Data=Temp*10).
_TENTHS = (404, 405, 406)

#: The raw holding registers read, by decimal address. The package names each
#: raw sensor after the address and its four-digit hex form, so the hex is
#: derived rather than listed: 404 is ``0194H``.
_RAW_ADDRESSES = (404, 405, 406, 518, 519, 601, 711, 712, 713, 714, 4109)

#: The named entities read, as the entity id the package's name slugs to.
_NAMED = {
    "unit_capacity": "sensor.{p}_unit_capacity",
    CONF_OUTDOOR_TEMP_ENTITY: "sensor.{p}_outdoor_air_temperature",
    CONF_DHW_TEMP_ENTITY: "sensor.{p}_dhw_tank_temperature",
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.{p}_leaving_water_temperature_t1",
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: "sensor.{p}_entering_water_temperature_tw_in",
    CONF_COMPRESSOR_FREQ_SENSOR: "sensor.{p}_actual_compressor_frequency",
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: (
        "binary_sensor.{p}_night_mode_frequency_reduction_active"
    ),
}

#: Day bitmaps put Monday on bit 7 and Sunday on bit 1; bit 0 is no day.
_DAY_BITS = 0b11111110

#: Control mode register 4109: 0 is water temperature control.
_WATER_TEMPERATURE_CONTROL = 0


def candidates(prefix: str) -> dict[str, ResolvedRole]:
    """The prefix resolver: per role, the ids tried (first match wins) and scale."""
    p = prefix.strip().lower()
    found = {
        f"r{addr}": ResolvedRole(
            (f"sensor.{p}_gchv_r{addr}", f"sensor.{p}_gchv_r{addr}_{addr:04x}h"),
            0.1 if addr in _TENTHS else 1.0,
        )
        for addr in _RAW_ADDRESSES
    }
    found.update(
        {label: ResolvedRole((template.format(p=p),)) for label, template in _NAMED.items()}
    )
    return found


def snapshot(
    get: Callable[[str], Any], resolved: Mapping[str, ResolvedRole]
) -> dict[str, tuple[str, str, float]]:
    """``role -> (entity_id, state, scale)`` for every role an id resolves.

    ``get`` is a plain state lookup (``hass.states.get``); ``resolved`` is a
    resolver's answer, such as :func:`candidates`.
    """
    snap: dict[str, tuple[str, str, float]] = {}
    for label, role in resolved.items():
        for entity_id in role.entity_ids:
            state = get(entity_id)
            if state is not None:
                snap[label] = (entity_id, str(state.state), role.scale)
                break
    return snap


def _number(snap: Mapping[str, tuple[str, str, float]], label: str) -> float | None:
    try:
        value = float(snap[label][1])
    except (KeyError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _register(snap: Mapping[str, tuple[str, str, float]], addr: int) -> int | None:
    value = _number(snap, f"r{addr}")
    return int(value) if value is not None and value.is_integer() else None


def _scaled(snap: Mapping[str, tuple[str, str, float]], addr: int) -> float | None:
    """A setpoint in its role's unit: the state times the resolver's scale."""
    value = _number(snap, f"r{addr}")
    return None if value is None else round(value * snap[f"r{addr}"][2], 1)


def _clock(raw: int | None) -> str | None:
    """``hour*256+minute`` as ``HH:MM``; None when either part is impossible."""
    if raw is None or raw < 0:
        return None
    hour, minute = divmod(raw, 256)
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def _window(
    snap: Mapping[str, tuple[str, str, float]], start: int, stop: int
) -> str | None:
    begin, end = _clock(_register(snap, start)), _clock(_register(snap, stop))
    if begin is None or end is None or begin == end:
        return None
    return f"{begin}-{end}"


def _interval_days(raw: int | None) -> float | None:
    """Seven days over the number of days the anti-legionella bitmap sets."""
    days = bin(raw & _DAY_BITS).count("1") if raw is not None else 0
    return float(7 // days) if days else None


def _hot_water(snap: Mapping[str, tuple[str, str, float]]) -> dict[str, Any]:
    schedule = _register(snap, 711)
    return {
        CONF_DHW_SETPOINT: _scaled(snap, 404),
        CONF_DHW_LEGIONELLA_TEMP: _scaled(snap, 405),
        CONF_DHW_MIN_TEMP: _scaled(snap, 406),
        CONF_DHW_WINDOWS: _window(snap, 712, 713) if schedule else None,
        CONF_DHW_LEGIONELLA_INTERVAL_DAYS: _interval_days(_register(snap, 714)),
    }


def _plant(
    snap: Mapping[str, tuple[str, str, float]], current: Mapping[str, Any]
) -> dict[str, Any]:
    capacity = _number(snap, "unit_capacity")
    cop = float(current.get(CONF_HEAT_PUMP_COP_NOMINAL) or DEFAULT_HEAT_PUMP_COP_NOMINAL)
    water = _register(snap, 4109) == _WATER_TEMPERATURE_CONTROL
    return {
        CONF_SILENT_MODE_WINDOWS: _window(snap, 518, 519),
        CONF_HEAT_PUMP_MAX_POWER: (
            round(capacity / cop, 1) if capacity and capacity > 0 else None
        ),
        CONF_SPACE_SETPOINT_UNIT: WRITE_TARGET_FLOW if water else None,
        # The building page refuses a flow write target without the two-zone
        # model's flow curve, so it is never suggested where it would be.
        CONF_MIXING_VALVE_WRITE_TARGET_KIND: (
            WRITE_TARGET_FLOW
            if water and current.get(CONF_UPPER_FLOOR_THERMAL_MASS)
            else None
        ),
    }


def infer(
    snap: Mapping[str, tuple[str, str, float]], current: Mapping[str, Any]
) -> dict[str, Any]:
    """Suggested option values; ``current`` is the configuration in force."""
    found = {**_hot_water(snap), **_plant(snap, current)}
    suggestions = {
        key: value
        for key, value in found.items()
        if value is not None and current.get(key) != value
    }
    for slot in _NAMED:
        if slot in snap and slot != "unit_capacity" and not current.get(slot):
            suggestions[slot] = snap[slot][0]
    return suggestions


def notes(snap: Mapping[str, tuple[str, str, float]]) -> dict[str, str]:
    """What the page says about the read: how much it found, and the heaters.

    The backup heater type register (601) reads 7 for a unit with no
    auxiliary heater; any other value is electric heat on the pump itself,
    which the heat pump telemetry page's heater slots exist to watch.
    """
    heater = _register(snap, 601)
    return {
        "found": str(len(snap)),
        "backup_heater_type": "–" if heater is None else str(heater),
    }
