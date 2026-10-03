"""Reviewer's own probe (#1869): create_issue calls per load, per direction.
Counts calls (the registry dedupes by id, so entries cannot show a double).
'floor-downgrade' replays upstream 2025.2.0, which has no
UnsupportedStorageVersionError: a newer document goes to _async_migrate_func."""
import asyncio, logging
from homeassistant.helpers import storage as hs
import custom_components.heatpump_optimizer.store as S
calls = []
real = S.create_issue
S.create_issue = lambda *a, **k: (calls.append(a[2]), real(*a, **k))
class H: pass
def run(stored, mine, floor=False):
    hs._reset_store_disk(); calls.clear()
    key = "probe"; hs._DISK[key] = '{"a": 1}'; hs._VERSIONS[key] = stored
    st = S.QuarantiningStore(H(), mine, key, lead=None)
    if floor:  # upstream 2025.2.0: no downgrade check before the hook
        async def go():
            st._reading = asyncio.get_running_loop().create_future(); st._reader = asyncio.current_task()
            try: return await st._async_migrate_func(stored, 1, {"a": 1})
            finally: st._reader=None; st._reading.set_result(None)
    else:
        go = st.async_load
    try: out = type(asyncio.run(go())).__name__
    except BaseException as e: out = type(e).__name__
    return out, len(calls)
for label, args in [("same", (1,1)), ("older(bump)", (1,2)), ("newer(downgrade,2026.3+)", (3,2)),
                    ("newer(downgrade,floor)", (3,2,True)), ("minor-only", None)]:
    if args is None: continue
    print(f"RESULT issue_calls[{label}] escaped={run(*args)[0]} create_issue_calls={run(*args)[1]}")
