#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s2-02: FLOW_BIAS_CLAMP_K vs the model's own curve.

Metric (one line): on each stress.py BUILDINGS preset (presets.derive, not the profile
default house), a radiator plant following a real weather curve
supply(out) = 21 + 1.0*(21 - out) degC (52 at -10, 31 at 10) is fed through
FlowCurveBias.observe for 400 cycles over outdoor -10..10; reported: max over outdoor
of (supply - ThermalModel.curve_flow_temp) = kelvin of real lift left unpriced, and
max of compute_cop / _cop_law(out, None, supply) - 1 (COP overstatement), beside the
same overstatement with flow_curve_cop OFF (the shipped default), which prices no lift.
Count key: the float compute_cop returns, against the model's own _cop_law at the supply.
Hooks: flow_lift:FlowCurveBias.observe, flow_lift:curve_supply_temp, thermal_model:ThermalModel.compute_cop.
Perturbation: --perturb sets flow_lift.FLOW_BIAS_CLAMP_K = 60 in memory: the flag-on overstatement must fall.
Null control: a plant at curve+5 K (inside the clamp): overstatement ~0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_flow.py [--perturb]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Deterministic.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import house  # noqa: E402
from stress import BUILDINGS  # noqa: E402
from heatpump_optimizer import flow_lift, presets  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

if "--perturb" in sys.argv:
    flow_lift.FLOW_BIAS_CLAMP_K = 60.0
t0p, t0t = time.process_time(), time.thread_time()
OUTS = np.arange(-10.0, 10.01, 1.0)


def model(name, flag):
    cfg = house(two_zone=False, dhw=False)
    d = presets.derive(BUILDINGS[name])
    d.pop("heating_response_hours", None)
    cfg.update(d)
    cfg["flow_curve_cop_enabled"] = flag
    return ThermalModel(ThermalParameters.from_config(cfg))


def run(name, supply_of):
    m = model(name, True)
    learner = flow_lift.FlowCurveBias()
    rng = np.random.default_rng(7)
    for _ in range(400):
        o = float(rng.choice(OUTS))
        learner.observe(supply_of(m, o), flow_lift.curve_supply_temp(m, o, m.params.flow_curve_indoor_target))
    m.params.flow_curve_bias = learner.bias_k
    off = model(name, False)
    unpriced = over_on = over_off = 0.0
    curve_max = -1e9
    for o in OUTS:
        sup = supply_of(m, o)
        priced = m.curve_flow_temp(o)
        curve_max = max(curve_max, priced - m.params.flow_curve_bias)
        unpriced = max(unpriced, sup - priced)
        truth = m._cop_law(o, None, sup)
        over_on = max(over_on, m.compute_cop(o) / truth - 1.0)
        over_off = max(over_off, off.compute_cop(o) / off._cop_law(o, None, sup) - 1.0)
    return curve_max, learner.bias_k, unpriced, over_on, over_off


worst_on = worst_off = worst_unpriced = null_worst = 0.0
for name in BUILDINGS:
    cm, b, un, on, of = run(name, lambda m, o: 21.0 + (21.0 - o))
    _, _, _, n_on, _ = run(name, lambda m, o: flow_lift.curve_supply_temp(m, o, 21.0) + 5.0)
    print(f"# {name}: curve_max={cm:.2f} C bias={b:.2f} K unpriced_max={un:.2f} K over_on={on:.4f} over_off={of:.4f} null_on={n_on:.2e}")
    worst_on, worst_off = max(worst_on, on), max(worst_off, of)
    worst_unpriced, null_worst = max(worst_unpriced, un), max(null_worst, abs(n_on))
print(f"RESULT presets={len(BUILDINGS)} count")
print(f"RESULT unpriced_lift_max={worst_unpriced:.3f} K")
print(f"RESULT cop_overstatement_flag_on_max={worst_on:.4f} ratio")
print(f"RESULT cop_overstatement_flag_off_max={worst_off:.4f} ratio")
print(f"RESULT null_curve_plus5_overstatement_max={null_worst:.2e} ratio")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
