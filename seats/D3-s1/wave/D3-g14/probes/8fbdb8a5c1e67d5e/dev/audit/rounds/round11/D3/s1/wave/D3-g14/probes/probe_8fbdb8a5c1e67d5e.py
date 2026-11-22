#!/usr/bin/env python3
# Metric: number of (dt, tank, n) inputs on which _build_dhw_requirements' schedule, suppressed count or raised exception differs between baseline and mutant, external heat active.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_8fbdb8a5c1e67d5e.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1343 `... 2.0 / max(dt, 1e-6) ...`
# Perturbation: mutant 8fbdb8a5c1e67d5e (dev/audit/rounds/round11/D3/s1/state/results/complete/8fbdb8a5c1e67d5e.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction (if any): only dt <= 0 can differ; dt == 0 raises ZeroDivisionError earlier at line 1214 in both arms; dt < 0 gives horizon n (baseline) vs 1 (mutant).
# Inputs tried: dt 0.25, 1.0, 1e-7, 1e-9, 0, -0.25, -1.0, -1e-9, NaN, +inf; tanks 30/44/46/50/60 C; n 8 and 24; an all-day window (min 45 C) so the planner buys; linear prices 0.1..1.0.
# Null control: dt 0.25: max(dt, 1e-6) == dt, both arms identical.
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
KEY = '8fbdb8a5c1e67d5e'

pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=parse_windows("00:00-23:59"), dhw_min_temp=45.0)


def outcome(h, mut):
    try:
        if mut:
            with mutated("_build_dhw_requirements", KEY):
                p, _ = pl._build_dhw_requirements(h, p_max=4.0)
        else:
            p, _ = pl._build_dhw_requirements(h, p_max=4.0)
        return (tuple(np.round(p.schedule, 9)), p.external_heat_suppressed_steps)
    except Exception as e:  # noqa: BLE001 - the raised type is the outcome
        return type(e).__name__


tried = sep = 0
for dt in (0.25, 1.0, 1e-7, 1e-9, 0.0, -0.25, -1.0, -1e-9, float("nan"), float("inf")):
    for T in (30.0, 44.0, 46.0, 50.0, 60.0):
        for n in (8, 24):
            h = horizon(prices=np.linspace(0.1, 1.0, n), n=n, dt=dt, step_hours=np.full(n, 19.0),
                        state=state(T, hsl=1.0, external_heat_active=True))
            tried += 1
            sep += int(outcome(h, False) != outcome(h, True))
print(f"RESULT inputs_separating={sep} of {tried}")
