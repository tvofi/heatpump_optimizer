"""One description of the configured system, shared by every picture of it.

Items 32 and 33. The config flow's setup overview and the card's setup page
both draw the same system — house, zones, tanks, valves, furnace, and every
sensor at its physical place. Two renderers with two ideas of the topology
would diverge the first time a sensor is added, so the description is built
here, once, and both consume it.

Everything is derived from configuration the integration already has — the
backlog is explicit that this needs no new options. The derived facts
(two-zone, DHW, valve mode, whether the tank is a store) come from
``ThermalParameters.from_config`` itself, so a picture can never disagree
with what the model actually believes.

**A slot that is empty is shown empty.** A diagram that silently omits an
unconfigured sensor looks complete, and "looks complete" is worse than no
diagram — the whole point is to reveal what is missing.

Kept free of Home Assistant imports so it can be unit-tested directly, like
`manual_plan`, `mixing_valve` and `external_heat`.
"""
from __future__ import annotations

from typing import Any

from . import mixing_valve
from .const import (
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_DHW_TEMP_ENTITY,
    CONF_ENERGY_ENTITY,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_HOUSE_POWER_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_MIXING_VALVE_TARGET_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_POWER_ENTITY,
    CONF_PV_PRODUCTION_ENTITY,
    CONF_SOLAR_RADIATION_ENTITY,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TANK_VOLUME,
    DEFAULT_WOOD_TANK_VOLUME,
)
from .thermal_model import ThermalParameters

# Every sensor slot the diagram can show: (config key, place, label).
# Places are stable ids both renderers key their drawing off; adding a place
# here without teaching the renderers about it is harmless — unknown places
# land in the "elsewhere" group rather than vanishing.
_SLOTS: tuple[tuple[str, str, str], ...] = (
    (CONF_OUTDOOR_TEMP_ENTITY, "outdoor", "Outdoor temperature"),
    (CONF_SOLAR_RADIATION_ENTITY, "outdoor", "Solar radiation"),
    (CONF_PV_PRODUCTION_ENTITY, "outdoor", "PV production"),
    (CONF_INDOOR_TEMP_ENTITY, "upper_zone", "Indoor temperature"),
    (CONF_LOWER_FLOOR_TEMP_ENTITY, "lower_zone", "Lower floor temperature"),
    (CONF_FLOOR_RETURN_TEMP_ENTITY, "floor_loop", "Floor loop return"),
    (CONF_HEAT_PUMP_SWITCH_ENTITY, "heat_pump", "Heat pump switch"),
    (CONF_POWER_ENTITY, "heat_pump", "Power meter"),
    (CONF_ENERGY_ENTITY, "heat_pump", "Energy meter"),
    (CONF_HOUSE_POWER_ENTITY, "heat_pump", "Whole-house power"),
    (CONF_BUFFER_TANK_TEMP_ENTITY, "buffer_tank", "Buffer tank temperature"),
    (CONF_MIXING_VALVE_TARGET_ENTITY, "mixing_valve", "Valve target"),
    (CONF_DHW_TEMP_ENTITY, "dhw_tank", "Hot water temperature"),
    (CONF_EXTERNAL_HEAT_ENTITY, "wood_tank", "Stove or flue sensor"),
    (CONF_WOOD_TANK_TOP_ENTITY, "wood_tank", "Wood tank top"),
    (CONF_WOOD_TANK_BOTTOM_ENTITY, "wood_tank", "Wood tank bottom"),
    (CONF_VALVE_OUTLET_TEMP_ENTITY, "wood_valve", "Valve outlet temperature"),
)

#: Places that only exist on some topologies, and the flag that brings them.
_CONDITIONAL_PLACES = ("lower_zone", "floor_loop", "dhw_tank", "mixing_valve",
                       "wood_tank", "wood_valve")


