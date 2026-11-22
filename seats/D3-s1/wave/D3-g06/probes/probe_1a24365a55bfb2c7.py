#!/usr/bin/env python3
# Metric: (n, scale, mx, my) of the solar-aperture regression after the folds; baseline arm vs the mutant arm, per input; cases_moved counts the inputs whose outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_1a24365a55bfb2c7.py
# EXPECTED RESULT n1_baseline=(1.0,1.0,0.0392,0.16)
# EXPECTED RESULT n1_mutant=(1.0,2.0,0.0392,0.16)
# EXPECTED RESULT n10_varied_baseline=(10.0,1.0,0.458124495,2.784389)
# EXPECTED RESULT n10_varied_mutant=(10.0,2.0,0.458124495,2.784389)
# EXPECTED RESULT n40_var0_baseline=(41.0,1.0,1.96,0.65)
# EXPECTED RESULT n40_var0_mutant=(41.0,0.3,1.96,0.65)
# EXPECTED RESULT cases_moved=3 count
# EXPECTED RESULT null_preset_n29_var0p5=(30.0,1.087994,1.9992,0.65)
# EXPECTED RESULT null_preset_n40_var0p5=(41.0,1.087994,1.9992,0.65)
# EXPECTED RESULT null_moved=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g06 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_solar_aperture
#   (coordinator.py:9402 `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:`), called on a live coordinator over tests/harness.py's FakeHass.
# Perturbation: mutant 1a24365a55bfb2c7, `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:` -> `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES or m["var"] > 1e-6:`, in memory: the method is recompiled from its own
#   source with the one line replaced and bound to the module's globals; the baseline arm calls the class's own method.
#   Direction: baseline keeps the scale at 1.0 until 30 samples; the mutant adopts cov/var from the first sample (scale 1.0 -> 2.0, the clamp), and past 30 samples with a near-zero variance (a constant modelled gain) takes cov/var of a degenerate regression and pins the scale at the 0.3 clamp.
# Reach: every installation's first sunny samples: n < SOLAR_APERTURE_MIN_SAMPLES (30) with a non-zero EWMA variance after the first fold.
# Should have failed: tests/features.py 'the aperture regression converges on the true scale' (_c36) runs 180 samples and reads only the end; no check asserts the scale stays 1.0 before SOLAR_APERTURE_MIN_SAMPLES.
# Null control: inputs on which both arms must agree (preset_n29_var0p5, preset_n40_var0p5); null_moved must be 0.
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


OLD = 'if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:'
NEW = 'if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES or m["var"] > 1e-6:'
BASE = C._fold_solar_aperture
MUT = mutant('_fold_solar_aperture', OLD, NEW)
CASES = {'n1': dict(), 'n10_varied': dict(samples=10, vary=True), 'n40_var0': dict(preset={'n': 40.0, 'var': 0.0, 'cov': 0.0, 'mx': 1.96, 'my': 0.5})}
NULLS = {'preset_n29_var0p5': dict(preset={'n': 29.0, 'var': 0.5, 'cov': 0.05, 'mx': 2.0, 'my': 0.5}), 'preset_n40_var0p5': dict(preset={'n': 40.0, 'var': 0.5, 'cov': 0.05, 'mx': 2.0, 'my': 0.5})}


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
