"""VERIFIER 3 own harness, D2-01 (independent of the finder's metric).

METRIC (one line): v3_ratio = tariff.peak_cost(production-shaped plan) /
(marginal_price * sum(sort(excess)[-k:])), where the plan is driven the way
production drives it (constant per-step baseline from
coordinator._baseline_house_load, window length from the shipped catalog
rows), plus the closed-form break point the bracket algebra predicts:
root_offset = tau*peak*ln((n-k)/k); the bracket half-width is the constant
1.0, so the analytic break is peak* = 1/(tau*ln((n-k)/k)).

Also attacks:
  - jitter within _PEAK_TIE_BAND (is the flat plateau an np.full artefact?)
  - per-step baseline variation ABOVE the tie band (does a bumpy house load
    dodge the smooth branch?)
  - flat vs spiky at identical billed top-k (does the objective reward the
    spiky profile?)

EXACT COMMAND (from a tree root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/verify03_d2_01.py

ROOT RULE: os.getcwd(). BASELINE SHA of the finding: 7dd68dd; this run is at
the branch head recorded in the report. MACHINE: 8-core Apple M1 audit box.
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

import numpy as np  # noqa: E402

from _d2common import Cpu, footer, result  # noqa: E402
from heatpump_optimizer import grid_fee, tariff  # noqa: E402

CPU = Cpu()
TAU = tariff._PEAK_SMOOTH_TAU
K = 3
PRICE = 45.0
MARGINAL = PRICE / K


def hard_topk(x: np.ndarray, k: int) -> float:
    return float(np.sum(np.sort(x)[-k:]))


def charged(house: np.ndarray, threshold: float, window_minutes: int,
            marginal: float = MARGINAL, k: int = K) -> float:
    with CPU:
        return tariff.peak_cost(
            house, np.zeros(house.size), threshold, marginal,
            window_minutes, 0.25, peaks_averaged=k,
        )


# --- 0. what the shipped catalog actually writes ----------------------------
rows = {}
for name in sorted(grid_fee.SWEDEN_CATALOG):
    row = grid_fee.apply_catalog(name)
    rows[name] = (int(row["peak_tariff_window_minutes"]),
                  int(row["peak_tariff_peaks_averaged"]))
result("v3_catalog_windows_minutes",
       ",".join(f"{n}:{v[0]}" for n, v in rows.items()), "")
result("v3_catalog_all_15min",
       int(all(v[0] == 15 for v in rows.values())), "bool")

# --- 1. closed-form break point (my own derivation) -------------------------
for n in (24, 96, 192):
    analytic = 1.0 / (TAU * float(np.log((n - K) / K)))
    result(f"v3_analytic_break_kw_n{n}", analytic, "kW")

# --- 2. production-shaped drive: constant baseline + saturated plan ---------
# house = p_max * ones + baseline_const; threshold set so excess = target.
N = 96  # 24 h at 15-min steps, the optimizer's horizon at dt=0.25
baseline = np.full(N, 0.5)  # coordinator._baseline_house_load is np.full
for target_excess in (4.0, 6.0, 9.0, 12.0):
    plan = np.full(N, 11.0)          # p_max, saturated
    house = plan + baseline
    threshold = 11.5 - target_excess  # flat excess above the tracker's level
    got = charged(house, threshold, 15)
    exact = MARGINAL * hard_topk(np.maximum(0.0, house - threshold).reshape(
        N // 4, 4).mean(axis=1) if False else np.full(N, target_excess), K)
    result(f"v3_ratio_saturated_{int(target_excess)}kw", got / exact, "ratio")

# --- 3. jitter inside the tie band (np.full artefact attack) ----------------
rng = np.random.default_rng(20260912)
for amp in (5e-4, 9e-4):
    excess = 12.0 + rng.uniform(-amp, amp, N)
    plan = excess - 0.5
    house = plan + baseline
    threshold = 0.0
    got = charged(house, threshold, 15)
    # exact bill on the same jagged windows (windows are single steps here)
    windows = house  # 15-min window == one 15-min step
    exact = MARGINAL * hard_topk(np.maximum(0.0, windows - threshold), K)
    n_at_peak = int(np.sum(
        np.maximum(0.0, windows - threshold)
        >= float(np.max(np.maximum(0.0, windows - threshold)))
        - tariff._PEAK_TIE_BAND))
    result(f"v3_ratio_jitter{amp}", got / exact, "ratio")
    result(f"v3_natpeak_jitter{amp}", n_at_peak, "count")

# --- 4. bumpy per-step baseline (does a real varying load dodge it?) --------
# household electricity that varies per 15-min step by ~0.4 kW around 0.5
bumpy = 0.5 + rng.uniform(-0.2, 0.2, N)
plan = np.full(N, 11.0)
house = plan + bumpy
threshold = 3.0
got = charged(house, threshold, 15)
excess = np.maximum(0.0, house - threshold)
n_at_peak = int(np.sum(excess >= float(np.max(excess))
                       - tariff._PEAK_TIE_BAND))
exact = MARGINAL * hard_topk(excess, K)
result("v3_ratio_bumpy_baseline", got / exact, "ratio")
result("v3_natpeak_bumpy", n_at_peak, "count")

# --- 5. flat vs spiky at the SAME billed top-k (reward inversion) -----------
flat = np.full(N, 12.0)
spiky = np.full(N, 11.0)
spiky[:K] = 12.0                      # identical top-3 sum = 36 kW
cost_flat = charged(flat, 0.0, 15)
cost_spiky = charged(spiky, 0.0, 15)
result("v3_cost_flat_sek", cost_flat, "SEK")
result("v3_cost_spiky_sek", cost_spiky, "SEK")
result("v3_flat_over_spiky", cost_flat / cost_spiky, "ratio")

# --- 6. the real perturbation, applied to the module in-process -------------
src_hold = tariff._smooth_topk_sum


def wide(values, k, tau):
    x = np.asarray(values, dtype=float)
    if x.size == 0 or k <= 0:
        return 0.0
    k = max(1, min(int(k), x.size))
    if not np.any(x > 0):
        return 0.0
    peak = float(np.max(x))
    scale = max(tau * peak, 1e-9)
    lo = float(np.min(x)) - 1.0 - 40.0 * scale
    hi = peak + 1.0 + 40.0 * scale
    mid = 0.5 * (lo + hi)
    for _ in range(64):
        z = np.clip((x - mid) / scale, -60.0, 60.0)
        w = 1.0 / (1.0 + np.exp(-z))
        count = float(np.sum(w))
        if abs(count - k) < 1e-6:
            break
        if count > k:
            lo = mid
        else:
            hi = mid
        mid = 0.5 * (lo + hi)
    z = np.clip((x - mid) / scale, -60.0, 60.0)
    w = 1.0 / (1.0 + np.exp(-z))
    return float(np.sum(w * x))


tariff._smooth_topk_sum = wide
try:
    plan = np.full(N, 11.0)
    house = plan + baseline
    got = charged(house, 11.5 - 12.0, 15)
    exact = MARGINAL * hard_topk(np.full(N, 12.0), K)
    result("v3_ratio_saturated_12kw_widebracket", got / exact, "ratio")
finally:
    tariff._smooth_topk_sum = src_hold

footer(CPU, "[v]erify03_d2_01")
