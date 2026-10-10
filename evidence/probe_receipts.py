#!/usr/bin/env python3
"""Reviewer probe 2 for PR #2119: the 24-receipt attribute and its size.

Usage: python3 probe_receipts.py <tree-root>
Prints RESULT lines. Mine, not the finder's.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime

root = os.path.abspath(sys.argv[1])
sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator as Coord,
)
from heatpump_optimizer.sensor import MonthlySavingsSensor  # noqa: E402

KEEP_MONTHS = 24
c = Coord(FakeHass(), FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
led = c._ledger
# a realistic month: spot, splits, reasons, savings comparison, wear
for i in range(KEEP_MONTHS):
    y, m = (2024 + (i // 12), (i % 12) + 1)
    when = datetime(y, m, 15, 12, 0, tzinfo=UTC)
    led.add(when, "spot", kwh=640.0, sek=920.0)
    led.add(when, "grid_fee", kwh=660.0, sek=150.0)
    led.add(when, "immersion", kwh=30.0, sek=45.0)
    led.add(when, "wear", kwh=0.0, sek=96.0)
    led.add(when, "space", kwh=520.0, sek=760.0)
    led.add(when, "dhw", kwh=120.0, sek=160.0)
    led.add(when, "reason:cheap_hours", kwh=400.0, sek=500.0)
    led.add(when, "reason:expensive_hours", kwh=240.0, sek=420.0)
    led.add(when, "savings_baseline", kwh=700.0, sek=1100.0)
    led.add(when, "savings_actual", kwh=680.0, sek=1000.0)

keys = [k for k in sorted(led.months) if k < "2026-05"]
print(f"RESULT months booked = {len(keys)}")
reports = {k: c._freeze_month_report(k) for k in keys}
print(f"RESULT receipts frozen = {len(reports)}")

view = {"receipts": [reports[k] for k in sorted(reports)], "plan_replay": None}
raw = json.dumps(view["receipts"], separators=(",", ":"))
print(f"RESULT json bytes of the receipts list = {len(raw)}")
print(f"RESULT 16 KB = 16384; exceeds limit = {len(raw) > 16384}")
print(f"RESULT number of receipts published = {len(view['receipts'])}")
print(f"RESULT months in ledger = {len(led.months)}; receipts published = {len(view['receipts'])}")

c.data = dict(c.data or {}, **view)
s = MonthlySavingsSensor(c, c.entry)
attrs = s.extra_state_attributes
print(f"RESULT sensor receipts len = {len(attrs.get('receipts', []))}")
print(f"RESULT sensor has plan_replay key = {'plan_replay' in attrs}")
print(f"RESULT _unrecorded_attributes = {sorted(MonthlySavingsSensor._unrecorded_attributes)}")
print(f"RESULT every frozen receipt reached the sensor = {attrs.get('receipts') == view['receipts']}")
