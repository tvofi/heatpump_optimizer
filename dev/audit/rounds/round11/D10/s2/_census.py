"""Shared builder for the D10-s2 gold harnesses (not a harness itself).

Builds every entity the six platforms add, through each platform's real
``async_setup_entry``, against a real coordinator after one input cycle.
Run from the export root with PYTHONPATH=tests/hastub.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib
import json
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = ["tests", "custom_components"]

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PKG = ROOT / "custom_components" / "heatpump_optimizer"

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
    "price_source": "entity",
    "price_entity": "sensor.prices",
}


def build(extra=None, states=None):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    for k, v in (states or {}).items():
        hass.states.set(k, v)
    cfg = {**CONFIG, **(extra or {})}
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    entry.runtime_data = coord
    return hass, entry, coord


def entities(extra=None, states=None):
    """[(platform, entity)] for every entity every platform adds."""
    hass, entry, coord = build(extra, states)
    out = []
    for platform in const.PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{platform}")
        added = []

        def add(ents, update_before_add=False, _a=added):
            for e in ents:
                e.hass = hass
            _a.extend(ents)

        asyncio.run(mod.async_setup_entry(hass, entry, add))
        out.extend((platform, e) for e in added)
    return out, coord, entry


def load_json(rel):
    return json.loads((PKG / rel).read_text())


def stats():
    """The contract's closing RESULT lines."""
    import resource
    pc = time.process_time()
    tc = time.thread_time() or 1e-9
    print(f"RESULT thread_factor={pc / tc:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
