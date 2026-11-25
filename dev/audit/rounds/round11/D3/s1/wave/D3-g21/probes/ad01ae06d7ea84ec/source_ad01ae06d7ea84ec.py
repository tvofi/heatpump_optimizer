#!/usr/bin/env python3
# Metric: whether HeatPumpOptimizer._derive_hold_schedule proposes a valve-hold schedule ("None" or the target array)
#   on a price profile whose spread is under 5 % (p85 < 1.05*p25), baseline vs mutant; then through optimize()
#   (smart-write valve, 500 L store) the count of proposed schedules (each one costs a full re-solve) and
#   the plan's max |power| difference between the arms.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ad01ae06d7ea84ec.py
# EXPECTED RESULT nearflat_baseline=None
# EXPECTED RESULT nearflat_mutant=array:23,23,19,19,19,19,23,23
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (exactly flat prices: every step is 'expensive', hold is empty, None in both arms)
# EXPECTED RESULT reach_proposed_baseline=0 count
# EXPECTED RESULT reach_proposed_mutant=1 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5054 `        if p85 <= p25 * 1.05:`), caller optimizer.py:4601.
# Perturbation: line 5054 -> `        if False:` (GUARD_OFF ad01ae06d7ea84ec), in memory. Direction: None -> a schedule
#   at a sub-5 % spread, i.e. one extra full re-solve per plan on near-flat days.
# Null control: exactly flat prices (both arms None).
#@PRE
NAME = "_derive_hold_schedule"
OLD, NEW = "if p85 <= p25 * 1.05:", "if False:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
pmax = opt.model.params.max_electrical_power
power = np.array([pmax, pmax, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0])
near = np.array([1.00, 1.00, 1.01, 1.01, 1.01, 1.02, 1.03, 1.03])   # p85/p25 = 1.03
flat = np.full(8, 1.0)
floors = np.full(8, 19.0)
call = lambda pr: outcome(lambda: HeatPumpOptimizer._derive_hold_schedule(opt, power, pr, floors))  # noqa: E731
b, bf = call(near), call(flat)
with mutated(NAME, OLD, NEW):
    m, mf = call(near), call(flat)
print(f"RESULT nearflat_baseline={b}")
print(f"RESULT nearflat_mutant={m}")
print(f"RESULT moved={int(b != m)} count")
print(f"RESULT null_delta={int(bf != mf)} count")
#@HOLD
PR = [1.0] * 6 + [1.02] * 12 + [1.04] * 6
sb, pb, ob = reach(PR, base_ctx)
sm, pm, om = reach(PR, lambda: mutated(NAME, OLD, NEW))
print(f"RESULT reach_proposed_baseline={sb['proposed']} count")
print(f"RESULT reach_proposed_mutant={sm['proposed']} count")
print(f"RESULT reach_plan_maxabs_diff_kw={float(np.max(np.abs(pb - pm))):.4f} kW")
print(f"RESULT reach_objective_delta={om - ob:.6f}")
print(f"RESULT reach_cpu_baseline_s={sb['cpu_s']:.2f} s (provisional)")
print(f"RESULT reach_cpu_mutant_s={sm['cpu_s']:.2f} s (provisional)")
