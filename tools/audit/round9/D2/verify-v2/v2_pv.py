#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s3-02: pv.import_margin's zero floor.

Metric (one line): per cell (price profile, export price), the real solve's
published predicted_cost minus the TRUE cost of the same power schedule under the
net-meter law  sum(export*min(P,s) + import*max(P-s,0))*dt  (my own evaluation, not
the production closure), and the money the floor costs: true cost of the floored
production plan minus true cost of the plan solved with the floor removed.
Also: the production closure (HeatPumpOptimizer._energy_cost_fn) on 200 seeded random
schedules vs the law, max |error|.
Count key: OptimizationResult.power_schedule / predicted_cost and the closure's value.
Hooks: optimizer:HeatPumpOptimizer._energy_cost_fn, optimizer:HeatPumpOptimizer.optimize, pv:import_margin.
Perturbation: the unfloored arm IS the perturbation (pv.import_margin -> import - export via
mock.patch.object): published-minus-true -> 0.
Null control: winter_typical @ export 0.0 (import >= export on every surplus step): both 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_pv.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Solve figures +-1e-6.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import prices, weather, house, DT, N  # noqa: E402
from heatpump_optimizer import pv  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
START = datetime(2026, 6, 20)
h = np.arange(N) * DT + DT / 2
# my own surplus: 8 kWp, partly cloudy (seeded), minus a 0.5 kW house
rng = np.random.default_rng(5)
prod = np.clip(8.0 * 0.75 * np.sin(np.pi * (h - 5.5) / 13.0), 0.0, None) * rng.uniform(0.5, 1.0, N)
SURPLUS = pv.surplus_kw(prod, np.full(N, 0.5))


def law(pr, P, s, ex):
    n = len(P)
    return float(np.sum(ex * np.minimum(P, s[:n]) + pr[:n] * np.maximum(P - s[:n], 0.0)) * DT)


def mk(ex):
    p = ThermalParameters.from_config(house(two_zone=False))
    p.dhw_enabled = False
    o = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.5))
    o.config.pv_export_price = ex
    return o


def solve(prof, wx, ex, unfloored):
    o = mk(ex)
    pr = prices(prof, START)
    ot, wi, ra, so = weather(wx, START)
    st = ThermalState(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                      upper_floor_temperature=20.5, lower_floor_temperature=20.5, buffer_tank_temperature=35.0)
    if unfloored:
        with mock.patch.object(pv, "import_margin", lambda a, b: np.asarray(a, float) - float(b)):
            r = o.optimize(st, pr, ot, wi, ra, so, start_time=START, pv_surplus=SURPLUS)
    else:
        r = o.optimize(st, pr, ot, wi, ra, so, start_time=START, pv_surplus=SURPLUS)
    P = np.asarray(r.power_schedule, float)
    return r.predicted_cost, law(pr, P, SURPLUS, ex), pr


# closure vs law on random schedules
worst = {}
for prof, ex in (("summer_negative", 0.0), ("summer_typical", 0.30), ("winter_typical", 0.0)):
    o = mk(ex)
    o._pv_surplus = SURPLUS
    pr = prices(prof, START)
    fn = o._energy_cost_fn(pr, DT)
    r2 = np.random.default_rng(11)
    worst[(prof, ex)] = max(abs(fn(P) - law(pr, P, SURPLUS, ex)) for P in r2.uniform(0, 4, (200, N)))
    print(f"RESULT closure_vs_law_max_abs_{prof}_export{ex:.2f}={worst[(prof, ex)]:.6f} currency")

for prof, wx, ex in (("summer_negative", "summer_cool", 0.0), ("summer_typical", "summer_cool", 0.30),
                     ("winter_typical", "winter_mild", 0.0)):
    pub_f, true_f, _ = solve(prof, wx, ex, False)
    pub_u, true_u, _ = solve(prof, wx, ex, True)
    tag = f"{prof}_export{ex:.2f}"
    print(f"RESULT {tag}_published_minus_true_floored={pub_f - true_f:.6f} currency")
    print(f"RESULT {tag}_published_minus_true_unfloored={pub_u - true_u:.6f} currency")
    print(f"RESULT {tag}_true_cost_floored_minus_unfloored={true_f - true_u:.6f} currency", flush=True)

pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
