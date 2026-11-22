#!/usr/bin/env python3
# Metric: the DHW active-step count in the INFO log line 'DHW+Space optimization completed ... in %d steps' (log only; nothing else reads dhw_active_steps), from a hot-water optimize() under a fuse-guard ceiling whose minimum is 0.1 kW (every planned DHW
#   step then sits at exactly the 0.1 kW planning floor), baseline vs mutant; plus the count of planned steps at 0.1.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_deb281264473bdd6.py
# EXPECTED RESULT dhw_active_steps_logged_baseline=0
# EXPECTED RESULT dhw_active_steps_logged_mutant=22
# EXPECTED RESULT null_delta=0 count  (no fuse cap: DHW steps at >= 0.6 kW, both arms identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._optimize_with_dhw
#   (line 5902 `dhw_active_steps = int(np.sum(optimal_dhw > 0.1))`).
# Perturbation: line 5902 `> 0.1` -> `>= 0.1` (CMP_BOUND deb281264473bdd6), in memory. Direction: the planned 0.1 kW DHW
#   steps, excluded on the baseline, are counted under the mutant.
# Null control: the same solve without the fuse cap (no DHW step at exactly 0.1 kW).
#@PRE
#@DHWCAP
NAME = "_optimize_with_dhw"
OLD = "dhw_active_steps = int(np.sum(optimal_dhw > 0.1))"
NEW = "dhw_active_steps = int(np.sum(optimal_dhw >= 0.1))"


def metric(cap):
    r, d, logged = dhw_cap_solve(cap)
    return logged, int(np.sum(d == 0.1)), r


vb, n01, rb = metric(0.1)
nb = metric(6.0)
with mutated(NAME, OLD, NEW):
    vm, _, rm = metric(0.1)
    nm = metric(6.0)
print(f"RESULT dhw_steps_at_0p1={n01} count")
print(f"RESULT dhw_active_steps_logged_baseline={vb}")
print(f"RESULT dhw_active_steps_logged_mutant={vm}")
print(f"RESULT null_delta={int(nb[0] != nm[0])} count")
print(f"RESULT plan_dhw_maxabs_diff_kw={float(np.max(np.abs(np.asarray(rb.dhw_power_schedule) - np.asarray(rm.dhw_power_schedule)))):.4f} kW")
