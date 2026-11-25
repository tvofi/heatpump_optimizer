#!/usr/bin/env python3
# Metric: (a) unit: (peak, final) at ua exactly 1e-9, baseline vs mutant;
#   (b) reach: over the production sweep in _drive.sweep() -- 120 two-state/one-state runs of SystemIdentification
#   arm/step/identify on the production ThermalModel (presets heavy_old, typical_slab, light_new x declared plant x
#   true house {as configured, gains 2.5 / -1.5 kW, heat-loss scale x3, room mass x0.25} x (noise, seed, cadence)
#   {(0,0,0.5h), (0.02C,0,0.5h), (0.05C,1,0.5h), (0.02C,2,0.25h)}) plus 48 one-state runs on the first-order plant of
#   tests/features.py:_drift_drive (seeds 1000..1011 x {sigma 0.02, 0, 0.02 with 0.10 C/h drift, 0.05 at 15 min}) --
#   the count of runs whose published outcome differs (every SysIdResult field, the override sequence, every sysid
#   log line), and the count of calls of the mutated symbol whose arguments separate the two arms.
#   Count key: the outcome the production seam delivers (SystemIdentification.result, step()'s return, the log).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_0c0a6bcb94a3ba3a.py
# Expected: see the RESULT lines recorded in dev/audit/rounds/round11/D3/s1/wave/D3-g37/results/0c0a6bcb94a3ba3a.json (exact; no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g37 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_predict_step_excursion (sysid.py:129); production callers sysid.py:1627 (SystemIdentification._size_step_power, the one-state peak in a debug log line only).
# Perturbation: sysid.py:129 `if ua <= 1e-9 or capacity <= 1e-9:` -> `if ua < 1e-9 or capacity <= 1e-9:` (key 0c0a6bcb94a3ba3a), applied in memory (the function recompiled
#   from its own source with the one line replaced; production reaches it through a module-attribute swap).
#   Direction: ua exactly 1e-9 returns finite excursions instead of (inf, inf)
# Null control: ua 5e-10 and 2e-9, where the guard is decided the same either way
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mut  # noqa: E402  thread pin first
import _drive  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import sysid  # noqa: E402

KEY = "0c0a6bcb94a3ba3a"
mut, name, rec = _mut.mutant_for(sysid, KEY)
assert name == "_predict_step_excursion", name
base = getattr(sysid, name)

def _same(u, v):
    if isinstance(u, tuple) and isinstance(v, tuple):
        return len(u) == len(v) and all(_same(p, q) for p, q in zip(u, v))
    a, b = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
    return a.shape == b.shape and bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))


def _call(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception as exc:  # an exception is an outcome too
        return type(exc).__name__


def separates(a, kw):
    u, v = _call(base, *a, **kw), _call(mut, *a, **kw)
    if isinstance(u, str) or isinstance(v, str):
        return u != v
    return not _same(u, v)


def arm(label, *a, **kw):
    u, v = _call(base, *a, **kw), _call(mut, *a, **kw)
    print(f"RESULT {label}_baseline={u}")
    print(f"RESULT {label}_mutant={v}")
    moved = (u != v) if (isinstance(u, str) or isinstance(v, str)) else (not _same(u, v))
    print(f"RESULT {label}_moved={int(moved)} count")
    return int(moved)


# _predict_step_excursion(baseline, outdoor, ua, capacity, gains, step_thermal_kw, step_hours, relax_hours)
moved = 0
for lab, ua, cap in (("ua_1e-9", 1e-9, 10.0),):
    moved += arm(f"unit_{lab}", 21.0, 2.0, ua, cap, 0.3, 4.0, 2.0, 2.0)
nm = 0
for lab, ua, cap in (("ua_5e-10", 5e-10, 10.0), ("ua_2e-9", 2e-9, 10.0)):
    nm += arm(f"null_{lab}", 21.0, 2.0, ua, cap, 0.3, 4.0, 2.0, 2.0)
print(f"RESULT unit_moved={moved} count")
print(f"RESULT null_moved={nm} count")


calls = []


def spy(*a, **kw):
    calls.append((a, kw))
    return base(*a, **kw)


runs, differ = _drive.reach(sysid, name, mut, spy)
print(f"RESULT reach_runs={runs} count")
print(f"RESULT reach_calls={len(calls)} count")
print(f"RESULT reach_calls_separating={sum(1 for a, kw in calls if separates(a, kw))} count")
print(f"RESULT reach_outcomes_differ={len(differ)} count")
for lab, b, m in differ[:10]:
    print(f"RESULT reach_differ_case={lab}: baseline[{b}] mutant[{m}]")
_mut.tail()
