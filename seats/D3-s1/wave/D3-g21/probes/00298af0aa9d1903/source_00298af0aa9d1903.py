#!/usr/bin/env python3
# Metric: what HeatPumpOptimizer._derive_hold_schedule returns when charging and an expensive block both exist but no
#   step lies between them ("None" or the target array), baseline vs mutant; then through optimize() (smart-write
#   valve, 500 L store, -15 C) the count of proposed schedules (each one a full re-solve), the plan's max |power|
#   difference and the solve CPU.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_00298af0aa9d1903.py
# EXPECTED RESULT nohold_baseline=None
# EXPECTED RESULT nohold_mutant=array:23,23,23,23,23,23,23,23
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (a profile with hold steps: both arms return the same schedule)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5074 `        if not bool(hold.any()):`), caller optimizer.py:4601.
# Perturbation: line 5074 -> `        if False:` (GUARD_OFF 00298af0aa9d1903), in memory. Direction: None -> an all-default
#   target array (no hold step), which the caller re-solves in full and then discards (same objective, not < -1e-9).
# Null control: an input with hold steps (the guard is false in both arms).
#@PRE
NAME = "_derive_hold_schedule"
OLD, NEW = "if not bool(hold.any()):", "if False:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
pmax = opt.model.params.max_electrical_power
f8 = np.full(8, 19.0)
adjacent = (np.array([pmax] * 5 + [0.0] * 3), np.array([0.5] * 5 + [3.0] * 3), f8)     # charge right up to the peak
with_hold = (np.array([pmax, pmax, 0.5, 0.5, 0.5, 0, 0, 0]), np.array([0.5, 0.5, 1, 1, 1, 3, 3, 3.0]), f8)
call = lambda a: outcome(lambda: HeatPumpOptimizer._derive_hold_schedule(opt, *a))  # noqa: E731
b, bn = call(adjacent), call(with_hold)
with mutated(NAME, OLD, NEW):
    m, mn = call(adjacent), call(with_hold)
print(f"RESULT nohold_baseline={b}")
print(f"RESULT nohold_mutant={m}")
print(f"RESULT moved={int(b != m)} count")
print(f"RESULT null_delta={int(bn != mn)} count")
#@HOLD
PROFILES = {"two_level_16_8": [1.0] * 16 + [1.2] * 8, "cheap_then_peak_12_12": [0.5] * 12 + [3.0] * 12}
for tag, PR in PROFILES.items():
    sb, pb, ob = reach(PR, base_ctx)
    sm, pm, om = reach(PR, lambda: mutated(NAME, OLD, NEW))
    print(f"RESULT reach_{tag}_proposed_baseline={sb['proposed']} count")
    print(f"RESULT reach_{tag}_proposed_mutant={sm['proposed']} count")
    print(f"RESULT reach_{tag}_plan_maxabs_diff_kw={float(np.max(np.abs(pb - pm))):.4f} kW")
    print(f"RESULT reach_{tag}_objective_delta={om - ob:.6f}")
    print(f"RESULT reach_{tag}_cpu_baseline_s={sb['cpu_s']:.2f} s (provisional)")
    print(f"RESULT reach_{tag}_cpu_mutant_s={sm['cpu_s']:.2f} s (provisional)")
