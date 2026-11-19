"""D12.M3 / D12.M5 -- every heat-pump axis cell driven through one real coordinator cycle.

Metric (one line): per cell, usable = the cycle returns a payload AND a plan is
published AND every service call targets a configured entity/topic through a
service of that entity's own domain, with a set-point/value inside the entity's
own declared range and a select option the entity offers AND the cell's
surface is actuated where the cell says it must be AND (modulation cells) the
declared compressor mode is the one the plan obeys (no planned step in
(0, p_min) under a declared on/off compressor, no projection under a declared
modulating one). RESULT fail_count = cells failing that bar.

Count key: the service calls the production cycle delivers to
``hass.services.async_call`` (domain, service, data) and the plan
``HeatPumpOptimizerCoordinator._optimization_result`` the cycle publishes --
never a config attribute of the harness's own records.

Hooks / drives: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data
(the whole cycle: _apply_action -> pump_arbiter.apply / write_supply,
heat_curve.publish, _command_frequency), thermal_model:declared_modulation via
optimizer:OptimizationConfig.from_mapping.

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/surfaces.py            # M3: generalization plant
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/surfaces.py --reference  # M5: null arm, fully-mapped coord_all_features plant
  ... surfaces.py --list           # the M3 universe (enumerator), one cell per line
  ... surfaces.py --perturb doc-modulation   # declared_modulation patched to its documented map (on_off->False): fail_count must go DOWN by 1
  ... surfaces.py --perturb range-keys       # C2: climate min_temp/max_temp unread (decoy min/max used): space_setpoint:climate and dhw_setpoint:climate/water_heater must FAIL (count up)
  ... surfaces.py --entry --setup [-v] [--reference]   # each cell set up through heatpump_optimizer.async_setup_entry
                                                    # (notifier, debugger, frontend, platforms), then run_optimization,
                                                    # simulate_plan, diagnose_interval services; a raise fails the cell
  ... surfaces.py --reference --perturb drop-pv   # plant shrink (brief M6 style): PV/away/peak dropped from the reference arm; the count must not move (0)
Expected at baseline 92d38ecb (export as handed over, box B6): 32 cells; fail_count=1 (modulation:on_off) exact on the
generalization arm (also with --entry --setup); --reference fails modulation:on_off as well (1-3 sub-minimum steps);
--entry --reference also reads heat_curve:number_offset / input_number_offset as "never actuated" -- a harness gap:
the entity already reads the cycle's displace (-3) and heat_curve.write_displace owes no write (_decide).
--perturb doc-modulation -> 0. The solve runs in the process worker (coordinator._run_in_process): only parent-side
patches (declared_modulation, inputs._RANGE_KEYS) reach it.
Machine: box B6, Linux x86_64, python 3.14, numpy 2.5.4 / scipy 1.18.1.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import logging
import tempfile
import time
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
os.environ.setdefault("TMPDIR", tempfile.gettempdir())

import numpy as np  # noqa: E402

import harness  # noqa: E402,F401  (inserts custom_components)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import boost as boost_mod  # noqa: E402
from heatpump_optimizer import const as c  # noqa: E402
from heatpump_optimizer import thermal_model  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.inputs import SETPOINT_SERVICES  # noqa: E402

logging.disable(logging.CRITICAL)

P_MIN, P_MAX = 1.2, 3.5


def _range_of(state):
    """The entity's own declared range, by its domain's keys."""
    a = state.attributes
    if "min_temp" in a or "max_temp" in a:
        return a.get("min_temp"), a.get("max_temp")
    return a.get("min"), a.get("max")


def T(v, **attrs):
    return FakeState(str(v), attributes={"unit_of_measurement": "°C", **attrs})


# ----- the plants -----------------------------------------------------------
GEN_BASE = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "target_temperature": 21.0, "min_temperature": 19.0, "max_temperature": 23.0,
    c.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    c.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    c.CONF_DHW_TANK_VOLUME: 180.0,
    c.CONF_DHW_TEMP_ENTITY: "sensor.dhw",
    c.CONF_HEAT_PUMP_MIN_POWER: P_MIN, c.CONF_HEAT_PUMP_MAX_POWER: P_MAX,
}
GEN_STATES = {
    "sensor.indoor": T(20.4), "sensor.outdoor": T(-3.0), "sensor.dhw": T(47.0),
}
# coord_all_features (tests/golden.py) with every reading mapped: the null arm.
REF_BASE = {
    **GEN_BASE,
    "dhw_tank_volume": 200.0,
    "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
    "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
    "away_enabled": True, "external_heat_detection_enabled": True,
    "comfort_learning_enabled": True, "system_identification_enabled": True,
    "compressor_cycling_cost": 0.5,
    c.CONF_POWER_ENTITY: "sensor.hp_power",
    c.CONF_ENERGY_ENTITY: "sensor.hp_energy",
    c.CONF_HOUSE_POWER_ENTITY: "sensor.house_power",
    c.CONF_PV_PRODUCTION_ENTITY: "sensor.pv",
    c.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.supply",
    c.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: "sensor.return",
    c.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.rh",
}
REF_STATES = {
    **GEN_STATES,
    "sensor.hp_power": FakeState("1800", attributes={"unit_of_measurement": "W", "device_class": "power"}),
    "sensor.hp_energy": FakeState("1234.5", attributes={"unit_of_measurement": "kWh", "device_class": "energy", "state_class": "total_increasing"}),
    "sensor.house_power": FakeState("2500", attributes={"unit_of_measurement": "W", "device_class": "power"}),
    "sensor.pv": FakeState("0", attributes={"unit_of_measurement": "W", "device_class": "power"}),
    "sensor.supply": T(38.0), "sensor.return": T(33.0),
    "sensor.rh": FakeState("40", attributes={"unit_of_measurement": "%", "device_class": "humidity"}),
}

CONTROL = {c.CONF_PUMP_DUTY_MODE: "control"}
TUYA_OPTIONS = ["Heating", "DHW", "Heating + DHW", "Cool", "Cool + DHW"]
MODBUS_OPTIONS = ["Off", "Cool + DHW", "Heat + DHW"]
METERED_FREQ = {
    c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_SPACE_SETPOINT_ENTITY: "number.flow_sp",
    c.CONF_SPACE_SETPOINT_UNIT: "flow", c.CONF_POWER_ENTITY: "sensor.hp_power",
    c.CONF_COMPRESSOR_FREQ_SENSOR: "sensor.hz",
}
METERED_STATES = {
    "switch.hp": FakeState("on"),
    "number.flow_sp": T(35, min=20, max=55, step=1),
    "sensor.hp_power": FakeState("1800", attributes={"unit_of_measurement": "W", "device_class": "power"}),
    "sensor.hz": FakeState("45", attributes={"unit_of_measurement": "Hz"}),
}

# Each cell: (extra config, extra states, surface the cycle must actuate or None, modulation expectation)
CELLS = {
    # --- switch surface: the three domains the heat-pump slot accepts (topology ASSIGNABLE_KEYS)
    "switch:switch": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp"}, {"switch.hp": FakeState("off")}, "switch.hp", None),
    "switch:input_boolean": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "input_boolean.hp"}, {"input_boolean.hp": FakeState("off")}, "input_boolean.hp", None),
    "switch:climate": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "climate.hp"}, {"climate.hp": FakeState("off", attributes={"min_temp": 7, "max_temp": 35})}, "climate.hp", None),
    # --- space set-point surface (number / input_number / climate); climate carries decoy min/max
    #     so a reader of the wrong keys writes outside min_temp/max_temp (C2)
    "space_setpoint:number": ({**CONTROL, c.CONF_SPACE_SETPOINT_ENTITY: "number.sp"}, {"number.sp": T(20, min=18, max=22, step=0.5)}, "number.sp", None),
    "space_setpoint:input_number": ({**CONTROL, c.CONF_SPACE_SETPOINT_ENTITY: "input_number.sp"}, {"input_number.sp": T(20, min=18, max=22, step=0.5)}, "input_number.sp", None),
    "space_setpoint:climate": ({**CONTROL, c.CONF_SPACE_SETPOINT_ENTITY: "climate.sp"}, {"climate.sp": FakeState("heat", attributes={"temperature": 20, "current_temperature": 20.4, "min_temp": 18, "max_temp": 22, "min": 5, "max": 35, "target_temp_step": 0.5})}, "climate.sp", None),
    "space_setpoint:flow_number": ({**CONTROL, c.CONF_SPACE_SETPOINT_ENTITY: "number.flow_sp", c.CONF_SPACE_SETPOINT_UNIT: "flow"}, {"number.flow_sp": T(35, min=20, max=55, step=1)}, "number.flow_sp", None),
    # --- DHW set-point surface
    "dhw_setpoint:number": ({**CONTROL, c.CONF_DHW_SETPOINT_ENTITY: "number.dhw_sp"}, {"number.dhw_sp": T(50, min=40, max=60, step=1)}, None, None),
    "dhw_setpoint:input_number": ({**CONTROL, c.CONF_DHW_SETPOINT_ENTITY: "input_number.dhw_sp"}, {"input_number.dhw_sp": T(50, min=40, max=60, step=1)}, None, None),
    "dhw_setpoint:climate": ({**CONTROL, c.CONF_DHW_SETPOINT_ENTITY: "climate.dhw_sp"}, {"climate.dhw_sp": FakeState("heat", attributes={"temperature": 50, "min_temp": 40, "max_temp": 60, "min": 5, "max": 80, "target_temp_step": 1})}, None, None),
    "dhw_setpoint:water_heater": ({**CONTROL, c.CONF_DHW_SETPOINT_ENTITY: "water_heater.dhw_sp"}, {"water_heater.dhw_sp": FakeState("heat_pump", attributes={"temperature": 50, "min_temp": 40, "max_temp": 60, "min": 5, "max": 80, "target_temp_step": 1})}, None, None),
    # --- operating-mode select: Tuya fork vocabulary and the Modbus package's
    "mode_select:tuya": ({**CONTROL, c.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode", c.CONF_SPACE_SETPOINT_ENTITY: "number.sp"}, {"select.hp_mode": FakeState("Heating + DHW", attributes={"options": TUYA_OPTIONS}), "number.sp": T(20, min=18, max=22, step=0.5)}, None, None),
    "mode_select:modbus": ({**CONTROL, c.CONF_HEAT_PUMP_MODE_ENTITY: "select.hp_mode", c.CONF_SPACE_SETPOINT_ENTITY: "number.sp"}, {"select.hp_mode": FakeState("Heat + DHW", attributes={"options": MODBUS_OPTIONS}), "number.sp": T(20, min=18, max=22, step=0.5)}, None, None),
    # --- heat-curve displace: ECL110 MQTT arms and the generic number arm
    "heat_curve:ecl110_set_topic": ({c.CONF_ECL110_DISPLACE_SET_TOPIC: "ecl110/displace/set", c.CONF_ECL110_DISPLACE_MIN: -5.0, c.CONF_ECL110_DISPLACE_MAX: 5.0}, {}, "mqtt:ecl110/displace/set", None),
    "heat_curve:ecl110_legacy_topic": ({c.CONF_ECL110_COMMAND_TOPIC: "ecl110/cmd", c.CONF_ECL110_DISPLACE_MIN: -5.0, c.CONF_ECL110_DISPLACE_MAX: 5.0}, {}, "mqtt:ecl110/cmd", None),
    "heat_curve:number_offset": ({c.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.curve_off", c.CONF_HEAT_CURVE_TARGET_KIND: "offset"}, {"number.curve_off": FakeState("-3", attributes={"unit_of_measurement": "°C", "min": -4, "max": 4, "step": 1})}, "number.curve_off", None),
    "heat_curve:input_number_offset": ({c.CONF_HEAT_CURVE_DISPLACE_ENTITY: "input_number.curve_off", c.CONF_HEAT_CURVE_TARGET_KIND: "offset"}, {"input_number.curve_off": FakeState("-3", attributes={"unit_of_measurement": "°C", "min": -4, "max": 4, "step": 1})}, "input_number.curve_off", None),
    "heat_curve:number_persistent": ({c.CONF_HEAT_CURVE_DISPLACE_ENTITY: "number.curve_par", c.CONF_HEAT_CURVE_TARGET_KIND: "persistent"}, {"number.curve_par": FakeState("40", attributes={"unit_of_measurement": "°C", "min": 30, "max": 42, "step": 1})}, "number.curve_par", None),
    # --- compressor: on/off vs modulating (the select) on a metered frequency plant
    "modulation:on_off": ({**METERED_FREQ, c.CONF_COMPRESSOR_MODULATION: "on_off"}, METERED_STATES, None, "on_off"),
    "modulation:modulating": ({**METERED_FREQ, c.CONF_COMPRESSOR_MODULATION: "modulating"}, METERED_STATES, None, "modulating"),
    "modulation:auto": ({**METERED_FREQ, c.CONF_COMPRESSOR_MODULATION: "auto"}, METERED_STATES, None, "auto"),
    # --- compressor-frequency surface: none (on/off pump), observe (sensor), control (number)
    "frequency:none": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp"}, {"switch.hp": FakeState("off")}, "switch.hp", None),
    "frequency:observe": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_COMPRESSOR_FREQ_SENSOR: "sensor.hz"}, {"switch.hp": FakeState("off"), "sensor.hz": FakeState("0", attributes={"unit_of_measurement": "Hz"})}, "switch.hp", None),
    "frequency:control": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_COMPRESSOR_FREQ_ENTITY: "number.hz", c.CONF_FREQ_CONTROL_MODE: "control", c.CONF_POWER_ENTITY: "sensor.hp_power"}, {"switch.hp": FakeState("off"), "number.hz": FakeState("45", attributes={"unit_of_measurement": "Hz", "min": 20, "max": 90, "step": 1}), "sensor.hp_power": FakeState("1800", attributes={"unit_of_measurement": "W", "device_class": "power"})}, "switch.hp", None),
    # --- control with an evidenced kW-per-Hz map (seeded before the cycle): the write must land in the number's own range
    "frequency:control_evidenced": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_COMPRESSOR_FREQ_ENTITY: "number.hz", c.CONF_FREQ_CONTROL_MODE: "control", c.CONF_POWER_ENTITY: "sensor.hp_power"}, {"switch.hp": FakeState("off"), "number.hz": FakeState("45", attributes={"unit_of_measurement": "Hz", "min": 20, "max": 90, "step": 1}), "sensor.hp_power": FakeState("1800", attributes={"unit_of_measurement": "W", "device_class": "power"})}, "number.hz", None),
    # --- a counter-metered pump whose spans hold hot-water charges (two cycles, counter advancing, tank charging)
    "metering:counter_dhw_spans": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_ENERGY_ENTITY: "sensor.hp_energy", c.CONF_HEAT_ENERGY_ENTITY: "sensor.heat_energy"}, {"switch.hp": FakeState("on"), "sensor.hp_energy": FakeState("1000.0", attributes={"unit_of_measurement": "kWh", "device_class": "energy", "state_class": "total_increasing"}), "sensor.heat_energy": FakeState("3000.0", attributes={"unit_of_measurement": "kWh", "device_class": "energy", "state_class": "total_increasing"})}, "switch.hp", None),
    # --- a short boost: shorter than one optimisation interval
    "boost:short_space": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp"}, {"switch.hp": FakeState("off")}, "switch.hp", None),
    # --- the other switch / number surfaces the tree writes (pump_schedule, quiet_windows silent
    #     switch, disinfection switch, mixing-valve smart_write)
    "circulation:space_pump_switch": ({c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", "space_circulation_pump_entity": "switch.circ"}, {"switch.hp": FakeState("on"), "switch.circ": FakeState("off")}, "switch.circ", None),
    "circulation:vvc_input_boolean": ({c.CONF_VVC_PUMP_ENTITY: "input_boolean.vvc", "dhw_windows": "06:00-08:30, 17:00-22:00"}, {"input_boolean.vvc": FakeState("off")}, "input_boolean.vvc", None),
    "silent:capacity_switch": ({**CONTROL, c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.silent", c.CONF_QUIET_SILENT_WINDOWS: "00:00-23:59", c.CONF_SILENT_MODE_FRACTION: 0.6}, {"switch.hp": FakeState("on"), "switch.silent": FakeState("off")}, "switch.silent", None),
    "disinfection:switch_control": ({c.CONF_DHW_DISINFECTION_SWITCH_ENTITY: "switch.legionella", c.CONF_DHW_DISINFECTION_MODE: "control"}, {"switch.legionella": FakeState("off")}, None, None),
    "mixing_valve:smart_write_number": ({c.CONF_MIXING_VALVE_MODE: "smart_write", c.CONF_MIXING_VALVE_WRITE_ENTITY: "number.valve", c.CONF_MIXING_VALVE_TARGET: 22.0}, {"number.valve": T(21, min=15, max=30, step=0.5)}, "number.valve", None),
}
#: Home Assistant's generic on/off service domain: it routes to any entity's own domain.
GENERIC_DOMAINS = {"homeassistant"}


def build(cfg, states, entry_id="d12s3", entry_setup=False):
    hass = FakeHass()
    for k, v in states.items():
        hass.states.set(k, v)
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    if entry_setup:
        return hass, _entry_setup(hass, cfg, entry_id, now)
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg, entry_id=entry_id))

    async def prices():
        coord._prices = [{"total": round(0.6 + 0.9 * (h % 12) / 12, 4),
                          "starts_at": (now + timedelta(hours=h - 1)).isoformat(), "level": "NORMAL"}
                         for h in range(48)]

    async def weather():
        coord._weather_forecast = [{"datetime": (now + timedelta(hours=h)).isoformat(),
                                    "temperature": -5 + 3 * (h % 24) / 24, "wind_speed": 3.0,
                                    "precipitation": 0.0, "humidity": 85.0} for h in range(48)]

    async def solar():
        return None

    coord._fetch_tibber_prices = prices
    coord._fetch_weather_forecast = weather
    coord._fetch_solar_forecast = solar
    return hass, coord


def _fake_feeds(now):
    """The three network fetches, as instance-free callables (class-level patch for --entry)."""
    async def prices(self):
        self._prices = [{"total": round(0.6 + 0.9 * (h % 12) / 12, 4),
                         "starts_at": (now + timedelta(hours=h - 1)).isoformat(), "level": "NORMAL"}
                        for h in range(48)]

    async def weather(self):
        self._weather_forecast = [{"datetime": (now + timedelta(hours=h)).isoformat(),
                                   "temperature": -5 + 3 * (h % 24) / 24, "wind_speed": 3.0,
                                   "precipitation": 0.0, "humidity": 85.0} for h in range(48)]

    async def solar(self):
        return None
    return prices, weather, solar


def _entry_setup(hass, cfg, entry_id, now):
    """--entry: the integration's own ``async_setup_entry`` (first refresh, notifier,
    debugger, frontend, every platform), the network fetches patched on the class."""
    import heatpump_optimizer as integ
    prices, weather, solar = _fake_feeds(now)
    K = HeatPumpOptimizerCoordinator
    K._fetch_tibber_prices, K._fetch_weather_forecast, K._fetch_solar_forecast = prices, weather, solar
    from homeassistant.config_entries import ConfigEntryState
    entry = FakeEntry(data=cfg, entry_id=entry_id)
    hass.config_entries.entries.append(entry)
    if not asyncio.run(integ.async_setup_entry(hass, entry)):
        raise RuntimeError("async_setup_entry returned False")
    entry.state = ConfigEntryState.LOADED  # what HA sets once setup returned True
    return entry.runtime_data


def entry_services(hass):
    """--entry: the services a user drives on the cell's plan; a raise is the observable."""
    from types import SimpleNamespace

    from heatpump_optimizer import services
    why = []
    services.async_register_services(hass)
    for name, fn, data in (("run_optimization", services.handle_run_optimization, {}),
                           ("simulate_plan", services.handle_simulate_plan, {"target_temp": 21.5}),
                           ("diagnose_interval", services.handle_diagnose_interval, {})):
        try:
            asyncio.run(fn(hass, SimpleNamespace(data=data, hass=hass, return_response=True)))
        except Exception as err:  # noqa: BLE001
            why.append(f"service {name} raised {type(err).__name__}: {err}")
    return why


