import sys, asyncio
sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C
D={"tibber_token":"x","weather_entity":"weather.home"}
e=FakeEntry(data=dict(D),entry_id="res")
async def main():
    a=C(FakeHass(),e); await a._async_load_accuracy()
    a._comfort_learner.overrides=7; a._mode="economy"; await a._async_save_accuracy()
    b=C(FakeHass(),e)  # restart; the load is spawned, not yet landed
    await b.async_set_mode("off", refresh=False)  # a tap before it lands
    await b._async_load_accuracy()
    c=C(FakeHass(),e); await c._async_load_accuracy()
    print("after: overrides", c._comfort_learner.overrides, "mode", c._mode)
asyncio.run(main())
