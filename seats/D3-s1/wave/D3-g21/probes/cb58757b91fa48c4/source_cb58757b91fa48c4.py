#!/usr/bin/env python3
# Metric: whether HeatPumpOptimizer._derive_hold_schedule proposes a valve-hold schedule ("None" or the target array)
#   on a two-level price profile whose 85th percentile is EXACTLY 1.05 x its 25th (the tie of the flat-price refusal),
#   baseline vs mutant; then through optimize() (smart-write valve, 500 L store, -15 C) the count of proposed
#   schedules (each one a full re-solve), the plan's max |power| difference and the solve CPU.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_cb58757b91fa48c4.py
# EXPECTED RESULT tie_baseline=None
# EXPECTED RESULT tie_mutant=array:23,23,19,19,19,23,23,23
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (p85 = 1.06 x p25: past the tie, both arms propose the same schedule)
# EXPECTED RESULT reach_three_level_10_8_6_proposed_baseline=0 count
# EXPECTED RESULT reach_three_level_10_8_6_proposed_mutant=1 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5054 `        if p85 <= p25 * 1.05:`), caller optimizer.py:4601.
# Perturbation: line 5054 -> `        if p85 < p25 * 1.05:` (CMP_BOUND cb58757b91fa48c4), in memory. Direction: None -> a
#   schedule at exactly a 5 % spread (the tie), one extra re-solve.
# Null control: a 6 % spread, where both arms propose.
#@PRE
NAME = "_derive_hold_schedule"
OLD, NEW = "if p85 <= p25 * 1.05:", "if p85 < p25 * 1.05:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
pmax = opt.model.params.max_electrical_power
power = np.array([pmax, pmax, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0])
tie = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.05, 1.05, 1.05])   # p25 = p40 = 1.0, p85 = 1.05 = 1.0 * 1.05
past = np.where(tie > 1.0, 1.06, 1.0)
floors = np.full(8, 19.0)
call = lambda pr: outcome(lambda: HeatPumpOptimizer._derive_hold_schedule(opt, power, pr, floors))  # noqa: E731
p25, p85 = np.percentile(tie, [25, 85])
print(f"RESULT tie_p85_equals_1p05_p25={int(p85 == p25 * 1.05)} count")
b, bn = call(tie), call(past)
with mutated(NAME, OLD, NEW):
    m, mn = call(tie), call(past)
print(f"RESULT tie_baseline={b}")
print(f"RESULT tie_mutant={m}")
print(f"RESULT moved={int(b != m)} count")
print(f"RESULT null_delta={int(bn != mn)} count")
#@HOLD
PROFILES = {"two_level_16_8": [1.0] * 16 + [1.05] * 8, "three_level_10_8_6": [1.0] * 10 + [1.02] * 8 + [1.05] * 6}
for tag, PR in PROFILES.items():
    a, b_ = np.percentile(PR, [25, 85])
    assert b_ == a * 1.05, tag
    sb, pb, ob = reach(PR, base_ctx)
    sm, pm, om = reach(PR, lambda: mutated(NAME, OLD, NEW))
    print(f"RESULT reach_{tag}_proposed_baseline={sb['proposed']} count")
    print(f"RESULT reach_{tag}_proposed_mutant={sm['proposed']} count")
    print(f"RESULT reach_{tag}_plan_maxabs_diff_kw={float(np.max(np.abs(pb - pm))):.4f} kW")
    print(f"RESULT reach_{tag}_objective_delta={om - ob:.6f}")
    print(f"RESULT reach_{tag}_cpu_baseline_s={sb['cpu_s']:.2f} s (provisional)")
    print(f"RESULT reach_{tag}_cpu_mutant_s={sm['cpu_s']:.2f} s (provisional)")
