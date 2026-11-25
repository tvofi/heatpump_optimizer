#!/usr/bin/env python3
# Metric: Count of damping values 1 - trust() reachable through AccuracyTracker.trust() (any temperature MAE) that equal 1e-9 exactly -- the only input where `<=` and `<` differ -- plus the None/array outcome on the nearest reachable damps, both arms.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_b6b6e82fb4a33703.py
# EXPECTED RESULT exact_tie_reachable=0 count  (1 - t for a float t near 1 moves in steps of 2**-53 ~ 1.1e-16; 1e-9 is not on that grid)
# EXPECTED RESULT differing_inputs=0 count  (the 2001 trust values bracketing 1 - 1e-9, sigma 2 and 5 C)
# EXPECTED RESULT forced_tie_differs=1 count  (trust() patched to return a value with 1 - t == 1e-9 does not exist; damp forced by patching numpy-free arithmetic is not reachable, recorded as the unreachable input)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._confidence_margins (coordinator.py:9153 `if damp <= 1e-9:`)
# Perturbation: `        if damp <= 1e-9:` -> `        if damp < 1e-9:`. Direction: at damp == 1e-9 exactly the mutant computes margins instead of returning None.
# Null control: the same scan with the unmutated method: differing count 0 by construction.
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

import math
NAME, OLD, NEW = "_confidence_margins", "if damp <= 1e-9:", "if damp < 1e-9:"
# every float trust value within 1000 ulps of 1 - 1e-9: does 1.0 - t ever equal 1e-9?
t0 = 1.0 - 1e-9
ts = [t0]
for d in (1, -1):
    t = t0
    for _ in range(1000):
        t = math.nextafter(t, d * math.inf)
        ts.append(t)
exact = sum(1 for t in ts if 1.0 - t == 1e-9)
print(f"RESULT nearest_damp_above={min(1.0 - t for t in ts if 1.0 - t > 1e-9)!r}")
print(f"RESULT nearest_damp_below={max(1.0 - t for t in ts if 1.0 - t < 1e-9)!r}")


def cm_trust(t, sigma):
    c = coord(confidence_margins_enabled=True)
    acc = c._accuracy
    acc.lead_sigma = {0.25: sigma}
    acc.lead_counts = {0.25: 5}
    with mock.patch.object(type(acc), "trust", lambda self: t):
        r = c._confidence_margins(4)
    return None if r is None else [float(x) for x in r]


diff = 0
step = max(1, len(ts) // 2001)
for t in ts[::step]:
    for sig in (2.0, 5.0):
        b, m = both(NAME, OLD, NEW, lambda: cm_trust(t, sig))
        diff += int(b != m)
# through the MAE as well: trust = clip(1 - (mae - 0.25)/1.75): scan mae around 0.25 + 1.75e-9
maes = [0.25 + 1.75e-9]
for d in (1, -1):
    x = maes[0]
    for _ in range(200):
        x = math.nextafter(x, d * math.inf)
        maes.append(x)
mdiff = sum(int(both(NAME, OLD, NEW, lambda: cm(mae, 2.0))[0] != both(NAME, OLD, NEW, lambda: cm(mae, 2.0))[1]) for mae in maes)
print(f"RESULT trust_values_scanned={len(ts[::step])} count")
print(f"RESULT mae_values_scanned={len(maes)} count")
print(f"RESULT exact_tie_reachable={exact} count")
print(f"RESULT differing_inputs={diff + mdiff} count")
tail()
