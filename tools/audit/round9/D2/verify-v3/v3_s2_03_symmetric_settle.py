#!/usr/bin/env python3
"""V3 (round 9, D2-s2-03): the wood-coil settle-up, one-sided fix versus a fix that drains both ends.

Metric (one line): on golden wood_coil (wood start W in {55, 70, 85} C), the DHW-path
HeatPumpOptimizer._deferred_energy_cost re-evaluated inside the production call (hooked) with
(A) production arguments, (B) optimized_end's stores replaced by the published
simulate_trajectory_with_dhw end state (the finder's one-sided fix), and (C) as B plus
baseline_end.wood_tank_temperature lowered by the baseline's own coil heat over the horizon,
sum_i coil(dhw_draw_power, W0)*dt / wood_tank_thermal_mass -- the same held-at-initial coil
_baseline_dhw_economics already prices for the baseline (optimizer.py, the dhw_coil_draw_reduction
call in the baseline) -- reported as savings overstatement = deferred(X) - deferred(A) for X in {B, C}.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s2_03_symmetric_settle.py
Perturbation: arm B is the finder's perturbation; arm C adds the baseline drain; null control: a DHW
scenario without the coil (winter_single_dhw) must read B = C = 0.
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
from heatpump_optimizer import thermal_model as tm
import golden

t0p, t0t = time.process_time(), time.thread_time()

def run(name, W):
    spec = copy.deepcopy(golden.SCENARIOS[name])
    if W is not None:
        spec.setdefault("state_overrides", {})["wood_tank_temperature"] = W
    built = golden.make(**spec)
    opt = built["optimizer"]
    p = opt.model.params
    W0 = built["state"].wood_tank_temperature
    last = {}
    orig_traj = tm.ThermalModel.simulate_trajectory_with_dhw
    def traj(self, *a, **k):
        r = orig_traj(self, *a, **k)
        last["r"] = r
        return r
    orig_def = om.HeatPumpOptimizer._deferred_energy_cost
    out = {}
    def dfc(self, baseline_end, optimized_end, prices, outdoor, include_dhw=False, caps=None, humidity=None):
        a = orig_def(self, baseline_end, optimized_end, prices, outdoor, include_dhw, caps, humidity)
        if include_dhw and "r" in last:
            room, slab, up, lo, dhw, buf, wood = last["r"]
            ob = copy.deepcopy(optimized_end)
            ob.room_temperature = float(room[-1]); ob.slab_temperature = float(slab[-1])
            ob.upper_floor_temperature = float(up[-1]); ob.lower_floor_temperature = float(lo[-1])
            ob.buffer_tank_temperature = float(buf[-1])
            if wood is not None: ob.wood_tank_temperature = float(wood[-1])
            b = orig_def(self, baseline_end, ob, prices, outdoor, include_dhw, caps, humidity)
            be = copy.deepcopy(baseline_end)
            if p.dhw_coil_active and W0 is not None and be.wood_tank_temperature is not None:
                red, q = tm.dhw_coil_draw_reduction(p.dhw_draw_power, W0, p.dhw_setpoint,
                                                    inlet_temp=p.dhw_inlet_reference)
                drain = q * 0.25 * len(prices) / p.wood_tank_thermal_mass
                be.wood_tank_temperature = max(p.dhw_inlet_reference, be.wood_tank_temperature - drain)
                out["baseline_drain_K"] = drain
            c = orig_def(self, be, ob, prices, outdoor, include_dhw, caps, humidity)
            out.update(A=a, B=b, C=c)
        return a
    with mock.patch.object(tm.ThermalModel, "simulate_trajectory_with_dhw", traj), \
         mock.patch.object(om.HeatPumpOptimizer, "_deferred_energy_cost", dfc):
        res = opt.optimize(built["state"], built["prices"], built["outdoor"], built["wind"],
                           built["rain"], built["solar"], golden.START, None, None)
    return out, res

for name, W in (("winter_single_dhw", None), ("wood_coil", 55.0), ("wood_coil", 70.0), ("wood_coil", 85.0)):
    o, res = run(name, W)
    tag = f"{name}_W{int(W) if W else 'na'}"
    if "A" not in o:
        print(f"RESULT {tag}_dhw_path_hit=0"); continue
    print(f"RESULT {tag}_overstatement_onesided_B={o['B']-o['A']:.4f} currency")
    print(f"RESULT {tag}_overstatement_symmetric_C={o['C']-o['A']:.4f} currency")
    print(f"RESULT {tag}_baseline_drain={o.get('baseline_drain_K', 0.0):.3f} K")
    print(f"RESULT {tag}_baseline_cost={res.baseline_cost:.3f} currency")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
