"""Reviewer's own instrument (not the finder's): water_heater DHW slot read/range/step/write at a tree."""
import asyncio, sys, types
sys.path[:0] = [sys.argv[1], sys.argv[1] + "/tests/hastub"]
from custom_components.heatpump_optimizer import inputs as I
class S:
    def __init__(s, st, a): s.state, s.attributes = st, a
class Svc:
    def __init__(s): s.calls = []
    async def async_call(s, d, sv, data, blocking=False): s.calls.append((d, sv, data))
def hass(unit, st):
    h = types.SimpleNamespace(states=types.SimpleNamespace(get=lambda e: st.get(e)), services=Svc(),
        config=types.SimpleNamespace(units=types.SimpleNamespace(temperature_unit=unit)))
    return h
for unit, a in (("°C", {"temperature": 62.0, "min_temp": 30.0, "max_temp": 65.0, "target_temp_step": 0.5}),
                ("°F", {"temperature": 140.0, "min_temp": 86.0, "max_temp": 149.0, "target_temp_step": 1.0})):
    for state in ("heat_pump", "off", "eco"):
        h = hass(unit, {"water_heater.dhw": S(state, a)})
        e = "water_heater.dhw"
        ok = asyncio.run(I.write_setpoint_c(h, e, 52.3))
        print(f"RESULT unit={unit} state={state} read={I.read_setpoint(h, e)} range={I.setpoint_range_c(h, e)} "
              f"step={I.setpoint_step(h, e)} q50.2={I.quantise_setpoint_c(h, e, 50.2)} write52.3={ok} calls={h.services.calls}")
# unavailable
h = hass("°C", {"water_heater.dhw": S("unavailable", {"temperature": 62.0})})
print("RESULT unavailable read=", I.read_setpoint(h, "water_heater.dhw"))
