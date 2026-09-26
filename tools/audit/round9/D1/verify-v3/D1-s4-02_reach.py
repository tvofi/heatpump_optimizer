#!/usr/bin/env python3
"""V3 (round 9) D1-s4-02 reach: does a non-finite value at the coordinator's own
input seams (price rows, weather forecast rows, solar list) reach the optimizer's
f"failed ({e})" guard with NO injected fault?

Metric (one line): of K coordinator-level cells (one hour of one input set to a
non-finite value), the number whose cycle publishes a plan with status starting
"failed" while _solve_failures stays 0 (the finding's mis-accounting), next to the
number whose cycle raises into the coordinator's failure branch, and the number
that publish a normal plan.
Command:  PYTHONPATH=tests/hastub /root/venv314/bin/python tools/audit/round9/D1/verify-v3/D1-s4-02_reach.py [--perturb]
  --perturb: optimize() raises when its own status starts "failed" (the finder's
  fix shape); failed_status_published must go to 0 and raised rise by the same count.
Expected: measured, exact (deterministic).  Baseline SHA 1936d5ca (evidence tree).
Machine: cloud 4-core box, CPython 3.14.0rc2 (V3 sub-seat for G1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import logging
import sys
import time
from datetime import timedelta
from unittest import mock

sys.path[:0] = [".", "tests", "tests/hastub", "custom_components"]
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402

PERTURB = "--perturb" in sys.argv
START = golden.START


async def _inline(hass, optimizer, state, *positional, **keywords):
    return O.optimize_in_process(optimizer, state, positional, keywords)


def build(config):
    hass = FakeHass()
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48
    return hass, coord


def cells():
    for bad in (float("nan"), float("inf"), float("-inf")):
        yield ("price.total", bad)
        for k in ("temperature", "wind_speed", "precipitation", "humidity"):
            yield ("weather." + k, bad)
        yield ("solar", bad)


def run(config, where, bad):
    hass, coord = build(config)
    if where == "price.total":
        coord._prices[5]["total"] = bad
    elif where == "solar":
        coord._solar_radiation_forecast[5] = bad
    else:
        coord._weather_forecast[5][where.split(".")[1]] = bad
    patches = [mock.patch.object(C, "_await_optimize", _inline)]
    if PERTURB:
        orig = O.HeatPumpOptimizer.optimize

        def _raising(self, *a, **k):
            res = orig(self, *a, **k)
            if str(res.status).startswith("failed"):
                raise RuntimeError(res.status)
            return res
        patches.append(mock.patch.object(O.HeatPumpOptimizer, "optimize", _raising))
    for p in patches:
        p.start()
    try:
        asyncio.run(coord.async_run_optimization())
    finally:
        for p in reversed(patches):
            p.stop()
    res = coord._optimization_result
    status = None if res is None else str(res.status)
    return status, coord._solve_failures


dt_util.freeze(START)
logging.getLogger().setLevel(logging.CRITICAL)
scen = golden.coordinator_scenarios()
print(f"MODE perturb={PERTURB}")
tot = failed_pub = raised = normal = 0
try:
    for name in ("coord_minimal", "coord_dhw"):
        for where, bad in cells():
            status, sf = run(scen[name], where, bad)
            tot += 1
            if status is not None and status.startswith("failed") and sf == 0:
                failed_pub += 1
                tag = "FAILED_PUBLISHED"
            elif sf > 0:
                raised += 1
                tag = "COUNTED_FAILURE"
            else:
                normal += 1
                tag = "normal"
            print(f"  {name} {where}={bad}: {tag} status={str(status)[:60]!r} solve_failures={sf}")
finally:
    dt_util.freeze(None)
print(f"RESULT cells={tot} count")
print(f"RESULT failed_status_published_uncounted={failed_pub} count")
print(f"RESULT counted_failure={raised} count")
print(f"RESULT normal_plan={normal} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
