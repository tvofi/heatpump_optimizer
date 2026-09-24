# D0 — price optimality, audit round 6

Baseline: `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), measured in the
worktree `~/audit-r6-D0`. Interpreter
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` (numpy 2.4.6,
scipy 1.17.1); every run from the repository root with `PYTHONPATH=tests/hastub`.

Machine: darwin arm64, 8-core M1, 8 GB, **shared with the other round-6
finders for the whole session** (`load1` printed beside every RESULT; 6.2-21.4
across the runs). Every number below is a count, a ratio or an objective value,
all contention-immune; wall figures carry `provisional: true`.

Measured conditions, printed by the harnesses themselves: `thread_factor =
1.0000` on `seed_race.py`'s DEEP re-run (`process_cpu = 201.83 s`,
`thread_cpu = 201.83 s` — BLAS pinned to one thread before numpy is imported,
no deliberate second thread), `load1` 6.2-21.4, and `swapins` read from
`vm_stat`'s cumulative `Pageins` counter (a machine-lifetime figure, printed so
its magnitude is visible; it is **not** a per-run count).

## Method

The brief asks whether the shipped solver minimises the objective it has. The
method that answers it without re-implementing anything is the **capture
harness** `tests/optimality.py` already uses as an idiom: patch
`optimizer._multi_start_minimize`, keep the seam intact, and record the
**objective closure itself** — the callable `_optimize_space_only` /
`_optimize_with_dhw` built — with the candidate list, bounds, `args`, `maxiter`
and `batch_objective` it was called with. Every challenger is raced against
*that* closure, so no cost is re-derived from constants or from reading code,
and the brief's "same objective, bounds and inputs" is satisfied literally.

Two properties make the numbers trustworthy, and both are re-measured in the
harness rather than asserted:

* **`production_replay_bitwise_cells = 80/80`** — re-invoking the seam with the
  recorded arguments reproduces the shipped objective value exactly, so the
  captured call is the one that produced the plan.
* **`null_control_bitwise_cells = 80/80`, `null_control_max_abs = 0.000000 %`** —
  a null arm appending three candidates that pre-score strictly worse than the
  worst already-refined one leaves the result bit-identical.

The null is not decorative. A first attempt appended byte-copies of the
existing candidates and the number moved by up to **3.0 %**. The cause is in
production, not in the harness: `_multi_start_minimize` ranks candidates by
their score **at the raw seed** and keeps the best `_MULTI_START_SOLVES`, and
Python's stable sort gives an equal-scoring duplicate the position beside its
twin — so a duplicate *displaces a real basin* from the refined set, and
`two|flat|winter_cold` went from `100.0011` (4 candidates) to `100.4995` (20
candidates, 16 of them copies). That is this dimension's mechanism seen from
the other side; it is why the null above uses strictly-worse candidates
instead of copies.

## Finding D0-01 — the space solve's candidate set leaves cheaper basins unfound

**Severity: medium. Stop-rule class: bug.**

**Instrumented symbol:** `heatpump_optimizer.optimizer:_multi_start_minimize`
(the objective closure, candidate list, bounds, `args`, `maxiter` and
`batch_objective` recorded; the seam itself left intact).

**Metric definition:** `gap_rel` of a cell = (A - B) / A, where A is the
objective value the shipped space plan scores on the solve's *own* captured
objective closure and B is the value `_multi_start_minimize` returns for the
same closure, bounds, `args`, `maxiter` and batched jac when its candidate list
is extended with 8 structured seeds and `optimizer._MULTI_START_SOLVES` is
raised to the candidate count; a challenger counts only if its comfort-floor
violation (degree-steps below the horizon's own `temp_min_bounds`, from
`ThermalModel.simulate_trajectory`) does not exceed production's.

**Perturbation:** the candidate list handed to `_multi_start_minimize` is
extended with 8 structured seeds — bang-bang schedules that buy the cheapest
steps first at 0.2 / 0.35 / 0.5 / 0.65 / 0.8 / 1.0 / 1.25 / 1.5 x the shipped
plan's own total energy, each clipped to the solve's own per-step upper bounds —
and `_MULTI_START_SOLVES` is raised from 4 to the candidate count so every
candidate is refined. **Direction: the objective must FALL.** Production's
`starts` list holds the smooth price-weighted guess, a bang-bang at the
baseline's own total energy, the thermostat baseline, and a bang-bang at 0.35 x
that energy; the added seeds are a different set of basins.

