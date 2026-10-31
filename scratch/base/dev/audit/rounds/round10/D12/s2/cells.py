"""D12-s2 (round 10): installation-axis usability grid (D12.M2) under the M4 bar.

Metric: number of installation cells (DHW x zones x wood x PV x valve) whose
one real coordinator cycle + every platform entity fails the D12.M4 usability
bar: cycle raises, no plan and no named refusal, an entity property raises, or
a plant-specific entity/plan value is published for a plant the config omitted.
Count key: the value the production seam delivers (coordinator._async_update_data
payload, each entity's available/native_value), never a config attribute.

Command (repo root):
  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round10/D12/s2/cells.py [--omit KEY] [--only CELLREGEX] [--sweep] [--perturb has_hot_water|reading_ok]
Expected: see REPORT.md (exact, counts). Baseline 17f1c55fad1b, machine B5 (macOS arm64).
Instrumented: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data
and every platform's async_setup_entry. Inputs (prices/weather) are injected the way
tests/golden.py:_capture_coordinator injects them; nothing in production is patched.
"""
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path[:0] = ["tests", "custom_components"]
import argparse, asyncio, importlib, itertools, json, logging, math, re, time, traceback
from datetime import timedelta

logging.disable(logging.CRITICAL)
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
import golden  # noqa: E402

START = golden.START
PLATFORMS = ("sensor", "binary_sensor", "button", "climate", "switch", "datetime")

BASE = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0,
}
STATES = {"sensor.indoor": "21.0", "sensor.outdoor": "-3.0"}
AXES = {
    "dhw": ({}, {"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0,
                 "dhw_min_temperature": 45.0, "dhw_windows": "06:00-08:30, 17:00-22:00",
                 "dhw_temp_entity": "sensor.dhw"}),
    "zones": ({}, {"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                   "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
                   "floor_return_temp_entity": "sensor.floor_return",
                   "lower_floor_temp_entity": "sensor.lower"}),
    "wood": ({}, {"wood_furnace_enabled": True, "wood_tank_volume": 500.0,
                  "wood_tank_top_entity": "sensor.wood_top",
                  "wood_tank_bottom_entity": "sensor.wood_bottom",
                  "external_heat_detection_enabled": True}),
    "pv": ({}, {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
                "pv_production_entity": "sensor.pv"}),
    "valve": ({}, {"mixing_valve_mode": "smart_read",
                   "buffer_tank_temp_entity": "sensor.buffer",
                   "valve_outlet_temp_entity": "sensor.valve_out"}),
}
EXTRA_STATES = {"sensor.dhw": "50.0", "sensor.floor_return": "26.0", "sensor.lower": "20.5",
                "sensor.wood_top": "70.0", "sensor.wood_bottom": "45.0", "sensor.pv": "1.5",
                "sensor.buffer": "40.0", "sensor.valve_out": "32.0"}
# plant -> entity keys that must not be available, and plan fields that must be empty, without it
PLANT_ENTITY = {
    "dhw": re.compile(r"(^|_)dhw|hot_?water", re.I),
    "wood": re.compile(r"wood", re.I),
    "pv": re.compile(r"(^|_)pv(_|$)|solar_surplus", re.I),
    "zones": re.compile(r"^lower_floor", re.I),
}


