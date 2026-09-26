"""Shared plumbing for the round-9 D9 verifier-V2 harnesses (not a harness).

Import FIRST: pins BLAS threads before numpy (tests/stress.py's pin, copied)
and puts tests/, tests/hastub and custom_components on sys.path relative to
the cwd, which must be the repository root (root rule: cwd, not __file__).
"""
from __future__ import annotations

import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
for _p in ("tests", "tests/hastub", "custom_components"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import platform  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402

_P0 = time.process_time()
_T0 = time.thread_time()


def result(name, value, unit=""):
    if isinstance(value, float):
        value = f"{value:.6g}"
    print(f"RESULT {name}={value} {unit}".rstrip(), flush=True)


def swapins():
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


def concurrent():
    out = subprocess.run(["ps", "ax", "-o", "args="], capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines() if ("stress.py" in l or "tests/run.sh" in l)
               and "grep" not in l and "gate_lock" not in l)


def trailer(extra_thread_cpu_s: float = 0.0):
    pc = time.process_time() - _P0 - extra_thread_cpu_s
    tc = time.thread_time() - _T0
    result("thread_factor", round(pc / tc, 4) if tc > 0 else 1.0)
    result("load1", round(os.getloadavg()[0], 2))
    result("swapins", swapins())
    result("concurrent_stress_procs", concurrent())
    print(f"# machine: {platform.machine()} {os.cpu_count()}cpu {platform.system()} "
          f"py{platform.python_version()}")
