import sys,types,asyncio;sys.path[:0]=["tests","."]
from harness import FakeHass,FakeState
from custom_components.heatpump_optimizer import pump_arbiter
from custom_components.heatpump_optimizer.inputs import temperature_c
to=lambda c,u:c*9/5+32 if u=="°F" else c
bad=0;n=0
for c in [5.0,21.0,35.0,50.0,60.0]:
  for unit in ("°F","°C"):
    ent="climate.x";st=FakeState("heat",attributes={"temperature":to(c-3,unit),"min_temp":to(5,unit),"max_temp":to(65,unit)})
    h=FakeHass({ent:st});h.config.units=types.SimpleNamespace(temperature_unit=unit)
    co=type("C",(),{})();co.hass=h;co.entry=types.SimpleNamespace(entry_id=f"{c}{unit}")
    asyncio.run(pump_arbiter._write(co,types.SimpleNamespace(hass=h,config={"space_setpoint_entity":ent}),"space_setpoint",c,__import__("datetime").datetime(2026,1,1,tzinfo=__import__("datetime").timezone.utc)))
    cs=[x for x in h.services.calls if x[2] and x[2].get("entity_id")==ent]
    if not cs: print("nocall",unit,c,h.services.calls); continue
    sent=cs[-1][2]["temperature"];got=temperature_c(sent,unit);n+=1
    if abs(got-c)>0.5: bad+=1
    print(unit,c,sent,round(got,2))
print("IND bad",bad,"of",n)
