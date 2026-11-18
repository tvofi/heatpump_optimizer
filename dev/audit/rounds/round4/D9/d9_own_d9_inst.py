"""VERIFIER-OWN harness for D9-INST (seat verify-0-1, round 4).

Tests the instrument finding's first half by construction: the harness
contract's ``thread_factor = process_cpu / thread_cpu`` rejection rule
("> 1.05") cannot be satisfied by any harness that pushes real work
through a real ``ThreadPoolExecutor`` (as ``h2_cycle.py`` deliberately
does, per the README's own FakeHass trap), because a second thread doing
real CPU work puts its CPU into ``time.process_time()`` but not into
``time.thread_time()`` -- BY CONSTRUCTION, with no BLAS anywhere.

This harness imports NO numpy at all (the strongest form: nothing that
could spin a BLAS thread pool is even loaded), pins the five thread
variables per the contract, runs a pure-Python busy loop on the main
thread and another of ~30 % of its size on a real
``ThreadPoolExecutor(max_workers=1)`` thread, and prints the contract's
ratio exactly the way ``d9common.telemetry`` computes it.

METRIC DEFINITIONS:
  own_pure_python_thread_factor = (process_time delta) / (thread_time
      delta) over the whole measured span, main+executor   (ratio)
  own_expected_factor = 1 + (executor-thread CPU) / (main-thread CPU)
      predicted from the two measured components            (ratio)
  own_idle_control_thread_factor = the same ratio with the executor
      job disabled -- must be ~1.0                          (ratio)

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/d9_own_d9_inst.py

EXPECTED: own_pure_python_thread_factor ~1.25-1.35 (matches h2's 1.29
shape); own_idle_control_thread_factor ~0.99-1.01.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import subprocess  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

# deliberately NO numpy import anywhere in this harness

N_MAIN = 30_000_000   # pure-Python iterations on the main thread
N_EXEC = 9_000_000    # ~30 % as many on the executor thread


def result(name, value, unit=""):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}".rstrip(), flush=True)


def load1():
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def concurrent_procs():
    out = subprocess.run(
        ["ps", "aux"], capture_output=True, text=True, timeout=20
    ).stdout
    n = 0
    for line in out.splitlines():
        if "grep" in line:
            continue
        if "stress.py" in line or "tests/run.sh" in line:
            n += 1
    return n


def busy(n):
    acc = 0
    for i in range(n):
        acc += i % 7
    return acc


def measured(with_executor: bool):
    pool = ThreadPoolExecutor(max_workers=1)
    p0, t0 = time.process_time(), time.thread_time()
    fut = pool.submit(busy, N_EXEC) if with_executor else None
    busy(N_MAIN)                      # main-thread work
    if fut is not None:
        fut.result()                  # executor-thread work joins here
    proc, thr = time.process_time() - p0, time.thread_time() - t0
    pool.shutdown()
    return proc, thr


def main():
    print("# verifier-own D9-INST harness; NO numpy imported")
    print(f"# procs_at_start={concurrent_procs()} load1={load1():.2f}")
    proc, thr = measured(with_executor=False)   # idle control
    result("own_idle_control_thread_factor",
           float(proc / thr) if thr else float("nan"))
    proc, thr = measured(with_executor=True)
    result("own_pure_python_thread_factor",
           float(proc / thr) if thr else float("nan"))
    result("own_span_process_cpu_s", float(proc), "s")
    result("own_span_thread_cpu_s", float(thr), "s")
    # the executor-thread CPU is the difference; the predicted factor is
    # 1 + exec/main -- print both so a reader can check the arithmetic
    exec_cpu = proc - thr
    result("own_second_thread_cpu_s", float(exec_cpu), "s")
    result("own_expected_factor", float(1.0 + exec_cpu / thr) if thr
           else float("nan"))
    result("thread_factor", float(proc / thr) if thr else float("nan"))
    result("load1", load1())
    result("concurrent_gate_procs", concurrent_procs())


if __name__ == "__main__":
    main()
