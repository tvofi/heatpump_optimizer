#!/usr/bin/env python3
"""Reviewer's own probe (review-2066), not the finder's or the fixer's.

Null control the dispatch asked for: a pump whose modulation floor is
CORRECTLY configured. Synthetic numbers only. Drives the real coordinator's
_learn_measured_cop exactly as tools/audit/harnesses/cop_duty_floor.py does
(measured == commanded, outdoor 8 C, outside the frost band), over duty-cycled
and running intervals. Duty d at running power P books d*P (the plan's
duty-cycle reading) and the meter averages d*P + (1-d)*0.05 kW idle.
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

def folds(p_max, p_min, commanded, measured, cycles=3):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(
        data=dict(CFG, heat_pump_max_power=p_max, heat_pump_min_power=p_min)))
    c._current_action = {"power": commanded, "dhw_power": 0.0}
    c._measured_power = measured
    c._current_state.outdoor_temperature = 8.0
    for _ in range(cycles):
        c._learn_measured_cop()
    return int(c._cop_samples), c._thermal_params.flow_lift_power_floor_kw

# (label, p_max, p_min, running power P the pump really runs at)
PUMPS = [("fixed_speed_6", 6.0, 6.0, 6.0),
         ("fixed_speed_9", 9.0, 9.0, 9.0),
         ("mod_2to6", 6.0, 2.0, 2.0),
         ("mod_3to8", 8.0, 3.0, 3.0)]
DUTIES = (0.3, 0.5, 0.7, 0.9, 1.0)
for label, pmax, pmin, P in PUMPS:
    tot = 0
    cells = []
    for d in DUTIES:
        cmd = d * P
        meas = d * P + (1 - d) * 0.05
        n, floor = folds(pmax, pmin, cmd, meas)
        tot += n
        cells.append(f"d{d:.1f}({meas:.2f}kW):{n}")
    print(f"  {label} floor={floor:.2f} " + " ".join(cells))
    print(f"RESULT {label}_duty_folded={tot}/{3*len(DUTIES)}")
    # running above the floor across the band (modulating only)
    if pmax > pmin:
        run = [pmin, (pmin + pmax) / 2, pmax]
        rn = sum(folds(pmax, pmin, k, k)[0] for k in run)
        print(f"RESULT {label}_running_folded={rn}/{3*len(run)}")
