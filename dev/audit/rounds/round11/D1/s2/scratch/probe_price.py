import os, sys
sys.path.insert(0, "dev/audit/rounds/round11/D1/s2")
import d1s2_lib as L
import asyncio, aiohttp
from datetime import timedelta
async def main(exc):
    hass = L.SchedHass(L.base_states())
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config()))
    await L.drain(hass)
    d1 = await coord._async_update_data(); await L.drain(hass)
    print("c1 ok", d1.get("current_price"), d1.get("plan_stale"), d1.get("prices_available"))
    L.PRICE_CALLS.update(raise_from=2, exc=exc)
    for i in (2,3):
        L.dtu.freeze(L.T0 + timedelta(minutes=15*(i-1)))
        m = L.mark()
        try:
            d2 = await coord._async_update_data()
            print(f"c{i} ok", d2.get("current_price"), d2.get("plan_stale"), d2.get("prices_available"), d2.get("plan_age_minutes"), d2.get("optimization_status"))
        except Exception as e:
            print(f"c{i} raised", type(e).__name__, e)
        await L.drain(hass)
        for r in L.since(m): print("  LOG", L.template(r)[:200])
for exc in (aiohttp.ClientError("boom"), RuntimeError("x"), TimeoutError()):
    L.reset_globals()
    ps = L.patches() + L.price_patches()
    for p in ps: p.start()
    L.dtu.freeze(L.T0)
    print("==", type(exc).__name__)
    asyncio.run(main(exc))
    for p in ps: p.stop()
