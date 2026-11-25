#!/usr/bin/env python3
# Metric: count of inputs on which HeatPumpOptimizer._derive_hold_schedule's outcome ("None", the target array, or the
#   exception) differs between baseline and mutant, over hand-picked edge inputs (no charging step, no expensive step,
#   NaN prices, all-zero power, all-maximum power, length 1) plus 3000 seeded random (power, prices) pairs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_8ac9888c3d5fed52.py
# EXPECTED RESULT edge_differ=0 count
# EXPECTED RESULT fuzz_differ=0 count
# EXPECTED RESULT fuzz_guard_true=1113 count  (random cases where the removed guard would have fired)
# EXPECTED RESULT reach_plan_maxabs_diff_kw=0.0000 kW
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._derive_hold_schedule
#   (line 5059 `        if not bool(expensive.any()) or not bool(charging.any()):`), caller optimizer.py:4601.
# Perturbation: line 5059 -> `        if False:` (GUARD_OFF 8ac9888c3d5fed52), in memory. Expected direction: none --
#   with no charging step after_charge is all False, with no expensive step before_peak is all False, so `hold` is
#   empty and line 5074's guard returns the same None: an equivalent mutant.
# Null control: the guard-false cases of the same fuzz (outcomes identical in both arms by construction).
#@PRE
NAME = "_derive_hold_schedule"
OLD, NEW = "if not bool(expensive.any()) or not bool(charging.any()):", "if False:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig())
pmax = opt.model.params.max_electrical_power
f8 = np.full(8, 19.0)
EDGE = {
    "no_charging": (np.full(8, 0.4 * pmax), np.array([0.5, 0.5, 1, 1, 1, 1, 3, 3.0]), f8),
    "nan_prices_no_expensive": (np.full(8, pmax), np.array([0.5, np.nan, 1, 1, 1, 1, 3, 3.0]), f8),
    "all_nan_prices": (np.full(8, pmax), np.full(8, np.nan), f8),
    "zero_power": (np.zeros(8), np.array([0.5, 0.5, 1, 1, 1, 1, 3, 3.0]), f8),
    "max_power_cheap_only_after_peak": (np.full(8, pmax), np.array([3, 3, 1, 1, 1, 1, 0.5, 0.5]), f8),
    "length_one": (np.array([pmax]), np.array([1.0]), np.array([19.0])),
}
rng = np.random.default_rng(11)
FUZZ = []
for _ in range(3000):
    n = int(rng.integers(2, 25))
    FUZZ.append((rng.uniform(0, pmax, n) * (rng.random(n) < rng.random()), np.round(rng.uniform(0.1, 3.0, n), 1), np.full(n, 19.0)))


def guard_fires(power, prices):
    p40, p85 = np.percentile(prices, [40, 85])
    return (not (prices >= p85).any()) or (not ((power > 0.5 * pmax) & (prices <= p40)).any())


def run_all():
    f = lambda a: outcome(lambda: HeatPumpOptimizer._derive_hold_schedule(opt, *a))  # noqa: E731
    return {k: f(v) for k, v in EDGE.items()}, [f(c) for c in FUZZ]


import warnings  # noqa: E402
warnings.simplefilter("ignore")
eb, fb = run_all()
with mutated(NAME, OLD, NEW):
    em, fm = run_all()
print(f"RESULT edge_differ={sum(eb[k] != em[k] for k in EDGE)} count")
for k in EDGE:
    print(f"RESULT edge_{k}={eb[k]}|{em[k]}")
print(f"RESULT fuzz_differ={sum(a != b for a, b in zip(fb, fm))} count")
print(f"RESULT fuzz_guard_true={sum(bool(guard_fires(p, q)) for p, q, _ in FUZZ)} count")
#@HOLD
PR = [0.5] * 6 + [1.0] * 10 + [3.0] * 4 + [1.0] * 4
sb, pb, ob = reach(PR, base_ctx)
sm, pm, om = reach(PR, lambda: mutated(NAME, OLD, NEW))
print(f"RESULT reach_plan_maxabs_diff_kw={float(np.max(np.abs(pb - pm))):.4f} kW")
