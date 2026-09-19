"""D2 round-5 harness 4: the monthly capacity tariff counted exactly once.

METRIC DEFINITIONS
------------------
* ``billed_err`` — |``PeakTracker.billed_peak_kw(tariff)`` - the mean of the
  top-``k`` 60-minute box means of the whole-house power series that was
  fed in|, kW.  The bill is ``full_price x mean(top-k hourly means)``, so the
  tracker's published peak must be that number exactly; the tolerance is
  1e-9 kW.
* ``windows_counted_err`` — (number of window closes) - (number of distinct
  metering windows the sample instants span), count.  "Charging the monthly
  peak exactly once" is this: no window may be closed twice, and none may be
  dropped.
* ``threshold_err`` — |``threshold_kw`` - the k-th largest billed-equivalent
  window mean|, kW, at full history.
* ``repeat_hour_err`` — with window_minutes=60 across the autumn fold, the
  number of *distinct* window keys the two passes of the repeated wall hour
  produce, minus 2 (they are two different metered hours and must not share
  an accumulator).
* ``factor_err`` — billed_peak_kw under a #13 mask vs the mean of the top-k
  of (window mean x window factor), kW.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/metering.py

Expected: every ``*_err`` at or below 1e-9 (counts exact).  Baseline
eaa2a06af16a1b5b006f58a0f36cc92131f80225.  Machine: darwin arm64, 8-core M1,
8 GB.  ROOT RULE: root from ``__file__`` (four parents up).
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "custom_components"))
sys.path.insert(0, str(ROOT / "tests"))

from heatpump_optimizer import tariff as T  # noqa: E402
from heatpump_optimizer.dhw_schedule import Window  # noqa: E402


def emit(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def feed(tracker, tariff, start, samples, dt_hours=0.25):
    closes = []
    prev = tracker._window_key
    for i, p in enumerate(samples):
        tracker.observe(start + timedelta(hours=i * dt_hours), float(p), tariff,
                        dt_hours=dt_hours)
        if tracker._window_key != prev:
            closes.append(tracker._window_key)
            prev = tracker._window_key
    return closes


def monthly():
    rng = np.random.default_rng(29)
    tariff = T.CapacityTariff(enabled=True, price_per_kw=60.0, peaks_averaged=3,
                              window_minutes=60)
    worst = 0.0
    worst_where = "-"
    cnt_err = 0
    for trial in range(6):
        start = datetime(2026, 1, 1) + timedelta(days=3 * trial)
        samples = np.abs(rng.normal(3.0, 2.0, 24 * 4 * 7))  # 7 days of 15-min
        tracker = T.PeakTracker()
        closes = feed(tracker, tariff, start, samples)
        hourly = samples.reshape(-1, 4).mean(axis=1)
        want = float(np.mean(np.sort(hourly)[-3:]))
        got = tracker.billed_peak_kw(tariff)
        err = abs(got - want)
        if err > worst:
            worst = err
            worst_where = f"trial{trial}"
        distinct = len({k for k in closes if k})
        if distinct != hourly.size:
            cnt_err += 1
        emit(f"billed_kw_t{trial}", float(got), "kW")
        emit(f"billed_want_t{trial}", float(want), "kW")
        emit(f"distinct_windows_t{trial}", distinct, "count")
        emit(f"expected_windows_t{trial}", int(hourly.size), "count")
        thr = tracker.threshold_kw(tariff)
        want_thr = float(np.sort(hourly)[-3])
        emit(f"threshold_err_t{trial}", float(abs(thr - want_thr)), "kW")
    emit("billed_cells", 6, "count")
    emit("billed_max_err", float(worst), "kW")
    emit("billed_worst_cell", worst_where, "label")
    emit("windows_counted_mismatches", cnt_err, "count")

    # masked month: outside the mask a window contributes nothing at all
    masked = T.CapacityTariff(
        enabled=True, price_per_kw=60.0, peaks_averaged=3, window_minutes=60,
        months=frozenset({1}),
    )
    start = datetime(2026, 2, 1)
    samples = np.abs(rng.normal(4.0, 2.0, 24 * 4 * 3))
    tr = T.PeakTracker()
    feed(tr, masked, start, samples)
    emit("masked_month_peaks", len(tr.peaks), "count")
    emit("masked_month_billed", float(tr.billed_peak_kw(masked)), "kW")

    # factor mask: half-rate window next to full-rate ones
    fac = T.CapacityTariff(
        enabled=True, price_per_kw=60.0, peaks_averaged=3, window_minutes=60,
        peak_hours=((6.0, 22.0),), offpeak_factor=0.5,
    )
    start = datetime(2026, 1, 5)
    samples = np.abs(rng.normal(5.0, 2.0, 24 * 4))
    tr = T.PeakTracker()
    feed(tr, fac, start, samples)
    hourly = samples.reshape(-1, 4).mean(axis=1)
    factors = np.array([
        fac.sample_factor(start + timedelta(hours=h)) for h in range(hourly.size)
    ])
    want = float(np.mean(np.sort(hourly * factors)[-3:]))
    emit("factor_err", float(abs(tr.billed_peak_kw(fac) - want)), "kW")
    emit("factor_half_windows",
         int(np.sum(factors == 0.5)), "count")


def fold():
    """The autumn fold: two real passes of the repeated hour, one accumulator.

    The instants are built in UTC and converted to the zone -- adding a
    ``timedelta`` to an aware datetime advances the WALL clock and re-derives
    the offset with ``fold=0``, so a wall-clock walk never enters the second
    pass of the repeated hour and cannot test this at all.
    """
    from zoneinfo import ZoneInfo

    stockholm = ZoneInfo("Europe/Stockholm")
    tariff = T.CapacityTariff(enabled=True, price_per_kw=60.0,
                              peaks_averaged=3, window_minutes=60)
    tr = T.PeakTracker()
    # Europe/Stockholm leaves CEST (+02:00) on 2026-10-25: 03:00 local becomes
    # 02:00.  Walk 4 real hours from 00:00 local in UTC.
    base_utc = datetime(2026, 10, 24, 22, 0, tzinfo=timezone.utc)
    keys = []
    for i in range(16):
        when = (base_utc + timedelta(minutes=15 * i)).astimezone(stockholm)
        tr.observe(when, 2.0, tariff, dt_hours=0.25)
        keys.append((tr._window_key, when.replace(tzinfo=None), when.fold))
    seen = {}
    for k, wall, fo in keys:
        seen.setdefault(k, (wall, fo))
    emit("fold_distinct_keys", len(seen), "count")
    emit("fold_repeated_wall_hours",
         sum(1 for wall, fo in seen.values() if fo == 1), "count")
    emit("fold_wall_hours_seen", len({wall for wall, _ in seen.values()}), "count")
    emit("fold_acc_before", float(tr.billed_peak_kw(tariff)), "kW")


def main():
    t0 = time.monotonic()
    for fn in (monthly, fold):
        try:
            fn()
        except Exception as err:
            emit(f"ERROR_{fn.__name__}", f"{type(err).__name__}:{err}", "label")
    import resource

    thread_cpu = time.thread_time()
    process_cpu = time.process_time()
    emit("process_cpu", f"{process_cpu:.3f}", "s")
    emit("thread_cpu", f"{thread_cpu:.3f}", "s")
    emit("thread_factor", f"{process_cpu / max(thread_cpu, 1e-9):.4f}", "ratio")
    try:
        emit("load1", f"{os.getloadavg()[0]:.2f}", "count")
    except OSError:
        emit("load1", "n/a", "count")
    emit("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_majflt, "count")
    emit("wall", f"{time.monotonic() - t0:.2f}", "s")


if __name__ == "__main__":
    main()
