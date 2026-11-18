#!/usr/bin/env python3
"""D1-s4 M4: does a loop-side write to live solve inputs tear an in-flight solve?

Metric (one line): over R solves run on a real ThreadPoolExecutor (the #511 in-process
fallback route) from ``_solve_snapshot``, while the main thread keeps rewriting every
live object the snapshot copies, the count whose power_schedule differs (any element,
exact) from the same snapshot solved with no writer.  Key: the delivered schedule.

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/snapshot_race.py
          [--perturb]  ``copy.deepcopy`` inside coordinator replaced by identity (the snapshot
                       shares the live objects): torn count must go UP from 0.
Expected (baseline): torn=0 of R=6; perturbed: torn>=1.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6
Instrumented: coordinator:HeatPumpOptimizerCoordinator._solve_snapshot, coordinator:_warm_seeded,
              optimizer:HeatPumpOptimizer.optimize (thread), thermal_model:ThermalParameters,
              defrost:DefrostDerate (live learner written mid-solve).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import concurrent.futures as cf
import logging
import sys
import threading
import time
from datetime import timedelta
from unittest import mock

sys.path[:0] = [".", "tests", "tests/hastub", "custom_components"]
t_proc0, t_thr0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402

PERTURB = "--perturb" in sys.argv
START = golden.START
R = 6
logging.getLogger().setLevel(logging.CRITICAL)
dt_util.freeze(START)

cfg = dict(golden.coordinator_scenarios()["coord_dhw"])
coord = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
coord._prices = [
    {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
     "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
    for h in range(48)
]
coord._weather_forecast = [
    {"datetime": (START + timedelta(hours=h)).isoformat(),
     "temperature": 1.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
     "precipitation": 0.0, "humidity": 90.0}
    for h in range(48)
]
coord._solar_radiation_forecast = [0.0] * 48
ctx = getattr(coord, "_ctx", coord)
arrays = coord._forecast_arrays()
args = tuple(arrays[:5]) + (START, arrays[5], arrays[6])

ctx._thermal_params.defrost_derate.duty = [[0.1, 0.2] for _ in range(6)]
ctx._thermal_params.defrost_derate.duty_counts = [[20, 20] for _ in range(6)]


THREAD_CPU = [0.0]


def solve(snapshot):
    t0 = time.thread_time()
    try:
        return _solve(snapshot)
    finally:
        THREAD_CPU[0] += time.thread_time() - t0


def _solve(snapshot):
    state, opt = snapshot
    return np.asarray(opt.optimize(state, *args).power_schedule, dtype=float)


stop = threading.Event()
writes = [0]
live0 = {
    "rtm": ctx._thermal_params.room_thermal_mass,
    "gains": ctx._thermal_params.internal_gains,
    "room": ctx._current_state.room_temperature,
    "target": ctx._opt_config.target_temp,
}


def writer():
    i = 0
    t0 = time.thread_time()
    der = ctx._thermal_params.defrost_derate
    while not stop.is_set():
        i += 1
        s = 1.0 + 0.5 * (i % 2)
        ctx._thermal_params.room_thermal_mass = live0["rtm"] * s
        ctx._thermal_params.internal_gains = live0["gains"] * s
        ctx._current_state.room_temperature = live0["room"] + (i % 3)
        ctx._opt_config.target_temp = live0["target"] + (i % 2)
        der.duty[3][1] = 0.3 * (i % 2)
        der.observe_duty(3.0, 90.0, 0.25 * (i % 2), 1)
        writes[0] += 1
        time.sleep(0.0005)
    THREAD_CPU[0] += time.thread_time() - t0


def restore():
    ctx._thermal_params.room_thermal_mass = live0["rtm"]
    ctx._thermal_params.internal_gains = live0["gains"]
    ctx._current_state.room_temperature = live0["room"]
    ctx._opt_config.target_temp = live0["target"]


patches = [mock.patch.object(C.copy, "deepcopy", lambda x, memo=None: x)] if PERTURB else []
for p in patches:
    p.start()
torn = 0
worker_cpu = 0.0
try:
    with cf.ThreadPoolExecutor(max_workers=1) as pool:
        for _ in range(R):
            restore()
            ref = pool.submit(solve, coord._solve_snapshot()).result()  # no writer
            restore()
            snap = coord._solve_snapshot()
            stop.clear()
            th = threading.Thread(target=writer)
            fut = pool.submit(lambda s=snap: (time.thread_time(), solve(s), time.thread_time()))
            th.start()
            t0, got, t1 = fut.result()
            stop.set()
            th.join()
            pass  # solve() books its own thread CPU
            if got.shape != ref.shape or not np.array_equal(got, ref):
                torn += 1
finally:
    for p in reversed(patches):
        p.stop()
    dt_util.freeze(None)

print(f"MODE perturb={PERTURB} R={R}")
print(f"RESULT torn={torn} count")
print(f"RESULT writer_iterations={writes[0]} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
worker_cpu = THREAD_CPU[0]
print(f"RESULT deliberate_thread_cpu={worker_cpu:.3f} s")
print(f"RESULT thread_factor={(pc - worker_cpu) / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
