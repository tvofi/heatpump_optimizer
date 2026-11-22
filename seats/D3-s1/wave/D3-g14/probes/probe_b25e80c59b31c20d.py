#!/usr/bin/env python3
# Metric: worst simulated tank shortfall (C) below the plan's own floor/ready requirement, for a plan built with manual DHW pins forcing the cheap night steps 8-15 OFF.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_b25e80c59b31c20d.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1184 `if dhw_pins is not None:` (the forced_off mask from pins)
# Perturbation: mutant b25e80c59b31c20d (dev/audit/rounds/round11/D3/s1/state/results/complete/b25e80c59b31c20d.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. Direction: shortfall up (the planners buy energy in the pinned-off steps, the pin overlay deletes it, nothing re-buys it).
# Inputs tried: pins OFF on steps 8-15 under a cheap night (prices 0.1 there, 1.0 elsewhere), window 18:00-20:00, min 45 C, tank 48 C; no pins; pins only ON (steps 40-43).
# Null control: no pins, and on-only pins: the forced_off mask is None in both arms, delta 0.
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
KEY = 'b25e80c59b31c20d'

pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[8:16] = 0.1
pins = np.full(N, np.nan); pins[8:16] = 0.0   # the user pins the cheap night steps OFF


def gap(p):
    """Worst shortfall (C) of the simulated tank below the plan's own floor/ready requirement."""
    t = pl.model.simulate_dhw_only(initial_temp=48.0, dhw_power_schedule=p.schedule, outdoor_temps=np.full(N, -5.0),
                                   draw_rates=p.draw_rates, dt_hours=0.25)
    return float(np.max(np.maximum(p.floor_temps, p.ready_temps) - t[1:]))


b, m = arms(pl, horizon(prices=pr, dhw_pins=pins), KEY, p_max=4.0)
print(f"RESULT baseline_shortfall_c={gap(b):.4f} C")
print(f"RESULT mutant_shortfall_c={gap(m):.4f} C")
print(f"RESULT baseline_kwh={b.schedule.sum() * 0.25:.4f} kWh")
print(f"RESULT mutant_kwh={m.schedule.sum() * 0.25:.4f} kWh")
b0, m0 = arms(pl, horizon(prices=pr), KEY, p_max=4.0)
print(f"RESULT null_delta_kw={float(np.max(np.abs(b0.schedule - m0.schedule))):.6f} kW")
pins_on = np.full(N, np.nan); pins_on[40:44] = 1.0
b1, m1 = arms(pl, horizon(prices=pr, dhw_pins=pins_on), KEY, p_max=4.0)
print(f"RESULT null_on_only_delta_kw={float(np.max(np.abs(b1.schedule - m1.schedule))):.6f} kW")
