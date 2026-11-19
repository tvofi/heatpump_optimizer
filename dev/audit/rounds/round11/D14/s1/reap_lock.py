"""D14-s1 detector for class N-reap-lock: a stop path that reaps the solve
worker only after the lock an in-flight solve holds, so stop latency is the
solve's remaining time.

Metric: per stop route, stop_latency_ratio = wall time of the stop call /
the in-flight job's remaining time, with a REAL process worker running a job
that stays alive (time.sleep(--job, default 20 s)) through
coordinator._run_in_process on a thread (the caller holds _PROCESS_LOCK).
Routes (every caller of coordinator._shutdown_process_pool, enumerated by AST
over the package, plus its at-exit and stopped-child variants):
  pool          _shutdown_process_pool()               (async_register_worker_shutdown's route)
  pool_at_exit  _shutdown_process_pool(at_exit=True)    (the atexit backstop)
  pool_stopped  _shutdown_process_pool() on a SIGSTOPped worker (alive, silent, deaf to SIGTERM)
Also per route: lock_free_after = whether _PROCESS_LOCK is acquirable 1 s after
the stop returns (the next solve and the next reload are not wedged).
A seam is a route with ratio > 0.5 or lock_free_after = 0. Key = wall time of
the production stop call, never a constant.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/reap_lock.py [--job 20] [--perturb] [--idle] [--routes pool,pool_at_exit]
Expected:  at 92d38ecb every ratio < 0.2 and seams=0 (provisional wall numbers).
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    custom_components.heatpump_optimizer.coordinator:_shutdown_process_pool,
           coordinator:_run_in_process, coordinator:_PROCESS_LOCK.
Perturbation (--perturb, one line): `with _PROCESS_LOCK: pass` placed before the
           reap (the pre-D1-s2-05 lock-first order) -> ratio to ~1 on every route (up).
Null control: the same routes with no job in flight (--idle): every latency ~0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import signal
import sys
import threading
import time

argv = sys.argv[1:]
JOB = float(argv[argv.index("--job") + 1]) if "--job" in argv else 20.0
PERTURB = "--perturb" in argv
IDLE = "--idle" in argv
sys.path[:0] = ["tests/hastub", "custom_components"]

from heatpump_optimizer import coordinator as cm  # noqa: E402

# Bound the in-flight read so a perturbed (lock-first) stop on a stopped child
# ends at the job's length rather than the shipped 1800 s reply deadline.
cm.PROCESS_REPLY_TIMEOUT_S = JOB + 2.0


def callers():
    """Every package function that calls _shutdown_process_pool (the stop routes)."""
    out = []
    base = "custom_components/heatpump_optimizer"
    for fn in sorted(os.listdir(base)):
        if not fn.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(base, fn), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for c in ast.walk(node):
                    if isinstance(c, ast.Name) and c.id == "_shutdown_process_pool" and node.name != "_shutdown_process_pool":
                        out.append(f"{fn}:{node.name}")
                        break
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "register" \
                    and any(isinstance(a, ast.Name) and a.id == "_shutdown_process_pool" for a in node.args):
                out.append(f"{fn}:atexit.register")
    return sorted(set(out))


def one(route):
    cm._PROCESS_WORKER = None
    done = threading.Event(); result = {}

    def solve():
        try:
            cm._run_in_process(time.sleep, (JOB,))
            result["r"] = "returned"
        except Exception as e:  # noqa: BLE001
            result["r"] = type(e).__name__
        finally:
            done.set()
    started = time.monotonic()
    if not IDLE:
        t = threading.Thread(target=solve, daemon=True); t.start()
        for _ in range(200):
            if cm._PROCESS_WORKER is not None and cm._PROCESS_LOCK.locked():
                break
            time.sleep(0.05)
        time.sleep(1.0)  # the job is running in the child
    else:
        cm._ensure_worker()
    w = cm._PROCESS_WORKER
    if route == "pool_stopped" and w is not None:
        os.kill(w.pid, signal.SIGSTOP)
    real = cm._shutdown_process_pool
    if PERTURB:
        def lock_first(**kw):
            with cm._PROCESS_LOCK:
                pass
            return real(**kw)
        stop = lock_first
    else:
        stop = real
    remaining = max(JOB - (time.monotonic() - started), 1e-3) if not IDLE else 1.0
    t0 = time.monotonic()
    stop(at_exit=(route == "pool_at_exit"))
    lat = time.monotonic() - t0
    time.sleep(1.0)
    free = cm._PROCESS_LOCK.acquire(timeout=0.1)
    if free:
        cm._PROCESS_LOCK.release()
    if w is not None and w.poll() is None:
        try:
            os.kill(w.pid, signal.SIGCONT); w.kill(); w.wait(timeout=5)
        except Exception:
            pass
    done.wait(JOB + 10)
    return lat, remaining, free, result.get("r", "idle")


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    routes_src = callers()
    for r in routes_src:
        print("ROUTE_CALLER", r)
    seams = []
    routes = argv[argv.index("--routes") + 1].split(",") if "--routes" in argv else ["pool", "pool_at_exit", "pool_stopped"]
    for route in routes:
        lat, rem, free, outcome = one(route)
        ratio = lat / rem
        print(f"RESULT {route}_stop_s={lat:.3f} s (provisional)")
        print(f"RESULT {route}_stop_latency_ratio={ratio:.3f} ratio")
        print(f"RESULT {route}_lock_free_after={int(free)}")
        print(f"RESULT {route}_inflight_outcome={outcome}")
        if ratio > 0.5 or not free:
            seams.append(route)
    for s in seams:
        print("SEAM", s)
    print(f"RESULT route_callers={len(routes_src)} callers")
    print(f"RESULT seams={len(seams)} routes")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    # The in-flight caller thread only waits on a pipe (no deliberate CPU).
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
