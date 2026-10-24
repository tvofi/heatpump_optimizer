# D9-s3 — round 10, D9.M2 (does the stress gate see a synthetic 2x?)

Baseline 17f1c55fad1b. Scope: D9-s3, step M2 only. Exposure: none (no docs/, no GitHub).

## Method
`gate_blind_2x.py` drives `tests/stress.py:build_case` on five sweep scenarios
(flat/1z/space, flat/2z/dhw, winter/1z/dhw, shoulder/2z/space,
winter/tariff+cycle), clean then injected with `stress.cpu_scaler(2.0)`, and
judges the injected solve with the gate's own verdicts: `work_over_verdict`
(evaluations, simulate step-equivalents), `kernel_cost_over_verdict`,
`scenario_verdict` (recorded table x SCENARIO_BUDGET_FACTOR) and the global
`live_solve_budget_ratio`. Two arms: solve (wrap `HeatPumpOptimizer.optimize`)
and kernel (wrap the three simulate seams SolverWork meters).

## Finding D9-s3-01 (medium, bug, class I1)
A 2x CPU regression located outside the three metered simulate seams is
invisible to every check the gate runs. Solve arm: solve CPU x2.015 median
(range 1.89-2.21), counts 1.000x, kernel CPU 0.91-1.09x -> **0 of 5 scenarios
flagged**. The only channel that judges solve-wide CPU is the per-scenario
budget at factor 3.0 (> DETECTION_TARGET 2.0), and the global ratio (244x) is
far above any scenario (8.7x-118.6x injected). Perturbation:
STRESS_SCENARIO_FACTOR=1.5 -> 5 of 5 flagged. Null: --factor 1.0 -> 0 of 5.
Positive control: kernel arm -> 5 of 5 flagged (kernel channel), so the harness
can see what the gate sees. Per stress.py's own note the seams are about half
the solve; the objective assembly, cost terms, L-BFGS-B Python and
`_multi_start_minimize` bookkeeping are the unmetered half.
Property: any solve CPU not inside a SolverWork-wrapped seam is judged only at
factor 3.0. Seam rule: `grep -n "_wrapped = " tests/stress.py` lists the
metered set; everything else under `HeatPumpOptimizer.optimize` is unjudged
below 3x.

## Non-findings
- Kernel per-call 2x is caught: `--arm kernel` -> flagged_kernel_arm=5/5.
- Null injection fires nothing: `--factor 1.0` -> 0/5.

## Harnesses
- dev/audit/rounds/round10/D9/s3/gate_blind_2x.py

Timing numbers provisional (load1 40-62 during fan-out; thread_factor 1.000).

## Unfinished
None for M2. Not measured: memory channel (rss/traced) detection of a 2x
retained-bytes regression.
