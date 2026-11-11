"""R10-TARIFF (#2230): does a month's last metering window reach the month's BILL?

D2-s3-01's harness (``dev/audit/rounds/round10/D2/s3/month_last_window.py``)
reads ``PeakTracker.peaks`` through a spy on ``_close_window``. That is the
period aggregate; the bill is what the coordinator books into the ledger.
This drives the real coordinator: a meter fold every 5 minutes through
``PeakTracker.observe`` and a settlement (``_roll_month``) every 15, over a
month of a constant 1.0 kW house with a 5.0 kW load in the month's final
metering window only, then reads the closed month's frozen receipt.

Metric: the closed month's receipt ``capacity_peak_kw`` (k = 1, so it is the
single billed peak). 5.0 means the last window reached the bill, 1.0 that it
did not. Counted over 12 months x {15, 60}-minute windows.

    PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_month_last_window_billed.py [--null]

``--null``: the spike moves one window earlier (the month's second-to-last
window), which every tree bills -- the control that a 1.0 reading is the
last-window defect and not a harness that cannot see a spike at all.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from harness import FakeEntry, FakeHass

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

TZ = ZoneInfo("Europe/Stockholm")
NULL = "--null" in sys.argv


def run_month(year: int, month: int, window: int) -> float:
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home",
        "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 50.0,
        "peak_tariff_peaks_averaged": 1, "peak_tariff_window_minutes": window,
    }))
    tariff = coord._capacity_tariff()
    start = datetime(year, month, 1, tzinfo=TZ).astimezone(timezone.utc)
    nxt = datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=TZ)
    end = nxt.astimezone(timezone.utc)
    spike_at = end - timedelta(minutes=window * (2 if NULL else 1))
    t, interval_start = start, None
    while t < end + timedelta(hours=1):
        kw = 5.0 if spike_at <= t < spike_at + timedelta(minutes=window) else 1.0
        if t.minute % 15 == 0:
            # A cycle settles the interval that STARTED at the previous
            # cycle (pending["when"]) before it folds its own sample, the
            # order _async_update_data runs _record_accuracy and
            # _track_realised_peak in.
            if interval_start is not None:
                coord._roll_month(interval_start.astimezone(TZ))
            interval_start = t
        coord._peak_tracker.observe(t.astimezone(TZ), kw, tariff)
        t += timedelta(minutes=5)
    receipt = coord._month_reports.get(f"{year}-{month:02d}", {})
    return float(receipt.get("capacity_peak_kw") or 0.0)


def main() -> None:
    vals = [run_month(2026, m, w) for w in (15, 60) for m in range(1, 13)]
    reached = sum(1 for v in vals if abs(v - 5.0) < 1e-9)
    print(f"RESULT arm={'null' if NULL else 'last_window'}")
    print(f"RESULT billed_spike_reached={reached} of {len(vals)}")
    print(f"RESULT min_billed_kw={min(vals):.3f} max_billed_kw={max(vals):.3f}")


if __name__ == "__main__":
    main()
