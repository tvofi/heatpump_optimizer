#!/usr/bin/env python3
"""V3 (round 9, D2-s3-01): stale current price under a Tibber QUARTER_HOURLY payload, minute by minute.

Metric (one line): with a Tibber QUARTER_HOURLY GraphQL payload (startsAt strings carrying the
+01:00 offset Tibber returns, 96 quarter prices = winter_typical profile x seeded +-15 % per-quarter
noise) parsed by production price_model.prices_from_tibber_payload into coordinator._prices, the
share of the 1440 minutes of the day (clock frozen aware in Europe/Stockholm, the real-HA
dt_util.now() shape) where HeatPumpOptimizerCoordinator._current_spot_price() differs from the
total of the entry covering that minute, and the settlement-ledger error of a constant 1 kW draw,
sum over minutes |returned - true| * (1/60) kWh, currency per day.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s3_01_tibber_minutes.py [--perturb]
Perturbation (--perturb): _current_spot_price routed through the coordinator's own
_known_prices_for([now])[0] in memory (the proposed fix); both numbers must go to 0.
Null control: an hourly (24-row) payload -> 0 minutes wrong at baseline.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G3-V3 cloud container, 4 cores, linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0, "tests")
sys.path.insert(0, ".")
import numpy as np
from unittest import mock
from harness import FakeEntry, FakeHass
from homeassistant.util import dt as dt_util
from custom_components.heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from custom_components.heatpump_optimizer.price_model import prices_from_tibber_payload
import profiles

PERTURB = "--perturb" in sys.argv
t0p, t0t = time.process_time(), time.thread_time()
TZ = ZoneInfo("Europe/Stockholm")
DAY = datetime(2026, 1, 14, 0, 0, tzinfo=TZ)
rng = np.random.default_rng(20260926)
base = profiles.prices("winter_typical", DAY.replace(tzinfo=None)).astype(float)[:96]

def payload(quarter):
    step = 15 if quarter else 60
    n = 96 if quarter else 24
    vals = base * (1 + rng.uniform(-0.15, 0.15, 96)) if quarter else base.reshape(24, 4).mean(axis=1)
    rows = [{"total": round(float(vals[i]), 4),
             "startsAt": (DAY + timedelta(minutes=step * i)).isoformat(timespec="milliseconds"),
             "level": "NORMAL"} for i in range(n)]
    return {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows, "tomorrow": []}}}]}}}, vals, step

coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"dhw_tank_volume": 180.0}))
for arm, quarter in (("quarter", True), ("hourly_null", False)):
    pl, vals, step = payload(quarter)
    coord._prices = prices_from_tibber_payload(pl)
    wrong = 0; ledger = 0.0
    for m in range(1440):
        now = DAY + timedelta(minutes=m)
        truth = float(round(vals[m // step], 4))
        dt_util.freeze(now)
        try:
            if PERTURB:
                got = float(coord._known_prices_for([now])[0])
            else:
                got = coord._current_spot_price()
        finally:
            dt_util.freeze(None)
        if abs(got - truth) > 1e-9:
            wrong += 1
            ledger += abs(got - truth) / 60.0
    print(f"RESULT {arm}_rows={len(coord._prices)} count")
    print(f"RESULT {arm}_minutes_wrong={wrong} of 1440")
    print(f"RESULT {arm}_ledger_abs_err_1kW={ledger:.4f} currency_per_day (day energy 24 kWh, mean price {np.mean(vals):.3f})")
print(f"RESULT perturbed={int(PERTURB)}")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