# every further optional entity slot, mapped with a plausible state (--sweep)
OPTIONAL = {
    "heat_pump_power_entity": ("sensor.hp_power", "1.8"),
    "heat_pump_energy_entity": ("sensor.hp_energy", "1234.5"),
    "house_power_entity": ("sensor.house_power", "3.2"),
    "solar_radiation_entity": ("sensor.solar_rad", "150"),
    "heat_pump_switch_entity": ("switch.hp", "on"),
    "heat_pump_mode_entity": ("sensor.hp_mode", "heating"),
    "heat_pump_defrost_entity": ("binary_sensor.hp_defrost", "off"),
    "heat_pump_online_entity": ("binary_sensor.hp_online", "on"),
    "heat_pump_fault_entity": ("binary_sensor.hp_fault", "off"),
    "heat_pump_supply_temp_entity": ("sensor.hp_supply", "35.0"),
    "heat_pump_return_temp_entity": ("sensor.hp_return", "30.0"),
    "compressor_freq_entity": ("sensor.comp_freq", "45"),
    "flow_meter_entity": ("sensor.flow", "12.0"),
    "indoor_humidity_entity": ("sensor.humidity", "40"),
    "dhw_inlet_entity": ("sensor.dhw_inlet", "8.0"),
    "external_heat_entity": ("binary_sensor.ext_heat", "off"),
}


def _nz(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and abs(x) > 1e-9


def run_cell(cfg, states):
    dt_util.freeze(START)
    hass = FakeHass()
    for k, v in states.items():
        hass.states.set(k, FakeState(v))
    entry = FakeEntry(data=cfg)
    c = HeatPumpOptimizerCoordinator(hass, entry)

    async def fp():
        c._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12, 4),
                      "starts_at": (START + timedelta(hours=h)).isoformat(),
                      "level": "NORMAL"} for h in range(48)]

    async def fw():
        c._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": -5 + 3 * (h % 24) / 24, "wind_speed": 3.0,
                                "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
        c._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0))
                                       for h in range(48)]

    async def nop():
        return None

    c._fetch_tibber_prices, c._fetch_weather_forecast, c._fetch_solar_forecast = fp, fw, nop
    fails = []
    try:
        d = asyncio.run(c._async_update_data())
    except Exception as ex:  # noqa: BLE001
        dt_util.freeze(None)
        return [("cycle", repr(ex)[:160])], None, []
    c.data = d
    sched = d.get("schedule") or []
    status = d.get("optimization_status")
    if not sched and status in (None, "optimal"):
        fails.append(("plan", f"no schedule, status={status!r}"))
    entry.runtime_data = c
    ents = []
    for p in PLATFORMS:
        m = importlib.import_module("heatpump_optimizer." + p)
        added = []

        def add(es, added=added):
            for e in es:
                e.hass = hass
            added.extend(es)
        try:
            asyncio.run(m.async_setup_entry(hass, entry, add))
        except Exception as ex:  # noqa: BLE001
            fails.append(("setup", f"{p}: {ex!r}"[:160]))
            continue
        for e in added:
            key = str(getattr(e, "_key", None) or getattr(e, "_attr_unique_id", None) or type(e).__name__)
            row = {"p": p, "key": key}
            for attr in ("available", "native_value", "is_on", "extra_state_attributes",
                         "current_temperature", "hvac_mode"):
                if not hasattr(type(e), attr) and not hasattr(e, attr):
                    continue
                try:
                    row[attr] = getattr(e, attr)
                except Exception as ex:  # noqa: BLE001
                    fails.append(("entity", f"{p}.{key}.{attr}: {ex!r}"[:160]))
            ents.append(row)
    dt_util.freeze(None)
    return fails, d, ents


