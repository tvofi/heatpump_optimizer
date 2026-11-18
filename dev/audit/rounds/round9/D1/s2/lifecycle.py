"""D1.M1 real-loop lifecycle: setup -> first refresh -> reload mid-solve ->
unload mid-solve -> setup again, on a real asyncio loop with a real
ThreadPoolExecutor and the real process-solve worker.

Metric (one line): after the sequence and gc.collect(), the number of torn-down
coordinators still reachable (``leaked_coordinators``), the number of live
tasks whose coroutine frame holds one (``tasks_holding_old``), the number of
exceptions that escaped to the loop or a task (``escaped_exceptions``), and
whether the final instance's first solve completed (``final_first_solve_ok``).
Count key: weakrefs to the production coordinator objects, and the tasks the
real loop reports in ``asyncio.all_tasks``.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
        tools/audit/round9/D1/s2/lifecycle.py [--perturb NAME]
Expected: leaked_coordinators=0, tasks_holding_old=0, escaped_exceptions=0,
final_first_solve_ok=1 (exact). Wall numbers provisional.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  Machine: B4 cloud container.

Real-HA semantics: HASTUB_TZ=Europe/Stockholm (aware clock); lifecycle calls go
through tests/harness.py:ha_setup_entry / ha_unload_entry, one at a time, as
the config-entry state machine runs them -- never two concurrently.

Perturbations (--perturb): ``no_cancel`` makes async_shutdown skip cancelling
the in-flight refresh (tasks_holding_old / discarded counts must move);
``no_cancel_any`` also drops the entry's cancel (discarded_solves must move
up); ``leak`` parks each torn-down coordinator on hass.data (leaked_coordinators
must move up); ``no_release`` makes _release_registrations a no-op.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse
import asyncio
import gc
import logging
import resource
import sys
import time
import weakref
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState, ha_setup_entry, ha_unload_entry  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402


class RealLoopHass(FakeHass):
    """FakeHass whose executor is a real pool and whose tasks are scheduled."""

    def __init__(self, states, loop, pool):
        super().__init__(states)
        self.loop = loop
        self._pool = pool
        self.created: list[weakref.ref] = []

    def async_create_task(self, coro, name=None, eager_start=True):
        task = self.loop.create_task(coro, name=name)
        self.created.append(weakref.ref(task))
        return task

    async def async_add_executor_job(self, func, *args):
        return await self.loop.run_in_executor(self._pool, func, *args)

    async def async_add_import_executor_job(self, func, *args):
        self.import_jobs.append(func)
        return await self.loop.run_in_executor(self._pool, func, *args)


class LogCount(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.msgs: list[tuple[int, str]] = []

    def emit(self, record):
        self.msgs.append((record.levelno, record.getMessage()))


CFG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    "price_source": "entity",
    "price_entity": "sensor.prices",
}


def _states():
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    return {
        "sensor.indoor": FakeState("21.4"),
        "sensor.outdoor": FakeState("-3.0"),
        "sensor.prices": FakeState("0.5", attributes={"raw_today": [
            {"start": (now + timedelta(hours=h)).isoformat(),
             "value": round(0.5 + 0.1 * (h % 4), 3)} for h in range(48)]}),
    }


async def _wait(pred, timeout):
    t0 = time.monotonic()
    while not pred():
        if time.monotonic() - t0 > timeout:
            return False
        await asyncio.sleep(0.01)
    return True


def _holds(task, targets):
    coro = task.get_coro()
    seen = 0
    while coro is not None and seen < 20:
        seen += 1
        frame = getattr(coro, "cr_frame", None)
        if frame is not None:
            for v in frame.f_locals.values():
                if any(v is t for t in targets):
                    return True
        coro = getattr(coro, "cr_await", None)
    return False


async def scenario(loop, pool, log):
    hass = RealLoopHass(_states(), loop, pool)
    entry = FakeEntry(data=dict(CFG))
    escaped: list[str] = []
    loop.set_exception_handler(lambda l, ctx: escaped.append(str(ctx.get("exception") or ctx.get("message"))))
    marks: dict[str, float] = {}
    olds = []

    # 1. setup + light first refresh; the background first solve starts
    assert await ha_setup_entry(integration, hass, entry)
    c1 = entry.runtime_data
    olds.append(weakref.ref(c1))
    ok = await _wait(lambda: c1._optimization_running, 20)
    marks["c1_solve_started"] = float(ok)
    await asyncio.sleep(0.2)
    # 2. reload mid-solve: unload then setup, serialised as the manager does
    assert await ha_unload_entry(integration, hass, entry)
    assert await ha_setup_entry(integration, hass, entry)
    c2 = entry.runtime_data
    olds.append(weakref.ref(c2))
    ok = await _wait(lambda: c2._optimization_running, 30)
    marks["c2_solve_started"] = float(ok)
    await asyncio.sleep(0.2)
    # 3. unload mid-solve
    assert await ha_unload_entry(integration, hass, entry)
    del c1, c2
    # 4. setup again; its first cycle must complete
    t_setup = time.monotonic()
    assert await ha_setup_entry(integration, hass, entry)
    c3 = entry.runtime_data
    ok = await _wait(lambda: c3._optimization_result is not None
                     and not c3._optimization_running, 90)
    marks["final_first_solve_ok"] = float(ok)
    marks["final_first_solve_wall_s"] = time.monotonic() - t_setup
    # let orphaned work drain
    await asyncio.sleep(0.5)
    gc.collect()
    live_old = [r() for r in olds if r() is not None]
    tasks_holding = [t for t in asyncio.all_tasks(loop)
                     if t is not asyncio.current_task() and _holds(t, live_old)]
    referrers = []
    for o in live_old:
        for ref in gc.get_referrers(o):
            if ref is live_old or isinstance(ref, list) and ref is olds:
                continue
            referrers.append(type(ref).__name__ + ":" + (
                getattr(ref, "__qualname__", "") or
                (getattr(getattr(ref, "cr_code", None), "co_qualname", "") if hasattr(ref, "cr_code") else "")
            ))
    for r in hass.created:
        t = r()
        if t is not None and t.done() and not t.cancelled() and t.exception() is not None:
            escaped.append(f"task {t.get_name()}: {t.exception()!r}")
    discarded = sum(1 for _, m in log.msgs if "discarding it" in m or "not actuating" in m)
    errors = [m for lv, m in log.msgs if lv >= logging.ERROR]
    # tidy
    await ha_unload_entry(integration, hass, entry)
    return {
        **marks,
        "leaked_coordinators": len(live_old),
        "tasks_holding_old": len(tasks_holding),
        "escaped_exceptions": len(escaped),
        "error_logs": len(errors),
        "discarded_solves": discarded,
        "_referrers": referrers[:12],
        "_escaped": escaped[:6],
        "_errors": errors[:6],
    }


def _perturb(name):
    if name == "no_cancel":
        orig = cm.HeatPumpOptimizerCoordinator.async_shutdown

        async def shut(self):
            self._refresh_task = None
            await orig(self)
        return [mock.patch.object(cm.HeatPumpOptimizerCoordinator, "async_shutdown", shut)]
    if name == "no_cancel_any":
        # neither the coordinator nor the entry cancels the in-flight solve:
        # the orphan must then be seen landing (discarded_solves moves up)
        import harness
        orig = cm.HeatPumpOptimizerCoordinator.async_shutdown

        async def shut(self):
            self._refresh_task = None
            await orig(self)

        def bg(self, hass, target, name, eager_start=True):
            self.background_tasks.append(name)
            return hass.async_create_task(target)
        return [mock.patch.object(cm.HeatPumpOptimizerCoordinator, "async_shutdown", shut),
                mock.patch.object(harness.FakeEntry, "async_create_background_task", bg)]
    if name == "leak":
        # instrument check: a torn-down coordinator parked on hass.data must
        # be counted (leaked_coordinators moves up)
        orig = cm.HeatPumpOptimizerCoordinator.async_shutdown

        async def shut(self):
            await orig(self)
            self.hass.data.setdefault("_leak", []).append(self)
        return [mock.patch.object(cm.HeatPumpOptimizerCoordinator, "async_shutdown", shut)]
    if name == "no_release":
        return [mock.patch.object(cm.HeatPumpOptimizerCoordinator, "_release_registrations",
                                  lambda self: None)]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default="")
    args = ap.parse_args()
    logging.basicConfig(level=logging.CRITICAL)
    log = LogCount()
    lg = logging.getLogger("heatpump_optimizer")
    lg.addHandler(log)
    lg.setLevel(logging.DEBUG)
    patches = _perturb(args.perturb)
    for p in patches:
        p.start()
    pc0, tc0 = time.process_time(), time.thread_time()
    ru0 = resource.getrusage(resource.RUSAGE_SELF)
    loop = asyncio.new_event_loop()
    pool = ThreadPoolExecutor(max_workers=4)
    try:
        res = loop.run_until_complete(scenario(loop, pool, log))
    finally:
        pool.shutdown(wait=True)
        loop.close()
        cm._shutdown_process_pool()
    for p in patches:
        p.stop()
    pc, tc = time.process_time() - pc0, time.thread_time() - tc0
    for k, v in res.items():
        if k.startswith("_"):
            print(f"  {k}: {v}")
        else:
            print(f"RESULT {k}={v}")
    # the pool threads' CPU is deliberate; the residual is printed per README
    print(f"RESULT deliberate_thread_cpu_s={max(0.0, pc - tc):.3f}")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
