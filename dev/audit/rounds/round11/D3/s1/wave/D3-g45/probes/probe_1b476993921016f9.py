#!/usr/bin/env python3
# Metric: dhw_draw_power (kW) for greywater_recovery in {-0.5, 0, 0.5, 0.9, 1.5}; expected: moves for -0.5 and 1.5 (out-of-range), null = 0/0.5/0.9
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_1b476993921016f9.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:852 ThermalParameters.dhw_draw_power `recovery = float(np.clip(self.greywater_recovery, 0.0, 0.9))`.
# Perturbation: key 1b476993921016f9, `recovery = float(np.clip(self.greywater_recovery, 0.0, 0.9))` -> `recovery = float((self.greywater_recovery))`, in an in-memory module copy (mutmod.load). 
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import mutmod
base, mut = mutmod.load(852, "recovery = float(np.clip(self.greywater_recovery, 0.0, 0.9))", "recovery = float((self.greywater_recovery))")
# Direction: recovery 1.5 -> power goes negative (baseline clipped at 0.9); -0.5 -> power rises above the no-recovery figure.
# Null control: in-range recoveries (0, 0.5, 0.9) are identical in both arms.
def pw(m, r):
    p = m.ThermalParameters(); p.greywater_recovery = r; return p.dhw_draw_power
moved = 0
for r in (-0.5, 0.0, 0.5, 0.9, 1.5, float("nan")):
    b, mu = pw(base, r), pw(mut, r)
    print(f"RESULT draw_power_recovery{r}_baseline={b!r} mutant={mu!r}")
    moved += not (b == mu or (b != b and mu != mu))
print(f"RESULT inputs_moved={moved} of 6 count")
print(f"RESULT null_moved={sum(pw(base,r)!=pw(mut,r) for r in (0.0,0.5,0.9))} count")
