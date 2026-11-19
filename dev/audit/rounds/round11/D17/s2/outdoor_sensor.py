"""D17-s2-02 -- the outdoor temperature sensor never reaches the plan while a forecast exists.

Metric: across outdoor-sensor readings {-25, -3, +10} C with the same weather forecast
(-5 C flat), the spread (max - min) of (a) the plan's step-0 outdoor temperature
(OptimizationResult.outdoor_temps[0]) and (b) the planned space-heating energy over
the horizon (sum power_schedule * 0.25 h). Key: the plan the real coordinator solves
(_update_current_state -> async_run_optimization -> _weather_series), never the
sensor's own state.
Oracle: strings.json config.step.user_sensors.data_description.outdoor_temp_entity
"A local outdoor thermometer is more accurate than the forecast for the current
hour"; docs/configuration.md:87 "A local thermometer beats the forecast for the
current hour." -> with it set, the current hour is planned at the measured value.
Null control: the no-forecast arm (coordinator._weather_forecast = []) -- there the
sensor IS the plan's outdoor series, so its spread must be > 0, proving the harness
can see the sensor reach the plan.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s2/outdoor_sensor.py [--perturb]
Expected at 92d38ecb: RESULT step0_outdoor_spread_K=0.0 ; RESULT plan_kwh_spread=0.0 ;
          RESULT null_no_forecast_step0_spread_K=35.0 ; tolerance 1e-6.
--perturb: HeatPumpOptimizerCoordinator._weather_series wrapped so the steps of the
current hour take the measured outdoor temperature (the documented behaviour, one
assignment in _weather_series). Expected: step0_outdoor_spread_K=35.0, plan_kwh_spread>0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (Linux x86_64 container).
Instrumented: custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._weather_series
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time  # noqa: E402
from unittest import mock  # noqa: E402

import rig  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402

READINGS = ("-25.0", "-3.0", "10.0")


def arm(reading, forecast=True):
    d = rig.walk("expert")  # indoor + outdoor sensor assigned on the second screen
    _, _, c = rig.build(d, states={"sensor.outdoor": reading})
    if not forecast:
        c._weather_forecast = []
    reason, res, data = rig.cycle(c)
    return res.outdoor_temps[0], sum(res.power_schedule) * 0.25, data.get("outdoor_temperature")


def measure():
    rows = [arm(r) for r in READINGS]
    for r, (o0, kwh, pub) in zip(READINGS, rows):
        print(f"sensor {r:>6}: published outdoor={pub} plan step-0 outdoor={o0} plan kWh={kwh:.3f}")
    null = [arm(r, forecast=False) for r in READINGS]
    for r, (o0, kwh, pub) in zip(READINGS, null):
        print(f"no forecast, sensor {r:>6}: plan step-0 outdoor={o0} plan kWh={kwh:.3f}")
    spread = lambda xs: max(xs) - min(xs)  # noqa: E731
    print(f"RESULT step0_outdoor_spread_K={spread([x[0] for x in rows]):.3f} K")
    print(f"RESULT plan_kwh_spread={spread([x[1] for x in rows]):.4f} kWh")
    print(f"RESULT null_no_forecast_step0_spread_K={spread([x[0] for x in null]):.3f} K")


def nowcast(orig):
    def wrapped(self, n_steps, midnight, step_offset):
        out = list(orig(self, n_steps, midnight, step_offset))
        outdoor = list(out[0])
        for i in range(min(4, len(outdoor))):  # the current hour's quarter steps
            outdoor[i] = float(self._ctx._current_state.outdoor_temperature)
        out[0] = outdoor
        return tuple(out)
    return wrapped


if __name__ == "__main__":
    t0 = time.time()
    C = cmod.HeatPumpOptimizerCoordinator
    if "--perturb" in sys.argv:
        with mock.patch.object(C, "_weather_series", nowcast(C._weather_series)):
            measure()
    else:
        measure()
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print("RESULT thread_factor=1.00 (counts only; single-thread pin)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
