import asyncio, sys
from harness import FakeHass, FakeState
from heatpump_optimizer import inputs as I
def hass(eid, attrs, unit=None, state="40"):
    return FakeHass({eid: FakeState(state, unit=unit, attributes=attrs)})
cases = [
 ("number.f", {"min": 44.6, "max": 131.9, "unit_of_measurement": "°F"}, "°F"),
 ("number.c05", {"min": 20, "max": 55.3, "step": 0.5}, "°C"),
 ("number.c01", {"min": 20, "max": 55.33, "step": 0.1}, "°C"),
 ("number.c1", {"min": 20.4, "max": 55.6}, "°C"),
 ("climate.f", {"min_temp": 44.6, "max_temp": 131.9, "target_temp_step": 1, "temperature": 70, "unit_of_measurement":"°F"}, "°F"),
 ("number.narrow", {"min": 25.3, "max": 25.7}, "°C"),
]
for eid, attrs, unit in cases:
    h = hass(eid, attrs, unit)
    lo, hi = I.setpoint_range_c(h, eid)
    for v in (lo, hi, 23.37, 53.0, 52.5):
        for r in ("nearest","up","down"):
            q = I.quantise_setpoint_c(h, eid, v, rounding=r, lo_c=lo, hi_c=hi)
            ok = (lo is None or q >= lo - 1e-9) and (hi is None or q <= hi + 1e-9)
            if not ok: print("OUT-OF-RANGE", eid, v, r, q, (lo, hi))
    calls=[]
    class Svc:
        async def async_call(self,*a,**k): calls.append(a)
    h.services = Svc()
    asyncio.run(I.write_setpoint_c(h, eid, 23.37)); asyncio.run(I.write_setpoint_c(h, eid, 53.0))
    print(eid, "range_c", (lo, hi), "writes 23.37C,53C ->", [c[2] for c in calls])
# repair path: write_setpoint with the DHW floor in degF, as setpoint_check computes it
for floor in (48.0, 53.0, 58.0, 60.0, 63.0):
    h = hass("number.dhw", {"unit_of_measurement": "°F"}, "°F", state="100")
    calls=[]
    class Svc:
        async def async_call(self,*a,**k): calls.append(a)
    h.services=Svc()
    value = round(I.temperature_from_c(floor, "°F"), 1)
    asyncio.run(I.write_setpoint(h, "number.dhw", value))
    sent = calls[0][2]["value"]; back = (sent-32)*5/9
    print(f"repair floor {floor}C -> value {value}F sent {sent}F = {back:.2f}C", "BELOW FLOOR-0.25" if back < floor-0.25 else "ok")
