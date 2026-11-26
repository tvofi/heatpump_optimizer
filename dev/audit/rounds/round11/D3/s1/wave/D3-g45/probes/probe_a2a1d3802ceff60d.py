#!/usr/bin/env python3
# Metric: number of times ThermalParameters.topology_layout recomputes (calls mixing_valve.is_throttling) over 1000 reads of an unchanged configuration; the returned layout key is also compared.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_a2a1d3802ceff60d.py
# EXPECTED RESULT recomputes_baseline=1 count ; recomputes_mutant=1000 count ; layout_equal=1
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:404 ThermalParameters.topology_layout `if cached is not None and cached[0] == key:`.
# Perturbation: key a2a1d3802ceff60d, GUARD_OFF `if False:` (memo never hits), in-memory module copy. Direction: recompute count up 1 -> 1000; value unchanged.
# Null control: a first read (cold cache) recomputes once in both arms; the value is identical in both arms for every read.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import mutmod
from unittest import mock
base, mut = mutmod.load(404, "if cached is not None and cached[0] == key:", "if False:")
def run(m, n=1000):
    p = m.ThermalParameters(); calls = [0]; real = m.mixing_valve.is_throttling
    def counting(*a, **k):
        calls[0] += 1; return real(*a, **k)
    with mock.patch.object(m.mixing_valve, "is_throttling", counting):
        vals = {p.topology_layout for _ in range(n)}
    return calls[0], vals
(bc, bv), (mc, mv) = run(base), run(mut)
print(f"RESULT recomputes_baseline={bc} count"); print(f"RESULT recomputes_mutant={mc} count")
print(f"RESULT layout_equal={int(bv == mv)} count")
