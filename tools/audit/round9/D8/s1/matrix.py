#!/usr/bin/env python3
"""D8-s1 (audit round 9): the sensor/binary_sensor matrix, D8.M1 + D8.M2.

METRIC: per violation class, the number of (cell, cycle, entity) triples of the
  sensor and binary_sensor platforms that break the class's rule, after two real
  coordinator cycles (``HeatPumpOptimizerCoordinator._async_update_data``: input
  read, price fetch, weather fetch, solve, build) with changed inputs.
KEY: every count keys on what the entity property returns (``native_value`` /
  ``is_on`` / ``extra_state_attributes`` / ``available``), never on the payload.
RUN:   PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/matrix.py
       (--perturb-dhw-runs: D8-s1 DHW-periods perturbation, dhw_periods_vs_slots -> 0)
       (--only CELL_SUBSTRING to restrict; --dump to print every offender line)
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact, deterministic):
  see REPORT.md; each RESULT line is an exact count.
MACHINE: B6 cloud container, 4 CPU, CPython 3.14.0rc2, numpy 2.4.6 / OpenBLAS.
Clock: frozen, tz-aware Europe/Stockholm (HASTUB_TZ), as Home Assistant runs.
Substituted: the worker child (tests/replay.py:InProcessWorker, in-process
  run_worker), Tibber's fetch (injected hourly prices), weather.get_forecasts
  (a registered FakeServices handler). Nothing else.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import logging
import math
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)

import orjson  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from replay import InProcessWorker, units_table  # noqa: E402
from golden import coordinator_scenarios  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import binary_sensor, sensor  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.entity import commanded_power_kw  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
T0 = datetime(2026, 1, 15, 6, 10, tzinfo=TZ)
STEP = timedelta(minutes=15)
SHOW = False

# Two cycles of inputs; every probe moves between them.
INPUTS = [
    {"sensor.indoor": 21.4, "sensor.outdoor": -3.0, "sensor.dhw": 48.0,
     "sensor.lower": 20.5, "sensor.buffer": 38.0, "sensor.floor_return": 27.0,
     "sensor.wood_top": 60.0, "sensor.wood_bottom": 40.0, "sensor.valve_out": 35.0,
     "sensor.hp_power": 1200.0, "sensor.house_power": 3100.0,
     "select.hp_mode": "DHW", "sensor.freq": 40.0, "sensor.humidity": 55.0},
    {"sensor.indoor": 20.7, "sensor.outdoor": -7.0, "sensor.dhw": 42.0,
     "sensor.lower": 19.8, "sensor.buffer": 44.0, "sensor.floor_return": 30.0,
     "sensor.wood_top": 70.0, "sensor.wood_bottom": 45.0, "sensor.valve_out": 38.0,
     "sensor.hp_power": 2100.0, "sensor.house_power": 4200.0,
     "select.hp_mode": "DHW", "sensor.freq": 55.0, "sensor.humidity": 58.0},
]
UNITS = {"sensor.hp_power": "W", "sensor.house_power": "W", "sensor.freq": "Hz",
         "sensor.humidity": "%"}
for _k in INPUTS[0]:
    if _k not in UNITS and _k not in ("select.hp_mode",):
        UNITS[_k] = "°C"

THERMO = {"indoor_temp_entity": "sensor.indoor",
          "outdoor_temp_entity": "sensor.outdoor"}
FEATURES: dict[str, dict] = {
    "none": {},
    "dhw": {"dhw_tank_volume": 200.0, "dhw_temp_entity": "sensor.dhw"},
    "two_zone": {"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                 "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
                 "lower_floor_temp_entity": "sensor.lower",
                 "floor_return_temp_entity": "sensor.floor_return"},
    "valve": {"mixing_valve_mode": "manual", "mixing_valve_target": 21.0,
              "buffer_tank_temp_entity": "sensor.buffer",
              "buffer_tank_volume": 300.0},
    "two_tank": {"mixing_valve_mode": "manual", "mixing_valve_target": 21.0,
                 "buffer_tank_temp_entity": "sensor.buffer",
                 "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0,
                 "upper_floor_heat_loss": 0.08, "lower_floor_heat_loss": 0.07,
                 "wood_tank_top_entity": "sensor.wood_top",
                 "wood_tank_bottom_entity": "sensor.wood_bottom",
                 "valve_outlet_temp_entity": "sensor.valve_out",
                 "topology_layout": "two_tank_4way"},
    "coil": {"dhw_tank_volume": 200.0, "dhw_wood_coil_enabled": True,
             "wood_tank_top_entity": "sensor.wood_top",
             "wood_tank_bottom_entity": "sensor.wood_bottom"},
    "wood": {"wood_furnace_enabled": True,
             "wood_tank_top_entity": "sensor.wood_top",
             "wood_tank_bottom_entity": "sensor.wood_bottom"},
    "ecl110": {"ecl110_displace_set_topic": "ecl/displace/set",
               "ecl110_state_topic": "ecl/state"},
    "pv": {"pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3},
    "capacity": {"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
                 "house_power_entity": "sensor.house_power"},
    "grid_fee": {"grid_fee_mode": "rules",
                 "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
                 "grid_fee_fixed": 0.05},
    # DHW-only: the pump's own mode entity says DHW, so space is blocked.
    "tuya_dhw_only": {"dhw_tank_volume": 200.0, "dhw_temp_entity": "sensor.dhw",
                      "heat_pump_mode_entity": "select.hp_mode",
                      "mold_guard_enabled": True,
                      "indoor_humidity_entity": "sensor.humidity"},
    "away": {"away_enabled": True},
    "measured_power": {"heat_pump_power_entity": "sensor.hp_power"},
    # Minimum modulation: a pump whose floor is most of its range.
    "min_modulation": {"heat_pump_min_power": 1.5, "heat_pump_max_power": 2.0,
                       "dhw_tank_volume": 200.0},
}


def topologies() -> dict[str, dict]:
    out = {}
    for name, cfg in coordinator_scenarios().items():
        out[name] = {**cfg, **THERMO}
    # The install the shipping flow produces when every optional form is left
    # empty: no thermometer at all.
    out["coord_minimal_bare"] = dict(coordinator_scenarios()["coord_minimal"])
    return out


def build(config: dict):
    worker = InProcessWorker()
    cm._ensure_worker = lambda: worker
    hass = FakeHass()

    async def forecasts(call):
        now = dt_util.now()
        return {"weather.home": {"forecast": [
            {"datetime": (now + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)]}}

    hass.services.async_register("weather", "get_forecasts", forecasts)
    entry = FakeEntry(data=config)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord

    async def prices() -> None:
        now = dt_util.now()
        d0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0 + 0.01 * cycle_no[0], 4),
             "starts_at": (d0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(48)]

    cycle_no = [0]
    coord._fetch_tibber_prices = prices
    ents: list = []
    asyncio.run(sensor.async_setup_entry(hass, entry, ents.extend))
    asyncio.run(binary_sensor.async_setup_entry(hass, entry, ents.extend))
    return hass, coord, ents, cycle_no


def read(e) -> dict:
    platform = e.entity_id.split(".")[0]
    rec = {"entity_id": e.entity_id, "platform": platform,
           "available": bool(e.available)}
    if platform == "sensor":
        rec["state"] = e.native_value
        rec["unit"] = getattr(e, "native_unit_of_measurement", None)
        rec["state_class"] = getattr(e, "state_class", None) or getattr(e, "_attr_state_class", None)
        rec["options"] = getattr(e, "_attr_options", None)
    else:
        rec["state"] = e.is_on
        rec["unit"] = None
        rec["state_class"] = None
        rec["options"] = None
    rec["device_class"] = getattr(e, "device_class", None) or getattr(e, "_attr_device_class", None)
    rec["attributes"] = getattr(e, "extra_state_attributes", None)
    rec["category"] = getattr(e, "_attr_entity_category", None)
    rec["translation_key"] = getattr(e, "_attr_translation_key", None)
    rec["enabled_default"] = bool(getattr(e, "entity_registry_enabled_default",
                                          getattr(e, "_attr_entity_registry_enabled_default", True)))
    return rec


def _numeric(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _has_nonfinite(v) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, float):
        return not math.isfinite(v)
    if isinstance(v, dict):
        return any(_has_nonfinite(x) for x in v.values())
    if isinstance(v, (list, tuple)):
        return any(_has_nonfinite(x) for x in v)
    return False


def judge(rec: dict, table: dict) -> list[tuple[str, str]]:
    out = []
    eid = rec["entity_id"]
    for part in ("state", "attributes"):
        try:
            orjson.dumps(rec[part])
        except TypeError as err:
            out.append(("not_serialisable", f"{eid}.{part}: {err}"))
        if _has_nonfinite(rec[part]):
            out.append(("nonfinite", f"{eid}.{part}"))
    if not rec["available"]:
        return out
    st, sc, dc = rec["state"], rec["state_class"], rec["device_class"]
    dcs = str(dc) if dc is not None else None
    if sc is not None and st is not None and not _numeric(st):
        out.append(("measurement_nonnumeric", f"{eid}: {sc} state {st!r}"))
    if dcs == "timestamp" and st is not None and (
            not isinstance(st, datetime) or st.tzinfo is None):
        out.append(("timestamp_not_aware", f"{eid}: {st!r}"))
    if dcs == "enum" and st is not None and st not in (rec["options"] or []):
        out.append(("enum_not_option", f"{eid}: {st!r}"))
    if dcs and dcs not in ("enum", "timestamp", "monetary") and rec["platform"] == "sensor":
        allowed = table.get(dcs)
        if allowed is not None and rec["unit"] not in allowed:
            out.append(("unit_vs_device_class", f"{eid}: {dcs} in {rec['unit']!r}"))
    if st is None:
        out.append(("available_unknown", f"{eid}"))
    return out


def plan_oracle(data: dict) -> tuple[float | None, bool | None]:
    action = data.get("current_action") or {}
    if "power" not in action:
        return None, None
    kw = float(action.get("power") or 0.0) + float(action.get("dhw_power") or 0.0)
    return kw, action.get("heat_pump_on")


def operating(recs: list[dict], data: dict) -> list[tuple[str, str]]:
    """Operating-state entities against the plan's own draw."""
    out = []
    kw, on = plan_oracle(data)
    if kw is None:
        return out
    for rec in recs:
        if not rec["available"]:
            continue
        key = rec["translation_key"]
        attrs = rec["attributes"] or {}
        if key == "heat_pump_action":
            if rec["state"] in ("off", "idle") and on:
                out.append(("action_off_while_on", f"{rec['entity_id']}={rec['state']} heat_pump_on"))
            if rec["state"] not in ("off", "idle") and on is False:
                out.append(("action_running_while_off", f"{rec['entity_id']}={rec['state']} heat_pump_on=False"))
            if _numeric(attrs.get("power_kw")) and abs(attrs["power_kw"] - kw) > 0.05:
                out.append(("power_disagrees", f"{rec['entity_id']}.power_kw={attrs['power_kw']} plan={kw:.2f}"))
        if key == "recommended_power":
            if _numeric(rec["state"]) and abs(rec["state"] - kw) > 0.05:
                out.append(("power_disagrees", f"{rec['entity_id']}={rec['state']} plan={kw:.2f}"))
            if on is False and _numeric(rec["state"]) and rec["state"] > 0.05:
                out.append(("power_while_off", f"{rec['entity_id']}={rec['state']} heat_pump_on=False"))
    return out


