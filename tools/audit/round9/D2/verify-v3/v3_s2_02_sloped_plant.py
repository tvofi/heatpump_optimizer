#!/usr/bin/env python3
"""V3 (round 9, D2-s2-02): the #1067 clamp against sloped (real weather-curve) plants, with the flag-off reference.

Metric (one line): per plant slope k in {0.5, 0.8, 1.0, 1.2} and fixed setpoints 45, 50 C (plant supply = min(55, 20 + k*(20 - out)) C,
a heating-curve plant rather than a fixed setpoint), the heat-demand-weighted mean over outdoor
-20..12 C (weight max(0, 17 - out)) of priced COP / COP at the plant's real supply - 1, where the
priced COP is production ThermalModel.compute_cop with flow_curve_cop on and flow_curve_bias as
learned by production flow_lift.FlowCurveBias.observe over the same outdoor sequence, and
"true" is the same model's _cop_law at the real supply; reported for three arms: on (production,
clamp 15 K), off (flag off: what an install without #1067 prices), wide (clamp 40 K in memory).
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s2_02_sloped_plant.py
Perturbation: the wide arm (flow_lift.FLOW_BIAS_CLAMP_K 15 -> 40 via mock.patch.object) must lower the
on-arm's overstatement wherever the learned bias sits at the clamp (direction: down).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G3-V3 cloud container, 4 cores, linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
from unittest import mock
from profiles import house
from heatpump_optimizer import flow_lift
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

t0p, t0t = time.process_time(), time.thread_time()
outs = np.arange(-20.0, 12.01, 0.5)
w = np.maximum(0.0, 17.0 - outs)

def model(flag, tz):
    cfg = house(two_zone=tz, dhw=False)
    cfg["flow_curve_cop_enabled"] = flag
    return ThermalModel(ThermalParameters.from_config(cfg))

def arm(k, tz, mode):
    plant = (lambda o: float(-k)) if k < 0 else (lambda o: min(55.0, 20.0 + k * (20.0 - o)))
    if mode == "off":
        m = model(False, tz)
        bias = 0.0
    else:
        m = model(True, tz)
        clamp = 40.0 if mode == "wide" else flow_lift.FLOW_BIAS_CLAMP_K
        with mock.patch.object(flow_lift, "FLOW_BIAS_CLAMP_K", clamp):
            L = flow_lift.FlowCurveBias()
            tgt = m.params.flow_curve_indoor_target
            for o in outs:
                L.observe(plant(float(o)), flow_lift.curve_supply_temp(m, float(o), tgt))
        bias = L.bias_k
        m.params.flow_curve_bias = bias
    over = np.array([m.compute_cop(float(o)) / max(m._cop_law(float(o), None, plant(float(o))), 1.0) - 1.0
                     for o in outs])
    return float(np.sum(w * over) / np.sum(w)), float(over.max()), bias

for k in (0.5, 0.8, 1.0, 1.2, -45.0, -50.0):  # negative k = fixed setpoint at |k| C
    for tz in (False, True):
        tag = (f"fixed{int(-k)}_" if k < 0 else f"k{k}_") + ("2z" if tz else "1z")
        for mode in ("on", "off", "wide"):
            mean, mx, b = arm(k, tz, mode)
            print(f"RESULT {tag}_{mode}_weighted_overstatement={mean:.4f} ratio (max {mx:.4f}, bias {b:.2f} K)")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
