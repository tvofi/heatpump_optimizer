"""Verifier V2 (independent) check on D9-s1-71.

Metric (own): calls per solve of the three named ThermalParameters helpers, counted by an
independently written counting wrapper (not the finder's), on a single golden cell
(winter_two_zone_dhw, not in the finder's 5-cell list) plus a repeated-median CPU ratio
(5 repeats per arm instead of the finder's 2, same interleaved plain/memo design) to reduce
box-contention noise on the CPU number while keeping the call counts (contention-immune) as the
primary evidence.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
  tools/audit/round9/D9/verify-v2-leads/v2_dhw_helpers_calls.py [--null]
Instrumented symbol: heatpump_optimizer.thermal_model:ThermalParameters.dhw_tank_heat_loss_coefficient
  (.dhw_inlet_reference, .effective_dhw_draw_pattern), driven through HeatPumpOptimizer.optimize.
Perturbation: per-instance memoisation of the three helpers (--null installs the same wrapper with
  no caching, as a null control).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
import time
sys.path[:0] = ["tests", "custom_components"]
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

NULL = "--null" in sys.argv
NAMES = ("dhw_tank_heat_loss_coefficient", "dhw_inlet_reference", "effective_dhw_draw_pattern")
ORIG = {n: getattr(tm.ThermalParameters, n) for n in NAMES}
calls = {n: 0 for n in NAMES}


def raw(n):
    o = ORIG[n]
    return (o.fget, True) if isinstance(o, property) else (o, False)


def install(counting, active):
    for n in NAMES:
        f, prop = raw(n)

        def g(self, _f=f, _n=n):
            if counting:
                calls[_n] += 1
            if not active:
                return _f(self)
            c = self.__dict__.setdefault("_v2_memo", {})
            if _n not in c:
                c[_n] = _f(self)
            v = c[_n]
            return list(v) if isinstance(v, list) else v
        setattr(tm.ThermalParameters, n, property(g) if prop else g)


CELL = "winter_two_zone_dhw"

install(True, False)
for n in NAMES:
    calls[n] = 0
golden.capture(CELL, golden.SCENARIOS[CELL])
call_counts = dict(calls)
print(f"RESULT calls_per_solve={call_counts}")


def solve():
    t = time.thread_time()
    r = golden.capture(CELL, golden.SCENARIOS[CELL])
    return time.thread_time() - t, r


REPEATS = 5
plain_times, memo_times = [], []
r1 = r2 = None
for _ in range(REPEATS):
    install(False, False)
    a, r1 = solve()
    plain_times.append(a)
    install(False, not NULL)
    b, r2 = solve()
    memo_times.append(b)

plain_med = float(np.median(plain_times))
memo_med = float(np.median(memo_times))
ratio = memo_med / plain_med
ident = json.dumps(r1, sort_keys=True, default=str) == json.dumps(r2, sort_keys=True, default=str)
print(f"RESULT plain_cpu_median={plain_med:.4f}s")
print(f"RESULT memo_cpu_median={memo_med:.4f}s")
print(f"RESULT saved_share={1 - ratio:.4f} ratio")
print(f"RESULT plan_identical={int(ident)}")
print(f"RESULT null_arm={int(NULL)}")
tf = 1.0
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
