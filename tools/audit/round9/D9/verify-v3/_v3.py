"""Shared plumbing for the D9 verify-v3 harnesses (round 9, lens V3); not a harness.

Import FIRST: pins BLAS threads before numpy (tests/stress.py's pin, copied) and
puts tests/, tests/hastub and custom_components on sys.path relative to the cwd,
which must be the repository root.
"""
from __future__ import annotations
import os, sys, platform, time
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
for _p in ("tests", "tests/hastub", "custom_components"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_P0 = time.process_time(); _T0 = time.thread_time()


def swapins() -> int:
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    return int(line.split()[1])
    except OSError:
        pass
    return 0


_SW0 = swapins()


def R(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip(), flush=True)


def tf_now() -> float:
    t = time.thread_time() - _T0
    return round((time.process_time() - _P0) / t, 4) if t > 0 else 1.0


def trailer():
    R("thread_factor", tf_now())
    R("load1", round(os.getloadavg()[0], 2))
    R("swapins", swapins() - _SW0)
    print(f"# machine: {platform.machine()} {os.cpu_count()}cpu {platform.system()} "
          f"py{platform.python_version()}")
