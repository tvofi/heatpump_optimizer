"""D12-s3 (round 9): the D12.M4 usability bar over the installation x heat-pump cell grid.

Metric: count of cells failing D12.M4's bar -- setup fails, the first full
coordinator cycle raises, no plan and no named refusal, an entity property
raises, or the published plan/actuation invents plant the config omitted.
Count key: the value the production seams deliver (the coordinator's
``_async_update_data`` return dict, each platform entity's delivered
properties, and the service calls / MQTT publishes the cycle issued) --
never an input attribute of the fixture.

Run from the export root:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s3/usable.py [--grid full|ref|loo] [--perturb NAME] [--shard i/n]
  (full grid: run shards 0/4..3/4 and sum the counts; tools/audit/round9/D12/s3/sum_shards.py does it)

Drives (production symbols): heatpump_optimizer.async_setup_entry via
tests/harness.py:ha_setup_entry, coordinator:HeatPumpOptimizerCoordinator._async_update_data
(one full cycle: read inputs, solve, _apply_action, pump/frequency drive),
then every platform in const.PLATFORMS through its real async_setup_entry.

Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B7 (cloud container,
linux). Expected: see REPORT.md (counts exact; wall is informational only).

Perturbations (--perturb): see PERTURB below; each is an in-memory swap.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import importlib
import itertools
import json
import logging
import math
import sys
import tempfile
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

_TMP = tempfile.mkdtemp(prefix="d12s3_")
os.environ.setdefault("HPO_PLANDATA", os.path.join(_TMP, "plandata"))

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.disable(logging.CRITICAL)

BASE = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
}

# --- axes (values the tree already has slots for) ---------------------------
LAYOUT = {
    "single": ({}, {}),
    "two_zone": (
        {
            "upper_floor_thermal_mass": 3.0,
            "lower_floor_thermal_mass": 8.0,
            "upper_floor_heat_loss": 0.08,
            "lower_floor_heat_loss": 0.07,
            "lower_floor_temp_entity": "sensor.lower",
        },
        {"sensor.lower": ("20.5", "°C")},
    ),
    "two_zone_nosensor": (
        {
            "upper_floor_thermal_mass": 3.0,
            "lower_floor_thermal_mass": 8.0,
            "upper_floor_heat_loss": 0.08,
            "lower_floor_heat_loss": 0.07,
        },
        {},
    ),
    "valve": (
        {
            "mixing_valve_mode": "smart_write",
            "mixing_valve_write_entity": "number.valve",
            "valve_outlet_temp_entity": "sensor.valve_out",
        },
        {"number.valve": ("22.0", None), "sensor.valve_out": ("35.0", "°C")},
    ),
}
DHW = {
    "none": ({}, {}),
    "tank": ({"dhw_tank_volume": 200.0, "dhw_setpoint": 55.0, "dhw_min_temperature": 45.0}, {}),
    "tank_sensor": (
        {
            "dhw_tank_volume": 200.0,
            "dhw_setpoint": 55.0,
            "dhw_min_temperature": 45.0,
            "dhw_temp_entity": "sensor.dhw",
        },
        {"sensor.dhw": ("48.0", "°C")},
    ),
}
WOOD = {
    "none": ({}, {}),
    "wood": (
        {
            "wood_furnace_enabled": True,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_bottom_entity": "sensor.wood_bottom",
            "wood_tank_volume": 500.0,
            "external_heat_detection_enabled": True,
            "wood_type": "birch",
            "wood_packing": "packed",
            "wood_price_sek_m3": 900.0,
            "wood_furnace_efficiency": 75.0,
        },
        {"sensor.wood_top": ("60.0", "°C"), "sensor.wood_bottom": ("40.0", "°C")},
    ),
}
PV = {
    "none": ({}, {}),
    "pv": ({"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3}, {}),
    "pv_meter": (
        {
            "pv_enabled": True,
            "pv_peak_kw": 8.0,
            "pv_export_price": 0.3,
            "pv_production_entity": "sensor.pv_power",
        },
        {"sensor.pv_power": ("1500", "W")},
    ),
}
BUFFER = {
    "none": ({}, {}),
    "buffer": (
        {"buffer_tank_volume": 300.0, "buffer_tank_temp_entity": "sensor.buffer"},
        {"sensor.buffer": ("38.0", "°C")},
    ),
}
SURFACE = {
    "none": ({}, {}),
    "switch": ({"heat_pump_switch_entity": "switch.hp"}, {"switch.hp": ("on", None)}),
    "climate_onoff": ({"heat_pump_switch_entity": "climate.hp"}, {"climate.hp": ("heat", None)}),
    "number_setpoint": (
        {"space_setpoint_entity": "number.hp_setpoint"},
        {"number.hp_setpoint": ("21.0", "°C")},
    ),
    "ecl110": (
        {
            "ecl110_displace_set_topic": "ecl110/displace/set",
            "ecl110_state_topic": "ecl110/state",
        },
        {},
    ),
    "freq_modulating": (
        {
            "compressor_freq_entity": "number.hp_freq",
            "freq_control_mode": "control",
            "heat_pump_switch_entity": "switch.hp",
        },
        {"number.hp_freq": ("50", "Hz"), "switch.hp": ("on", None)},
    ),
}
AXES = (("layout", LAYOUT), ("dhw", DHW), ("wood", WOOD), ("pv", PV), ("buffer", BUFFER), ("surface", SURFACE))

# The fully-mapped reference plant (D12.M5 null control): every axis at its
# richest value plus coord_all_features' feature flags and every optional
# measurement slot the harness can honestly feed.
REF_EXTRA = (
    {
        "peak_tariff_enabled": True,
        "peak_tariff_price_per_kw": 45.0,
        "away_enabled": True,
        "comfort_learning_enabled": True,
        "system_identification_enabled": True,
        "compressor_cycling_cost": 0.5,
        "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_energy_entity": "sensor.hp_energy",
        "house_power_entity": "sensor.house_power",
        "floor_return_temp_entity": "sensor.floor_return",
        "solar_radiation_entity": "sensor.solar",
        "indoor_humidity_entity": "sensor.humidity",
        "heat_pump_supply_temp_entity": "sensor.hp_supply",
        "heat_pump_return_temp_entity": "sensor.hp_return",
        "heat_pump_defrost_entity": "binary_sensor.defrost",
        "dhw_setpoint_entity": "number.dhw_setpoint",
    },
    {
        "sensor.hp_power": ("1200", "W"),
        "sensor.hp_energy": ("1234.5", "kWh"),
        "sensor.house_power": ("2500", "W"),
        "sensor.floor_return": ("27.0", "°C"),
        "sensor.solar": ("120", "W/m²"),
        "sensor.humidity": ("45", "%"),
        "sensor.hp_supply": ("35.0", "°C"),
        "sensor.hp_return": ("30.0", "°C"),
        "binary_sensor.defrost": ("off", None),
        "number.dhw_setpoint": ("55", "°C"),
    },
)
REF_CELL = {"layout": "two_zone", "dhw": "tank_sensor", "wood": "wood", "pv": "pv_meter", "buffer": "buffer", "surface": "freq_modulating"}

SUBJECT = {
    # axis value that omits the plant -> tokens naming that plant's entities
    ("dhw", "none"): ("dhw", "hot_water", "legionella", "shower", "vvc", "disinfection", "mixed_water"),
    ("wood", "none"): ("wood",),
    ("pv", "none"): ("pv_",),
    ("buffer", "none"): ("buffer",),
}


def _seed(hass, states):
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set(
        "sensor.prices",
        FakeState(
            "0.5",
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(0.5 + 0.1 * (h % 4) + 0.4 * ((h % 24) >= 16), 3),
                    }
                    for h in range(48)
                ]
            },
        ),
    )
    hass.states.set("weather.home", FakeState("cloudy", attributes={"temperature": -3.0, "temperature_unit": "°C"}))
    hass.states.set("sensor.indoor", FakeState("21.0", unit="°C"))
    hass.states.set("sensor.outdoor", FakeState("-3.0", unit="°C"))
    for eid, (val, unit) in states.items():
        hass.states.set(eid, FakeState(val, unit=unit) if unit else FakeState(val))

    async def forecasts(call):
        return {
            "weather.home": {
                "forecast": [
                    {
                        "datetime": (now + timedelta(hours=h)).isoformat(),
                        "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                        "wind_speed": 3.0,
                        "precipitation": 0.0,
                        "humidity": 85.0,
                        "solar_irradiance": max(0.0, 300.0 * (1 - abs(12 - (h % 24)) / 6.0)),
                    }
                    for h in range(48)
                ]
            }
        }

    hass.services.async_register("weather", "get_forecasts", forecasts)
    hass.mqtt_published = []


def _cell_config(cell, extra=None):
    cfg = dict(BASE)
    states = {}
    for axis, table in AXES:
        c, s = table[cell[axis]]
        cfg.update(c)
        states.update(s)
    if extra:
        cfg.update(extra[0])
        states.update(extra[1])
    return cfg, states


def _read_entity(ent):
    out = {}
    for attr in ("available", "native_value", "is_on", "current_temperature", "target_temperature", "hvac_mode", "extra_state_attributes"):
        if not hasattr(type(ent), attr) and not hasattr(ent, attr):
            continue
        try:
            out[attr] = getattr(ent, attr)
        except Exception as err:  # noqa: BLE001
            out[attr] = err
    return out


def _entity_ids_in(obj):
    if isinstance(obj, dict):
        ids = []
        for k, v in obj.items():
            if k == "entity_id":
                ids.extend(v if isinstance(v, list) else [v])
            else:
                ids.extend(_entity_ids_in(v))
        return ids
    return []


def run_cell(cell, extra=None, drop=None):
    cfg, states = _cell_config(cell, extra)
    if drop:
        cfg.pop(drop, None)
    fails = []
    hass = FakeHass()
    _seed(hass, states)
    entry = FakeEntry(data=cfg)
    try:
        ok = asyncio.run(ha_setup_entry(integration, hass, entry))
    except Exception as err:  # noqa: BLE001
        return ["setup_raised:" + type(err).__name__ + ":" + str(err)[:80]], {}
    if not ok:
        return ["setup_false"], {}
    coord = entry.runtime_data
    hass.services.calls.clear()
    try:
        data = asyncio.run(coord._async_update_data())
    except Exception as err:  # noqa: BLE001
        return ["cycle_raised:" + type(err).__name__ + ":" + str(err)[:120]], {}
    coord.data = data
    sched = data.get("schedule") or []
    status = data.get("optimization_status")
    if not sched and status in (None, "optimal", ""):
        fails.append(f"no_plan_no_refusal:status={status}")
    # invented plant in the published plan
    if cell["dhw"] == "none":
        dp = [(r.get("dhw_power") or 0.0) for r in (data.get("dhw_plan") or {}).get("forecast", [])]
        if any(p > 0 for p in dp):
            fails.append("invented_dhw_plan")
    if cell["pv"] == "none":
        ps = [(r.get("pv_surplus") or 0.0) for r in (data.get("space_plan") or {}).get("forecast", [])]
        if any(p > 0 for p in ps):
            fails.append("invented_pv_surplus")
    if cell["wood"] == "none" and (data.get("wood_fuel") or {}).get("slots"):
        fails.append("invented_wood_slots")
    # invented actuation: a service call targeting an entity the config never named
    configured = {v for v in cfg.values() if isinstance(v, str)}
    for domain, service, payload in hass.services.calls:
        if domain == "weather":
            continue
        for eid in _entity_ids_in(payload or {}):
            if eid not in configured:
                fails.append(f"invented_actuation:{domain}.{service}:{eid}")
    # entities through the real platform setup
    entry.runtime_data = coord
    subjects = [tok for (axis, val), toks in SUBJECT.items() if cell[axis] == val for tok in toks]
    n_ent = 0
    for platform in const.PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{platform}")
        added = []
        try:
            asyncio.run(mod.async_setup_entry(hass, entry, added.extend))
        except Exception as err:  # noqa: BLE001
            fails.append(f"platform_raised:{platform}:{type(err).__name__}")
            continue
        for ent in added:
            n_ent += 1
            key = str(getattr(ent, "_key", None) or getattr(ent, "unique_id", None) or type(ent).__name__)
            got = _read_entity(ent)
            for attr, val in got.items():
                if isinstance(val, Exception):
                    fails.append(f"entity_raised:{platform}:{key}.{attr}:{type(val).__name__}")
            if got.get("available") is True:
                name = (key + type(ent).__name__).lower()
                val = got.get("native_value", got.get("is_on", got.get("current_temperature")))
                if any(t in name for t in subjects) and val not in (None, False, 0, 0.0, "unknown"):
                    fails.append(f"invented_entity:{key}={str(val)[:30]}")
    return sorted(set(fails)), {"status": status, "steps": len(sched), "entities": n_ent}


# In-memory perturbations (the judge's knob). Each must move the fail count.
PERTURB = {}


def _perturb_drop_dhw_guard():
    """Make the plan publisher ignore dhw_enabled: publish the optimizer's
    dhw power even when no tank is configured -> invented_dhw_plan fires on
    every dhw=none cell (direction: up)."""
    from heatpump_optimizer import coordinator as cm
    orig = cm.HeatPumpOptimizerCoordinator._build_data_dict

    def patched(self):
        d = orig(self)
        for r in (d.get("dhw_plan") or {}).get("forecast", []):
            r["dhw_power"] = 1.0
        return d

    cm.HeatPumpOptimizerCoordinator._build_data_dict = patched


PERTURB["force_dhw_power"] = _perturb_drop_dhw_guard


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=("full", "ref", "loo"), default="full")
    ap.add_argument("--perturb", choices=sorted(PERTURB), default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", default=None)
    ap.add_argument("--shard", default="0/1", help="i/n: run every n-th cell starting at i")
    args = ap.parse_args()
    if args.perturb:
        PERTURB[args.perturb]()
    t0 = time.process_time()
    tt0 = time.thread_time()
    w0 = time.perf_counter()
    rows = []
    if args.grid == "full":
        names = [a for a, _ in AXES]
        si, sn = (int(x) for x in args.shard.split("/"))
        for idx, combo in enumerate(itertools.product(*[list(t) for _, t in AXES])):
            if idx % sn != si:
                continue
            cell = dict(zip(names, combo))
            fails, info = run_cell(cell)
            rows.append({"cell": cell, "fails": fails, **info})
            print("CELL", idx, json.dumps(cell), fails[:4], info.get("status"), flush=True)
            if args.limit and len(rows) >= args.limit:
                break
    elif args.grid == "ref":
        fails, info = run_cell(REF_CELL, REF_EXTRA)
        rows.append({"cell": REF_CELL, "fails": fails, **info})
        # coord_all_features-shaped reference as well
        fails, info = run_cell(REF_CELL)
        rows.append({"cell": {**REF_CELL, "note": "axes only"}, "fails": fails, **info})
    else:  # leave-one-entity-out from the reference plant
        cfg, _ = _cell_config(REF_CELL, REF_EXTRA)
        optional = sorted(k for k, v in cfg.items() if k.endswith("_entity") and k not in ("price_entity", "weather_entity"))
        fails, info = run_cell(REF_CELL, REF_EXTRA)
        rows.append({"cell": {"drop": None}, "fails": fails, **info})
        for key in optional:
            fails, info = run_cell(REF_CELL, REF_EXTRA, drop=key)
            rows.append({"cell": {"drop": key}, "fails": fails, **info})
    cpu = time.process_time() - t0
    tcpu = time.thread_time() - tt0
    wall = time.perf_counter() - w0
    failing = [r for r in rows if r["fails"]]
    classes = {}
    for r in failing:
        for f in r["fails"]:
            c = f.split(":")[0]
            classes[c] = classes.get(c, 0) + 1
    for r in failing[:60]:
        print("FAIL", json.dumps(r["cell"]), r["fails"][:6], r.get("status"))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(rows, fh, default=str, indent=1)
    print(f"RESULT cells={len(rows)} count")
    print(f"RESULT failing_cells={len(failing)} count")
    for c, n in sorted(classes.items()):
        print(f"RESULT fail_class_{c}={n} count")
    print(f"RESULT wall_s={wall:.1f} s (provisional)")
    print(f"RESULT thread_factor={cpu / tcpu if tcpu else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = next((int(l.split()[1]) for l in fh if l.startswith("pswpin")), 0)
    except OSError:
        sw = 0
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