def _planned_sub_min(result):
    """Plan steps whose total electrical level lies strictly in (0, p_min)."""
    sp = np.asarray(result.power_schedule, dtype=float)
    dh = np.asarray(getattr(result, "dhw_power_schedule", None) or np.zeros_like(sp), dtype=float)
    tot = sp + dh[: len(sp)]
    return int(np.sum((tot > 1e-3) & (tot < P_MIN - 1e-3)))


_READ = ("native_value", "extra_state_attributes", "is_on", "available", "current_temperature",
         "target_temperature", "hvac_mode", "hvac_action", "preset_mode", "min_temp", "max_temp")


def setup_stage(hass, coord):
    """--setup: every platform's real ``async_setup_entry`` on this cycle's
    coordinator, then every published property read; plus the diagnostics
    download. Returns the failures (a raise is the observable)."""
    import importlib

    entry = coord.entry
    entry.runtime_data = coord
    why, n = [], 0
    for plat in ("sensor", "binary_sensor", "button", "climate", "switch", "datetime"):
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")
        added = []

        def add(entities, *_a, _sink=added, **_k):
            for e in entities:
                e.hass = hass
            _sink.extend(entities)
        try:
            asyncio.run(mod.async_setup_entry(hass, entry, add))
        except Exception as err:  # noqa: BLE001
            why.append(f"setup {plat} raised {type(err).__name__}: {err}")
            continue
        for e in added:
            n += 1
            for attr in _READ:
                try:
                    getattr(e, attr, None)
                except Exception as err:  # noqa: BLE001
                    why.append(f"{plat} {getattr(e, '_attr_unique_id', e)}.{attr} raised {type(err).__name__}: {err}")
    try:
        from heatpump_optimizer import diagnostics
        asyncio.run(diagnostics.async_get_config_entry_diagnostics(hass, entry))
    except Exception as err:  # noqa: BLE001
        why.append(f"diagnostics raised {type(err).__name__}: {err}")
    return why, n


