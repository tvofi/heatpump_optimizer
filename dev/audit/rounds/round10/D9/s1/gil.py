"""D9-s1 gil_hold: longest contiguous GIL hold of an in-process solve.

Metric: max gap (ms) between consecutive 1 ms heartbeat ticks of an asyncio
task on a real event loop while HeatPumpOptimizer.optimize runs in a
concurrent.futures.ThreadPoolExecutor (the #511 in-process fallback path);
starvation share = fraction of the solve's wall time covered by gaps > 5 ms.
Gaps are attributed to a phase by overlap with the solve thread's recorded
intervals: "cont" = optimizer._scoped_minimize calls given a callable jac
(the two-zone continuation, _optimize_space_only.move_starts), else "rest".
Key: heartbeat gaps on the loop thread; the solve is the production
HeatPumpOptimizer.optimize built by tests/golden.py:make.
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D9/s1/gil.py [--perturb noyield|contyield]
Expected (17f1c55fad1b, Darwin arm64, loaded box): all wall numbers provisional.
--perturb realsleep makes optimizer._gil_yield sleep 0.1 ms instead of
sleep(0) (starvation share must fall if sleep(0) is not a handoff).
Null control: scenario 'idle' runs a 3 s sleeping job in the pool.
Perturbation: --perturb noyield makes optimizer._gil_yield a no-op (rest max
gap must rise); --perturb contyield wraps the continuation's fun/jac with
optimizer._gil_yield (cont max gap must fall to the rest level).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, asyncio, argparse, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
import golden
from profiles import solve_inputs
from heatpump_optimizer import optimizer as om

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", default="none")
ap.add_argument("--scenarios", default="idle,winter_two_zone_no_dhw,winter_two_zone_dhw,winter_single_dhw,shoulder_two_zone")
ap.add_argument("--reps", type=int, default=2)
a = ap.parse_args()

if a.perturb == "noyield":
    om._gil_yield = lambda: None
if a.perturb == "realsleep":   # a real (non-zero) sleep forces a GIL handoff
    om._gil_yield = lambda: time.sleep(0.0001)
intervals = []
_sm = om._scoped_minimize
def sm(fun, x0, *aa, **kk):
    jac = kk.get("jac")
    if not callable(jac):
        return _sm(fun, x0, *aa, **kk)
    if a.perturb == "contyield":
        f0, j0 = fun, jac
        def fun(x, *b, _f=f0):
            om._gil_yield(); return _f(x, *b)
        kk["jac"] = lambda x, *b, _j=j0: (om._gil_yield(), _j(x, *b))[1]
    t = time.perf_counter()
    try:
        return _sm(fun, x0, *aa, **kk)
    finally:
        intervals.append((t, time.perf_counter()))
om._scoped_minimize = sm

def solve(name):
    if name == "idle":   # null control: same heartbeat, a sleeping job
        time.sleep(3.0); return None
    b = golden.make(**golden.SCENARIOS[name])
    opt = b["optimizer"]
    return opt.optimize(inputs=solve_inputs(
        initial_state=b["state"], prices=b["prices"], outdoor_temps=b["outdoor"],
        wind_speeds=b["wind"], precipitation=b["rain"], solar_radiation=b["solar"], start_time=golden.START))

async def measure(name, pool):
    ticks = []
    done = asyncio.Event()
    async def beat():
        while not done.is_set():
            ticks.append(time.perf_counter())
            await asyncio.sleep(0.001)
    hb = asyncio.create_task(beat())
    await asyncio.sleep(0.02)
    intervals.clear()
    t0 = time.perf_counter()
    cpu_t = []
    def job():
        s = time.thread_time(); solve(name); cpu_t.append(time.thread_time() - s)
    await asyncio.get_running_loop().run_in_executor(pool, job)
    t1 = time.perf_counter()
    done.set(); await hb
    gaps = [(ticks[i] - ticks[i-1], ticks[i-1], ticks[i]) for i in range(1, len(ticks)) if ticks[i] > t0 and ticks[i-1] < t1]
    def in_cont(g0, g1):
        return any(g0 < e and g1 > s for s, e in intervals)
    cont = [g for g, s, e in gaps if in_cont(s, e)]
    rest = [g for g, s, e in gaps if not in_cont(s, e)]
    starve = sum(g for g, _, _ in gaps if g > 0.005) / (t1 - t0)
    return max(rest or [0]), max(cont or [0]), starve, t1 - t0, cpu_t[0]

def main():
    import resource
    pool = ThreadPoolExecutor(max_workers=1)
    solve("winter_single_no_dhw")  # warm imports
    sub_cpu = 0.0
    t0p, t0t = time.process_time(), time.thread_time()
    for name in a.scenarios.split(","):
        best = None
        for _ in range(a.reps):
            r = asyncio.run(measure(name, pool))
            sub_cpu += r[4]
            best = r if best is None or r[0] + r[1] < best[0] + best[1] else best
        mr, mc, st, wall, _ = best
        print(f"RESULT {name}.max_gap_rest_ms={mr*1e3:.1f} ms (provisional)")
        print(f"RESULT {name}.max_gap_cont_ms={mc*1e3:.1f} ms (provisional)")
        print(f"RESULT {name}.starvation_share={st:.3f} ratio (provisional)")
        print(f"RESULT {name}.solve_wall_ms={wall*1e3:.0f} ms (provisional)")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT deliberate_thread_cpu_ms={sub_cpu*1e3:.0f} ms")
    print(f"RESULT thread_factor={(pc - sub_cpu)/max(tc,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
main()
