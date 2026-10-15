"""Reviewer's adapter (mine, not the finder's) of catch-up l2_bounded_climate.py
(5ff600f1) for the head's _bounded(inp, slot, value, floor) signature. Same
states, same 4 values, same range, same reach arm; plus a degF-instance arm
(climate range 44.6..122 degF == 7..50 degC) and a degF reach arm."""
from types import SimpleNamespace
from datetime import datetime, timezone
from heatpump_optimizer import pump_arbiter as pa

LO, HI = 7.0, 50.0
VALUES = (3.0, 10.0, 55.0, 70.0)
CLIMATE = SimpleNamespace(state="heat", attributes={"min_temp": LO, "max_temp": HI, "temperature": 45})
CLIMATE_F = SimpleNamespace(state="heat", attributes={"min_temp": 44.6, "max_temp": 122.0, "temperature": 113})
NUMBER = SimpleNamespace(state="45", attributes={"min": LO, "max": HI, "unit_of_measurement": "°C"})

def hass_for(ent, st, unit=None):
    h = SimpleNamespace(states=SimpleNamespace(get=lambda e: st if e == ent else None))
    if unit:
        h.config = SimpleNamespace(units=SimpleNamespace(temperature_unit=unit))
    return h

def count(ent, st, unit=None):
    cfg = {"dhw_setpoint_entity": ent, "heat_pump_mode_entity": None, "space_setpoint_entity": None}
    inp = SimpleNamespace(config=cfg, hass=hass_for(ent, st, unit))
    out = [pa._bounded(inp, "dhw_setpoint", v) for v in VALUES]
    return sum(1 for o in out if o < LO - 1e-9 or o > HI + 1e-9), out

for name, ent, st, unit in (("arm_climate", "climate.dhw", CLIMATE, None),
                            ("arm_climate_degC_instance", "climate.dhw", CLIMATE, "°C"),
                            ("arm_climate_degF_instance", "climate.dhw", CLIMATE_F, "°F"),
                            ("null_number", "number.dhw", NUMBER, None),
                            ("null_number_on_degF_instance", "number.dhw", NUMBER, "°F")):
    n, out = count(ent, st, unit)
    print(f"RESULT head {name} out_of_range={n} of {len(VALUES)} returned={out}")

now = datetime(2026, 10, 15, 12, tzinfo=timezone.utc)
for label, st, unit in (("reach_desired_dhw_slot_climate", CLIMATE, None),
                        ("reach_desired_dhw_slot_climate_degF", CLIMATE_F, "°F")):
    cfg = {"dhw_setpoint_entity": "climate.dhw", "heat_pump_mode_entity": None, "space_setpoint_entity": None}
    inp = SimpleNamespace(config=cfg, hass=hass_for("climate.dhw", st, unit),
                          params=SimpleNamespace(dhw_setpoint=55.0), plan=None, disinfecting=False)
    cmd = pa.desired(None, inp, "dhw", now)
    print(f"RESULT head {label} command.dhw={cmd.dhw_setpoint} outside_range={int(cmd.dhw_setpoint > HI)}")
