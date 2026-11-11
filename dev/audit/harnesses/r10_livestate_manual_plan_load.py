"""R10-LIVESTATE (#2248): does the startup manual-plan load revert a clear or an apply
made inside its await? Ported from the design review's probe
(design-verdict/r10-livestate 5af5526b5, evidence/probe_manual_restore_port.py).

A stub store whose async_load is held on an asyncio.Event and registers its read
future on its first step, as QuarantiningStore does. The load runs as a task; the
user's clear (or apply) runs as a task inside it; the gate opens.
Metrics: lost_midload_clear / lost_midload_apply -- 1 when the user's write is not
the override after both finish. Nulls: the same write after the load, 0.
Expected at merge base fd7e289d0: lost_midload_clear 1, lost_midload_apply 1, nulls 0.
Expected at the R10-LIVESTATE head: all 0.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_livestate_manual_plan_load.py
"""
import asyncio
from datetime import timedelta
from types import SimpleNamespace

from homeassistant.util import dt as dt_util

from heatpump_optimizer import coordinator as cmod
from heatpump_optimizer.manual_plan import ManualOverride

C = cmod.HeatPumpOptimizerCoordinator


class Store:
    def __init__(self, gate, data):
        self.gate, self.data, self.reading = gate, data, None

    async def async_load(self):
        self.reading = asyncio.get_running_loop().create_future()
        await self.gate.wait()
        self.reading.set_result(None)
        return dict(self.data)

    async def async_wait_for_read(self):
        if self.reading is not None:
            await asyncio.shield(self.reading)

    async def async_save(self, data):
        return None


async def run(action, midload):
    gate = asyncio.Event()
    now = dt_util.now()
    c = SimpleNamespace(_manual_override=None)
    c._manual_plan_store = Store(gate, {
        "active": True, "expires_at": (now + timedelta(hours=6)).isoformat(),
        "space_slots": [], "dhw_slots": [], "released_space": [], "released_dhw": []})

    async def refresh():
        return None

    c.async_request_refresh = refresh
    c._async_save_manual_plan = lambda: C._async_save_manual_plan(c)
    c._horizon_step_starts = lambda start, n: []
    c._opt_config = SimpleNamespace(n_steps=0)
    mine = ManualOverride(space_slots=None, dhw_slots=None, expires_at=now + timedelta(hours=2))
    write = (lambda: C.async_clear_manual_plan(c)) if action == "clear" else (
        lambda: C.async_apply_manual_plan(c, mine))
    load = asyncio.ensure_future(C._async_load_manual_plan(c))
    await asyncio.sleep(0)
    if midload:
        task = asyncio.ensure_future(write())
        await asyncio.sleep(0)
        gate.set()
        await load
        await task
    else:
        gate.set()
        await load
        await write()
    return int(c._manual_override is not (None if action == "clear" else mine))


for action in ("clear", "apply"):
    print(f"RESULT lost_midload_{action}={asyncio.run(run(action, True))} count")
    print(f"RESULT lost_null_{action}={asyncio.run(run(action, False))} count")
