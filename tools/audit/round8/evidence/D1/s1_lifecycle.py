"""D1 s1 real-loop lifecycle harness (round 8, baseline cdf82daa, 4-vCPU cloud container).

Metric: after reload-mid-solve and unload-mid-solve through the entry state
machine, count (a) live asyncio tasks / scheduled loop timers / bus+state
listeners / executor futures that still reference a torn-down coordinator,
(b) torn-down coordinators still reachable after gc, (c) exceptions escaping
(loop exception handler + ERROR log records), (d) whether the new instance's
first real solve completes, (e) the old solve's executor future still running
when unload returned (it holds coordinator._PROCESS_LOCK).
Count key: objects reachable from asyncio.all_tasks()/loop._scheduled/
hass.bus/hass.state_listeners/hass.executor_futures whose referent graph
(depth 4) contains the torn-down coordinator; weakref liveness after gc.

Command (from the tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/s1_lifecycle.py
Optional: --perturb-no-cancel  (instance-patches async_shutdown to skip the
  in-flight refresh cancel; the "old_solve_landed_after_unload" and
  service_calls_after_unload / store_saves_after_unload counts must move up) -- a harness-side perturbation of
  coordinator.HeatPumpOptimizerCoordinator.async_shutdown, restored in finally.
Expected (baseline): leaked_refs=0, alive_after_gc=0, escaped_exceptions=0,
  new_first_solve_ok=2, old_solve_landed_after_unload=0 (exact counts);
  old_future_running_at_unload is 0 or 1 (timing), provisional.
Instrumented: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_shutdown,
  heatpump_optimizer:async_setup_entry/async_unload_entry, coordinator:_run_in_process.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import gc  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import weakref  # noqa: E402

sys.path.insert(0, "tools/audit/round8/D1")
from s1_realloop import (  # noqa: E402
    RealEntry, RealLoopHass, base_config, base_states, load1, swapins,
)

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

PERTURB = "--perturb-no-cancel" in sys.argv


class ErrorLog(logging.Handler):
    def __init__(self):
        super().__init__(logging.ERROR)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def _refs(obj, target, depth=4, seen=None):
    """Whether ``target`` is reachable from ``obj`` within ``depth`` referents."""
    if obj is target:
        return True
    if depth == 0:
        return False
    seen = seen if seen is not None else set()
    if id(obj) in seen:
        return False
    seen.add(id(obj))
    if isinstance(obj, (str, bytes, int, float, type(None))):
        return False
    try:
        kids = gc.get_referents(obj)
    except Exception:  # noqa: BLE001
        return False
    return any(_refs(k, target, depth - 1, seen) for k in kids
               if not isinstance(k, type) and getattr(k, "__name__", "") != "builtins")


def leaked(hass, target):
    loop = asyncio.get_running_loop()
    out = []
    cur = asyncio.current_task()
    for t in asyncio.all_tasks():
        if t is cur or t.done():
            continue
        coro = t.get_coro()
        frame = getattr(coro, "cr_frame", None)
        locs = frame.f_locals if frame is not None else {}
        if any(v is target for v in locs.values()) or _refs(coro, target, 3):
            out.append(("task", t.get_name()))
    for h in list(getattr(loop, "_scheduled", [])):
        if not h.cancelled() and _refs(h._callback, target, 4):
            out.append(("timer", repr(h._callback)[:80]))
    for kind, fn in hass.bus.listeners:
        if _refs(fn, target, 4):
            out.append(("bus", kind))
    for ids, fn in getattr(hass, "state_listeners", []):
        if _refs(fn, target, 4):
            out.append(("state_listener", ids))
    return out


async def wait_for(pred, timeout):
    t0 = time.monotonic()
    while not pred():
        if time.monotonic() - t0 > timeout:
            return False
        await asyncio.sleep(0.05)
    return True


async def main():
    res = {}
    elog = ErrorLog()
    logging.getLogger().addHandler(elog)
    loop = asyncio.get_running_loop()
    escaped = []
    loop.set_exception_handler(lambda l, ctx: escaped.append(ctx.get("message")))

    in_solve = threading.Event()
    solve_threads = []
    orig_run = cm._run_in_process

    def hooked(fn, args):
        in_solve.set()
        solve_threads.append(threading.current_thread().name)
        try:
            return orig_run(fn, args)
        finally:
            in_solve.clear()

    cm._run_in_process = hooked
    orig_shutdown = cm.HeatPumpOptimizerCoordinator.async_shutdown
    if PERTURB:
        async def no_cancel(self):
            # the perturbation: forget the in-flight refresh AND drop the
            # #237 latch after shutdown, i.e. remove both guards.
            self._refresh_task = None
            out = await orig_shutdown(self)
            self._entry_released = False
            return out
        cm.HeatPumpOptimizerCoordinator.async_shutdown = no_cancel
    try:
        hass = RealLoopHass(base_states())
        hass.config_entries.integration = integration
        entry = RealEntry(data=base_config(const), entry_id="e1")
        hass.config_entries.entries.append(entry)
        await integration.async_setup(hass, {})
        ok = await hass.config_entries.async_setup("e1")
        c1 = entry.runtime_data
        first_ok = await wait_for(lambda: c1._optimization_result is not None, 240)
        res["setup_ok"] = int(bool(ok))
        res["c1_first_solve_ok"] = int(first_ok)

        async def one_mid_solve(coord, action):
            # A scheduled-cycle refresh, as the interval timer runs it.
            refresh = hass.async_create_task(coord.async_refresh(), name="interval_refresh")
            got = await wait_for(in_solve.is_set, 120)
            before = coord._optimization_result
            futs_running = int(in_solve.is_set())
            await action()
            futs_after = int(in_solve.is_set())
            try:
                await asyncio.wait_for(asyncio.shield(refresh), 5)
            except BaseException:  # noqa: BLE001
                pass
            return got, before, futs_running, futs_after

        # ---- reload mid-solve --------------------------------------------
        got, before1, fr, fa = await one_mid_solve(
            c1, lambda: hass.config_entries.async_reload("e1"))
        res["reload_hit_mid_solve"] = int(got)
        res["old_future_running_at_reload"] = fa
        c2 = entry.runtime_data
        w1 = weakref.ref(c1)
        # let the orphaned executor future finish (it holds _PROCESS_LOCK)
        await wait_for(lambda: not in_solve.is_set(), 240)
        await asyncio.sleep(0.5)
        landed1 = int(c1._optimization_result is not before1)
        ok2 = await wait_for(lambda: c2._optimization_result is not None, 240)
        res["new_first_solve_ok"] = int(ok2)
        leaks1 = leaked(hass, c1)
        c1_actuated_released = int(bool(c1._entry_released))
        del c1
        # ---- unload mid-solve --------------------------------------------
        store_before = dict(cm.__dict__.get("_NOSUCH", {}))
        from homeassistant.helpers import storage as st
        got2, before2, fr2, fa2 = await one_mid_solve(
            c2, lambda: hass.config_entries.async_unload("e1"))
        saves_at_unload = sum(st.SAVE_COUNTS.values())
        calls_at_unload = len(hass.services.calls)
        res["unload_hit_mid_solve"] = int(got2)
        res["old_future_running_at_unload"] = fa2
        await wait_for(lambda: not in_solve.is_set(), 240)
        await asyncio.sleep(0.5)
        saves_after = sum(st.SAVE_COUNTS.values())
        res["service_calls_after_unload"] = len(hass.services.calls) - calls_at_unload
        landed2 = int(c2._optimization_result is not before2)
        leaks2 = leaked(hass, c2)
        w2 = weakref.ref(c2)
        del c2
        # ---- setup again -------------------------------------------------
        ok3 = await hass.config_entries.async_setup("e1")
        c3 = entry.runtime_data
        ok3s = await wait_for(lambda: c3._optimization_result is not None, 240)
        res["new_first_solve_ok"] += int(ok3 and ok3s)
        gc.collect()
        alive = [n for n, w in (("c1", w1), ("c2", w2)) if w() is not None]
        for n, w in (("c1", w1), ("c2", w2)):
            if w() is not None:
                holders = [type(r).__name__ for r in gc.get_referrers(w())][:8]
                print(f"  alive {n}: referrers={holders}")
        res["leaked_refs"] = len(leaks1) + len(leaks2)
        for item in leaks1 + leaks2:
            print("  leak:", item)
        res["alive_after_gc"] = len(alive)
        res["old_solve_landed_after_unload"] = landed1 + landed2
        res["store_saves_after_unload"] = saves_after - saves_at_unload
        res["released_latch_set"] = c1_actuated_released
        await hass.config_entries.async_unload("e1")
        res["escaped_exceptions"] = len(escaped) + len(elog.records)
        for m in escaped:
            print("  escaped:", m)
        for r in elog.records:
            print("  ERROR log:", r.name, r.getMessage()[:160])
        res["solve_threads_distinct"] = len(set(solve_threads))
        hass.executor.shutdown(wait=True)
    finally:
        cm._run_in_process = orig_run
        cm.HeatPumpOptimizerCoordinator.async_shutdown = orig_shutdown
        cm._shutdown_process_pool()
    return res


if __name__ == "__main__":
    t_cpu, t_thr = time.process_time(), time.thread_time()
    out = asyncio.run(main())
    for k, v in out.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={load1()}")
    print(f"RESULT swapins={swapins()}")
    print(f"RESULT perturbed={int(PERTURB)}")
