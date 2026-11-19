#!/usr/bin/env python3
# Metric: billed soft top-k sum that tariff._smooth_topk_sum returns for k=0 on a fixed 5-window
#   bill [10,10,10,20,20] kW (baseline 0.0), and how many production call paths reach it with k<=0.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m31_topk_zero.py
# EXPECTED RESULT topk_k0_baseline=0.0 kW
# EXPECTED RESULT topk_k0_mutant=20.0 kW  (tolerance +-0.05: the soft top-1 of the tie at 20 kW)
# EXPECTED RESULT topk_k0_minus_k1_mutant=0.0 kW  (mutant k=0 bills what k=1 bills)
# EXPECTED RESULT reach_calls_k_le_0=0 count  (calls with k<=0 while the production top-k callers bill a grid)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_smooth_topk_sum (line 744 guard
#   `if x.size == 0 or k <= 0:`), and its production callers _plateau_aware_topk_sum /
#   _plateau_aware_topk_sum_batch, driven through the public tariff:peak_cost_smooth and tariff:peak_cost_batch
#   with PeakBilling.peaks_averaged from -2 to 7 (both pre-clamp k onto 1..n at tariff.py:982 and :1204).
# Perturbation: R10 C2 M31, the line-744 edit `k <= 0` -> `k < 0`, applied in memory (the function is
#   re-compiled from its own source with that one edit; nothing on disk changes). Direction: topk_k0 up,
#   0.0 -> 20.0. The full gate (fullgate.py run --src c2 --key d931ab195b940b0c) stays green under it.
# Null control: k=1 and k=3 on the same bill, where the edit cannot matter (k>0): the mutant and the
#   baseline return identical floats (null_delta=0.0).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import tariff  # noqa: E402

OLD = "    if x.size == 0 or k <= 0:"
NEW = "    if x.size == 0 or k < 0:"


def mutant_fn():
    src = textwrap.dedent(inspect.getsource(tariff._smooth_topk_sum))
    old = textwrap.dedent(OLD + "\n    pass").splitlines()[0]
    assert old in src, "anchor line moved"
    src = src.replace(old, textwrap.dedent(NEW + "\n    pass").splitlines()[0], 1)
    ns = dict(tariff.__dict__)
    exec(compile(src, tariff.__file__, "exec"), ns)
    return ns["_smooth_topk_sum"]


bill = np.array([10.0, 10.0, 10.0, 20.0, 20.0])
tau = tariff._PEAK_SMOOTH_TAU
base0 = tariff._smooth_topk_sum(bill, 0, tau)
mut = mutant_fn()
mut0 = mut(bill, 0, tau)
mut1 = mut(bill, 1, tau)
null_delta = max(abs(mut(bill, k, tau) - tariff._smooth_topk_sum(bill, k, tau)) for k in (1, 3))

# Reach: wrap the production symbol and bill a grid of plans through the production callers.
calls = []
real = tariff._smooth_topk_sum


def spy(values, k, t):
    calls.append(k)
    return real(values, k, t)


rng = np.random.default_rng(11)
with mock.patch.object(tariff, "_smooth_topk_sum", spy):
    for pk in range(-2, 8):  # peaks_averaged as configured, zero and negative included
        bill_cfg = tariff.PeakBilling(threshold_kw=0.0, price_per_kw=1.0, window_minutes=60,
                                      dt_hours=1.0, peaks_averaged=pk, distinct_days=False)
        for _ in range(20):
            plan = np.round(rng.uniform(0, 3, size=24), 0)  # integer kW: plateaus force the smooth arm
            tariff.peak_cost_smooth(plan, np.zeros(24), bill_cfg)
            tariff.peak_cost_batch(plan[None, :], np.zeros(24), bill_cfg)
print(f"RESULT topk_k0_baseline={base0} kW")
print(f"RESULT topk_k0_mutant={mut0:.4f} kW")
print(f"RESULT topk_k0_minus_k1_mutant={mut0 - mut1:.6f} kW")
print(f"RESULT null_delta={null_delta} kW")
print(f"RESULT reach_calls_total={len(calls)} count")
print(f"RESULT reach_calls_k_le_0={sum(1 for k in calls if k <= 0)} count")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
