#!/usr/bin/env python3
# Metric: live process_worker.py children after three consecutive coordinator._ensure_worker() calls (the call every
#   off-loop solve makes, coordinator.py:_await_optimize), counted as distinct pids whose poll() is None.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_dc6c13ec.py
# Expected: RESULT live_workers_after_3_calls_baseline=1, mutant=3 (each call spawns a fresh worker and drops the old one
#   unreaped); null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_ensure_worker (line 1864,
#   `    if worker is not None and worker.poll() is None:`).
# Perturbation: mutant dc6c13eca2ca1737, `if worker is not None and worker.poll() is None:` -> `if False:`, in memory
#   (recompiled from its own source in a copy of the module namespace, so its `global _PROCESS_WORKER` lives in that
#   copy). Direction: 1 -> 3 live workers (one per solve, unbounded; REPORT-D3-u1d.md's ensure_worker_leak.py measured
#   214 workers of ~67 MB each before the OOM killer under boost_drift_replay.py). Every spawned child is killed at exit.
# Null control: one call per arm (no reuse decision is taken): one live worker in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path.cwd()  # run from the repository root (harness contract)
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402


def mutate(fn, old, new, name=None):
    """Recompile fn's own source with the one-line mutant, in the module namespace (in memory)."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name or fn.__name__]


def tail_results(t0_cpu, t0_thr):
    import time
    pc, tc = time.process_time() - t0_cpu, time.thread_time() - t0_thr
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

import time

t0, t1 = time.process_time(), time.thread_time()
OLD = "if worker is not None and worker.poll() is None:"
MUT = mutate(co._ensure_worker, OLD, "if False:")
SPAWNED = []


def live_after(fn, calls):
    g = fn.__globals__
    g["_PROCESS_WORKER"] = None
    g["_PROCESS_ATEXIT"] = True  # no atexit hook from the probe; children are killed below
    procs = []
    for _ in range(calls):
        procs.append(fn())
    SPAWNED.extend(procs)
    live = {p.pid for p in procs if p.poll() is None}
    for p in procs:
        if p.poll() is None:
            p.kill()
            p.wait()
    g["_PROCESS_WORKER"] = None
    return len(live)


try:
    print(f"RESULT live_workers_after_3_calls_baseline={live_after(co._ensure_worker, 3)} mutant={live_after(MUT, 3)}")
    print(f"RESULT null_moved={int(live_after(co._ensure_worker, 1) != live_after(MUT, 1))} count")
finally:
    for p in SPAWNED:
        if p.poll() is None:
            p.kill()
tail_results(t0, t1)
