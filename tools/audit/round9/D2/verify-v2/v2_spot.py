#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s3-01: _current_spot_price under 15-minute entries.

Metric (one line): minutes of one day (1440, clock frozen at every whole minute)
where HeatPumpOptimizerCoordinator._current_spot_price() differs from the price of
the entry whose [start, next start) covers now, with the entry list produced by the
PRODUCTION Tibber parser (price_model.prices_from_tibber_payload) from a
Tibber-shaped QUARTER_HOURLY payload in local time (+01:00), every quarter a
distinct price; arms: distinct (every quarter distinct), hourly-constant quarters
(the finder's step shape), and a null control of 24 hourly entries.
Count key: the value the seam returns.
Hooks: coordinator:HeatPumpOptimizerCoordinator._current_spot_price, price_model:prices_from_tibber_payload.
Perturbation: --perturb patches coordinator.timedelta so the 1 h span is 15 min
(in memory): quarter arms -> 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_spot.py [--perturb]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Deterministic.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timedelta, timezone
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, ".")
import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import custom_components.heatpump_optimizer.coordinator as cm  # noqa: E402
from custom_components.heatpump_optimizer.price_model import prices_from_tibber_payload  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
PERT = "--perturb" in sys.argv
TZ = timezone(timedelta(hours=1))
DAY = datetime(2026, 2, 3, 0, 0, tzinfo=TZ)


class Span:
    def __call__(self, *a, **k):
        if not a and k == {"hours": 1}:
            return timedelta(minutes=15)
        return timedelta(*a, **k)


def payload(starts, totals):
    rows = [{"total": float(t), "startsAt": s.isoformat(), "level": "NORMAL"} for s, t in zip(starts, totals)]
    return {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows, "tomorrow": []}}}]}}}


rng = np.random.default_rng(31)
q_starts = [DAY + timedelta(minutes=15 * i) for i in range(96)]
h_starts = [DAY + timedelta(hours=i) for i in range(24)]
distinct = np.round(rng.uniform(0.05, 0.60, 96), 4)
hourly = np.round(rng.uniform(0.05, 0.60, 24), 4)
arms = {
    "quarter_distinct": (q_starts, distinct),
    "quarter_hourly_constant": (q_starts, np.repeat(hourly, 4)),
    "null_hourly_entries": (h_starts, hourly),
}
coord = cm.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"dhw_tank_volume": 180.0}))
for arm, (starts, totals) in arms.items():
    parsed = prices_from_tibber_payload(payload(starts, totals))
    assert isinstance(parsed, list) and len(parsed) == len(starts)
    coord._prices = parsed
    mism = 0
    err = []
    for minute in range(1440):
        now = DAY + timedelta(minutes=minute)
        idx = max(i for i, s in enumerate(starts) if s <= now)
        truth = float(totals[idx])
        dt_util.freeze(now)
        try:
            if PERT:
                with mock.patch.object(cm, "timedelta", Span()):
                    got = coord._current_spot_price()
            else:
                got = coord._current_spot_price()
        finally:
            dt_util.freeze(None)
        mism += got != truth
        err.append(abs(got - truth))
    print(f"RESULT {arm}_minutes_mispriced={mism} of 1440")
    print(f"RESULT {arm}_mean_abs_err={np.mean(err):.4f} currency_per_kWh")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
