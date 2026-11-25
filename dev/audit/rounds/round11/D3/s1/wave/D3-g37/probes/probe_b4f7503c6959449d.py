#!/usr/bin/env python3
# Metric: (a) unit: the UA 95 % half-width on a real completed one-state fit's arguments, baseline vs mutant;
#   (b) reach: over the production sweep in _drive.sweep() -- 120 two-state/one-state runs of SystemIdentification
#   arm/step/identify on the production ThermalModel (presets heavy_old, typical_slab, light_new x declared plant x
#   true house {as configured, gains 2.5 / -1.5 kW, heat-loss scale x3, room mass x0.25} x (noise, seed, cadence)
#   {(0,0,0.5h), (0.02C,0,0.5h), (0.05C,1,0.5h), (0.02C,2,0.25h)}) plus 48 one-state runs on the first-order plant of
#   tests/features.py:_drift_drive (seeds 1000..1011 x {sigma 0.02, 0, 0.02 with 0.10 C/h drift, 0.05 at 15 min}) --
#   the count of runs whose published outcome differs (every SysIdResult field, the override sequence, every sysid
#   log line), and the count of calls of the mutated symbol whose arguments separate the two arms.
#   (c) adoption: over the same sweep, adoption_decision(result, params, config) baseline vs mutant (admit, weight,
#   scale, reason) -- the count that differs, and the admitted count per arm.
#   Count key: the outcome the production seam delivers (SystemIdentification.result, step()'s return, the log).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_b4f7503c6959449d.py
# Expected: see the RESULT lines recorded in dev/audit/rounds/round11/D3/s1/wave/D3-g37/results/b4f7503c6959449d.json (exact; no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g37 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_one_state_ua_halfwidth (sysid.py:1073); production callers sysid.py:2134 (SystemIdentification.identify, published as SysIdResult.ua_profile_halfwidth).
# Perturbation: sysid.py:1073 `if solution.shape[0] >= 4:` -> `if solution.shape[0] > 4:` (key b4f7503c6959449d), applied in memory (the function recompiled
#   from its own source with the one line replaced; production reaches it through a module-attribute swap).
#   Direction: a four-column solution (the main path, drift column present) takes the two-column fallback's plain least-squares covariance instead of the full normal-equation inverse: the half-width changes
# Null control: the two-column fallback arguments (size-2 solution), which take the else branch either way
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mut  # noqa: E402  thread pin first
import _drive  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import sysid  # noqa: E402

KEY = "b4f7503c6959449d"
mut, name, rec = _mut.mutant_for(sysid, KEY)
assert name == "_one_state_ua_halfwidth", name
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


# The real arguments of one completed one-state fit (first-order plant, seed 1000), captured at sysid.py:2134.
got = []
def _cap(*a, **kw):
    got.append((a, kw)); return base(*a, **kw)
with _mut.swap(sysid, "_one_state_ua_halfwidth", _cap):
    _drive.run_first_order(1000)
a0, kw0 = got[0]
print(f"RESULT unit_solution_size={a0[0].shape[0]} count")
moved = arm("unit_halfwidth_seed1000", *a0, **kw0)
# The two-column fallback (solution of size 2, design of 2 columns): the else branch either way.
sol2 = np.asarray(a0[0][:2], dtype=float)
nm = arm("null_fallback_size2", sol2, a0[1][:2, :2], a0[2][:2], a0[3], a0[4][:, :2])
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

# Adoption: the one gate the half-width feeds (sysid.py:1239 adoption_decision, called at coordinator.py:11112),
# on each sweep case's published result; params are the configured preset (first-order cases: the
# ThermalParameters defaults with the plant's UA and capacity).
import dataclasses  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
flips = admitted_b = admitted_m = 0
for label, th in _drive.sweep():
    if label.startswith("first_order"):
        params = ThermalParameters(heat_loss_coefficient=_drive.D_UA, room_thermal_mass=_drive.D_C)
        cfg = sysid.SysIdConfig(enabled=True, gains_prior_kw=_drive.D_G, thermal_mass_prior=_drive.D_C)
    else:
        params = _drive.params_for(label.split(",")[0])
        cfg = _drive.sysid_config(params)
    rb = th()["result"]
    with _mut.swap(sysid, name, mut):
        rm = th()["result"]
    db, dm = sysid.adoption_decision(rb, params, cfg), sysid.adoption_decision(rm, params, cfg)
    admitted_b += bool(db.admit)
    admitted_m += bool(dm.admit)
    if dataclasses.astuple(db) != dataclasses.astuple(dm):
        flips += 1
        if flips <= 6:
            print(f"RESULT adoption_differ_case={label}: baseline={dataclasses.astuple(db)} mutant={dataclasses.astuple(dm)}")
print(f"RESULT adoption_admitted_baseline={admitted_b} count")
print(f"RESULT adoption_admitted_mutant={admitted_m} count")
print(f"RESULT adoption_decisions_differ={flips} count")
_mut.tail()
