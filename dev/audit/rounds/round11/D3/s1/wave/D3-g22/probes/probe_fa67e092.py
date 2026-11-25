#!/usr/bin/env python3
# Metric: max |baseline - mutant| (displace units) of HeatPumpOptimizer._power_to_displace_schedule over outdoor
#   temperatures at and around the 0 C boundary, each held over a 48-step schedule.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_fa67e092.py
# EXPECTED RESULT max_abs_delta=0.0 displace  (at out_t == 0 the added term is min(2, |0|*0.08) = 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._power_to_displace_schedule, line 6498 `if out_t < 0:`.
# Perturbation: key fa67e0922f51edda, `if out_t < 0:` -> `if out_t <= 0:` (CMP_BOUND), in memory.
#   Direction: none expected (equivalent): the extra branch adds 0.0.
# Null control: out_t = -10 (both arms take the branch) and +5 (neither does).
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer

mut = rig.mutant(HeatPumpOptimizer, "_power_to_displace_schedule", "if out_t < 0:", "if out_t <= 0:")
o = rig.bare_optimizer()
tried = [0.0, -0.0, 1e-300, -1e-300, 5e-324, float("nan"), -10.0, 5.0]
worst = 0.0
for t in tried:
    for pw in (np.zeros(48), np.full(48, 3.0), np.linspace(0, 6, 48)):
        out = np.full(48, t)
        b = HeatPumpOptimizer._power_to_displace_schedule(o, pw, out)
        m = mut(o, pw, out)
        worst = max(worst, max(abs(x - y) for x, y in zip(b, m)))
print(f"RESULT inputs_tried={tried}")
print(f"RESULT max_abs_delta={worst} displace")
rig.tail()
