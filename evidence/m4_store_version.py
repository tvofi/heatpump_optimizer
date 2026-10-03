"""M4 probe: does the test stub's Store honour a version change the way Home Assistant's does?
Run from the repo root: PYTHONPATH=tests/hastub:custom_components python3 m4_store_version.py"""
import asyncio, pathlib, re
from homeassistant.helpers.storage import Store
async def arm(save_v, load_v):
    await Store(None, save_v, "probe_key").async_save({"learned": 42})
    try:
        got = await Store(None, load_v, "probe_key").async_load()
        return f"returned {got!r}"
    except Exception as e:  # noqa
        return f"raised {type(e).__name__}"
print("stub, saved v1 loaded v2 (a major bump):", asyncio.run(arm(1, 2)))
print("stub, saved v1 loaded v1 (null control):", asyncio.run(arm(1, 1)))
P = pathlib.Path("custom_components/heatpump_optimizer")
n = sum(len(re.findall(r"_async_migrate_func", p.read_text())) for p in P.glob("*.py"))
print("_async_migrate_func overrides in the package:", n)
print("Home Assistant's Store on a major mismatch with no override: raises NotImplementedError "
      "(homeassistant/helpers/storage.py, dev branch, _async_load_data: 'except NotImplementedError: if data[\"version\"] != self.version: raise')")
