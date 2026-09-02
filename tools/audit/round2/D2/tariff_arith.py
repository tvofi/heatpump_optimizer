#!/usr/bin/env python
"""D2 harness -- tariff, grid-fee and price-folding arithmetic.

Metrics (each one line):
  metering_mean_identity: |sum(windows)*per_window - sum(house)| for a horizon that
    starts on a window boundary (box averages conserve energy);
  peak_cost_topk_identity: |peak_cost - marginal*sum(top-k excess)| on constructed plans
    with 1, k and k+2 windows above threshold;
  tracker_month_once: after a month of hourly samples with three spikes, billed_peak_kw
    == mean of the three and threshold_kw == the third (the peak is billed once, not per hour);
  tracker_month_reset: the first sample of a new month clears the peaks;
  grid_fee_*: the Nov-Mar Mon-Fri 06:00-22:00 rule at the month boundary, the weekday
    boundary and the wrapping window;
  price_fold_*: _known_prices_for on hourly and quarter-hour entries, the last entry's span,
    stale (yesterday-only) lists, and naive-vs-aware timestamps;
  pv_blended_identity: blended_block_prices*block*dt == piecewise_cost of the block;
  import_margin_floor: export price above import never makes consumption pay.
Command: PYTHONPATH=tests/hastub python tools/audit/round2/D2/tariff_arith.py
Expected (c398fc84): every identity residual 0 (exact) and every boolean 1.
Perturbation: editing peak_cost to use np.max instead of the top-k sum moves
  peak_cost_topk_identity up on the k-window plan.
Instrumented: tariff:metering_windows, peak_cost, PeakTracker.observe/billed_peak_kw/threshold_kw,
  grid_fee:GridFeeSchedule.fee_vector, coordinator:HeatPumpOptimizerCoordinator._known_prices_for,
  pv:blended_block_prices, piecewise_cost, import_margin.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import resource
import sys
import time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

from harness import FakeEntry, FakeHass
from heatpump_optimizer import pv
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.grid_fee import GridFeeSchedule
from heatpump_optimizer.tariff import CapacityTariff, PeakTracker, metering_windows, peak_cost, realised_peak

# ---- metering windows ----
rng = np.random.default_rng(2)
house = rng.uniform(0, 8, size=96)
w = metering_windows(house, 60, 0.25, 0)
print(f"RESULT metering_mean_identity={abs(float(np.sum(w)) * 4 - float(np.sum(house))):.3e} kW")
w2 = metering_windows(house, 60, 0.25, 2)  # 2 steps to the next boundary
print(f"RESULT metering_offset_windows={w2.size} count (expected 1 + 23 + 1 = 25)")
print(f"RESULT metering_offset_head_mean_identity={abs(float(w2[0]) - float(np.mean(house[:2]))):.3e} kW")

# ---- peak_cost top-k ----
price, thr, k = 20.0, 5.0, 3
res = 0.0
for n_above in (1, 3, 5):
    plan = np.full(96, 3.0)
    for j in range(n_above):
        plan[j * 8: j * 8 + 4] = 5.0 + 2.0 * (j + 1)  # window mean = 3 + (j+1)   (half the window high)
    cost = peak_cost(plan, np.zeros(96), thr, price, 60, 0.25, k)
    wins = metering_windows(plan, 60, 0.25)
    exc = np.sort(np.maximum(0.0, wins - thr))[-k:]
    res = max(res, abs(cost - price * float(np.sum(exc))))
    print(f"CELL peak_cost n_above={n_above}: cost={cost:.3f} top-k sum={price * float(np.sum(exc)):.3f}")
print(f"RESULT peak_cost_topk_identity={res:.3e} SEK")
print(f"RESULT peak_cost_zero_below_threshold={peak_cost(np.full(96, 4.9), np.zeros(96), thr, price, 60, 0.25, k):.3e} SEK")
print(f"RESULT peak_cost_inf_threshold={peak_cost(np.full(96, 9.0), np.zeros(96), float('inf'), price, 60, 0.25, k):.3e} SEK")

# ---- the tracker bills the monthly peak once ----
tariff = CapacityTariff(enabled=True, price_per_kw=60.0, peaks_averaged=3, window_minutes=60)
tr = PeakTracker()
t = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
spikes = {(2026, 1, 5, 7): 9.0, (2026, 1, 12, 18): 8.0, (2026, 1, 20, 8): 7.0}
for h in range(31 * 24):
    when = t + timedelta(hours=h)
    kw = spikes.get((when.year, when.month, when.day, when.hour), 3.0)
    for q in range(4):
        tr.observe(when + timedelta(minutes=15 * q), kw, tariff)
tr.observe(datetime(2026, 2, 1, 0, 0, tzinfo=timezone.utc), 1.0, tariff)  # closes the last January window, resets
billed_before = None
tr2 = PeakTracker()
for h in range(31 * 24):
    when = t + timedelta(hours=h)
    kw = spikes.get((when.year, when.month, when.day, when.hour), 3.0)
    for q in range(4):
        tr2.observe(when + timedelta(minutes=15 * q), kw, tariff)
tr2.observe(t + timedelta(hours=31 * 24), 3.0, tariff)  # Feb 1 00:00 closes the last window of January
# read January's figures from a tracker still in January: replay to Jan 31 23:45 then close by a Jan sample
tr3 = PeakTracker()
for h in range(31 * 24 - 1):
    when = t + timedelta(hours=h)
    kw = spikes.get((when.year, when.month, when.day, when.hour), 3.0)
    for q in range(4):
        tr3.observe(when + timedelta(minutes=15 * q), kw, tariff)
tr3.observe(t + timedelta(hours=31 * 24 - 1), 3.0, tariff)
print(f"CELL tracker January: peaks={tr3.peaks[:4]} billed={tr3.billed_peak_kw(tariff):.3f} threshold={tr3.threshold_kw(tariff):.3f}")
print(f"RESULT tracker_month_once={int(abs(tr3.billed_peak_kw(tariff) - 8.0) < 1e-9 and abs(tr3.threshold_kw(tariff) - 7.0) < 1e-9)} bool")
print(f"RESULT tracker_month_reset={int(tr2.month == '2026-02' and tr2.peaks == [])} bool")
print(f"RESULT tracker_marginal_price={tariff.marginal_price_per_kw:.3f} SEK_per_kW (60/3)")

# ---- grid fee rules ----
sched = GridFeeSchedule.from_config({"grid_fee_mode": "rules", "grid_fee_rules": "Nov-Mar Mon-Fri 06:00-22:00 = 0.25, 22:00-06:00 = 0.05", "grid_fee_fixed": 0.10})
checks = {
    "fri_2145_march": (datetime(2026, 3, 27, 21, 45), 0.35),
    "fri_2200_march": (datetime(2026, 3, 27, 22, 0), 0.15),
    "sat_1200_march": (datetime(2026, 3, 28, 12, 0), 0.10),
    "tue_1200_march31": (datetime(2026, 3, 31, 12, 0), 0.35),
    "wed_1200_april1": (datetime(2026, 4, 1, 12, 0), 0.10),
    "mon_0545_nov": (datetime(2026, 11, 2, 5, 45), 0.15),
    "mon_0600_nov": (datetime(2026, 11, 2, 6, 0), 0.35),
}
bad = 0
for label, (when, want) in checks.items():
    got = sched.current_fee(when)
    if abs(got - want) > 1e-12:
        bad += 1
        print(f"CELL grid_fee {label}: got {got} want {want}")
print(f"RESULT grid_fee_rule_mismatches={bad} count of {len(checks)}")
vec = sched.fee_vector([datetime(2026, 3, 31, 21, 0) + timedelta(minutes=15 * i) for i in range(96)])
print(f"RESULT grid_fee_vector_month_boundary_sum={float(np.sum(vec)) * 0.25:.4f} SEK_per_kW_day")

# ---- price folding into steps ----
cfg = {"tibber_token": "x", "weather_entity": "weather.home"}
coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
mid = datetime(2026, 1, 15, 0, 0)
steps = [mid + timedelta(minutes=15 * i) for i in range(96)]
coord._prices = [{"total": float(h), "starts_at": (mid + timedelta(hours=h)).isoformat()} for h in range(24)]
known = coord._known_prices_for(steps)
print(f"RESULT price_fold_hourly_len={len(known)} count (96 expected)")
print(f"RESULT price_fold_hourly_mismatch={int(sum(1 for i, v in enumerate(known) if v != i // 4))} count")
coord._prices = [{"total": float(q) / 4.0, "starts_at": (mid + timedelta(minutes=15 * q)).isoformat()} for q in range(96)]
known = coord._known_prices_for(steps)
print(f"RESULT price_fold_quarter_len={len(known)} count (96 expected)")
print(f"RESULT price_fold_quarter_mismatch={int(sum(1 for i, v in enumerate(known) if v != i / 4.0))} count")
coord._prices = [{"total": float(h), "starts_at": (mid + timedelta(hours=h)).isoformat()} for h in range(12)]
known = coord._known_prices_for(steps)
print(f"RESULT price_fold_partial_len={len(known)} count (48 expected: 12 hourly entries, last spans 1 h)")
coord._prices = [{"total": float(h), "starts_at": (mid - timedelta(days=1) + timedelta(hours=h)).isoformat()} for h in range(24)]
known = coord._known_prices_for(steps)
print(f"RESULT price_fold_stale_len={len(known)} count (0 expected: yesterday's list covers no step)")
# mixed spacing: an hourly series that switches to quarters at 13:00
coord._prices = ([{"total": float(h), "starts_at": (mid + timedelta(hours=h)).isoformat()} for h in range(13)]
                 + [{"total": 13.0 + q / 4.0, "starts_at": (mid + timedelta(hours=13, minutes=15 * q)).isoformat()} for q in range(44)])
known = coord._known_prices_for(steps)
want = [float(i // 4) if i < 52 else 13.0 + (i - 52) / 4.0 for i in range(96)]
print(f"RESULT price_fold_mixed_mismatch={int(sum(1 for a, b in zip(known, want) if a != b))} count len={len(known)}")

# ---- PV piecewise ----
prices = rng.uniform(0.2, 2.5, size=96)
surplus = rng.uniform(0.0, 3.0, size=96)
block = 2.0
blended = pv.blended_block_prices(prices, surplus, 0.3, block)
res = 0.0
for i in range(96):
    one = np.zeros(96); one[i] = block
    res = max(res, abs(blended[i] * block * 0.25 - pv.piecewise_cost(prices, surplus, 0.3, one, 0.25)))
print(f"RESULT pv_blended_identity={res:.3e} SEK")
m = pv.import_margin(np.array([0.1, 0.5]), 0.4)
print(f"RESULT import_margin_floor={int(m[0] == 0.0 and abs(m[1] - 0.1) < 1e-12)} bool")

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
