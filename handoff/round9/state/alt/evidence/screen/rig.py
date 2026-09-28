"""Shared rig for the phase-A a3 probes (not part of the repo).

Run every probe from the worktree root with
  PYTHONPATH=tests/hastub:custom_components:tests:<OUT> python3 <OUT>/<id>.py

Builds a real HeatPumpOptimizerCoordinator on the tests/harness.py FakeHass,
with injected hourly prices/weather anchored on the real clock (the
tests/features.py `_solve_coord` pattern), network fetches as no-ops, a
recording service registry, real asyncio tasks, and the solve forced
in-process (the tests/features.py `_r9f13_inline` pattern) behind an optional
asyncio.Event gate so a probe can hold the solve await open.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from datetime import timedelta

sys.argv = [sys.argv[0]]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402


class RigHass(FakeHass):
    spawn_real = False

    def async_create_task(self, coro, name=None, eager_start=None):
        if not self.spawn_real:
            coro.close()
            return None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            coro.close()
            return None
        return loop.create_task(coro)


# ---- the solve: in-process, optionally gated --------------------------------
class SolveGate:
    """Hold every solve await until released (when armed)."""

    def __init__(self) -> None:
        self.armed = False
        self.entered = None
        self.release = None
        self.fail = False
        self.calls = 0

    def arm(self):
        self.armed = True
        self.entered = asyncio.Event()
        self.release = asyncio.Event()

    def disarm(self):
        self.armed = False


GATE = SolveGate()


async def _inline_await_optimize(hass, optimizer, state, *positional, **keywords):
    GATE.calls += 1
    if GATE.armed:
        GATE.entered.set()
        await GATE.release.wait()
    if GATE.fail:
        raise RuntimeError("probe-injected solve failure")
    return optimize_in_process(optimizer, state, positional, keywords)


cmod._await_optimize = _inline_await_optimize


def _t0():
    return dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)


def prices(n=48, t0=None):
    t0 = t0 or _t0()
    return [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (t0 + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(n)
    ]


def weather(n=48, t0=None, temp=-5.0):
    t0 = t0 or _t0()
    return [
        {
            "datetime": (t0 + timedelta(hours=h)).isoformat(),
            "temperature": temp,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(n)
    ]


def make(entry_id="probe", extra=None, hass=None):
    hass = hass or RigHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C"),
            "sensor.outdoor": FakeState("-5.0", unit="°C"),
            "switch.heat_pump": FakeState("on"),
        }
    )
    data = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "heat_pump_switch_entity": "switch.heat_pump",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "ecl110_displace_set_topic": "ecl_probe/set",
        "ecl110_command_topic": "ecl_probe/command",
        **(extra or {}),
    }
    coord = Coord(hass, FakeEntry(data=data, entry_id=entry_id))
    hass.spawn_real = True
    coord._skip_solve_once = False
    coord._prices = prices()
    coord._weather_forecast = weather()

    async def _noop(*_a, **_k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    return coord


def actuations(hass, since=0):
    return [(d, s, dict(x or {})) for d, s, x in hass.services.calls[since:] if d in ("switch", "mqtt", "homeassistant")]


def spy_publish(coord):
    """Record every async_publish_current_action with a copy of the action it sends."""
    sent = []
    real = coord.async_publish_current_action

    async def _spy(*a, **k):
        act = coord._current_action or {}
        sent.append({k2: act.get(k2) for k2 in ("mode", "power", "power_normalized", "heat_pump_on", "displace_value", "boost_space", "boost_dhw", "dhw_power", "setpoint")})
        return await real(*a, **k)

    coord.async_publish_current_action = _spy
    return sent
