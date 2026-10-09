#!/usr/bin/env python3
"""Reviewer probe 5 (review-2066 round 2): a self-setting pump on a day whose ask varies slowly.

Synthetic only. 14 kW nameplate, 1 kW floor (the round-1 probe's install),
true COP equals the model's (right scale 1.000). The pump draws 2.2 kW +-3 %
whatever is asked. 96 ticks (one day at a 15-minute interval). Ask shapes:
hourly_steps: one level per hour (4 ticks) from 1.0-2.0 kW, seeded;
three_hour_steps: one level per 3 h (12 ticks); flat_day: 1.5 kW +-2 % all day.
"""
import sys, random
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.pump_power"}
STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("8.0", unit="°C"),
          "sensor.pump_power": FakeState("2200", unit="W")}
def go(pairs):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(
        data=dict(CFG, heat_pump_max_power=14.0, heat_pump_min_power=1.0)))
    c._current_state.outdoor_temperature = 8.0
    for cmd, meas in pairs:
        c._current_action = {"power": cmd, "dhw_power": 0.0}
        c._measured_power = meas
        c._learn_measured_cop()
    return c._cop_samples, c._cop_scale
for name, block in (("hourly_steps", 4), ("three_hour_steps", 12), ("flat_day", 96)):
    rng = random.Random(7)
    asks = []
    while len(asks) < 96:
        lvl = 1.5 if block == 96 else rng.uniform(1.0, 2.0)
        asks += [lvl * rng.uniform(0.98, 1.02) for _ in range(block)]
    pairs = [(a, 2.2 * rng.uniform(0.97, 1.03)) for a in asks[:96]]
    n, s = go(pairs)
    print(f"RESULT selfset_{name}_folded={n}/96 cop_scale={s:.3f}")
