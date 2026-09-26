"""Verifier V2 (independent) check on D2-s1-51.

Metric (own, independent of the finder's coordinator rig): relative overstatement of
compute_cop_dhw(outdoor, flow) at the ThermalState default outdoor=5.0 degC versus at a cold
forecast outdoor temperature, for the flow temperatures the DHW setpoint sweep actually uses
(45-65 degC in 5 degC steps, matching the candidate setpoints). This is the physical root of
D2-s1-51 (the coordinator prices candidates using this COP), measured directly on the production
COP function rather than through the coordinator/_rig harness.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
  tools/audit/round9/D2/verify-v2-leads/v2_dhw_cop_sensitivity.py
Instrumented symbol: heatpump_optimizer.thermal_model:ThermalParameters.compute_cop_dhw (via a
  default ThermalParameters instance, matching thermal_model.ThermalState's constructor default
  outdoor_temperature=5.0).
Perturbation: none needed here (this is a direct evaluation of the production function at two
  operating points); the coordinator-level perturbation is verified by re-running the finder's own
  harness with --forecast (recorded separately).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

t0, th0 = time.process_time(), time.thread_time()
params = ThermalParameters.from_config({})
model = ThermalModel(params)
DEFAULT_OUTDOOR = ThermalState().outdoor_temperature
assert DEFAULT_OUTDOOR == 5.0, DEFAULT_OUTDOOR

flows = np.arange(45.0, 66.0, 5.0)
cold_forecasts = (-15.0, -5.0)
worst = 0.0
for f in cold_forecasts:
    for flow in flows:
        cop_default = model.compute_cop_dhw(DEFAULT_OUTDOOR, float(flow))
        cop_forecast = model.compute_cop_dhw(f, float(flow))
        rel = abs(cop_default - cop_forecast) / cop_forecast
        worst = max(worst, rel)
        print(f"CELL forecast={f:+.0f} flow={flow:.0f} cop_default={cop_default:.3f} "
              f"cop_forecast={cop_forecast:.3f} rel_diff={rel:.3f}")

print(f"RESULT worst_cop_rel_diff={worst:.4f} ratio")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
