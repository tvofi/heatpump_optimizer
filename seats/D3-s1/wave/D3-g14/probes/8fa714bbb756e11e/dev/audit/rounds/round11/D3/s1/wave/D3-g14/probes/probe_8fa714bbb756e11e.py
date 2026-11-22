#!/usr/bin/env python3
# Metric: DhwPlan.external_heat_suppressed_steps and the kWh planned in steps 0-7 by _build_dhw_requirements with external heat active and the tank coasting above its requirement.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_8fa714bbb756e11e.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1343 `horizon = min(n_steps, max(1, int(round(2.0 / max(dt, 1e-6)))))`
# Perturbation: mutant 8fa714bbb756e11e (dev/audit/rounds/round11/D3/s1/state/results/complete/8fa714bbb756e11e.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: the suppression horizon shrinks from 2 h (8 steps) to 1 step: suppressed 1 -> 0 and electric DHW bought under a running external source (kWh in steps 0-7 up).
# Inputs tried: tank 48 and 55 C, external heat on/off, prices 0.05 on steps 1-7, 1.0 elsewhere; window 18:00-20:00, min 45 C.
# Null control: external heat off (branch not run), and tank 55 C (nothing planned early): both arms equal.
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
KEY = '8fa714bbb756e11e'

pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[1:8] = 0.05
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=True)), KEY, p_max=4.0)
print(f"RESULT suppressed_baseline={b.external_heat_suppressed_steps}")
print(f"RESULT suppressed_mutant={m.external_heat_suppressed_steps}")
print(f"RESULT kwh_steps0_7_baseline={b.schedule[:8].sum() * 0.25:.4f} kWh")
print(f"RESULT kwh_steps0_7_mutant={m.schedule[:8].sum() * 0.25:.4f} kWh")
d = 0.0
for T, ext in ((48.0, False), (55.0, True), (55.0, False)):
    b, m = arms(pl, horizon(prices=pr, state=state(T, external_heat_active=ext)), KEY, p_max=4.0)
    d = max(d, float(np.max(np.abs(b.schedule - m.schedule))))
print(f"RESULT null_delta_kw={d:.6f} kW")
