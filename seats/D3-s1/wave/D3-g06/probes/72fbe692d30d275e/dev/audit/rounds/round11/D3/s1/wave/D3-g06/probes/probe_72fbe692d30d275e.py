#!/usr/bin/env python3
# Metric: hour 19 of the learned internal-gains profile after one dark fold with residual 0.1 K over 0.5 h; baseline arm vs the mutant arm, per input; cases_moved counts the inputs whose outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_72fbe692d30d275e.py
# EXPECTED RESULT g0_0_baseline=0.1
# EXPECTED RESULT g0_0_mutant=0.0
# EXPECTED RESULT g0_0p01_baseline=0.11
# EXPECTED RESULT g0_0p01_mutant=0.03
# EXPECTED RESULT g0_0p04_baseline=0.14
# EXPECTED RESULT g0_0p04_mutant=0.12
# EXPECTED RESULT cases_moved=3 count
# EXPECTED RESULT null_g0_default=0.4
# EXPECTED RESULT null_g0_0p05=0.15
# EXPECTED RESULT null_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g06 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_internal_gains
#   (coordinator.py:9452 `np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))`), called on a live coordinator over tests/harness.py's FakeHass.
# Perturbation: mutant 72fbe692d30d275e, `np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))` -> `np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * (g0))`, in memory: the method is recompiled from its own
#   source with the one line replaced and bound to the module's globals; the baseline arm calls the class's own method.
#   Direction: g0 < 0.05: baseline lets the hour learn up to 0.15 kW; the mutant caps it at 3*g0 (0 at g0 = 0).
# Reach: g0 is ThermalParameters.internal_gains: not a config key (ThermalParameters._tabled_values has none), so every production coordinator carries the 0.3 default and max(g0, 0.05) == g0; only a params object built with gains < 0.05 separates the arms.
# Should have failed: tests/features.py 'a warm evening hour learns extra gains, tethered under the cap' asserts <= 3*g0 at g0 0.3 only; no check runs a g0 below 0.05 where the 0.05 floor binds.
# Null control: inputs on which both arms must agree (g0_default, g0_0p05); null_moved must be 0.
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

WHEN = datetime(2026, 1, 15, 19, 10, tzinfo=timezone.utc)  # a dark 19:00 interval


def drive(fn, residual=0.1, dt_h=0.5, capacity=None, g0=None, prior19=None):
    """hour 19 of _internal_gains_profile after one fold (None: no profile formed), or the raise."""
    c = coord()
    c._house_heat_loss_samples = 400  # #2223: the heat-loss level has converged, the fold's gate is open
    st = replace(c._current_state)
    st.solar_radiation = 0.0
    if g0 is not None:  # the configured constant the profile is tethered to (ThermalParameters.internal_gains)
        object.__setattr__(c._ctx, "_thermal_params", replace(c._ctx._thermal_params, internal_gains=g0))
    if prior19 is not None:
        c._internal_gains_profile = [float(c._ctx._thermal_params.internal_gains)] * 24
        c._internal_gains_profile[19] = prior19
    ps = [mock.patch.object(co, "_zone_capacity", lambda p: capacity)] if capacity is not None else []
    for p in ps:
        p.start()
    try:
        r = outcome(lambda: fn(c, WHEN, st, residual, dt_h))
    finally:
        for p in ps:
            p.stop()
    if isinstance(r, str):
        return r
    prof = c._internal_gains_profile
    return None if prof is None else round(prof[19], 6)


OLD = 'np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))'
NEW = 'np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * (g0))'
BASE = C._fold_internal_gains
MUT = mutant('_fold_internal_gains', OLD, NEW)
CASES = {'g0_0': dict(g0=0.0), 'g0_0p01': dict(g0=0.01), 'g0_0p04': dict(g0=0.04)}
NULLS = {'g0_default': dict(), 'g0_0p05': dict(g0=0.05)}


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