**Harness:** `tools/audit/round6/D0/seed_race.py` — the 8 x 5 grid of
`profiles.prices` x `profiles.weather`, single- and two-zone, `dhw=0`.

```
PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round6/D0/seed_race.py
```

### Numbers

| quantity | value |
|---|---|
| cells run | 80 (16 `summer_warm` cells have no heating at all, gap 0 — excluded) |
| `production_replay_bitwise_cells` | 80/80 |
| `null_control_bitwise_cells` | 80/80 (`null_control_max_abs = 0.000000 %`) |
| gap median (`gap_seeds8_all`) | **0.0615 %** |
| gap max | **11.1729 %** |
| cells with gap > 0.1 % | 24 of 64 |
| cells with gap > 0.5 % | 5 of 64 |
| leave-one-out range (most favourable cell dropped) | **[0.0000 %, 11.1729 %]** |
| inverse arm, `_MULTI_START_SOLVES = 1` (`gap_cut1`) | median **-0.0018 %**, max **0.0000 %** |
| flat-price control, median | **0.0146 %** (8 cells) |
| non-flat, median | **0.0729 %** (56 cells) |
| flat-price control, max | 0.3087 % |

The widest ten cells (`|dhw=0` elided):

| cell | gap | production obj | challenger obj | step-0 prod->ch | steps differ |
|---|---|---|---|---|---|
| `one|summer_negative|shoulder` | 11.1729 % | 0.2865 | 0.2545 | 0.000->0.000 | 13 |
| `one|summer_negative|summer_cool` | 1.3576 % | 0.6694 | 0.6603 | 0.000->0.000 | 16 |
| `one|winter_narrow|shoulder` | 1.0958 % | 11.5918 | 11.4647 | 0.000->0.016 | 17 |
| `two|summer_negative|winter_mild` | 0.7339 % | 1.9463 | 1.9320 | 0.000->0.000 | 41 |
| `one|shoulder|winter_cold` | 0.6853 % | 48.8137 | 48.4792 | 4.552->6.000 | 48 |
| `one|winter_extreme|shoulder` | 0.3846 % | 9.4464 | 9.4101 | 0.582->0.000 | 28 |
| `one|winter_typical|summer_cool` | 0.3383 % | 3.3181 | 3.3069 | 0.000->0.000 | 17 |
| `two|winter_moderate|winter_cold` | 0.3235 % | 95.3390 | 95.0305 | 6.000->6.000 | 64 |
| `two|winter_moderate|summer_cool` | 0.3214 % | 4.6783 | 4.6633 | 0.000->0.000 | 8 |
| `two|flat|winter_cold` | 0.3087 % | 100.0011 | 99.6924 | 5.478->6.000 | 96 |

**Feasibility parity:** on every cell above the challenger's comfort-floor
violation is 0.000000 degree-steps, equal to production's, and no bound is
exceeded because the seeds are clipped to the solve's own captured `bounds`.

**Leave-one-out.** The aggregate is not a referendum on one row: dropping the
single most favourable cell leaves the range `[0.0000 %, 11.1729 %]`, and 19 of
the 64 heating cells have gap exactly 0. The median (0.0615 %) is the honest
summary; the tail is the story.

### What the effect is, and what it is not

* **It is the candidate set, not the budget.** `gap_cut1` — the inverse
  perturbation, refining only the single best-scoring candidate — is never
  better than production (max 0.0000 %, median -0.0018 %). The separate
  `maxiter`/`ftol` arm measured in `challenge.py` (`polish_gap_rel`)
  contributes to a minority of the cells; the ranked list, extended, is what
  moves the number.
* **The flat-price arm does not vanish, and the residual is named.** At
  `profiles.prices("flat")` the median gap falls 5.0x (0.0146 % vs 0.0729 %)
  and the max by 36x (0.3087 % vs 11.1729 %), but not to zero. A flat price
  removes the *when* signal entirely, so what survives there is exactly the
  claimed mechanism — a solver that stops short of its own reachable minimum —
  and not a price-arbitrage gain. D0-01 is a **solver-convergence** defect; the
  structured price profiles amplify it and are not its cause.
* **MPC does not mask it.** Of the 24 cells with a gap above 0.1 %, **11 change
  the step-0 action** (46 %); the median gap cell differs on 21 of 96 steps. On
  those cells the first action the integration publishes is a different
  dispatch, so a re-plan next cycle does not reproduce the trajectory.
