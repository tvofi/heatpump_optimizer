#!/usr/bin/env python3
# Metric: (n, scale, mx, my) of the solar-aperture regression after one fold; baseline arm vs the mutant arm, per input; cases_moved counts the inputs whose outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_96fe4cecaa16f997.py
# EXPECTED RESULT x0_baseline=(0.0,1.0,0.0,0.0)
# EXPECTED RESULT x0_mutant=(1.0,1.0,0.0,0.16)
# EXPECTED RESULT res_nan_baseline=(0.0,1.0,0.0,0.0)
# EXPECTED RESULT res_nan_mutant=(1.0,1.0,0.0392,nan)
# EXPECTED RESULT res_inf_baseline=(0.0,1.0,0.0,0.0)
# EXPECTED RESULT res_inf_mutant=(1.0,1.0,0.0392,inf)
# EXPECTED RESULT cases_moved=3 count
# EXPECTED RESULT null_default=(1.0,1.0,0.0392,0.16)
# EXPECTED RESULT null_res0=(1.0,1.0,0.0392,0.0)
# EXPECTED RESULT null_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g06 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_solar_aperture
#   (coordinator.py:9390 `if x <= 1e-6 or not np.isfinite(y):`), called on a live coordinator over tests/harness.py's FakeHass.
# Perturbation: mutant 96fe4cecaa16f997, `if x <= 1e-6 or not np.isfinite(y):` -> `if False:`, in memory: the method is recompiled from its own
#   source with the one line replaced and bound to the module's globals; the baseline arm calls the class's own method.
#   Direction: baseline skips; the mutant folds a zero-gain sample (n 0 -> 1) or writes NaN/inf into my, permanently.
# Reach: x is the modelled solar gain (0 with a zero aperture); a non-finite residual is dropped upstream at coordinator.py:5805, so y non-finite needs a direct call.
# Should have failed: tests/features.py #36 aperture block; no check with a zero modelled gain or a non-finite residual.
# Null control: inputs on which both arms must agree (default, res0); null_moved must be 0.
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

def drive(fn, irr=400.0, residual=0.4, dt_h=0.5, capacity=None, x=None, samples=1, vary=False, preset=None):
    """(n, scale, mx, my) of _solar_aperture after the folds, or the raise."""
    c = coord()
    st = replace(c._current_state)
    if preset:
        c._solar_aperture.update(preset)
    ps = []
    if capacity is not None:
        ps.append(mock.patch.object(co, "_zone_capacity", lambda p: capacity))
    if x is not None:
        ps.append(mock.patch.object(c._thermal_model, "compute_solar_gain", lambda i: x))
    for p in ps:
        p.start()
    try:
        for i in range(samples):
            st.solar_radiation = (200.0 + 600.0 * i / max(samples - 1, 1)) if vary else irr
            r = outcome(lambda: fn(c, st, residual * (1 + i % 3) if vary else residual, dt_h))
            if isinstance(r, str):
                return r
    finally:
        for p in ps:
            p.stop()
    m = c._solar_aperture
    return (m["n"], round(m["scale"], 6), round(m["mx"], 9), m["my"] if not math.isfinite(m["my"]) else round(m["my"], 6))


OLD = 'if x <= 1e-6 or not np.isfinite(y):'
NEW = 'if False:'
BASE = C._fold_solar_aperture
MUT = mutant('_fold_solar_aperture', OLD, NEW)
CASES = {'x0': dict(x=0.0), 'res_nan': dict(residual=float('nan')), 'res_inf': dict(residual=float('inf'))}
NULLS = {'default': dict(), 'res0': dict(residual=0.0)}


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
