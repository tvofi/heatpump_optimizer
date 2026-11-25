#!/usr/bin/env python3
# Metric: buffer_tank_heat_loss_coefficient (kW/degC) of a 200 L buffer whose buffer_cooling_rate is a tiny positive value (1e-6 C/h).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_b2faf84904db389e.py
# EXPECTED RESULT ua_baseline=lower-bound UA (>0.0005)  ; ua_mutant=~0 (rate*mass/ref, ~1e-9)
# EXPECTED RESULT ua_ratio_mutant_over_baseline<<1
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:677 ThermalParameters.buffer_tank_heat_loss_coefficient `rate = min(max(float(rate), low), high)`.
# Perturbation: key b2faf84904db389e, CLAMP_DROP `min(max(rate,low),high)` -> `min(rate,high)`, applied to an in-memory copy of the module. Direction: UA falls to ~0.
# Null control: rate=0.0 (<=0 branch takes default, inside bounds): identical both arms.
import sys; sys.path.insert(0, __import__("os").path.dirname(__file__))
import mutmod
base, mut = mutmod.load(677, "rate = min(max(float(rate), low), high)", "rate = min((float(rate)), high)")
def ua(m, rate):
    p = m.ThermalParameters(); p.buffer_tank_volume = 200.0; p.buffer_cooling_rate = rate
    return p.buffer_tank_heat_loss_coefficient
for rate in (1e-6, 0.0):
    b, m = ua(base, rate), ua(mut, rate)
    print(f"RESULT ua_baseline_rate{rate}={b!r}"); print(f"RESULT ua_mutant_rate{rate}={m!r}")
b, m = ua(base, 1e-6), ua(mut, 1e-6)
print(f"RESULT ua_ratio_mutant_over_baseline={m/b:.3e}")
print(f"RESULT null_delta={abs(ua(base,0.0)-ua(mut,0.0))!r}")
