#!/usr/bin/env python3
"""D1-s4 M5: a solver blow-up swallowed by the optimizer's guard is counted as a successful solve.

Metric (one line): after SOLVE_FAILURE_ISSUE_COUNT (3) consecutive cycles whose every
L-BFGS-B run raises, the coordinator's ``_solve_failures`` counter and the number of
``solve_failures`` repair issues raised; key = the counter the coordinator itself keeps.
Also: how many of those cycles published a plan whose status starts "failed".

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/solve_guard.py
          [--perturb]  the one-line fix shape: ``optimize`` raises when its own status
                       starts "failed" (in memory, a wrapper on HeatPumpOptimizer.optimize);
                       solve_failures must go UP from 0 to 3 and the issue to 1.
Expected (baseline): per config, solve_failures=0, issues=0, failed_plans_published=3;
          null control (the SAME fault raised outside the optimizer's guard, from
          ``_forecast_arrays``): solve_failures=3, issues=1.
          Second trigger (optimizer only, golden.make dhw 12 h): of 15 cells (one
          nan/inf/-inf step in prices/outdoor/wind/rain/solar), returned_failed_plan=9,
          raised=2; --perturb: returned_failed_plan=0, raised=11.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6 (4 CPU, 15 GiB)
Instrumented: custom_components.heatpump_optimizer.optimizer:_scoped_minimize (fault injected),
              HeatPumpOptimizer._optimize_space_only / _solve_space (the guards under test),
              coordinator:HeatPumpOptimizerCoordinator.async_run_optimization (the observer).
Transport: coordinator._await_optimize is replaced by an in-process call of
optimize_in_process, so the in-memory fault reaches the solve (the process worker would
re-import an unpatched optimizer). This is the coordinator's own #511 fallback route.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
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


class _Sink(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.n = 0

    def emit(self, record):
        self.n += 1


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


def _boom(*_a, **_k):
    raise RuntimeError("injected L-BFGS-B blow-up")


def run(config, arm):
    hass, coord = build(config)
    sink = _Sink()
    opt_log = logging.getLogger(O.__name__)
    opt_log.addHandler(sink)
    opt_log.setLevel(logging.ERROR)
    failed_published = 0
    patches = [mock.patch.object(C, "_await_optimize", _inline)]
    if arm == "guarded":
        patches.append(mock.patch.object(O, "_scoped_minimize", _boom))
    else:  # null control: the same fault, raised where no optimizer guard sits
        patches.append(mock.patch.object(coord, "_forecast_arrays", _boom))
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
        for _ in range(C.SOLVE_FAILURE_ISSUE_COUNT):
            asyncio.run(coord.async_run_optimization())
            res = coord._optimization_result
            if res is not None and str(res.status).startswith("failed"):
                failed_published += 1
                coord._optimization_result = None  # count each cycle's own plan
    finally:
        for p in reversed(patches):
            p.stop()
        opt_log.removeHandler(sink)
    issues = [i for i in getattr(hass, "issues", []) if i[1] == "solve_failures"]
    return coord._solve_failures, len(issues), failed_published, sink.n


dt_util.freeze(START)
logging.getLogger().setLevel(logging.CRITICAL)
scen = golden.coordinator_scenarios()
print(f"MODE perturb={PERTURB}")
try:
    for name in ("coord_minimal", "coord_dhw"):
        for arm in ("guarded", "null_control"):
            sf, iss, fp, errs = run(scen[name], arm)
            print(f"RESULT {name}.{arm}.solve_failures={sf} count")
            print(f"RESULT {name}.{arm}.solve_failures_issues={iss} count")
            print(f"RESULT {name}.{arm}.failed_plans_published={fp} count")
            print(f"RESULT {name}.{arm}.optimizer_error_logs={errs} count")
finally:
    dt_util.freeze(None)

# Second trigger, optimizer only: one non-finite step in one horizon input.
import numpy as np  # noqa: E402
logging.getLogger(O.__name__).addHandler(logging.NullHandler())
NAMES = ["prices", "outdoor", "wind", "rain", "solar"]
returned_failed = raised = cells = 0
orig_opt = O.HeatPumpOptimizer.optimize
for nm in NAMES:
    for bad in (float("nan"), float("inf"), float("-inf")):
        b = golden.make(dhw=True, hours=12)
        arrs = [np.array(b[k], dtype=float) for k in NAMES]
        arrs[NAMES.index(nm)][5] = bad
        cells += 1
        opt = b["optimizer"]
        call = orig_opt
        if PERTURB:
            def call(self, *a, **k):
                res = orig_opt(self, *a, **k)
                if str(res.status).startswith("failed"):
                    raise RuntimeError(res.status)
                return res
        try:
            with np.errstate(all="ignore"):
                res = call(opt, b["state"], *arrs, golden.START)
            if str(res.status).startswith("failed"):
                returned_failed += 1
        except Exception:  # noqa: BLE001
            raised += 1
print(f"RESULT nonfinite_input.cells={cells} count")
print(f"RESULT nonfinite_input.returned_failed_plan={returned_failed} count")
print(f"RESULT nonfinite_input.raised={raised} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
