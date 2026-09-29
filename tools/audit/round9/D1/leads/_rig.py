"""Shared rig for the round-9 leads harnesses (imported, never run alone).

Builds a real HeatPumpOptimizerCoordinator on tests/harness.py:FakeHass with a
frozen aware clock, deterministic prices and weather, and the three network
fetches (_fetch_tibber_prices, _fetch_weather_forecast, _fetch_solar_forecast)
replaced by no-ops that keep the injected series -- they sit upstream of every
seam these harnesses measure. Run from the repository root with
PYTHONPATH=tests/hastub. Thread pin first, before numpy.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import resource
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta, timezone

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
_T0 = (time.process_time(), time.thread_time())


def freeze(when=NOW):
    dt_util.freeze(when)


def base_config(**extra):
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    cfg.update(extra)
    return cfg


def make_hass(now=NOW, states=None):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0", last_updated=now - timedelta(minutes=5)))
    hass.states.set("sensor.outdoor", FakeState("-3.0", last_updated=now - timedelta(minutes=5)))
    for k, v in (states or {}).items():
        hass.states.set(k, v)
    return hass


def inject_series(coord, now=NOW, outdoor=-5.0):
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (now + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(-2, 48)
    ]
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": outdoor,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]


def no_fetch(coord):
    async def _noop(*a, **k):
        return None
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


def make_coord(config=None, hass=None, entry=None):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    hass = hass or make_hass()
    entry = entry or FakeEntry(data=config or base_config())
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    inject_series(coord)
    no_fetch(coord)
    return hass, entry, coord


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
