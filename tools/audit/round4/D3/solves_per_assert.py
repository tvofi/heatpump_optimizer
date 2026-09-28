#!/usr/bin/env python3
"""D3 round 4 -- does a gate script solve more than it asserts?

METRIC: for one gate script, the number of `HeatPumpOptimizer.optimize` calls
it makes divided by the number of checks it reports -- a count, so it is
contention-immune, and it is the cost side of "what the suite cannot fail on":
a script that solves 22 plans and asserts 8 things paid 22 solves for 8 checks.

RUN (from the repository root, one script per invocation):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/solves_per_assert.py tests/validate.py

EXPECTED: prints RESULT solves=<n>, RESULT checks=<n>, RESULT solves_per_check.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import io
import re
import runpy
import sys
import time
from contextlib import redirect_stdout

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

COUNT = {"optimize": 0}
_orig = HeatPumpOptimizer.optimize


def _wrapped(self, *a, **k):
    COUNT["optimize"] += 1
    return _orig(self, *a, **k)


HeatPumpOptimizer.optimize = _wrapped

_PASSED = re.compile(r"^ALL (\d+) .* PASSED\s*$", re.M)
_FAILED = re.compile(r"^\s*(\d+) of (\d+) .* FAILED\s*$", re.M)
_OK = re.compile(r"^\s{2,}ok\s", re.M)


def main() -> int:
    script = sys.argv[1]
    buf = io.StringIO()
    t0 = time.monotonic()
    rc = 0
    try:
        with redirect_stdout(buf):
            runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        rc = int(exc.code or 0)
    secs = time.monotonic() - t0
    out = buf.getvalue()
    m = _PASSED.search(out) or _FAILED.search(out)
    if m:
        checks = int(m.group(2) if m.lastindex == 2 else m.group(1))
    else:
        checks = len(_OK.findall(out))
    print(f"RESULT script={script}")
    print(f"RESULT rc={rc}")
    print(f"RESULT solves={COUNT['optimize']} count")
    print(f"RESULT checks={checks} count")
    ratio = COUNT["optimize"] / checks if checks else float("inf")
    print(f"RESULT solves_per_check={ratio:.3f} ratio")
    print(f"RESULT wall={secs:.1f} s (provisional: load1={os.getloadavg()[0]:.2f})")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
