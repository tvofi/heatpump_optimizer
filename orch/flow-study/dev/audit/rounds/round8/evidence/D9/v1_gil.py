"""D9 round 8 verifier v1 -- loop starvation by an in-interpreter solve, against a pure-Python null.

Metric (v1, one line): on a real asyncio loop with a 1 ms heartbeat task, while ONE real
  optimizer.optimize() (stress.build_case winter / one zone / DHW, the shape the default
  coordinator solves) runs on a real ThreadPoolExecutor thread in THIS interpreter -- the
  #511 fallback's execution shape -- the share of executor-busy wall time spent in heartbeat
  gaps longer than T, at T = 5, 10 and 20 ms, plus the max and p99 gap.
Why three thresholds: CPython's switch interval is 5 ms (sys.getswitchinterval), so ANY
  CPU-bound Python thread keeps a waiting loop out for ~5 ms per hand-off; a 5 ms cut sits on
  that structural boundary. 10/20 ms read what exceeds the interpreter's own hand-off.
Arms, interleaved in one session so they share the box's load:
  idle   : no executor work (box-contention floor)
  pybusy : NULL CONTROL -- a pure-Python arithmetic loop on the executor for the solve's wall
           time (any CPU-bound executor job; what HA itself tolerates)
  solve  : the real optimize() on the executor
  solve_noyield : PERTURBATION -- optimizer._gil_yield replaced by a no-op (restored in finally)
  --switch S : second perturbation, sys.setswitchinterval(S) for every arm
Command (repo root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 TMPDIR=/home/claude/audit-r8/tmp/D9-v1 \
  python3 tools/audit/round8/D9/v1_gil.py [--rounds 3] [--switch 0.001]
Expected: every wall number PROVISIONAL (shared 4-vCPU box); the ordering between arms is the
  reading. Baseline cdf82daa.
"""
from __future__ import annotations

import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import asyncio
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
import stress  # noqa: E402

O = stress.optimizer_module
POOL = ThreadPoolExecutor(max_workers=1)
BUSY = {"on": False, "cpu": 0.0}
SPEC = dict(season="winter", two_zone=False, dhw=True)


def job_solve():
    t0 = time.thread_time()
    BUSY["on"] = True
    try:
        stress.build_case(**SPEC)
    finally:
        BUSY["on"] = False
        BUSY["cpu"] += time.thread_time() - t0


def job_pybusy(seconds):
    t0 = time.thread_time()
    BUSY["on"] = True
    try:
        end = time.perf_counter() + seconds
        x = 0
        while time.perf_counter() < end:
            for i in range(200):
                x += i * i
    finally:
        BUSY["on"] = False
        BUSY["cpu"] += time.thread_time() - t0


async def measure(fn, *a):
    gaps = []
    stop = asyncio.Event()

    async def hb():
        last = time.perf_counter()
        while not stop.is_set():
            await asyncio.sleep(0.001)
            now = time.perf_counter()
            if BUSY["on"]:
                gaps.append(now - last)
            last = now

    t = asyncio.get_running_loop().create_task(hb())
    await asyncio.sleep(0.02)
    w0 = time.perf_counter()
    if fn is None:
        BUSY["on"] = True
        await asyncio.sleep(a[0])
        BUSY["on"] = False
    else:
        await asyncio.get_running_loop().run_in_executor(POOL, fn, *a)
    wall = time.perf_counter() - w0
    stop.set()
    await t
    return np.array(gaps) * 1000.0, wall


def summarise(g):
    tot = max(g.sum(), 1e-9)
    return {
        "busy_ms": g.sum(),
        "s5": g[g > 5].sum() / tot, "s10": g[g > 10].sum() / tot, "s20": g[g > 20].sum() / tot,
        "max": g.max() if g.size else 0.0, "p99": np.percentile(g, 99) if g.size else 0.0,
        "med": np.median(g) if g.size else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--switch", type=float, default=0.0)
    args = ap.parse_args()
    sw0 = sys.getswitchinterval()
    y0 = O._gil_yield
    if args.switch:
        sys.setswitchinterval(args.switch)
    cpu0, th0 = time.process_time(), time.thread_time()
    res = {k: [] for k in ("idle", "pybusy", "solve", "solve_noyield")}
    loop = asyncio.new_event_loop()
    try:
        for _ in range(args.rounds):
            g, wall = loop.run_until_complete(measure(job_solve))
            res["solve"].append(summarise(g))
            O._gil_yield = lambda: None
            try:
                g, _w = loop.run_until_complete(measure(job_solve))
            finally:
                O._gil_yield = y0
            res["solve_noyield"].append(summarise(g))
            g, _w = loop.run_until_complete(measure(job_pybusy, wall))
            res["pybusy"].append(summarise(g))
            g, _w = loop.run_until_complete(measure(None, min(wall, 3.0)))
            res["idle"].append(summarise(g))
    finally:
        O._gil_yield = y0
        sys.setswitchinterval(sw0)
        loop.close()
        POOL.shutdown(wait=True)
    tag = f"sw{args.switch or sw0:g}"
    for arm, rows in res.items():
        for key in ("s5", "s10", "s20", "max", "p99", "med", "busy_ms"):
            vals = [r[key] for r in rows]
            unit = "ratio" if key.startswith("s") and key != "s" else "ms-wall"
            print(f"RESULT {tag}.{arm}.{key}={np.median(vals):.4f} {unit} (provisional; median of "
                  f"{len(vals)}: {', '.join(f'{v:.3f}' for v in vals)})")
    cpu, th = time.process_time() - cpu0, time.thread_time() - th0
    print(f"RESULT deliberate_executor_cpu_ms={BUSY['cpu'] * 1000:.0f} ms-cpu")
    print(f"RESULT thread_factor={(cpu - BUSY['cpu']) / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            swi = [ln.split()[1] for ln in fh if ln.startswith("pswpin")]
        print(f"RESULT swapins={swi[0] if swi else 0}")
    except OSError:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
