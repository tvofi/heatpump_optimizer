#!/usr/bin/env python3
# Metric: seasonal_inlet_temp (degC) at day 60 and 240 for dhw_inlet_seasonal_amplitude in {0, -3, 4}; expected: 0 and 4 identical (cos form equals mean at 0), -3 moves
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_b098598faf0d87dc.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:835 ThermalParameters.seasonal_inlet_temp `if swing <= 0.0:`.
# Perturbation: key b098598faf0d87dc, `if swing <= 0.0:` -> `if False:`, in an in-memory module copy (mutmod.load). 
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import mutmod
base, mut = mutmod.load(835, "if swing <= 0.0:", "if False:")
# Direction: with a negative amplitude the baseline returns the constant mean, the mutant applies the (inverted) cosine.
# Null control: amplitude 0 and +4: identical.
def t(m, a, d):
    p = m.ThermalParameters(); p.dhw_inlet_seasonal_amplitude = a; return p.seasonal_inlet_temp(d)
moved = 0
for a in (0.0, -3.0, 4.0, float("nan")):
    for d in (60, 240):
        b, mu = t(base, a, d), t(mut, a, d)
        print(f"RESULT inlet_amp{a}_day{d}_baseline={b!r} mutant={mu!r}")
        moved += not (b == mu or (b != b and mu != mu))
print(f"RESULT inputs_moved={moved} of 8 count")
print(f"RESULT null_moved_amp0_pos4={sum(t(base,a,d)!=t(mut,a,d) for a in (0.0,4.0) for d in (60,240))} count")