def plan_views(recs: list[dict], data: dict) -> list[tuple[str, str]]:
    """One plan fact published twice must agree: the DHW Heating Schedule's
    count of "heating periods" against the DHW Heating Plan's slot count, and
    Current Electricity Price against the price the current plan step bought."""
    out = []
    by = {r["translation_key"]: r for r in recs}
    sched, plan = by.get("dhw_heating_schedule"), by.get("plan_dhw_heating")
    if sched and plan and sched["available"] and plan["available"]:
        st = sched["state"] or ""
        n = int(st.split()[0]) if st and st[0].isdigit() else 0
        slots = (plan["attributes"] or {}).get("slot_count")
        if isinstance(slots, int) and n != slots:
            out.append(("dhw_periods_vs_slots", f"{sched['entity_id']}={st!r} plan slot_count={slots}"))
    return out


def set_inputs(hass, values: dict, now: datetime) -> None:
    for eid, value in values.items():
        # The pump's mode is a select declaring its options, as the Tuya
        # integration publishes it (pump_mode.declares_current_option).
        attrs = ({"options": ["Heating", "DHW", "Heating + DHW", "Cooling"]}
                 if eid.startswith("select.") else None)
        hass.states.set(eid, FakeState(str(value), last_updated=now,
                                       unit=UNITS.get(eid), attributes=attrs))


