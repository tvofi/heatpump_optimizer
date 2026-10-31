"""D12: the cell matrix, derived from the tree at run time.

Nothing here carries a count.  Every axis is read out of production or out of
``tests/golden.py`` when the module is imported, so a plant slot added to the
options pages enlarges the matrix without anyone editing this file.

Axes, and where each is read from:

  T  the coordinator topologies      tests/golden.py:coordinator_scenarios()
  P  plant presence combinations     DHW x wood x PV x two-zone, 2**4
  L  hydronic layouts x valve modes  topology.LAYOUTS (selectable) x the
                                     `mixing_valve_mode` selector on the
                                     options `building` page
  E  optional entity slots           every `*_entity` field the options pages
                                     present, each MAPPED alone on a minimal
                                     plant and each OMITTED from the fully
                                     mapped plant (leave-one-out)
  S  heat-pump control surfaces      the write paths the tree already has:
                                     switch, ECL110 MQTT displace, the
                                     `space_setpoint_unit` / `freq_control_mode`
                                     / `mixing_valve_write_target_kind`
                                     selectors
"""
from __future__ import annotations

import asyncio
import sys

import d12lib  # noqa: F401  (thread pin + sys.path)
from golden import _presented_fields
from harness import FakeEntry, FakeHass, FakeState

import golden
from heatpump_optimizer import config_flow, const, topology

# --------------------------------------------------------------------------
# Read the options pages once: which fields exist, and which are selectors.
# --------------------------------------------------------------------------


def _options_pages():
    hass = FakeHass()
    entry = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"})
    flow = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = hass
    fields: dict[str, str] = {}
    selects: dict[str, list] = {}
    for name in sorted(dir(flow)):
        if not name.startswith("async_step_"):
            continue
        try:
            res = asyncio.run(getattr(flow, name)(None))
        except Exception:  # noqa: BLE001
            continue
        if res.get("type") != "form":
            continue
        page = name[len("async_step_"):]
        for key, validator in _presented_fields(res.get("data_schema")):
            fields[str(key)] = page
            cfg = getattr(validator, "config", None)
            if isinstance(cfg, dict) and "options" in cfg:
                selects[str(key)] = [
                    o["value"] if isinstance(o, dict) else o for o in cfg["options"]
                ]
    return fields, selects


OPTION_FIELDS, OPTION_SELECTS = _options_pages()
ENTITY_SLOTS = sorted(k for k in OPTION_FIELDS if k.endswith("_entity"))

# --------------------------------------------------------------------------
# A plausible state for every slot, keyed by what the slot is.
# --------------------------------------------------------------------------

_TEMP = ("indoor_temp_entity", "outdoor_temp_entity", "floor_return_temp_entity",
         "lower_floor_temp_entity", "dhw_temp_entity", "buffer_tank_temp_entity",
         "dhw_inlet_entity")
_FLAG_ON = ("heat_pump_switch_entity", "heat_pump_online_entity",
            "vvc_pump_entity", "space_circulation_pump_entity")
_FLAG_OFF = ("heat_pump_defrost_entity", "heat_pump_fault_entity",
             "away_presence_entity")

SLOT_STATE = {
    "indoor_temp_entity": FakeState("21.4", unit="°C"),
    "outdoor_temp_entity": FakeState("-3.0", unit="°C"),
    "floor_return_temp_entity": FakeState("28.0", unit="°C"),
    "lower_floor_temp_entity": FakeState("20.8", unit="°C"),
    "dhw_temp_entity": FakeState("52.0", unit="°C"),
    "buffer_tank_temp_entity": FakeState("40.0", unit="°C"),
    "dhw_inlet_entity": FakeState("9.0", unit="°C"),
    "indoor_humidity_entity": FakeState("42.0", unit="%"),
    "heat_pump_power_entity": FakeState("2400", unit="W"),
    "house_power_entity": FakeState("3900", unit="W"),
    "pv_production_entity": FakeState("1200", unit="W"),
    "heat_pump_energy_entity": FakeState("1234.5", unit="kWh"),
    "solar_radiation_entity": FakeState("180", unit="W/m²"),
    "compressor_freq_entity": FakeState("55", unit="Hz",
                                        attributes={"min": 20.0, "max": 90.0,
                                                    "step": 1.0}),
    "price_entity": FakeState("0.85", unit="SEK/kWh"),
    "grid_fee_entity": FakeState("0.25", unit="SEK/kWh"),
    "pv_export_price_entity": FakeState("0.30", unit="SEK/kWh"),
    "dhw_setpoint_entity": FakeState("55.0", unit="°C"),
    "space_setpoint_entity": FakeState("21.0", unit="°C"),
    "mixing_valve_target_entity": FakeState("35.0", unit="°C"),
    "mixing_valve_write_entity": FakeState("35.0", unit="°C"),
    "heat_pump_mode_entity": FakeState("heating"),
    "heat_pump_switch_entity": FakeState("on"),
    "heat_pump_online_entity": FakeState("on"),
    "heat_pump_defrost_entity": FakeState("off"),
    "heat_pump_fault_entity": FakeState("off"),
    "vvc_pump_entity": FakeState("on"),
    "space_circulation_pump_entity": FakeState("on"),
    "away_presence_entity": FakeState("home"),
    "holiday_calendar_entity": FakeState("off"),
    "weather_entity": FakeState("cloudy", attributes={"temperature": -3.0,
                                                      "humidity": 85.0}),
}

