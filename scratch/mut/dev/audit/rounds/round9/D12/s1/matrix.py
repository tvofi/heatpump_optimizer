"""D12-s1 installation-axis matrix (D12.M1 inventory, D12.M2 axes).

Metric: per installation cell, the first failing step of
  setup (integration async_setup_entry) -> light refresh -> platform setup
  -> one full coordinator cycle (async_refresh) -> entity reads
plus 'invented plant' counts read from the published OptimizationResult /
data dict: plan fields carrying a DHW, wood, second-zone or PV quantity the
config did not give. Count key: the value the production seam delivers
(coordinator._optimization_result / coordinator.data), never a config attr.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/s1/matrix.py [--quick] [--json] [--entities | --entities-2z]
      (default: the plant-axis product; --entities: every entity slot added to
       the minimal plant and removed from the fully mapped rich plant;
       --entities-2z: each hydronic probe removed from the two-zone, valve,
       two-tank reference)
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B6 container (4 CPU).
Expected: see REPORT.md (counts exact).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import itertools
import json
import math
import sys
import time
import traceback
import logging
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import const, config_flow  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import (sensor, binary_sensor, button, climate,  # noqa: E402
                                switch)
from heatpump_optimizer import datetime as dt_platform  # noqa: E402

logging.disable(logging.CRITICAL)

from golden import START  # noqa: E402

PLATFORMS = (sensor, binary_sensor, button, climate, switch, dt_platform)

# ---------------------------------------------------------------- M1 inventory
ENTITY_KEYS = [r.key for r in config_flow._OPTION_FIELDS
               if type(r.widget).__name__ == "EntitySelector"]
from heatpump_optimizer import topology  # noqa: E402
SLOT_KEYS = list(topology.ASSIGNABLE_KEYS)


def state_for(key):
    k = key
    if "switch" in k and "entity" in k or k in ("vvc_pump_entity", "space_circulation_pump_entity"):
        return FakeState("on")
    if k in ("heat_pump_defrost_entity", "heat_pump_online_entity", "heat_pump_fault_entity",
             "heat_pump_backup_heater_entity", "heat_pump_dhw_booster_entity",
             "heat_pump_capacity_limited_entity", "away_presence_entity"):
        return FakeState("on" if k in ("heat_pump_online_entity", "away_presence_entity") else "off")
    if k == "external_heat_entity":
        return FakeState("off")
    if k == "heat_pump_mode_entity":
        return FakeState("heating")
    if k == "holiday_calendar_entity":
        return FakeState("off")
    if "power" in k:
        return FakeState("1500", unit="W")
    if "energy" in k:
        return FakeState("1234.5", unit="kWh")
    if "freq" in k:
        return FakeState("45", unit="Hz")
    if "humidity" in k:
        return FakeState("40", unit="%")
    if k == "solar_radiation_entity":
        return FakeState("120", unit="W/m²")
    if k in ("price_entity", "grid_fee_entity", "pv_export_price_entity"):
        return FakeState("0.5")
    if k == "dhw_temp_entity":
        return FakeState("50.0", unit="°C")
    if k == "wood_tank_top_entity":
        return FakeState("60.0", unit="°C")
    if k == "wood_tank_bottom_entity":
        return FakeState("40.0", unit="°C")
    if k == "buffer_tank_temp_entity":
        return FakeState("38.0", unit="°C")
    if k == "outdoor_temp_entity":
        return FakeState("-3.0", unit="°C")
    return FakeState("21.0", unit="°C")


BASE = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
    "indoor_temp_entity": "sensor.indoor_temp_entity",
    "outdoor_temp_entity": "sensor.outdoor_temp_entity",
}

ZONE2 = {
    "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
    "lower_floor_temp_entity": "sensor.lower_floor_temp_entity",
}
DHW = {"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0,
       "dhw_windows": "06:00-08:30, 17:00-22:00", "dhw_temp_entity": "sensor.dhw_temp_entity"}
WOOD = {"wood_furnace_enabled": True, "external_heat_detection_enabled": True,
        "wood_tank_top_entity": "sensor.wood_tank_top_entity",
        "wood_tank_bottom_entity": "sensor.wood_tank_bottom_entity",
        "external_heat_entity": "binary_sensor.external_heat_entity",
        "wood_tank_volume": 500.0}
PV = {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3}
VALVES = {
    "none": {"mixing_valve_mode": "none"},
    "manual": {"mixing_valve_mode": "manual", "mixing_valve_target": 21.0},
    "smart_read": {"mixing_valve_mode": "smart_read",
                   "mixing_valve_target_entity": "sensor.mixing_valve_target_entity"},
}
LAYOUTS = [None, const.TOPOLOGY_NO_VALVE, const.TOPOLOGY_SINGLE_TANK_VALVE,
           const.TOPOLOGY_TWO_TANK_4WAY, const.TOPOLOGY_VALVE_UPPER_DIRECT_SLAB]


def states_for(cfg):
    out = {}
    for k, v in cfg.items():
        if k.endswith("_entity") and isinstance(v, str) and "." in v and k != "weather_entity":
            out[v] = state_for(k)
    return out


def inject(coord):
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


async def _fake_prices(self):
    inject(self)


async def _noop(self):
    return None

coord_mod.HeatPumpOptimizerCoordinator._fetch_tibber_prices = _fake_prices
coord_mod.HeatPumpOptimizerCoordinator._fetch_weather_forecast = _noop
coord_mod.HeatPumpOptimizerCoordinator._fetch_solar_forecast = _noop

READ_ATTRS = ("native_value", "extra_state_attributes", "is_on", "available",
              "current_temperature", "target_temperature", "hvac_mode",
              "hvac_action", "preset_mode", "icon")


def read_entities(hass, entry):
    errs, n = [], 0
    for mod in PLATFORMS:
        added = []
        try:
            asyncio.run(mod.async_setup_entry(hass, entry, added.extend))
        except Exception as e:  # noqa: BLE001
            errs.append(f"platform {mod.__name__}: {type(e).__name__}: {e}")
            continue
        for ent in added:
            n += 1
            for a in READ_ATTRS:
                try:
                    getattr(ent, a, None)
                except Exception as e:  # noqa: BLE001
                    errs.append(f"{type(ent).__name__}.{a}: {type(e).__name__}: {e}")
    return n, errs


def _nz(xs, tol=1e-9):
    xs = [] if xs is None else list(xs)
    return sum(1 for x in xs if x is not None and isinstance(x, (int, float)) and not isinstance(x, bool)
               and math.isfinite(x) and abs(x) > tol)


def invented(coord, cfg):
    """Plant quantities the published plan carries that cfg did not give."""
    from heatpump_optimizer.thermal_model import ThermalParameters
    p = coord._thermal_model.params
    res = coord._optimization_result
    data = coord.data or {}
    out = {}
    if res is None:
        return out
    if not p.dhw_enabled:
        out["dhw_power_steps"] = _nz(res.dhw_power_schedule)
    if not p.two_zone_enabled:
        pass
    wood_on = bool(cfg.get("wood_furnace_enabled"))
    if not wood_on:
        out["wood_traj_steps"] = sum(1 for x in (res.wood_temp_trajectory or []) if x is not None)
    if not cfg.get("pv_enabled"):
        out["pv_surplus_steps"] = _nz(coord._forecast_arrays()[6])
    return {k: v for k, v in out.items() if v}


def run_cell(cfg):
    rec = {"first_fail": None, "detail": None}
    dt_util.freeze(START + timedelta(hours=10))
    try:
        hass = FakeHass(states_for(cfg))
        entry = FakeEntry(data=dict(cfg))
        try:
            ok = asyncio.run(integ.async_setup_entry(hass, entry))
        except Exception as e:  # noqa: BLE001
            rec.update(first_fail="setup", detail=f"{type(e).__name__}: {e}")
            return rec
        coord = entry.runtime_data
        rec["layout"] = coord._thermal_model.params.topology_layout
        n, errs = read_entities(hass, entry)
        rec["entities_light"] = n
        if errs:
            rec.update(first_fail="entities_light", detail=errs[:3])
            return rec
        async def cyc():
            await coord.async_refresh()
        asyncio.run(cyc())
        if not coord.last_update_success:
            rec.update(first_fail="cycle", detail=repr(coord.last_exception))
            return rec
        if coord._optimization_result is None:
            rec.update(first_fail="no_plan", detail=None)
            return rec
        rec["status"] = coord._optimization_result.status
        n, errs = read_entities(hass, entry)
        rec["entities_cycle"] = n
        if errs:
            rec.update(first_fail="entities_cycle", detail=errs[:3])
            return rec
        inv = invented(coord, cfg)
        if inv:
            rec.update(first_fail="invented", detail=inv)
        return rec
    except Exception as e:  # noqa: BLE001
        rec.update(first_fail="harness", detail=traceback.format_exc()[-400:])
        return rec
    finally:
        dt_util.freeze(None)


def plant_cells():
    for zones, dhw, wood, pv, valve, layout in itertools.product(
            (1, 2), (0, 1), (0, 1), (0, 1), VALVES, LAYOUTS):
        throttling = valve != "none"
        if layout is not None and not const.topology_layout_valid(
                layout, two_zone=zones == 2, throttling=throttling, wood_probe=bool(wood)):
            continue
        cfg = dict(BASE)
        if zones == 2: cfg.update(ZONE2)
        if dhw: cfg.update(DHW)
        if wood: cfg.update(WOOD)
        if pv: cfg.update(PV)
        cfg.update(VALVES[valve])
        if layout: cfg["topology_layout"] = layout
        name = f"z{zones}-dhw{dhw}-wood{wood}-pv{pv}-v_{valve}-L_{layout or 'auto'}"
        yield name, cfg


def entity_cells():
    """Every EntitySelector key both added to the minimal plant and removed
    from the fully mapped rich plant (one-at-a-time)."""
    def ent(k):
        dom = "switch" if ("switch" in k or "pump_entity" in k) else (
            "binary_sensor" if k in ("heat_pump_defrost_entity", "heat_pump_online_entity",
                                     "heat_pump_fault_entity", "external_heat_entity",
                                     "away_presence_entity") else "sensor")
        return f"{dom}.{k}"
    rich = dict(BASE); rich.update(DHW); rich.update(WOOD); rich.update(PV)
    rich.update({k: ent(k) for k in ENTITY_KEYS})
    rich["weather_entity"] = "weather.home"
    yield "rich-all-mapped", rich
    for k in ENTITY_KEYS:
        if k in ("weather_entity",):
            continue
        cfg = dict(BASE); cfg[k] = ent(k)
        yield f"minimal+{k}", cfg
        cfg = dict(rich); cfg.pop(k, None)
        yield f"rich-{k}", cfg


TWO_Z_KEYS = ("lower_floor_temp_entity", "floor_return_temp_entity",
              "mixing_valve_target_entity", "wood_tank_top_entity",
              "wood_tank_bottom_entity", "valve_outlet_temp_entity",
              "external_heat_entity", "buffer_tank_temp_entity", "dhw_temp_entity")


def entity_cells_2z():
    """The two-zone, valve, two-tank reference with each hydronic probe
    removed one at a time (the layout-bearing slots)."""
    ref = dict(BASE); ref.update(ZONE2); ref.update(DHW); ref.update(WOOD)
    ref.update(VALVES["smart_read"])
    ref.update({"floor_return_temp_entity": "sensor.floor_return_temp_entity",
                "valve_outlet_temp_entity": "sensor.valve_outlet_temp_entity",
                "buffer_tank_temp_entity": "sensor.buffer_tank_temp_entity",
                "topology_layout": const.TOPOLOGY_TWO_TANK_4WAY})
    yield "2z-ref", ref
    for k in TWO_Z_KEYS:
        cfg = dict(ref); cfg.pop(k, None)
        yield f"2z-{k}", cfg
    both = dict(ref)
    for k in ("wood_tank_top_entity", "wood_tank_bottom_entity"):
        both.pop(k)
    yield "2z-no-wood-probes", both


def main():
    quick = "--quick" in sys.argv
    t0 = time.process_time(); tt0 = time.thread_time()
    if "--entities-2z" in sys.argv:
        cells = list(entity_cells_2z())
    elif "--entities" in sys.argv:
        cells = list(entity_cells())
    else:
        cells = list(plant_cells())
    if quick:
        cells = cells[::7]
    print(f"RESULT entity_slot_keys_options={len(ENTITY_KEYS)} count")
    print(f"RESULT entity_slot_keys_topology={len(SLOT_KEYS)} count")
    print(f"RESULT plant_cells={len(cells)} count")
    fails = {}
    results = {}
    for name, cfg in cells:
        t = time.time()
        rec = run_cell(cfg)
        rec["wall_s"] = round(time.time() - t, 2)
        results[name] = rec
        print(f"cell {name} {rec['first_fail']} {rec['wall_s']}s", flush=True)
        if rec["first_fail"]:
            fails[name] = rec
            print(f"FAIL {name}: {rec['first_fail']} {rec['detail']}")
    print(f"RESULT plant_fail_cells={len(fails)} count")
    from collections import Counter
    for step, c in Counter(r['first_fail'] for r in fails.values()).items():
        print(f"RESULT plant_fail_{step}={c} count")
    if "--json" in sys.argv:
        import tempfile
        out = os.path.join(tempfile.mkdtemp(prefix="d12s1_"), "matrix.json")
        json.dump(results, open(out, "w"), indent=1, default=str)
        print(f"json: {out}")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
