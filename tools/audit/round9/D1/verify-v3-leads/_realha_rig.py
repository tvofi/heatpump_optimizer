"""Shared rig for the V3 real-HA verify harnesses (imported, never run alone).

Builds a REAL homeassistant.core.HomeAssistant instance (genuine 2026.2.3 package, no
tests/hastub on the path) with a real StateMachine and a real executor, and a real
HeatPumpOptimizerCoordinator on top of it. The three network fetches are no-op'd exactly as
tests/harness.py / D1/leads/_rig.py do for the stub, and "now" is pinned with
unittest.mock.patch.object on the real homeassistant.util.dt module (an in-memory perturbation,
never an on-disk edit). Run with:
    PYTHONPATH=custom_components:tests /root/venvha/bin/python -c "import typing; typing.ByteString=bytes; ..."
or import this module first (it installs the compat shim itself). Thread pin first, before numpy.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import resource
import tempfile
import asyncio
from datetime import datetime, timedelta, timezone
from unittest import mock

import typing
typing.ByteString = bytes  # CPython 3.14 compat shim, per SUBSEAT.md

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import homeassistant.core as core  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from harness import FakeEntry  # noqa: E402 (no hastub dependency: only imports ConfigEntryState)
from heatpump_optimizer import const  # noqa: E402

_T0 = (time.process_time(), time.thread_time())
NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)


def tail():
    cpu = time.process_time() - _T0[0]
    thr = time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={(cpu / thr) if thr else 1.0:.3f}")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1}")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    print(f"RESULT swapins={ru.ru_minflt}")


def freeze_now(when=NOW):
    """In-memory perturbation (mock.patch.object), never an on-disk edit."""
    p1 = mock.patch.object(dt_util, "now", return_value=when)
    p2 = mock.patch.object(dt_util, "utcnow", return_value=when.astimezone(timezone.utc))
    p1.start()
    p2.start()
    return [p1, p2]


def base_config(**extra):
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    cfg.update(extra)
    return cfg


def make_hass(now=NOW, states=None):
    # StateMachine.async_set stamps last_updated from time.time() (real wall
    # clock), not from dt_util -- so an explicit timestamp is required or
    # every state is "ahead of" a frozen `now` in the past and reads stale.
    ts = now.timestamp()
    d = tempfile.mkdtemp()
    hass = core.HomeAssistant(d)
    hass.states = core.StateMachine(hass.bus, hass.loop)
    hass.states.async_set("sensor.indoor", "21.0", timestamp=ts)
    hass.states.async_set("sensor.outdoor", "-3.0", timestamp=ts)
    for k, v in (states or {}).items():
        set_state_spec(hass, k, v, now=now)
    return hass


def set_state_spec(hass, entity_id, spec, now=NOW):
    """spec is a bare state string (stamped at `now`), or a dict with any of
    state/attrs/age_min (age_min shifts the timestamp back that many minutes)."""
    if isinstance(spec, dict):
        state = spec.get("state", "unknown")
        attrs = spec.get("attrs") or {}
        age_min = spec.get("age_min", 0.0)
    else:
        state, attrs, age_min = spec, {}, 0.0
    ts = (now - timedelta(minutes=age_min)).timestamp()
    hass.states.async_set(entity_id, state, attrs, timestamp=ts)


def make_entry(**extra):
    return FakeEntry(data=base_config(**extra))


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
    coord._solar_forecast = []

    async def _noop(*a, **k):
        return None
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop


def build_coordinator(config=None, states=None, now=NOW):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    entry = FakeEntry(data=base_config(**(config or {})))

    async def _build():
        hass = make_hass(now=now, states=states)  # needs a running loop
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        inject_series(coord, now=now)
        return coord
    return asyncio.run(_build())


async def abuild_coordinator(config=None, states=None, now=NOW):
    """Same as build_coordinator, but for callers that already run a loop
    (e.g. to keep the coordinator's hass and event loop alive for later awaits)."""
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    entry = FakeEntry(data=base_config(**(config or {})))
    hass = make_hass(now=now, states=states)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    inject_series(coord, now=now)
    return coord
