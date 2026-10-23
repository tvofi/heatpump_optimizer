"""Design-review probe: does a startup manual-plan load revert a clear made inside its await?
Metric: lost_midload (1 = the user's clear was reverted in memory). Null: clear after the load -> 0."""
import asyncio, sys
from datetime import timedelta
from types import SimpleNamespace
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as cmod
from heatpump_optimizer.manual_plan import ManualOverride
C = cmod.HeatPumpOptimizerCoordinator

class Store:
    def __init__(self, gate, data): self.gate, self.data, self.saved = gate, data, []
    async def async_load(self):
        await self.gate.wait(); return dict(self.data)
    async def async_save(self, d): self.saved.append(d)

def stored():
    now = dt_util.now()
    return {"active": True, "expires_at": (now + timedelta(hours=6)).isoformat(),
            "space_slots": [], "dhw_slots": [], "released_space": [], "released_dhw": []}

async def run(midload):
    gate = asyncio.Event()
    c = SimpleNamespace(_manual_override=None)
    c._manual_plan_store = Store(gate, stored())
    async def refresh(): return None
    c.async_request_refresh = refresh
    c._async_save_manual_plan = lambda: C._async_save_manual_plan(c)
    load = asyncio.ensure_future(C._async_load_manual_plan(c))
    await asyncio.sleep(0)
    if midload:
        await C.async_clear_manual_plan(c)
        gate.set(); await load
    else:
        gate.set(); await load
        await C.async_clear_manual_plan(c)
    return int(c._manual_override is not None)

print(f"RESULT lost_midload={asyncio.run(run(True))} lost_null={asyncio.run(run(False))}")
