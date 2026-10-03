"""Reviewer's own probe (#1869): race the reader-task exemption.

The stub Store is wrapped with upstream 2025.2.0's async_load dedupe
(helpers/storage.py L274-302: a second concurrent call awaits the first's
_load_future) and an executor-style yield before the read, so a second
task can interleave while the first is mid-load.
"""
import asyncio, sys
from homeassistant.helpers import storage as hs
from custom_components.heatpump_optimizer.store import QuarantiningStore

_raw_load = hs.Store.async_load

async def ha_load(self):
    fut = getattr(self, "_load_future", None)
    if fut:
        return await fut
    self._load_future = asyncio.get_running_loop().create_future()
    try:
        await asyncio.sleep(0.01)          # the executor read
        result = await _raw_load(self)
    except BaseException as ex:
        if not self._load_future.done():
            self._load_future.set_exception(ex); self._load_future.exception()
        raise
    else:
        self._load_future.set_result(result)
    finally:
        self._load_future = None
    return result
hs.Store.async_load = ha_load

class Migrating(QuarantiningStore):
    async def _async_migrate_func(self, a, b, old):
        await asyncio.sleep(0.01)
        return {"migrated": True, **old}

def seed(key, version):
    hs._reset_store_disk()
    hs._DISK[key] = '{"x": 1}'
    hs._VERSIONS[key] = version

async def scenario_other_task_save():
    key = "race_a"; seed(key, 1)
    st = Migrating(None, 2, key, lead=None)
    order = []
    async def loader():
        d = await st.async_load(); order.append(("load-done", d))
    async def writer():
        await asyncio.sleep(0.001)     # start while the load is in flight
        await st.async_save({"x": 99}); order.append(("save-done",))
    try:
        await asyncio.wait_for(asyncio.gather(loader(), writer()), 2)
    except (asyncio.TimeoutError, TimeoutError):
        return "TimeoutError", hs._DISK[key]
    first = order[0][0]
    on_disk = hs._DISK[key]
    return first, on_disk

async def scenario_two_loaders():
    key = "race_b"; seed(key, 1)
    st = Migrating(None, 2, key, lead=None)
    async def loader(n):
        await asyncio.sleep(0.001 * n)
        return await st.async_load()
    try:
        r = await asyncio.wait_for(asyncio.gather(loader(0), loader(1)), 2)
        return f"ok {r}"
    except (asyncio.TimeoutError, TimeoutError):
        return "TimeoutError (deadlock)"

async def scenario_save_spawned_by_reader():
    # a task the reader spawns is a different task: it must wait
    key = "race_c"; seed(key, 1)
    st = Migrating(None, 2, key, lead=None)
    log = []
    async def loader():
        await st.async_load(); log.append("load")
    async def w():
        await st.async_save({"y": 2}); log.append("save")
    t = asyncio.ensure_future(loader())
    await asyncio.sleep(0.001)
    try:
        await asyncio.wait_for(asyncio.gather(t, w()), 2)
    except (asyncio.TimeoutError, TimeoutError):
        return "TimeoutError"
    return log

async def main():
    first, disk = await scenario_other_task_save()
    print(f"RESULT other_task_save_first_event={first} disk={disk}")
    print(f"RESULT two_concurrent_loaders={await scenario_two_loaders()}")
    print(f"RESULT spawned_save_order={await scenario_save_spawned_by_reader()}")

asyncio.run(main())
