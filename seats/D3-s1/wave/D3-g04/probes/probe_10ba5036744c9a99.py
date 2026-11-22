#!/usr/bin/env python3
# Metric: Max |difference| of _confidence_margins(n) between arms over the step lengths production can hand it (OptimizationConfig.time_step_minutes, never assigned outside its 15.0 default), and over sub-minute steps fed in directly.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_10ba5036744c9a99.py
# EXPECTED RESULT production_step_minutes=15.0
# EXPECTED RESULT max_abs_delta_production=0.0 C  (15 >= 1: max() is the identity)
# EXPECTED RESULT max_abs_delta_subminute>0 C  (separates only on a sub-minute step, which nothing in production sets)
# EXPECTED RESULT null_max_abs_delta=0.0 C (step 5, 15, 60)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._confidence_margins (coordinator.py:9155 `dt_h = max(ctx._opt_config.time_step_minutes, 1.0) / 60.0`)
# Perturbation: `max(time_step_minutes, 1.0)` -> `(time_step_minutes)`. Direction: identical for steps >= 1 min; a sub-minute step shortens every lead.
# Null control: steps of 5, 15 and 60 minutes: identical by construction of max().
# Reachability: grep shows no assignment of time_step_minutes outside optimizer.py:2667's dataclass default (15.0); no config key sets it.
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

import dataclasses
NAME = "_confidence_margins"
OLD = "dt_h = max(ctx._opt_config.time_step_minutes, 1.0) / 60.0"
NEW = "dt_h = (ctx._opt_config.time_step_minutes) / 60.0"


def cm_step(step):
    c = coord(confidence_margins_enabled=True)
    acc = c._accuracy
    acc.lead_sigma = {0.01: 0.3, 0.1: 0.6}
    acc.lead_counts = {0.01: 5, 0.1: 5}
    # the context is a frozen dataclass: swap in a copy of its OptimizationConfig with this step
    object.__setattr__(c._ctx, "_opt_config", dataclasses.replace(c._ctx._opt_config, time_step_minutes=step))
    with mock.patch.object(type(acc), "temperature_mae", lambda self: 1.125):
        r = c._confidence_margins(8)
    return None if r is None else [float(x) for x in r]


def delta(step):
    b, m = both(NAME, OLD, NEW, lambda: cm_step(step))
    if b is None or m is None or isinstance(b, str) or isinstance(m, str):
        return 0.0 if b == m else float("inf")
    return max(abs(x - y) for x, y in zip(b, m))


prod = coord()._ctx._opt_config.time_step_minutes
print(f"RESULT production_step_minutes={prod}")
print(f"RESULT max_abs_delta_production={delta(prod)} C")
sub = {s: delta(s) for s in (0.0, 0.25, 0.5, 0.999)}
for s, d in sub.items():
    print(f"RESULT input step={s} delta={d}")
print(f"RESULT max_abs_delta_subminute={max(sub.values())} C")
print(f"RESULT null_max_abs_delta={max(delta(s) for s in (5.0, 15.0, 60.0))} C")
tail()
