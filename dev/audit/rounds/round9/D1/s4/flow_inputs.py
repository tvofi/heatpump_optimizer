#!/usr/bin/env python3
"""D1-s4 M6: hostile supply/return readings into the flow-curve bias learner.

Metric (one line): over the hostile reading table x 50 cycles, the count of cycles that raise,
and the count whose learned bias_k leaves [-FLOW_BIAS_CLAMP_K, +FLOW_BIAS_CLAMP_K] or is
non-finite.  Key: FlowCurveBias.bias_k as the production fold leaves it.

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/flow_inputs.py
          [--perturb]  np.clip in flow_lift replaced by identity (the estimate clamp removed):
                       out_of_clamp goes UP.
Expected (baseline): raised=0, out_of_clamp=0, bias at +/-15 K for the 1e308-class rows.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6
Instrumented: custom_components.heatpump_optimizer.flow_lift:FlowCurveBias.observe_temps,
              FlowCurveBias.observe, curve_supply_temp (through a real ThermalModel)
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import math
import sys
import time
from unittest import mock

sys.path[:0] = [".", "tests", "tests/hastub", "custom_components"]
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import flow_lift as F  # noqa: E402

PERTURB = "--perturb" in sys.argv
model = golden.make(dhw=False, hours=6)["optimizer"].model
HOSTILE = [45.0, float("nan"), float("inf"), float("-inf"), 1e308, -1e308, 0.0, -273.15,
           5000.0, None, np.float32(1e38), np.float64("nan")]
OUTDOOR = [-10.0, 0.0, float("nan"), float("inf"), 1e308]

ps = []
if PERTURB:
    real_np = F.np

    class _NP:
        def __getattr__(self, k):
            return getattr(real_np, k)

        @staticmethod
        def clip(v, lo, hi):
            return v
    ps.append(mock.patch.object(F, "np", _NP()))
for p in ps:
    p.start()
raised = oob = cycles = 0
try:
    for out in OUTDOOR:
        fb = F.FlowCurveBias()
        for _ in range(50 // len(HOSTILE) + 1):
            for sup in HOSTILE:
                cycles += 1
                try:
                    fb.observe_temps(sup, sup)
                    curve = F.curve_supply_temp(model, out, 21.0)
                    if fb.last_supply_c is not None and curve is not None:
                        fb.observe(fb.last_supply_c, curve)
                except Exception:  # noqa: BLE001
                    raised += 1
                    continue
                if not math.isfinite(fb.bias_k) or abs(fb.bias_k) > F.FLOW_BIAS_CLAMP_K:
                    oob += 1
finally:
    for p in reversed(ps):
        p.stop()
print(f"MODE perturb={PERTURB}")
print(f"RESULT cycles={cycles} count")
print(f"RESULT raised={raised} count")
print(f"RESULT out_of_clamp={oob} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
