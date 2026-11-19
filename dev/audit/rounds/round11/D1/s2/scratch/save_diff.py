import sys, json, asyncio
sys.path.insert(0, "dev/audit/rounds/round11/D1/s2")
import d1s2_lib as L
import clock_save as CS
from unittest import mock

disks = {"control": CS.healthy_at(L.T0)}
real_load = L.storage_stub.Store.async_load


async def slow_load(self):
    await asyncio.sleep(0.01)
    return await real_load(self)

ps = L.patches() + [mock.patch.object(L.storage_stub.Store, "async_load", slow_load)]
for p in ps:
    p.start()
docs = {}


async def go():
    disk, vers = disks["control"]
    for tag, early in (("control", False), ("race", True)):
        L.reset_globals()
        L.dtu.freeze(L.T0)
        hass, coord = await CS.restart(disk, vers, savers_early=early)
        docs[tag] = {k: json.loads(v) for k, v in L.storage_stub._DISK.items()}
        await coord.async_shutdown()
        await L.drain(hass, 5)
asyncio.run(go())
for name in ("dhw_draws", "dhw_legionella", "duty_switch", "off_restore", "pump_duty"):
    k = CS.SF.KEYPFX + name
    print("==", name)
    print("  healthy:", json.dumps(disks["control"][0].get(k))[:400])
    print("  control:", json.dumps(docs["control"].get(k))[:400])
    print("  race   :", json.dumps(docs["race"].get(k))[:400])
