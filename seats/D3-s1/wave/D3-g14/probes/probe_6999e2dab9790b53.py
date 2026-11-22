#!/usr/bin/env python3
# Metric: max |schedule| difference (kW) of _build_dhw_requirements with one DHW pin exactly 0.5 at step 13 (others free).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_6999e2dab9790b53.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1187 `mask[...] = ~np.isnan(pins_arr) & (pins_arr < 0.5)`
# Perturbation: mutant 6999e2dab9790b53 (dev/audit/rounds/round11/D3/s1/state/results/complete/6999e2dab9790b53.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: a 0.5 pin becomes forced-off for the planners (then force-on by the overlay), moving the plan's energy.
# Inputs tried: pin 0.5 at step 13 under a cheap night; pins 0, 1, NaN, 0.49999, 0.50001 at the same step; production reach: manual_plan.channel_pins emits only 0.0, 1.0, NaN (manual_plan.py:41-42, 215-220).
# Null control: pin 1.0, 0.0, NaN and 0.5 +- 1e-5 at step 13: identical in both arms.
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
KEY = '6999e2dab9790b53'

pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[8:16] = 0.1


def at(v):
    pins = np.full(N, np.nan); pins[13] = v
    return arms(pl, horizon(prices=pr, dhw_pins=pins), KEY, p_max=4.0)


b, m = at(0.5)
print(f"RESULT pin0p5_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
print(f"RESULT pin0p5_kwh_baseline={b.schedule.sum() * 0.25:.4f} kWh")
print(f"RESULT pin0p5_kwh_mutant={m.schedule.sum() * 0.25:.4f} kWh")
d = 0.0
for v in (1.0, 0.0, float("nan"), 0.49999, 0.50001):
    b, m = at(v)
    d = max(d, float(np.max(np.abs(b.schedule - m.schedule))))
print(f"RESULT null_delta_kw={d:.6f} kW")
