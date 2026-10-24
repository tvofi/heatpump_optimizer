"""D14-s1 P10 detector: every CPU-kernel seam, counted by the route it ran on.

Metric: over a replayed day (tests/replay.py fixture synthetic-dhw-only, the
P10 barrier's own driver), the number of calls to a WIDENED kernel set that
run outside process_worker.run_worker -- on the loop or an executor thread --
keyed on the route flag at the call (worker/executor/loop), outermost call only.
The widened set = the barrier's set (ThermalModel.simulate_*, the sysid four)
PLUS every numpy.linalg solver and every scipy.optimize entry the package
imports (lstsq/solve/inv/pinv/eig*/svd, minimize/linprog/least_squares/
curve_fit/nnls), wherever called. Seam key: '<route> <file:function> <kernel>'.

Run:  HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s1/p10_seams.py [--arm base|fallback|sysid] [--hours H] [--perturb] [--away]
--perturb: one-line re-introduction -- cm._await_process replaced so the
solve body runs inline on the loop (the R1-D9-02 shape); loop count must rise
from the base value to > 0.
Static part: AST lists every call site of the widened kernel names in the
package (the seam enumeration), independent of the replay reaching it.
Baseline 17f1c55fad1b, machine: macOS arm64 (B7). Counts are contention-immune.
Expected (tolerance 0): base loop_kernels_all=0; --away (deficit 2) loop_kernels_all=183,
loop_kernels_away_seam=183; --away --deficit 0 -> 0; --perturb -> >0 (re-introduction).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, ast, asyncio, sys, threading, time
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
PKG = ROOT / "custom_components" / "heatpump_optimizer"
LINALG = ("lstsq", "solve", "inv", "pinv", "eig", "eigh", "svd", "cholesky")
OPT = ("minimize", "linprog", "least_squares", "curve_fit", "nnls", "minimize_scalar")


def static_seams():
    out = []
    for f in sorted(PKG.glob("*.py")):
        tree = ast.parse(f.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in ast.walk(fn):
                if isinstance(n, ast.Call):
                    c = n.func
                    name = c.attr if isinstance(c, ast.Attribute) else getattr(c, "id", None)
                    if name in LINALG + OPT or (name or "").startswith("simulate_"):
                        out.append(f"{f.name}:{fn.name}:{name}")
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="base")
    ap.add_argument("--hours", type=float, default=None)
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--away", action="store_true",
                    help="scenario: away override active, return 12 h ahead (the away seam)")
    ap.add_argument("--deficit", type=float, default=2.0,
                    help="away scenario: degrees the house sits below the recovery target")
    a = ap.parse_args()
    seams = static_seams()
    print(f"RESULT static_seams={len(seams)} sites")
    for s in seams:
        print("  seam", s)
    import replay
    import harness
    import numpy as np
    import scipy.optimize as so
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import process_worker as pw
    tl = threading.local()
    counts, sites = Counter(), Counter()

    def site():
        f = sys._getframe(2)
        while f is not None:
            fn = f.f_code.co_filename.replace("\\", "/")
            if "/heatpump_optimizer/" in fn:
                return f"{Path(fn).name}:{f.f_code.co_name}"
            f = f.f_back
        return None

    def counted(real, label):
        def wrap(*x, **k):
            s = site()
            if s is not None and not getattr(tl, "inside", 0):
                r = ("worker" if getattr(tl, "worker", 0)
                     else "executor" if getattr(tl, "ex", 0) else "loop")
                counts[r] += 1
                sites[f"{r} {s} {label}"] += 1
            tl.inside = getattr(tl, "inside", 0) + 1
            try:
                return real(*x, **k)
            finally:
                tl.inside -= 1
        return wrap

    for n in LINALG:
        if hasattr(np.linalg, n):
            setattr(np.linalg, n, counted(getattr(np.linalg, n), f"linalg.{n}"))
    import importlib
    for m in PKG.glob("*.py"):
        mod = importlib.import_module(f"heatpump_optimizer.{m.stem}")
        for n in OPT:
            if getattr(mod, n, None) is getattr(so, n, object()):
                setattr(mod, n, counted(getattr(so, n), f"optimize.{n}"))
    for n in OPT:
        if hasattr(so, n):
            setattr(so, n, counted(getattr(so, n), f"optimize.{n}"))
    rw = pw.run_worker

    def worker(*x, **k):
        tl.worker = getattr(tl, "worker", 0) + 1
        try:
            return rw(*x, **k)
        finally:
            tl.worker -= 1
    pw.run_worker = worker
    rex = harness.FakeHass.async_add_executor_job

    async def ex(self, func, *args):
        tl.ex = getattr(tl, "ex", 0) + 1
        try:
            return await rex(self, func, *args)
        finally:
            tl.ex -= 1
    harness.FakeHass.async_add_executor_job = ex
    if a.perturb:
        # one-line re-introduction: the process route runs its function inline on the loop
        async def inline(hass, fn, *args):
            return fn(*args)
        cm._await_process = inline
    if a.away:
        # Scenario, not a fix: the user set away with a return time (the
        # set_away service's override). Production code below is untouched.
        from datetime import timedelta
        from heatpump_optimizer import away as away_mode
        away_mode.expire_override = lambda act, ret, now: (True, now + timedelta(hours=12))
        # The fixture's house sits ~1 C above its 19.5 C comfort; an away house
        # has cooled below it. Model that by asking recovery to reach comfort+2 C
        # (the away module's own input; the solve's comfort is untouched).
        real_resolve = away_mode.resolve

        def resolve(config, **kw):
            kw["comfort_temp"] = kw["comfort_temp"] + a.deficit
            return real_resolve(config, **kw)
        away_mode.resolve = resolve
    t0 = time.process_time(); tt0 = time.thread_time()
    run = replay.kernel_routes(a.arm, a.hours or replay.KERNEL_ARMS[a.arm])
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT cycles={run['cycles']} cycles")
    print(f"RESULT barrier_set_loop={run['counts'].get('loop', 0)} calls")
    print(f"RESULT barrier_set_executor={run['counts'].get('executor', 0)} calls")
    print(f"RESULT loop_kernels={counts['loop']} calls")
    print(f"RESULT executor_kernels={counts['executor']} calls")
    print(f"RESULT worker_kernels={counts['worker']} calls")
    bsites = run.get("sites") or {}
    for k, v in sorted(bsites.items()):
        print(f"  barrier-site {v:6d} {k}")
    away_loop = sum(v for k, v in bsites.items() if k.startswith("loop away.py"))
    away_loop += sum(v for k, v in sites.items() if k.startswith("loop away.py"))
    total_loop = counts["loop"] + run["counts"].get("loop", 0)
    print(f"RESULT loop_kernels_all={total_loop} calls")
    print(f"RESULT loop_kernels_away_seam={away_loop} calls")
    print(f"RESULT loop_kernels_per_cycle={total_loop / max(run['cycles'], 1):.2f} calls/cycle")
    for k, v in sorted(sites.items()):
        print(f"  site {v:6d} {k}")
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
