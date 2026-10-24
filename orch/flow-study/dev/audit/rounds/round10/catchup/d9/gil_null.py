"""catchup/d9 gil_null: loop starvation by an in-process solve, with the null controls interleaved.

Metric: max gap (ms) and p99 gap between consecutive 1 ms heartbeat ticks
(--hb asyncio: an asyncio task on a real event loop, as D9-s1/gil.py;
--hb thread: a plain threading.Thread doing time.sleep(0.001), an independent
entry point that does not go through the loop), and starvation share = solve
wall covered by gaps > 5 ms. Arms, interleaved per rep in ONE process so load
cancels: idle (a 3 s sleeping job in the ThreadPoolExecutor: null),
thread (the shipped _gil_yield = sleep(0)), noyield (_gil_yield no-op),
realsleep (_gil_yield = sleep(1e-4)), process (the same solve in a spawned
worker process: null for the GIL hold, the shipped path's shape).
Key: defect/null ratio = thread max gap / idle max gap and thread / process.
Command (repo root): PYTHONPATH=tests/hastub python dev/audit/rounds/round10/catchup/d9/gil_null.py [--hb asyncio|thread] [--reps 3]
Expected: idle and process max gap near the timer floor (< 10 ms on a quiet
box); thread >> idle; wall numbers provisional, load-dependent.
Known defect: --hb thread printed thread_factor 39.4 and 2.0 (>1.05) on
2026-10-15, so its runs are rejected; only --hb asyncio numbers are cited.
Baseline: origin/main d749c986d (production byte-identical to 17f1c55fad1b).
Machine: Darwin arm64 Apple M-series 8-core, shared seat box; seat venv python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, asyncio, argparse, threading, multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")

SCEN = "winter_two_zone_dhw"


def solve(name=SCEN):
    import golden
    from profiles import solve_inputs
    b = golden.make(**golden.SCENARIOS[name])
    b["optimizer"].optimize(inputs=solve_inputs(
        initial_state=b["state"], prices=b["prices"], outdoor_temps=b["outdoor"],
        wind_speeds=b["wind"], precipitation=b["rain"], solar_radiation=b["solar"],
        start_time=golden.START))
    return time.process_time()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hb", default="asyncio", choices=("asyncio", "thread"))
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--scenario", default=SCEN)
    a = ap.parse_args()
    from heatpump_optimizer import optimizer as om
    orig = om._gil_yield
    yields = {"thread": orig, "noyield": (lambda: None),
              "realsleep": (lambda: time.sleep(0.0001))}
    tpool = ThreadPoolExecutor(max_workers=1)
    ppool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("spawn"))
    solve(a.scenario)                      # warm in-process
    ppool.submit(solve, a.scenario).result()  # warm the worker
    sub_cpu = [0.0]

    def job_for(arm):
        if arm == "idle":
            return lambda: time.sleep(3.0)
        if arm == "process":
            return lambda: ppool.submit(solve, a.scenario).result()
        def j():
            om._gil_yield = yields[arm]
            s = time.thread_time()
            try:
                solve(a.scenario)
            finally:
                sub_cpu[0] += time.thread_time() - s
                om._gil_yield = orig
        return j

    def stats(ticks, t0, t1):
        g = sorted(ticks[i] - ticks[i - 1] for i in range(1, len(ticks))
                   if ticks[i] > t0 and ticks[i - 1] < t1)
        if not g:
            return 0, 0, 0
        return g[-1], g[min(len(g) - 1, int(0.99 * len(g)))], sum(x for x in g if x > 0.005) / (t1 - t0)

    async def m_async(arm):
        ticks = []; done = asyncio.Event()
        async def beat():
            while not done.is_set():
                ticks.append(time.perf_counter()); await asyncio.sleep(0.001)
        hb = asyncio.create_task(beat()); await asyncio.sleep(0.02)
        t0 = time.perf_counter()
        await asyncio.get_running_loop().run_in_executor(tpool, job_for(arm))
        t1 = time.perf_counter(); done.set(); await hb
        return stats(ticks, t0, t1) + (t1 - t0,)

    def m_thread(arm):
        ticks = []; stop = threading.Event()
        def beat():
            s0 = time.thread_time()
            while not stop.is_set():
                ticks.append(time.perf_counter()); time.sleep(0.001)
            sub_cpu[0] += time.thread_time() - s0
        th = threading.Thread(target=beat); th.start(); time.sleep(0.02)
        t0 = time.perf_counter(); tpool.submit(job_for(arm)).result(); t1 = time.perf_counter()
        stop.set(); th.join()
        return stats(ticks, t0, t1) + (t1 - t0,)

    arms = ("idle", "thread", "noyield", "realsleep", "process")
    res = {k: [] for k in arms}
    t0p, t0t = time.process_time(), time.thread_time()
    for _ in range(a.reps):
        for arm in arms:
            res[arm].append(asyncio.run(m_async(arm)) if a.hb == "asyncio" else m_thread(arm))
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    med = lambda xs: sorted(xs)[len(xs) // 2]
    for arm in arms:
        r = res[arm]
        print(f"RESULT {a.hb}.{arm}.max_gap_ms_median={med([x[0] for x in r])*1e3:.1f} ms (all {[round(x[0]*1e3,1) for x in r]}) (provisional)")
        print(f"RESULT {a.hb}.{arm}.p99_gap_ms_median={med([x[1] for x in r])*1e3:.1f} ms (provisional)")
        print(f"RESULT {a.hb}.{arm}.starvation_median={med([x[2] for x in r]):.3f} ratio (provisional)")
        print(f"RESULT {a.hb}.{arm}.wall_ms_median={med([x[3] for x in r])*1e3:.0f} ms (provisional)")
    mg = {arm: med([x[0] for x in res[arm]]) for arm in arms}
    print(f"RESULT {a.hb}.defect_over_idle={mg['thread']/mg['idle']:.2f} x")
    print(f"RESULT {a.hb}.defect_over_process={mg['thread']/mg['process']:.2f} x")
    print(f"RESULT {a.hb}.noyield_over_thread={mg['noyield']/mg['thread']:.2f} x")
    print(f"RESULT {a.hb}.realsleep_over_thread={mg['realsleep']/mg['thread']:.2f} x")
    print(f"RESULT deliberate_thread_cpu_ms={sub_cpu[0]*1e3:.0f} ms")
    print(f"RESULT thread_factor={(pc - sub_cpu[0]) / max(tc, 1e-9):.3f} (residual after subtracting the deliberate solve and heartbeat threads)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    import resource
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    ppool.shutdown()


if __name__ == "__main__":
    main()
