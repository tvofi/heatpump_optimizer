#!/usr/bin/env python3
"""D1-s3 M5: a workload script for local_inject.py -- direct calls into the d1-excepts handlers no
test script and no lifecycle phase reached (process worker, store loaders, small parse guards).

Not a harness on its own: it only supplies calls. Run under the injection arm:
    PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/local_inject.py --script dev/audit/rounds/round11/D1/s3/drivers_misc.py \
        --out dev/audit/rounds/round11/D1/s3/out/loc2/drivers_misc.jsonl
Every call is wrapped so one raised call never stops the next: the arm records what the
production handler did, not what this script does with it.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import io
import pickle
import sys
import traceback
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

CALLS = []


def call(name, fn, *a, **k):
    try:
        out = fn(*a, **k)
        if asyncio.iscoroutine(out):
            out = asyncio.run(out)
        CALLS.append((name, "ok"))
        return out
    except BaseException as err:  # noqa: BLE001 - the arm reads the handler, not this
        CALLS.append((name, type(err).__name__))
        return None


NOW = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)

# --- process worker (runs in a child in production; driven in-process here)
from heatpump_optimizer import process_worker as pw  # noqa: E402

call("pw._bootstrap", pw._bootstrap)


class _Bad:
    def __str__(self):
        raise RuntimeError("str")


call("pw._describe", pw._describe, _Bad())
call("pw._describe ok", pw._describe, 1)
call("pw._dump unpicklable", pw._dump, io.BytesIO(), ("ok", lambda: 1))
call("pw._dump ok", pw._dump, io.BytesIO(), ("ok", 1))
jobs = pickle.dumps((len, ([1, 2],))) + pickle.dumps((int, ("x",))) + b"garbage-not-a-pickle"
saved = sys.stdin, sys.stdout
sys.stdin = SimpleNamespace(buffer=io.BytesIO(jobs))
sys.stdout = SimpleNamespace(buffer=io.BytesIO())
call("pw.run_worker", pw.run_worker)
sys.stdin, sys.stdout = saved

# --- coordinator: the worker's lifecycle, the off-loop waits
import heatpump_optimizer.coordinator as cmod  # noqa: E402

call("cmod._run_in_process", cmod._run_in_process, len, ([1],))
call("cmod._shutdown_process_pool", cmod._shutdown_process_pool)
call("cmod._run_in_process 2", cmod._run_in_process, len, ([1],))
call("cmod._shutdown_process_pool at_exit", cmod._shutdown_process_pool, True)
hass = FakeHass()
call("cmod._await_off_loop", cmod._await_off_loop, hass, len, [1])
call("cmod._thermal_param_changes", getattr(cmod, "_thermal_param_changes", len), {"a": 1}, {"a": 2})

# --- stored-record loaders: each from_dict over its own healthy record
from heatpump_optimizer import (  # noqa: E402
    accuracy, dhw_draws, draw_range, duty_switch, freq_control, manual_plan, snapshots, tariff, wear,
)

for cls in (accuracy.AccuracyTracker, dhw_draws.DrawStats, draw_range.DrawRange, freq_control.FrequencyMap,
            tariff.PeakTracker, wear.StartCounter, snapshots.SnapshotRing):
    inst = call(f"{cls.__name__}()", cls)
    rec = call(f"{cls.__name__}.as_dict", inst.as_dict) if inst is not None else None
    call(f"{cls.__name__}.from_dict", cls.from_dict, rec if rec is not None else {})
    call(f"{cls.__name__}.from_dict garbage", cls.from_dict, {"a": "x", "samples": [{"x": 1}], "peaks": [[1, "x"]]})
call("DutySwitchLearner.from_record", duty_switch.DutySwitchLearner.from_record, {"version": 1, "cells": {"a": [1, 2]}})
call("ManualOverride.from_dict", manual_plan.ManualOverride.from_dict,
     {"space": [{"start": "2026-01-15T13:00:00+00:00", "end": "2026-01-15T14:00:00+00:00", "value": 1.0}],
      "expires_at": "2026-01-15T18:00:00+00:00", "created_at": "2026-01-15T12:00:00+00:00"})
call("manual_plan._parse_dt", manual_plan._parse_dt, "2026-01-15T13:00:00+00:00", NOW)
call("tariff._stored_peaks", tariff._stored_peaks, [[1.0, "2026-01-15"]], 3)
call("draw_range._stored_ceiling", draw_range._stored_ceiling, [[1.0, 2.0]])
call("draw_range._command_cells", draw_range._command_cells, [1.0, 2.0])

# --- small parse guards
from heatpump_optimizer import (  # noqa: E402
    boost, drift, dhw_schedule, price_tiles, quiet_windows, store, wood_fuel, whatif,
)
import heatpump_optimizer as integ  # noqa: E402

call("drift._positive_definite", drift._positive_definite, [1.0, 0.0, 0.0, 1.0], 2)
call("drift._positive_definite bad", drift._positive_definite, [1.0, 2.0, 2.0, 1.0], 2)
call("price_tiles._aware", price_tiles._aware, "2026-01-15T00:00:00+00:00")
call("boost._due_inside_horizon", boost._due_inside_horizon,
     SimpleNamespace(data={"dhw_legionella_due_in_hours": 3.0, "horizon_hours": 24.0}))
call("boost._window_open", boost._window_open,
     SimpleNamespace(plan=SimpleNamespace(predictive_info={"dhw_windows": "06:00-08:00"}),
                     params=SimpleNamespace(dhw_demand_windows=[])), NOW)
call("dhw_schedule._parse_day_selector", dhw_schedule._parse_day_selector, "Mon-Fri")
call("dhw_schedule._parse_day_selector 2", dhw_schedule._parse_day_selector, "Mon,Wed")
call("quiet_windows.silent_cap_kw", quiet_windows.silent_cap_kw, {"silent_mode_power_fraction": 0.5}, None, 5.0)
call("quiet_windows._parse_spec_pair", quiet_windows._parse_spec_pair, "22:00-06:00", "10:00-11:00")
call("quiet_windows.overlap_problem", quiet_windows.overlap_problem, "22:00-06:00", "10:00-11:00", "06:00-08:00")
call("store.in_domain", store.in_domain, SimpleNamespace(null=False, kind="real", lo=0, hi=10), "5")
call("integ._take_fresh_handover", integ._take_fresh_handover, hass, "e", 60.0)
integ._plan_handovers(hass)["e"] = {"x": 1}
integ._handover_stamps(hass)["e"] = NOW
call("integ._take_fresh_handover stamped", integ._take_fresh_handover, hass, "e", 60.0)
stamps = [NOW + timedelta(minutes=15 * i) for i in range(8)]
call("wood_fuel._as_dt", wood_fuel._as_dt, NOW.isoformat(), stamps)
call("wood_fuel.wood_fuel_ready", wood_fuel.wood_fuel_ready, {"wood_furnace_enabled": True, "wood_furnace_kw": "8"})
call("wood_fuel.wood_slots_to_kw", wood_fuel.wood_slots_to_kw, [{"start": NOW.isoformat(), "kw": 3}], stamps)
call("wood_fuel._wood_slots_error", wood_fuel._wood_slots_error, [{"start": NOW.isoformat(), "kw": 3}], stamps)
call("whatif.scratch_copies", whatif.scratch_copies, SimpleNamespace(), SimpleNamespace(), {"dhw_windows": "06:00-08:00"})

# --- a coordinator for the methods the lifecycle never reached
cfg = {"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
       "outdoor_temp_entity": "sensor.outdoor", "dhw_tank_volume": 200.0,
       "solar_location": {"latitude": "x", "longitude": "y"}}
h2 = FakeHass()
h2.states.set("sensor.indoor", FakeState("21.0"))
h2.states.set("sensor.outdoor", FakeState("-3.0"))
coord = call("Coordinator()", cmod.HeatPumpOptimizerCoordinator, h2, FakeEntry(data=cfg))
if coord is not None:
    call("coord._solar_location", coord._solar_location)
    call("coord._check_pump_mode_expired", coord._check_pump_mode_expired)
    call("coord._raise_cop_issue", getattr(coord, "_raise_cop_issue", len))
    call("coord._async_load_thermal_learning", coord._async_load_thermal_learning)
    call("coord._async_load_manual_plan", coord._async_load_manual_plan)
    call("coord._command_frequency", getattr(coord, "_command_frequency", len))
    call("coord.async_simulate", getattr(coord, "async_simulate", len), {})
    call("coord._async_setup_ecl110_state_subscription", coord._async_setup_ecl110_state_subscription)
    call("coord._fetch_weather_forecast", coord._fetch_weather_forecast)
    call("coord._fetch_tibber_prices", coord._fetch_tibber_prices)

for name, res in CALLS:
    print(f"CALL {name}: {res}")
print(f"CALLS {len(CALLS)}")
