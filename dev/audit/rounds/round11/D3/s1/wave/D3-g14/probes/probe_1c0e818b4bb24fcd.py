#!/usr/bin/env python3
# Metric: max |plan| difference (kW) between baseline and mutant _apply_dhw_min_run on a plan with entries outside [0, p_dhw_max] that takes the per-slot path (joint raise does not fit; the line-2106 return); and the count of 400 seeded random plans that separate.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_1c0e818b4bb24fcd.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run line 2106 `repaired = np.clip(plan, 0.0, p_dhw_max)`
# Perturbation: mutant 1c0e818b4bb24fcd (dev/audit/rounds/round11/D3/s1/state/results/complete/1c0e818b4bb24fcd.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: the mutant returns entries above p_dhw_max and below 0 unclipped.
# Inputs tried: plan [0,3,3,-1,0.1,5,0.3,-1] at 48.971 C (per-slot path); 400 random plans over {-1,0,0.1,0.3,3,5}^8 with tank 30..56 C (seed 0), ceiling 55 C; in-range plans; the three ordinary days (realistic_delta).
# Null control: the same plan with every entry in [0, p_dhw_max] ([0,3,3,0,0.1,3,0.3,0]): delta 0.
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
KEY = '1c0e818b4bb24fcd'

pl, params = planner()
n = 8
OUT, DR, MT = np.full(n, -5.0), np.zeros(n), np.full(n, 55.0)  # 55 C: the default dhw_max_temp


def call(plan, T0, fn=None):
    kw = dict(plan=np.array(plan, float), initial_temp=T0, outdoor_temps=OUT, draw_rates=DR, dt=0.25,
              p_dhw_max=3.0, min_run_power=0.6, max_temp=MT)
    return (fn or DhwPlanner._apply_dhw_min_run)(pl, **kw)


MUT = mutant_method("_apply_dhw_min_run", mutant_dict(KEY))

P = [0.0, 3.0, 3.0, -1.0, 0.1, 5.0, 0.3, -1.0]
T0 = 48.97104160717855
b, m = call(P, T0), call(P, T0, MUT)
print(f"RESULT baseline_plan={fmt(b)} kW")
print(f"RESULT mutant_plan={fmt(m)} kW")
print(f"RESULT delta_kw={float(np.max(np.abs(b - m))):.6f} kW")
rng = np.random.default_rng(0)
hits = 0
for _ in range(400):
    p = rng.choice([-1.0, 0.0, 0.1, 0.3, 3.0, 5.0], size=n)
    t = float(rng.uniform(30, 56))
    hits += int(float(np.max(np.abs(call(p, t) - call(p, t, MUT)))) > 1e-12)
print(f"RESULT random_plans_separating={hits} of 400")
Q = [0.0, 3.0, 3.0, 0.0, 0.1, 3.0, 0.3, 0.0]
print(f"RESULT null_delta_kw={float(np.max(np.abs(call(Q, T0) - call(Q, T0, MUT)))):.6f} kW")
print(f"RESULT realistic_delta_kw={realistic_delta(KEY, '_apply_dhw_min_run'):.6f} kW")
