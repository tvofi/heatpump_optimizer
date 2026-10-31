"""D8-s3 shared builder: every entity of every platform through the real
async_setup_entry, against a real coordinator built the way
tests/golden.py:_capture_coordinator builds it (frozen clock, injected
prices/forecasts, _build_data_dict). Imported by the D8-s3 harnesses; not a
harness itself.

    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/roster.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
import golden  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    binary_sensor, button, climate, sensor, switch,
)
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
PLATFORMS = {
    "sensor": sensor, "binary_sensor": binary_sensor, "button": button,
    "climate": climate, "switch": switch, "datetime": datetime_platform,
}
STRINGS = {
    "strings": json.loads((ROOT / "strings.json").read_text())["entity"],
    "en": json.loads((ROOT / "translations/en.json").read_text())["entity"],
    "sv": json.loads((ROOT / "translations/sv.json").read_text())["entity"],
}


def build_coordinator(config):
    """Real coordinator, one data dict built -- golden._capture_coordinator."""
    START = golden.START
    dt_util.freeze(START)
    hass = FakeHass()
    entry = FakeEntry(data=config)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    coord._forecast_arrays()
    coord.data = coord._build_data_dict()
    return hass, entry, coord


def collect(hass, entry, coord):
    """(platform, entity) for every entity the six platforms add."""
    out = []
    entry.runtime_data = coord
    for plat, module in PLATFORMS.items():
        added = []
        asyncio.run(module.async_setup_entry(hass, entry, added.extend))
        out.extend((plat, e) for e in added)
    return out


def enabled_default(entity):
    return bool(getattr(entity, "entity_registry_enabled_default",
                        getattr(entity, "_attr_entity_registry_enabled_default", True)))


def record(plat, e):
    key = getattr(e, "_attr_translation_key", None)
    names = {lang: STRINGS[lang].get(plat, {}).get(key, {}).get("name")
             for lang in STRINGS}
    return {
        "platform": plat, "entity_id": e.entity_id, "key": key,
        "name_en": names["en"], "name_sv": names["sv"],
        "name_strings": names["strings"],
        "enabled": enabled_default(e),
        "category": getattr(e, "entity_category", None),
        "cls": type(e).__name__,
    }


def roster(config):
    hass, entry, coord = build_coordinator(config)
    try:
        return [record(p, e) for p, e in collect(hass, entry, coord)]
    finally:
        dt_util.freeze(None)


if __name__ == "__main__":
    cfg = golden.coordinator_scenarios()[sys.argv[1] if len(sys.argv) > 1 else "coord_all_features"]
    for r in roster(cfg):
        print(json.dumps(r, ensure_ascii=False))


def build_honest(config, states=None, cycles=1, price_base=0.6):
    """Real coordinator after `cycles` real input-read cycles
    (_update_current_state), prices/forecasts injected as golden does, then
    _build_data_dict -- tests/entities.py:_honest_coordinator plus golden's
    injection. The clock is frozen at golden.START (+1 h per extra cycle)."""
    from harness import FakeState
    START = golden.START
    hass = FakeHass()
    for eid, st in (states or {}).items():
        hass.states.set(eid, st if not isinstance(st, str) else FakeState(st))
    entry = FakeEntry(data=config)
    dt_util.freeze(START)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    for c in range(cycles):
        dt_util.freeze(START + timedelta(hours=c))
        coord._prices = [
            {"total": round(price_base + 0.5 * (h % 12) / 12.0 + 0.1 * c, 4),
             "starts_at": (START + timedelta(hours=h)).isoformat(),
             "level": "NORMAL"}
            for h in range(48)
        ]
        coord._weather_forecast = [
            {"datetime": (START + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0 - c, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0}
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
        ]
        asyncio.run(coord._update_current_state())
        coord._forecast_arrays()
        coord.data = coord._build_data_dict()
    return hass, entry, coord
