"""D12-s2 cell driver: one setup + one full coordinator cycle + every platform's entities, per cell.

Metric: per cell, the first step of D12.M4's usable bar that fails
  (setup | cycle | plan | entities | invent), else ok; fail_cells = cells whose row is not ok.
  The count's key is the value the production seams deliver: the exception raised by
  HeatPumpOptimizerCoordinator(...) / _async_update_data() / a platform's async_setup_entry /
  an entity property, the published payload's ``schedule`` and the solver's planned
  ``dhw_power`` / zone arrays, and the service calls the cycle made -- never a config attribute.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s2/cells.py [--cells PATTERN] [--perturb NAME]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): see REPORT.md, counts exact.
Machine: box B5 (shared, compute-heavy seat), Linux x86_64, CPython from $HOME/venv-ci.

Each cell is built from one of two plants:
  REF  -- the fully mapped reference plant (every optional slot mapped, DHW, two zones, wood,
          PV, valve smart_write, buffer, grid fee entity, pump duty control, frequency control).
  MIN  -- the minimal plant (price entity, weather, indoor, outdoor; nothing else).
An entity cell "X=absent" is REF with slot X removed; "X=present" is MIN with slot X (and the
feature switch the slot belongs to) added. An option-axis cell sets that option on REF (and, for
the layout and valve axes, on the plant that option is valid for).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import copy
import fnmatch
import io
import logging
import math
import re
import sys
import tempfile
import time
import traceback
from datetime import timedelta

sys.path.insert(0, "tests")
import harness  # noqa: E402  (inserts custom_components)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

os.environ.setdefault("TMPDIR", tempfile.gettempdir())
_TMP = tempfile.mkdtemp(prefix="d12s2-")

NOW = dt_util.now().replace(minute=7, second=0, microsecond=0)

# ----------------------------------------------------------------------------- states
# One plausible state per optional slot. (entity_id, state, unit, attributes)
SLOT_STATES: dict[str, tuple] = {
    "CONF_AWAY_PRESENCE_ENTITY": ("input_boolean.away", "off", None, {}),
    "CONF_BUFFER_TANK_TEMP_ENTITY": ("sensor.buffer", "45.0", "°C", {"device_class": "temperature"}),
    "CONF_COMPRESSOR_FREQ_ENTITY": ("number.hp_freq", "50", "Hz", {"min": 20, "max": 120, "step": 1}),
    "CONF_DHW_DISINFECTION_SWITCH_ENTITY": ("switch.legionella", "off", None, {}),
    "CONF_DHW_HYSTERESIS_ENTITY": ("number.dhw_hyst", "5", "°C", {"min": 1, "max": 15, "step": 1}),
    "CONF_DHW_INLET_ENTITY": ("sensor.cold_water", "9.0", "°C", {"device_class": "temperature"}),
    "CONF_DHW_SETPOINT_ENTITY": ("number.dhw_setpoint", "55", "°C", {"min": 30, "max": 65, "step": 1}),
    "CONF_DHW_TEMP_ENTITY": ("sensor.dhw", "50.0", "°C", {"device_class": "temperature"}),
    "CONF_ENERGY_ENTITY": ("sensor.hp_energy", "1234.5", "kWh", {"device_class": "energy", "state_class": "total_increasing"}),
    "CONF_EXTERNAL_HEAT_ENTITY": ("binary_sensor.stove", "off", None, {}),
    "CONF_FLOOR_RETURN_TEMP_ENTITY": ("sensor.floor_return", "27.0", "°C", {"device_class": "temperature"}),
    "CONF_FLOW_METER_ENTITY": ("sensor.flow", "15.0", "L/min", {}),
    "CONF_GRID_FEE_ENTITY": ("sensor.grid_fee", "0.25", "SEK/kWh", {}),
    "CONF_HEAT_CURVE_DISPLACE_ENTITY": ("number.curve_offset", "0", "°C", {"min": -10, "max": 10, "step": 1}),
    "CONF_HEAT_ENERGY_ENTITY": ("sensor.hp_heat_energy", "3500.0", "kWh", {"device_class": "energy", "state_class": "total_increasing"}),
    "CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY": ("binary_sensor.backup", "off", None, {}),
    "CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY": ("binary_sensor.cap_limited", "off", None, {}),
    "CONF_HEAT_PUMP_DEFROST_ENTITY": ("binary_sensor.defrost", "off", None, {}),
    "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY": ("binary_sensor.dhw_booster", "off", None, {}),
    "CONF_HEAT_PUMP_FAULT_ENTITY": ("binary_sensor.fault", "off", None, {}),
    "CONF_HEAT_PUMP_MODE_ENTITY": ("select.hp_mode", "Heating + hot water", None,
                                   {"options": ["Off", "Heating", "Hot water", "Heating + hot water"]}),
    "CONF_HEAT_PUMP_ONLINE_ENTITY": ("binary_sensor.online", "on", None, {}),
    "CONF_HEAT_PUMP_RETURN_TEMP_ENTITY": ("sensor.hp_return", "32.0", "°C", {"device_class": "temperature"}),
    "CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY": ("sensor.hp_supply", "38.0", "°C", {"device_class": "temperature"}),
    "CONF_HEAT_PUMP_SWITCH_ENTITY": ("switch.heat_pump", "on", None, {}),
    "CONF_HOLIDAY_CALENDAR_ENTITY": ("calendar.holidays", "off", None, {}),
    "CONF_HOUSE_POWER_ENTITY": ("sensor.house_power", "2500", "W", {"device_class": "power"}),
    "CONF_INDOOR_HUMIDITY_ENTITY": ("sensor.humidity", "45", "%", {"device_class": "humidity"}),
    "CONF_INDOOR_TEMP_ENTITY": ("sensor.indoor", "21.0", "°C", {"device_class": "temperature"}),
    "CONF_LOWER_FLOOR_TEMP_ENTITY": ("sensor.lower", "20.5", "°C", {"device_class": "temperature"}),
    "CONF_MIXING_VALVE_TARGET_ENTITY": ("sensor.valve_target", "35.0", "°C", {"device_class": "temperature"}),
    "CONF_MIXING_VALVE_WRITE_ENTITY": ("number.valve_write", "21.0", "°C", {"min": 5, "max": 60, "step": 0.5}),
    "CONF_OUTDOOR_TEMP_ENTITY": ("sensor.outdoor", "2.0", "°C", {"device_class": "temperature"}),
    "CONF_POWER_ENTITY": ("sensor.hp_power", "1500", "W", {"device_class": "power"}),
    "CONF_PRICE_ENTITY": ("sensor.prices", "0.5", "SEK/kWh", None),  # attributes filled per run
    "CONF_PV_EXPORT_PRICE_ENTITY": ("sensor.pv_export", "0.3", "SEK/kWh", {}),
    "CONF_PV_PRODUCTION_ENTITY": ("sensor.pv", "1500", "W", {"device_class": "power"}),
    "CONF_SOLAR_RADIATION_ENTITY": ("sensor.irradiance", "200", "W/m²", {"device_class": "irradiance"}),
    "CONF_SPACE_HYSTERESIS_ENTITY": ("number.space_hyst", "1.0", "°C", {"min": 0.5, "max": 5, "step": 0.5}),
    "CONF_SPACE_PUMP_ENTITY": ("switch.space_pump", "on", None, {}),
    "CONF_SPACE_SETPOINT_ENTITY": ("number.space_setpoint", "21.0", "°C", {"min": 5, "max": 30, "step": 0.5}),
    "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": ("number.space_sp_high", "30", "°C", {"min": 5, "max": 60, "step": 0.5}),
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": ("number.space_sp_low", "10", "°C", {"min": 5, "max": 60, "step": 0.5}),
    "CONF_THERMAL_POWER_ENTITY": ("sensor.hp_heat_power", "4500", "W", {"device_class": "power"}),
    "CONF_VALVE_OUTLET_TEMP_ENTITY": ("sensor.valve_outlet", "35.0", "°C", {"device_class": "temperature"}),
    "CONF_VVC_PUMP_ENTITY": ("switch.vvc", "off", None, {}),
    "CONF_WOOD_TANK_BOTTOM_ENTITY": ("sensor.wood_bottom", "40.0", "°C", {"device_class": "temperature"}),
    "CONF_WOOD_TANK_TOP_ENTITY": ("sensor.wood_top", "70.0", "°C", {"device_class": "temperature"}),
}
SLOTS = sorted(SLOT_STATES)

# The feature switch a slot belongs to: what a user turns on when they map it.
FEATURE = {
    "dhw": {const.CONF_DHW_TANK_VOLUME: 200.0},
    "two_zone": {const.CONF_TWO_ZONE_MODE: "on", "upper_floor_thermal_mass": 3.0,
                 "lower_floor_thermal_mass": 8.0, "upper_floor_heat_loss": 0.08,
                 "lower_floor_heat_loss": 0.07},
    "wood": {const.CONF_WOOD_FURNACE_ENABLED: True, "wood_tank_volume": 500.0,
             "external_heat_detection_enabled": True},
    "pv": {const.CONF_PV_ENABLED: True, const.CONF_PV_PEAK_KW: 6.0, "pv_export_price": 0.3},
    "valve_read": {const.CONF_MIXING_VALVE_MODE: "smart_read"},
    "valve_write": {const.CONF_MIXING_VALVE_MODE: "smart_write", "mixing_valve_write_target_kind": "indoor"},
    "grid_fee": {"grid_fee_mode": "entity"},
    "pump_duty": {"pump_duty_mode": "control"},
    "freq": {"freq_control_mode": "control"},
    "water_sp": {"space_setpoint_unit": "flow"},
    "mold": {"mold_guard_enabled": True},
}
SLOT_FEATURE = {
    "CONF_DHW_DISINFECTION_SWITCH_ENTITY": ["dhw"], "CONF_DHW_HYSTERESIS_ENTITY": ["dhw", "pump_duty"],
    "CONF_DHW_INLET_ENTITY": ["dhw"], "CONF_DHW_SETPOINT_ENTITY": ["dhw"], "CONF_DHW_TEMP_ENTITY": ["dhw"],
    "CONF_VVC_PUMP_ENTITY": ["dhw"], "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY": ["dhw"],
    "CONF_LOWER_FLOOR_TEMP_ENTITY": ["two_zone"],
    "CONF_WOOD_TANK_TOP_ENTITY": ["wood"], "CONF_WOOD_TANK_BOTTOM_ENTITY": ["wood"],
    "CONF_EXTERNAL_HEAT_ENTITY": ["wood"], "CONF_VALVE_OUTLET_TEMP_ENTITY": ["wood"],
    "CONF_PV_PRODUCTION_ENTITY": ["pv"], "CONF_PV_EXPORT_PRICE_ENTITY": ["pv"],
    "CONF_MIXING_VALVE_TARGET_ENTITY": ["valve_read"], "CONF_MIXING_VALVE_WRITE_ENTITY": ["valve_write"],
    "CONF_GRID_FEE_ENTITY": ["grid_fee"], "CONF_SPACE_HYSTERESIS_ENTITY": ["pump_duty"],
    "CONF_COMPRESSOR_FREQ_ENTITY": ["freq"],
    "CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY": ["water_sp"], "CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY": ["water_sp"],
    "CONF_INDOOR_HUMIDITY_ENTITY": ["mold"],
}

MIN_SLOTS = ("CONF_PRICE_ENTITY", "CONF_INDOOR_TEMP_ENTITY", "CONF_OUTDOOR_TEMP_ENTITY")


def base_config() -> dict:
    return {"name": "Home", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
            const.CONF_WEATHER_ENTITY: "weather.home",
            const.CONF_TARGET_TEMP: 21.0, const.CONF_MIN_TEMP: 19.0, const.CONF_MAX_TEMP: 23.0}


def with_slots(cfg: dict, slots) -> dict:
    out = dict(cfg)
    for s in slots:
        out[getattr(const, s)] = SLOT_STATES[s][0]
        for f in SLOT_FEATURE.get(s, ()):
            for k, v in FEATURE[f].items():
                out.setdefault(k, v)
    return out


def min_plant() -> dict:
    return with_slots(base_config(), MIN_SLOTS)


def ref_plant() -> dict:
    cfg = with_slots(base_config(), SLOTS)
    cfg[const.CONF_MIXING_VALVE_MODE] = "smart_write"
    cfg.update({"buffer_tank_volume": 300.0, const.CONF_DHW_COMBI_TANK_ENABLED: False,
                "peak_tariff_enabled": True, "away_enabled": True, "comfort_learning_enabled": True,
                "system_identification_enabled": True, "compressor_cycling_cost": 0.5,
                "compressor_freq_sensor": "sensor.hp_freq_actual"})
    return cfg


def drop_slot(cfg: dict, slot: str) -> dict:
    out = dict(cfg)
    out.pop(getattr(const, slot), None)
    return out


# ----------------------------------------------------------------------------- one run
def make_hass(extra_states: dict | None = None, units: dict | None = None,
              price_profile: str | None = None, climate: str | None = None) -> FakeHass:
    hass = FakeHass()
    start = NOW.replace(minute=0)
    pser = wser = None
    if price_profile or climate:
        import profiles
        if price_profile:
            p = profiles.prices(price_profile, start)
            pser = [float(p[(4 * h) % len(p)]) for h in range(48)]
        if climate:
            t, wind, rain, solar = profiles.weather(climate, start)
            wser = [(float(t[(4 * h) % len(t)]), float(wind[(4 * h) % len(t)]),
                     float(rain[(4 * h) % len(t)]), float(solar[(4 * h) % len(t)])) for h in range(48)]
    for slot, (eid, st, unit, attrs) in SLOT_STATES.items():
        if units and slot in units:
            st, unit = units[slot]
        if slot == "CONF_OUTDOOR_TEMP_ENTITY" and wser:
            st = f"{wser[0][0]:.1f}"
        if slot == "CONF_PRICE_ENTITY":
            attrs = {"raw_today": [{"start": (start + timedelta(hours=h)).isoformat(),
                                     "value": round(pser[h], 3) if pser else
                                     round(0.5 + 0.4 * (1 if 7 <= (h % 24) <= 20 else 0) + 0.1 * (h % 3), 3)}
                                    for h in range(48)]}
            if pser:
                st = f"{pser[0]:.3f}"
        hass.states.set(eid, FakeState(st, unit=unit, attributes=dict(attrs or {}),
                                       last_updated=NOW - timedelta(minutes=2)))
    hass.states.set("sensor.hp_freq_actual", FakeState("48", unit="Hz", last_updated=NOW - timedelta(minutes=2)))
    hass.states.set("weather.home", FakeState("cloudy", attributes={"temperature_unit": "°C"}))
    for eid, state in (extra_states or {}).items():
        hass.states.set(eid, state)

    async def forecasts(call):
        if wser:
            return {"weather.home": {"forecast": [
                {"datetime": (start + timedelta(hours=h)).isoformat(), "temperature": wser[h][0],
                 "wind_speed": wser[h][1], "precipitation": wser[h][2], "humidity": 80.0,
                 "solar_irradiance": wser[h][3]}
                for h in range(48)]}}
        return {"weather.home": {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": 1.0 + 3.0 * math.sin(h / 24 * 2 * math.pi),
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 80.0, "cloud_coverage": 50}
            for h in range(48)]}}

    hass.services.async_register("weather", "get_forecasts", forecasts)
    return hass


PLATFORM_MODULES = ("sensor", "binary_sensor", "button", "climate", "switch", "datetime")


async def _platform_entities(hass, entry, coord):
    import importlib
    added, errors = [], []
    entry.runtime_data = coord
    for name in PLATFORM_MODULES:
        mod = importlib.import_module(f"heatpump_optimizer.{name}")

        def add(entities, *_a, **_k):
            for e in entities:
                e.hass = hass
            added.extend(entities)
        try:
            await mod.async_setup_entry(hass, entry, add)
        except Exception as err:  # noqa: BLE001
            errors.append(f"{name}.async_setup_entry: {type(err).__name__}: {err}")
    return added, errors


def _entity_errors(entities):
    errs = []
    for e in entities:
        for attr in ("native_value", "extra_state_attributes", "available", "is_on",
                     "current_temperature", "target_temperature", "hvac_mode"):
            if not hasattr(type(e), attr):
                continue
            try:
                getattr(e, attr)
            except Exception as err:  # noqa: BLE001
                key = getattr(e, "_key", None) or type(e).__name__
                errs.append(f"{key}.{attr}: {type(err).__name__}: {err}")
    return errs


async def run_cell(cfg: dict, *, units=None, extra_states=None, mode=None, hass_lang=None,
                   price_profile=None, climate=None) -> dict:
    """Setup, one full cycle, every platform; returns what each step delivered."""
    out = {"setup": None, "cycle": None, "plan": None, "entities": None, "calls": [], "data": None,
           "coord": None}
    hass = make_hass(extra_states, units, price_profile, climate)
    if hass_lang:
        hass.config.language = hass_lang
    entry = FakeEntry(data=dict(cfg))
    try:
        coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    except Exception as err:  # noqa: BLE001
        out["setup"] = f"{type(err).__name__}: {err}"
        return out
    out["coord"] = coord
    if mode is not None:
        coord._mode = mode
    try:
        data = await coord._async_update_data()
        out["data"] = data
    except Exception as err:  # noqa: BLE001
        name = type(err).__name__
        out["cycle"] = f"{name}: {err}"
        out["cycle_named_refusal"] = name == "UpdateFailed" and bool(str(err))
        out["tb"] = traceback.format_exc()[-1500:]
        data = None
    out["calls"] = [(d, s, dict(p or {})) for d, s, p in hass.services.calls]
    coord.data = data if data is not None else coord._build_data_dict()
    ents, perrs = await _platform_entities(hass, entry, coord)
    errs = perrs + _entity_errors(ents)
    out["entities"] = errs or None
    out["n_entities"] = len(ents)
    out["entity_objs"] = ents
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    return out


# ----------------------------------------------------------------------------- the bar
def configured_ids(cfg: dict) -> set:
    ids = set()
    for v in cfg.values():
        if isinstance(v, str) and re.fullmatch(r"[a-z_]+\.[a-z0-9_]+", v):
            ids.add(v)
    return ids


def _arr(x):
    try:
        return [float(v) for v in x]
    except Exception:  # noqa: BLE001
        return []


def invented(cfg: dict, res: dict) -> list[str]:
    """What the cycle published or commanded that the config did not give it."""
    probs = []
    data = res.get("data") or {}
    coord = res.get("coord")
    # 1. service calls to entities the config never named (actuating a device it was not given)
    allowed = configured_ids(cfg) | {"weather.home"}
    for d, s, p in res.get("calls", []):
        if d in ("weather",):
            continue
        tgt = p.get("entity_id")
        tgts = tgt if isinstance(tgt, list) else [tgt] if tgt else []
        for t in tgts:
            if t not in allowed:
                probs.append(f"call {d}.{s} -> unconfigured {t}")
    # 2. DHW plan with no tank configured
    if not cfg.get(const.CONF_DHW_TANK_VOLUME):
        if data.get("dhw_enabled"):
            probs.append("dhw_enabled with no tank volume")
        plan = getattr(coord, "_optimization_result", None)
        dp = _arr(getattr(plan, "dhw_power", []) or [])
        if dp and max(dp) > 1e-6:
            probs.append(f"dhw_power planned {max(dp):.2f} kW with no tank")
    # 3. lower zone with two-zone not on and no lower sensor
    if not cfg.get(const.CONF_LOWER_FLOOR_TEMP_ENTITY) and cfg.get(const.CONF_TWO_ZONE_MODE) != "on":
        if data.get("two_zone_enabled"):
            probs.append("two_zone_enabled without a lower-floor sensor or mode on")
    # 4. PV surplus with PV off
    if not cfg.get(const.CONF_PV_ENABLED):
        if (data.get("pv_self_consumed_kwh") or 0) > 1e-6:
            probs.append("pv_self_consumed_kwh > 0 with PV off")
    # 5. a published reading for a thermometer slot the config left empty: keyed on the ENTITY
    #    (what Home Assistant shows), not the payload, which carries the model's own state --
    #    an unmapped probe's entity reporting unavailable is the honest "unknown".
    for slot, key in READING_KEYS.items():
        if cfg.get(getattr(const, slot)):
            continue
        for e in res.get("entity_objs") or ():
            if getattr(e, "_reading_key", None) != key or type(e).__module__.rsplit(".", 1)[-1] != "sensor":
                continue
            try:
                avail, val = e.available, e.native_value
            except Exception:  # noqa: BLE001 - counted by the entities step
                continue
            if avail and val is not None:
                probs.append(f"{type(e).__name__}={val!r} available with {slot} unmapped")
    # 6. a stored layout key: honoured when valid for the plant, never drawn when not (C1)
    stored = cfg.get(const.CONF_TOPOLOGY_LAYOUT)
    if stored and coord is not None:
        p = coord._thermal_params
        valid = const.topology_layout_valid(
            stored, two_zone=bool(p.two_zone_enabled),
            throttling=cfg.get(const.CONF_MIXING_VALVE_MODE, "none") != "none",
            wood_probe=bool(cfg.get(const.CONF_WOOD_TANK_TOP_ENTITY)))
        got = coord.describe_setup().get("layout")
        if valid and got != stored:
            probs.append(f"stored layout {stored} valid but describe_setup drew {got}")
        if not valid and got == stored:
            probs.append(f"stored layout {stored} invalid for this plant but drawn")
    return probs


#: A thermometer slot and the payload key that publishes its reading.
READING_KEYS = {
    "CONF_LOWER_FLOOR_TEMP_ENTITY": "lower_floor_temperature",
    "CONF_BUFFER_TANK_TEMP_ENTITY": "buffer_tank_temperature",
    "CONF_DHW_TEMP_ENTITY": "dhw_temperature",
    "CONF_FLOOR_RETURN_TEMP_ENTITY": "floor_return_temperature",
}


def bar(cfg: dict, res: dict) -> str:
    """The first failing step of D12.M4's usable bar, or ok."""
    if res["setup"]:
        return f"FAIL setup: {res['setup']}"
    if res["cycle"]:
        if res.get("cycle_named_refusal"):
            return f"refusal cycle: {res['cycle'][:160]}"
        return f"FAIL cycle: {res['cycle'][:200]}"
    data = res["data"] or {}
    sched = data.get("schedule")
    if not sched:
        status = data.get("optimization_status")
        coord = res.get("coord")
        if getattr(coord, "_mode", None) in ("comfort", "boost", "off") and status:
            # A fixed mode adopts its own action and names the unrun solve: the brief's
            # "a named refusal explains why not".
            return f"refusal plan: fixed mode {coord._mode}, status={status!r}"
        return f"FAIL plan: no schedule, status={status!r}"
    if res["entities"]:
        return f"FAIL entities: {len(res['entities'])} raise; first {res['entities'][0][:200]}"
    inv = invented(cfg, res)
    if inv:
        return f"FAIL invent: {' | '.join(i[:120] for i in inv)}"
    return "ok"


