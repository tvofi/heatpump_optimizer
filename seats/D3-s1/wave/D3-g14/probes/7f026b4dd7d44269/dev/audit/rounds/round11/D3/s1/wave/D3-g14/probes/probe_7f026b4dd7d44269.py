#!/usr/bin/env python3
# Metric: max |schedule| difference (kW) and kWh of _build_dhw_requirements on a cheap-night day, per tank cooling rate (the hold hours that set max_lead_steps).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_7f026b4dd7d44269.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1214 `max_lead_steps = max(1, min(n_steps, int(np.ceil(max_lead_hours / dt))))`
# Perturbation: mutant 7f026b4dd7d44269 (dev/audit/rounds/round11/D3/s1/state/results/complete/7f026b4dd7d44269.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: the lead window widens to the whole horizon, so a leaky tank pre-heats further ahead than its hold time (kWh up).
# Inputs tried: dhw_cooling_rate 0.3 (default-like, hold 28 h > horizon), 2.0 (hold 4.2 h), 5.0 (hold 2.8 h); prices 0.01 on steps 0-7, 1.0 elsewhere; window 18:00-20:00, min 45 C.
# Null control: cooling rate 0.3: hold 28 h, min(n_steps, ceil) == n_steps in both arms, delta 0.
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
KEY = '7f026b4dd7d44269'

pr = np.full(N, 1.0); pr[0:8] = 0.01
for cr in (0.3, 2.0, 5.0):
    pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0, dhw_cooling_rate=cr)
    b, m = arms(pl, horizon(prices=pr), KEY, p_max=4.0)
    tag = f"cr{cr:g}".replace(".", "p")
    print(f"RESULT {tag}_hold_hours={b.max_lead_hours:.4f} h")
    print(f"RESULT {tag}_kwh_baseline={b.schedule.sum() * 0.25:.4f} kWh")
    print(f"RESULT {tag}_kwh_mutant={m.schedule.sum() * 0.25:.4f} kWh")
    print(f"RESULT {tag}_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
