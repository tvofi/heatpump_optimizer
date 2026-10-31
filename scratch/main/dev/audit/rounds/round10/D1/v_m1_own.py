"""Verifier V2 for D1-s1-01. Metric: torn coordinators alive after gc, with
async_on_unload coroutines AWAITED (real HA semantics), and whether the only
path from a gc root goes through early_cutoff._STATES[c].wiring.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/v_m1_own.py [--clear-wiring]"""
import os, sys, asyncio, gc, weakref, inspect
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "s1"))
import rig
from harness import FakeEntry, ha_setup_entry
from heatpump_optimizer import early_cutoff
CLEAR = "--clear-wiring" in sys.argv
async def main():
    rig.install_inputs(); g = rig.Gate(); g.install(); g.release.set()
    hass = rig.make_hass(); type(hass.bus).async_fire = lambda *a, **k: None; entry = FakeEntry(data=dict(rig.CONFIG)); refs = []
    for _ in range(3):
        assert await ha_setup_entry(rig.integration, hass, entry)
        c = entry.runtime_data
        assert await rig.wait_for(lambda: c._optimization_result is not None and not c._optimization_running, 120)
        await asyncio.sleep(0.05)
        assert await rig.integration.async_unload_entry(hass, entry)
        for cb in list(getattr(entry, "_on_unload", ())):
            r = cb()
            if inspect.isawaitable(r): await r
        entry._on_unload.clear(); delattr(entry, "runtime_data")
        if CLEAR and c in early_cutoff._STATES: early_cutoff._STATES[c].wiring = None
        refs.append(weakref.ref(c)); del c
    await asyncio.sleep(0.2); hass.created.clear(); gc.collect(); gc.collect()
    print(f"RESULT own_torn_alive={sum(r() is not None for r in refs)} of 3 clear_wiring={CLEAR}")
    hass.pool.shutdown(wait=True)
asyncio.run(main())
