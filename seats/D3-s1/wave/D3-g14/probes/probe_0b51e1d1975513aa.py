#!/usr/bin/env python3
# Metric: outcome of DhwPlanner._apply_dhw_pins on a pins array shorter than the plan: 1 = returns a plan, 0 = raises IndexError.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_0b51e1d1975513aa.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_pins line 1645 `for i in range(min(len(out), len(dhw_pins))):`
# Perturbation: mutant 0b51e1d1975513aa (dev/audit/rounds/round11/D3/s1/state/results/complete/0b51e1d1975513aa.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: returns_plan 1 -> 0 (IndexError) when len(dhw_pins) < len(plan).
# Inputs tried: pins shorter than the plan (2 of 4), equal length, longer (6 of 4), empty pins; production reach: HeatPumpOptimizer._normalise_pins pads every pin array to the horizon (optimizer.py:5003-5018).
# Null control: equal-length and longer pins: both arms return the same plan.
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
KEY = '0b51e1d1975513aa'

MUT = mutant_method("_apply_dhw_pins", mutant_dict(KEY))
plan = np.array([0.0, 0.0, 2.0, 2.0])


def ok(fn, pins):
    try:
        return 1, fn(plan, np.array(pins, float), 0.6)
    except IndexError:
        return 0, None


for label, pins in (("short", [1.0, 0.0]), ("empty", [])):
    rb, _ = ok(DhwPlanner._apply_dhw_pins, pins)
    rm, _ = ok(MUT.__func__ if isinstance(MUT, staticmethod) else MUT, pins)
    print(f"RESULT {label}_pins_returns_plan_baseline={rb}")
    print(f"RESULT {label}_pins_returns_plan_mutant={rm}")
same = 0
for pins in ([1.0, 0.0, float("nan"), 0.0], [1.0, 0.0, float("nan"), 0.0, 1.0, 1.0]):
    rb, pb = ok(DhwPlanner._apply_dhw_pins, pins)
    rm, pm = ok(MUT.__func__ if isinstance(MUT, staticmethod) else MUT, pins)
    same += int(rb == rm == 1 and np.array_equal(pb, pm))
print(f"RESULT null_equal_or_longer_identical={same} of 2")
