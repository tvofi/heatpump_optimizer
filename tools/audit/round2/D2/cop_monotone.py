#!/usr/bin/env python
"""D2 harness -- COP monotonicity in outdoor temperature under the Carnot flow derate.

Metric: number of sign changes of dCOP/dT_out over T_out in [-25, 30] deg C (0.5 K
grid) for ThermalModel.compute_cop(T_out, flow_temp=F) with cop_flow_carnot=True
(what ThermalParameters.from_config sets whenever a mixing valve throttles), per
flow temperature F; the outdoor temperature at which COP peaks; and COP at 20 deg C
outdoor as a ratio of that peak. Plus the implied Carnot fraction band of the base
curve, the DHW COP monotonicity, the defrost derate bounds and band-edge jump, and
the downstream buffer marginal COP / charge ceiling.
Command:
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/cop_monotone.py
  PYTHONPATH=tests/hastub python tools/audit/round2/D2/cop_monotone.py --perturb
Expected (c398fc84): cop_sign_changes_flow55 = 1 (peak near +10 deg C outdoor),
  cop_ratio_20_over_peak_flow55 < 1; cop_sign_changes_flowNone = 0.
Perturbation (--perturb): cop_flow_carnot=False -> every sign-change count = 0 (to_zero).
Instrumented: thermal_model:ThermalModel.compute_cop, ThermalModel.marginal_cop,
  ThermalModel.compute_cop_dhw, defrost:DefrostDerate.factor,
  optimizer:HeatPumpOptimizer._buffer_charge_ceiling.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import resource
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

import golden
from profiles import house
from heatpump_optimizer import defrost
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", action="store_true")
args = ap.parse_args()

cfg = house(two_zone=True, dhw=False)
cfg.update({"mixing_valve_mode": "manual", "buffer_tank_volume": 750.0})
p = ThermalParameters.from_config(cfg)
print(f"CELL cop_flow_carnot as set by from_config for a valve install: {p.cop_flow_carnot}")
if args.perturb:
    p.cop_flow_carnot = False
m = ThermalModel(p)

outs = np.arange(-25.0, 30.01, 0.5)
flows = [None, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0]
changes = {}
ratios = {}
for F in flows:
    cop = np.array([m.compute_cop(float(t), flow_temp=F) for t in outs])
    d = np.sign(np.round(np.diff(cop), 12))
    d = d[d != 0]
    n_changes = int(np.sum(d[1:] != d[:-1])) if d.size > 1 else 0
    i_max = int(np.argmax(cop))
    label = "None" if F is None else f"{int(F)}"
    i20 = int(np.argmin(np.abs(outs - 20.0)))
    i10 = int(np.argmin(np.abs(outs - 10.0)))
    ratio = float(cop[i20] / cop[i_max])
    changes[label] = n_changes
    ratios[label] = ratio
    print(f"CELL flow={label}: sign_changes={n_changes} argmax_out={outs[i_max]:.1f} "
          f"cop_peak={cop[i_max]:.3f} cop10={cop[i10]:.3f} cop20={cop[i20]:.3f} ratio20/peak={ratio:.3f}")
    print(f"RESULT cop_sign_changes_flow{label}={n_changes} count")
    print(f"RESULT cop_argmax_out_flow{label}={outs[i_max]:.1f} degC")
    print(f"RESULT cop_ratio_20_over_peak_flow{label}={ratio:.4f} ratio")
flow_cells = [k for k in changes if k != "None"]
nonmono = [k for k in flow_cells if changes[k] > 0]
print(f"RESULT cop_flow_cells={len(flow_cells)} count")
print(f"RESULT cop_flow_cells_nonmonotone={len(nonmono)} count")
rs = np.array([ratios[k] for k in flow_cells])
print(f"RESULT cop_ratio_20_over_peak_min={float(rs.min()):.4f} ratio")
print(f"RESULT cop_ratio_20_over_peak_max={float(rs.max()):.4f} ratio")
print(f"RESULT cop_ratio_20_over_peak_drop_most_favourable={float(np.sort(rs)[1:].min()) if rs.size > 1 else 0:.4f} ratio")

# Monotone in flow temperature at fixed outdoor (should be non-increasing above ref)
viol = 0
for t in (-10.0, 0.0, 7.0, 15.0):
    seq = [m.compute_cop(t, flow_temp=F) for F in np.arange(35.0, 70.1, 1.0)]
    viol += int(np.sum(np.diff(seq) > 1e-12))
print(f"RESULT cop_flow_monotone_violations={viol} count")

# Implied Carnot fraction of the base curve (flow at reference 35 C)
eta = []
for t in np.arange(-20.0, 25.01, 1.0):
    c = m.compute_cop(float(t))
    lift = (p.cop_flow_reference_temp + 273.15) - (t + 273.15)
    eta.append(c * lift / (p.cop_flow_reference_temp + 273.15))
eta = np.array(eta)
print(f"RESULT carnot_fraction_min={float(eta.min()):.3f} ratio")
print(f"RESULT carnot_fraction_max={float(eta.max()):.3f} ratio")

# DHW COP: monotone non-increasing in tank temperature, non-decreasing in outdoor
v1 = 0
for t in (-10.0, 0.0, 10.0, 20.0):
    seq = [m.compute_cop_dhw(t, T) for T in np.arange(30.0, 70.1, 1.0)]
    v1 += int(np.sum(np.diff(seq) > 1e-12))
v2 = 0
for T in (45.0, 55.0, 60.0):
    seq = [m.compute_cop_dhw(float(t), T) for t in outs]
    v2 += int(np.sum(np.diff(seq) < -1e-12))
print(f"RESULT cop_dhw_monotone_violations_tank={v1} count")
print(f"RESULT cop_dhw_monotone_violations_outdoor={v2} count")

# Defrost derate: bounds over random learning, and the jump at the band edges
d = defrost.DefrostDerate()
rng = np.random.default_rng(3)
lo, hi = 10.0, 0.0
for _ in range(2000):
    d.observe(float(rng.uniform(-30, 40)), float(rng.uniform(0, 100)), float(rng.uniform(0.01, 3.0)))
    d.observe_duty(float(rng.uniform(-30, 40)), float(rng.uniform(0, 100)), float(rng.uniform(0.0, 1.0)))
    f = d.factor(float(rng.uniform(-30, 40)), float(rng.uniform(0, 100)))
    lo, hi = min(lo, f), max(hi, f)
print(f"RESULT derate_factor_min={lo:.4f} ratio")
print(f"RESULT derate_factor_max={hi:.4f} ratio")
d2 = defrost.DefrostDerate()
for _ in range(200):
    d2.observe(1.0, 85.0, 0.8)  # a fully-earned 0.8 in the [0,2) C humid bucket
jump = abs(d2.factor(-1e-9, 85.0) - d2.factor(0.0, 85.0))
print(f"RESULT derate_jump_at_0C_edge={jump:.4f} ratio")
p.defrost_derate = d2
cj = abs(m.compute_cop(-1e-9, humidity=85.0) - m.compute_cop(0.0, humidity=85.0)) / m.compute_cop(-1e-9, humidity=85.0)
print(f"RESULT cop_relative_jump_at_0C_edge={cj:.4f} ratio")
p.defrost_derate = None

# Downstream: the buffer's marginal COP at 60 C and the charge ceiling vs outdoor mean
built = golden.make(**golden.SCENARIOS["valve_storage"])
opt = built["optimizer"]
if args.perturb:
    opt.model.params.cop_flow_carnot = False
for t in (0.0, 5.0, 10.0, 15.0, 20.0):
    mc = opt.model.marginal_cop(t, "buffer", store_temp=60.0)
    ceil = opt._buffer_charge_ceiling(t)
    print(f"CELL out_mean={t:.0f}: marginal_cop_buffer60={mc:.3f} charge_ceiling={ceil:.2f}")
    print(f"RESULT marginal_cop_buffer60_out{int(t)}={mc:.4f} ratio")
    print(f"RESULT buffer_charge_ceiling_out{int(t)}={ceil:.3f} degC")
mc = [opt.model.marginal_cop(t, "buffer", store_temp=60.0) for t in np.arange(0.0, 25.1, 1.0)]
print(f"RESULT marginal_cop_buffer60_sign_changes={int(np.sum(np.diff(np.sign(np.diff(mc))) != 0))} count")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
