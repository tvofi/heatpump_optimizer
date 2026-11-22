#!/usr/bin/env python3
# Metric: max |baseline - mutant| (displace units) of HeatPumpOptimizer._power_to_displace_schedule over a grid of
#   displace windows and PID time constants, split into windows the config flow / set_parameters service admit
#   (d_min in [-30, 0], d_max in [0, 30], tau >= 0.01 h) and windows they refuse (d_min > 0 or d_max < 0).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1897b1e8.py
# EXPECTED RESULT admitted_max_abs_delta=0.0 displace  (an EWMA with alpha in [0, 1] from effective=0 stays inside
#   the hull of {0} and the clipped commands, which the admitted window contains)
# EXPECTED RESULT refused_max_abs_delta > 0 displace   (d_min = 2: the first filtered values sit below d_min)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._power_to_displace_schedule, line 6509
#   `filtered.append(round(float(np.clip(effective, d_min, d_max)), 1))`.
# Perturbation: key 1897b1e8f0e09c02, the np.clip dropped (CLAMP_DROP), in memory. Direction: only for a window
#   excluding 0.
# Null control: the default window (-20, 20) at the default tau 1.5 h.
# Reachability: config_flow.py:1888 bounds ecl110_displace_min to [-30, 0] (the max field likewise to [0, 30]);
#   services.py:517-522 the same; line 6504 keeps alpha in [0, 1].
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer

mut = rig.mutant(HeatPumpOptimizer, "_power_to_displace_schedule",
                 "filtered.append(round(float(np.clip(effective, d_min, d_max)), 1))",
                 "filtered.append(round(float((effective)), 1))")
o = rig.bare_optimizer()
p = o.model.params
pmax = p.max_electrical_power
schedules = [np.zeros(24), np.full(24, pmax), np.array([0.0, pmax] * 12), np.linspace(0, pmax, 24)]
outs = [np.full(24, -30.0), np.full(24, 10.0), np.linspace(-20, 10, 24)]
fas = [None, {"solar_reduction_factor": 0.0, "wind_anticipation_factor": 2.0, "rain_anticipation_factor": 2.0}]
admitted = [(-20.0, 20.0), (-30.0, 0.0), (0.0, 30.0), (0.0, 0.0), (-0.5, 0.5), (-30.0, 30.0)]
refused = [(2.0, 10.0), (-10.0, -2.0)]
worst = {"admitted": 0.0, "refused": 0.0}
n = 0
for label, wins in (("admitted", admitted), ("refused", refused)):
    for lo, hi in wins:
        p.ecl110_displace_min, p.ecl110_displace_max = lo, hi
        for tau in (0.01, 0.25, 1.5, 24.0):
            p.ecl110_pid_time_constant_hours = tau
            for pw in schedules:
                for out in outs:
                    for fa in fas:
                        b = HeatPumpOptimizer._power_to_displace_schedule(o, pw, out, fa)
                        m = mut(o, pw, out, fa)
                        worst[label] = max(worst[label], max(abs(x - y) for x, y in zip(b, m)))
                        n += 1
print(f"RESULT cells={n} count")
print(f"RESULT windows_admitted={admitted}")
print(f"RESULT windows_refused={refused}")
print(f"RESULT admitted_max_abs_delta={worst['admitted']} displace")
print(f"RESULT refused_max_abs_delta={worst['refused']} displace")
rig.tail()
