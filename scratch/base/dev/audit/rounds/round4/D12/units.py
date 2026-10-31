"""D12-H2 -- the same physical plant, expressed in the units Home Assistant
hands a household that is not on the metric unit system.

METRIC (one line): for one physical plant driven twice -- once with every
sensor state in °C/kWh, once with the identical plant expressed in °F/Wh with
the matching ``unit_of_measurement`` attribute -- the number of guarded inputs
whose value the coordinator adopts unconverted, and the resulting published
indoor temperature and planned heating energy.

RUN (from the repository root):

    PYTHONPATH=tests/hastub:tools/audit/round4/D12 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D12/units.py

EXPECTED at the baseline (counts and published values -- immune to box load):
  imperial_inputs_misread=10, celsius_inputs_misread=0 (the null control),
  imperial_indoor_temperature_c=70.5, celsius_indoor_temperature_c=21.4,
  imperial_plan_kwh=0.0, celsius_plan_kwh=4.752.  Tolerance exact on the
  counts, ±0.1 on the °C.  --convert takes misread 10 -> 1 and plan_kwh
  0.0 -> 4.198; --shrink takes misread 10 -> 4.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: MacBookAir10,1 (8-core Apple M1, 8 GB), macOS 25.6.0
INSTRUMENTED SYMBOL: heatpump_optimizer.inputs:InputReader.read -- wrapped, so
  every guarded read is recorded with the entity's own
  ``unit_of_measurement`` and the value the caller received.
PERTURBATION: --convert installs a one-line °F->°C conversion in
  ``InputReader.read``; imperial_inputs_misread must fall to 0 and
  imperial_indoor_temperature_c must return to the metric arm's value (the
  residual 1 is the Wh energy meter, a second unit family the one-line fix
  does not reach).  --shrink drops DHW / wood / PV / one zone / four sensors:
  the count must move with the plant.
NULL CONTROL: the °C arm of the same harness, printed beside it.
"""
from __future__ import annotations

import sys

import d12lib
import cells as cellmod
from harness import FakeState

from heatpump_optimizer import inputs as inputs_mod

# Units Home Assistant can hand an integration for each guarded read, and the
# factor/offset that would take them to what the model assumes.  Only the
# temperature row is unhandled in production; the power row IS handled
# (``read_power_kw`` / ``const.POWER_UNIT_TO_KW``) and is the in-tree proof
# that the conversion problem is understood.
TEMPERATURE_UNITS = {"°C", "C"}
ENERGY_UNITS = {"kWh"}


def f_of_c(c):
    return round(c * 9.0 / 5.0 + 32.0, 1)


#: The brief's mandated shrink: one omitted sensor, DHW dropped, wood
#: dropped, PV dropped, one zone removed -- all five at once.
SHRINK_DROP_CONFIG = (
    "dhw_tank_volume", "dhw_setpoint", "dhw_min_temperature", "dhw_windows",
    "wood_tank_top_entity", "wood_tank_volume", "mixing_valve_mode",
    "buffer_tank_volume", "buffer_max_temperature",
    "pv_enabled", "pv_peak_kw", "pv_export_price",
    "upper_floor_thermal_mass", "lower_floor_thermal_mass",
    "upper_floor_heat_loss", "lower_floor_heat_loss",
    "dhw_temp_entity", "buffer_tank_temp_entity", "lower_floor_temp_entity",
    "pv_production_entity", "mixing_valve_target_entity",
)


def _arm(imperial: bool, convert: bool, shrink: bool = False):
    """Drive the fully mapped plant with every sensor in one unit system."""
    cfg, states = cellmod.fully_mapped()
    if shrink:
        for key in SHRINK_DROP_CONFIG:
            value = cfg.pop(key, None)
            if isinstance(value, str):
                states.pop(value, None)
        states.pop("sensor.wood_top", None)
    if imperial:
        new = {}
        for entity_id, state in states.items():
            unit = state.attributes.get("unit_of_measurement")
            if unit in TEMPERATURE_UNITS:
                new[entity_id] = FakeState(str(f_of_c(float(state.state))),
                                           unit="°F")
            elif unit in ENERGY_UNITS:
                new[entity_id] = FakeState(str(float(state.state) * 1000.0),
                                           unit="Wh")
            else:
                new[entity_id] = state
        states = new

    seen = []
    real_read = inputs_mod.InputReader.read

    def spy(self, key, **kw):
        reading = real_read(self, key, **kw)
        state = self.hass.states.get(reading.entity_id) if reading.entity_id else None
        unit = None
        if state is not None:
            unit = getattr(state, "attributes", {}).get("unit_of_measurement")
        if reading.value is not None:
            seen.append((key, unit, reading.value))
        return reading

    if convert:
        # The PERTURBATION: the one-line conversion production does not have.
        def converted(self, key, **kw):
            reading = spy(self, key, **kw)
            state = self.hass.states.get(reading.entity_id) if reading.entity_id else None
            unit = getattr(state, "attributes", {}).get("unit_of_measurement") if state else None
            if reading.value is not None and unit == "°F":
                reading.value = (reading.value - 32.0) * 5.0 / 9.0
                seen[-1] = (key, "°C", reading.value)
            return reading
        inputs_mod.InputReader.read = converted
    else:
        inputs_mod.InputReader.read = spy
    try:
        r = d12lib.drive_cell("units", cfg, states)
    finally:
        inputs_mod.InputReader.read = real_read

    misread = [
        (key, unit, value) for key, unit, value in seen
        if unit is not None and unit not in TEMPERATURE_UNITS | ENERGY_UNITS
        and unit not in ("W", "kW", "MW", "mW", "%", "W/m²", "SEK/kWh", "Hz")
    ]
    data = r["data"] or {}
    plan_kwh = sum(
        float(s.get("power", 0.0) or 0.0) * 0.25
        for s in (data.get("schedule") or [])
    )
    return r, seen, misread, data, plan_kwh


def main(argv):
    convert = "--convert" in argv
    shrink = "--shrink" in argv

    for label, imperial in (("celsius", False), ("imperial", True)):
        r, seen, misread, data, plan_kwh = _arm(
            imperial, convert and imperial, shrink)
        print(f"RESULT {label}_setup_ok={int(r['ok'])} count")
        print(f"RESULT {label}_inputs_guarded={len(seen)} count")
        print(f"RESULT {label}_inputs_misread={len(misread)} count")
        print(f"RESULT {label}_indoor_temperature_c="
              f"{data.get('indoor_temperature')} degC")
        print(f"RESULT {label}_dhw_temperature_c={data.get('dhw_temperature')} degC")
        print(f"RESULT {label}_outdoor_temperature_c="
              f"{data.get('outdoor_temperature')} degC")
        print(f"RESULT {label}_plan_kwh={round(plan_kwh, 3)} kWh")
        print(f"RESULT {label}_plan_steps={len(data.get('schedule') or [])} count")
        if misread:
            print(f"  misread inputs ({label}):")
            for key, unit, value in sorted(set(misread)):
                print(f"    {key:32s} unit={unit!r:8s} adopted={value}")
        print()

    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={d12lib.load1()}")
    print(f"RESULT swapins={d12lib.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
