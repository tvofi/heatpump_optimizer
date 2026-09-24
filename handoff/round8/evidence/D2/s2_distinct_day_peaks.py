"""D2-s2 harness: capacity-tariff peaks counted per window, not per day.

Metric: SEK/month the tracker's billed_peak_kw x price_per_kw differs from the
DSO bill for the catalog rows' own rule ("the k highest peaks, on k different
days"), i.e. price * (tracker billed kW - mean of top-k DAILY maxima); plus the
"free" hour the tracker's threshold admits that the bill charges for.
Count key: the value tariff.PeakTracker.billed_peak_kw / threshold_kw deliver
(production seam), compared with the per-day reference computed here from the
same observed windows. Plan side: tariff.peak_cost on a 24 h plan with k tied
high windows on one day vs the distinct-day marginal (price/k per day).

Command (repo root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s2_distinct_day_peaks.py [--k1]
  --k1  perturbation/null control: peaks_averaged=1 (top-1 window == top-1 day),
        every error must go to zero.
Expected (baseline, Goteborg row 49 SEK/kW, k=3): headline_overbill_sek=
  (10+9.8+9.6)/3-(10+7+6.5)/3 = 1.9667 kW * 49 = 96.37 SEK (exact, deterministic);
  free_hour_true_cost_sek = 49/3*(9.0-6.5)= 40.83 SEK; plan_overcharge_ratio=3.0.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, ".")
import numpy as np
from custom_components.heatpump_optimizer import tariff as T
from custom_components.heatpump_optimizer import grid_fee as G

K1 = "--k1" in sys.argv
TZ = ZoneInfo("Europe/Stockholm")
t0p, t0t = time.process_time(), time.thread_time()


def catalog_tariff(product):
    row = G.SWEDEN_CATALOG[product]
    hours = ()
    if row["peak_tariff_hours"] and row["peak_tariff_offpeak_factor"] < 1.0:
        from custom_components.heatpump_optimizer.dhw_schedule import parse_windows
        hours = tuple(parse_windows(row["peak_tariff_hours"]))
    return T.CapacityTariff(
        enabled=True, price_per_kw=float(row["peak_tariff_price_per_kw"]),
        peaks_averaged=1 if K1 else int(row["peak_tariff_peaks_averaged"]),
        window_minutes=int(row["peak_tariff_window_minutes"]),
        peak_hours=hours, weekdays_only=bool(row["peak_tariff_weekdays_only"]),
        offpeak_factor=float(row["peak_tariff_offpeak_factor"]))


def run_month(hourly, tariff, start):
    """Feed hourly kW (list of per-day 24-lists) through PeakTracker.observe at
    two samples per window (the 30-min tick). Returns tracker and the per-day
    billed-equivalent maxima the DSO rule bills."""
    tr = T.PeakTracker()
    day_max = {}
    for d, day in enumerate(hourly):
        for h, kw in enumerate(day):
            for m in (0, 30):
                when = (start + timedelta(days=d)).replace(hour=h, minute=m)
                tr.observe(when, kw, tariff)
            f = tariff.sample_factor((start + timedelta(days=d)).replace(hour=h))
            if f > 0:
                day_max[d] = max(day_max.get(d, 0.0), kw * f)
    # close the last window
    tr.observe(start + timedelta(days=len(hourly)), 0.0, tariff)  # same month (<=30 days from the 1st)
    return tr, day_max


def true_billed(day_max, k):
    top = sorted(day_max.values(), reverse=True)[:k]
    return sum(top) / len(top)


def true_threshold(day_max, k):
    top = sorted(day_max.values(), reverse=True)
    return top[k - 1] if len(top) >= k else (top[-1] if top else float("inf"))


start = datetime(2026, 10, 1, tzinfo=TZ)
tariff = catalog_tariff("goteborg_energi_effekt_2026")
k = tariff.peaks_averaged
price = tariff.price_per_kw

# Headline scenario: a 10-day month-start. Day 2 is a cold morning with three
# consecutive high hours (10, 9.8, 9.6 kW); the other days peak at 7, 6.5, ...
base = [3.0] * 24
days = []
peaks = [5.0, 5.5, None, 7.0, 6.5, 6.0, 5.8, 5.2, 4.9, 6.2]
for p in peaks:
    d = list(base)
    if p is None:
        d[6], d[7], d[8] = 10.0, 9.8, 9.6
    else:
        d[18] = p
    days.append(d)
tr, dmax = run_month(days, tariff, start)
billed = tr.billed_peak_kw(tariff)
truth = true_billed(dmax, k)
thr = tr.threshold_kw(tariff)
tthr = true_threshold(dmax, k)
print(f"# tracker peaks {tr.peaks[:6]}  day maxima {sorted(dmax.values(), reverse=True)[:4]}")
print(f"RESULT tracker_billed_peak_kw={billed:.4f} kW")
print(f"RESULT true_billed_peak_kw={truth:.4f} kW")
print(f"RESULT headline_overbill_sek={(billed - truth) * price:.4f} SEK/month")
print(f"RESULT tracker_threshold_kw={thr:.4f} kW")
print(f"RESULT true_threshold_kw={tthr:.4f} kW")
# A 9.0 kW hour on a new day: tracker says it displaces nothing (free).
new_kw = 9.0
tracker_marginal = max(0.0, new_kw - thr) * price / k
true_marginal = max(0.0, new_kw - tthr) * price / k
print(f"RESULT free_hour_tracker_cost_sek={tracker_marginal:.4f} SEK")
print(f"RESULT free_hour_true_cost_sek={true_marginal:.4f} SEK")

# Grid of cells: random 30-day months, hourly house load with morning and
# evening bumps and occasional multi-hour cold-snap plateaus.
cells = []
for seed in range(8):
    rng = np.random.default_rng(seed)
    days = []
    for d in range(30):
        lvl = rng.uniform(4.0, 7.0)
        day = [2.5 + rng.uniform(0, 0.5) for _ in range(24)]
        day[7] = lvl
        day[18] = lvl * rng.uniform(0.85, 1.05)
        if rng.random() < 0.15:  # cold snap: several near-equal high hours
            hi = rng.uniform(7.5, 10.0)
            for h in (5, 6, 7, 8):
                day[h] = hi * rng.uniform(0.95, 1.0)
        days.append(day)
    tr, dmax = run_month(days, tariff, start)
    err = (tr.billed_peak_kw(tariff) - true_billed(dmax, k)) * price
    cells.append(err)
    print(f"# cell seed={seed} overbill_sek={err:.3f} thr_err_kw={tr.threshold_kw(tariff) - true_threshold(dmax, k):.3f}")
cells = np.array(cells)
fav = cells.max()
loo = np.delete(cells, int(np.argmax(cells)))
print(f"RESULT grid_cells={cells.size} count")
print(f"RESULT grid_overbill_min_sek={cells.min():.3f} SEK/month")
print(f"RESULT grid_overbill_max_sek={cells.max():.3f} SEK/month")
print(f"RESULT grid_overbill_mean_sek={cells.mean():.3f} SEK/month")
print(f"RESULT grid_overbill_mean_drop_max_sek={loo.mean():.3f} SEK/month")
print(f"RESULT grid_cells_nonzero={int(np.sum(cells > 1e-9))} count")

# Plan side: a 24 h plan at 15-min steps, threshold 6 kW, k windows tied 1 kW
# above it on the same morning. Distinct-day bill: one peak per day -> price/k.
dt = 0.25
n = 96
power = np.full(n, 1.0)
baseline = np.full(n, 2.0)
for w in range(k):  # k consecutive hourly windows at 7 kW house
    power[28 + 4 * w: 32 + 4 * w] = 5.0
pc = T.peak_cost(power, baseline, 6.0, tariff.marginal_price_per_kw, 60, dt, k)
true_pc = tariff.marginal_price_per_kw * 1.0  # only the day's max counts once
print(f"RESULT plan_peak_cost_sek={pc:.4f} SEK")
print(f"RESULT plan_true_cost_sek={true_pc:.4f} SEK")
print(f"RESULT plan_overcharge_ratio={pc / true_pc:.4f} ratio")

pc_, tc_ = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc_ / max(tc_, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