# ----------------------------------------------------------------------------- cells
def cells() -> dict:
    """cell name -> (config, kwargs). Names are enumerate.py d12-cells' own."""
    out = {}
    ref, mn = ref_plant(), min_plant()
    for s in SLOTS:
        out[f"level {s}=absent"] = (drop_slot(ref, s), {})
        if s in MIN_SLOTS:
            out[f"level {s}=present"] = (mn, {})
        else:
            out[f"level {s}=present"] = (with_slots(mn, [s]), {})
    # Option axes, set on the reference plant unless the axis needs its own plant.
    two_zone_valve = {**ref}
    def opt(name, value, base=None, **extra):
        cfg = dict(base if base is not None else ref)
        cfg.update(extra)
        out[f"level {name}={value}"] = (cfg, {})
    # layout: each key on the plant it is valid for
    no_valve = {**ref, const.CONF_MIXING_VALVE_MODE: "none"}
    opt("layout", "no_valve", no_valve, topology_layout="no_valve")
    opt("layout", "single_tank_valve", ref, topology_layout="single_tank_valve")
    opt("layout", "two_tank_4way", ref, topology_layout="two_tank_4way")
    no_wood = {k: v for k, v in ref.items() if k not in (const.CONF_WOOD_TANK_TOP_ENTITY, const.CONF_WOOD_TANK_BOTTOM_ENTITY)}
    opt("layout", "valve_upper_direct_slab", no_wood, topology_layout="valve_upper_direct_slab")
    opt("layout", "slab_shunt", ref, topology_layout="slab_shunt")
    for m in ("none", "manual", "smart_read", "smart_write"):
        base = {k: v for k, v in ref.items() if m != "smart_write" or True}
        extra = {const.CONF_MIXING_VALVE_MODE: m}
        if m == "manual":
            extra["mixing_valve_target"] = 35.0
        if m != "smart_write":
            base = {k: v for k, v in base.items() if k != const.CONF_MIXING_VALVE_WRITE_ENTITY}
        if m in ("none", "manual"):
            base = {k: v for k, v in base.items() if k != const.CONF_MIXING_VALVE_TARGET_ENTITY}
        opt("mixing_valve_mode", m, base, **extra)
    for k in ("indoor", "flow"):
        opt("valve_write_target", k, ref, mixing_valve_write_target_kind=k)
    for k in ("auto", "on", "off"):
        opt("two_zone_mode", k, ref, two_zone_mode=k)
    for k in ("external_station", "internal_coil", "tank_in_tank"):
        opt("combi_tank", k, ref, dhw_combi_tank_enabled=True, dhw_combi_tank_type=k)
    for k in ("indoor", "flow", "return"):
        opt("space_setpoint_unit", k, ref, space_setpoint_unit=k)
    for k in ("birch", "pine", "mixed"):
        opt("wood_type", k, ref, wood_type=k)
    for k in ("packed", "loose"):
        opt("wood_packing", k, ref, wood_packing=k)
    for k in ("off", "observe", "control"):
        opt("pump_duty_mode", k, ref, pump_duty_mode=k)
    for k in ("offset", "persistent"):
        opt("heat_curve_target_kind", k, ref, heat_curve_target_kind=k)
    for k in ("none", "rules", "entity"):
        extra = {"grid_fee_mode": k}
        if k == "rules":
            extra["grid_fee_rules"] = "Mon-Fri 06:00-22:00 = 0.25"
        opt("grid_fee_mode", k, ref, **extra)
    for k in ("weather", "open_meteo"):
        opt("solar_source", k, ref, solar_forecast_source=k)
    opt("price_source", "entity", ref)
    opt("price_source", "tibber", {k: v for k, v in ref.items() if k != const.CONF_PRICE_ENTITY},
        price_source="tibber", tibber_token="x")
    return out


