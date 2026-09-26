"""Verifier V3 (lc unit, G1) real-HA reachability check of D3-s1-91.

Lens question: on real Home Assistant 2026.2.3, dt_util.now() returns an
AWARE datetime by default (DEFAULT_TIME_ZONE defaults to UTC there, unlike
tests/hastub's stub which is naive unless HASTUB_TZ is set). So on real HA
the guard at coordinator.py:8384 (`if when.tzinfo is None and now.tzinfo is
not None: when = when.replace(tzinfo=now.tzinfo)`) is ALWAYS live whenever a
persisted immersion-event timestamp is naive -- confirming the finding's
"only crashes, never silently drifts" framing is about the test gate's
default clock, not about production: in real production this guard is not
dead, it is exercised on every stored naive-ISO event and its absence would
crash real installs immediately, not just under a HASTUB_TZ=... test.

Metric: with a real dt_util.now() (unpatched, genuine tzinfo=UTC) and one
naive stored ISO event, GUARD_ON vs GUARD_OFF (guard line removed the same
way the finder's harness removes it) on real HA's
`_immersion_dhw_margin`-equivalent inline logic.

Run:      PYTHONPATH=custom_components:tests /root/venvha/bin/python \
            tools/audit/round9/D3/verify-v3-lc/D3-s1-91_realha_reach.py
Baseline: 79aa98ec (handoff/audit-r9-evidence)
Expected: guard_on returns a float with no error; guard_off raises TypeError
comparing naive vs aware, on real HA's OWN clock with no perturbation of
HASTUB_TZ needed (there is no HASTUB_TZ on real HA).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import inspect
import re
import sys
import textwrap
import time
import resource

import typing
typing.ByteString = bytes  # CPython 3.14 compat shim

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402


def _guard_off(func, pattern, repl=""):
    src = textwrap.dedent(inspect.getsource(func))
    new_src, n = re.subn(pattern, repl, src, count=1)
    assert n == 1, f"pattern not found once: {pattern!r}"
    ns = dict(vars(sys.modules[func.__module__]))
    exec(compile(new_src, f"<guard_off:{func.__name__}>", "exec"), ns)
    return ns[func.__name__]


class _Ctx:
    def __init__(self):
        self._config = {"immersion_feedback_enabled": True}


class _FakeCoord:
    def __init__(self, events):
        self._ctx = _Ctx()
        self._immersion_events = events


def main():
    t0 = time.process_time()
    on = C.HeatPumpOptimizerCoordinator._immersion_dhw_margin
    off = _guard_off(
        on,
        r" {8}if when\.tzinfo is None and now\.tzinfo is not None:\n"
        r" {12}when = when\.replace\(tzinfo=now\.tzinfo\)\n",
    )
    coord = _FakeCoord(
        ["2026-01-05T00:00:00", "2026-01-10T00:00:00", "2026-01-14T00:00:00"]
    )
    now = dt_util.now()  # REAL HA clock, no patching, no HASTUB_TZ
    now_aware = now.tzinfo is not None
    a = on(coord, now)
    try:
        b = off(coord, now)
        b_repr = repr(b)
        b_raised = 0
    except TypeError as err:
        b_repr = f"raises {err}"
        b_raised = 1
    cpu = time.process_time() - t0
    print(f"real HA now={now!r} tzaware={now_aware}")
    print(f"guard_on={a!r} guard_off={b_repr}")
    print(f"RESULT realha_now_tzaware={int(now_aware)}")
    print(f"RESULT realha_guard_off_raises_typeerror={b_raised}")
    print(f"RESULT realha_guard_on_ok={int(isinstance(a, float))}")
    print(f"RESULT cpu_s={cpu:.3f}")
    print("RESULT thread_factor=1.0 (no numpy/BLAS on this path)")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_minflt}")


if __name__ == "__main__":
    main()
