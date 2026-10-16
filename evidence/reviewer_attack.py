"""Reviewer's own attack harness for R10-TARIFF (#2230). Not the finder's.

Drives the real coordinator (_roll_month on the previous cycle's start, then
PeakTracker.observe) as r10_month_last_window_billed.py does, over:
  dst   : Stockholm months whose last day is a DST change day (2027-10-31,
          2030-03-31, 2024-03-31, 2026-10-25 is NOT month end -> control)
  k3    : peaks_averaged=3, distinct days, daily peaks + last-window spike
  rst   : restart (JSON round trip of as_dict) at every 5-min step between
          the rollover and the freezing settlement
  empty : a month masked out by peak_tariff_months (no peaks) -> 0 booked,
          and the next month unaffected
"""
import json, sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.tariff import PeakTracker

TZ = ZoneInfo("Europe/Stockholm")


def coord_for(**kw):
    data = {"tibber_token": "x", "weather_entity": "weather.home",
            "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 50.0,
            "peak_tariff_peaks_averaged": 1, "peak_tariff_window_minutes": 60}
    data.update(kw)
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=data))


def drive(coord, year, month, load, restart_step=None, start_days_before=3):
    tariff = coord._capacity_tariff()
    nxt = datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=TZ)
    end = nxt.astimezone(timezone.utc)
    t = end - timedelta(days=start_days_before)
    interval_start, step = None, 0
    while t < end + timedelta(hours=2):
        if t.minute % 15 == 0:
            if interval_start is not None:
                coord._roll_month(interval_start.astimezone(TZ))
            interval_start = t
        coord._peak_tracker.observe(t.astimezone(TZ), load(t, end), tariff)
        if restart_step is not None and t >= end and step == restart_step:
            coord._peak_tracker = PeakTracker.from_dict(
                json.loads(json.dumps(coord._peak_tracker.as_dict())))
        if t >= end:
            step += 1
        t += timedelta(minutes=5)
    rep = coord._month_reports.get(f"{year}-{month:02d}", {})
    return rep.get("capacity_peak_kw"), rep


def last_window_spike(window):
    return lambda t, end: 5.0 if end - timedelta(minutes=window) <= t < end else 1.0


out = []
# DST month ends (and window 15/60)
for (y, m) in ((2027, 10), (2030, 3), (2024, 3), (2029, 3)):
    for w in (15, 60):
        got, _ = drive(coord_for(peak_tariff_window_minutes=w), y, m, last_window_spike(w))
        out.append(("dst", f"{y}-{m:02d} w{w}", got, 5.0))
# k = 3 distinct days: day peaks 4,3,2 on the last three days at noon; last window spike 6
def k3(last_day_has_peak):
    def load(t, end):
        lt = t.astimezone(TZ)
        last = (end - timedelta(minutes=1)).astimezone(TZ).date()
        if end - timedelta(minutes=60) <= t < end:
            return 6.0
        if lt.hour == 12:
            d = (last - lt.date()).days
            if d == 0 and last_day_has_peak:
                return 3.5
            return {1: 4.0, 2: 3.0, 3: 2.0}.get(d, 1.0)
        return 1.0
    return load
for has in (False, True):
    got, _ = drive(coord_for(peak_tariff_peaks_averaged=3), 2026, 4, k3(has), start_days_before=4)
    want = (6 + 4 + 3) / 3
    out.append(("k3", f"last_day_has_peak={has}", got, round(want, 3)))
# k = 3 not distinct days
got, _ = drive(coord_for(peak_tariff_peaks_averaged=3, peak_tariff_distinct_days=False), 2026, 4, k3(True), start_days_before=4)
out.append(("k3", "distinct_days=False", got, round((6 + 4 + 3.5) / 3, 3)))
# restart at each step after the rollover (00:00 .. 00:25 local)
for s in range(6):
    got, _ = drive(coord_for(), 2026, 4, last_window_spike(60), restart_step=s)
    out.append(("rst", f"restart_step={s}", got, 5.0))
# empty month: April masked out; spike in its last window must bill nothing, May unaffected
got, rep = drive(coord_for(peak_tariff_months="nov-mar"), 2026, 4, last_window_spike(60))
out.append(("empty", "masked April", got, 0.0))
fail = 0
for kind, case, got, want in out:
    ok = got is not None and abs(float(got) - want) < 6e-3
    fail += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {kind:5s} {case:28s} got={got} want={want}")
print(f"RESULT attack_cases={len(out)} failures={fail}")
# May after a masked April: the closed-April statement must not leak into May
c = coord_for(peak_tariff_months="nov-mar")
drive(c, 2026, 4, last_window_spike(60))
print("may_running_after_masked_april", c._peak_tracker.billing_statements(c._capacity_tariff()))
