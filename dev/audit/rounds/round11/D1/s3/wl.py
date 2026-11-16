"""D1-s3 shared workload: a real coordinator driven through full `_async_update_data` cycles.

Not a harness on its own (no RESULT lines): imported by excepts_inject.py and parsers_fuzz.py.
Run from the export root with PYTHONPATH=tests/hastub. The network edges are the only fakes:
Tibber's HTTP POST (a fake aiohttp session answering a quarter-hour priceInfo payload) and
Home Assistant's `weather.get_forecasts` service (registered on FakeHass's honest registry).
Everything between those edges and the published dict is production code.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import logging
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer.coordinator as cmod  # noqa: E402

START = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)

BASE = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "target_temperature": 21.0,
    "min_temperature": 17.0,
    "max_temperature": 23.0,
}
CONFIGS = {
    "minimal": dict(BASE),
    "all": {**BASE, "dhw_tank_volume": 200.0, "peak_tariff_enabled": True,
            "peak_tariff_price_per_kw": 45.0, "pv_enabled": True, "pv_peak_kw": 8.0,
            "pv_export_price": 0.3, "away_enabled": True,
            "external_heat_detection_enabled": True, "comfort_learning_enabled": True,
            "system_identification_enabled": True, "compressor_cycling_cost": 0.5,
            "grid_fee_mode": "rules", "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
            "dhw_windows": "06:00-08:30, 17:00-22:00"},
}


def tibber_payload(start=START, quarters=48 * 4):
    rows = [{"total": round(0.6 + 0.5 * ((q // 4) % 12) / 12.0, 4),
             "startsAt": (start + timedelta(minutes=15 * q)).isoformat(), "level": "NORMAL"}
            for q in range(quarters)]
    return {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows}}}]}}}


def forecast_rows(start=START, hours=48):
    return [{"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(hours)]


class FakeResp:
    def __init__(self, status, payload):
        self.status, self._payload = status, payload

    async def json(self):
        if isinstance(self._payload, BaseException):
            raise self._payload
        return copy.deepcopy(self._payload)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class FakeSession:
    """The Tibber edge. `payload` may be a dict, any JSON value, or an exception to raise."""

    def __init__(self):
        self.status = 200
        self.payload = tibber_payload()
        self.posts = 0

    def post(self, *a, **k):
        self.posts += 1
        return FakeResp(self.status, self.payload)


class Rig:
    """One installation: hass, entry, coordinator and its two network edges."""

    def __init__(self, name="minimal", extra=None):
        cfg = dict(CONFIGS[name])
        cfg.update(extra or {})
        self.hass = FakeHass()
        self.hass.states.set("sensor.indoor", FakeState("21.4"))
        self.hass.states.set("sensor.outdoor", FakeState("-3.0"))
        self.hass.states.set("weather.home", FakeState("cloudy", attributes={"temperature": -3.0}))
        self.session = FakeSession()
        self.forecast = forecast_rows()
        self.forecast_raise = None

        async def get_forecasts(call):
            if self.forecast_raise is not None:
                raise self.forecast_raise
            return {"weather.home": {"forecast": copy.deepcopy(self.forecast)}}

        self.hass.services.async_register("weather", "get_forecasts", get_forecasts)
        cmod.async_get_clientsession = lambda hass, *a, **k: self.session
        self.entry = FakeEntry(data=cfg)
        self.coord = cmod.HeatPumpOptimizerCoordinator(self.hass, self.entry)

    async def cycle(self):
        """One update as DataUpdateCoordinator runs it: data or a raised UpdateFailed."""
        data = await self.coord._async_update_data()
        self.coord.data = data
        return data


def frozen(fn):
    """Run fn() under the frozen START clock in UTC."""
    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    dt_util.freeze(START.replace(tzinfo=None))
    try:
        return fn()
    finally:
        dt_util.freeze(None)
        dt_util.DEFAULT_TIME_ZONE = saved


class Capture(logging.Handler):
    """Every record the integration's loggers emit, for log-once counting."""

    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def capture():
    cap = Capture()
    lg = logging.getLogger("custom_components.heatpump_optimizer")
    lg2 = logging.getLogger("heatpump_optimizer")
    for l in (lg, lg2):
        l.addHandler(cap)
        l.setLevel(logging.DEBUG)
        l.propagate = False
    return cap
