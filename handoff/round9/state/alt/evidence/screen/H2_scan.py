"""H2 scan: look for a realistic input where the configured vs effective band flips the quiet-period verdict."""
import asyncio
import rig, H2
from heatpump_optimizer.comfort_learning import ComfortLearner

async def one(temp, mode, indoor, amp):
    c = rig.make(f"scan", extra={"comfort_learning_enabled": True})
    c.hass.states.set("sensor.indoor", rig.FakeState(str(indoor), unit="°C"))
    c.hass.states.set("sensor.outdoor", rig.FakeState(str(temp), unit="°C"))
    c._weather_forecast = rig.weather(temp=temp)
    c._prices = [dict(p, total=round(0.8 + amp * ((i % 12) / 12.0 - 0.5), 4)) for i, p in enumerate(rig.prices())]
    if mode != "auto":
        await c.async_set_mode(mode, refresh=False)
    H2.CAP.clear()
    await c.async_run_optimization()
    return H2.CAP[0] if H2.CAP else None

async def main():
    for temp in (-10, -5, 0, 5):
        for indoor in (20.0, 21.0):
            for amp in (0.15, 0.3, 0.6):
                a = await one(temp, "auto", indoor, amp); e = await one(temp, "economy", indoor, amp)
                print(temp, indoor, amp, "auto", a, "| economy", e)
import sys; sys.argv=[sys.argv[0]]
asyncio.run(main())
