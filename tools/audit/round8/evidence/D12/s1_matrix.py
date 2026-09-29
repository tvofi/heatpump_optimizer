"""D12 s1 -- installation-axis usability matrix.

Metric: count of plant cells (hydronic layout x DHW x wood x PV, plus the
reference plant with each optional entity slot omitted in turn) that fail the
"usable" bar: setup via __init__.async_setup_entry finishes, one full
coordinator cycle (_async_update_data -> async_run_optimization) publishes a
plan (OptimizationResult) or a named refusal, every entity platform sets up and
every entity's state/attributes read without raising, and the plan invents no
plant the config omitted (DHW power on a no-DHW cell, a wood trajectory on a
no-wood cell, a lower-zone trajectory on a one-zone cell, PV surplus on a no-PV
cell). The count key is what the production seams deliver (the plan object,
coord.data, entity properties), never the config.

Command (from tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D12/s1_matrix.py [--only NAME]
Expected: RESULT fail_cells=0 cells (exact) at baseline cdf82daa; see REPORT-s1.md.
Machine: 4-vCPU cloud Linux container (audit round 8 fan-out), not the M1 box.
Perturbation: --shrink drops one optional entity / DHW / wood / PV / a zone per
cell (the drop arms are part of the matrix itself); a one-line production edit
that makes a no-DHW plan carry DHW power moves fail_cells up.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import itertools
import json
import sys
import time
import traceback
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_mod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

PLATFORM_MODULES = ("sensor", "binary_sensor", "button", "climate", "switch", "datetime")

# ---------------------------------------------------------------- states
def base_states(now):
    start = now.replace(minute=0, second=0, microsecond=0)
    return {
        "sensor.prices": FakeState("0.5", attributes={"raw_today": [
            {"start": (start + timedelta(hours=h)).isoformat(),
             "value": round(0.5 + 0.4 * ((h % 24) in (7, 8, 17, 18, 19)) + 0.05 * (h % 3), 3)}
            for h in range(48)]}),
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-2.0", unit="°C"),
        "switch.heat_pump": FakeState("on"),
    }


OPTIONAL = {
    # key: (entity_id, state, unit)
    const.CONF_SOLAR_RADIATION_ENTITY: ("sensor.irr", "120", "W/m²"),
    const.CONF_POWER_ENTITY: ("sensor.hp_power", "1800", "W"),
    const.CONF_ENERGY_ENTITY: ("sensor.hp_energy", "1234.5", "kWh"),
    const.CONF_HOUSE_POWER_ENTITY: ("sensor.house_power", "2600", "W"),
    const.CONF_HEAT_PUMP_MODE_ENTITY: ("select.hp_mode", "heating", None),
    const.CONF_HEAT_PUMP_DEFROST_ENTITY: ("binary_sensor.defrost", "off", None),
    const.CONF_HEAT_PUMP_ONLINE_ENTITY: ("binary_sensor.online", "on", None),
    const.CONF_HEAT_PUMP_FAULT_ENTITY: ("binary_sensor.fault", "off", None),
    const.CONF_BUFFER_TANK_TEMP_ENTITY: ("sensor.buffer", "38.0", "°C"),
    const.CONF_FLOOR_RETURN_TEMP_ENTITY: ("sensor.floor_return", "27.0", "°C"),
}
DHW_ENTITIES = {const.CONF_DHW_TEMP_ENTITY: ("sensor.dhw", "50.0", "°C")}
ZONE2_ENTITIES = {const.CONF_LOWER_FLOOR_TEMP_ENTITY: ("sensor.lower", "20.5", "°C")}
PV_ENTITIES = {const.CONF_PV_PRODUCTION_ENTITY: ("sensor.pv", "1500", "W")}
WOOD_ENTITIES = {
    const.CONF_EXTERNAL_HEAT_ENTITY: ("binary_sensor.stove", "off", None),
    const.CONF_WOOD_TANK_TOP_ENTITY: ("sensor.wood_top", "65.0", "°C"),
    const.CONF_WOOD_TANK_BOTTOM_ENTITY: ("sensor.wood_bottom", "40.0", "°C"),
    const.CONF_VALVE_OUTLET_TEMP_ENTITY: ("sensor.valve_out", "34.0", "°C"),
}
VALVE_ENTITIES = {const.CONF_MIXING_VALVE_TARGET_ENTITY: ("sensor.valve_target", "21.0", "°C")}

BASE = {
    "name": "Home",
    const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
    const.CONF_PRICE_ENTITY: "sensor.prices",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.heat_pump",
}


def cell_config(zones, dhw, wood, pv, valve, entities=True):
    cfg = dict(BASE)
    ents = {}
    if entities:
        ents.update(OPTIONAL)
    cfg[const.CONF_TWO_ZONE_MODE] = "on" if zones == 2 else "off"
    if zones == 2:
        cfg.update({"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                    "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07})
        ents.update(ZONE2_ENTITIES)
    cfg[const.CONF_DHW_ENABLED] = bool(dhw)
    if dhw:
        cfg.update({const.CONF_DHW_TANK_VOLUME: 200.0, "dhw_setpoint": 55.0,
                    "dhw_min_temperature": 45.0, "dhw_windows": "06:00-08:30, 17:00-22:00"})
        if entities:
            ents.update(DHW_ENTITIES)
    cfg[const.CONF_WOOD_FURNACE_ENABLED] = wood != "none"
    if wood != "none":
        cfg[const.CONF_EXTERNAL_HEAT_ENABLED] = True
        ents[const.CONF_EXTERNAL_HEAT_ENTITY] = WOOD_ENTITIES[const.CONF_EXTERNAL_HEAT_ENTITY]
        if wood == "tanks":
            for k in (const.CONF_WOOD_TANK_TOP_ENTITY, const.CONF_WOOD_TANK_BOTTOM_ENTITY,
                      const.CONF_VALVE_OUTLET_TEMP_ENTITY):
                ents[k] = WOOD_ENTITIES[k]
    cfg[const.CONF_PV_ENABLED] = bool(pv)
    if pv:
        cfg[const.CONF_PV_PEAK_KW] = 6.0
        if entities:
            ents.update(PV_ENTITIES)
    if valve:
        cfg[const.CONF_MIXING_VALVE_MODE] = "smart_read"
        ents.update(VALVE_ENTITIES)
    for k, (eid, _s, _u) in ents.items():
        cfg[k] = eid
    return cfg, ents


# ---------------------------------------------------------------- one cell
def _read_entity(ent):
    for attr in ("native_value", "is_on", "current_temperature", "target_temperature",
                 "extra_state_attributes", "available", "hvac_mode"):
        if hasattr(type(ent), attr) or hasattr(ent, attr):
            getattr(ent, attr)


async def run_cell(name, cfg, ents, now):
    out = {"cell": name, "fail": None, "detail": "", "entities": 0}
    states = base_states(now)
    for _k, (eid, st, unit) in ents.items():
        states[eid] = FakeState(st, unit=unit) if unit else FakeState(st)
    hass = FakeHass(states)
    start = now.replace(minute=0, second=0, microsecond=0)

    async def _forecasts(call):
        return {call.data["entity_id"]: {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -4.0 + 4.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0,
             "solar_irradiance": max(0.0, 300.0 * (1 - abs(12 - (h % 24)) / 6.0))}
            for h in range(48)]}}

    hass.services.async_register("weather", "get_forecasts", _forecasts)
    entry = FakeEntry(data=dict(cfg), entry_id=f"e_{name}")
    try:
        ok = await ha_setup_entry(integration, hass, entry)
        if not ok:
            out.update(fail="setup", detail="async_setup_entry returned False")
            return out
    except Exception as err:  # noqa: BLE001
        out.update(fail="setup", detail=f"{type(err).__name__}: {err}")
        return out
    coord = entry.runtime_data
    try:
        coord.data = await coord._async_update_data()
    except Exception as err:  # noqa: BLE001
        out.update(fail="cycle", detail=f"{type(err).__name__}: {err}")
        return out
    res = coord._optimization_result
    if res is None:
        out.update(fail="no_plan", detail="no OptimizationResult after one full cycle")
        return out
    p = coord._thermal_params
    # invented plant, keyed on the delivered plan
    if not p.dhw_enabled and any(float(x) > 1e-6 for x in (res.dhw_power_schedule or [])):
        out.update(fail="invented_dhw", detail=f"max dhw kW={max(res.dhw_power_schedule):.3f}")
        return out
    if cfg[const.CONF_WOOD_FURNACE_ENABLED] is False and res.wood_temp_trajectory:
        out.update(fail="invented_wood", detail="wood_temp_trajectory on a no-wood cell")
        return out
    if not cfg[const.CONF_PV_ENABLED]:
        surplus = coord.data.get("forecast_pv_surplus") if isinstance(coord.data, dict) else None
        arr = coord._forecast_arrays(now).pv_surplus
        if np.any(np.asarray(arr, dtype=float) > 1e-6):
            out.update(fail="invented_pv", detail=f"pv_surplus max={float(np.max(arr)):.3f}")
            return out
    if cfg.get(const.CONF_TWO_ZONE_MODE) == "off" and coord.data.get("two_zone_enabled"):
        out.update(fail="invented_zone", detail="two_zone_enabled published on a one-zone cell")
        return out
    # entities
    errs = []
    n = 0
    for modname in PLATFORM_MODULES:
        mod = __import__(f"heatpump_optimizer.{modname}", fromlist=["x"])
        added = []
        try:
            await mod.async_setup_entry(hass, entry, added.extend)
        except Exception as err:  # noqa: BLE001
            errs.append(f"{modname}.setup {type(err).__name__}: {err}")
            continue
        for ent in added:
            n += 1
            try:
                _read_entity(ent)
            except Exception as err:  # noqa: BLE001
                errs.append(f"{type(ent).__name__} {type(err).__name__}: {err}")
    out["entities"] = n
    out["status"] = res.status
    out["dhw_kwh"] = round(float(np.sum(res.dhw_power_schedule or [0.0])) * 0.25, 3)
    out["space_kwh"] = round(float(np.sum(res.power_schedule)) * 0.25, 3)
    out["calls"] = [c[:2] + ((c[2] or {}).get("entity_id"),) for c in hass.services.calls
                    if c[0] not in ("weather",)]
    if errs:
        out.update(fail="entities", detail="; ".join(errs[:4]) + f" (+{max(0, len(errs)-4)})")
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    return out


def cells():
    grid = []
    for zones, dhw, wood, pv, valve in itertools.product((1, 2), (False, True),
                                                         ("none", "stove", "tanks"),
                                                         (False, True), (False, True)):
        name = f"z{zones}_{'dhw' if dhw else 'nodhw'}_{wood}_{'pv' if pv else 'nopv'}_{'valve' if valve else 'novalve'}"
        grid.append((name, zones, dhw, wood, pv, valve))
    return grid


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    real_solve = coordinator_mod._await_optimize

    async def solve_inline(hass, optimizer, state, *positional, **keywords):
        return optimize_in_process(optimizer, state, positional, keywords)

    coordinator_mod._await_optimize = solve_inline
    now = dt_util.now().replace(minute=7, second=0, microsecond=0)
    real_now = dt_util.now
    dt_util.now = lambda *a, **k: now
    t0p, t0t = time.process_time(), time.thread_time()
    rows = []
    try:
        todo = []
        for name, zones, dhw, wood, pv, valve in cells():
            cfg, ents = cell_config(zones, dhw, wood, pv, valve)
            todo.append((name, cfg, ents))
        # reference plant with each optional entity omitted in turn
        ref_cfg, ref_ents = cell_config(2, True, "tanks", True, True)
        for key in sorted(ref_ents):
            cfg = {k: v for k, v in ref_cfg.items() if k != key}
            ents = {k: v for k, v in ref_ents.items() if k != key}
            todo.append((f"ref_minus_{key}", cfg, ents))
        # entity-free cells: every optional entity unmapped
        for name, zones, dhw, wood, pv, valve in cells():
            if wood == "tanks":
                continue
            cfg, ents = cell_config(zones, dhw, wood, pv, valve, entities=False)
            todo.append((f"bare_{name}", cfg, ents))
        for name, cfg, ents in todo:
            if only and only not in name:
                continue
            try:
                row = asyncio.run(run_cell(name, cfg, ents, now))
            except Exception as err:  # noqa: BLE001
                row = {"cell": name, "fail": "harness", "detail": traceback.format_exc()[-300:]}
            rows.append(row)
            print(f"  {row['cell']:<70} {row.get('fail') or 'ok':<14} {row.get('status','')} "
                  f"space={row.get('space_kwh')} dhw={row.get('dhw_kwh')} ents={row.get('entities')} "
                  f"{row.get('detail','')[:200]}", flush=True)
    finally:
        coordinator_mod._await_optimize = real_solve
        dt_util.now = real_now
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    fails = [r for r in rows if r.get("fail")]
    with open(os.path.join(os.environ.get("TMPDIR", "/tmp"), "s1_matrix_rows.json"), "w") as fh:
        json.dump(rows, fh, indent=1, default=str)
    print(f"RESULT cells={len(rows)} cells")
    print(f"RESULT fail_cells={len(fails)} cells")
    by = {}
    for r in fails:
        by[r["fail"]] = by.get(r["fail"], 0) + 1
    for k, v in sorted(by.items()):
        print(f"RESULT fail_{k}={v} cells")
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [l for l in fh if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
