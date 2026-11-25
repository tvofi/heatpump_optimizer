"""D8-s2 rig: every entity of every platform, built through the real
async_setup_entry over each tests/golden.py coordinator scenario (union).

Not a harness on its own; m3_naming.py imports it. Run from the export root
with PYTHONPATH=tests/hastub.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import contextlib
import io
import sys
from datetime import timedelta, timezone

sys.path[:0] = ["tests", "tests/hastub"]
import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402

PLATFORMS = ("sensor", "binary_sensor", "button", "switch", "climate", "datetime")


def build(config):
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.coordinator import (
        HeatPumpOptimizerCoordinator, _with_sensor_advisor)
    import importlib
    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    dt_util.freeze(golden.START)
    try:
        hass = FakeHass()
        entry = FakeEntry(data=config)
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        S = golden.START
        coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                          "starts_at": (S + timedelta(hours=h)).isoformat(),
                          "level": "NORMAL"} for h in range(48)]
        coord._weather_forecast = [{"datetime": (S + timedelta(hours=h)).isoformat(),
                                    "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
                                    "wind_speed": 3.0, "precipitation": 0.0,
                                    "humidity": 85.0} for h in range(48)]
        coord._solar_radiation_forecast = [
            max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
        coord._forecast_arrays()
        data = coord._build_data_dict()
        coord.data = asyncio.run(_with_sensor_advisor(coord, dict(data)))
        entry.runtime_data = coord
        out = []
        for plat in PLATFORMS:
            mod = importlib.import_module(f"heatpump_optimizer.{plat}")
            added = []

            def add(ents, *a, **k):
                for e in ents:
                    e.hass = hass
                added.extend(ents)
            with contextlib.redirect_stdout(io.StringIO()):
                asyncio.run(mod.async_setup_entry(hass, entry, add))
            out.extend((plat, e) for e in added)
        return out
    finally:
        dt_util.freeze(None)
        dt_util.DEFAULT_TIME_ZONE = saved


def all_entities():
    """{(platform, translation_key or class): (platform, entity, [scenarios])}"""
    seen = {}
    for name, cfg in golden.coordinator_scenarios().items():
        for plat, e in build(cfg):
            k = (plat, getattr(e, "_attr_translation_key", None) or type(e).__name__)
            seen.setdefault(k, [plat, e, []])[2].append(name)
    return seen
