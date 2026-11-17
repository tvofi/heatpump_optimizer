import sys, traceback, asyncio
sys.path.insert(0, "dev/audit/rounds/round11/D1/s2")
import d1s2_lib as L
import config_fuzz as CF
from datetime import timedelta

CASES = [("dhw_tank_volume", "abc"), ("min_temperature", ""), ("max_temperature", "abc"),
         ("target_temperature", None), ("indoor_temp_entity", ["sensor.x"])]


async def go(k, v):
    d = dict(CF.HEALTHY)
    d[k] = v
    hass = L.SchedHass(L.base_states())
    entry = L.FakeEntry(data=d)
    try:
        coord = L.HeatPumpOptimizerCoordinator(hass, entry)
    except Exception:
        print("BUILD", k, repr(v))
        traceback.print_exc(limit=-3)
        return
    await L.drain(hass)
    try:
        await coord._async_update_data()
        print("OK", k)
    except Exception as e:
        print("CYCLE", k, repr(v))
        c = e.__cause__ or e.__context__ or e
        traceback.print_exception(type(c), c, c.__traceback__, limit=-3)

for k, v in CASES:
    L.reset_globals()
    ps = L.patches() + L.price_patches()
    for p in ps:
        p.start()
    L.dtu.freeze(L.T0)
    asyncio.run(go(k, v))
    for p in ps:
        p.stop()
