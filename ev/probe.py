"""Reviewer's probe: desired() through tests/block_duty.py helpers (finder's oracle)."""
import sys
from dataclasses import replace
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import block_duty as bd
from heatpump_optimizer import pump_arbiter as arb, setpoint_check
from heatpump_optimizer.thermal_model import ThermalParameters
from harness import FakeHass, FakeState
def snap(action=None, dis=False, conf=55.0, cyc=True, temp=60.0, attrs=None, reading=55.0):
    s = bd._snap(config={"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"},
        params=ThermalParameters(dhw_setpoint=conf, dhw_legionella_temp=temp, dhw_legionella_enabled=cyc, dhw_min_temp=40.0),
        action=action, disinfecting=dis)
    return replace(s, hass=FakeHass({"number.dhw": FakeState(str(reading), attributes=attrs or {"min":30,"max":65,"step":1})}))
def w(s, d): return arb.desired(bd._Coord(s), s, d, bd.NOW).dhw_setpoint
L = {"dhw_reason": "legionella"}
print("RESULT booked_legionella_dhw", w(snap(action=L), "dhw"))
print("RESULT disinfecting_both", w(snap(dis=True), "both"))
print("RESULT ordinary_dhw", w(snap(), "dhw"))
print("RESULT everyday62_disinfecting", w(snap(dis=True, conf=62.0), "dhw"))
print("RESULT everyday62_booked", w(snap(action=L, conf=62.0), "dhw"))
print("RESULT offstep_60.3_step0.5", w(snap(dis=True, temp=60.3, attrs={"min":30,"max":65,"step":0.5}), "dhw"))
print("RESULT offstep_59.6_step1", w(snap(dis=True, temp=59.6), "dhw"))
print("RESULT above_range_max58", w(snap(dis=True, attrs={"min":30,"max":58,"step":1}), "dhw"))
print("RESULT max_offstep_59.5_step1", w(snap(dis=True, attrs={"min":30,"max":59.5,"step":1}), "dhw"))
for d in (None, "idle", "space", "dhw", "both"):
    print(f"RESULT row_{d}_booked", w(snap(action=L), d), "held", w(snap(dis=True), d), "disabled_held", w(snap(dis=True, cyc=False), d))
def repair(s, written):
    c = bd._Coord(s)
    if written is not None: arb.state_for(c).written["dhw_setpoint"] = (written, bd.NOW)
    setpoint_check._dhw(s.hass, s.config, s.params, lambda p: arb.dhw_gated(c, p))
    r = [i for i in getattr(s.hass, "issues", []) if i[1] == setpoint_check.ISSUE_DHW]
    return r[0][2]["data"]["value"] if r else None
print("RESULT repair_arbiter_wrote55_read55", repair(snap(), 55.0))
print("RESULT repair_arbiter_wrote30gate_read30", repair(snap(reading=30.0), 30.0))
print("RESULT repair_person50_arbiter55", repair(snap(reading=50.0), 55.0))
print("RESULT repair_nowrite_read55", repair(snap(), None))
print("RESULT repair_disabled_nowrite_read45", repair(snap(reading=45.0, cyc=False), None))
print("RESULT repair_disabled_wrote55", repair(snap(cyc=False), 55.0))
