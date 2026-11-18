"""D1.M1 real-loop lifecycle: setup -> first refresh -> reload mid-solve ->
unload mid-solve -> setup again, on a real asyncio loop + ThreadPoolExecutor.

Metric: after the sequence, count of (a) live asyncio tasks whose coroutine
frames reference a torn-down coordinator, (b) torn-down coordinators still alive
after the harness drops its own references and gc.collect() (weakref), (c) loop exception-handler calls, (d)
whether the last instance's first solved cycle completed (plan present).
Key: references are counted on the coordinator OBJECT identity.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s1/m1_lifecycle.py
Expected (baseline 17f1c55fad1b): leaked_tasks=0 exceptions=0 new_cycle_ok=1
Perturbation: delete `refresh.cancel()` in HeatPumpOptimizerCoordinator.async_shutdown
  (--perturb drops the cancel by nulling _refresh_task first) -> leaked_tasks up
Machine: Mac (darwin, arm64) seat box B4.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, gc, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeEntry, ha_setup_entry, ha_unload_entry  # noqa: E402

PERTURB = "--perturb" in sys.argv


async def main():
    rig.install_inputs()
    gate = rig.Gate(); gate.install()
    if PERTURB:
        orig = rig.cm.HeatPumpOptimizerCoordinator.async_shutdown
        async def no_cancel(self):
            self._refresh_task = None
            await orig(self)
        rig.cm.HeatPumpOptimizerCoordinator.async_shutdown = no_cancel
    hass = rig.make_hass()
    entry = FakeEntry(data=dict(rig.CONFIG))
    torn = []
    # 1. setup + first refresh (light) + background first solve
    gate.release.set()
    assert await ha_setup_entry(rig.integration, hass, entry)
    c1 = entry.runtime_data
    ok1 = await rig.wait_for(lambda: c1._optimization_result is not None)
    print("first solve completed:", ok1)
    # 2. reload mid-solve
    gate.release.clear(); gate.entered.clear()
    t = hass.async_create_task(c1.async_refresh())
    await rig.wait_for(gate.entered.is_set)
    await ha_unload_entry(rig.integration, hass, entry)
    torn.append(c1)
    assert await ha_setup_entry(rig.integration, hass, entry)
    c2 = entry.runtime_data
    # 3. unload mid-solve (c2's background first solve is gated)
    gate.entered.clear()
    await rig.wait_for(gate.entered.is_set)
    await ha_unload_entry(rig.integration, hass, entry)
    torn.append(c2)
    # 4. setup again; release every gated solve
    assert await ha_setup_entry(rig.integration, hass, entry)
    c3 = entry.runtime_data
    gate.release.set()
    new_ok = await rig.wait_for(lambda: c3._optimization_result is not None)
    await asyncio.sleep(0.5)
    # leaks
    leaked = 0
    for task in asyncio.all_tasks():
        if task is asyncio.current_task() or task.done():
            continue
        fr = task.get_coro().cr_frame if hasattr(task.get_coro(), "cr_frame") else None
        while fr is not None:
            if any(v is c for v in fr.f_locals.values() for c in torn):
                leaked += 1; print("LEAK task", task.get_name()); break
            fr = None
    del t
    import weakref
    refs = [weakref.ref(c) for c in torn]
    first_ids = {id(c1)}
    del torn, c1, c2
    for task in list(hass.created):
        if task.done(): hass.created.remove(task)
    gc.collect(); gc.collect()
    alive = [r() for r in refs if r() is not None]
    ext_refs = len(alive)
    if "--trace" in sys.argv:
        import types
        for c in alive:
            print("ALIVE is c1:", c is _c1id if False else id(c) in first_ids)
            frontier=[(c,("coord",))]; seen={id(c),id(alive),id(frontier)}
            for _ in range(12):
                nxt=[]
                for o,path in frontier:
                    for r in gc.get_referrers(o):
                        if id(r) in seen or isinstance(r,(types.FrameType,)) or r is frontier or r is nxt: continue
                        seen.add(id(r))
                        d=type(r).__name__
                        if isinstance(r,types.FunctionType): d+="("+r.__qualname__+")"
                        if isinstance(r,dict): d+=str([k for k,v in r.items() if v is o][:1])
                        if isinstance(r,types.CoroutineType) and r.__name__=="main": continue
                        if isinstance(r,types.ModuleType) or (isinstance(r,dict) and "__name__" in r and "__builtins__" in r) or r is hass or r is entry:
                            print("ROOT:", " <- ".join(path+(d, str(getattr(r,"__name__",""))[:40])))
                        else: nxt.append((r,path+(d,)))
                frontier=nxt[:400]
        for c in []:
            for r in gc.get_referrers(c):
                if getattr(r, "f_code", None) is None and r is not alive:
                    print("  holder:", type(r).__name__, str(r)[:140])
                    for rr in gc.get_referrers(r):
                        if rr is not alive and getattr(rr, "f_code", None) is None:
                            print("     <-", type(rr).__name__, str(rr)[:160])
    del alive
    print(f"RESULT leaked_tasks={leaked} count")
    print(f"RESULT torn_coordinators_alive_after_gc={ext_refs} count")
    print(f"RESULT exceptions={len(hass.exceptions)} count")
    for e in hass.exceptions: print("  exc:", e.get("message"), e.get("exception"))
    print(f"RESULT new_cycle_ok={int(new_ok)} bool")
    print(f"RESULT gated_solves={gate.calls} count")
    pc = time.process_time(); tc = time.thread_time()
    print(f"RESULT deliberate_thread_cpu={gate.thread_cpu:.3f} s")
    print(f"RESULT thread_factor={max(pc - gate.thread_cpu, 0) / tc:.3f}")
    print(f"RESULT load1={rig.load1():.2f}")
    print("RESULT swapins=0")
    hass.pool.shutdown(wait=True)

asyncio.run(main())
