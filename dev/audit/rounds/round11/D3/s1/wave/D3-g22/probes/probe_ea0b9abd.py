#!/usr/bin/env python3
# Metric: HeatPumpOptimizer._power_to_displace_schedule's output length (count) for a power schedule one step longer
#   than its outdoor series (the padding branch), and for production-shaped equal lengths.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_ea0b9abd.py
# EXPECTED RESULT short_outdoor_baseline=4 count; short_outdoor_mutant=IndexError
# EXPECTED RESULT equal_len_delta=0 count  (every production shape: the branch never pads)
# EXPECTED RESULT reach_outdoor_shorter_than_power=0 count  (7 real solves, reach_scan.py)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._power_to_displace_schedule, line 6497
#   `out_t = outdoor_temps[i] if i < len(outdoor_temps) else outdoor_temps[-1]`.
# Perturbation: key ea0b9abd134c33cd, `i < len(outdoor_temps)` -> `i <= len(outdoor_temps)` (CMP_BOUND), in memory.
#   Direction: a short outdoor series pads on the baseline and raises IndexError under the mutant.
# Null control: equal lengths (48/48), where i < len is true at every step under both arms.
# Reachability: the only caller (optimizer.py:3881) passes h.outdoor_temps, the horizon's n_steps-long series, with
#   space_power of the same length; reach_scan.py counts outdoor shorter than power in real solves.
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer

mut = rig.mutant(HeatPumpOptimizer, "_power_to_displace_schedule",
                 "if i < len(outdoor_temps) else", "if i <= len(outdoor_temps) else")
o = rig.bare_optimizer()
power = np.array([0.0, 2.0, 4.0, 1.0])
short = np.array([-5.0, -3.0, 2.0])


def call(fn, pw, out):
    try:
        return fn(o, pw, out)
    except Exception as e:
        return type(e).__name__


b = call(HeatPumpOptimizer._power_to_displace_schedule, power, short)
m = call(mut, power, short)
print(f"RESULT short_outdoor_baseline={len(b) if isinstance(b, list) else b} count")
print(f"RESULT short_outdoor_mutant={len(m) if isinstance(m, list) else m} count")
pw48 = np.linspace(0, 5, 48); out48 = np.linspace(-16, 4, 48)
d = call(HeatPumpOptimizer._power_to_displace_schedule, pw48, out48) != call(mut, pw48, out48)
print(f"RESULT equal_len_delta={int(d)} count")
print("RESULT reach_outdoor_shorter_than_power=0 count  (reach_scan.py RESULT disp_outdoor_shorter_than_power)")
rig.tail()
