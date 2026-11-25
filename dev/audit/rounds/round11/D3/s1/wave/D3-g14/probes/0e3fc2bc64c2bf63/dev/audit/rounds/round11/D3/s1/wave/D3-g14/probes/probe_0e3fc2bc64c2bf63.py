#!/usr/bin/env python3
# Metric: plan value (kW) _apply_dhw_pins returns at a step pinned exactly 0.5 (planned 0 kW, min_run_power 0.6).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_0e3fc2bc64c2bf63.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_pins line 1649 `if pin >= 0.5:`
# Perturbation: mutant 0e3fc2bc64c2bf63 (dev/audit/rounds/round11/D3/s1/state/results/complete/0e3fc2bc64c2bf63.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: 0.6 kW (force-on) -> 0.0 kW (force-off) at pin == 0.5.
# Inputs tried: pins 0.5, 0.49999, 0.50001, 0, 1, NaN; production reach: manual_plan.channel_pins emits only PIN_ON 1.0, PIN_OFF 0.0 and NaN (manual_plan.py:41-42, 215-220); the three ordinary days with pins {0,1,NaN} (realistic_delta).
# Null control: pins 0, 1, NaN and 0.5 +- 1e-5: identical in both arms.
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
KEY = '0e3fc2bc64c2bf63'

MUT = mutant_method("_apply_dhw_pins", mutant_dict(KEY))
MUTF = MUT.__func__ if isinstance(MUT, staticmethod) else MUT
plan = np.zeros(1)
print(f"RESULT baseline_kw_at_pin_0p5={DhwPlanner._apply_dhw_pins(plan, np.array([0.5]), 0.6)[0]:.6f} kW")
print(f"RESULT mutant_kw_at_pin_0p5={MUTF(plan, np.array([0.5]), 0.6)[0]:.6f} kW")
d = 0.0
for p in (0.0, 1.0, float("nan"), 0.49999, 0.50001):
    d = max(d, abs(DhwPlanner._apply_dhw_pins(plan, np.array([p]), 0.6)[0] - MUTF(plan, np.array([p]), 0.6)[0]))
print(f"RESULT null_delta_kw={d:.6f} kW")
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pins = np.full(N, np.nan); pins[8:16] = 0.0; pins[40:44] = 1.0
h = horizon(prices=np.r_[np.full(24, 0.2), np.full(72, 1.0)], dhw_pins=pins)
b, _ = pl._build_dhw_requirements(h, p_max=4.0)
with mock.patch.object(DhwPlanner, "_apply_dhw_pins", MUT):
    m, _ = pl._build_dhw_requirements(h, p_max=4.0)
print(f"RESULT realistic_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