def run_cell(name, reference=False, drop_pv=False, setup=False, entry=False):
    extra_cfg, extra_states, surface, modulation = CELLS[name]
    base, bstates = (REF_BASE, REF_STATES) if reference else (GEN_BASE, GEN_STATES)
    cfg = {**base, **extra_cfg}
    if drop_pv:
        for k in ("pv_enabled", "pv_peak_kw", "pv_export_price", "away_enabled", "peak_tariff_enabled",
                  "peak_tariff_price_per_kw", c.CONF_PV_PRODUCTION_ENTITY):
            cfg.pop(k, None)
    states = {**bstates, **{k: FakeState(v.state, attributes=dict(v.attributes)) for k, v in extra_states.items()}}
    why = []
    data = None
    try:
        hass, coord = build(cfg, states, entry_id=f"d12s3_{name}_{int(reference)}", entry_setup=entry)
    except Exception as err:  # noqa: BLE001 -- setup not finishing is the first failing step
        return {"cell": name, "usable": False, "why": [f"setup raised {type(err).__name__}: {err}"],
                "sub_min": None, "calls": [], "entities": None}
    try:
        if name == "boost:short_space":
            now = dt_util.now()
            boost_mod.held_for(coord).set(boost_mod.CHANNEL_SPACE, True, now)
            boost_mod.held_for(coord).until[boost_mod.CHANNEL_SPACE] = now + timedelta(minutes=10)
        if name == "frequency:control_evidenced":
            coord._freq_map.buckets = {d: [0.04, 50] for d in range(10)}
            coord._freq_last_write = None  # past the designed 5-minute post-start hold (coordinator init stamp)
        data = asyncio.run(coord._async_update_data())
        if name == "metering:counter_dhw_spans":
            hass.states.set("sensor.hp_energy", FakeState("1000.6", attributes=dict(states["sensor.hp_energy"].attributes)))
            hass.states.set("sensor.heat_energy", FakeState("3001.9", attributes=dict(states["sensor.heat_energy"].attributes)))
            hass.states.set("sensor.dhw", T(53.0))
            data = asyncio.run(coord._async_update_data())
    except Exception as err:  # noqa: BLE001 -- a crash is the failing step
        why.append(f"cycle raised {type(err).__name__}: {err}")
    result = coord._optimization_result
    if data is None or not isinstance(data, dict):
        why.append("no payload")
    if result is None:
        why.append("no plan published")
    configured = {v for v in cfg.values() if isinstance(v, str)}
    hit = False
    for domain, service, payload in hass.services.calls:
        payload = payload or {}
        if domain == "mqtt":
            topic = payload.get("topic")
            if topic not in configured:
                why.append(f"mqtt publish to unconfigured topic {topic}")
            if surface == f"mqtt:{topic}":
                hit = True
                if name.endswith("set_topic"):
                    v = float(payload["payload"])
                    lo, hi = cfg[c.CONF_ECL110_DISPLACE_MIN], cfg[c.CONF_ECL110_DISPLACE_MAX]
                    if not lo <= v <= hi:
                        why.append(f"displace {v} outside [{lo},{hi}]")
            continue
        ent = payload.get("entity_id")
        if ent not in configured:
            why.append(f"{domain}.{service} to unconfigured {ent}")
            continue
        if ent.split(".", 1)[0] != domain and domain not in GENERIC_DOMAINS:
            why.append(f"{domain}.{service} sent to {ent} (domain mismatch)")
        if ent == surface:
            hit = True
        st = hass.states.get(ent)
        if service in ("set_temperature", "set_value") and st is not None:
            key = SETPOINT_SERVICES.get(domain, (None, "value"))[1]
            val = payload.get(key)
            lo, hi = _range_of(st)
            if val is not None and ((lo is not None and float(val) < float(lo) - 1e-9) or (hi is not None and float(val) > float(hi) + 1e-9)):
                why.append(f"{ent} written {val} outside its own range [{lo},{hi}]")
        if service == "select_option" and st is not None:
            if payload.get("option") not in st.attributes.get("options", ()):
                why.append(f"{ent} option {payload.get('option')!r} not offered")
    # The persistent heat-curve arm writes baseline + displace and skips a
    # target equal to the reading (heat_curve._write_persistent_target, W1):
    # a cycle whose displace rounds to 0 owes it no write (a harness gap the
    # first run of this cell read as a failure).
    displace = round(float((coord._current_action or {}).get("displace_value", 0.0) or 0.0))
    owed = surface and not (name == "heat_curve:number_persistent" and displace == 0)
    if owed and not hit:
        why.append(f"surface {surface} never actuated (displace {displace})")
    sub_min = None
    if modulation and result is not None:
        sub_min = _planned_sub_min(result)
        clamped = bool(coord._ctx._opt_config.clamp_planned_levels)
        if modulation == "on_off" and sub_min > 0:
            why.append(f"declared on/off but {sub_min} planned steps in (0,{P_MIN}) kW (clamp_planned_levels={clamped})")
        if modulation == "modulating" and clamped:
            why.append("declared modulating but the plan is projected onto {0}u[p_min,p_max]")
    calls = [(d, s, (p or {}).get("entity_id") or (p or {}).get("topic"),
              (p or {}).get("value", (p or {}).get("temperature", (p or {}).get("option", (p or {}).get("payload")))))
             for d, s, p in hass.services.calls]
    entities = None
    if entry:
        why.extend(entry_services(hass))
    if setup:
        setup_why, entities = setup_stage(hass, coord)
        why.extend(setup_why)
    return {"cell": name, "usable": not why, "why": why, "sub_min": sub_min, "calls": calls,
            "entities": entities}