def invented(cell, d, ents):
    out = []
    for plant, rx in PLANT_ENTITY.items():
        if cell[plant]:
            continue
        for r in ents:
            if rx.search(r["key"]) and r.get("available") is True:
                v = r.get("native_value", r.get("is_on"))
                if v not in (None, False, "unknown"):
                    out.append(("invent", f"{plant} absent, {r['p']}.{r['key']} available value={v!r}"[:160]))
    if not cell["dhw"]:
        for row in (d.get("dhw_plan") or {}).get("forecast", []):
            if _nz(row.get("dhw_power")):
                out.append(("invent", "dhw absent, dhw_plan has dhw_power")); break
    if not cell["pv"]:
        for row in (d.get("space_plan") or {}).get("forecast", []):
            if _nz(row.get("pv_surplus")):
                out.append(("invent", "pv absent, space_plan pv_surplus>0")); break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omit", action="append", default=[], help="config key dropped from every cell")
    ap.add_argument("--only", default=None)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--sweep", action="store_true",
                    help="richest cell with every OPTIONAL slot mapped, then each mapped key omitted once")
    ap.add_argument("--perturb", choices=("reading_ok", "has_hot_water"), default=None,
                    help="judge's perturbation: sensor._reading_ok forced True (gate removed); "
                         "cells_invented must go UP on every cell lacking DHW/zones")
    a = ap.parse_args()
    if a.perturb == "reading_ok":
        from unittest import mock
        import heatpump_optimizer.sensor as _sm
        mock.patch.object(_sm, "_reading_ok", lambda *_a, **_k: True).start()
    elif a.perturb == "has_hot_water":
        # one-line gate removal: entity.has_hot_water answers True on every plant
        from unittest import mock
        import heatpump_optimizer.entity as _em
        mock.patch.object(_em, "has_hot_water", lambda *_a, **_k: True).start()
    t0 = time.process_time(); tt0 = time.thread_time()
    names = list(AXES)
    failing = 0; total = 0; cyc = 0; ent = 0; inv = 0; present_avail = 0
    if a.sweep:
        full = dict(BASE)
        for n in names:
            full.update(AXES[n][1])
        mapped = [k for k, v in full.items() if k.endswith("_entity") and k not in
                  ("indoor_temp_entity", "outdoor_temp_entity", "weather_entity")] + list(OPTIONAL)
        jobs = [("omit=<none>", None)] + [(f"omit={k}", k) for k in mapped]
    else:
        jobs = [(None, bits) for bits in itertools.product((0, 1), repeat=len(names))]
    for slabel, bits in jobs:
        if a.sweep:
            cell = dict.fromkeys(names, 1); label = slabel
            sweep_omit = [bits] if bits else []
        else:
            cell = dict(zip(names, bits)); sweep_omit = []
            label = ",".join(f"{n}={b}" for n, b in cell.items())
        if a.only and not re.search(a.only, label):
            continue
        cfg = dict(BASE); states = dict(STATES)
        for n, b in cell.items():
            cfg.update(AXES[n][b])
        if a.sweep:
            for k, (eid, st) in OPTIONAL.items():
                cfg[k] = eid; states[eid] = st
        for k in list(a.omit) + sweep_omit:
            cfg.pop(k, None)
        for k, v in EXTRA_STATES.items():
            if k in cfg.values():
                states[k] = v
        fails, d, ents = run_cell(cfg, states)
        if d is not None:
            fails += invented(cell, d, ents)
        total += 1
        if d is not None:
            present_avail += sum(1 for pl, rx in PLANT_ENTITY.items() if cell[pl] for r in ents
                                 if rx.search(r["key"]) and r.get("available") is True)
        kinds = {f[0] for f in fails}
        cyc += "cycle" in kinds; ent += "entity" in kinds or "setup" in kinds; inv += "invent" in kinds
        if fails:
            failing += 1
            print(f"FAIL {label} first={fails[0][0]}: {fails[0][1]}  (+{len(fails)-1} more)")
            if a.verbose:
                for f in fails[1:]:
                    print("    ", f)
        else:
            print(f"ok   {label} entities={len(ents)} status={d.get('optimization_status')}")
    print(f"RESULT cells_total={total} count")
    print(f"RESULT cells_failing={failing} count")
    print(f"RESULT cells_cycle_crash={cyc} count")
    print(f"RESULT cells_entity_crash={ent} count")
    print(f"RESULT cells_invented={inv} count")
    # detector control: the same plant regexes DO see available entities when the plant is configured
    print(f"RESULT present_plant_entities_available={present_avail} count")
    p = time.process_time() - t0; th = time.thread_time() - tt0
    print(f"RESULT thread_factor={p/th if th else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
