#!/usr/bin/env python3
# Metric: which DHW plan HeatPumpOptimizer._co_optimize returns ("original" or "replanned") when the re-planned
#   candidate scores EXACTLY best_score - 1e-9 (the tie of the adoption rule), baseline vs mutant; plus the same one
#   ulp either side of the tie (where both arms must agree).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_fd57e13959b23a4c.py
# EXPECTED RESULT tie_baseline=original
# EXPECTED RESULT tie_mutant=replanned
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT null_delta=0 count  (score one ulp below and above the tie: both arms agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize
#   (line 3997 `            if score < best_score - 1e-9:`), called from _optimize_with_dhw.
# Perturbation: line 3997 `<` -> `<=` (CMP_BOUND fd57e13959b23a4c), in memory. Direction: a candidate scoring exactly
#   1e-9 better is adopted instead of kept out (the docstring's 'adopted only if it scores better').
# Harness: the method's collaborators are stubbed (duty_legs.space_headroom, _dhw_build, the planner's coil forecast,
#   the space re-solve) so the adoption comparison is reached with a controlled score; the comparison itself is the
#   production line, recompiled from source.
# Null control: scores one ulp off the tie.
#@PRE
from types import SimpleNamespace  # noqa: E402
NAME = "_co_optimize"
OLD, NEW = "if score < best_score - 1e-9:", "if score <= best_score - 1e-9:"
opt = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
    horizon_hours=4, time_step_minutes=60))
P_MAX = 5.0
space = np.array([5.0, 5.0, 1.0, 1.0])
dhw = np.array([1.0, 0.0, 0.0, 0.0])        # step 0 has DHW and space hard at the headroom -> pinned
replanned = np.array([0.0, 1.0, 0.0, 0.0])
planner = SimpleNamespace(_dhw_coil_wood_forecast=lambda *a: None)
BEST = 12.345678


def run(score):
    cand_space = np.array([4.0, 4.0, 1.0, 1.0])
    with mock.patch.object(optimizer.duty_legs, "space_headroom", lambda *a: np.full(4, 5.0)), \
            mock.patch.object(optimizer, "_dhw_build", lambda *a, **k: (SimpleNamespace(schedule=replanned), None)):
        out = HeatPumpOptimizer._co_optimize(
            opt, None, space_power=space, dhw_power=dhw, status="ok", best_score=BEST,
            solve_space=lambda r, s: (cand_space, "cand", score), p_max=P_MAX, planner=planner)
    return "replanned" if np.array_equal(out[1], replanned) else "original"


tie = BEST - 1e-9
below, above = np.nextafter(tie, -np.inf), np.nextafter(tie, np.inf)
b = (run(tie), run(below), run(above))
with mutated(NAME, OLD, NEW):
    m = (run(tie), run(below), run(above))
print(f"RESULT tie_baseline={b[0]}")
print(f"RESULT tie_mutant={m[0]}")
print(f"RESULT moved={int(b[0] != m[0])} count")
print(f"RESULT null_delta={int(b[1:] != m[1:])} count")
print(f"RESULT below_tie={b[1]}|{m[1]}")
print(f"RESULT above_tie={b[2]}|{m[2]}")
