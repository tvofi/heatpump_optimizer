#!/usr/bin/env python3
# Metric: number of p_max / p_run_cap inputs (of 11) on which _build_dhw_requirements' schedule differs between baseline and mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_4813f0fd25bc8bb4.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1138 `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))`
# Perturbation: mutant 4813f0fd25bc8bb4 (dev/audit/rounds/round11/D3/s1/state/results/complete/4813f0fd25bc8bb4.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction (if any): p_dhw_run changes only where p_max*0.8 > p_max, i.e. p_max < 0, where max(0.1, .) returns 0.1 in both arms.
# Inputs tried: p_max 4, 0, -1, 1e-9, 0.125, +inf, -inf, NaN; p_max 4 with p_run_cap None, 0.05, 2.0.
# Null control: p_max 4.0 (ordinary): both arms equal by construction of min(0.8p, p) = 0.8p for p >= 0.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
warnings.simplefilter("ignore")
from _g14lib import *  # noqa: E402,F401,F403

W = parse_windows("18:00-20:00")
N = 96


def state(T=48.0, hsl=20.0, **kw):
    return ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                        dhw_temperature=T, dhw_hours_since_legionella=hsl,
                        buffer_tank_temperature=40.0, **kw)


def arms(pl, h, key, **kw):
    """(baseline DhwPlan, mutant DhwPlan) of _build_dhw_requirements on one horizon."""
    b, _ = pl._build_dhw_requirements(h, **kw)
    with mutated("_build_dhw_requirements", key):
        m, _ = pl._build_dhw_requirements(h, **kw)
    return b, m


def realistic_delta(key, method="_build_dhw_requirements"):
    """Max |schedule| difference over three ordinary planning days (flat, cheap night, evening peak)."""
    pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
    worst = 0.0
    for pr in (np.full(N, 1.0), np.r_[np.full(24, 0.2), np.full(72, 1.0)],
               np.r_[np.full(68, 1.0), np.full(16, 3.0), np.full(12, 1.0)]):
        h = horizon(prices=pr)
        b, _ = pl._build_dhw_requirements(h, p_max=4.0)
        with mutated(method, key):
            m, _ = pl._build_dhw_requirements(h, p_max=4.0)
        worst = max(worst, float(np.max(np.abs(b.schedule - m.schedule))))
    return worst
KEY = '4813f0fd25bc8bb4'

pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[8:16] = 0.1
cases = [dict(p_max=v) for v in (4.0, 0.0, -1.0, 1e-9, 0.125, float("inf"), float("-inf"), float("nan"))]
cases += [dict(p_max=4.0, p_run_cap=c) for c in (None, 0.05, 2.0)]
diff = 0
for kw in cases:
    b, m = arms(pl, horizon(prices=pr), KEY, **kw)
    diff += int(not np.array_equal(b.schedule, m.schedule))
print(f"RESULT inputs_separating={diff} of {len(cases)}")
b, m = arms(pl, horizon(prices=pr), KEY, p_max=4.0)
print(f"RESULT null_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
