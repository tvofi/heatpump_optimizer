"""R10-NIGHT-FOLDS companion: does each heat-loss fold take the dark only?

The sweep's enumerator (`dev/audit/rounds/round10/D14/sweep-N-confounded-learner/
enumerate.py`) prices the class with re-implementations of the learners and a
fixture written before `AccuracySample` carried irradiance, so it reads the same
on this tree as on the baseline. This applies the tree's own rule to the same
inputs, through the production symbols.

Metric (one line each):
  house.sunlit.samples / house.dark.samples -- intervals the house learner folded
  lower.sunlit.samples / lower.dark.samples -- the same for the lower-floor split
  refit.sunlit.pairs / refit.dark.pairs     -- pairs the drift refit admitted
  gains.unconverged.rel_dev                 -- profile's max |g-g0|/g0 after 8
      dark intervals whose only error is a heat-loss level (+10 %), while that
      level is still unidentified (the coupling the RCA names)
  gains.converged.rel_dev                   -- the same drive at a converged
      level with no level error and a genuine evening gain (the positive arm)

Command (tree root):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_night_folds_learners.py

Expected at the fix's head: sunlit samples 0 on house and lower, dark samples
> 0 on both, refit sunlit pairs 0 and dark pairs 192, gains.unconverged 0.0000,
gains.converged > 0.05. At the baseline: sunlit samples > 0 on both, refit
sunlit pairs 192, gains.unconverged ~1.0.

Null control: the dark arm of every pair reads the same at both ends.
Perturbation: the sunlit arm -- set the interval's irradiance to 600 W/m2 and
the fold must stop, or the harness is measuring nothing.
"""
import asyncio
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import homeassistant.util.dt as dt_util  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer.accuracy import AccuracySample, heat_loss_refit  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HOUSE_LOSS_MAX_RESIDUAL,
    HOUSE_LOSS_MIN_DELTA,
    HeatPumpOptimizerCoordinator as Coord,
)
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402

UTC = timezone.utc
T0 = datetime(2026, 1, 15, 7, 0, tzinfo=UTC)
METER = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-5.0", unit="°C"),
}


def coord(**extra):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **extra,
    }
    return Coord(FakeHass(dict(METER)), FakeEntry(data=cfg))


def drive_house(c, residual, n, sun, start=T0):
    """Replay ``n`` half-hour intervals of one residual through the learner."""
    c._current_state.room_temperature = 20.0
    c._current_state.outdoor_temperature = 0.0
    c._current_action = {"power": 2.0}
    c._current_weather = lambda: (0.0, 0.0)
    observed = c._current_state.room_temperature
    real_now = dt_util.now
    c._thermal_model.simulate_step = (
        lambda prev, power, outdoor, **kw: replace(
            prev, room_temperature=observed - residual
        )
    )
    try:
        for i in range(n + 1):
            c._current_state.solar_radiation = float(sun)
            dt_util.now = lambda i=i: start + timedelta(minutes=30 * i)
            asyncio.run(c._async_learn_house_heat_loss())
    finally:
        dt_util.now = real_now


def drive_lower(c, observed_lower, sun):
    base = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.0, slab_temperature=27.0,
        outdoor_temperature=-5.0, solar_radiation=float(sun),
    )
    c._last_house_sample = base
    c._last_house_sample_time = dt_util.now() - timedelta(hours=0.5)
    c._current_state = replace(base, lower_floor_temperature=observed_lower)
    c._current_action = {"power": 2.0}
    asyncio.run(c._async_learn_lower_floor_loss())
    return c._lower_floor_loss_samples


def two_zone():
    return coord(
        upper_floor_thermal_mass=3.0, lower_floor_thermal_mass=8.0,
        lower_floor_temp_entity="sensor.lower",
    )


try:  # the field the fix adds; a baseline tree has no such field
    AccuracySample(when=T0, solar_radiation=0.0)
    SOLAR_FIELD = True
except TypeError:
    SOLAR_FIELD = False


def refit(solar):
    extra = {"solar_radiation": solar} if SOLAR_FIELD else {}
    rows = [
        AccuracySample(
            when=T0 + timedelta(hours=0.5 * i), predicted_temp=21.0,
            actual_temp=20.97, outdoor_temp=-4.0, **extra,
        )
        for i in range(1, 193)
    ]
    return heat_loss_refit(
        rows, current_scale=1.0, base_u=0.15, capacity=10.0, dt_hours=0.5,
        min_delta=HOUSE_LOSS_MIN_DELTA, max_residual=HOUSE_LOSS_MAX_RESIDUAL,
        settle=timedelta(0), since=None,
    )


def gains_profile(sun, samples, residual):
    """The #53 profile after eight dark intervals off the house learner."""
    c = coord(internal_gains_learning_enabled=True)
    c._house_heat_loss_samples = samples
    drive_house(c, residual, 8, sun=sun)
    g0 = float(c._thermal_params.internal_gains)
    prof = c._internal_gains_profile or [g0] * 24
    return max(abs(g - g0) for g in prof) / g0


house_sun = coord()
drive_house(house_sun, -0.3, 8, sun=600.0)
house_dark = coord()
drive_house(house_dark, -0.3, 8, sun=0.0)
print(f"RESULT house.sunlit.samples={house_sun._house_heat_loss_samples}")
print(f"RESULT house.dark.samples={house_dark._house_heat_loss_samples}")

low_sun = drive_lower(two_zone(), 19.6, sun=600.0)
low_dark = drive_lower(two_zone(), 19.6, sun=0.0)
print(f"RESULT lower.sunlit.samples={low_sun}")
print(f"RESULT lower.dark.samples={low_dark}")

r_sun, r_dark = refit(600.0), refit(0.0)
print(f"RESULT refit.sunlit.pairs={r_sun['pairs']}")
print(f"RESULT refit.dark.pairs={r_dark['pairs']}")

# A heat-loss level 10 % low on a C=10 kWh/K house over one half-hour is a
# residual of -0.10*0.15*dT*0.5/10 per K of dT; this drive holds dT at 20 K.
level_residual = -0.10 * 0.15 * 20.0 * 0.5 / 10.0
print("RESULT gains.unconverged.rel_dev=%.4f" % gains_profile(0.0, 0, level_residual))
print("RESULT gains.converged.rel_dev=%.4f" % gains_profile(0.0, 400, 0.3))