* **Money, and the sign trap.** The objective is the production criterion and
  contains the terminal credit, so a lower objective is not always a smaller
  bill. `delta_sek` (energy bought at the horizon's own import prices) is
  **+2.225 SEK/day on `two|winter_moderate|winter_cold` (2.74 % of that day's
  energy bill)** and +0.889 SEK/day on `two|winter_typical|winter_cold`
  (1.51 %), in 7 of 64 cells above +0.1 SEK/day — while 12 cells are below
  -0.1 SEK/day, because the challenger stores more heat than the shipped plan
  and the terminal credit pays for it. The claim this finding makes is the
  objective one; the SEK column is reported so it is not read the other way.

### Why the gate does not see it

`tests/optimality.py` races **one** scenario per topology
(`winter_typical` / `winter_cold`) with a same-total-energy greedy schedule and
300 random perturbations, floored at 0.965 of the optimizer's cost. On that
scenario the solver finds the basin: `one|winter_typical|winter_cold` has gap
0.0000 % here. The cells that carry a gap (`shoulder`/`winter_cold`,
`winter_narrow`/`shoulder`) are not in the file.

## Finding D0-02 — the candidate-count comment is stale, and one candidate is always dropped

**Severity: low. Stop-rule class: hygiene.**

**Instrumented symbol:** `heatpump_optimizer.optimizer:_multi_start_minimize`
(the candidate list it is handed, counted at the seam).

**Metric definition:** the number of candidates offered to
`_multi_start_minimize` in one production solve, against
`optimizer._MULTI_START_SOLVES`, the number of them refined.

**Perturbation:** setting `HeatPumpOptimizer._prev_shipped_plan` — which
`coordinator:_warm_seeded` sets on every production cycle — from unset to the
previous cycle's plan. Direction: the offered count must rise by one.

**Harness:** `tools/audit/round6/D0/discard.py` (`CELLS=SPACE`).

```
PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round6/D0/discard.py     # CELLS=SPACE for the 80-cell grid
```

**Numbers.** 80/80 cells offer **5** candidates and have `_MULTI_START_SOLVES =
4`, so `n_discarded = 1` in 80/80. `optimizer.py:251` states the opposite:
*"The candidates number four, so this is the whole list."* The comment is false
in every production cell because #1295 added the coordinator's warm start as a
fifth.

**Consequence measured as nil:** re-running the same seam with the cut raised to
refine the dropped candidate changes the shipped objective by `gap_max =
0.0000 %`, `n_cells_gap_gt_0 = 0` of 80. The dropped candidate is always the
worst-scoring at its own start. So this is a documentation defect and not a
money one, which is exactly why it is filed separately from D0-01 and at `low`.

## Non-findings (checked, held)

| what | harness | number |
|---|---|---|
| `_co_optimize` is a dead pass | `diag_coopt2.py` | 32 cells: 12 early-return (`not np.any(pinned) and not coil_replan`), 20 re-plan, **4 ship a DHW plan that differs from the first**. The contention pass fires. |
| A further DHW<->space pass would help | `coopt.py` (`CELLS=FIRE K=5`) | On the 4 cells where the pass is adopted plus the widest-gap cell, K=5 gives `gap = 0.0000 %`; the loop returns identical plans after the second pass. Converged. |
| The refinement budget (`maxiter`) binds | `challenge.py`; `tests/optimality.py`'s own note | Production passes `maxiter` 200 (space-only) / 300 (with DHW); the observed `nit` never approaches it — round 4 measured 0 of 488 calls at the cap, worst nit 52. **Inherited, not re-measured here.** |
| The objective closure is pure | direct probe in `seed_race.py`'s development | Calling the captured `objective` 6x at one `x` returns bit-identical values, and `objective_batch(matrix)[0]` equals the scalar at the same row to `0.000e+00`. So the seam is a function and the replay/null equalities above mean something. |
| The batched jac moves the plan | `tests/optimality.py` challengers 4/5 (pre-existing) | Not re-measured. The captured `batch_objective` was used on **both** arms of every race, so both ran the jac path production would — the brief's jac trap is honoured. |
| A low-energy seed is missing entirely | `challenge.py`, `seed_race.py` | It is not: `_LOW_ENERGY_START_FRACTION = 0.35` seeds one, and production's `start_scores` on `two|winter_typical|winter_cold` span `77.884 .. 10876.7` — the extra seeds win by landing in basins *between* the existing anchors, not by reaching one production never tries. |

## What I could not finish

* **The DHW channel's own optimality.** Every race here is on the `dhw=0` path,
  where the captured objective closure is comparable end to end. With DHW on,
  `optimize` returns a co-optimized pair whose `objective_value` covers both
  channels, so the same race needs the space race re-run inside every iteration
  of the DHW decomposition. Affordable, not done inside this budget.
  `two|winter_moderate|winter_cold`'s DHW-on sibling is the first cell to run.
* **The closed-loop (rolling) realisation.** The step-0 test above shows the gap
  is not masked on 46 % of the gap cells, but a full receding-horizon day
  (`tests/rolling.py:run_rolling`) was not run: the box sat at `load1` 6-21 for
  the whole session. The open-loop step-0 number is final; the day-cost number
  is not taken.
* **The restart keep gate** (`_LBFGSB_RESTART_KEEP_REL = 2e-5`). It is
  *relative* to the whole objective, and on a cell whose objective is dominated
  by the comfort penalty (`summer_warm`: 6435.6) the absolute threshold it
  implies is 0.129 — a plausible second mechanism. No number was executed for
  it; a sweep of `_LBFGSB_RESTART_KEEP_REL` 2e-5 -> 0.0 over the same grid is
  the clean instrument and was not run.
* **Horizons 6/24/48 h and the coordinator's own captures** came after the
  seeding race in my ordering and did not get run.

## Harnesses

All under `tools/audit/round6/D0/`, each carrying its metric definition, exact
command, baseline SHA and the machine in its header, each pinning the BLAS
thread count before importing numpy, each printing `RESULT` lines plus
`thread_factor`, `load1` and `swapins`.

| file | what it does |
|---|---|
| `seed_race.py` | **D0-01's harness.** 80-cell grid; the perturbation, its inverse arm and the null control, all through `_multi_start_minimize`. `CELLS=DEEP` for the widest 16. |
| `discard.py` | **D0-02's harness.** The coordinator's warm start, the five candidates, and what the pre-refinement cut drops. `CELLS=SPACE`. |
| `challenge.py` | Exploratory capture-and-race: 34 structured L-BFGS-B starts plus a large-budget polish of production's own point; separates `race_gap_rel` from `polish_gap_rel`. `CELLS=ALL`. |
| `coopt.py` | The DHW<->space pass count, over the same seam. `CELLS=FIRE K=5`. |
| `diag_coopt.py`, `diag_coopt2.py` | How often `_co_optimize`'s guard fires and what it does. |
| `summarize.py` | Reads `challenge_out.json` for the money / flat-control / leave-one-out table. |
| `recon.py` | What one production solve asks the seam to do (calls, candidate counts, start scores). |

**Reproduction check.** `seed_race.py` was re-run in `CELLS=DEEP` after the
harness-contract tail was added, and every cell reproduced bit-for-bit
(`gap_seeds8_all` median 0.2671 %, max 11.1729 %, `two|winter_moderate|winter_cold`
0.3235 %, `one|shoulder|winter_cold` 0.6853 %) — the 80-cell grid above and the
re-run share the same code path, the patch having touched only the printout.

Raw outputs: `seed_race_GRID.log` and `seed_race_out.json` (the 80-cell
finding run), `discard_SPACE.log` and `discard_out.json`, `challenge_ALL.log`
(the 80-cell exploratory run — `challenge_out.json` holds only the last
4-cell smoke run), `coopt_out.json`.

`challenge.py`'s 80-cell run, for the record: `n_cells_race_strictly_better=47`
and `n_cells_polish_strictly_better=26` of 64 heating cells, flat-price median
0.0213 % against non-flat 0.0814 % — the same shape as `seed_race.py`'s, from an
independently written challenger set (34 L-BFGS-B starts plus a large-budget
polish of production's own point) that never touches `_MULTI_START_SOLVES`.

## Exposure

* No `gh`, no GitHub, no `docs/audit-*.md`, no `docs/backlog.md`, no
  `tools/audit/round3|4|5` — none were opened; the worktree contains none.
* Production files were **not** mutated. Every perturbation is applied in
  process through `unittest.mock.patch.object` on a named production symbol, or
  to a module-level constant (`optimizer._MULTI_START_SOLVES`) restored in a
  `finally`. `git status` on the worktree is clean apart from this directory.
* `tests/profiles.py` (the price/weather grid) and `tests/optimality.py` (the
  capture idiom) were read; neither was modified.
* Wall/CPU numbers are `provisional: true` — the box was shared all session.
  Counts, objective values and ratios are final.
