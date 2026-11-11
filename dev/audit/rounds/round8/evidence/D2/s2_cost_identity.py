"""D2-s2 harness (non-finding): predicted_cost and savings identities on every
golden plan fixture.

Metric: max over fixtures of |predicted_cost - dt*sum(p*(P+D) - margin*min(P+D,s))|
(margin = pv.import_margin(p, export=0.0, the golden default)) and of
|predicted_savings - (baseline_cost - predicted_cost - deferred_energy_cost)|.
Recorded fixtures round power to 1e-3 kW, so the tolerance is 5e-4 SEK.
Command: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s2_cost_identity.py
Expected: fixtures=50, max_cost_residual<5e-4 SEK, max_savings_residual<5e-4 SEK.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, glob, json, time
sys.path.insert(0, ".")
import numpy as np
from custom_components.heatpump_optimizer import pv

t0p, t0t = time.process_time(), time.thread_time()
DT = 0.25
worst_c = worst_s = 0.0
n = 0
for f in sorted(glob.glob("tests/golden/*.json")):
    d = json.load(open(f))
    if "predicted_cost" not in d:
        continue
    n += 1
    p = np.asarray(d["prices"], float)
    P = np.asarray(d["power_schedule"], float) + np.asarray(
        d.get("dhw_power_schedule") or np.zeros(len(p)), float)
    s = np.asarray(d.get("pv_surplus") or np.zeros(len(p)), float)
    m = pv.import_margin(p, 0.0)
    c = (np.sum(p * P) - np.sum(m * np.minimum(P, s))) * DT
    worst_c = max(worst_c, abs(c - d["predicted_cost"]))
    worst_s = max(worst_s, abs(d["predicted_savings"] - (
        d["baseline_cost"] - d["predicted_cost"] - d["deferred_energy_cost"])))
print(f"RESULT fixtures={n} count")
print(f"RESULT max_cost_residual={worst_c:.6f} SEK")
print(f"RESULT max_savings_residual={worst_s:.6f} SEK")
pc_, tc_ = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc_ / max(tc_, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
