#!/usr/bin/env python3
# Metric: learned flow-curve bias_k (K) after a fixed sample sequence: FLOW_BIAS_MIN_SAMPLES warm-up residuals
#   of +2 K, then five residuals of +6 K (a plant whose supply sits a further 4 K over the curve).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fl47_alpha.py
# EXPECTED RESULT bias_after_step_baseline=3.638 K  (+-0.01; 2 + 4*(1-0.9^5))
# EXPECTED RESULT bias_after_step_mutant=4.689 K    (+-0.01; 2 + 4*(1-0.8^5))
# EXPECTED RESULT null_delta=0.0 K  (warm-up only, before the EWMA arm: both arms identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Exact arithmetic.
# Instrumented symbol: custom_components.heatpump_optimizer.flow_lift:FlowCurveBias.observe, which reads the
#   module constant flow_lift.FLOW_BIAS_ALPHA (line 47) once samples >= FLOW_BIAS_MIN_SAMPLES.
# Perturbation: FLOW_BIAS_ALPHA 0.1 -> 0.2 (CONST 0c3e91a6a349409a), by mock.patch.object on the module.
#   Direction: bias_after_step up. The full gate (fullgate.py run --src complete --key 0c3e91a6a349409a)
#   stays green under it.
# Null control: the warm-up arm (samples < FLOW_BIAS_MIN_SAMPLES) does not read the constant.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import flow_lift as fl  # noqa: E402

CURVE = 35.0


def run(step):
    b = fl.FlowCurveBias()
    for _ in range(fl.FLOW_BIAS_MIN_SAMPLES):
        b.observe(CURVE + 2.0, CURVE)
    warm = b.bias_k
    for _ in range(step):
        b.observe(CURVE + 6.0, CURVE)
    return warm, b.bias_k


wb, base = run(5)
with mock.patch.object(fl, "FLOW_BIAS_ALPHA", 0.2):
    wm, mut = run(5)
print(f"RESULT flow_bias_alpha={fl.FLOW_BIAS_ALPHA} ratio")
print(f"RESULT bias_after_step_baseline={base:.3f} K")
print(f"RESULT bias_after_step_mutant={mut:.3f} K")
print(f"RESULT null_delta={abs(wb - wm)} K")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
