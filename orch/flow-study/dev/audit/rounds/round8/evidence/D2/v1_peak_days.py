"""D2-v1 (verifier) harness for D2-s2-01: what the per-window tracker hides from the planner.

Metric (one line): per month, the SEK the distinct-day bill (mean of top-k DAILY maxima x price,
the catalog row's quoted rule) rises by across hours that PeakTracker.threshold_kw, read just
before each hour, prices as free (hour kW <= threshold) while the same threshold rule applied
to per-day maxima (k-th highest day max; lowest seen before k days) does not; summed over the month, median and
range over 20 seeded months.  Also: count of such hours, and final billed_peak_kw error.
Differs from the finder's metric (end-of-month billed error): this counts the solver-facing
signal, hour by hour, as the month unfolds.
Instrumented: tariff.PeakTracker.observe / threshold_kw / billed_peak_kw, catalog row
goteborg_energi_effekt_2026 via grid_fee.SWEDEN_CATALOG.
Perturbation (--k1): peaks_averaged 3 -> 1; the hidden SEK must go to 0.
Null (--no-snaps): months with no multi-hour cold-snap plateaus (one high hour per day).
Load model: hourly, morning/evening bumps, 15 % of days a 3-4 h cold-snap plateau.

Command: OMP_NUM_THREADS=1 ... PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/v1_peak_days.py [--k1] [--no-snaps]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, ".")
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import tariff as T  # noqa: E402
from custom_components.heatpump_optimizer import grid_fee as G  # noqa: E402

K1 = "--k1" in sys.argv
NOSNAP = "--no-snaps" in sys.argv
TZ = ZoneInfo("Europe/Stockholm")


def tariff():
    row = G.SWEDEN_CATALOG["goteborg_energi_effekt_2026"]
    return T.CapacityTariff(enabled=True, price_per_kw=float(row["peak_tariff_price_per_kw"]),
                            peaks_averaged=1 if K1 else int(row["peak_tariff_peaks_averaged"]),
                            window_minutes=60, peak_hours=(), weekdays_only=False,
                            offpeak_factor=1.0)


def day_bill(daymax, k, price):
    top = sorted(daymax.values(), reverse=True)[:k]
    return price * sum(top) / k if top else 0.0  # the bill divides by k (month partially filled)


def month(seed, tf):
    rng = np.random.default_rng(1000 + seed)
    k, price = tf.peaks_averaged, tf.price_per_kw
    start = datetime(2026, 1, 1, tzinfo=TZ)
    tr = T.PeakTracker()
    daymax = {}
    hidden_sek, hidden_hours = 0.0, 0
    for d in range(31):
        lvl = rng.uniform(4.0, 7.0)
        day = [2.5 + rng.uniform(0, 0.5) for _ in range(24)]
        day[7] = lvl
        day[18] = lvl * rng.uniform(0.85, 1.05)
        if not NOSNAP and rng.random() < 0.15:
            hi = rng.uniform(7.5, 10.0)
            for h in (5, 6, 7, 8):
                day[h] = hi * rng.uniform(0.95, 1.0)
        for h, kw in enumerate(day):
            when = start + timedelta(days=d, hours=h)
            thr = tr.threshold_kw(tf)  # what the solver/guard is told right now
            before = day_bill(daymax, k, price)
            nd = dict(daymax)
            nd[d] = max(nd.get(d, 0.0), kw)
            after = day_bill(nd, k, price)
            vals = sorted(daymax.values(), reverse=True)
            true_thr = (float("inf") if not vals else vals[k - 1] if len(vals) >= k else vals[-1])
            if true_thr < kw <= thr and after - before > 1e-9:
                hidden_sek += after - before
                hidden_hours += 1
            daymax = nd
            tr.observe(when, kw, tf)
            tr.observe(when + timedelta(minutes=30), kw, tf)
    tr.observe(start + timedelta(days=31) - timedelta(minutes=1), 0.0, tf)  # still January; closes last hour
    err = (tr.billed_peak_kw(tf) - sum(sorted(daymax.values(), reverse=True)[:k]) / k) * price
    return hidden_sek, hidden_hours, err


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    tf = tariff()
    rows = [month(s, tf) for s in range(20)]
    h = np.array([r[0] for r in rows]); n = np.array([r[1] for r in rows]); e = np.array([r[2] for r in rows])
    for i, r in enumerate(rows):
        print(f"cell seed={i} hidden_sek={r[0]:.3f} hidden_hours={r[1]} billed_err_sek={r[2]:.3f}")
    print(f"RESULT hidden_sek_median={np.median(h):.3f} SEK/month")
    print(f"RESULT hidden_sek_min={h.min():.3f} SEK/month")
    print(f"RESULT hidden_sek_max={h.max():.3f} SEK/month")
    print(f"RESULT hidden_sek_mean_drop_max={np.delete(h, int(np.argmax(h))).mean():.3f} SEK/month")
    print(f"RESULT months_with_hidden={int((h > 1e-9).sum())} of {h.size}")
    print(f"RESULT hidden_hours_median={np.median(n):.1f} count")
    print(f"RESULT billed_err_median={np.median(e):.3f} SEK/month")
    print(f"RESULT billed_err_max={e.max():.3f} SEK/month")
    print(f"RESULT billed_err_min={e.min():.3f} SEK/month")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = 'n/a'
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
