#!/usr/bin/env python3
# Metric: the plan's published pv_surplus list (HeatPumpOptimizer._pv_surplus_list, result.pv_surplus, which the
#   coordinator turns into each forecast step's "pv_surplus" at coordinator.py:4895-4913) for surplus vectors at and
#   around the 1e-6 kW threshold; the count of entries that differ between the arms.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_7c2ae6b7.py
# EXPECTED RESULT exact1e-6_baseline_len=0, exact1e-6_mutant_len=48 (each 0.0 at 3 dp): the only moving input
# EXPECTED RESULT null_delta=0 count (zeros, 9.99e-7, 1.01e-6, 3 kW)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._pv_surplus_list, line 5693 `if not np.any(self._pv_surplus > 1e-6):`.
# Perturbation: key 7c2ae6b70ec6acb7, `> 1e-6` -> `>= 1e-6` (CMP_BOUND), in memory. Direction: a surplus whose
#   maximum is exactly 1e-6 kW publishes [] (each step's pv_surplus null) on the baseline, [0.0]*n under the mutant.
# Null control: every surplus vector whose maximum is not exactly 1e-6.
# Reachability: the surplus is pv.surplus_kw = clip(production - baseline load, 0) (pv.py:80-91); a maximum of
#   exactly 1e-6 kW (1 mW) needs a float difference landing on that value at every positive step.
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer
mut = rig.mutant(HeatPumpOptimizer, "_pv_surplus_list", "np.any(self._pv_surplus > 1e-6)", "np.any(self._pv_surplus >= 1e-6)")
o = rig.bare_optimizer()
cases = {"exact1e-6": np.full(48, 1e-6), "zeros": np.zeros(48), "below": np.full(48, 9.99e-7),
         "above": np.full(48, 1.01e-6), "3kW": np.r_[np.zeros(20), np.full(8, 3.0), np.zeros(20)]}
null = 0
for name, s in cases.items():
    o._pv_surplus = s
    b, m = HeatPumpOptimizer._pv_surplus_list(o, 48), mut(o, 48)
    print(f"RESULT {name}_baseline_len={len(b)} count")
    print(f"RESULT {name}_mutant_len={len(m)} count  values={sorted(set(m))}")
    if name != "exact1e-6":
        null += b != m
print(f"RESULT null_delta={null} count")
rig.tail()
