"""D2-s3 M4: the last metering window of a month never enters that month's billed peaks.

Metric: per month M, the highest billed-equivalent kW that PeakTracker ever
held in ``peaks`` while ``month == M`` (read after every ``_close_window``),
for a month of constant 1.0 kW with a 5.0 kW load only in the month's final
metering window. Count key: value delivered into ``PeakTracker.peaks`` (the
seam ``billed_peak_kw`` and ``coordinator._roll_month``'s book_capacity read).
Also the count of months (of 12 x {15, 60} min windows) whose final window
reached ``peaks``.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D2/s3/month_last_window.py [--perturb]
Expected (baseline 17f1c55fad1b): last_window_reached=0 of 24, max_billed_last_window_spike=1.0 kW (exact).
--perturb: closes the open window before the month-change reset in
``PeakTracker.observe`` (the one-line fix shape) -> 24 of 24, 5.0 kW.
Machine: macOS arm64 audit box B6.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from unittest import mock

sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import tariff as T  # noqa: E402

PERTURB = "--perturb" in sys.argv
TZ = ZoneInfo("Europe/Stockholm")
_orig_observe = T.PeakTracker.observe


def _patched_observe(self, when, kw, tariff, dt_hours=None, measured_house_kw=None):
    if when.strftime("%Y-%m") != self.month and self.month:
        self._close_window(tariff)
    return _orig_observe(self, when, kw, tariff, dt_hours, measured_house_kw)


def run_month(year, month, window):
    tariff = T.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3,
                              window_minutes=window)
    tr = T.PeakTracker()
    seen = {}
    orig_close = T.PeakTracker._close_window

    def spy(self, tf):
        orig_close(self, tf)
        if self.peaks:
            seen[self.month] = max(seen.get(self.month, 0.0), max(self.peaks))

    start = datetime(year, month, 1, tzinfo=TZ)
    nm = datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=TZ)
    end_utc = (nm + timedelta(hours=1)).astimezone(timezone.utc)
    last_slot = nm.astimezone(timezone.utc) - timedelta(minutes=window)
    t = start.astimezone(timezone.utc)
    with mock.patch.object(T.PeakTracker, "_close_window", spy):
        while t < end_utc:
            kw = 5.0 if last_slot <= t < nm.astimezone(timezone.utc) else 1.0
            tr.observe(t.astimezone(TZ), kw, tariff)
            t += timedelta(minutes=5)
    return seen.get(start.strftime("%Y-%m"), 0.0)


def main():
    ctx = mock.patch.object(T.PeakTracker, "observe", _patched_observe) if PERTURB else mock.MagicMock()
    c0, t0 = time.process_time(), time.thread_time()
    with ctx:
        vals = [run_month(2026, m, w) for w in (15, 60) for m in range(1, 13)]
    reached = sum(1 for v in vals if abs(v - 5.0) < 1e-9)
    print(f"RESULT last_window_reached={reached} of {len(vals)}")
    print(f"RESULT max_billed_last_window_spike={max(vals):.3f} kW")
    print(f"RESULT min_billed_last_window_spike={min(vals):.3f} kW")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
