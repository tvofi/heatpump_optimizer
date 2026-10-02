# Reviewer's own probe (not the finder's): stub Store version paths upstream's _async_load_data treats differently.
import asyncio
from homeassistant.helpers import storage as st
class Mig(st.Store):
    async def _async_migrate_func(self, a, b, d): return {"from": a, **d}
async def arm(cls, save_v, load_v, loads=1):
    st._reset_store_disk(); st.SAVE_COUNTS.clear()
    await st.Store(None, save_v, "k").async_save({"n": 1})
    out = []
    for _ in range(loads):
        try: out.append(await cls(None, load_v, "k").async_load())
        except Exception as e: out.append(type(e).__name__)
    return out, st.SAVE_COUNTS.get("k"), st._VERSIONS.get("k")
for label, a in [("downgrade no-migrate 2->1", (st.Store, 2, 1)), ("downgrade migrate 2->1", (Mig, 2, 1)), ("bump migrate 1->2 loaded twice", (Mig, 1, 2, 2))]:
    print("RESULT", label, asyncio.run(arm(*a)))
