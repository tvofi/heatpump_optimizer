#!/usr/bin/env python3
# Metric: max |plan| difference (kW) between baseline and mutant _apply_dhw_min_run on one plan whose entries lie outside [0, p_dhw_max] and whose weak slots all fit jointly (the line-2076 return).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_3685cdbd27c1680f.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run line 2076 `jointly_raised = np.clip(joint, 0.0, p_dhw_max)`
# Perturbation: mutant 3685cdbd27c1680f (dev/audit/rounds/round11/D3/s1/state/results/complete/3685cdbd27c1680f.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: the mutant returns the unclipped plan (5.0 kW where p_dhw_max=3.0; -1.0 kW).
# Inputs tried: plan [5.0, 0.1, 0...] and [-1.0, 0.1, 0...] at tank 30 C; in-range plan [3.0, 0.1, 0...]; the three ordinary days through _build_dhw_requirements (realistic_delta).
# Null control: an in-range plan ([3.0, 0.1, 0, ...]): the clip is the identity, delta 0.
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
KEY = '3685cdbd27c1680f'

pl, params = planner()
n = 8
OUT, DR, MT = np.full(n, -5.0), np.zeros(n), np.full(n, 55.0)  # 55 C: the default dhw_max_temp


def call(plan, T0, fn=None):
    kw = dict(plan=np.array(plan, float), initial_temp=T0, outdoor_temps=OUT, draw_rates=DR, dt=0.25,
              p_dhw_max=3.0, min_run_power=0.6, max_temp=MT)
    return (fn or DhwPlanner._apply_dhw_min_run)(pl, **kw)


MUT = mutant_method("_apply_dhw_min_run", mutant_dict(KEY))

b, m = call([5.0, 0.1] + [0.0] * 6, 30.0), call([5.0, 0.1] + [0.0] * 6, 30.0, MUT)
print(f"RESULT baseline_step0_kw={b[0]:.6f} kW")
print(f"RESULT mutant_step0_kw={m[0]:.6f} kW")
b2, m2 = call([-1.0, 0.1] + [0.0] * 6, 30.0), call([-1.0, 0.1] + [0.0] * 6, 30.0, MUT)
print(f"RESULT negative_entry_delta_kw={abs(b2[0] - m2[0]):.6f} kW")
print(f"RESULT null_delta_kw={float(np.max(np.abs(call([3.0, 0.1] + [0.0] * 6, 30.0) - call([3.0, 0.1] + [0.0] * 6, 30.0, MUT)))):.6f} kW")
print(f"RESULT realistic_delta_kw={realistic_delta(KEY, '_apply_dhw_min_run'):.6f} kW")
