#!/usr/bin/env python3
# Metric: (a) unit: _slab_refusal(ua, room_cap, gains_kw, slab_mass) verdict (reason string, or "accept") on the
#   key's boundary/separating inputs, baseline vs mutant; (b) reach: over a production sweep of two-state fits
#   (SystemIdentification.arm/step/identify_slab on the production ThermalModel; presets heavy_old, typical_slab,
#   light_new x declared plant x true house {as configured, internal gains 2.5/5.0/-1.5 kW, heat-loss scale x3} x
#   configured gains profile {none, flat 0.0 kW, flat 0.9 kW (the learner's clip ceiling at g0=0.3)} x
#   (noise, seed, cadence) in {(0,0,0.5h), (0.02C,0,0.5h), (0.05C,1,0.5h), (0.02C,2,0.25h)}), the count of
#   _slab_refusal calls whose inputs separate baseline from mutant, and the count of SysIdResults that differ.
#   Count key: the arguments production delivers to _slab_refusal (spied at the call), and the published SysIdResult.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_66e79426a66d3362.py
# Expected: see the EXPECTED block below (exact counts; no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g37 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_slab_refusal (sysid.py:897), called only at
#   sysid.py:2408 (SystemIdentification._slab_outcome).
# Perturbation: sysid.py:897 `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):` -> `if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):` (key 66e79426a66d3362), applied in memory (the function recompiled from
#   its own source with the one line replaced; production reaches it through an attribute swap). Direction: tau exactly 200 h flips from accepted to refused; unchanged off the tie.
# Null control: inputs where the predicate's value cannot depend on the mutated comparison (the null rows below).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mut  # noqa: E402  thread pin first
import _drive  # noqa: E402
from custom_components.heatpump_optimizer import sysid  # noqa: E402

KEY = "66e79426a66d3362"
mut, name, rec = _mut.mutant_for(sysid, KEY)
assert name == "_slab_refusal"
base = sysid._slab_refusal


def verdict(fn, *a):
    r = fn(*a)
    return "accept" if r is None else r.reason


UNIT = [(0.5, 50.0, 0.3, 50.0)]
NULL = [(0.5, 49.0, 0.3, 50.0), (0.5, 51.0, 0.3, 50.0), (0.2, 5.0, 0.3, 10.0)]
moved = 0
for i, a in enumerate(UNIT):
    b, m = verdict(base, *a), verdict(mut, *a)
    moved += b != m
    print(f"RESULT unit{i}_args={a}")
    print(f"RESULT unit{i}_baseline={b!r}")
    print(f"RESULT unit{i}_mutant={m!r}")
print(f"RESULT unit_moved={moved} count")
nd = sum(verdict(base, *a) != verdict(mut, *a) for a in NULL)
print(f"RESULT null_moved={nd} count (over {len(NULL)} null rows)")

calls = []


def spy(*a):
    calls.append(a)
    return base(*a)


def res_key(o):
    r = o["result"]
    return None if r is None else (r.completed, r.reason, r.heat_loss_kw_per_c, r.confidence)


TRUTHS = ({}, {"internal_gains": 2.5}, {"internal_gains": 5.0}, {"internal_gains": -1.5},
          {"house_heat_loss_scale": 3.0})
# The gains prior is night_gains_prior_kw (sysid.py:1291) over the learned profile, which the coordinator clips to
# [0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05)] (coordinator.py:9452) with g0 = internal_gains: the profile's
# two extremes at the default g0 = 0.3 are configured here.
CONFIGS = ({}, {"internal_gains_profile": [0.0] * 24}, {"internal_gains_profile": [0.9] * 24})
runs = differ = 0
for preset, cfgv in [(pr, c) for pr in ("heavy_old", "typical_slab", "light_new") for c in CONFIGS]:
    for decl in (True, False):
        for ti, truth in enumerate(TRUTHS):
            for noise, seed, cad in ((0.0, 0, 0.5), (0.02, 0, 0.5), (0.05, 1, 0.5), (0.02, 2, 0.25)):
                p = _drive.params_for(preset, **cfgv)
                tp = _drive.params_for(preset, **cfgv, **truth) if truth else None
                with _mut.swap(sysid, "_slab_refusal", spy):
                    ob = _drive.run(p, declare_plant=decl, true_params=tp, noise=noise, seed=seed, cadence_h=cad)
                with _mut.swap(sysid, "_slab_refusal", mut):
                    om = _drive.run(p, declare_plant=decl, true_params=tp, noise=noise, seed=seed, cadence_h=cad)
                runs += 1
                if res_key(ob) != res_key(om):
                    differ += 1
                    print(f"RESULT reach_differ_case={preset},cfg={cfgv},decl={decl},truth={truth},noise={noise},seed={seed},cad={cad}: "
                          f"baseline[{_drive.summary(ob)}] mutant[{_drive.summary(om)}]")
sep = sum(verdict(base, *a) != verdict(mut, *a) for a in calls)
print(f"RESULT reach_runs={runs} count")
print(f"RESULT reach_slab_refusal_calls={len(calls)} count")
print(f"RESULT reach_calls_separating={sep} count")
print(f"RESULT reach_results_differ={differ} count")
if calls:
    for j, lab in enumerate(("ua", "room_cap", "gains_kw", "slab_mass")):
        vs = [c[j] for c in calls]
        print(f"RESULT reach_{lab}_range=[{min(vs):.6g}, {max(vs):.6g}]")
_mut.tail()
