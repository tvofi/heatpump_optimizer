# D0 — price optimality — round 4

- **Baseline SHA**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- **Tree**: isolated worktree `.claude/worktrees/audit-r4-D0`
- **Machine**: 8-core Apple M1, 8 GB, macOS 25.6.0, numpy on OpenBLAS, python 3.11
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, always from the worktree root.
- **Gate lock**: not taken. `tests/stress.py` was not run and no full gate was run.
- **Contention**: every number in this report is an objective value, a ratio of
  two objective values, an iteration count or a schedule-times-price sum. None
  is a wall, CPU or RSS figure, so none is provisional. `thread_factor` was
  1.0000–1.0001 on all four harnesses; `load1` at the end of each run was
  13.53 / 6.90 / 6.74 / 6.32 — a busy shared box, which is why no timing claim
  is made here.

## Method

The hunt is for a plan the shipped solver returns that a better search beats on
**the same objective, bounds and inputs**, with comfort no worse. Everything is
scored with the production objective, never with energy price alone: the
objective is captured by hooking `optimizer.py:_scoped_minimize` — the single
funnel through which every L-BFGS-B call in the optimizer passes — so a
challenger arm changes exactly one option in the dict production builds and
nothing else. Plans are compared through `OptimizationResult.objective_value`,
which the production path computes itself.

Grid: the 7 priced profiles of `tests/profiles.py` plus `flat` (the null
control), × 5 weather profiles, × single/two-zone, DHW on (the shipped
default), horizon 24 h, 15-minute steps — 80 cells for the main harness, a
10–12 cell subset for the three supporting ones. Every aggregate is printed
with its range and with the single most favourable cell dropped.

The three homes of sub-optimality named in the brief were each raced:

| home | arm | result |
|---|---|---|
| the budget (iterations) | `maxiter` × 15 | **0.0000 % in every cell** — never binding |
| the budget (tolerance) | `ftol` 1e-6 → 1e-14 | the entire gap (finding 01) |
| the budget (gradient) | `gtol` → 1e-12 | **0.0000 % in every cell** |
| seeding / basin | 12 extra structural starts, `_MULTI_START_SOLVES` 4 → 16 | ≈ the same points the tolerance arm reaches (see non-findings) |
| structure — restart | `_LBFGSB_RESTART_KEEP_REL` 2e-2 → 0, looped to convergence | max 0.135 %, mean 0.014 % — non-finding |
| structure — decomposition | DHW ↔ space co-optimization iterated 4× | **0.0000 % in every cell** — non-finding |
| MPC masking | one simulated day of closed-loop re-planning | kills the money claim (see below) |

## Findings

### D0-01 — the shipped plan is not a minimum of its own objective (`low`, bug)

`optimizer.py:_multi_start_minimize` and `_lbfgsb_restart` both pass
`options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4}`. `ftol` is L-BFGS-B's
*relative one-iteration* stop test, so the solve halts on a flat stretch of the
descent while further descent remains. Changing that one number to 1e-14 —
identical seeds, identical `_MULTI_START_SOLVES`, identical bounds, identical
batched jac, identical `maxiter`, identical `eps` — lowers the production
objective in **34 of 70 priced cells**, 18 of them by more than 0.1 %:

```
mean_gap_priced_pct       0.1176 %      max 0.7998 %   LOO-mean 0.1078 %
mean_gap_flat_pct         0.1048 %      max 0.5543 %   LOO-mean 0.0549 %   (null control)
cells_negative_gap        0
cells_challenger_worse_comfort 0   (of 80)
cells_step0_differs_gt_0p01kW  9   (of 70), max step-0 delta 4.056 kW
```

Per price profile (mean / max over 10 weather×topology cells each):

