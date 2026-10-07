"""l3_dhw_helpers: what the per-step DHW parameter helpers cost inside a solve.

Metric (one line): per cell, golden.capture() (one optimize() plus its invariant checks) thread CPU with the three ThermalParameters helpers
(dhw_tank_heat_loss_coefficient, dhw_inlet_reference, effective_dhw_draw_pattern) memoised per
instance for the solve, divided by the same solve unmemoised -- 1 - ratio is the share a cache
could save; also calls per solve (contention-immune counts).
Cells: tests/golden.py scenarios winter_single_dhw, winter_two_zone_dhw, summer_dhw_only,
dhw_cold_tank, dhw_learned_windows. Arms interleaved plain/memo/plain/memo; plans compared bitwise.
Null control: --null memoises nothing but installs the same wrapper layer, so the ratio must read ~1.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_dhw_helpers.py [--null]
Expected (provisional, fan-out box): saved share per cell 0.00-0.05; plans_identical=5 of 5.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, venv314.
Instrumented symbols: heatpump_optimizer.thermal_model:ThermalParameters.dhw_tank_heat_loss_coefficient,
.dhw_inlet_reference, .effective_dhw_draw_pattern, driven through HeatPumpOptimizer.optimize.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, sys, time
import numpy as np
sys.path[:0] = ["tests", "custom_components"]
import golden  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

NULL = "--null" in sys.argv
NAMES = ("dhw_tank_heat_loss_coefficient", "dhw_inlet_reference", "effective_dhw_draw_pattern")
ORIG = {n: getattr(tm.ThermalParameters, n) for n in NAMES}
calls = {n: 0 for n in NAMES}


def _raw(n):
    o = ORIG[n]
    return (o.fget, True) if isinstance(o, property) else (o, False)


def counting():
    for n in NAMES:
        f, prop = _raw(n)
        def g(self, _f=f, _n=n):
            calls[_n] += 1
            return _f(self)
        setattr(tm.ThermalParameters, n, property(g) if prop else g)


def memo(active):
    for n in NAMES:
        f, prop = _raw(n)
        def g(self, _f=f, _n=n):
            if not active:
                return _f(self)
            c = self.__dict__.setdefault("_l3_memo", {})
            if _n not in c:
                c[_n] = _f(self)
            return list(c[_n]) if isinstance(c[_n], list) else c[_n]
        setattr(tm.ThermalParameters, n, property(g) if prop else g)


def solve(name):
    t = time.thread_time()
    p = time.process_time()
    golden_res = golden.capture(name, golden.SCENARIOS[name])
    return time.thread_time() - t, time.process_time() - p, golden_res


CELLS = ("winter_single_dhw", "winter_two_zone_dhw", "summer_dhw_only", "dhw_cold_tank", "dhw_learned_windows")
counting()
per_solve = {}
for c in CELLS:
    for n in NAMES:
        calls[n] = 0
    solve(c)
    per_solve[c] = dict(calls)
ratios, same, tf = [], 0, []
for c in CELLS:
    memo(False); a1, pa1, r1 = solve(c)
    memo(not NULL); b1, pb1, r2 = solve(c)
    memo(False); a2, pa2, _ = solve(c)
    memo(not NULL); b2, pb2, _ = solve(c)
    ratio = (b1 + b2) / (a1 + a2)
    ratios.append(ratio)
    ident = json.dumps(r1, sort_keys=True, default=str) == json.dumps(r2, sort_keys=True, default=str)
    same += bool(ident)
    tf.append((pa1 + pa2 + pb1 + pb2) / (a1 + a2 + b1 + b2))
    print(f"cell {c:22s} calls/solve={per_solve[c]} plain_cpu={a1 + a2:.2f}s memo_cpu={b1 + b2:.2f}s ratio={ratio:.4f} saved={1 - ratio:.4f} plan_identical={ident}")
saved = [1 - r for r in ratios]
best = max(saved)
loo = sorted(saved)[:-1]
print(f"RESULT saved_share_min={min(saved):.4f} ratio")
print(f"RESULT saved_share_max={best:.4f} ratio")
print(f"RESULT saved_share_mean={np.mean(saved):.4f} ratio")
print(f"RESULT saved_share_mean_drop_best={np.mean(loo):.4f} ratio")
print(f"RESULT plans_identical={same} of {len(CELLS)} count")
print(f"RESULT null_arm={int(NULL)}")
print(f"RESULT thread_factor={max(tf):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:  # noqa: BLE001
    sw = -1
print(f"RESULT swapins={sw}")
