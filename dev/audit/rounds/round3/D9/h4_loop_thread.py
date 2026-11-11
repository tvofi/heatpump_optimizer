"""D9 round 3 / H4 -- loop-thread work per cycle, and the longest GIL hold.

METRICS (from tools/audit/briefs/D9.md, verbatim):
  loop_thread_cpu_ms  = time.thread_time() on the event-loop thread across one
                        coordinator cycle, EXCLUDING the executor (the solve
                        runs in another thread, or in the process worker, so
                        its CPU is not on this clock).
  longest_gil_hold_ms = the maximum gap between 1 ms heartbeat ticks of a task
                        on a REAL asyncio loop while the solve runs in a real
                        ThreadPoolExecutor.  Never on FakeHass's inline
                        executor -- tests/harness.py:FakeHass.
                        async_add_executor_job runs the function on the
                        CALLING thread and would measure nothing.
  starvation_share    = fraction of the cycle's wall time spent in gaps > 5 ms.

  Every millisecond figure here is PROVISIONAL (wall/CPU on a shared box) and
  is reported both raw and as a RATIO against tests/stress.py:reference_solve
  measured in the same process in the same session, which is the ruler
  tools/audit/README.md requires for a share-of-a-solve claim.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h4_loop_thread.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, Apple M1,
python 3.11.5; two runs at load1 8.1 and 33.1, thread_factor 1.000/1.002).
Every ms figure is PROVISIONAL; the ratios against reference_solve are what
travel.
  reference_solve_cpu_ms                = 43.4    +-15 %
  process_warm.loop_thread_cpu_ms       = 5.7-6.9         loop work per cycle
  process_warm.loop_cpu_over_reference  = 0.137-0.159     OUTSIDE the executor
  process_cold.loop_cpu_over_reference  = 0.152-0.191
  idle.starvation_share (NULL CONTROL)  = 0.006-0.033     no solve at all
  idle.longest_gil_hold_ms              = 6.4-25.8
  process_route.starvation_share        = 0.006-0.076     the SHIPPED path,
  process_route.longest_gil_hold_ms     = 5.1-8.3         at the idle floor
  inprocess_fallback.starvation_share   = 0.83-0.89   <-- the #511 fallback
  inprocess_fallback.longest_gil_hold_ms= 40-50
A run whose inprocess_fallback.starvation_share is not at least 5x the
process_route figure has not reproduced the finding.

PERTURBATION: HPO_D9_ROUTE=inprocess forces coordinator._await_process to run
the job on the executor thread of this interpreter -- the #511 fallback --
under which longest_gil_hold_ms and starvation_share must RISE.
HPO_D9_ROUTE=process is the shipped path.

INSTRUMENTED SYMBOLS: heatpump_optimizer.coordinator._await_optimize,
coordinator._await_process, HeatPumpOptimizerCoordinator._async_update_data.
"""
from __future__ import annotations

import asyncio
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D9"))
import d9lib  # noqa: E402
from d9lib import result, telemetry  # noqa: E402

GAP_CUTOFF = 0.005
HEARTBEAT = 0.001
IDLE_SECONDS = 2.0
ROUTE = os.environ.get("HPO_D9_ROUTE", "process")


def reference_cpu_ms(samples: int = 5) -> float:
    """The ruler: median process-CPU ms of tests/stress.py:reference_solve."""
    from stress import reference_solve

    reference_solve()  # scipy's first-call cost is not the machine's speed
    return statistics.median(reference_solve()[1] for _ in range(samples))


class LoopHass:
    """A FakeHass whose executor is a REAL thread pool on a REAL loop."""

    def __init__(self, inner, loop, pool) -> None:
        self._inner = inner
        self._loop = loop
        self._pool = pool

    def __getattr__(self, name):
        return getattr(self._inner, name)

    async def async_add_executor_job(self, func, *args):
        return await self._loop.run_in_executor(self._pool, func, *args)

    async def async_add_import_executor_job(self, func, *args):
        return await self._loop.run_in_executor(self._pool, func, *args)


async def heartbeat(stop: asyncio.Event, stamps: list[float]) -> None:
    while not stop.is_set():
        stamps.append(time.perf_counter())
        try:
            await asyncio.wait_for(stop.wait(), timeout=HEARTBEAT)
        except asyncio.TimeoutError:
            continue


def gaps_of(stamps, t0, t1):
    inside = [s for s in stamps if t0 <= s <= t1]
    return [b - a for a, b in zip(inside, inside[1:])]


