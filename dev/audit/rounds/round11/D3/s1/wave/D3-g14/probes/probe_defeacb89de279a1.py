#!/usr/bin/env python3
# Metric: number of horizons on which DhwPlan.external_heat_suppressed_steps differs between baseline and mutant, and the count of planned slots in (0, 1e-5] kW (the only values `>=` and `>` 1e-6 can split) the pipeline ever leaves before the suppression line.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_defeacb89de279a1.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1348 `suppress_steps = int(np.sum(mask & (schedule > 1e-6)))`
# Perturbation: mutant defeacb89de279a1 (dev/audit/rounds/round11/D3/s1/state/results/complete/defeacb89de279a1.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction (if any): suppressed count +1 at a slot of exactly 1e-6 kW.
# Inputs tried: external heat on; tanks 40-56 C in 2 C steps; cheap blocks at steps 0-7, 1-7, 2-5 and flat; window 18:00-20:00 and 06:00-08:00; min 45 C; p_max 4.0 and 0.3 (a 0.24 kW block); also the slot values seen by a spy on _repair_dhw_floor's output.
# Null control: external heat off: the branch does not run, both 0.
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
KEY = 'defeacb89de279a1'

tried = sep = tiny = 0
for win in ("18:00-20:00", "06:00-08:00"):
    pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=parse_windows(win), dhw_min_temp=45.0)
    for T in np.arange(40.0, 56.01, 2.0):
        for blk in ((0, 8), (1, 8), (2, 6), None):
            for pmax in (4.0, 0.3):
                pr = np.full(N, 1.0)
                if blk:
                    pr[blk[0]:blk[1]] = 0.05
                h = horizon(prices=pr, state=state(float(T), external_heat_active=True))
                b, m = arms(pl, h, KEY, p_max=pmax)
                tried += 1
                sep += int(b.external_heat_suppressed_steps != m.external_heat_suppressed_steps)
                tiny += int(np.sum((b.schedule > 0.0) & (b.schedule <= 1e-5)))
print(f"RESULT inputs_separating={sep} of {tried}")
print(f"RESULT slots_in_0_1e-5_kw={tiny}")
