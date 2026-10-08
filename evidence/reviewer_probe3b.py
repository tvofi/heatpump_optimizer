#!/usr/bin/env python3
"""Reviewer probe 3 (review-2066): a self-modulating pump whose draw does not follow the ask.

Synthetic: 14 kW nameplate, 1.0 kW modulation floor, true COP == the model's
(so the right cop_scale stays 1.0). The plan asks a level the pump ignores
(DESIGN.md A4's independent case): asked cycles 1.0..2.0 kW, the meter reads
a draw cycling 1.9..2.55 kW independently. 96 ticks. Print folds and the
learned cop_scale. Also the honest case (draw == ask) for contrast.
"""
import sys, itertools
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.pump_power"}
STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("8.0", unit="°C"),
          "sensor.pump_power": FakeState("2200", unit="W")}
PMAX = float(sys.argv[1])
def go(pairs):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(
        data=dict(CFG, heat_pump_max_power=PMAX, heat_pump_min_power=1.0)))
    c._current_state.outdoor_temperature = 8.0
    for cmd, meas in pairs:
        c._current_action = {"power": cmd, "dhw_power": 0.0}
        c._measured_power = meas
        c._learn_measured_cop()
    return int(c._cop_samples), c._cop_scale
asked = [1.0, 1.25, 1.5, 1.75, 2.0]
drawn = [1.9, 2.2, 2.55]
indep = list(zip(itertools.islice(itertools.cycle(asked), 96), itertools.islice(itertools.cycle(drawn), 96)))
n, s = go(indep)
print(f"RESULT pmax{PMAX:g}_selfmod_independent_folded={n}/96 cop_scale={s:.3f}")
n, s = go([(d, d) for d in itertools.islice(itertools.cycle(drawn), 96)])
print(f"RESULT pmax{PMAX:g}_honest_tracking_folded={n}/96 cop_scale={s:.3f}")
