"""D8 round 5 -- the topology x feature matrix, first pass: enumerate every
entity of every platform against a realistic coordinator payload and print
its published surface.

    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/explore.py [scenario]

Read-only exploration; the finding harness is matrix.py.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

# --- thread pin, before numpy -------------------------------------------------
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tests"))

from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402

from golden import START, coordinator_scenarios, _capture_coordinator  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor,
    button,
    climate,
    datetime as datetime_mod,
    sensor,
    switch,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
_STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]

PLATFORM_MODULES = {
    "sensor": sensor,
    "binary_sensor": binary_sensor,
    "button": button,
    "climate": climate,
    "switch": switch,
    "datetime": datetime_mod,
}


def real_coordinator(config):
    """A real coordinator with one input cycle, the way golden captures it."""
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        entry = FakeEntry(data=dict(config))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = [
            {
                "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                "starts_at": (START + timedelta(hours=h)).isoformat(),
                "level": "NORMAL",
            }
            for h in range(48)
        ]
        coord._weather_forecast = [
            {
                "datetime": (START + timedelta(hours=h)).isoformat(),
                "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                "wind_speed": 3.0,
                "precipitation": 0.0,
                "humidity": 85.0,
            }
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
        ]
        coord.data = coord._build_data_dict()
    finally:
        dt_util.freeze(None)
    return hass, entry, coord


def collect(module, coordinator):
    added = []

    def add_entities(entities):
        added.extend(entities)

    hass = FakeHass()
    entry = FakeEntry()
    entry.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(hass, entry, add_entities))
    return added


def display_name(platform, entity):
    key = getattr(entity, "_attr_translation_key", None)
    return _STRINGS.get(platform, {}).get(key, {}).get("name", f"<untranslated {platform}:{key}>")


def main():
    scenarios = coordinator_scenarios()
    which = sys.argv[1:] or list(scenarios)
    for name in which:
        cfg = scenarios[name]
        hass, entry, coord = real_coordinator(cfg)
        data = coord.data
        print(f"\n===== {name} (data keys={len(data)}) =====")
        for platform, module in PLATFORM_MODULES.items():
            entities = collect(module, coord)
            for e in entities:
                tkey = getattr(e, "_attr_translation_key", None)
                enabled = getattr(e, "_attr_entity_registry_enabled_default", True)
                avail = None
                try:
                    avail = e.available
                except Exception as exc:  # noqa: BLE001
                    avail = f"ERR {exc!r}"
                nv = None
                for attr in ("native_value", "is_on", "current_temperature"):
                    try:
                        nv = getattr(e, attr)
                    except Exception:  # noqa: BLE001
                        continue
                    if nv is not None:
                        break
                print(
                    f"  {platform:14s} {type(e).__name__:34s} key={tkey!r:34s} "
                    f"name={display_name(platform, e)!r:44s} "
                    f"enabled={enabled} avail={avail} nv={nv!r}"
                )


if __name__ == "__main__":
    main()