| profile | mean | max |
|---|---|---|
| summer_negative | 0.238 % | 0.686 % |
| winter_extreme | 0.158 % | 0.780 % |
| shoulder | 0.150 % | 0.800 % |
| winter_narrow | 0.117 % | 0.569 % |
| winter_typical | 0.110 % | 0.796 % |
| winter_moderate | 0.045 % | 0.184 % |
| summer_typical | 0.005 % | 0.051 % |
| **flat (null control)** | **0.105 %** | **0.554 %** |

**Feasibility parity holds**: in none of the 80 cells is the challenger worse
on comfort (degree-steps below the configured 17 °C floor); the largest
violation on either arm anywhere is 0.147 degree-steps. Bounds are enforced by
L-BFGS-B itself, so the challenger is feasible by construction.

**What the null control says, and it is the important half.** The gap does
**not** vanish at `flat` prices — 0.105 % mean against 0.118 % priced. So this
is *not* a price-optimality gap: it is a stopping-rule defect that leaves the
same residual whatever the price shape. Named, per the brief: premature
termination of the local solve, not basin selection.

**No money claim is made, and the reason is measured.** `mpc_realised.py` runs
one simulated day of closed-loop re-planning (every 2 h, 24 h horizon, exact
plant) and compares realised SEK. On priced profiles the tightened arm is
0.321 SEK/day cheaper on average (0.56 % of a 57.02 SEK bill, LOO 0.148), but
production is cheaper in **4 of 8** priced cells, and at flat prices the
tightened arm is **2.11 SEK/day more expensive** — the null control moves in
the *opposite* direction and by a larger magnitude than the priced mean. A
saving that fails its null control that badly is not a saving. What is
established is the objective gap and the changed step-0 command, not a bill.

Severity `low` on that basis: a real solver defect, bounded, with no
demonstrated wrong money and no wrong comfort.

- **Harness**: `tools/audit/round4/D0/ftol_gap.py` (80 cells) and
  `tools/audit/round4/D0/mpc_realised.py` (10 cells, MPC realisation).
- **Instrumented symbol**: `custom_components/heatpump_optimizer/optimizer.py:_scoped_minimize`,
  driving `optimizer.py:HeatPumpOptimizer.optimize`.
- **Perturbation**: set `ftol` to 1e-14 in `_multi_start_minimize` and
  `_lbfgsb_restart` → every gap RESULT falls to 0. Raise it to 1e-4 → they grow.
- **Metric**: relative objective gap `(J_prod − J_ftol)/|J_prod|` between the
  shipped plan and the same solve with only L-BFGS-B's `ftol` tightened.
