#!/usr/bin/env python3
# Metric: _capacity_envelope after one nameplate fold whose thermal figure is exactly 0 kW; baseline arm vs the mutant arm, per input; cases_moved counts the inputs whose outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_dff127b334682936.py
# EXPECTED RESULT cop0_baseline={}
# EXPECTED RESULT cop0_mutant={-4:[0.0,1]}
# EXPECTED RESULT heat0_baseline={}
# EXPECTED RESULT heat0_mutant={-4:[0.0,1]}
# EXPECTED RESULT draw0_baseline={}
# EXPECTED RESULT draw0_mutant={-4:[0.0,1]}
# EXPECTED RESULT cases_moved=3 count
# EXPECTED RESULT null_cop_neg={}
# EXPECTED RESULT null_cop2={-4:[8.0,1]}
# EXPECTED RESULT null_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g06 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_capacity_envelope
#   (coordinator.py:9327 `if not np.isfinite(thermal_kw) or thermal_kw <= 0.0:`), called on a live coordinator over tests/harness.py's FakeHass.
# Perturbation: mutant dff127b334682936, `if not np.isfinite(thermal_kw) or thermal_kw <= 0.0:` -> `if not np.isfinite(thermal_kw) or thermal_kw < 0.0:`, in memory: the method is recompiled from its own
#   source with the one line replaced and bound to the module's globals; the baseline arm calls the class's own method.
#   Direction: baseline leaves the envelope empty; the mutant opens bucket -4 at 0.0 kW with one nameplate sample counted.
# Reach: thermal_kw = observed_cop * measured_power or a measured heat_kw; through _fold_cop_evidence (coordinator.py:5422) observed_cop > 0.1 and heat 0 is refused as observed_cop, so 0 kW needs a 0 kW measured draw with a passing observed COP or a direct call; tests/features.py calls the symbol directly (#17, round-5 D3-06 block).
# Should have failed: tests/features.py 'a non-positive thermal figure never enters the learned envelope' (_c14_neg, round-5 D3-06 block) feeds observed_cop -1.0 only; no check feeds a thermal figure of exactly 0 kW.
# Null control: inputs on which both arms must agree (cop_neg, cop2); null_moved must be 0.
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

def drive(fn, observed=0.0, heat=None, measured=4.0):
    """_capacity_envelope after one fold at nameplate, -10 C outdoor (bucket -4), 4 kW measured draw."""
    c = coord()
    c._current_state.outdoor_temperature = -10.0
    c._current_action = {"power": 5.0}  # commanded at nameplate, as tests/features.py #17 drives it
    c._measured_power = measured
    r = outcome(lambda: fn(c, observed, heat))
    return r if isinstance(r, str) else dict(c._capacity_envelope)


OLD = 'if not np.isfinite(thermal_kw) or thermal_kw <= 0.0:'
NEW = 'if not np.isfinite(thermal_kw) or thermal_kw < 0.0:'
BASE = C._fold_capacity_envelope
MUT = mutant('_fold_capacity_envelope', OLD, NEW)
CASES = {'cop0': dict(observed=0.0), 'heat0': dict(observed=2.0, heat=0.0), 'draw0': dict(observed=2.0, measured=0.0)}
NULLS = {'cop_neg': dict(observed=-1.0), 'cop2': dict(observed=2.0)}


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
