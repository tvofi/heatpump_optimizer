"""What the shared set-point helpers make of a curve-offset entity declared in K.

Run from the repository root:
    PYTHONPATH=tests/hastub python dev/programme/designs/generic-heat-curve-probes/k_unit_probe.py
The entity mirrors luxtronik_shi's `cfg_heating_offset` (unit K, -20..20, step 0.5).
A displace is a temperature DIFFERENCE; these helpers convert ABSOLUTE temperatures.
"""
import os
import sys
import types

sys.path.insert(0, os.getcwd())
from custom_components.heatpump_optimizer import inputs


class _State:
    def __init__(self, state, attrs):
        self.state, self.attributes = state, attrs


hass = types.SimpleNamespace(
    states={},
    config=types.SimpleNamespace(units=types.SimpleNamespace(temperature_unit="°C")),
)
EID = "number.lwdv_shi_heating_curve_offset"
hass.states[EID] = _State("-2.0", {"unit_of_measurement": "K", "min": -20, "max": 20, "step": 0.5})
print("read_setpoint            :", inputs.read_setpoint(hass, EID))
print("setpoint_range_c         :", inputs.setpoint_range_c(hass, EID))
print("quantise_setpoint_c(-2.0):", inputs.quantise_setpoint_c(hass, EID, -2.0))
print("temperature_from_c(-2, K):", inputs.temperature_from_c(-2.0, "K"))
print("setpoint_step            :", inputs.setpoint_step(hass, EID))
