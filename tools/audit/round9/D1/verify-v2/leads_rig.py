"""Verifier V2's rig for the leads harnesses (imported, never run alone).

A real HeatPumpOptimizerCoordinator on tests/harness.py:FakeHass with a frozen aware clock,
deterministic prices and weather, and the three network fetches replaced by no-ops. Written for
this seat (its NOW, price and weather shapes differ from the finder's _rig.py on purpose).
Run from the repository root with PYTHONPATH=tests/hastub. Thread pin first, before numpy.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import resource
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta, timezone

from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

NOW = datetime(2026, 2, 3, 17, 15, tzinfo=timezone.utc)
_T0 = (time.process_time(), time.thread_time())


def freeze(when=NOW):
    dt_util.freeze(when)


def config(**extra):
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.room", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.out"}
    cfg.update(extra)
    return cfg


def hass_with(now=NOW, states=None):
    hass = FakeHass()
    hass.states.set("sensor.room", FakeState("20.6", last_updated=now - timedelta(minutes=3)))
    hass.states.set("sensor.out", FakeState("-7.5", last_updated=now - timedelta(minutes=3)))
    for k, v in (states or {}).items():
        hass.states.set(k, v)
    return hass


def series(coord, now=NOW):
    # A two-peak day (morning and evening), so a solve has something to trade.
    prices = []
    for h in range(-3, 48):
        hod = (now + timedelta(hours=h)).hour
        peak = 0.9 if hod in (7, 8, 17, 18, 19) else 0.0
        prices.append({"total": round(0.45 + peak + 0.02 * (h % 5), 4),
                       "starts_at": (now + timedelta(hours=h)).isoformat(), "level": "NORMAL"})
    coord._prices = prices
    coord._weather_forecast = [
        {"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -7.5 + 3.0 * ((h % 24) > 10),
         "wind_speed": 5.0, "precipitation": 0.0, "humidity": 80.0} for h in range(48)]


def no_fetch(coord):
    async def _noop(*a, **k):
        return None
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


def coordinator(cfg=None, hass=None, options=None):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    hass = hass or hass_with()
    entry = FakeEntry(data=cfg or config(), options=dict(options or {}))
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    series(coord)
    no_fetch(coord)
    return hass, entry, coord


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
