"""Shared plumbing for the D9-s1 round-9 harnesses (not a harness itself).

Import this FIRST: it pins BLAS threads before numpy loads (tests/stress.py's
pin, copied), and puts tests/ and tests/hastub on sys.path relative to the
cwd, which must be the repository root.
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

import platform
import time


def swapins() -> int:
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    return int(line.split()[1])
    except OSError:
        pass
    return 0


def load1() -> float:
    try:
        return round(os.getloadavg()[0], 2)
    except OSError:
        return -1.0


def machine() -> str:
    return f"{platform.machine()} {os.cpu_count()}cpu {platform.system()} py{platform.python_version()}"


def concurrent_stress() -> int:
    import subprocess
    out = subprocess.run(["ps", "aux"], capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines()
               if ("stress.py" in l or "tests/run.sh" in l) and "grep" not in l)


class Clock:
    """process/thread CPU around a block; thread_factor = process/thread."""

    def __enter__(self):
        self.p0, self.t0, self.w0 = time.process_time(), time.thread_time(), time.perf_counter()
        self.sw0 = swapins()
        return self

    def __exit__(self, *exc):
        self.process_ms = (time.process_time() - self.p0) * 1000
        self.thread_ms = (time.thread_time() - self.t0) * 1000
        self.wall_ms = (time.perf_counter() - self.w0) * 1000
        self.swapins = swapins() - self.sw0
        return False

    @property
    def thread_factor(self) -> float:
        return round(self.process_ms / self.thread_ms, 3) if self.thread_ms > 0 else 1.0


def result(name: str, value, unit: str = "") -> None:
    print(f"RESULT {name}={value} {unit}".rstrip(), flush=True)


def trailer(thread_factor: float, sw: int | None = None) -> None:
    result("thread_factor", thread_factor)
    result("load1", load1())
    result("swapins", swapins() if sw is None else sw)
    result("concurrent_stress_procs", concurrent_stress())
    print(f"# machine: {machine()}")
