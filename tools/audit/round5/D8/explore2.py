"""D8 round 5 -- explore: run each topology through a real solve, then read
every entity of every platform, printing state/availability/metadata.

    PYTHONPATH=tests/hastub python3 tools/audit/round5/D8/explore2.py [scenario]
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

for _var in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tests"))

from datetime import timedelta  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, datetime as datetime_mod, sensor, switch,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
_STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]

PLATFORM_MODULES = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_mod,
}


def solved_coordinator(config, cycles=2):
    dt_util.freeze(START)
    try:
        hass = FakeHass()
        entry = FakeEntry(data=dict(config))
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        coord._prices = [
            {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(48)
        ]
        coord._weather_forecast = [
            {"datetime": (START + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
        ]

        async def run():
            await coord._update_current_state()
            coord.data = coord._build_data_dict()
            for _ in range(cycles - 1):
                await coord._update_current_state()
                await coord.async_run_optimization()
                coord.data = coord._build_data_dict()

        asyncio.run(run())
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


def name_of(platform, entity):
    key = getattr(entity, "_attr_translation_key", None)
    return _STRINGS.get(platform, {}).get(key, {}).get("name", f"<untranslated {platform}:{key}>")


def main():
    scenarios = coordinator_scenarios()
    which = sys.argv[1:] or list(scenarios)
    for name in which:
        hass, entry, coord = solved_coordinator(scenarios[name])
        print(f"\n===== {name} (data keys={len(coord.data)}) =====")
        for platform, module in PLATFORM_MODULES.items():
            for e in collect(module, coord):
                avail = e.available if hasattr(e, "available") else "?"
                nv = None
                for attr in ("native_value", "is_on", "current_temperature"):
                    try:
                        v = getattr(e, attr)
                    except Exception as exc:  # noqa: BLE001
                        nv = f"ERR:{exc!r}"
                        break
                    if v is not None:
                        nv = v
                        break
                flag = "  <-- None" if nv is None and avail is True else ""
                print(
                    f"  {platform:14s} {name_of(platform, e)!r:44s} "
                    f"avail={str(avail):5s} nv={nv!r}{flag}"
                )


if __name__ == "__main__":
    main()
