import asyncio, sys
from types import SimpleNamespace
from datetime import datetime, timezone
sys.path.insert(0,'tests')
from harness import FakeHass, FakeState
from custom_components.heatpump_optimizer import pump_arbiter as pa, const
from custom_components.heatpump_optimizer.pump_arbiter import ArbiterInputs
def run(mode):
    hass=FakeHass({"number.dhw":FakeState("45",unit="°C"),"number.sp":FakeState("30",unit="°C")})
    calls=[]
    async def ac(domain, svc, data, blocking=False, **k): calls.append((domain,svc,data))
    hass.services.async_call=ac
    cfg={const.CONF_DHW_SETPOINT_ENTITY:"number.dhw", const.CONF_SPACE_SETPOINT_ENTITY:"number.sp", const.CONF_PUMP_DUTY_MODE:mode}
    inp=ArbiterInputs(hass=hass,config=cfg,mode="auto",plan=None,plan_stale=False,entry_released=False,state=__import__("unittest.mock").mock.MagicMock(),thermal=None,params=__import__("unittest.mock").mock.MagicMock(),action=None,measured_power_kw=None,disinfecting=False)
    class C: pass
    coord=C(); coord.hass=hass; coord.entry=SimpleNamespace(entry_id="x"); coord.arbiter_inputs=lambda:inp
    held=pa.state_for(coord)
    now=datetime(2026,1,15,12,tzinfo=timezone.utc)
    try: asyncio.run(pa._arbitrate(coord,held,inp,mode,now))
    except Exception as e: print("exc",type(e).__name__,e)
    return calls, dict(held.written)
for m in ("observe","control"): print(m, run(m))
