#!/usr/bin/env python3
# Metric: DhwPlan.external_heat_suppressed_steps (count) published by _build_dhw_requirements with blocked=True while external heat is active, and the schedule sum (kW).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_de02e0a048abc451.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1190 `if blocked:` (forced_off = all steps)
# Perturbation: mutant de02e0a048abc451 (dev/audit/rounds/round11/D3/s1/state/results/complete/de02e0a048abc451.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: suppressed count 0 -> 1 (the mutant plans slots in a blocked mode, then suppresses one of them); the final schedule is zeroed by the restated invariant at line 1368 in both arms.
# Inputs tried: blocked=True with external_heat_active True and False, tank 48 C, cheap steps 1-7; blocked=False.
# Null control: external heat inactive (the suppression branch does not run): both arms 0; blocked=False: identical.
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
KEY = 'de02e0a048abc451'

pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[1:8] = 0.05
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=True)), KEY, p_max=4.0, blocked=True)
print(f"RESULT suppressed_steps_baseline={b.external_heat_suppressed_steps}")
print(f"RESULT suppressed_steps_mutant={m.external_heat_suppressed_steps}")
print(f"RESULT schedule_sum_baseline={b.schedule.sum():.6f} kW")
print(f"RESULT schedule_sum_mutant={m.schedule.sum():.6f} kW")
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=False)), KEY, p_max=4.0, blocked=True)
print(f"RESULT null_ext_off_suppressed={b.external_heat_suppressed_steps},{m.external_heat_suppressed_steps}")
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=True)), KEY, p_max=4.0, blocked=False)
print(f"RESULT null_unblocked_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