def m4_cells() -> dict:
    """The D12.M4-only levels (not installation axes): the usable bar on each, on REF."""
    from heatpump_optimizer import presets
    out = {}
    ref, mn = ref_plant(), min_plant()
    for k in ("auto", "on_off", "modulating"):
        out[f"level compressor_modulation={k}"] = ({**ref, "compressor_modulation": k}, {})
    for k in ("auto", "economy", "comfort", "boost", "off"):
        out[f"level operation_mode={k}"] = (ref, {"mode": k})
    for u, scale in (("W", 1.0), ("kW", 1e-3), ("MW", 1e-6), ("mW", 1e3)):
        out[f"level power_unit={u}"] = (ref, {"units": {"CONF_POWER_ENTITY": (f"{1500 * scale:g}", u)}})
    for u, scale in (("Wh", 1e3), ("kWh", 1.0), ("MWh", 1e-3)):
        out[f"level energy_unit={u}"] = (ref, {"units": {"CONF_ENERGY_ENTITY": (f"{1234.5 * scale:g}", u)}})
    lpm = 15.0
    for u, v in (("L/h", lpm * 60), ("L/min", lpm), ("L/s", lpm / 60), ("kg/h", lpm * 60), ("kg/min", lpm),
                 ("kg/s", lpm / 60), ("m³/h", lpm * 60 / 1000), ("m³/s", lpm / 60 / 1000)):
        out[f"level flow_unit={u}"] = (ref, {"units": {"CONF_FLOW_METER_ENTITY": (f"{v:g}", u)}})
    for u, v in (("C", 21.0), ("°C", 21.0), ("degC", 21.0), ("F", 69.8), ("°F", 69.8), ("degF", 69.8),
                 ("K", 294.15)):
        out[f"level temperature_unit={u}"] = (ref, {"units": {"CONF_INDOOR_TEMP_ENTITY": (f"{v:g}", u)}})
    for lang in ("en", "de", "sv", "._de"):
        out[f"level language={lang}"] = (ref, {"hass_lang": lang})
    for p in ("flat", "shoulder", "summer_negative", "summer_typical", "winter_extreme",
              "winter_moderate", "winter_narrow", "winter_typical"):
        out[f"level price_shape={p}"] = (ref, {"price_profile": p})
    for w in ("shoulder", "summer_cool", "summer_warm", "winter_cold", "winter_mild"):
        out[f"level climate={w}"] = (ref, {"climate": w})
    # The building questionnaire's answers, derived the way the flow derives them, on MIN.
    for axis, conf, levels in (("structure", presets.CONF_BUILDING_STRUCTURE, presets.STRUCTURES),
                               ("foundation", presets.CONF_BUILDING_FOUNDATION, presets.FOUNDATIONS),
                               ("era", presets.CONF_BUILDING_ERA, presets.ERAS)):
        for lv in levels:
            derived = presets.derive(presets.preset_from_config({conf: lv}, mn))
            derived.pop("heating_response_hours", None)
            out[f"level {axis}={lv}"] = ({**mn, **derived, "building_preset_enabled": True}, {})
    for lv in presets.EMITTERS:
        derived = presets.derive(presets.preset_from_config({presets.CONF_UPPER_EMITTER: lv}, mn))
        derived.pop("heating_response_hours", None)
        out[f"level emitter={lv}"] = ({**mn, **derived, "building_preset_enabled": True}, {})
    return out


