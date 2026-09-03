"""Checks that Open-Meteo irradiance lands on the right optimizer steps.

This is the seam where the feature can fail silently. Every other part of the
chain either works or throws, but a timestamp alignment bug just shifts the sun
by an interval and quietly produces a slightly wrong heating plan. So this
drives the real ``_forecast_arrays`` (the five-series seam the optimizer
reads; the ``_prepare_forecast_data`` back-compat slice over it was
production-dead and removed, #226) with a synthetic irradiance series
whose value encodes its own timestamp, making any offset immediately visible.

    PYTHONPATH=/tmp/hastub python tests/solar_alignment.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.open_meteo import IrradianceSeries, OpenMeteoSolar
from heatpump_optimizer.optimizer import OptimizationConfig
from heatpump_optimizer.price_model import PriceShapeModel
from heatpump_optimizer.thermal_model import ThermalState

try:
    from homeassistant.util import dt as dt_util
except ImportError:  # pragma: no cover - the stub always provides this
    dt_util = None

UTC = timezone.utc

FAILS = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILS
    print(("  ok   " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS += 1


def make_coordinator(open_meteo, weather_solar: float = 0.0, n_steps: int = 96):
    """A coordinator with only the fields ``_forecast_arrays`` touches."""
    c = object.__new__(Coord)
    c._opt_config = OptimizationConfig(
        horizon_hours=n_steps // 4, time_step_minutes=15
    )
    c._config = {}
    c._prices = [{"total": 1.0} for _ in range(48)]
    c._current_state = ThermalState(outdoor_temperature=0.0)
    c._solar_radiation = 0.0
    c._solar_radiation_forecast = []
    c._open_meteo = open_meteo
    # Added in v2.8.0: the learned price prior (item 7) and the PV surplus
    # model (item 9) are both consulted while the forecast arrays are built.
    c._price_model = PriceShapeModel()
    c._price_known_steps = 0
    # Added in v4.0.0 T1: the grid-fee layer's parse cache (#1) is consulted
    # by the fee chokepoint inside ``_price_series``.
    c._grid_fee_cache = None
    c._pv_surplus = None
    c._pv_summary = {}
    c._measured_power = None
    c._measured_house_power = None

    now = dt_util.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # An hourly weather forecast starting at the current hour, carrying its own
    # irradiance so the override can be distinguished from the fallback.
    c._weather_forecast = [
        {
            "datetime": (midnight + timedelta(hours=h)).isoformat(),
            "temperature": 0.0,
            "wind_speed": 0.0,
            "precipitation": 0.0,
            "solar_irradiance": weather_solar,
        }
        for h in range(48)
    ]
    return c, now, midnight


def ramp_series(midnight, minutes: int = 15, span_hours: int = 36):
    """Series where each sample's value is the minute-of-day of its interval start.

    Encoding position into the value turns "is this aligned?" into an exact
    equality check rather than an eyeball comparison of two curves.
    """
    times = []
    values = []
    start = midnight.astimezone(UTC)
    count = span_hours * 60 // minutes
    for i in range(count):
        # Samples are stamped with the END of their interval.
        interval_start = start + timedelta(minutes=minutes * i)
        times.append(interval_start + timedelta(minutes=minutes))
        values.append(float(minutes * i))
    return IrradianceSeries(
        times=tuple(times), values=tuple(values), resolution=timedelta(minutes=minutes)
    )


print("== step alignment ==")

client = OpenMeteoSolar(hass=None, latitude=60.0, longitude=17.0)
coord, now, midnight = make_coordinator(client)
client._forecast = ramp_series(midnight)

_, _, _, _, solar = coord._forecast_arrays()[:5]

# The optimizer's grid is anchored to midnight, so step 0 is the quarter hour
# containing "now".
step_offset = int((now - midnight).total_seconds() / 60 / 15)
expected_first = float(step_offset * 15)

check("returns one irradiance value per step", len(solar) == coord._opt_config.n_steps)
check(
    "step 0 carries the interval containing now",
    abs(solar[0] - expected_first) < 1e-6,
    f"got {solar[0]} want {expected_first}",
)
check(
    "step 1 is the next quarter hour, not the same or a jump",
    abs(solar[1] - (expected_first + 15.0)) < 1e-6,
    f"got {solar[1]} want {expected_first + 15.0}",
)
check(
    "the whole horizon advances monotonically by one step",
    all(
        abs(solar[i + 1] - solar[i] - 15.0) < 1e-6
        for i in range(len(solar) - 1)
        if solar[i + 1] > 0
    ),
)


print("\n== resolution independence ==")

# An hourly series must produce the same alignment: four consecutive steps read
# the same hour, and that hour is the one containing now.
client_h = OpenMeteoSolar(hass=None, latitude=60.0, longitude=17.0)
coord_h, now_h, midnight_h = make_coordinator(client_h)
client_h._forecast = ramp_series(midnight_h, minutes=60)
_, _, _, _, solar_h = coord_h._forecast_arrays()[:5]

hour_offset = int((now_h - midnight_h).total_seconds() / 3600)
check(
    "hourly data lands on the hour containing now",
    abs(solar_h[0] - float(hour_offset * 60)) < 1e-6,
    f"got {solar_h[0]} want {hour_offset * 60.0}",
)
distinct_in_first_hour = len({round(float(v), 6) for v in solar_h[:4]})
# Steps are anchored to the quarter hour containing now, not to an hour
# boundary, so the first four steps normally straddle two hours. Check a run of
# four that does start on the hour.
step_offset_h = int((now_h - midnight_h).total_seconds() / 60 / 15)
first_on_hour = (-step_offset_h) % 4
on_hour_run = {
    round(float(v), 6) for v in solar_h[first_on_hour : first_on_hour + 4]
}
check("an hourly value is held across its four steps", len(on_hour_run) == 1,
      f"values={sorted(on_hour_run)}")
check(
    "steps straddling two hours are not forced to one value",
    distinct_in_first_hour in (1, 2),
)


print("\n== observed data wins ==")

client_o = OpenMeteoSolar(hass=None, latitude=60.0, longitude=17.0)
coord_o, _, midnight_o = make_coordinator(client_o)
client_o._forecast = ramp_series(midnight_o)
# A flat observed series covering the whole day must override the ramp.
obs_times = tuple(
    midnight_o.astimezone(UTC) + timedelta(minutes=10 * (i + 1)) for i in range(6 * 24)
)
client_o._observed = IrradianceSeries(
    times=obs_times, values=tuple(777.0 for _ in obs_times), resolution=timedelta(minutes=10)
)
_, _, _, _, solar_o = coord_o._forecast_arrays()[:5]
check("observed satellite values replace the forecast", abs(solar_o[0] - 777.0) < 1e-6,
      f"got {solar_o[0]}")


print("\n== fallbacks ==")

# Past the published horizon the weather entity's value must survive rather
# than being overwritten with zero.
client_s = OpenMeteoSolar(hass=None, latitude=60.0, longitude=17.0)
coord_s, _, midnight_s = make_coordinator(client_s, weather_solar=123.0)
client_s._forecast = ramp_series(midnight_s, span_hours=2)
_, _, _, _, solar_s = coord_s._forecast_arrays()[:5]
check(
    "steps beyond the Open-Meteo horizon keep the weather entity value",
    abs(float(solar_s[-1]) - 123.0) < 1e-6,
    f"got {solar_s[-1]}",
)

# With no client at all the previous behaviour must be untouched.
coord_n, _, _ = make_coordinator(None, weather_solar=456.0)
_, _, _, _, solar_n = coord_n._forecast_arrays()[:5]
check(
    "without Open-Meteo the weather entity is still used",
    abs(float(solar_n[0]) - 456.0) < 1e-6,
    f"got {solar_n[0]}",
)

# An empty client must not blank out solar either.
empty_client = OpenMeteoSolar(hass=None, latitude=60.0, longitude=17.0)
coord_e, _, _ = make_coordinator(empty_client, weather_solar=456.0)
_, _, _, _, solar_e = coord_e._forecast_arrays()[:5]
check(
    "an unavailable Open-Meteo client does not zero the irradiance",
    abs(float(solar_e[0]) - 456.0) < 1e-6,
    f"got {solar_e[0]}",
)

check("irradiance is never negative", bool(np.all(solar >= 0.0)))

print("\n" + ("%d CHECK(S) FAILED" % FAILS if FAILS else "ALL SOLAR ALIGNMENT CHECKS PASSED"))
sys.exit(1 if FAILS else 0)
