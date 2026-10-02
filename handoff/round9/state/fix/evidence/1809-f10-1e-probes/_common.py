import sys
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState
from homeassistant.util import dt as dt_util

__all__ = [
    "sys",
    "asyncio",
    "datetime",
    "timedelta",
    "timezone",
    "SimpleNamespace",
    "ZoneInfo",
    "FakeEntry",
    "FakeHass",
    "FakeState",
    "dt_util",
    "S",
    "UTC",
    "FOLD_LAST",
    "FOLD_NOW",
    "F60_LAST",
    "F60_NOW",
    "SP_LAST",
    "SP_NOW",
    "true_s",
    "wall_s",
    "show",
    "coord",
]

S = ZoneInfo("Europe/Stockholm")
UTC = timezone.utc
# fold: LAST 00:55Z, NOW 01:55Z (true 1 h, wall 0)
FOLD_LAST = datetime(2026, 10, 25, 2, 55, tzinfo=S)
FOLD_NOW = datetime(2026, 10, 25, 2, 55, tzinfo=S, fold=1)
# true 60 s, wall -3540 s
F60_LAST = datetime(2026, 10, 25, 2, 59, 30, tzinfo=S)
F60_NOW = datetime(2026, 10, 25, 2, 0, 30, tzinfo=S, fold=1)
# spring gap: true 2 min, wall 62 min
SP_LAST = datetime(2026, 3, 29, 1, 59, tzinfo=S)
SP_NOW = datetime(2026, 3, 29, 3, 1, tzinfo=S)


def true_s(a, b):
    return (a.astimezone(UTC) - b.astimezone(UTC)).total_seconds()


def wall_s(a, b):
    return (a - b).total_seconds()


def show(label, observed, expected):
    print(
        f"{'MISFIRE' if observed != expected else 'ok     '} | {label} | observed={observed} expected={expected}"
    )


def coord(hass=None, **cfg):
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    base = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }
    return HeatPumpOptimizerCoordinator(
        hass or FakeHass(), FakeEntry(data={**base, **cfg})
    )
