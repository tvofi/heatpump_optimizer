#!/usr/bin/env python3
# Metric: predictive_info.dhw_preheat_hours, hours (published by sensor.py:1249), from a hot-water optimize() under a fuse-guard ceiling whose minimum is 0.1 kW (every planned DHW
#   step then sits at exactly the 0.1 kW planning floor), baseline vs mutant; plus the count of planned steps at 0.1.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ed5e3ec5b879ed90.py
# EXPECTED RESULT dhw_preheat_hours_baseline=0.0
# EXPECTED RESULT dhw_preheat_hours_mutant=13.0
# EXPECTED RESULT null_delta=0 count  (no fuse cap: DHW steps at >= 0.6 kW, both arms identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._optimize_with_dhw
#   (line 5962 `float(np.sum((optimal_dhw > 0.1) & ~in_demand_window) * dt), 2`).
# Perturbation: line 5962 `> 0.1` -> `>= 0.1` (CMP_BOUND ed5e3ec5b879ed90), in memory. Direction: the planned 0.1 kW DHW
#   steps, excluded on the baseline, are counted under the mutant.
# Null control: the same solve without the fuse cap (no DHW step at exactly 0.1 kW).
#@PRE
#@DHWCAP
NAME = "_optimize_with_dhw"
OLD = "float(np.sum((optimal_dhw > 0.1) & ~in_demand_window) * dt), 2"
NEW = "float(np.sum((optimal_dhw >= 0.1) & ~in_demand_window) * dt), 2"


def metric(cap):
    r, d, logged = dhw_cap_solve(cap)
    return r.predictive_info['dhw_preheat_hours'], int(np.sum(d == 0.1)), r


vb, n01, rb = metric(0.1)
nb = metric(6.0)
with mutated(NAME, OLD, NEW):
    vm, _, rm = metric(0.1)
    nm = metric(6.0)
print(f"RESULT dhw_steps_at_0p1={n01} count")
print(f"RESULT dhw_preheat_hours_baseline={vb}")
print(f"RESULT dhw_preheat_hours_mutant={vm}")
print(f"RESULT null_delta={int(nb[0] != nm[0])} count")
print(f"RESULT plan_dhw_maxabs_diff_kw={float(np.max(np.abs(np.asarray(rb.dhw_power_schedule) - np.asarray(rm.dhw_power_schedule)))):.4f} kW")
