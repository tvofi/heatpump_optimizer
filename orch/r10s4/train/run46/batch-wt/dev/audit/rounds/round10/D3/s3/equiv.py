#!/usr/bin/env python3
"""D3-s3 equivalence check for the two pre-screen survivors (M15, M18) -- a non-finding instrument.
Metric: number of probe inputs on which the mutated production symbol's output differs from the
baseline's (0 = equivalent mutant on the probed domain, so the suite cannot and need not kill it).
Symbols: away:interpret_presence (M18); dhw_draws:DrawStats.fold reached through its only caller's
energy term dhw_learning (energy = max(0, ...) * dt_h * mass >= 0), probed with non-negative energies.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D3/s3/equiv.py
Expected: RESULT M18_diff=0, M15_diff_nonneg=0, M15_diff_negative>0 (the perturbation arm: a negative
energy the caller never produces does move it). Baseline 17f1c55fad1b."""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import sys, types, importlib
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ".")
from mutants import MUTANTS, P
def mutated(modname, mid):
    base = importlib.import_module("custom_components.heatpump_optimizer." + modname)
    m = [x for x in MUTANTS if x[0] == mid][0]
    src = open(P + m[2]).read(); assert src.count(m[3]) == 1
    mod = types.ModuleType(base.__name__ + "_mut"); mod.__package__ = "custom_components.heatpump_optimizer"; mod.__file__ = base.__file__
    sys.modules[mod.__name__] = mod
    exec(compile(src.replace(m[3], m[4]), base.__file__, "exec"), mod.__dict__)
    return base, mod
b, mu = mutated("away", "M18")
probes = [(s, f"{d}.x") for d in ("person", "device_tracker", "sensor", "input_boolean") for s in ("away", "not_home", "home", "work", "on", "off", "Away", " AWAY ")]
print(f"RESULT M18_probes={len(probes)} count")
print(f"RESULT M18_diff={sum(b.interpret_presence(s, e) != mu.interpret_presence(s, e) for s, e in probes)} count")
b, mu = mutated("dhw_draws", "M15")
def run(cls, energies):
    st = cls(); t = datetime(2026, 1, 1, 6, 0)
    for i, e in enumerate(energies): st.fold(t.replace(minute=i % 60), "w", e)
    st.fold(datetime(2026, 1, 2, 6, 0), "w", 0.0); return st.reservoirs
nonneg = [[0.0, 0.1, 0.5], [0.0], [2.0, 0.0, 3.3, 1e-9]]
neg = [[0.5, -0.2], [-1.0], [0.3, -0.3, 0.1]]
print(f"RESULT M15_diff_nonneg={sum(run(b.DrawStats, e) != run(mu.DrawStats, e) for e in nonneg)} count")
print(f"RESULT M15_diff_negative={sum(run(b.DrawStats, e) != run(mu.DrawStats, e) for e in neg)} count")
print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT thread_factor=1.00")
