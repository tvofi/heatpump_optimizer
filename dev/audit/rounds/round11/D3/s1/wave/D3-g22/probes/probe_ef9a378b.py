#!/usr/bin/env python3
# Metric: max |baseline - mutant| (displace units) of the published ECL110 displace schedule
#   (HeatPumpOptimizer._power_to_displace_schedule) for a power step 0 -> max -> 0 at -5 C, with the PID time
#   constant at the set_parameters service's floor (0.01 h, read through ecl110_pid_tau_hours' 0.1 h floor,
#   alpha = 0.25/0.1 = 2.5), plus the count of steps whose value differs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_ef9a378b.py
# EXPECTED RESULT tau_0.1h_max_abs_delta > 0 displace (the mutant's alpha 2.5 overshoots and rings, clamped by
#   line 6509 only at d_min/d_max), tau_0.1h_steps_moved > 0 count
# EXPECTED RESULT null_delta_tau_1.5h=0.0 displace (default tau: alpha 0.167, the clip is inert)
# EXPECTED RESULT null_delta_tau_0.25h=0.0 displace (the config flow's floor: alpha exactly 1.0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._power_to_displace_schedule, line 6504
#   `alpha = float(np.clip(self.config.dt_hours / tau, 0.0, 1.0))`.
# Perturbation: key ef9a378b671791ca, the np.clip dropped (CLAMP_DROP), in memory. Direction: delta 0 -> > 0.
# Reachability: services.py:516 admits ecl110_pid_time_constant_hours down to POSITIVE_PARAM_FLOOR (0.01 h);
#   coordinator.py:2739 maps it onto ThermalParameters; thermal_model.py:725 floors it at 0.1 h; the solve step is
#   fixed at 15 min (OptimizationConfig.time_step_minutes), so any tau < 0.25 h gives alpha > 1.
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer

mut = rig.mutant(HeatPumpOptimizer, "_power_to_displace_schedule",
                 "alpha = float(np.clip(self.config.dt_hours / tau, 0.0, 1.0))",
                 "alpha = float((self.config.dt_hours / tau))")
o = rig.bare_optimizer()
p = o.model.params
pw = np.array([0.0] * 4 + [p.max_electrical_power] * 8 + [0.0] * 12)
out = np.full(pw.size, -5.0)
res = {}
for tau in (0.01, 0.1, 0.2, 0.25, 1.5):
    p.ecl110_pid_time_constant_hours = tau
    b = HeatPumpOptimizer._power_to_displace_schedule(o, pw, out)
    m = mut(o, pw, out)
    d = [abs(x - y) for x, y in zip(b, m)]
    res[tau] = (max(d), sum(1 for x in d if x > 0), b, m)
    print(f"RESULT tau_{tau}h_alpha={o.config.dt_hours / p.ecl110_pid_tau_hours:.3f} ratio")
    print(f"RESULT tau_{tau}h_max_abs_delta={max(d):.1f} displace")
    print(f"RESULT tau_{tau}h_steps_moved={res[tau][1]} count")
print(f"RESULT tau_0.01h_baseline={res[0.01][2]}")
print(f"RESULT tau_0.01h_mutant={res[0.01][3]}")
print(f"RESULT null_delta_tau_1.5h={res[1.5][0]} displace")
print(f"RESULT null_delta_tau_0.25h={res[0.25][0]} displace")
rig.tail()
