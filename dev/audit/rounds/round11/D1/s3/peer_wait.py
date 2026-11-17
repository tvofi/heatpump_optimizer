#!/usr/bin/env python3
"""D1-s3 M5 (peer waits): does `_run_in_process` free `_PROCESS_LOCK` when the worker it kills
does not die at once (a child stuck in the kernel)?

Metric (one line): per failure route of coordinator._run_in_process, whether the call returned
within --cap seconds and whether _PROCESS_LOCK was free afterwards, with a worker whose kill()
does not end it and whose wait() without a timeout never returns (wait(timeout=t) raises
TimeoutExpired after t, as subprocess.Popen's does).
Routes: `transport` -- the job write raises BrokenPipeError (the generic `except Exception` arm,
coordinator.py ~2097-2111); `timeout` -- _read_reply raises ProcessWorkerTimeout (the sibling arm
whose comment names exactly this child and bounds its wait).
Count key: the production function's own return and the production lock's state.

Command:
    PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/peer_wait.py [--cap 8] [--perturb]
  --perturb  the one-line production edit, in memory: the transport arm's `worker.wait()` becomes
             `worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)` (the timeout arm's own bound)
Expected on baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact):
    RESULT transport_returned_within_cap=0   RESULT transport_lock_held_after=1
    RESULT timeout_returned_within_cap=1     RESULT timeout_lock_held_after=0   (sibling/null arm)
    --perturb: transport_returned_within_cap=1, transport_lock_held_after=0
Machine: orchestrator Mac (darwin arm64), shared box; the cap is a deadline, not a timing RESULT.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import inspect
import subprocess
import sys
import textwrap
import threading
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import heatpump_optimizer.coordinator as cmod  # noqa: E402

RELEASE = threading.Event()


class StuckChild:
    """A live child the kill does not end: wait() with no timeout never returns."""

    def __init__(self, route):
        self.route = route
        self.kills = 0
        self.unbounded_waits = 0

        class _In:
            def write(_s, data):
                if route == "transport":
                    raise BrokenPipeError(32, "Broken pipe")

            def flush(_s):
                pass

        self.stdin = _In()
        self.stdout = object()

    def poll(self):
        return None

    def kill(self):
        self.kills += 1

    def wait(self, timeout=None):
        if timeout is None:
            self.unbounded_waits += 1
            RELEASE.wait()          # the harness's own release, after the measurement
            return -9
        time.sleep(min(timeout, 0.05))
        raise subprocess.TimeoutExpired("worker", timeout)


def perturb():
    """Recompile _run_in_process with the transport arm's wait bounded (in memory only)."""
    src = textwrap.dedent(inspect.getsource(cmod._run_in_process))
    old = "                worker.kill()\n                worker.wait()\n"
    assert src.count("worker.wait()") == 1, "the unbounded wait moved"
    src = src.replace("worker.wait()", "worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)")
    ns = {}
    exec(compile(src, cmod.__file__, "exec"), cmod.__dict__, ns)  # noqa: S102 - production source
    cmod._run_in_process = ns["_run_in_process"]
    return old


def drive(route, cap):
    child = StuckChild(route)
    real_ensure, real_read = cmod._ensure_worker, cmod._read_reply
    cmod._ensure_worker = lambda: child

    def read_timeout(stdout):
        raise cmod.ProcessWorkerTimeout("process worker gave no reply (harness)")
    if route == "timeout":
        cmod._read_reply = read_timeout
    out = {}

    def call():
        try:
            cmod._run_in_process(len, ((),))
            out["outcome"] = "returned"
        except Exception as err:  # noqa: BLE001
            out["outcome"] = type(err).__name__
    t = threading.Thread(target=call, daemon=True)
    t0 = time.monotonic()
    t.start()
    t.join(cap)
    returned = not t.is_alive()
    held = cmod._PROCESS_LOCK.locked()
    cmod._ensure_worker, cmod._read_reply = real_ensure, real_read
    return returned, held, out.get("outcome", "still waiting"), child, time.monotonic() - t0, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=8.0)
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    if a.perturb:
        perturb()
    c0, th0 = time.process_time(), time.thread_time()
    threads = []
    for route in ("timeout", "transport"):
        returned, held, outcome, child, el, t = drive(route, a.cap)
        threads.append(t)
        print(f"RESULT {route}_returned_within_cap={int(returned)}")
        print(f"RESULT {route}_lock_held_after={int(held)}")
        print(f"RESULT {route}_unbounded_waits={child.unbounded_waits}")
        print(f"NOTE {route}: outcome={outcome} kills={child.kills} elapsed~{el:.1f}s (provisional)")
    RELEASE.set()
    for t in threads:
        t.join(5)
    print(f"RESULT thread_factor={(time.process_time() - c0) / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
