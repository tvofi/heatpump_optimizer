"""V3 reach for D1-s2-02 (finite-but-absurd forecast values reach the solve) under real HA.

Metric: a REAL homeassistant WeatherEntity (native degC, m/s, mm) returns 48
healthy hourly rows with ONE row poisoned (temperature -1e308, or wind 1e12 m/s);
real HA's weather.async_get_forecasts_service converts it (to the instance's
metric units: wind in km/h), the REAL coordinator's _fetch_weather_forecast stores
it, and coordinator._weather_series() (the weather half of _forecast_arrays) builds the arrays the solve receives.
Reported per case: reaches_solve_arrays (1 = the absurd value, in model units, is
in HorizonArrays.outdoor_temps / wind_speeds). Count key: the series
_weather_series returns (prices are not configured, so _forecast_arrays itself returns empty). No solve is run (the runaway itself is the finder's
solve_poison.py number, re-run separately).
Perturbation --clip: _forecast_in_model_units wrapped in memory to clip temperature
to [-60,60] and wind to [0,60] -> reaches_solve_arrays=0.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s2-02_realha.py [--clip]
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import numpy as np

logging.disable(logging.CRITICAL)
CLIP = "--clip" in sys.argv


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from homeassistant.components.weather import (
        WeatherEntity, WeatherEntityFeature, async_get_forecasts_service)
    from homeassistant.core import SupportsResponse
    from heatpump_optimizer import coordinator as cm

    box = {}

    class W(WeatherEntity):
        _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY
        _attr_native_temperature_unit = "°C"
        _attr_native_wind_speed_unit = "m/s"
        _attr_native_precipitation_unit = "mm"

        async def async_forecast_hourly(self):
            return box["native"]

    ent = W(); ent.hass = hass; ent.entity_id = "weather.home"

    async def handler(call):
        return {"weather.home": await async_get_forecasts_service(ent, SimpleNamespace(data={"type": "hourly"}))}
    hass.services.async_register("weather", "get_forecasts", handler, supports_response=SupportsResponse.ONLY)
    hass.states.async_set("weather.home", "cloudy", {"temperature_unit": ent._temperature_unit,
                                                      "wind_speed_unit": ent._wind_speed_unit,
                                                      "precipitation_unit": ent._precipitation_unit})
    coord = cm.HeatPumpOptimizerCoordinator(hass, make_entry({
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "weather_entity": "weather.home"}))
    await asyncio.sleep(0.05)
    orig = cm._forecast_in_model_units

    def clipped(state, forecast):
        rows = orig(state, forecast)
        out = []
        for r in rows:
            r = dict(r)
            r["temperature"] = float(np.clip(float(r.get("temperature", 0.0)), -60, 60))
            r["wind_speed"] = float(np.clip(float(r.get("wind_speed", 0.0)), 0, 60))
            out.append(r)
        return out
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    cases = {"temp_minus_1e308": ("native_temperature", -1e308), "wind_1e12": ("native_wind_speed", 1e12)}
    reached = 0
    with mock.patch.object(cm, "_forecast_in_model_units", clipped if CLIP else orig):
        for name, (field, val) in cases.items():
            rows = [{"datetime": (now + timedelta(hours=h)).isoformat(), "native_temperature": -5.0,
                     "native_wind_speed": 3.0, "native_precipitation": 0.0, "humidity": 85.0}
                    for h in range(48)]
            rows[3][field] = val
            box["native"] = rows
            coord._weather_forecast = []
            await coord._fetch_weather_forecast()
            n = coord._ctx._opt_config.n_steps
            mid = now.replace(hour=0)
            off = int((now - mid).total_seconds() / 60 / cm.FORECAST_STEP_MINUTES)
            outdoor, wind, *_ = coord._weather_series(n, mid, off)
            t = np.asarray(outdoor, float); w = np.asarray(wind, float)
            hit = int((t.min() < -1e300) if name.startswith("temp") else (w.max() >= 1e11))
            reached += hit
            print(f"# {name}: ha_wind_unit={ent._wind_speed_unit} min_T={t.min():.3g} max_wind={w.max():.3g} m/s reached={hit}")
    print(f"RESULT reaches_solve_arrays={reached} count_of_{len(cases)}")

asyncio.run(main())
tail()
os._exit(0)
