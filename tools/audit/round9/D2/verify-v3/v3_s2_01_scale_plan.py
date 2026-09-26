#!/usr/bin/env python3
"""V3 (round 9, D2-s2-01): plan consequence of the unscaled settlement caps at moderate learned scales.

Metric (one line): per (scenario, learned house_heat_loss_scale s), with s set on the params
the way coordinator._apply_house_heat_loss_scale sets it, the published
OptimizationResult.predicted_savings of the production solve minus that of a solve whose
optimizer.slab_settlement_cap and optimizer.hold_demand_kw receive a params copy with
heat_loss_coefficient/upper_floor_heat_loss/lower_floor_heat_loss multiplied by s and the scale
reset to 1 (the dynamics' own effective loss), as a share of |baseline_cost|; plus the
end-slab delta (production - fixed) and the L1 difference of the two power schedules (kWh).
s in {0.7, 1.3, 2.0}; scenarios winter_single_no_dhw, winter_two_zone_no_dhw, shoulder; null s=1.0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s2_01_scale_plan.py
Perturbation: the fixed arm is the perturbation (in memory, mock.patch.object on the two
optimizer module symbols); at s=1 every delta must be 0 (null control).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G3-V3 cloud container, 4 cores, linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy, sys, time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from unittest import mock
from heatpump_optimizer import optimizer as om
import golden

t0p, t0t = time.process_time(), time.thread_time()
_cap, _hold = om.slab_settlement_cap, om.hold_demand_kw

def folded(p):
    q = copy.copy(p)
    s = p.house_heat_loss_scale
    q.heat_loss_coefficient = p.heat_loss_coefficient * s
    q.upper_floor_heat_loss = p.upper_floor_heat_loss * s
    q.lower_floor_heat_loss = p.lower_floor_heat_loss * s
    q.house_heat_loss_scale = 1.0
    return q

def solve(name, s, fix):
    built = golden.make(**golden.SCENARIOS[name])
    opt = built["optimizer"]
    opt.model.params.house_heat_loss_scale = s
    patches = []
    if fix:
        patches = [mock.patch.object(om, "slab_settlement_cap", lambda p, *a, **k: _cap(folded(p), *a, **k)),
                   mock.patch.object(om, "hold_demand_kw", lambda p, *a, **k: _hold(folded(p), *a, **k))]
    for pt in patches: pt.start()
    try:
        return golden.capture.__globals__["HeatPumpOptimizer"] and opt.optimize(
            built["state"], built["prices"], built["outdoor"], built["wind"], built["rain"],
            built["solar"], golden.START, None, None)
    finally:
        for pt in patches: pt.stop()

rows = []
for name in ("winter_single_no_dhw", "winter_two_zone_no_dhw", "shoulder"):
    for s in (1.0, 0.7, 1.3, 2.0):
        a = solve(name, s, False); b = solve(name, s, True)
        base = abs(a.baseline_cost) or 1.0
        dsav = a.predicted_savings - b.predicted_savings
        dslab = a.slab_temp_trajectory[-1] - b.slab_temp_trajectory[-1]
        l1 = float(np.sum(np.abs(np.asarray(a.power_schedule) - np.asarray(b.power_schedule)))) * 0.25
        rows.append((name, s, dsav, dsav / base, dslab, l1))
        print(f"RESULT {name}_s{s}_savings_prod_minus_fix={dsav:.4f} currency ({100*dsav/base:.2f} pct of baseline {a.baseline_cost:.2f})")
        print(f"RESULT {name}_s{s}_end_slab_prod_minus_fix={dslab:.4f} K")
        print(f"RESULT {name}_s{s}_power_L1={l1:.4f} kWh")
null = [r for r in rows if r[1] == 1.0]
print(f"RESULT null_max_abs_savings_delta={max(abs(r[2]) for r in null):.3e} currency")
for s in (0.7, 1.3, 2.0):
    sel = [r for r in rows if r[1] == s]
    print(f"RESULT s{s}_max_abs_savings_share={max(abs(r[3]) for r in sel)*100:.3f} pct")
    print(f"RESULT s{s}_max_abs_end_slab={max(abs(r[4]) for r in sel):.3f} K")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
