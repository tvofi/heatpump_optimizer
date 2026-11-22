"""Shared driver of box D3-g07's three _forecast_arrays probes: no measurement of its own.

The coordinator is built as tests/golden.py:_capture_coordinator builds it (48 h of Tibber-shaped prices, a weather
forecast carrying humidity 85 %, a solar series), with the clock frozen at golden.START in UTC as
capture_coordinator does. An Open-Meteo client, when asked for, is the production OpenMeteoSolar with its series
built by the production parser open_meteo._parse_block from an hourly block.
"""
from datetime import timedelta, timezone

import _probe_lib as L
from golden import START
from homeassistant.util import dt as dt_util
from heatpump_optimizer import open_meteo as om


def build(open_meteo_rh=None, ghi=300.0):
    c = L.coord()
    c._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4), "starts_at": (START + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"} for h in range(48)]
    c._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(), "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    c._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    if open_meteo_rh is not None:
        client = om.OpenMeteoSolar(c.hass, 59.3, 18.0)
        times = [(START + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(72)]
        block = {"time": times, om._VARIABLE: [ghi] * 72, om._VARIABLE_HUMIDITY: [open_meteo_rh] * 72,
                 om._VARIABLE_SNOWFALL: [0.0] * 72}
        client._forecast = om._parse_block(block, om._VARIABLE)
        client._humidity = om._parse_block(block, om._VARIABLE_HUMIDITY, max_value=100.0)
        client._snowfall = om._parse_block(block, om._VARIABLE_SNOWFALL, max_value=50.0)
        c._open_meteo = client
    return c


def arrays(fn, c):
    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    dt_util.freeze(START)
    try:
        return fn(c)
    finally:
        dt_util.freeze(None)
        dt_util.DEFAULT_TIME_ZONE = saved
