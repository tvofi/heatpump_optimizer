"""D2-s2 / D2.M2 -- the #1067 direct-plant flow lift cannot reach the plant's real supply.

Metric (one line): cop_overstatement_max = max over outdoor in [-25, 10] C of
  compute_cop(outdoor) [flow_curve_cop on, flow_curve_bias = what FlowCurveBias learns from a
  plant whose measured supply is SUPPLY_C] / _cop_law(outdoor, None, SUPPLY_C) - 1
  i.e. how much the priced COP exceeds the COP at the supply the plant actually ran at.
  count key: the float ThermalModel.compute_cop returns (production seam), against the same
  model's own Carnot law evaluated at the measured supply.
Also: curve_flow_max = max of ThermalModel.curve_flow_temp over -30..15 C on the default houses,
  and clamp_bound_cells = outdoor cells where the learned bias sits at the clamp.
Arms: SUPPLY_C = 45 (flow_lift.py's own fixed-setpoint example), 40, 50; one- and two-zone
  default houses (tests/profiles.py:house). Null control: SUPPLY_C = curve + 10 K (within the
  clamp) -> overstatement 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/flow_bias_clamp.py [--perturb]
Expect (baseline 1936d5ca, box B5): see REPORT, deterministic (exact to 1e-6).
Perturbation (--perturb): flow_lift.FLOW_BIAS_CLAMP_K 15 -> 40 (in memory) ->
  cop_overstatement_max falls to 0 (direction: to_zero).
Instrumented: flow_lift:FlowCurveBias.observe, flow_lift:curve_supply_temp,
  thermal_model:ThermalModel.compute_cop
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
from heatpump_optimizer import flow_lift  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

if "--perturb" in sys.argv:
    flow_lift.FLOW_BIAS_CLAMP_K = 40.0

t0 = time.process_time(); tt0 = time.thread_time()


def mk(two_zone):
    cfg = house(two_zone=two_zone, dhw=False)
    cfg["flow_curve_cop_enabled"] = True
    p = ThermalParameters.from_config(cfg)
    assert p.flow_curve_cop, "flag did not reach params"
    return ThermalModel(p)


season = np.arange(-25.0, 10.01, 0.5)
res = {}
cmax = -1e9
for tz in (False, True):
    m = mk(tz)
    cmax = max(cmax, max(m.curve_flow_temp(float(o)) for o in np.arange(-30.0, 15.01, 0.5)))
res["curve_flow_max_C"] = round(cmax, 3)
worst_all = 0.0
for label, supply_fn in (("fixed45", lambda c: 45.0), ("fixed40", lambda c: 40.0),
                         ("fixed50", lambda c: 50.0), ("null_curve_plus10", lambda c: c + 10.0)):
    worst = 0.0; at_clamp = 0; cells = 0; mean_over = []
    for tz in (False, True):
        m = mk(tz)
        target = m.params.flow_curve_indoor_target
        # learn: one season of (measured, curve) pairs through the production fold
        learner = flow_lift.FlowCurveBias()
        for o in season:
            curve = flow_lift.curve_supply_temp(m, float(o), target)
            learner.observe(supply_fn(curve), curve)
        m.params.flow_curve_bias = learner.bias_k
        for o in season:
            curve = flow_lift.curve_supply_temp(m, float(o), target)
            real_supply = supply_fn(curve)
            priced = m.compute_cop(float(o))
            true = max(m._cop_law(float(o), None, real_supply), 1.0)
            over = priced / true - 1.0
            cells += 1
            mean_over.append(over)
            worst = max(worst, over)
            if abs(abs(learner.bias_k) - flow_lift.FLOW_BIAS_CLAMP_K) < 1e-9:
                at_clamp += 1
        print(f"# arm={label:18s} two_zone={tz} learned_bias={learner.bias_k:.3f} K")
    res[f"{label}_cop_overstatement_max"] = round(worst, 4)
    res[f"{label}_cop_overstatement_mean"] = round(float(np.mean(mean_over)), 4)
    res[f"{label}_clamp_bound_cells"] = at_clamp
    res[f"{label}_cells"] = cells
    if not label.startswith("null"):
        worst_all = max(worst_all, worst)
res["cop_overstatement_max"] = round(worst_all, 4)
res["clamp_K"] = flow_lift.FLOW_BIAS_CLAMP_K
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
for k, v in res.items():
    print(f"RESULT {k}={v}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