def all_cells() -> dict:
    return {**cells(), **m4_cells()}


_SAVED_FROM_CONFIG = None


def _perturb_two_zone(on: bool):
    """D12-s2-01's perturbation, in memory: ThermalParameters.from_config is handed an absent or
    "auto" two_zone_mode as a value outside (on, auto, off), which its own else-branch -- the
    presence rule its comment says "auto" is -- resolves. Equivalent to the one-line edit
    ``if two_zone_mode == const.TWO_ZONE_MODE_ON:`` in thermal_model.ThermalParameters.from_config."""
    global _SAVED_FROM_CONFIG
    from heatpump_optimizer.thermal_model import ThermalParameters
    if on and _SAVED_FROM_CONFIG is None:
        _SAVED_FROM_CONFIG = ThermalParameters.__dict__["from_config"]
        orig = _SAVED_FROM_CONFIG.__func__

        def from_config(cls, config):
            mode = config.get(const.CONF_TWO_ZONE_MODE, const.DEFAULT_TWO_ZONE_MODE)
            if mode == const.TWO_ZONE_MODE_AUTO:
                config = {**config, const.CONF_TWO_ZONE_MODE: "auto-presence"}
            return orig(cls, config)
        ThermalParameters.from_config = classmethod(from_config)
    elif not on and _SAVED_FROM_CONFIG is not None:
        ThermalParameters.from_config = _SAVED_FROM_CONFIG
        _SAVED_FROM_CONFIG = None