- **Proposed fix scope**: one constant in `optimizer.py`, plus whatever golden
  fixtures move — which is precisely the cost the current value was chosen to
  avoid (`_LBFGSB_RESTART_KEEP_REL`'s docstring records the same trade-off).
  This is a decision for the owner, not an obvious repair.

### D0-02 — the budget the code and its own gate police is never the binding one (`low`, bug)

Three things in the tree treat the **iteration** budget as the solution-quality
control: `_MULTI_START_SOLVES = 4`, `maxiter=200` (space-only) / `maxiter=300`
(DHW path), and `tests/optimality.py`'s challenger 3, which starves `maxiter`
to 3 and asserts "the production iteration budget buys a materially better
plan". Measured over the shipped configuration:

```
lbfgsb_solves_observed          420   (ftol_gap.py)   68  (budget_knobs.py)
solves_terminating_on_maxiter     0                    0
max_nit_observed                 —                    52   (cap 200 / 300)
median_nit_observed              —                     8
max_gain_maxiter_x15_priced_pct                   0.0000 %
max_gain_gtol_1e-12_priced_pct                    0.0000 %
max_gain_ftol_1e-14_priced_pct                    0.7958 %
```

Not one of 488 observed L-BFGS-B calls terminates on the iteration cap; the
worst observed `nit` is 52 against a cap of 200, and the median is 8.
Multiplying the cap by 15 changes no plan anywhere, to the last printed digit,
on priced and flat cells alike. The budget therefore has 4–6× headroom it never
uses, while the parameter that does decide every plan — `ftol`, D0-01 — has
no gate at all. The existing gate is not wrong (starving `maxiter` to 3 really
does cost 16 %), it is aimed at a knob with slack.

Severity `low`: nothing a user sees today; it is a control that does not control.

- **Harness**: `tools/audit/round4/D0/budget_knobs.py`; the 420-solve census is
  also emitted by `tools/audit/round4/D0/ftol_gap.py`.
- **Instrumented symbol**: `custom_components/heatpump_optimizer/optimizer.py:_multi_start_minimize`
  (per-solve `nit`/`status` census) and `:_scoped_minimize` (the arms).
- **Perturbation**: cut production's `maxiter` to 3.
  `max_gain_maxiter_x15_priced_pct` must then become large and
  `solves_terminating_on_maxiter` must equal the solve count — the metric moves,
  it is simply zero at the shipped budget.
- **Metric**: the number of L-BFGS-B calls whose scipy `status` is 1 or whose
  `nit` reaches the `maxiter` production passed, over a whole solve grid; and
  the relative objective change from multiplying that `maxiter` by 15.
- **Proposed fix scope**: either lower `maxiter` to something the solve can
  actually reach (a D9 runtime saving, not a D0 one) or move the quality gate
  onto `ftol`. Both are one-line changes plus a gate edit; the second is the one
  that would have caught D0-01.

## Non-findings

Each is a lead that was raced and did not hold. The command is the committed
harness; the number is from its RESULT block.

1. **The discarded restart.** `_lbfgsb_restart` computes a polished point and
   throws it away unless it beats the prior by `_LBFGSB_RESTART_KEEP_REL = 2e-2`
   relative — a large bar, and the discarded point is strictly better. Running
   that restart to convergence and keeping every improvement gains
   **mean 0.014 %, max 0.135 %** over 10 priced cells (LOO-mean 0.0006 %; flat
   null control 0.012 %). The threshold is not where the objective is.
   `nonfindings.py`, `RESULT max_gain_restart_priced_pct=0.134817 %`.
2. **The single co-optimization pass.** `_co_optimize` re-plans hot water
   against the solved space profile exactly once. Iterating it up to four times,
   adopting only strict improvements and using production's own `pinned`
   widening of `space_demand`, changes the objective by **0.0000 % in all 12
   cells** — the single pass already reaches the fixed point on this grid, and
   `cells_coopt_iter_worse_than_production=0`. `nonfindings.py`.
   (An earlier arm that dropped the `pinned` widening was 1.2–1.5 % *worse* than
   production on `summer_negative`, which is a positive result for that
   widening.)
3. **The iteration cap.** `maxiter` × 15: 0.0000 % in all 12 cells.
   `budget_knobs.py`.
4. **The gradient tolerance.** `gtol` 1e-5 → 1e-12: 0.0000 % in all 12 cells.
   `budget_knobs.py`.
5. **Wider seeding.** Twelve extra structural starts (level schedules at
   0/15/30/50/70/85/100 % of each step's upper bound, plus the production guess
   scaled by 0.25/0.5/0.75/1.25/1.5) with `_MULTI_START_SOLVES` raised to 16 and
   production's `ftol`: measured 0.00–0.76 % on a 10-cell probe, i.e. the same
   points the tolerance arm reaches and never materially past them. The
   committed harness for this is `outer_bound.py`; **it was written but not
   executed inside the round's wall clock**, so this row is a lead, not a
   result. See "What I could not finish".
6. **Comfort parity.** Across all 80 cells of `ftol_gap.py` no challenger plan
   is worse on comfort than production's, and the worst violation on either arm
   is 0.147 degree-steps below the 17 °C floor. Production never buys its
   objective with comfort the challenger keeps.

## Harnesses

All under `tools/audit/round4/D0/`, each runnable by the single command in its
header, from the repository root, with `PYTHONPATH=tests/hastub`.

| file | what it measures | run? |
|---|---|---|
| `d0lib.py` | shared: BLAS thread pin (before any numpy import), cell builder over `tests/profiles.py`, the two `mock.patch.object` capture idioms, `RESULT`/`thread_factor`/`load1`/`swapins` plumbing, leave-one-out | imported |
| `ftol_gap.py` | D0-01: objective gap, 80 cells, with comfort parity, step-0 delta and the 420-solve `maxiter` census | yes → `ftol_gap.out` |
| `mpc_realised.py` | D0-01: realised SEK/day under closed-loop re-planning, 10 cells | yes → `mpc_realised.out` |
| `budget_knobs.py` | D0-02: `maxiter` / `gtol` / `ftol` one at a time, 12 cells | yes → `budget_knobs.out` |
| `nonfindings.py` | non-findings 1 and 2, 12 cells | yes → `nonfindings.out` |
| `outer_bound.py` | non-finding 5: the gap to a 16-start, tight-tolerance outer bound | **no** |

The `.out` files beside them are the exact stdout of the run the numbers in this
report come from.

## What I could not finish

- **`outer_bound.py` was not executed.** It is committed and self-describing,
  but the round's wall clock went on the 80-cell main harness. The seeding
  numbers quoted in non-finding 5 come from an uncommitted probe of the same
  logic, so treat them as indicative only; the judge should run
  `outer_bound.py` before relying on "seeding buys nothing once the stop rule is
  fixed".
- **Topologies beyond single/two-zone.** Valve storage, wood fuel, manual pins,
  power caps and the grid-fee tariff were not raced; the grid here is
  price × weather × zones × DHW. A bounds shape that puts the solve on the
  scalar scipy-FD path instead of the batched jac was therefore not covered.
- **Horizons other than 24 h.** 6 h and 48 h were not run.
- **The coordinator captures** (`tests/golden.py:_capture_coordinator`) were not
  raced; every cell here is built directly from `tests/profiles.py`.
- **A DHW-block-placement challenger.** The objective prices space comfort and
  the *combined* draw but carries no DHW term at all — the tank schedule is
  decided entirely by `_build_dhw_requirements` and handed to the space solve as
  a constant. A challenger that shifts a DHW block therefore needs its own
  feasibility check against `floor_temps`/`ready_temps` rather than the
  objective. Designed, not built. This is the most promising unexplored lead in
  the dimension.
- **Quiet-window re-takes**: none needed. No timing, CPU or RSS number is
  claimed.

## Exposure

- `CLAUDE.md` is loaded automatically at session start and names
  `docs/audit-2026-09.md`, `docs/backlog.md` and `docs/plan-2026-09-open-issues.md`.
  **None of them was opened**, nor was any `docs/audit-*.md`, `docs/backlog.md`
  or `docs/plan-*.md`. `tools/audit/round3/` is absent from this tree.
- `gh` was not run and GitHub was not read.
- Production comments in `optimizer.py` cite earlier audit ids (`R1-D0-01`,
  `R1-D0-02`, `D9-01`) and issue numbers (`#89`, `#97`, `#234`, `#288`, `#400`,
  `#826`). Per `COMMON.md` these were read as context for what the code does,
  not as a to-do list, and no earlier finding was looked up.
- Files read outside `custom_components/heatpump_optimizer/`: `tests/profiles.py`,
  `tests/optimality.py`, `tests/stress.py` (the thread pin and
  `reference_solve` docstring), `tests/rolling.py` (the loop shape),
  `tools/audit/README.md`, `tools/audit/briefs/COMMON.md`,
  `tools/audit/briefs/D0.md`, `tools/audit/round4/BASELINE.md`.
- Nothing outside `tools/audit/round4/D0/` was modified. No production or test
  file was edited; every arm is a `mock.patch.object` inside a harness.
