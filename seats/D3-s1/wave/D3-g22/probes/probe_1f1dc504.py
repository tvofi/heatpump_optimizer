#!/usr/bin/env python3
# Metric: max |baseline - mutant| (kWh) of HeatPumpOptimizer._pv_self_consumed (rounded to 3 dp as published) over
#   surplus vectors at and around the 1e-6 kW threshold, power schedules and step lengths.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1f1dc504.py
# EXPECTED RESULT max_abs_delta=0.0 kWh (surplus exactly 1e-6 kW is the only differing input, and its served energy
#   is at most n*1e-6*dt kWh, which rounds to 0.000 for any horizon under 2000 steps at dt=0.25 h)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._pv_self_consumed, line 5699
#   `if self._pv_surplus is None or not np.any(self._pv_surplus > 1e-6):`.
# Perturbation: key 1f1dc504455f17da, `> 1e-6` -> `>= 1e-6` (CMP_BOUND), in memory. Direction: none expected.
# Null control: a 3 kW surplus (both arms compute the same sum).
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer
mut = rig.mutant(HeatPumpOptimizer, "_pv_self_consumed", "np.any(self._pv_surplus > 1e-6)", "np.any(self._pv_surplus >= 1e-6)")
o = rig.bare_optimizer()
surpluses = {"exact1e-6": np.full(48, 1e-6), "exact1e-6_one": np.r_[1e-6, np.zeros(47)], "zeros": np.zeros(48),
             "below": np.full(48, 9.99e-7), "above": np.full(48, 1.01e-6), "null_3kW": np.full(48, 3.0)}
powers = {"zero": np.zeros(48), "6kW": np.full(48, 6.0), "ramp": np.linspace(0, 6, 48)}
worst, moved_raw = 0.0, 0
for sn, s in surpluses.items():
    for pn, pw in powers.items():
        for dt in (0.25, 1.0):
            o._pv_surplus = s
            b = HeatPumpOptimizer._pv_self_consumed(o, pw, dt)
            m = mut(o, pw, dt)
            worst = max(worst, abs(b - m))
print(f"RESULT inputs_surplus={list(surpluses)} powers={list(powers)} dt=[0.25, 1.0]")
print(f"RESULT max_abs_delta={worst} kWh")
o._pv_surplus = np.full(48, 3.0)
print(f"RESULT null_delta={abs(HeatPumpOptimizer._pv_self_consumed(o, np.full(48, 2.0), 0.25) - mut(o, np.full(48, 2.0), 0.25))} kWh")
rig.tail()
