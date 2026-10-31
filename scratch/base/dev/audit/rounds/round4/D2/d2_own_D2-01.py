"""VERIFIER-OWN harness for round-4 D2-01 (seat D2-1, refute-first).

Independent of the finder's peak_topk_bracket.py: it drives
tariff._smooth_topk_sum DIRECTLY (bypassing peak_cost / metering_windows
entirely), cross-checks the production number against a closed form derived
from the bracket-exit hypothesis, and re-measures the ratio on plateau
plans that are NOT perfectly flat (jitter inside _PEAK_TIE_BAND, and a
plateau covering only 40 of 96 windows) to attack "a perfectly flat plan
is an unphysical corner".

METRIC (one line):
  own_multiplier_direct = _smooth_topk_sum(x, k, tau) / (k * peak) on a flat
  96-window plateau at 12 kW (contract: the docstring says the smooth sum
  "stays k x tie_level", so this must be 1.0 + float noise);
  own_ratio_jittered    = peak_cost(...) / (marginal * exact top-k of the
  SAME jittered array) for a plateau with +-5e-4 kW noise (inside the 1e-3
  _PEAK_TIE_BAND, so production still takes the smooth branch);
  own_ratio_partial40   = the same when only 40 of 96 windows sit at the peak;
  own_closedform_maxrel = max over a 28-cell grid of the relative deviation
  of the production smooth sum from (n/k)*sigmoid(-1/scale)*peak -- the value
  the bracket-exit hypothesis predicts (bisection parked at the bracket end).

EXACT COMMAND (from a tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D2/d2_own_D2-01.py

EXPECTED (baseline 7dd68dd; all counts/ratios, tolerance 1e-6 rel):
  own_multiplier_direct   ~ 5.08       (96 windows, k=3, 12 kW flat)
  own_multiplier_6kw      ~ 1.102
  own_ratio_jittered      ~ 5.08       (noise does not repair it)
  own_ratio_partial40     >  2         (a 40-window plateau, not all 96)
  own_closedform_maxrel   <  1e-9      (mechanism confirmed: bracket exit)
  own_cells_root_outside  = cells where peak + scale*ln((n-k)/k) > peak + 1
  own_phantom_sek_ellevio_12kw ~ 3982

INSTRUMENTED SYMBOLS: tariff.py:_smooth_topk_sum (driven directly),
tariff.py:peak_cost (jittered/partial plateaus), grid_fee.py:apply_catalog.
PERTURBATION (executed in-section 5): widen the bracket by 40*scale in a
local re-implementation; own_perturbed_multiplier must fall to 1.0.
NULL CONTROL: at 5 kW the root is inside the bracket and the multiplier
must be 1.0 (own_multiplier_5kw).

ROOT RULE: os.getcwd(). BASELINE SHA: 7dd68dd (finder baseline); measured on
branch head 0855277 whose custom_components/ diff vs 7dd68dd is version
strings only. MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11.5.
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools", "audit", "round4", "D2"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np  # noqa: E402  (after the pin, deliberately)

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import grid_fee, tariff  # noqa: E402

CPU = Cpu()
K = 3
TAU = tariff._PEAK_SMOOTH_TAU


def closed_form(x: np.ndarray, k: int) -> float:
    """What the smooth sum MUST be if the bisection parks at hi = peak+1:
    every window keeps weight sigmoid(-1/scale), so the sum is
    n * sigmoid((peak - (peak+1))/scale) * peak = n*sigmoid(-1/scale)*peak."""
    peak = float(np.max(x))
    n = x.size
    scale = TAU * peak
    return n * (1.0 / (1.0 + np.exp(1.0 / scale))) * peak


# --- 1. direct drive of _smooth_topk_sum, no peak_cost plumbing -------------
for tag, e in (("5kw", 5.0), ("6kw", 6.0), ("9kw", 9.0), ("12kw", 12.0)):
    x = np.full(96, e)
    with CPU:
        smooth = tariff._smooth_topk_sum(x, K, TAU)
    result(f"own_multiplier_{tag}", smooth / (K * e), "ratio")
    result(f"own_closedform_{tag}",
           abs(smooth - closed_form(x, K)) / max(smooth, 1e-9), "rel")

# --- 2. the bracket-exit proof over the finder's grid ------------------------
GRID_N = (24, 48, 96, 192)
GRID_E = (2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0)
outside = 0
worst_rel_out = 0.0
over_1pc = 0
cells = 0
for n in GRID_N:
    for e in GRID_E:
        x = np.full(n, e)
        scale = TAU * e
        root = e + scale * np.log((n - K) / K)
        with CPU:
            smooth = tariff._smooth_topk_sum(x, K, TAU)
        mult = smooth / (K * e)
        if mult > 1.01:
            over_1pc += 1
        if root > e + 1.0:
            outside += 1
            worst_rel_out = max(
                worst_rel_out,
                abs(smooth - closed_form(x, K)) / max(smooth, 1e-9))
        cells += 1
result("own_cells", cells, "count")
result("own_cells_root_outside_bracket", outside, "count")
result("own_cells_multiplier_over_1pc", over_1pc, "count")
result("own_closedform_maxrel_outside_cells", worst_rel_out, "rel")

# --- 3. jittered and partial plateaus through the real peak_cost ------------
rng = np.random.default_rng(20260912)
MARGINAL = 45.0 / K


def ratio_of(x_windows: np.ndarray) -> float:
    steps = np.repeat(x_windows, 1)          # 15-min windows, dt 0.25 h
    exact_topk = float(np.sum(np.sort(x_windows)[-K:]))
    with CPU:
        got = tariff.peak_cost(
            steps, np.zeros(steps.size), 0.0, MARGINAL, 15, 0.25,
            peaks_averaged=K)
    return got / (MARGINAL * exact_topk)


jit = 12.0 + rng.uniform(-5e-4, 5e-4, 96)    # inside _PEAK_TIE_BAND = 1e-3
result("own_ratio_jittered", ratio_of(jit), "ratio")
n_at_peak = int(np.sum(jit >= np.max(jit) - tariff._PEAK_TIE_BAND))
result("own_jitter_n_at_peak", n_at_peak, "count")

part = rng.uniform(0.5, 2.0, 96)             # noise floor elsewhere
part[:40] = 12.0 + rng.uniform(-5e-4, 5e-4, 40)   # a 40-window plateau
result("own_ratio_partial40", ratio_of(part), "ratio")
n_at_peak40 = int(np.sum(part >= np.max(part) - tariff._PEAK_TIE_BAND))
result("own_partial40_n_at_peak", n_at_peak40, "count")

# --- 4. money through the Ellevio row, own arithmetic ------------------------
row = grid_fee.apply_catalog("ellevio_villa_effekt_2026")
marg = float(row["peak_tariff_price_per_kw"]) / int(row["peak_tariff_peaks_averaged"])
x = np.full(96, 12.0)
with CPU:
    charged = tariff.peak_cost(x, np.zeros(96), 0.0, marg, 15, 0.25,
                               peaks_averaged=int(row["peak_tariff_peaks_averaged"]))
result("own_charged_sek_ellevio_12kw", charged, "SEK")
result("own_billed_sek_ellevio_12kw", marg * 3 * 12.0, "SEK")
result("own_phantom_sek_ellevio_12kw",
       charged - marg * 3 * 12.0, "SEK")

# --- 5. perturbation: the SAME bisection with the bracket widened ------------
def smooth_topk_wide(values_in, k, tau):
    x = np.asarray(values_in, dtype=float)
    if x.size == 0 or k <= 0:
        return 0.0
    k = max(1, min(int(k), x.size))
    if not np.any(x > 0):
        return 0.0
    peak = float(np.max(x))
    scale = max(tau * peak, 1e-9)
    lo, hi = float(np.min(x)) - 1.0 - 40.0 * scale, peak + 1.0 + 40.0 * scale
    mid = 0.5 * (lo + hi)
    for _ in range(64):
        w = 1.0 / (1.0 + np.exp(-np.clip((x - mid) / scale, -60.0, 60.0)))
        count = float(np.sum(w))
        if abs(count - k) < 1e-6:
            break
        if count > k:
            lo = mid
        else:
            hi = mid
        mid = 0.5 * (lo + hi)
    w = 1.0 / (1.0 + np.exp(-np.clip((x - mid) / scale, -60.0, 60.0)))
    return float(np.sum(w * x))


x12 = np.full(96, 12.0)
result("own_perturbed_multiplier_12kw",
       smooth_topk_wide(x12, K, TAU) / (K * 12.0), "ratio")

footer(CPU, "[d]2_own_D2-01")