def run_cell(name: str, config: dict, table: dict) -> dict:
    hass, coord, ents, cycle_no = build(config)
    cycles = []
    for c, inputs in enumerate(INPUTS):
        now = T0 + c * STEP
        dt_util.freeze(now)
        cycle_no[0] = c
        set_inputs(hass, inputs, now)
        err = None
        try:
            data = asyncio.run(coord._async_update_data())
            coord.data = data
            coord.last_update_success = True
        except Exception as exc:  # noqa: BLE001 - the observation
            err = f"{type(exc).__name__}: {exc}"
            data = coord.data or {}
        recs, viol = [], []
        if err:
            viol.append(("cycle_raises", f"{name}#{c}: {err}"))
        for e in ents:
            try:
                recs.append(read(e))
            except Exception as exc:  # noqa: BLE001
                viol.append(("property_raises", f"{e.entity_id}: {type(exc).__name__}: {exc}"))
        for r in recs:
            viol += judge(r, table)
        viol += operating(recs, data)
        viol += plan_views(recs, data)
        if SHOW:
            by = {r['translation_key']: r for r in recs}
            a = data.get('current_action') or {}
            print(f"  {name}#{c} action={by['heat_pump_action']['state']} on={a.get('heat_pump_on')} p={a.get('power')} dhw={a.get('dhw_power')} rec={by['recommended_power']['state']} sched={by['dhw_heating_schedule']['state']!r}/{by['dhw_heating_schedule']['available']} dhwplan={by['plan_dhw_heating']['state']!r}", flush=True)
        cycles.append({"recs": recs, "viol": viol, "data": data})
    dt_util.freeze(None)
    # The value follows the payload: a numeric sensor whose state did not
    # move although every input moved.
    unmoved = []
    by_id = [{r["entity_id"]: r for r in cyc["recs"]} for cyc in cycles]
    for eid, r0 in by_id[0].items():
        r1 = by_id[1].get(eid)
        if not r1 or not (r0["available"] and r1["available"]):
            continue
        if _numeric(r0["state"]) and r0["state"] == r1["state"]:
            unmoved.append(eid)
    return {"cycles": cycles, "unmoved": unmoved}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--perturb-dhw-runs", action="store_true",
                    help="perturbation: DHW Heating Schedule counts contiguous runs at the plan's 0.05 kW threshold")
    args = ap.parse_args(argv)
    global SHOW
    SHOW = args.show
    if args.perturb_dhw_runs:
        def runs(self):
            sched = (self.coordinator.data or {}).get("dhw_schedule") or []
            on = [s.get("dhw_power", 0) > 0.05 for s in sched]
            n = sum(1 for i, x in enumerate(on) if x and (i == 0 or not on[i - 1]))
            return f"{n} heating period{'s' if n != 1 else ''}" if sched else "no schedule"
        sensor.DHWScheduleSensor.native_value = property(runs)
    table = units_table()
    counts: dict[str, int] = {}
    lines: dict[str, list[str]] = {}
    unmoved: dict[str, int] = {}
    cells = 0
    t_cpu = time.process_time()
    t_thr = time.thread_time()
    for tname, tcfg in topologies().items():
        for fname, fcfg in FEATURES.items():
            cell = f"{tname}+{fname}"
            if args.only and args.only not in cell:
                continue
            cfg = {**tcfg, **fcfg}
            if tname == "coord_minimal_bare":
                # the bare install keeps its probes off, whatever the feature
                cfg = {k: v for k, v in cfg.items() if not k.endswith("_entity") or k in ("heat_pump_mode_entity", "weather_entity")}
            res = run_cell(cell, cfg, table)
            cells += 1
            for c, cyc in enumerate(res["cycles"]):
                for cls, line in cyc["viol"]:
                    counts[cls] = counts.get(cls, 0) + 1
                    lines.setdefault(cls, []).append(f"{cell}#{c} {line}")
            for eid in res["unmoved"]:
                unmoved[eid] = unmoved.get(eid, 0) + 1
    print(f"cells={cells}")
    for cls in sorted(lines):
        per_entity: dict[str, int] = {}
        for ln in lines[cls]:
            ent = ln.split(" ", 1)[1].split(":")[0].split("=")[0].split(".")[1] if "." in ln.split(" ", 1)[1] else ln
            per_entity[ent] = per_entity.get(ent, 0) + 1
        print(f"--- {cls}: {sum(per_entity.values())}")
        for ent, n in sorted(per_entity.items()):
            print(f"    {n:4d}  {ent}")
        if args.dump:
            for ln in lines[cls]:
                print("      ", ln)
    print("--- unmoved numeric state across the two cycles (cells):")
    for eid, n in sorted(unmoved.items()):
        print(f"    {n:4d}  {eid}")
    for cls in ("cycle_raises", "property_raises", "not_serialisable", "nonfinite",
                "measurement_nonnumeric", "timestamp_not_aware", "enum_not_option",
                "unit_vs_device_class", "available_unknown", "action_off_while_on",
                "action_running_while_off", "power_disagrees", "power_while_off",
                "dhw_periods_vs_slots"):
        print(f"RESULT {cls}={counts.get(cls, 0)} count")
    cpu = time.process_time() - t_cpu
    thr = time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        swap = "n/a"
    print(f"RESULT swapins={swap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
