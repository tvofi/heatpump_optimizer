"""D2-s3 (round 9, D2.M4): identities that HELD (non-findings), one RESULT each.

Metric (one line per probe): count of violations of an independent identity
against the production seam named in the RESULT, over the grid stated.
  1. coordinator:_known_prices_for on Europe/Stockholm 2026-03-29 (23 h) and
     2026-10-25 (25 h) with hourly and quarter entries: steps whose price is
     not the covering entry's (entry start <= step < next start).
  2. grid_fee:GridFeeSchedule.fee_vector over both DST days and a full
     January week, rules "= 0.05, Nov-Mar Mon-Fri 06:00-22:00 = 0,25, 22:00-06:00 = 0.02":
     steps whose fee differs from an independent local-wall-clock rule.
  3. tariff:peak_cost == price_per_kw * sum(top-k per-day max excess) over
     500 seeded random 2-day plans (window 60 min, dt 0.25, k=3, distinct
     days) -- |diff| > 1e-9.
  4. tariff:PeakTracker billed_peak_kw == mean of top-3 distinct-day hourly
     means over a seeded 31-day month of 15-min samples, and a month
     rollover resets it: |diff| > 1e-9 and billed after rollover.
Command:
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D2/s3/m4_probes.py [--perturb]
Expected (baseline 1936d5ca): 0 violations on every probe. --perturb swaps
tariff._exact_topk_sum for a top-(k-1) sum, which must move probe 3 to >0
(the harness is live). Tolerance: exact (counts).
Machine: B7 audit container (linux). Root rule: cwd (run from repo root).
"""
import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, ".")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import tariff  # noqa: E402
from custom_components.heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator, _utc_step_starts)
from custom_components.heatpump_optimizer.grid_fee import GridFeeSchedule  # noqa: E402

PERTURB = "--perturb" in sys.argv
TZ = ZoneInfo("Europe/Stockholm")


def probe_known_prices():
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"dhw_tank_volume": 180.0}))
    bad = 0
    total = 0
    for day in (datetime(2026, 3, 29, tzinfo=TZ), datetime(2026, 10, 25, tzinfo=TZ)):
        utc0 = day.astimezone(timezone.utc)
        nxt = (day + timedelta(days=1)).replace(hour=0).astimezone(timezone.utc)
        hours = int((nxt - utc0).total_seconds() // 3600)
        for res_min in (60, 15):
            n_e = hours * 60 // res_min
            starts = [(utc0 + timedelta(minutes=res_min * i)).astimezone(TZ) for i in range(n_e)]
            vals = [round(0.1 + 0.013 * i, 6) for i in range(n_e)]
            coord._prices = [{"total": v, "starts_at": s.isoformat()} for s, v in zip(starts, vals)]
            steps = _utc_step_starts(day, hours * 4)
            known = coord._known_prices_for(steps)
            total += len(steps)
            if len(known) != len(steps):
                bad += abs(len(steps) - len(known))
            for st, got in zip(steps, known):
                idx = int((st.astimezone(timezone.utc) - utc0).total_seconds() // (res_min * 60))
                if got != vals[idx]:
                    bad += 1
    return bad, total


def fee_truth(when):
    local = when.astimezone(TZ)
    h = local.hour + local.minute / 60
    fee = 0.05
    if local.month in (11, 12, 1, 2, 3) and local.weekday() < 5 and 6 <= h < 22:
        fee += 0.25
    if h >= 22 or h < 6:
        fee += 0.02
    return fee


def probe_fee():
    sched = GridFeeSchedule.from_config({
        "grid_fee_mode": "rules",
        "grid_fee_rules": "= 0.05, Nov-Mar Mon-Fri 06:00-22:00 = 0,25, 22:00-06:00 = 0.02",
    })
    bad = total = 0
    for day, ndays in ((datetime(2026, 3, 29, tzinfo=TZ), 1),
                       (datetime(2026, 10, 25, tzinfo=TZ), 1),
                       (datetime(2026, 1, 12, tzinfo=TZ), 7)):
        steps = _utc_step_starts(day, ndays * 100)
        vec = sched.fee_vector(steps)
        for st, got in zip(steps, vec):
            total += 1
            if abs(got - fee_truth(st)) > 1e-12:
                bad += 1
    return bad, total


def probe_peak_cost(rng):
    bad = 0
    n = 192
    days = np.repeat([0, 1], 24)
    for _ in range(500):
        power = rng.uniform(0, 8, n)
        base = rng.uniform(0, 2, n)
        thr = rng.uniform(2, 6)
        got = tariff.peak_cost(power, base, thr, 20.0, 60, 0.25, 3,
                               0, None, days, True)
        win = (power + base).reshape(48, 4).mean(axis=1)
        exc = np.maximum(0, win - thr)
        per_day = np.array([exc[days == d].max() for d in (0, 1)])
        want = 20.0 * np.sort(per_day)[-2:].sum() if np.any(exc > 0) else 0.0
        if abs(got - want) > 1e-9:
            bad += 1
    return bad


def probe_tracker(rng):
    tr = tariff.PeakTracker()
    cap = tariff.CapacityTariff(enabled=True, price_per_kw=50.0)
    start = datetime(2026, 1, 1)
    hourly = {}
    for q in range(31 * 96):
        when = start + timedelta(minutes=15 * q)
        kw = float(rng.uniform(1, 9))
        tr.observe(when, kw, cap)
        hourly.setdefault((when.date(), when.hour), []).append(kw)
    tr.observe(datetime(2026, 1, 31, 23, 59), 0.0, cap)  # stays in last window
    # close the final window by an observation that is still in January
    day_max = {}
    for (d, h), v in hourly.items():
        if (d, h) == (datetime(2026, 1, 31).date(), 23):
            v = v + [0.0]
        m = float(np.mean(v))
        day_max[d] = max(day_max.get(d, 0.0), m)
    # the tracker has closed every window but the open 23:00 one
    closed = {}
    for (d, h), v in hourly.items():
        if (d, h) == (datetime(2026, 1, 31).date(), 23):
            continue
        closed[d] = max(closed.get(d, 0.0), float(np.mean(v)))
    want = float(np.mean(sorted(closed.values())[-3:]))
    bad = int(abs(tr.billed_peak_kw(cap) - want) > 1e-9)
    tr.observe(datetime(2026, 2, 1, 0, 5), 1.0, cap)
    bad += int(tr.billed_peak_kw(cap) != 0.0)
    return bad


def main():
    c0, t0 = time.process_time(), time.thread_time()
    rng = np.random.default_rng(9)
    k, kt = probe_known_prices()
    f, ft = probe_fee()
    if PERTURB:
        with mock.patch.object(tariff, "_exact_topk_sum",
                               lambda e, kk: float(np.sum(np.sort(e)[-(kk - 1):])) if kk > 1 else 0.0):
            pc = probe_peak_cost(rng)
    else:
        pc = probe_peak_cost(rng)
    tk = probe_tracker(np.random.default_rng(10))
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT known_prices_dst_violations={k} of {kt} steps")
    print(f"RESULT grid_fee_violations={f} of {ft} steps")
    print(f"RESULT peak_cost_identity_violations={pc} of 500 plans")
    print(f"RESULT peak_tracker_violations={tk} of 2 checks")
    print(f"RESULT perturbed={int(PERTURB)}")
    print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            sw = [ln for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
