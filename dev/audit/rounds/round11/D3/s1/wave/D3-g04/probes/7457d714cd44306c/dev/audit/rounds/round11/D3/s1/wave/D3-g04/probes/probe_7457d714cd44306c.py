#!/usr/bin/env python3
# Metric: Whether _confidence_margins(4) returns None or an array when every margin equals 1e-9 exactly (sigma*damp == 1e-9: sigma 2e-9 C at damp 0.5, mae 1.125). Count = inputs whose None/array outcome differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_7457d714cd44306c.py
# EXPECTED RESULT outcome_baseline=None
# EXPECTED RESULT outcome_mutant=array[4] max=1e-09
# EXPECTED RESULT differing_inputs=2 count  (sigma 2e-9 at damp 0.5, mae 1.125; sigma 4e-9 at damp 0.25, mae 0.6875)
# EXPECTED RESULT null_differing=0 count (sigma 1e-8 and 1e-10)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._confidence_margins (coordinator.py:9166 `return margins if bool(np.any(margins > 1e-9)) else None`)
# Perturbation: `margins > 1e-9` -> `margins >= 1e-9`. Direction: None -> array of 1e-9 C at the exact tie.
# Null control: sigma 1e-8 (array on both arms) and 1e-10 (None on both).
# Run from the repository root; the mutant is applied in memory (the method recompiled from its own
# source with the one line replaced, patched onto the class for the mutant arm only).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock

# The repository root is the working directory (the harness contract): the probe imports
# production from there, so a gate mutating the tree it is stored in never leaks into it.
ROOT = Path.cwd()
assert (ROOT / "custom_components" / "heatpump_optimizer" / "manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
_T0, _C0 = time.thread_time(), time.process_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
C = co.HeatPumpOptimizerCoordinator


def mutant(name, old, new):
    """The method recompiled from its own source with the one-line mutant applied."""
    src = textwrap.dedent(inspect.getsource(getattr(C, name)))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


BASE_CFG = {"tibber_token": "x", "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return C(FakeHass(dict(states or {})), FakeEntry(data={**BASE_CFG, **extra}))


def both(name, old, new, fn):
    """fn() on the baseline and under the mutant; an exception is the value (its type name)."""
    def run():
        try:
            return fn()
        except Exception as err:  # noqa: BLE001 - a raise is an observable outcome
            return f"raises {type(err).__name__}"
    base = run()
    with mock.patch.object(C, name, mutant(name, old, new)):
        mut = run()
    return base, mut


def tail():
    thread = time.thread_time() - _T0
    proc = time.process_time() - _C0
    print(f"RESULT thread_factor={proc / thread if thread > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")][0].split()[1]
    except Exception:  # noqa: BLE001
        swap = "na"
    print(f"RESULT swapins={swap}")

import numpy as np


def cm(mae, sigma, n=4):
    """_confidence_margins(n) with the tracker's temperature MAE fixed (trust() runs for real) and one
    0.25 h lead bucket of the given sigma (sigma() runs for real)."""
    c = coord(confidence_margins_enabled=True)
    acc = c._accuracy
    acc.lead_sigma = {0.25: sigma}
    acc.lead_counts = {0.25: 5}
    with mock.patch.object(type(acc), "temperature_mae", lambda self: mae):
        r = c._confidence_margins(n)
    return None if r is None else [float(x) for x in r]


def show(v):
    return "None" if v is None else f"array[{len(v)}] max={max(v):.6g}"

NAME = "_confidence_margins"
OLD = "return margins if bool(np.any(margins > 1e-9)) else None"
NEW = "return margins if bool(np.any(margins >= 1e-9)) else None"
cells = [(1.125, 2e-9), (0.6875, 4e-9)]
diff = 0
for mae, sig in cells:
    b, m = both(NAME, OLD, NEW, lambda: cm(mae, sig))
    diff += int((b is None) != (m is None))
    print(f"RESULT input mae={mae} sigma={sig}: baseline={show(b)} mutant={show(m)}")
nd = sum(int(x[0] != x[1]) for x in (both(NAME, OLD, NEW, lambda s=s: cm(1.125, s)) for s in (1e-8, 1e-10)))
b, m = both(NAME, OLD, NEW, lambda: cm(1.125, 2e-9))
print(f"RESULT outcome_baseline={show(b)}")
print(f"RESULT outcome_mutant={show(m)}")
print(f"RESULT differing_inputs={diff} count")
print(f"RESULT null_differing={nd} count")
tail()
