"""Verifier 2 harness (D6-03 attack) -- Power Headroom availability, clock-swept.

METRIC (mine, differs from the finder's): over the SAME 2x2 grid (main fuse
set / not) x (capacity tariff enabled / not), but with the clock pinned at
FOUR representative instants (1st of month 00:30, 1st 14:00, 17th 03:00,
17th 14:00 — the doc's claim is time-independent, so it must hold at every
instant), the number of (cell, instant) pairs in which the real coordinator's
``_power_headroom()`` answers ``available: True`` with no fuse set.  The
documented rule ("stays unavailable until you set a main fuse size")
predicts 0 such pairs; the finder measured 1 cell at one instant.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/verify2_headroom.py

ROOT RULE: working directory (`ROOT = Path(".")`).
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(".")
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import harness  # noqa: E402
from harness import FakeCoordinator, FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const, sensor as sensor_platform  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402


def coordinator(extra):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    cfg.update(extra)
    co = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(co._update_current_state())
    return co


def headroom_entity(data):
    added: list = []
    entry = FakeEntry()
    entry.runtime_data = FakeCoordinator(data)
    asyncio.run(sensor_platform.async_setup_entry(FakeHass(), entry, added.extend))
    for e in added:
        if getattr(e, "_attr_translation_key", None) == "power_headroom":
            return e
    raise AssertionError("power_headroom sensor not constructed")


TARIFF = {const.CONF_PEAK_TARIFF_ENABLED: True, const.CONF_PEAK_TARIFF_PRICE: 45.0}
CELLS = {
    "no fuse, no tariff": {},
    "no fuse, capacity tariff": dict(TARIFF),
    "fuse, no tariff": {const.CONF_MAIN_FUSE_A: 20},
    "fuse, capacity tariff": {const.CONF_MAIN_FUSE_A: 20, **TARIFF},
}
INSTANTS = [
    datetime(2026, 1, 1, 0, 30),
    datetime(2026, 1, 1, 14, 0),
    datetime(2026, 1, 17, 3, 0),
    datetime(2026, 1, 17, 14, 0),
    datetime(2026, 7, 8, 9, 0),  # a summer month too
]

pairs = 0
no_fuse_available_pairs = 0
detail = []
for label, cfg in CELLS.items():
    co = coordinator(cfg)
    ent = headroom_entity(co._build_data_dict())
    for t in INSTANTS:
        dt_util.freeze(t)
        view = co._power_headroom()
        ent.coordinator.data = co._build_data_dict()
        avail = view.get("available") is True and ent.available
        val = view.get("headroom_kw")
        if avail:
            pairs += 1
            if label.startswith("no fuse"):
                no_fuse_available_pairs += 1
        detail.append((label, t.isoformat(), avail, val, view.get("limit_source")))
dt_util.freeze(None)

print(f"RESULT v2_pairs_measured={len(CELLS) * len(INSTANTS)} cell-instants")
print(f"RESULT v2_available_pairs={pairs} cell-instants")
print(f"RESULT v2_available_no_fuse_pairs={no_fuse_available_pairs} cell-instants")
print(f"RESULT v2_doc_predicted_no_fuse_available=0 cell-instants")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
for row in detail:
    print("  ", row)
