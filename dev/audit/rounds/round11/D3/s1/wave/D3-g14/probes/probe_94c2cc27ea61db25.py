#!/usr/bin/env python3
# Metric: number of horizons (legionella due, external heat active) on which _build_dhw_requirements' schedule or suppressed count differs between baseline and mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_94c2cc27ea61db25.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1346 `if legionella_step is not None:` (protects the disinfection step from external-heat suppression)
# Perturbation: mutant 94c2cc27ea61db25 (dev/audit/rounds/round11/D3/s1/state/results/complete/94c2cc27ea61db25.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction (if any): energy at the legionella step zeroed by the suppression mask.
# Inputs tried: legionella enabled 60 C / 7 d; hours since 160-169 (legionella steps 0,1,3,5,7 seen); tank 58-62 C in 0.1 C; a single cheap step at 1,3,5,7 or none; windows 18:00-20:00, 01:00-03:00, 04:00-06:00, 10:00-12:00 with min 45/55 C and draw 150/400 L/day; step 0 at 0.01 against 3.0. 2 x 240 + 60 + 21 horizons.
# Null control: external heat inactive: the branch does not run, delta 0.
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
KEY = '94c2cc27ea61db25'

LEG = dict(dhw_legionella_enabled=True, dhw_legionella_temp=60.0, dhw_legionella_interval_days=7.0)
tried = sep = 0
legs = set()


def one(pl, h):
    global tried, sep
    b, m = arms(pl, h, KEY, p_max=4.0)
    legs.add(b.legionella_step)
    tried += 1
    sep += int(not np.array_equal(b.schedule, m.schedule)
               or b.external_heat_suppressed_steps != m.external_heat_suppressed_steps)


pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0, **LEG)
for T in np.arange(59.0, 61.01, 0.1):
    one(pl, horizon(prices=np.full(N, 1.0), state=state(float(T), hsl=169.0, external_heat_active=True)))
for hsl in (160.0, 163.0, 165.0, 166.0, 167.0, 168.0):
    for cheap in (None, 1, 3, 5, 7):
        for T in (59.0, 59.5, 59.8, 60.0, 60.3, 60.6, 61.0, 62.0):
            pr = np.full(N, 1.0)
            if cheap is not None:
                pr[cheap] = 0.01
            one(pl, horizon(prices=pr, state=state(T, hsl=hsl, external_heat_active=True)))
for win in ("01:00-03:00", "04:00-06:00", "10:00-12:00"):
    for mint in (45.0, 55.0):
        for cons in (150.0, 400.0):
            plw, _ = planner(dhw_schedule_enabled=True, dhw_windows=parse_windows(win), dhw_min_temp=mint,
                             dhw_daily_consumption=cons, **LEG)
            for T in (59.6, 59.8, 60.0, 60.5, 61.0):
                pr = np.full(N, 3.0); pr[0] = 0.01
                one(plw, horizon(prices=pr, state=state(T, hsl=169.0, external_heat_active=True)))
print(f"RESULT inputs_separating={sep} of {tried}")
print(f"RESULT legionella_steps_seen={sorted(s for s in legs if s is not None)}")
