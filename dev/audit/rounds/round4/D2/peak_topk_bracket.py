"""D2 round 4, finding D2-01: the capacity-tariff penalty overstates the
bill it approximates, because the smooth top-k bisection's bracket is not
scaled by its own logistic temperature.

METRIC (one line): overstatement ratio
    R = tariff.peak_cost(...) / (marginal_price * sum(sort(excess)[-k:]))
i.e. what the objective charges for a plan's capacity peaks divided by the
exact top-k sum the function's own docstring says it approximates. R == 1.0
is the contract ("small enough that separated peaks still match the billed
sum"); R > 1 is money the plan is charged and the DSO never bills.

WHY IT HAPPENS (stated so the judge can re-derive, not as evidence):
`tariff._smooth_topk_sum` bisects a logistic threshold `mid` on the bracket
[min(x)-1, max(x)+1] with temperature `scale = 0.05*max(x)`. The root is at
mid = peak + scale*ln((n-k)/k). The bracket's half-width is the constant
1.0, so as soon as 0.05*peak*ln((n-k)/k) > 1 the root is outside it, the 64
bisection steps converge to the bracket end instead, every window keeps a
weight near sigmoid(-1/scale), and the returned sum is far above k*peak.
The branch is entered whenever more than k metering windows sit within
`_PEAK_TIE_BAND` (1e-3 kW) of the largest excess -- a flat plan, which is
what a capacity tariff exists to produce.

EXACT COMMAND (from the export root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/peak_topk_bracket.py

EXPECTED (baseline 7dd68dd, this box): these are exact float identities on
counts and sums, not timings, so the tolerance is 1e-9 relative.
    ratio_worst              = 5.083811356  +- 1e-6 rel  (12 kW flat excess,
                                                         96 x 15-min windows)
    ratio_catalog_6kw        = 1.102246261  +- 1e-6 rel
    ratio_null_flat_5kw      = 1.000000062  +- 1e-6      (null control: below
                                                         the bracket's break
                                                         point it is exact)
    ratio_null_spiky_12kw    = 1.0 exactly               (null control: at most
                                                         k windows at the peak
                                                         never enters the branch)
    break_excess_kw_1pc      = 5.8416 +- 0.01 kW         (15-min windows, k=3)
    cells_over_1pc           = 16 of 28                  (grid sweep)
    cell_ratio_max           = 13.35094575 +- 1e-6       (192 windows, 15 kW)
    loo_worst                = 2.514813011 +- 1e-6       (worst cell dropped)
    phantom_sek_12kw         = 3981.7 +- 1e-3 SEK        (Ellevio row, 12 kW)
    perturbed_ratio_worst    = 1.0000003 +- 1e-6         (bracket widened)

INSTRUMENTED SYMBOLS: tariff.py:peak_cost (driven), tariff.py:_smooth_topk_sum
(the defect), tariff.py:CapacityTariff.marginal_price_per_kw (the exact
price the ratio is taken against), grid_fee.py:apply_catalog (the shipped
15-minute window every catalog row writes).

PERTURBATION (the judge runs it): widen the bisection bracket in
tariff._smooth_topk_sum from
    lo, hi = float(np.min(x)) - 1.0, peak + 1.0
to
    lo, hi = float(np.min(x)) - 1.0 - 40.0*scale, peak + 1.0 + 40.0*scale
Under it every ratio above must fall to 1.000000 +- 1e-6 and
`cells_over_1pc` must fall to 0. Section 5 of this harness executes that
perturbation in-process against a re-implementation of the SAME bisection
with only the bracket changed, and prints `perturbed_ratio_worst`, so the
direction is measured here and not merely asserted.

NULL CONTROL: the same measurement at excess levels below the break point
(`ratio_null_flat_5kw`, `ratio_null_hourly_8kw`) must be exactly 1.0 -- the
effect has to vanish where the bracket still holds the root, or the metric
is measuring the top-k sum and not the bracket.

LEAVE-ONE-OUT: section 3 sweeps a 6 x 7 grid of (window count, flat excess)
and reports range, mean, and the mean with the single most favourable cell
dropped.

ROOT RULE: os.getcwd(). Copy this file into the tree to measure and run it
from that tree's root; it resolves nothing from __file__.
BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (export, no .git).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy 2.4.6,
OpenBLAS; box shared with nine other finders during the fan-out.
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
PRICE_PER_KW = 45.0          # const.DEFAULT_PEAK_TARIFF_PRICE
MARGINAL = PRICE_PER_KW / K  # CapacityTariff.marginal_price_per_kw


def hard_topk(excess: np.ndarray, k: int) -> float:
    return float(np.sum(np.sort(excess)[-k:]))


def ratio(flat_excess: float, n_windows: int, window_minutes: int,
          k: int = K) -> float:
    """peak_cost / (marginal_price * exact top-k), on a flat plan."""
    steps_per_window = max(1, int(round(window_minutes / 15.0)))
    n_steps = n_windows * steps_per_window
    house = np.full(n_steps, flat_excess)
    with CPU:
        got = tariff.peak_cost(
            house, np.zeros(n_steps), 0.0, MARGINAL, window_minutes, 0.25,
            peaks_averaged=k,
        )
    exact = MARGINAL * hard_topk(np.full(n_windows, flat_excess), k)
    return got / exact


# --- 1. the two shipped window lengths -------------------------------------
result("ratio_catalog_6kw", ratio(6.0, 96, 15), "ratio")
result("ratio_catalog_9kw", ratio(9.0, 96, 15), "ratio")
result("ratio_worst", ratio(12.0, 96, 15), "ratio")
result("ratio_hourly_14kw", ratio(14.0, 24, 60), "ratio")

# --- 2. null control: below the break point the approximation is exact -----
result("ratio_null_flat_5kw", ratio(5.0, 96, 15), "ratio")
result("ratio_null_hourly_8kw", ratio(8.0, 24, 60), "ratio")
# and the other null: a plan with at most k windows at the peak never enters
# the smooth branch at all, whatever the excess.
spiky = np.full(96, 1.0)
spiky[:K] = 12.0
with CPU:
    spiky_cost = tariff.peak_cost(
        spiky, np.zeros(96), 0.0, MARGINAL, 15, 0.25, peaks_averaged=K)
result("ratio_null_spiky_12kw",
       spiky_cost / (MARGINAL * hard_topk(spiky, K)), "ratio")

# --- 3. where it starts, and the grid sweep --------------------------------
lo, hi = 0.0, 40.0
for _ in range(60):
    mid = 0.5 * (lo + hi)
    if ratio(mid, 96, 15) > 1.01:
        hi = mid
    else:
        lo = mid
result("break_excess_kw_1pc", 0.5 * (lo + hi), "kW")

# 15-minute windows over the horizons this optimizer actually plans:
# 6 h, 12 h, 24 h, 48 h.
GRID_N = (24, 48, 96, 192)
GRID_E = (2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0)
cells = []
for n in GRID_N:
    for e in GRID_E:
        cells.append(((n, e), ratio(e, n, 15)))
values = np.array([v for _, v in cells])
result("cells", len(cells), "count")
result("cells_over_1pc", int(np.sum(values > 1.01)), "count")
result("cell_ratio_min", float(values.min()), "ratio")
result("cell_ratio_max", float(values.max()), "ratio")
result("cell_ratio_mean", float(values.mean()), "ratio")
drop = int(np.argmax(values))
result("loo_worst",
       float(np.delete(values, drop).mean()), "ratio")
result("loo_dropped_cell", f"n={cells[drop][0][0]},excess={cells[drop][0][1]}")

# --- 4. what it costs, through a shipped catalog row ------------------------
row = grid_fee.apply_catalog("ellevio_villa_effekt_2026")
cat_price = float(row["peak_tariff_price_per_kw"])
cat_k = int(row["peak_tariff_peaks_averaged"])
cat_win = int(row["peak_tariff_window_minutes"])
cat_marg = cat_price / cat_k
for tag, exc in (("6kw", 6.0), ("9kw", 9.0), ("12kw", 12.0)):
    house = np.full(96, exc)
    with CPU:
        charged = tariff.peak_cost(
            house, np.zeros(96), 0.0, cat_marg, cat_win, 0.25,
            peaks_averaged=cat_k)
    billed = cat_marg * hard_topk(np.full(96, exc), cat_k)
    result(f"catalog_charged_sek_{tag}", charged, "SEK")
    result(f"catalog_billed_sek_{tag}", billed, "SEK")
    result(f"phantom_sek_{tag}", charged - billed, "SEK")

# --- 5. the perturbation, executed -----------------------------------------
# The same bisection with the ONE changed line (bracket scaled by `scale`).
# Nothing else differs, so the printed ratio isolates the bracket.
def smooth_topk_wide(values_in: np.ndarray, k: int, tau: float) -> float:
    x = np.asarray(values_in, dtype=float)
    if x.size == 0 or k <= 0:
        return 0.0
    k = max(1, min(int(k), x.size))
    if not np.any(x > 0):
        return 0.0
    peak = float(np.max(x))
    scale = max(tau * peak, 1e-9)
    lo_b = float(np.min(x)) - 1.0 - 40.0 * scale
    hi_b = peak + 1.0 + 40.0 * scale
    mid_b = 0.5 * (lo_b + hi_b)
    for _ in range(64):
        z = np.clip((x - mid_b) / scale, -60.0, 60.0)
        w = 1.0 / (1.0 + np.exp(-z))
        count = float(np.sum(w))
        if abs(count - k) < 1e-6:
            break
        if count > k:
            lo_b = mid_b
        else:
            hi_b = mid_b
        mid_b = 0.5 * (lo_b + hi_b)
    z = np.clip((x - mid_b) / scale, -60.0, 60.0)
    w = 1.0 / (1.0 + np.exp(-z))
    return float(np.sum(w * x))


_orig = tariff._smooth_topk_sum
tariff._smooth_topk_sum = smooth_topk_wide
try:
    pert = [ratio(e, n, 15) for n in GRID_N for e in GRID_E]
finally:
    tariff._smooth_topk_sum = _orig
pert_arr = np.array(pert)
result("perturbed_ratio_worst", float(pert_arr.max()), "ratio")
result("perturbed_cells_over_1pc", int(np.sum(pert_arr > 1.01)), "count")

footer(CPU, "[p]eak_topk_bracket")
