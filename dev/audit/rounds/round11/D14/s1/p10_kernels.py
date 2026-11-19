"""D14-s1 detector for class P10: CPU work (a model kernel, a fit, a solve, a
batch simulation) that runs outside the process worker -- on the event loop or
on an executor thread.

Metric: per replay arm (tests/replay.py:kernel_routes's arms: base, fallback,
sysid, away, learner, each on the synthetic day through the real coordinator),
the count of outermost CPU-kernel calls by route, the route read off the call
stack (process_worker.run_worker on the stack = worker; tests/harness.py
FakeHass.async_add_executor_job on the stack = executor; else loop). The kernel
set is wider than the barrier's: every ThermalModel.simulate_* and the sysid
entry points (the barrier's), plus optimizer.HeatPumpOptimizer.optimize,
scipy.optimize.minimize / linprog (patched before the package binds them) and
numpy.linalg solve / lstsq / inv / pinv / cholesky. seams = distinct
(kernel, package call site) pairs on the loop in any arm, or on an executor
in any arm but fallback (where the executor is the #511 trade).

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/p10_kernels.py [--arms base,learner] [--perturb]
Expected:  at 92d38ecb seams as printed (exact count over the five arms).
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    tests/replay.py:kernel_routes driving custom_components.heatpump_optimizer.coordinator;
           the kernels above; process_worker:run_worker.
Pre-fix re-find: from the root of an export of c4e1e0c072^ (git archive c4e1e0c072^ | tar -x -C $T;
           cd $T; PYTHONPATH=tests/hastub python3 <abs>/p10_kernels.py --arms base): the base arm replays
           the same 3 h window through run_fixture and the loop count is the pre-#1658 instance.
Perturbation (--perturb, one line): coordinator._await_process replaced by a direct
           in-loop call of the job (the worker hop removed) -> loop calls in base up (up).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import threading
import time
from collections import Counter

ARMS = ("base", "fallback", "sysid", "away", "learner")
MARK = "P10JSON "


def child(arm, perturb):
    sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
    import numpy as np
    import scipy.optimize as so
    tl = threading.local()
    counts = Counter(); sites = Counter()

    def _frames(f):
        while f is not None:
            yield f
            f = f.f_back

    def route():
        f = sys._getframe(2)
        r = "loop"
        while f is not None:
            n = f.f_code.co_name; fn = f.f_code.co_filename.replace("\\", "/")
            if n == "run_worker" and fn.endswith("process_worker.py"):
                return "worker"
            if n == "async_add_executor_job" and fn.endswith("harness.py"):
                r = "executor"
            f = f.f_back
        return r

    def site():
        # The outermost-but-one package frame below the kernel that is not a
        # kernel module; failing that, the innermost frame outside the package.
        f = sys._getframe(2); outside = None
        while f is not None:
            fn = f.f_code.co_filename.replace("\\", "/")
            if "/heatpump_optimizer/" in fn and not fn.endswith(("thermal_model.py", "sysid.py", "optimizer.py", "dhw_planner.py")):
                return f"{fn.rsplit('/', 1)[1]}:{f.f_code.co_name}"
            if outside is None and "/heatpump_optimizer/" not in fn and "p10_kernels" not in fn:
                outside = f"{fn.rsplit('/', 1)[1]}:{f.f_code.co_name}"
            f = f.f_back
        return f"(outside) {outside}"

    def counted(real, label):
        def wrap(*a, **k):
            if not getattr(tl, "inside", 0) and not any(
                    "/heatpump_optimizer/" in fr.f_code.co_filename.replace("\\", "/")
                    for fr in _frames(sys._getframe(1))):
                counts["instrument_only"] += 1  # e.g. tests/stress.py:reference_solve, the replay's ruler
            elif not getattr(tl, "inside", 0):
                r = route()
                counts[r] += 1
                counts[f"{r}:{label}"] += 1
                if r != "worker":
                    sites[f"{r} {site()} {label}"] += 1
            tl.inside = getattr(tl, "inside", 0) + 1
            try:
                return real(*a, **k)
            finally:
                tl.inside -= 1
        wrap.__name__ = getattr(real, "__name__", label)
        return wrap

    so.minimize = counted(so.minimize, "scipy.minimize")
    so.linprog = counted(so.linprog, "scipy.linprog")
    for n in ("solve", "lstsq", "inv", "pinv", "cholesky"):
        setattr(np.linalg, n, counted(getattr(np.linalg, n), f"linalg.{n}"))
    from heatpump_optimizer import thermal_model as tm, sysid, optimizer as opt, coordinator as cm
    for n in dir(tm.ThermalModel):
        if n.startswith("simulate_"):
            setattr(tm.ThermalModel, n, counted(getattr(tm.ThermalModel, n), f"simulate:{n}"))
    for n in ("identify", "identify_slab", "_size_step_power", "_unadoptable"):
        setattr(sysid.SystemIdentification, n, counted(getattr(sysid.SystemIdentification, n), f"sysid:{n}"))
    opt.HeatPumpOptimizer.optimize = counted(opt.HeatPumpOptimizer.optimize, "optimizer.optimize")
    if perturb:
        async def inline(hass, fn, *args):
            return fn(*args)
        cm._await_process = inline
    import replay
    if hasattr(replay, "kernel_routes"):
        out = replay.kernel_routes(arm, replay.KERNEL_ARMS[arm])
    else:  # a tree before #1658 (c4e1e0c072^): the base arm, the same 3 h window, no route flags
        import contextlib, io, tempfile
        from datetime import datetime, timedelta
        from pathlib import Path
        src = json.loads((replay.FIXTURES / "synthetic-dhw-only.json").read_text())
        start = datetime.fromisoformat(src["window"]["start"])
        src["window"]["end"] = (start + timedelta(hours=3.0)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "day.json"
            path.write_text(json.dumps(src))
            with contextlib.redirect_stdout(io.StringIO()):
                run = replay.run_fixture(path, 30)
        out = {"cycles": run["cycles"], "counts": {}}
    print(MARK + json.dumps({"arm": arm, "cycles": out["cycles"], "counts": dict(counts),
                             "sites": dict(sites), "barrier_counts": out["counts"]}))


def main():
    argv = sys.argv[1:]
    if "--child" in argv:
        child(argv[argv.index("--child") + 1], "--perturb" in argv)
        return
    t0 = time.process_time(); th0 = time.thread_time()
    arms = argv[argv.index("--arms") + 1].split(",") if "--arms" in argv else list(ARMS)
    env = {**os.environ, "PYTHONPATH": "tests/hastub"}
    here = os.path.abspath(__file__)
    seams = set(); runs = {}
    for arm in arms:
        cmd = [sys.executable, here, "--child", arm] + (["--perturb"] if "--perturb" in argv else [])
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=1800)
        line = next((ln for ln in p.stdout.splitlines() if ln.startswith(MARK)), None)
        if line is None:
            print(f"ARM {arm} did not run rc={p.returncode}: {p.stderr.strip()[-400:]}")
            continue
        r = json.loads(line[len(MARK):]); runs[arm] = r
        c = r["counts"]
        print(f"ARM {arm} cycles={r['cycles']} worker={c.get('worker', 0)} executor={c.get('executor', 0)} loop={c.get('loop', 0)}")
        for k, v in sorted(r["sites"].items()):
            print(f"  SITE {arm} {k} x{v}")
            rte = k.split(" ")[0]
            if rte == "loop" or (rte == "executor" and arm != "fallback"):
                seams.add(" ".join(k.split(" ")[1:]) + f" [{rte}]")
    for s in sorted(seams):
        print("SEAM", s)
    for arm, r in runs.items():
        c = r["counts"]
        print(f"RESULT {arm}_loop={c.get('loop', 0)} calls")
        print(f"RESULT {arm}_executor={c.get('executor', 0)} calls")
        print(f"RESULT {arm}_worker={c.get('worker', 0)} calls")
        print(f"RESULT {arm}_instrument_only={c.get('instrument_only', 0)} calls (no package frame; not counted)")
    print(f"RESULT arms_run={len(runs)} arms")
    print(f"RESULT seams={len(seams)} (kernel, site) pairs")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