def documented_declared_modulation(config):
    """``declared_modulation`` as its own docstring states it: on_off -> False."""
    cfg = config or {}
    mode = cfg.get(c.CONF_COMPRESSOR_MODULATION, c.DEFAULT_COMPRESSOR_MODULATION)
    legacy = cfg.get(c.CONF_CLAMP_PLANNED_LEVELS)
    return (False if mode == c.COMPRESSOR_MODULATION_ON_OFF
            else True if mode == c.COMPRESSOR_MODULATION_MODULATING
            else False if legacy is True else True if legacy is False else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--reference", action="store_true")
    ap.add_argument("--cell", action="append")
    ap.add_argument("--perturb", choices=["doc-modulation", "drop-pv", "range-keys"])
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--entry", action="store_true",
                    help="set each cell up through heatpump_optimizer.async_setup_entry, then drive three services")
    ap.add_argument("--setup", action="store_true",
                    help="also set every platform up on the cycle's coordinator, read every entity, download diagnostics")
    a = ap.parse_args()
    if a.list:
        for n in CELLS:
            print(n)
        return
    t0, c0 = time.time(), time.process_time()
    th0 = time.thread_time()
    patches = []
    if a.perturb == "doc-modulation":
        patches.append(mock.patch.object(thermal_model, "declared_modulation", documented_declared_modulation))
    if a.perturb == "range-keys":
        # C2's perturbation: the climate/water_heater min_temp/max_temp keys removed, so the
        # set-point range is read from min/max (the decoys); the climate cells must fail.
        from heatpump_optimizer import inputs as _inputs
        patches.append(mock.patch.object(_inputs, "_RANGE_KEYS", {}))
    for p in patches:
        p.start()
    try:
        rows = [run_cell(n, reference=a.reference, drop_pv=a.perturb == "drop-pv", setup=a.setup, entry=a.entry)
                for n in (a.cell or CELLS)]
    finally:
        for p in patches:
            p.stop()
    fails = [r for r in rows if not r["usable"]]
    for r in rows:
        ents = "" if r["entities"] is None else f"\tentities={r['entities']}"
        print(f"CELL {r['cell']}\t{'ok' if r['usable'] else 'FAIL'}\tsub_min={r['sub_min']}{ents}"
              f"\t{'; '.join(r['why'])}")
        if a.v:
            print("   calls:", r["calls"])
    arm = "reference" if a.reference else "generalization"
    print(f"RESULT arm={arm}")
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT fail_count={len(fails)} count")
    for r in rows:
        if r["sub_min"] is not None:
            print(f"RESULT sub_min_steps[{r['cell']}]={r['sub_min']} count")
    pc, tc = time.process_time() - c0, time.thread_time() - th0
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin"):
                sw = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
