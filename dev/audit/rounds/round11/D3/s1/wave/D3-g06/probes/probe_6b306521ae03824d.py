#!/usr/bin/env python3
# Metric: (refusal returned, cop_scale, cop_samples) after one interval of evidence: commanded 4 kW, drawn 1 kW, no heat meter; baseline arm vs the mutant arm, per input; cases_moved counts the inputs whose outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_6b306521ae03824d.py
# EXPECTED RESULT modelled0p1_baseline=('modelled_cop',1.0,0)
# EXPECTED RESULT modelled0p1_mutant=(None,1.05,1)
# EXPECTED RESULT cases_moved=1 count
# EXPECTED RESULT null_modelled3=(None,1.05,1)
# EXPECTED RESULT null_modelled0p05=('modelled_cop',1.0,0)
# EXPECTED RESULT null_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g06 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_cop_evidence
#   (coordinator.py:5382 `if modelled_cop <= 0.1:`), called on a live coordinator over tests/harness.py's FakeHass.
# Perturbation: mutant 6b306521ae03824d, `if modelled_cop <= 0.1:` -> `if modelled_cop < 0.1:`, in memory: the method is recompiled from its own
#   source with the one line replaced and bound to the module's globals; the baseline arm calls the class's own method.
#   Direction: baseline refuses (modelled_cop) and leaves the scale at 1.0; the mutant learns from it: scale 1.0 -> 1.05, one sample counted.
# Reach: modelled_cop is the reference curve's COP for the interval (_cop_reference_curve); exactly 0.1 is the boundary.
# Should have failed: tests/features.py's _fold_cop_evidence checks (the _cf_/_cu_ blocks near line 75990 and 76223) and tests/boost_drift_replay.py never pass modelled_cop at 0.1 and assert COP_REFUSED_MODELLED.
# Null control: inputs on which both arms must agree (modelled3, modelled0p05); null_moved must be 0.
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

def drive(fn, modelled=0.1, heat=None, commanded=4.0, elec=1.0):
    """(refusal code returned, cop_scale after, cop_samples after) for one interval's evidence."""
    c = coord()
    r = outcome(lambda: fn(c, commanded, elec, heat, (modelled, False, None)))
    return (r, round(c._cop_scale, 6), c._cop_samples)


OLD = 'if modelled_cop <= 0.1:'
NEW = 'if modelled_cop < 0.1:'
BASE = C._fold_cop_evidence
MUT = mutant('_fold_cop_evidence', OLD, NEW)
CASES = {'modelled0p1': dict(modelled=0.1)}
NULLS = {'modelled3': dict(modelled=3.0), 'modelled0p05': dict(modelled=0.05)}


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
