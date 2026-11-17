"""D9-s1 gil_hold: longest contiguous GIL hold seen by a real asyncio loop.

Metric (D9.md): longest hold = max gap between ticks of a 1 ms heartbeat task
on a REAL asyncio loop while a solve runs off the loop; starvation share =
sum(gaps > 5 ms) / solve wall. Never FakeHass (its executor runs inline).

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_gil_hold.py [--reps 3]

Arms
  idle                      null control, no solve
  process.<scenario>        heatpump_optimizer.coordinator:_await_optimize, the
                            shipped route (persistent process worker)
  thread.<scenario>         optimize_in_process on a ThreadPoolExecutor: the
                            #511 in-process fallback _await_optimize degrades to
  thread_si05.<scenario>    perturbation: sys.setswitchinterval 5 ms -> 0.5 ms
  thread_yield100us.<sc>     optimizer._gil_yield made time.sleep(0.0001)
  thread_noyield.<scenario> optimizer._gil_yield (sleep(0) per evaluation) made a
                            no-op: the in-run yield's own contribution
  cycle.process             one full HeatPumpOptimizerCoordinator._async_update_data
                            (real process worker; the loop thread's own work
                            counts, as it would in Home Assistant)
  pickle.<scenario>         contiguous pickle.dumps(job) / loads(reply) the
                            executor thread does on the shipped route (ms, bytes)

Perturbation (production symbol): coordinator._await_process swapped for a
plain executor submit of the same picklable job (the fallback) -> process.*
longest hold must go UP to the thread.* level.

Expected (host, quiet, load1 < 1): idle and process.* longest <= ~2-6 ms;
thread.* longest tens of ms. Provisional -- wall-clock on a shared box.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import pickle  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402

HEARTBEAT = 0.001
CUT = 0.005
SCENARIOS = ("two_zone_dhw", "dhw_cap_zero_range")


class LoopHass:
    def __init__(self, loop, pool):
        self.loop, self.pool = loop, pool
        self.data = {}

    async def async_add_executor_job(self, func, *args):
        return await self.loop.run_in_executor(self.pool, func, *args)


async def heartbeat(stop, stamps):
    while not stop.is_set():
        stamps.append(time.perf_counter())
        await asyncio.sleep(HEARTBEAT)


async def measure(name, work):
    stop = asyncio.Event()
    stamps: list[float] = []
    hb = asyncio.create_task(heartbeat(stop, stamps))
    await asyncio.sleep(0.05)
    t0 = time.perf_counter()
    await work()
    t1 = time.perf_counter()
    await asyncio.sleep(0.003)  # the stamp after a trailing block joins the window
    stop.set()
    await hb
    win = [s for s in stamps if t0 <= s <= t1] + [s for s in stamps if s > t1][:1]
    gaps = [b - a for a, b in zip(win, win[1:])]
    wall = t1 - t0
    over = sum(g for g in gaps if g > CUT)
    longest = max(gaps) * 1e3 if gaps else 0.0
    p99 = sorted(gaps)[int(0.99 * (len(gaps) - 1))] * 1e3 if gaps else 0.0
    return {"longest_ms": longest, "share": over / wall if wall else 0.0,
            "p99_ms": p99, "wall_s": wall}


def report(name, rows):
    longest = [r["longest_ms"] for r in rows]
    L.result(f"{name}.longest_gil_hold_ms_max", max(longest), "ms")
    L.result(f"{name}.longest_gil_hold_ms_median", statistics.median(longest), "ms")
    L.result(f"{name}.starvation_share_median", statistics.median(r["share"] for r in rows), "1")
    L.result(f"{name}.gap_p99_ms_median", statistics.median(r["p99_ms"] for r in rows), "ms")
    L.result(f"{name}.wall_s_median", statistics.median(r["wall_s"] for r in rows), "s")


async def main(reps: int, arms: set[str]):
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer.optimizer import optimize_in_process

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=2)
    hass = LoopHass(loop, pool)

    if "idle" in arms:
        rows = [await measure("idle", lambda: asyncio.sleep(2.0)) for _ in range(reps)]
        report("idle", rows)

    for sc in SCENARIOS:
        if "process" in arms:
            # warm the worker (spawn + imports) outside the window
            opt, inp, _ = L.make_solve(sc)
            await cm._await_optimize(hass, opt, inp)
            rows = []
            for _ in range(reps):
                opt, inp, _ = L.make_solve(sc)
                rows.append(await measure(sc, lambda: cm._await_optimize(hass, opt, inp)))
            report(f"process.{sc}", rows)

        if "perturb" in arms:
            # one-line production edit: the shipped route replaced by the fallback
            real = cm._await_process

            async def as_thread(h, fn, *args):
                return await h.async_add_executor_job(fn, *args)

            cm._await_process = as_thread
            try:
                rows = []
                for _ in range(reps):
                    opt, inp, _ = L.make_solve(sc)
                    rows.append(await measure(sc, lambda: cm._await_optimize(hass, opt, inp)))
                report(f"perturb_process_as_thread.{sc}", rows)
            finally:
                cm._await_process = real

        if "thread" in arms:
            rows = []
            for _ in range(reps):
                opt, inp, _ = L.make_solve(sc)
                rows.append(await measure(sc, lambda: hass.async_add_executor_job(
                    optimize_in_process, opt, inp)))
            report(f"thread.{sc}", rows)

        if "noyield" in arms:
            # the in-run yield (optimizer._gil_yield, time.sleep(0) per
            # objective / fused value-and-gradient evaluation) made a no-op:
            # does it bound the hold on the thread route?
            from heatpump_optimizer import optimizer as om
            real_y = om._gil_yield
            om._gil_yield = lambda: None
            try:
                rows = []
                for _ in range(reps):
                    opt, inp, _ = L.make_solve(sc)
                    rows.append(await measure(sc, lambda: hass.async_add_executor_job(
                        optimize_in_process, opt, inp)))
                report(f"thread_noyield.{sc}", rows)
            finally:
                om._gil_yield = real_y

        if "yield100us" in arms:
            # the in-run yield made a REAL sleep (100 us): the waiter can take
            # the GIL while the solver thread is off it
            from heatpump_optimizer import optimizer as om
            real_y = om._gil_yield
            om._gil_yield = lambda: time.sleep(0.0001)
            try:
                rows = []
                for _ in range(reps):
                    opt, inp, _ = L.make_solve(sc)
                    rows.append(await measure(sc, lambda: hass.async_add_executor_job(
                        optimize_in_process, opt, inp)))
                report(f"thread_yield100us.{sc}", rows)
            finally:
                om._gil_yield = real_y

        if "si05" in arms:
            prev = sys.getswitchinterval()
            sys.setswitchinterval(0.0005)
            try:
                rows = []
                for _ in range(reps):
                    opt, inp, _ = L.make_solve(sc)
                    rows.append(await measure(sc, lambda: hass.async_add_executor_job(
                        optimize_in_process, opt, inp)))
                report(f"thread_si05.{sc}", rows)
            finally:
                sys.setswitchinterval(prev)

        if "pickle" in arms:
            opt, inp, _ = L.make_solve(sc)
            t = time.perf_counter()
            blob = pickle.dumps((optimize_in_process, (opt, inp)), protocol=pickle.HIGHEST_PROTOCOL)
            dump_ms = (time.perf_counter() - t) * 1e3
            res = optimize_in_process(opt, inp)
            rblob = pickle.dumps(("ok", res), protocol=pickle.HIGHEST_PROTOCOL)
            t = time.perf_counter()
            pickle.loads(rblob)
            load_ms = (time.perf_counter() - t) * 1e3
            L.result(f"pickle.{sc}.job_bytes", len(blob), "bytes")
            L.result(f"pickle.{sc}.reply_bytes", len(rblob), "bytes")
            L.result(f"pickle.{sc}.job_dumps_ms", dump_ms, "ms")
            L.result(f"pickle.{sc}.reply_loads_ms", load_ms, "ms")

    if "cycle" in arms:
        from homeassistant.util import dt as dtu
        chass = L.make_loop_hass(loop, pool)
        dtu.freeze(L.CYCLE_NOW)
        coord = L.make_coordinator(chass, {"dhw_tank_volume": 180.0}, entry_id="gil")
        await coord._async_update_data()  # warm-up cycle outside the window
        rows = []
        for i in range(reps):
            now = L.CYCLE_NOW + timedelta(minutes=30 * (i + 1))
            dtu.freeze(now)
            L.feed(coord, now)
            rows.append(await measure("cycle", coord._async_update_data))
        report("cycle.process", rows)

    cm._shutdown_process_pool()
    pool.shutdown()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--arms", default="idle,process,perturb,thread,noyield,si05,pickle,cycle")
    a = ap.parse_args()
    clock = L.Clock()
    swap0 = L.swapins()
    L.result("switchinterval_s", sys.getswitchinterval(), "s")
    L.result("load1_start", L.load1(), "1")
    asyncio.run(main(a.reps, set(a.arms.split(","))))
    # executor threads and the worker carry deliberate work, so the BLAS
    # signal is taken over a single-threaded reference section alone
    L.result("whole_run_process_over_main_thread", clock.factor(), "1")
    rclock = L.Clock()
    L.result("reference_solve_cpu_ms", L.ref_ms(), "ms")
    L.tail(rclock, swap0=swap0)
