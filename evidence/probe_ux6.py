#!/usr/bin/env python3
"""Reviewer probe for PR #2119 (R9-UX-6): the receipt total.

Usage: python3 probe_ux6.py <tree-root>

Books the finder's fixture (tests/features.py UX-6 block) and prints the
receipt total each tree computes, plus the restatement arms. Prints RESULT
lines. This is MY probe (built by the reviewer); the finder's harness is the
UX-6 block in tests/features.py.
"""
from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

root = os.path.abspath(sys.argv[1])
sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator as Coord,
)

MARCH = datetime(2026, 3, 15, 12, 0, tzinfo=UTC)


def coord(**config):
    return Coord(FakeHass(), FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home", **config}))


def book(c, *, splits=True):
    led = c._ledger
    led.add(MARCH, "spot", kwh=100.0, sek=150.0)
    led.add(MARCH, "grid_fee", kwh=105.0, sek=25.0)
    led.add(MARCH, "immersion", kwh=5.0, sek=7.5)
    led.add(MARCH, "wear", kwh=0.0, sek=12.0)
    if splits:
        led.add(MARCH, "space", kwh=80.0, sek=120.0)
        led.add(MARCH, "dhw", kwh=25.0, sek=37.5)
        led.add(MARCH, "reason:cheap_hours", kwh=100.0, sek=150.0)
        led.add(MARCH, "savings_baseline", kwh=120.0, sek=200.0)
        led.add(MARCH, "savings_actual", kwh=105.0, sek=157.5)


print(f"ROOT {root}")

# --- the money the month cost, computed by hand from the finder's fixture ---
HAND = 150.0 + 25.0 + 7.5 + 12.0
print(f"RESULT hand-computed billed total = {HAND} SEK")

# --- arm A: the split fixture through the tree's own receipt path ---
a = coord()
book(a, splits=True)
rec = a._freeze_month_report("2026-03")
print(f"RESULT coordinator receipt total_sek (split fixture) = {rec['total_sek']}")
print(f"RESULT receipt basis = {rec.get('basis')}")

# --- arm B: the null control, no splits/comparisons ---
b = coord()
book(b, splits=False)
rec_b = b._freeze_month_report("2026-03")
print(f"RESULT coordinator receipt total_sek (null, no splits) = {rec_b['total_sek']}")

# --- arm C: the pure function in ledger.py, if it exists at this tree ---
try:
    from heatpump_optimizer import ledger as L
except Exception as exc:  # noqa: BLE001
    L = None
    print(f"RESULT ledger import failed: {exc}")

if L is not None and hasattr(L, "freeze_month_report"):
    pure = L.freeze_month_report(
        a._ledger, "2026-03", compressor_starts=7, contract_comparison={"month": "2026-03"}
    )
    print(f"RESULT ledger.freeze_month_report total_sek = {pure['total_sek']}")
    print(f"RESULT ledger.freeze_month_report basis = {pure['basis']}")
    print(f"RESULT BILLED_LINES = {L.BILLED_LINES}")

    # --- restatement arms ---
    fresh = L.restate_total(pure)
    print(f"RESULT restate_total(fresh) total = {fresh['total_sek']} (fresh {pure['total_sek']})")
    old = dict(pure, total_sek=709.5)
    old.pop("basis")
    print(f"RESULT restate_total(old 709.5) total = {L.restate_total(old)['total_sek']}")
    empty = L.restate_total({"month": "2026-01", "lines": {}})
    print(f"RESULT restate_total(empty lines) total = {empty['total_sek']}")
    # a receipt whose lines were never split: the old formula and the new agree
    print(
        "RESULT billed_total over the split receipt's published lines = "
        f"{L.billed_total(pure['lines'])}"
    )
else:
    print("RESULT no ledger.freeze_month_report at this tree (base)")

# --- what the OLD formula (sum every non-reason line) would give, at this tree ---
full = {"spot": 150.0, "grid_fee": 25.0, "immersion": 7.5, "wear": 12.0,
        "space": 120.0, "dhw": 37.5, "savings_baseline": 200.0, "savings_actual": 157.5}
print(f"RESULT sum-every-non-reason-line (the defect) = {round(sum(full.values()), 2)}")
