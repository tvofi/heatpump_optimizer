#!/usr/bin/env python3
"""V2 (D1-2) own harness for D1-s4-02: a solve whose every start is unusable, as seen by the
coordinator's own failure accounting and by what it publishes.

Metric: over 3 consecutive async_run_optimization cycles with the fault injected at
  optimizer:_multi_start_minimize (raising the production's own ValueError('no usable starting
  point'); a different site from the finder's _scoped_minimize), per config: the coordinator's
  _solve_failures, solve_failures repair issues, cycles whose adopted result.status starts
  'failed', and cycles that advanced coordinator.last_optimization (the "last success" stamp).
Reachability arm (no injection): one non-finite value placed in a coordinator INPUT (a price
  row's total, a forecast temperature, the solar forecast) -- count cycles that adopt a
  'failed' plan; a zero here means the non-finite trigger is fenced before the optimizer.
Null: the same config, no fault: failed=0.
Transport: coordinator._await_optimize replaced by an inline optimize_in_process call (the
  coordinator's own #511 fallback), so an in-memory patch reaches the solve.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u2_solve_fail.py
Expected (exact): fault arm per config solve_failures=0 issues=0 failed_adopted=3 last_opt_advanced=3.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, logging, sys, time
from datetime import timedelta
from unittest import mock
sys.path[:0] = [".", "tests", "tests/hastub", "custom_components"]
p0, t0 = time.process_time(), time.thread_time()
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402

START = golden.START


async def _inline(hass, optimizer, state, *positional, **keywords):
    return O.optimize_in_process(optimizer, state, positional, keywords)


def build(config, poison=None):
    hass = FakeHass()
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    coord._prices = [{"total": round(0.5 + 0.4 * ((h * 7) % 24) / 24.0, 4),
                      "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                     for h in range(48)]
    coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": -3.0 + 4.0 * (h % 24) / 24.0, "wind_speed": 2.0,
                                "precipitation": 0.0, "humidity": 80.0} for h in range(48)]
    coord._solar_radiation_forecast = [0.0] * 48
    if poison == "price":
        coord._prices[5]["total"] = float("nan")
    elif poison == "temp":
        coord._weather_forecast[5]["temperature"] = float("nan")
    elif poison == "solar":
        coord._solar_radiation_forecast[5] = float("inf")
    return hass, coord


def _no_start(*_a, **_k):
    raise ValueError("no usable starting point")


def run(config, fault, poison=None, cycles=3):
    hass, coord = build(config, poison)
    patches = [mock.patch.object(C, "_await_optimize", _inline)]
    if fault:
        patches.append(mock.patch.object(O, "_multi_start_minimize", _no_start))
    for p in patches:
        p.start()
    failed = advanced = raised_out = 0
    try:
        for i in range(cycles):
            dt_util.freeze(START + timedelta(minutes=15 * i))
            before = coord.last_optimization
            coord._optimization_result = None
            try:
                asyncio.run(coord.async_run_optimization())
            except Exception:  # noqa: BLE001
                raised_out += 1
            res = coord._optimization_result
            if res is not None and str(res.status).startswith("failed"):
                failed += 1
            if coord.last_optimization is not None and coord.last_optimization != before:
                advanced += 1
    finally:
        for p in reversed(patches):
            p.stop()
    issues = sum(1 for i in getattr(hass, "issues", []) if i[1] == "solve_failures")
    return coord._solve_failures, issues, failed, advanced, raised_out


logging.getLogger().setLevel(logging.CRITICAL)
scen = golden.coordinator_scenarios()
try:
    for name in ("coord_minimal", "coord_two_zone", "coord_all_features"):
        sf, iss, fl, adv, ro = run(scen[name], True)
        print(f"RESULT {name}.fault.solve_failures={sf} count")
        print(f"RESULT {name}.fault.issues={iss} count")
        print(f"RESULT {name}.fault.failed_adopted={fl} count")
        print(f"RESULT {name}.fault.last_opt_advanced={adv} count")
    sf, iss, fl, adv, ro = run(scen["coord_minimal"], False, cycles=1)
    print(f"RESULT coord_minimal.null.failed_adopted={fl} count (solve_failures={sf})")
    for poison in ("price", "temp", "solar"):
        sf, iss, fl, adv, ro = run(scen["coord_minimal"], False, poison, cycles=1)
        print(f"RESULT reach.{poison}.failed_adopted={fl} count (solve_failures={sf}, adopted_any={adv})")
finally:
    dt_util.freeze(None)
p1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