async def measure_cpu(name: str, coord, hass_wrap) -> float:
    """Loop-thread CPU for one cycle with NO heartbeat running.

    The heartbeat is itself loop-thread work (1 ms period costs ~9 % of the
    loop thread's CPU on this box, see the idle arm), so a loop-CPU figure
    taken while it runs measures the instrument. This arm runs the cycle
    alone.
    """
    coord.hass = hass_wrap
    t0 = time.perf_counter()
    c0 = time.thread_time()
    await coord._async_update_data()
    cpu_ms = (time.thread_time() - c0) * 1000.0
    wall_ms = (time.perf_counter() - t0) * 1000.0
    result(f"{name}.wall_ms", wall_ms, "ms")
    result(f"{name}.loop_thread_cpu_ms", cpu_ms, "ms")
    result(f"{name}.loop_thread_cpu_share_of_wall", cpu_ms / wall_ms, "1")
    return cpu_ms


async def measure(name: str, coord, hass_wrap) -> None:
    stop = asyncio.Event()
    stamps: list[float] = []
    hb = asyncio.create_task(heartbeat(stop, stamps))
    await asyncio.sleep(0.05)
    t0 = time.perf_counter()
    c0 = time.thread_time()
    if coord is None:
        await asyncio.sleep(IDLE_SECONDS)
    else:
        coord.hass = hass_wrap
        await coord._async_update_data()
    loop_cpu = time.thread_time() - c0
    wall = time.perf_counter() - t0
    stop.set()
    await hb
    # A window with fewer than two ticks is not "no gap": it is ONE gap at
    # least as long as the window. Bounding it by the window edges is what
    # keeps a fully starved loop from reporting a longest hold of zero.
    inside = [s for s in stamps if t0 <= s <= t0 + wall]
    edged = [t0] + inside + [t0 + wall]
    gaps = [b - a for a, b in zip(edged, edged[1:])]
    over = [g for g in gaps if g > GAP_CUTOFF]
    result(f"{name}.wall_ms", wall * 1000.0, "ms")
    result(f"{name}.loop_thread_cpu_ms", loop_cpu * 1000.0, "ms")
    result(
        f"{name}.loop_thread_cpu_share_of_wall",
        (loop_cpu / wall) if wall else 0.0, "1",
    )
    result(f"{name}.longest_gil_hold_ms", (max(gaps) if gaps else 0.0) * 1000.0, "ms")
    result(f"{name}.gap_p50_ms", (statistics.median(gaps) if gaps else 0.0) * 1000.0, "ms")
    result(f"{name}.starvation_share", (sum(over) / wall) if wall else 0.0, "1")
    result(f"{name}.ticks", len(gaps) + 1, "count")
    globals()["_LAST_LOOP_CPU_MS"] = loop_cpu * 1000.0


async def build(profile="tibber_like"):
    hass, coord = await d9lib.abuild_coordinator(profile=profile)

    async def _noop(*a, **k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    return hass, coord


async def main() -> None:
    result("baseline_sha", "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1", "sha")
    result("route", ROUTE, "enum")
    ref = reference_cpu_ms()
    result("reference_solve_cpu_ms", ref, "ms")

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=2)

    print("-- idle (NULL CONTROL: the loop with no cycle at all)", flush=True)
    await measure("idle", None, None)

    print("-- process route, loop CPU with no heartbeat (cold then warm)", flush=True)
    hass, coord = await build()
    wrap = LoopHass(hass, loop, pool)
    cold = await measure_cpu("process_cold", coord, wrap)
    warm = await measure_cpu("process_warm", coord, wrap)
    result("process_cold.loop_cpu_over_reference", cold / ref, "1")
    result("process_warm.loop_cpu_over_reference", warm / ref, "1")

    print("-- process route, heartbeat running (starvation)", flush=True)
    await measure("process_route", coord, wrap)

    print("-- NULL CONTROL: flat prices, same route", flush=True)
    hassf, coordf = await build("flat")
    wrapf = LoopHass(hassf, loop, pool)
    await measure_cpu("flat_cold", coordf, wrapf)
    flat_warm = await measure_cpu("flat_warm", coordf, wrapf)
    result("flat_warm.loop_cpu_over_reference", flat_warm / ref, "1")

    print("-- #511 fallback: worker unavailable, solve on the executor thread",
          flush=True)
    restore = d9lib.break_worker()
    try:
        hass2, coord2 = await build()
        wrap2 = LoopHass(hass2, loop, pool)
        fb = await measure_cpu("fallback_cpu", coord2, wrap2)
        result("fallback_cpu.loop_cpu_over_reference", fb / ref, "1")
        await measure("inprocess_fallback", coord2, wrap2)
    finally:
        restore()

    pool.shutdown(wait=False)
    telemetry()


_LAST_LOOP_CPU_MS = 0.0

if __name__ == "__main__":
    asyncio.run(main())
