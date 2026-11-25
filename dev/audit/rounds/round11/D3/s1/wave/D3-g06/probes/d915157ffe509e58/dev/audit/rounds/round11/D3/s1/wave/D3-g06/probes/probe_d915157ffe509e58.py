#!/usr/bin/env python3
# Metric: the lead predictions _file_lead_predictions files (lead h, value) for an n-point room trajectory, or the exception it raises; baseline arm vs the mutant arm, per input; cases_moved counts the inputs whose outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_d915157ffe509e58.py
# EXPECTED RESULT len4_baseline=[]
# EXPECTED RESULT len4_mutant=raisesIndexError
# EXPECTED RESULT len12_baseline=[(1.0,20.04)]
# EXPECTED RESULT len12_mutant=raisesIndexError
# EXPECTED RESULT len24_baseline=[(1.0,20.04),(3.0,20.12)]
# EXPECTED RESULT len24_mutant=raisesIndexError
# EXPECTED RESULT len48_baseline=[(1.0,20.04),(3.0,20.12),(6.0,20.24)]
# EXPECTED RESULT len48_mutant=raisesIndexError
# EXPECTED RESULT len96_baseline=[(1.0,20.04),(3.0,20.12),(6.0,20.24),(12.0,20.48)]
# EXPECTED RESULT len96_mutant=raisesIndexError
# EXPECTED RESULT cases_moved=5 count
# EXPECTED RESULT null_len5=[(1.0,20.04)]
# EXPECTED RESULT null_len97=[(1.0,20.04),(3.0,20.12),(6.0,20.24),(12.0,20.48),(24.0,20.96)]
# EXPECTED RESULT null_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g06 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._file_lead_predictions
#   (coordinator.py:10231 `if 0 < idx < len(trajectory):`), called on a live coordinator over tests/harness.py's FakeHass.
# Perturbation: mutant d915157ffe509e58, `if 0 < idx < len(trajectory):` -> `if 0 < idx <= len(trajectory):`, in memory: the method is recompiled from its own
#   source with the one line replaced and bound to the module's globals; the baseline arm calls the class's own method.
#   Direction: a trajectory exactly lead/dt_h points long: baseline files the shorter leads and skips that one; the mutant reads trajectory[len] and raises IndexError out of the solve's record step.
# Reach: the plan's room trajectory (OptimizationResult.sensor_trajectory) is exactly lead/dt_h points long: a horizon of 3, 11, 23, 47 or 95 steps at 15 min; the caller is _solve_record at coordinator.py:6461.
# Should have failed: tests/features.py 'each solve files one promise per lead bucket within the horizon' (the _c16 block) drives only a 97-point trajectory; no check files from a trajectory exactly lead/dt_h points long and asserts that lead is skipped without a raise.
# Null control: inputs on which both arms must agree (len5, len97); null_moved must be 0.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, sys, textwrap, time, types
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import coordinator as co  # noqa: E402

C = co.HeatPumpOptimizerCoordinator
CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "solar_aperture_learning_enabled": True, "internal_gains_learning_enabled": True,
    "capacity_curve_enabled": True,
}
_CPU0, _THR0 = time.process_time(), time.thread_time()


def coord(**extra):
    """A live coordinator over the fake bus (tests/features.py's _t2_coord two-liner)."""
    states = {"sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("-5.0", unit="°C")}
    return C(FakeHass(states), FakeEntry(data=dict(CFG, **extra)))


def mutant(name, old, new):
    """The method recompiled from its own source with the one-line mutant, bound to the module's globals."""
    src = textwrap.dedent(inspect.getsource(getattr(C, name)))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    loc = {}
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), dict(co.__dict__), loc)
    f = loc[name]
    return types.FunctionType(f.__code__, co.__dict__, name, f.__defaults__, f.__closure__)


def outcome(fn):
    """fn()'s value, or the exception's class name: a raise is an observable outcome."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        return f"raises {type(exc).__name__}"


def footer():
    cpu, thr = time.process_time() - _CPU0, time.thread_time() - _THR0
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = 0
    print(f"RESULT swapins={sw}")

T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def drive(fn, n):
    """The (lead h, value) pairs _file_lead_predictions files for an n-point room trajectory, or the raise."""
    c = coord()  # mode auto, sysid inactive, 15 min steps: dt_h 0.25, so leads 1/3/6/12/24 h index 4/12/24/48/96
    filed = []
    traj = [20.0 + 0.01 * i for i in range(n)]
    res = SimpleNamespace(sensor_trajectory=lambda two_zone: list(traj), power_schedule=[1.0] * n,
                          dhw_power_schedule=[0.0] * n, prices=[1.0] * n)
    with mock.patch.object(c, "_file_dhw_lead_predictions", lambda *a, **k: None), \
         mock.patch.object(c._accuracy, "note_promise", lambda *a, **k: None), \
         mock.patch.object(c._accuracy, "note_lead_prediction", lambda when, lead, v: filed.append((lead, round(v, 4)))):
        r = outcome(lambda: fn(c, res, T0))
    return r if isinstance(r, str) else filed


OLD = 'if 0 < idx < len(trajectory):'
NEW = 'if 0 < idx <= len(trajectory):'
BASE = C._file_lead_predictions
MUT = mutant('_file_lead_predictions', OLD, NEW)
CASES = {'len4': dict(n=4), 'len12': dict(n=12), 'len24': dict(n=24), 'len48': dict(n=48), 'len96': dict(n=96)}
NULLS = {'len5': dict(n=5), 'len97': dict(n=97)}


def show(v):
    return str(v).replace(" ", "")


moved = 0
for label, kw in CASES.items():
    b, m = drive(BASE, **kw), drive(MUT, **kw)
    moved += int(b != m)
    print(f"RESULT {label}_baseline={show(b)}")
    print(f"RESULT {label}_mutant={show(m)}")
print(f"RESULT cases_moved={moved} count")
null_moved = 0
for label, kw in NULLS.items():
    b, m = drive(BASE, **kw), drive(MUT, **kw)
    null_moved += int(b != m)
    print(f"RESULT null_{label}={show(b)}")
print(f"RESULT null_moved={null_moved} count")
footer()
