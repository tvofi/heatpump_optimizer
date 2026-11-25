#!/usr/bin/env python3
# Metric: number of empty-plan inputs on which DhwPlanner._clamp_dhw_to_capacity's return (or raised type) differs between baseline and mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_c9404a6ea551b041.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._clamp_dhw_to_capacity line 1943 `if plan.size == 0:`
# Perturbation: mutant c9404a6ea551b041 (dev/audit/rounds/round11/D3/s1/state/results/complete/c9404a6ea551b041.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction (if any): the mutant runs the setup (np.asarray(max_temp), float(initial_temp)) and the empty loop, then returns the same empty plan.
# Inputs tried: empty plan with max_temp scalar 60, empty array, NaN, inf, None; initial_temp 50, NaN, inf, -inf; plus out-of-type initial_temp None (TypeError in the mutant only, recorded separately); a horizon of n=0 through _build_dhw_requirements.
# Null control: a non-empty plan ([1.0, 2.0]): the guard is not taken, both arms identical.
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
KEY = 'c9404a6ea551b041'

pl, _ = planner()
MUT = mutant_method("_clamp_dhw_to_capacity", mutant_dict(KEY))


def out(fn, plan, T, mt):
    try:
        r = fn(pl, np.array(plan, float), T, np.full(len(plan), -5.0), np.zeros(len(plan)), 0.25, mt)
        return ("ok", tuple(r.tolist()), r.dtype.str)
    except Exception as e:  # noqa: BLE001
        return type(e).__name__


tried = sep = 0
for mt in (60.0, np.zeros(0), float("nan"), float("inf"), None):
    for T in (50.0, float("nan"), float("inf"), float("-inf")):
        tried += 1
        sep += int(out(DhwPlanner._clamp_dhw_to_capacity, [], T, mt) != out(MUT, [], T, mt))
print(f"RESULT typed_inputs_separating={sep} of {tried}")
print(f"RESULT out_of_type_initial_none_baseline={out(DhwPlanner._clamp_dhw_to_capacity, [], None, 60.0)[0]}")
print(f"RESULT out_of_type_initial_none_mutant={out(MUT, [], None, 60.0)}")
print(f"RESULT null_nonempty_equal={int(out(DhwPlanner._clamp_dhw_to_capacity, [1.0, 2.0], 50.0, np.full(2, 60.0)) == out(MUT, [1.0, 2.0], 50.0, np.full(2, 60.0)))}")
pl2, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
h0 = horizon(prices=np.zeros(0), n=0)
def n0(mut):
    try:
        if mut:
            with mutated("_clamp_dhw_to_capacity", KEY):
                p, _ = pl2._build_dhw_requirements(h0, p_max=4.0)
        else:
            p, _ = pl2._build_dhw_requirements(h0, p_max=4.0)
        return ("ok", p.schedule.size)
    except Exception as e:  # noqa: BLE001
        return type(e).__name__
print(f"RESULT n0_build_baseline={n0(False)}")
print(f"RESULT n0_build_mutant={n0(True)}")
