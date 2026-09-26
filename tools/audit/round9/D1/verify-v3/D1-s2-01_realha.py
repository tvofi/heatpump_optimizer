"""V3 reach for D1-s2-01 (malformed get_forecasts response wedges every cycle) under real HA.

Metric: the finder's 200 seeded hostile payloads (tools/audit/round9/D1/s2/parsers.py
hostile(), copied verbatim, seed 9) are handed to a REAL homeassistant WeatherEntity
as the native forecast its integration returns; the response real HA's
weather.async_get_forecasts_service builds is served to the REAL coordinator's
_fetch_weather_forecast (via a registered weather.get_forecasts handler returning
{entity_id: response}); then _current_humidity() -- the wedge site -- is called.
Reported: malformed_responses (forecast not a list, or any non-dict row, in what
real HA returns), ha_service_raised (real HA's own service raised: the coordinator
records a failed fetch and stores nothing), wedged (the stored forecast makes
_current_humidity raise). Count key: exceptions out of _current_humidity.
Control --bypass: the raw hostile payload served directly (the stub's model).

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s2-01_realha.py [--bypass] [--n 200] [--seed 9]
Expected: real arm wedged=0, malformed_responses=0; --bypass wedged=35 (finder's number).
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import copy
import logging
import random
from collections import Counter
from datetime import timedelta

logging.disable(logging.CRITICAL)
BYPASS = "--bypass" in sys.argv
N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 200
SEED = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 9

from homeassistant.util import dt as dt_util  # noqa: E402


# ---- verbatim from tools/audit/round9/D1/s2/parsers.py ----
def healthy_forecast():
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    return [{"datetime": (now + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(48)]


HOSTILE_VALUES = [float("nan"), float("inf"), float("-inf"), "NaN", "abc", None,
                  1e308, -1e308, -50.0, 1e6, "", [], {}, True, "12,5"]
FIELDS = ["datetime", "temperature", "wind_speed", "precipitation", "humidity",
          "solar_irradiance", "native_solar_irradiance"]


def hostile(rng):
    fc = healthy_forecast()
    kind = rng.choice(["field", "field", "field", "entry", "shape", "oversize",
                       "order", "dt"])
    if kind == "field":
        for _ in range(rng.randint(1, 5)):
            i = rng.randrange(len(fc))
            fc[i][rng.choice(FIELDS)] = rng.choice(HOSTILE_VALUES)
        return {"weather.home": {"forecast": fc}}, kind
    if kind == "entry":
        i = rng.randrange(len(fc))
        fc[i] = rng.choice(["x", None, 5, [], ["a"]])
        return {"weather.home": {"forecast": fc}}, kind
    if kind == "shape":
        return rng.choice([
            {"weather.home": {"forecast": "x"}}, {"weather.home": {"forecast": {"a": 1}}},
            {"weather.home": "x"}, {"weather.home": None}, {"weather.home": []},
            {"weather.home": {"forecast": None}}, {"other": {}}, None, [],
        ]), kind
    if kind == "oversize":
        big = []
        base = dt_util.now()
        for h in range(20000):
            big.append({"datetime": (base + timedelta(minutes=h)).isoformat(),
                        "temperature": 1.0, "wind_speed": 1.0, "precipitation": 0.0})
        return {"weather.home": {"forecast": big}}, kind
    if kind == "order":
        rng.shuffle(fc)
        fc += copy.deepcopy(fc[:5])
        return {"weather.home": {"forecast": fc}}, kind
    for i in rng.sample(range(len(fc)), 6):
        fc[i]["datetime"] = rng.choice([
            fc[i]["datetime"][:19], "2026-13-01T00:00:00+00:00", "9999-12-31T23:00:00+00:00",
            "0001-01-01T00:00:00+00:00", 1767225600, "yesterday"])
    return {"weather.home": {"forecast": fc}}, kind
# ---- end verbatim ----


def native_of(payload):
    """What an integration's async_forecast_hourly would have to return."""
    inner = payload.get("weather.home") if isinstance(payload, dict) else payload
    if isinstance(inner, dict) and "forecast" in inner:
        return inner["forecast"]
    return inner


async def main():
    hass = await make_hass()
    from homeassistant.components.weather import (
        WeatherEntity, WeatherEntityFeature, async_get_forecasts_service)
    from homeassistant.core import SupportsResponse
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    box = {"native": None, "raw": None}

    class W(WeatherEntity):
        _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY
        _attr_native_temperature_unit = "°C"
        _attr_native_wind_speed_unit = "m/s"
        _attr_native_precipitation_unit = "mm"

        async def async_forecast_hourly(self):
            return box["native"]

    ent = W(); ent.hass = hass; ent.entity_id = "weather.home"
    hass.states.async_set("weather.home", "cloudy", {"temperature_unit": "°C", "wind_speed_unit": "m/s",
                                                      "precipitation_unit": "mm"})
    from types import SimpleNamespace
    stats = Counter()

    async def handler(call):
        if BYPASS:
            return box["raw"]
        try:
            resp = await async_get_forecasts_service(ent, SimpleNamespace(data={"type": "hourly"}))
        except Exception:
            stats["ha_service_raised"] += 1
            raise
        fc = resp.get("forecast")
        if not isinstance(fc, list) or any(not isinstance(r, dict) for r in fc):
            stats["malformed_responses"] += 1
        return {"weather.home": resp}

    hass.services.async_register("weather", "get_forecasts", handler,
                                 supports_response=SupportsResponse.ONLY)
    coord = HeatPumpOptimizerCoordinator(hass, make_entry({
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "weather_entity": "weather.home"}))
    await asyncio.sleep(0.05)
    rng = random.Random(f"{SEED}:weather")
    kinds = Counter()
    for i in range(N):
        payload, kind = hostile(rng)
        box["raw"], box["native"] = payload, native_of(payload)
        coord._weather_forecast = []
        await coord._fetch_weather_forecast()
        try:
            coord._current_humidity()
        except Exception:  # noqa: BLE001
            stats["wedged"] += 1
            kinds[kind] += 1
    print(f"# arm={'bypass' if BYPASS else 'real-ha-service'} n={N} seed={SEED} wedged_by_kind={dict(kinds)}")
    for k in ("malformed_responses", "ha_service_raised", "wedged"):
        print(f"RESULT {k}={stats[k]} payloads_of_{N}")

asyncio.run(main())
tail()
os._exit(0)