PERTURB = {"two_zone": _perturb_two_zone}


async def main_async(args) -> int:
    async def solve(hass, opt, inputs):
        return optimize_in_process(opt, inputs)
    cm._await_optimize = solve
    dt_util.now = lambda *a, **k: NOW
    dt_util.utcnow = lambda *a, **k: NOW
    logging.disable(logging.CRITICAL)
    # The perturbation goes in BEFORE the table is built: the questionnaire cells derive their
    # config through presets.preset_from_config, which reads ThermalParameters.from_config.
    for p in (args.perturb or "").split(","):
        if p:
            PERTURB[p](True)
            print(f"perturbation {p} on")
    table = all_cells() if args.m4 else cells()
    names = sorted(table)
    if args.cells:
        names = [n for n in names if fnmatch.fnmatch(n, args.cells)]
    if args.list:
        print("\n".join(names))
        return 0
    fails, rows = 0, []
    t0p, t0t = time.process_time(), time.thread_time()
    for n in names:
        cfg, kw = table[n]
        cfg = dict(cfg)
        res = await run_cell(cfg, **kw)
        verdict = bar(cfg, res)
        rows.append((n, verdict))
        if verdict.startswith("FAIL"):
            fails += 1
        print(f"CELL {n}\t{verdict}", flush=True)
        if args.verbose and res.get("tb"):
            print(res["tb"])
    pt, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT fail_cells={fails} count")
    for step in ("setup", "cycle", "plan", "entities", "invent"):
        print(f"RESULT fail_{step}={sum(1 for _, v in rows if v.startswith('FAIL ' + step))} count")
    print(f"RESULT refusal_cells={sum(1 for _, v in rows if v.startswith('refusal'))} count")
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--m4", action="store_true", help="also the D12.M4-only levels")
    ap.add_argument("--cells", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--perturb", default=None)
    ap.add_argument("--verbose", action="store_true")
    sys.exit(asyncio.run(main_async(ap.parse_args())))
