"""V2 (independent) for D1-s2-52: does a save during the startup read lose persisted state on
Home Assistant 2026.2.3's REAL Store, and which production writers wait?

Part 1 (hastub, the production writers): of the 5 writers the finding names plus async_set_mode,
count those that call QuarantiningStore.async_wait_for_read when invoked (spy); and count which of
the 5 the setup-time first refresh (_skip_solve_once=True, then _async_update_data -- what
async_config_entry_first_refresh runs inside async_setup_entry) invokes.
Part 2 (real HA, subprocess): production store.py's QuarantiningStore over the REAL
homeassistant.helpers.storage.Store on a real HomeAssistant(config_dir), 12 stores spawned through
the real hass.async_create_task in the coordinator's __init__ order (coordinator.py _spawn(load())
tuple), each store's file holding a persisted marker. The writers of the 5 named stores (tuple
positions 4-8: thermal, price, accuracy, energy, ledger) save their in-memory value (the default
until their load lands) after a delay. Grid: other-integration loads in flight {0, 6} x writer
delay {0 s (same tick), 1 ms, 20 ms} x 5 stores = 30 cells; a cell is LOST when the store's
in-memory value after every load has landed is not its persisted marker.
Count key: the value each loader installed (Part 2), spy call counts (Part 1).
Command: LEADS_HA_ROOT=<root> PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_startup_race_realha.py
Expected: Part 1 writers_waiting=0 of 5, set_mode_waiting=1 of 1, first_refresh_invokes price_model:1
(others 0); Part 2 as_shipped lost=2 of 30 (both in the 6-other-loads cells, delay 0 and 1 ms,
store 'thermal'; timing-dependent, +-2), wait arm (each writer first awaits async_wait_for_read,
the fix shape, run in the same script) lost=0 of 30 (exact).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import leads_rig as rig  # noqa: E402  (thread pin inside)
import leads_realha  # noqa: E402
import asyncio
import json
from heatpump_optimizer.store import QuarantiningStore

WRITERS = ["_async_save_thermal_learning", "_async_save_price_model", "_async_save_accuracy",
           "_async_save_energy_totals", "_async_save_ledger"]


def part1():
    rig.freeze()
    hass, entry, coord = rig.coordinator()
    calls = {"n": 0}
    orig = QuarantiningStore.async_wait_for_read

    async def spy(self):
        calls["n"] += 1
        return await orig(self)
    QuarantiningStore.async_wait_for_read = spy
    invoked = {w: 0 for w in WRITERS}
    try:
        waiting = 0
        for w in WRITERS:
            calls["n"] = 0
            asyncio.run(getattr(coord, w)())
            waiting += calls["n"] > 0
        calls["n"] = 0
        asyncio.run(coord.async_set_mode("auto", refresh=False))
        mode_wait = int(calls["n"] > 0)
        for w in WRITERS:
            real = getattr(coord, w)

            async def s(*a, _w=w, _r=real, **k):
                invoked[_w] += 1
                return await _r(*a, **k)
            setattr(coord, w, s)
        coord._skip_solve_once = True

        async def first():
            await coord._update_current_state()
            await coord._async_update_data()
        try:
            asyncio.run(first())
        except Exception as err:  # noqa: BLE001
            print(f"RESULT first_refresh_raised={type(err).__name__}")
    finally:
        QuarantiningStore.async_wait_for_read = orig
    print(f"RESULT writers_waiting={waiting} of_5")
    print(f"RESULT set_mode_waiting={mode_wait} of_1")
    print("RESULT first_refresh_invokes=" + ",".join(f"{k.replace('_async_save_', '')}:{v}" for k, v in invoked.items()))


REAL = r'''
import asyncio, importlib.util, json, os, sys, tempfile, logging
logging.disable(logging.CRITICAL)
from homeassistant.core import HomeAssistant
spec = importlib.util.spec_from_file_location("hpo_store", "custom_components/heatpump_optimizer/store.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
WAIT = json.loads(sys.stdin.read())["wait"]
NAMES = ["dhw_profile", "dhw_draws", "legionella", "thermal", "price", "accuracy", "energy",
         "ledger", "snapshots", "peak", "defrost", "manual_plan"]
TARGETS = ["thermal", "price", "accuracy", "energy", "ledger"]
async def cell(extra, delay):
    d = tempfile.mkdtemp()
    hass = HomeAssistant(d)
    os.makedirs(os.path.join(d, ".storage"))
    keys = [("other_%d" % i) for i in range(extra)] + NAMES
    for k in keys:
        with open(os.path.join(d, ".storage", k), "w") as fh:
            fh.write(json.dumps({"version": 1, "minor_version": 1, "key": k, "data": {"m": "persisted_" + k}}))
    stores = {k: mod.QuarantiningStore(hass, 1, k) for k in keys}
    mem = {k: "default" for k in keys}
    async def loader(k):
        data = await stores[k].async_load()
        if data:
            mem[k] = data["m"]
    tasks = [hass.async_create_task(loader(k)) for k in keys]   # other integrations first, then __init__ order
    async def writer(k):
        if WAIT:
            await stores[k].async_wait_for_read()
        await stores[k].async_save({"m": mem[k]})
    if delay:
        await asyncio.sleep(delay)
    for k in TARGETS:
        await writer(k)
    await asyncio.gather(*tasks)
    await asyncio.sleep(0.05)
    return [k for k in TARGETS if mem[k] != "persisted_" + k]
async def main():
    out = {}
    for extra in (0, 6):
        for delay in (0, 0.001, 0.02):
            out["extra%d_delay%s" % (extra, delay)] = await cell(extra, delay)
    print(json.dumps(out))
asyncio.run(main())
'''


def part2(wait):
    return json.loads(leads_realha.run_real(REAL, json.dumps({"wait": wait})))


part1()
for wait in (False, True):
    res = part2(wait)
    tag = "wait" if wait else "as_shipped"
    lost = sum(len(v) for v in res.values())
    for cellname, stores in res.items():
        print(f"RESULT real_{tag}_{cellname}: lost={len(stores)} of_5 ({','.join(stores) or 'none'})")
    print(f"RESULT real_{tag}_lost={lost} of_30")
rig.tail()
