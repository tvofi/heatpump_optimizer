import sys, asyncio; sys.path.insert(0,'tests')
import guard_pins as g
params = g.ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=65.0, dhw_legionella_enabled=True, dhw_enabled=True)
hass = g.FakeHass({"number.dhw": g.FakeState("50", attributes={"min": 30, "max": 60, "step": 1})})
guard = g.LegionellaGuard(hass, "probe", lambda: params, {"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"},
    action=lambda: {}, disinfect=g.DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None), dhw_blocked=lambda: False)
asyncio.run(guard.async_observe(None, None))
guard.raise_unreachable_issue(60.0, 65.0)
print("entity max 60, step 1, disinfection 65: standing =", sorted({i[1] for i in getattr(hass, "issues", [])}))
