#!/usr/bin/env python3
"""Reviewer probe 2 (review-2066): instantaneous metering and the dispatch's configuration.

_measured_power is the power entity's state at the tick (coordinator.py
read_power_kw), not an interval mean. So a fixed-speed pump on a duty-cycled
step reads its rating (on tick) or idle (off tick) against a commanded
duty average. A: fixed-speed 6/6, commanded d*6, ticks alternate on/off in
proportion d over 40 ticks; print folds and the resulting cop_scale.
B: the dispatch's configuration, min 3 kW correctly configured, 14 kW nameplate,
pump running at 3.0-4.0 kW with commanded == measured; and a self-modulating
case where the pump draws 3.2 kW against commanded 1.5 / 2.0 / 3.0 / 4.0 kW.
Synthetic numbers only.
"""
import sys
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.pump_power"}
STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("8.0", unit="°C"),
          "sensor.pump_power": FakeState("2200", unit="W")}
def mk(pmax, pmin):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(
        data=dict(CFG, heat_pump_max_power=pmax, heat_pump_min_power=pmin)))
    c._current_state.outdoor_temperature = 8.0
    return c
def run(c, pairs):
    s0 = c._cop_scale
    for cmd, meas in pairs:
        c._current_action = {"power": cmd, "dhw_power": 0.0}
        c._measured_power = meas
        c._learn_measured_cop()
    return int(c._cop_samples), s0, c._cop_scale
for d in (0.3, 0.5, 0.7):
    ticks = [(d * 6.0, 6.0 if (i * d) % 1 + d >= 1 or d >= 1 else 0.05) for i in range(40)]
    on = sum(1 for _, m in ticks if m > 1)
    n, s0, s1 = run(mk(6.0, 6.0), ticks)
    print(f"RESULT fixed6_instant_d{d:.1f}_folded={n}/40 on_ticks={on} cop_scale {s0:.3f}->{s1:.3f}")
n, *_ = run(mk(14.0, 3.0), [(k, k) for k in (3.0, 3.5, 4.0) for _ in range(3)])
print(f"RESULT min3_max14_running3to4_folded={n}/9")
for cmd in (1.5, 2.0, 3.0, 4.0):
    c = mk(14.0, 3.0)
    n, *_ = run(c, [(cmd, 3.2)] * 3)
    print(f"RESULT selfmod_min3_cmd{cmd:g}_meas3.2_folded={n}/3 refusal={c._measured_cop.refusal if hasattr(c, '_measured_cop') else 'n/a'}")
