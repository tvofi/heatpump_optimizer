"""D2 verify-v1 (round 9): D2-s2-02 reach -- how high the model's own flow curve goes on every presets.derive house.

Metric (one line): over every presets.derive configuration (structure x era x foundation x
  upper/lower emitter x 1/2-zone x area) with flow_curve_cop_enabled, the maximum of
  flow_lift.curve_supply_temp(model, outdoor, indoor_target) over outdoor -25..10 C; and the
  count of configurations whose curve max + FLOW_BIAS_CLAMP_K is below 45 C (a 45 C fixed-setpoint
  plant cannot be priced at its real supply there).
Count key: the float curve_supply_temp returns (production seam) and flow_lift.FLOW_BIAS_CLAMP_K.
Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v1/curve_reach.py [--perturb]
Perturbation (--perturb): flow_lift.FLOW_BIAS_CLAMP_K 15 -> 40 in memory; unreachable_45C count -> 0.
Expected (baseline 1936d5ca + evidence 6f51db2c): see verify-v1 report; deterministic, exact.
Machine: G3-V1 cloud container, 4 cores, py3.14.0rc2, numpy 2.4.6.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import itertools
import sys
import time
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import flow_lift, presets  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

if "--perturb" in sys.argv:
    flow_lift.FLOW_BIAS_CLAMP_K = 40.0
t0p, t0t = time.process_time(), time.thread_time()
outs = np.arange(-25.0, 10.01, 1.0)
n = unreach45 = unreach40 = 0
cmax_all, cmin_all = -1e9, 1e9
by_emitter = {}
for st, era, fnd, up, lo, tz, area in itertools.product(
        presets.STRUCTURES, tuple(presets._ERA_LOSS_W_PER_M2K), tuple(presets._FOUNDATION_ADJUST),
        presets.EMITTERS, presets.EMITTERS, (False, True), (40.0, 140.0, 400.0)):
    bp = presets.BuildingPreset(structure=st, era=era, foundation=fnd, heated_area_m2=area,
                                upper_emitter=up, lower_emitter=lo, upper_area_ratio=0.5, two_zone=tz)
    cfg = dict(presets.derive(bp))
    cfg["two_zone_mode"] = "on" if tz else "off"
    cfg["flow_curve_cop_enabled"] = True
    p = ThermalParameters.from_config(cfg)
    if not p.flow_curve_cop:
        continue
    m = ThermalModel(p)
    tgt = p.flow_curve_indoor_target
    cm = max(flow_lift.curve_supply_temp(m, float(o), tgt) for o in outs)
    n += 1
    cmax_all = max(cmax_all, cm); cmin_all = min(cmin_all, cm)
    key = f"{up}/{lo}"
    by_emitter[key] = max(by_emitter.get(key, -1e9), cm)
    if cm + flow_lift.FLOW_BIAS_CLAMP_K < 45.0:
        unreach45 += 1
    if cm + flow_lift.FLOW_BIAS_CLAMP_K < 40.0:
        unreach40 += 1
for k, v in sorted(by_emitter.items()):
    print(f"# emitters {k:22s} curve_max {v:.2f} C")
print(f"RESULT configs={n} count")
print(f"RESULT curve_max_over_configs={cmax_all:.3f} C")
print(f"RESULT curve_max_min_over_configs={cmin_all:.3f} C")
print(f"RESULT unreachable_45C={unreach45} configs")
print(f"RESULT unreachable_40C={unreach40} configs")
print(f"RESULT clamp_K={flow_lift.FLOW_BIAS_CLAMP_K}")
print(f"RESULT thread_factor={(time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
