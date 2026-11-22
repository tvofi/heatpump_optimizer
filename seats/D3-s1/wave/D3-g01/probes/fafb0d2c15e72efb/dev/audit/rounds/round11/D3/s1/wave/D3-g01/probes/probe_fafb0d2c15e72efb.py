#!/usr/bin/env python3
# Metric: repair issues ("solve_failures") _note_solve_failure creates over N consecutive failed solves on a live
#   coordinator, and the first failure count at which the issue is raised.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_fafb0d2c15e72efb.py
# EXPECTED RESULT issues_after_3_baseline=1 count ; issues_after_3_mutant=0 count
# EXPECTED RESULT first_issue_at_baseline=3 ; first_issue_at_mutant=6
# EXPECTED RESULT null_delta=0 count  (2 failures: below both thresholds, no issue either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_note_solve_failure (reads
#   SOLVE_FAILURE_ISSUE_COUNT at coordinator.py:705; the constant is coordinator.py:822); _create_issue is spied.
# Perturbation: key fafb0d2c15e72efb, `SOLVE_FAILURE_ISSUE_COUNT = 3` -> `= 6`, in memory (mock.patch.object on the
#   module global the function reads at call time). Direction: issue at failure 3 -> at failure 6.
# Null control: two consecutive failures, where neither threshold is reached.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return co.HeatPumpOptimizerCoordinator(FakeHass(dict(states or {})), FakeEntry(data={**CFG, **extra}))


def recompile(cls, name, old, new):
    """The method `name` of `cls` with its single line `old` replaced by `new`, compiled in the module namespace."""
    src = textwrap.dedent(inspect.getsource(getattr(cls, name)))
    assert src.count(old) == 1, f"anchor {old!r} moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = 0
    print(f"RESULT swapins={sw} count")


def drive(n, count):
    c = coord()
    created = []
    with mock.patch.object(co, "SOLVE_FAILURE_ISSUE_COUNT", count), \
         mock.patch.object(co, "_create_issue", lambda *a, **k: created.append(c._solve_failures)):
        for _ in range(n):
            co._note_solve_failure(c, RuntimeError("probe"))
    return created


b, m = drive(8, 3), drive(8, 6)
print(f"RESULT issues_after_3_baseline={len(drive(3, 3))} count")
print(f"RESULT issues_after_3_mutant={len(drive(3, 6))} count")
print(f"RESULT first_issue_at_baseline={b[0] if b else None}")
print(f"RESULT first_issue_at_mutant={m[0] if m else None}")
print(f"RESULT null_delta={abs(len(drive(2, 3)) - len(drive(2, 6)))} count")
tail()