# Entity id per slot: "<domain>.<slot without _entity>"
_DOMAIN = {
    "heat_pump_switch_entity": "switch",
    "heat_pump_online_entity": "binary_sensor",
    "heat_pump_defrost_entity": "binary_sensor",
    "heat_pump_fault_entity": "binary_sensor",
    "vvc_pump_entity": "switch",
    "space_circulation_pump_entity": "switch",
    "away_presence_entity": "device_tracker",
    "holiday_calendar_entity": "calendar",
    "weather_entity": "weather",
    "dhw_setpoint_entity": "number",
    "space_setpoint_entity": "number",
    "mixing_valve_target_entity": "number",
    "mixing_valve_write_entity": "number",
    "compressor_freq_entity": "number",
}


def slot_entity_id(slot: str) -> str:
    return f"{_DOMAIN.get(slot, 'sensor')}.hpo_{slot[:-len('_entity')]}"


# --------------------------------------------------------------------------
# The base plants.
# --------------------------------------------------------------------------

BASE = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
}

DHW_ON = {"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0,
          "dhw_min_temperature": 45.0, "dhw_windows": "06:00-08:30, 17:00-22:00"}
TWO_ZONE_ON = {"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
               "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07}
PV_ON = {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3}
# The two-tank wood plant the golden `wood_two_tank` fixture already pins.
WOOD_ON = {"mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
           "buffer_max_temperature": 70.0,
           "wood_tank_top_entity": "sensor.wood_top", "wood_tank_volume": 500.0}
WOOD_STATES = {"sensor.wood_top": FakeState("55.0", unit="°C")}


def fully_mapped():
    """The reference plant: every optional entity slot mapped, every feature on."""
    cfg = dict(BASE)
    cfg.update(DHW_ON)
    cfg.update(TWO_ZONE_ON)
    cfg.update(PV_ON)
    cfg.update(WOOD_ON)
    cfg.update({
        "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
        "away_enabled": True, "external_heat_detection_enabled": True,
        "comfort_learning_enabled": True, "system_identification_enabled": True,
        "compressor_cycling_cost": 0.5,
        "grid_fee_mode": "entity",
    })
    states = dict(WOOD_STATES)
    for slot in ENTITY_SLOTS:
        eid = slot_entity_id(slot)
        cfg[slot] = eid
        states[eid] = SLOT_STATE.get(slot, FakeState("0"))
    # `weather_entity` is not optional; keep the id the injected forecast uses.
    cfg["weather_entity"] = "weather.home"
    states["weather.home"] = SLOT_STATE["weather_entity"]
    return cfg, states


def enumerate_cells():
    """Every cell, as (group, name, config, states)."""
    cells = []

    # --- T: the coordinator topologies, verbatim ---------------------------
    for name, cfg in golden.coordinator_scenarios().items():
        cells.append(("T", name, dict(cfg), {}))

    # --- P: plant presence, 2**4 ------------------------------------------
    for dhw in (0, 1):
        for wood in (0, 1):
            for pv in (0, 1):
                for tz in (0, 1):
                    cfg = dict(BASE)
                    states = {}
                    if dhw:
                        cfg.update(DHW_ON)
                    if wood:
                        cfg.update(WOOD_ON)
                        states.update(WOOD_STATES)
                    if pv:
                        cfg.update(PV_ON)
                    if tz:
                        cfg.update(TWO_ZONE_ON)
                    name = "P_dhw%d_wood%d_pv%d_tz%d" % (dhw, wood, pv, tz)
                    cells.append(("P", name, cfg, states))

    # --- L: hydronic layout x valve mode ----------------------------------
    layouts = [l.key for l in topology.LAYOUTS.values() if l.selectable]
    valve_modes = OPTION_SELECTS.get("mixing_valve_mode", [])
    for layout in layouts:
        for mode in valve_modes:
            cfg = dict(BASE)
            cfg.update(DHW_ON)
            cfg.update(TWO_ZONE_ON)
            cfg["topology_layout"] = layout
            cfg["mixing_valve_mode"] = mode
            cfg["buffer_tank_volume"] = 750.0
            cfg["buffer_max_temperature"] = 70.0
            states = {}
            if layout == "two_tank_4way":
                cfg["wood_tank_top_entity"] = "sensor.wood_top"
                cfg["wood_tank_volume"] = 500.0
                states.update(WOOD_STATES)
            if mode in ("smart_read", "smart_write"):
                cfg["mixing_valve_target_entity"] = "number.hpo_mixing_valve_target"
                states["number.hpo_mixing_valve_target"] = SLOT_STATE[
                    "mixing_valve_target_entity"]
            if mode == "smart_write":
                cfg["mixing_valve_write_entity"] = "number.hpo_mixing_valve_write"
                states["number.hpo_mixing_valve_write"] = SLOT_STATE[
                    "mixing_valve_write_entity"]
            cells.append(("L", f"L_{layout}__{mode}", cfg, states))

    # --- E: every optional entity slot, mapped alone and omitted ----------
    full_cfg, full_states = fully_mapped()
    for slot in ENTITY_SLOTS:
        # mapped alone on a minimal plant
        cfg = dict(BASE)
        eid = slot_entity_id(slot)
        cfg[slot] = eid
        states = {eid: SLOT_STATE.get(slot, FakeState("0"))}
        cells.append(("E_mapped", f"Emap_{slot}", cfg, states))
        # omitted from the fully mapped plant (leave-one-out)
        cfg2 = dict(full_cfg)
        cfg2.pop(slot, None)
        states2 = dict(full_states)
        states2.pop(eid, None)
        cells.append(("E_omitted", f"Eomit_{slot}", cfg2, states2))

    # --- S: the heat-pump control surfaces the tree already has -----------
    for key in ("freq_control_mode", "space_setpoint_unit",
                "mixing_valve_write_target_kind"):
        for value in OPTION_SELECTS.get(key, []):
            cfg = dict(BASE)
            cfg.update(DHW_ON)
            cfg[key] = value
            states = {}
            if key == "freq_control_mode":
                cfg["compressor_freq_entity"] = "number.hpo_compressor_freq"
                states["number.hpo_compressor_freq"] = SLOT_STATE[
                    "compressor_freq_entity"]
            if key == "space_setpoint_unit":
                cfg["space_setpoint_entity"] = "number.hpo_space_setpoint"
                states["number.hpo_space_setpoint"] = SLOT_STATE[
                    "space_setpoint_entity"]
            if key == "mixing_valve_write_target_kind":
                cfg["mixing_valve_mode"] = "smart_write"
                cfg["buffer_tank_volume"] = 750.0
                cfg["mixing_valve_write_entity"] = "number.hpo_mixing_valve_write"
                states["number.hpo_mixing_valve_write"] = SLOT_STATE[
                    "mixing_valve_write_entity"]
            cells.append(("S", f"S_{key}__{value}", cfg, states))
    # The two actuation surfaces that are not selectors: the on/off switch
    # (an on/off pump) and the ECL110 MQTT displace (a modulating curve shift).
    onoff = dict(BASE); onoff.update(DHW_ON)
    onoff["heat_pump_switch_entity"] = "switch.hpo_heat_pump_switch"
    cells.append(("S", "S_onoff_switch", onoff,
                  {"switch.hpo_heat_pump_switch": FakeState("on")}))
    ecl = dict(BASE); ecl.update(DHW_ON)
    ecl["ecl110_displace_set_topic"] = const.DEFAULT_ECL110_DISPLACE_SET_TOPIC
    ecl["ecl110_state_topic"] = const.DEFAULT_ECL110_STATE_TOPIC
    cells.append(("S", "S_ecl110_mqtt", ecl, {}))

    # --- N: the null control ----------------------------------------------
    cells.append(("NULL", "NULL_fully_mapped", full_cfg, full_states))
    return cells


if __name__ == "__main__":
    cells = enumerate_cells()
    from collections import Counter
    print("option keys presented by the options pages:", len(OPTION_FIELDS))
    print("optional entity slots:", len(ENTITY_SLOTS))
    print("selectable layouts:",
          len([l for l in topology.LAYOUTS.values() if l.selectable]))
    print("coordinator_scenarios:", len(golden.coordinator_scenarios()))
    print("golden SCENARIOS:", len(golden.SCENARIOS))
    for group, n in sorted(Counter(g for g, *_ in cells).items()):
        print(f"  group {group}: {n}")
    print("TOTAL CELLS:", len(cells))
