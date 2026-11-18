"""Verifier D1#1, V2 for D1-s1-03: a refresh request issued while a debounced refresh executes.

Metric: of N=8 request_refresh calls, each issued while one in-flight refresh is held, the number
that produce NO later _async_update_data run (dropped), for an in-flight refresh started by
async_request_refresh (claim arm) and by async_refresh (null arm), on the integration's
coordinator class resolution of async_request_refresh / async_refresh (which methods it owns).
The update body is a gated counter, so the count is of the refresh machinery the integration
inherits, independent of the solve; cooldown is shortened to 0.05 s so a trailing run, if armed,
lands before the settle.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s1_03_debounce.py
"""
import asyncio
import os
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from homeassistant.helpers import update_coordinator as uc  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as H  # noqa: E402

own = {m: (m in H.__dict__ or any(m in k.__dict__ for k in H.__mro__ if k.__module__.startswith("heatpump_optimizer")))
       for m in ("async_request_refresh", "async_refresh", "_async_refresh")}
print(f"integration overrides: {own}")


class Hass:
    def __init__(self, loop):
        self.loop = loop

    def async_create_task(self, coro):
        return self.loop.create_task(coro)


class Coord(uc.DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(hass, None, name="t")
        self._debounced_refresh.cooldown = 0.05
        self.runs = 0
        self.gate = None

    async def _async_update_data(self):
        self.runs += 1
        if self.gate is not None:
            g, self.gate = self.gate, None
            await g.wait()
        return {}


async def trial(origin):
    c = Coord(Hass(asyncio.get_running_loop()))
    gate = asyncio.Event()
    c.gate = gate
    starter = c.async_request_refresh if origin == "debounced" else c.async_refresh
    t = asyncio.ensure_future(starter())
    await asyncio.sleep(0.01)
    before = c.runs
    await c.async_request_refresh()  # the writer's re-plan request
    gate.set()
    await t
    await asyncio.sleep(0.3)
    c._debounced_refresh.async_shutdown()
    return int(c.runs == before)  # dropped: no run after the write


async def main():
    res = {o: sum([await trial(o) for _ in range(8)]) for o in ("debounced", "direct")}
    print(f"RESULT dropped_debounced={res['debounced']} of 8")
    print(f"RESULT null_dropped_direct={res['direct']} of 8")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


asyncio.run(main())