def describe_setup(config: dict[str, Any]) -> dict[str, Any]:
    """The configured system as one structured description.

    Pure over the config dict. The ``slots`` list includes empty slots for
    every place the configured topology has, each entry
    ``{key, label, place, entity}`` with ``entity`` ``None`` when nothing is
    assigned.
    """
    p = ThermalParameters.from_config(config)
    valve = mixing_valve.is_throttling(p.mixing_valve_mode)
    wood = bool(
        config.get(CONF_EXTERNAL_HEAT_ENABLED)
        or config.get(CONF_WOOD_TANK_TOP_ENTITY)
        or config.get(CONF_WOOD_TANK_BOTTOM_ENTITY)
        or config.get(CONF_VALVE_OUTLET_TEMP_ENTITY)
        or config.get(CONF_EXTERNAL_HEAT_ENTITY)
    )
    present = {
        "outdoor": True,
        "upper_zone": True,
        "heat_pump": True,
        "buffer_tank": True,
        "lower_zone": p.two_zone_enabled,
        "floor_loop": p.two_zone_enabled,
        "dhw_tank": p.dhw_enabled,
        "mixing_valve": valve,
        "wood_tank": wood,
        "wood_valve": wood,
    }
    slots = [
        {
            "key": key,
            "label": label,
            "place": place,
            "entity": config.get(key) or None,
        }
        for key, place, label in _SLOTS
        if present.get(place, True)
    ]
    return {
        "two_zone": p.two_zone_enabled,
        "dhw": p.dhw_enabled,
        "valve_mode": p.mixing_valve_mode,
        "buffer": {
            "volume_l": p.buffer_tank_volume,
            "is_store": p.buffer_is_store,
            "max_temp": p.buffer_max_temp,
        },
        "wood": {
            "present": wood,
            "volume_l": float(
                config.get(CONF_WOOD_TANK_VOLUME) or DEFAULT_WOOD_TANK_VOLUME
            ),
        },
        "slots": slots,
    }


def _slot_lines(setup: dict[str, Any], place: str) -> list[str]:
    lines = []
    for slot in setup["slots"]:
        if slot["place"] != place:
            continue
        mark = "*" if slot["entity"] else "-"
        value = slot["entity"] or "not configured"
        lines.append(f"  {mark} {slot['label']}: {value}")
    return lines


def render_text_summary(setup: dict[str, Any]) -> str:
    """The read-only overview for the config flow, as monospaced markdown.

    Item 32's recommended staging: a picture of what is configured so far,
    with the empty slots visible. Home Assistant renders flow descriptions
    as markdown, and a fenced block is the one drawing surface that needs no
    endpoint, no authentication story and no frontend support beyond what
    every install already has.
    """
    valve = mixing_valve.is_throttling(setup["valve_mode"])
    parts: list[str] = []

    house = ["House: two zones" if setup["two_zone"] else "House: one zone"]
    house += _slot_lines(setup, "upper_zone")
    if setup["two_zone"]:
        house += _slot_lines(setup, "lower_zone")
        house += _slot_lines(setup, "floor_loop")
    parts.append("\n".join(house))

    hp = ["Heat pump"]
    hp += _slot_lines(setup, "heat_pump")
    parts.append("\n".join(hp))

    buf = setup["buffer"]
    tank = [
        f"Buffer tank: {buf['volume_l']:.0f} L"
        + (
            f", used as a store up to {buf['max_temp']:.0f} °C"
            if buf["is_store"]
            else (", too small to store" if valve else "")
        )
    ]
    if valve:
        tank.append(f"  * Mixing valve: {setup['valve_mode']}")
        tank += _slot_lines(setup, "mixing_valve")
    else:
        tank.append("  - Mixing valve: none (delivery is not throttled)")
    tank += _slot_lines(setup, "buffer_tank")
    parts.append("\n".join(tank))

    if setup["dhw"]:
        dhw = ["Hot water tank"]
        dhw += _slot_lines(setup, "dhw_tank")
        parts.append("\n".join(dhw))

    if setup["wood"]["present"]:
        wood = [f"Wood furnace tank: {setup['wood']['volume_l']:.0f} L"]
        wood += _slot_lines(setup, "wood_tank")
        wood += _slot_lines(setup, "wood_valve")
        parts.append("\n".join(wood))

    outside = ["Outside"]
    outside += _slot_lines(setup, "outdoor")
    parts.append("\n".join(outside))

    body = "\n\n".join(parts)
    return f"```\n{body}\n```"
