# D0 — Price optimality, audit round 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Export with no `.git`, no
`docs/audit-*.md`, no `docs/backlog.md`, no `RELEASE_NOTES.md`. 8-core Apple M1,
python 3.11.5, numpy 2.4.6, scipy 1.17.1, OpenBLAS, all five thread variables
pinned to `"1"` before the numpy import in every harness.

`load1` during the fan-out ranged 35–51 with 15–24 concurrent python processes.
**No number in this report is a wall-clock, CPU or RSS number**, so nothing here
is provisional: every figure is an objective value, a SEK cost computed from a
plan, a call count or an iteration count. `tests/stress.py` was not run, no full
`tests/run.sh` was run, and the gate lock was neither taken nor stolen.

## Question and method

Not "is the objective the right objective" (D2's question) but "does the solver
minimise the one it has". Every comparison is therefore on
`OptimizationResult.objective_value` — the production objective closure
evaluated at the plan each arm returned — never on energy price alone.

The rig is `d0lib.py`:

1. **Capture.** `mock.patch.object(optimizer_module, "_multi_start_minimize", …)`
   — the `tests/optimality.py` idiom — recording every call's objective,
   candidates, bounds, args, `maxiter`, `batch_objective`, `fd_eps` and result,
   plus `nit`, `nfev`, `status`, `message`, and whether the batched jac served
   the call.
2. **Challenge by strict superset.** Every challenger *is* the production
   `_multi_start_minimize`, called on the identical closure, bounds, `args`,
   `maxiter`, `ftol`, `eps` and `fd_eps`, with a **superset** of the starting
   points production passed and `_MULTI_START_SOLVES` lifted so no scored
   candidate is discarded. Since `_multi_start_minimize` returns the best of the
   starts it refines, `challenger_objective <= production_objective` holds **by
   construction**: a gap cannot be BLAS noise or a lucky arm, only a point
   production's own four starts did not reach. The batched gradient therefore
   serves exactly the bound shapes it serves in production — no part of the
   `jac` path is re-derived.
3. **Feasibility parity.** Every "cheaper" verdict carries both arms' per-step
   comfort floor and ceiling (degree-steps below 17.0 °C and above 23.0 °C from
   `ThermalModel.simulate_trajectory`); the hot-water probe additionally scores
   the tank against **production's own** `requirement` / `draw_rates` /
   `max_temp` arrays, captured from `_plan_dhw_cheapest_first`.

**No production or test file was edited.** Every hook is `unittest.mock`, so
there is nothing to restore; the export is byte-identical to the baseline apart
from the new files under `tools/audit/round3/D0/`.

Grid: the 8 `tests/profiles.py` price profiles × 4 topologies (single /
two-zone × DHW off / on) at `winter_cold` — 32 cells — plus 8-cell probes for
the hot-water planner, the co-optimisation gate and the arm attribution.

---

## Findings

### D0-01 — the shipped candidate set under-covers the basins: 15 of 32 cells improve on the production objective under a strict superset of the same search (medium)

`_optimize_space_only` seeds `_multi_start_minimize` with exactly four points
(the smooth price-weighted guess; `_price_ranked_start` at the baseline energy;
the baseline power profile; `_price_ranked_start` at
`_LOW_ENERGY_START_FRACTION = 0.35` of it), and `_solve_space` seeds four of the
same shape. `_MULTI_START_SOLVES = 4` refines all of them — nothing is
discarded (`budget_slack.py`: `candidates_discarded_max=0`). The set is
nevertheless too narrow.

Adding five constant-power starts (`lo + f·(hi−lo)`, f ∈ {0, ¼, ½, ¾, 1}) and
changing nothing else:

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/seed_race.py
RESULT cells=32                     RESULT gap_max_pct=1.0430
RESULT cells_with_gap=15            RESULT gap_mean_pct=0.1438
RESULT comfort_regressions=0        RESULT step0_differs_where_gap=12/15
```

A second, independent seed family says the same thing: handing
`_price_ranked_start` the whole bang-bang **ladder** (energy fractions
0.2 … 1.5) instead of the two rungs production samples (1.0 and 0.35) gives
`gap_max_pct=1.1087` over `cells_with_gap=13`, `comfort_regressions=0`
(`price_seed_race.py`). Two different families, one mechanism.

**It is not the budget.** `arms_decomposition.py` separates the three changes:
`arm_maxiter_x10_max_pct=0.0000` — a ten-fold iteration budget recovers nothing
in any of eight cells — against `arm_extra_seeds_max_pct=1.0430`.
`budget_slack.py` shows why: over 39 production solver calls the winning start's
`nit` never exceeds 47 against a `maxiter` of 200/300
(`max_nit_over_maxiter=0.2350`), `calls_hitting_maxiter=0`, and every call ends
`status=0, CONVERGENCE`.

**Null control, and it renames the finding.** The same race at
`profiles.prices("flat")` does not shrink — it grows:
`null_flat_gap_mean_pct=0.1570` against `null_structured_gap_mean_pct=0.1419`,
and the biggest two-zone gap in the whole grid, 0.5618 %, *is* the flat cell.
The ladder harness agrees more strongly still (`null_flat_gap_mean_pct=0.3187`
vs `gap_mean_structured_pct=0.1616`). **So this is not price optimality.** It is
basin selection in a non-convex objective — the one-sided comfort penalty plus
the terminal credit — and it is there whatever the price curve does. Filing it
as a price-arbitrage gap would be exactly the error that killed five earlier
measurement designs on this project.

**Money, and its honest shape.** Because the objective prices comfort as well as
energy, a plan with a lower objective can carry a *higher* electricity bill. Of
the 15 gap cells the bill falls in 10 and rises in 5. Reported per cell, never
averaged:

| cell | objective gap | bill change | as % of that day's bill |
|---|---|---|---|
| `winter_moderate` two-zone (ladder arm) | +0.1373 % | −4.413 SEK/day | 5.4 % of 81.36 SEK |
| `shoulder` single (ladder arm) | +0.8145 % | −1.898 SEK/day | 4.7 % of 40.09 SEK |
| `flat` two-zone (seed arm) | +0.5618 % | −2.354 SEK/day | 2.6 % of 90.75 SEK — **null-control cell** |
| `summer_negative` single (seed arm) | +1.0430 % | −0.797 SEK/day | 7.0 % of 11.34 SEK — a small day, quoted as required |
| `winter_moderate` two-zone (seed arm) | +0.0326 % | **+3.487 SEK/day** | the objective improves while the bill rises |

**MPC masking.** The step-0 action differs in 12 of the 15 gap cells (9 of 13 in
the ladder arm), so re-planning at the next tick does not walk the two arms onto
the same trajectory in the large majority of them.

**Leave-one-out.** Two-zone arm: 16 cells, range 0.0000–0.5618 %, mean
0.1465 %, mean with the single most favourable cell dropped 0.1188 %. Ladder
arm, structured prices: 28 cells, range 0.0000–1.1087 %, drop-most-favourable
mean 0.1265 %. The aggregate is not one row carrying the grid.

**Perturbation, executed.** `D0_NO_EXTRA_SEEDS=1` removes the extra starting
points and keeps everything else, including the `_MULTI_START_SOLVES` lift:
all 32 cells go to exactly 0.0000 % (`gap_max_pct=0.0000`). That also proves the
lift on its own contributes nothing — the seeds are the whole effect.

### D0-02 — the solver stops short of its own basin's floor: restarting L-BFGS-B from the point it just returned descends further in 9 of 32 cells, by up to 1.17 % (low)

The challenger here adds **no new starting point and no extra budget**. It runs
production's `_multi_start_minimize` exactly as production does, then calls it
again from the winning point itself, same closure, same bounds, same `maxiter`,
same `ftol=1e-6`, same `eps`, same batched jac. All that changes is that
L-BFGS-B gets a fresh limited-memory history at the point it had already stopped
at.

```
PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/polish_race.py
RESULT cells=32                     RESULT gap_max_pct=1.1703
RESULT cells_with_gap=9             RESULT gap_mean_pct=0.0462
RESULT comfort_regressions=0        RESULT step0_differs_where_gap=2/9
```

The 1.1703 % is `summer_negative`, single zone, DHW off (0.679 SEK/day of an
11.34 SEK day). The next largest is `winter_moderate` two-zone at 0.200 SEK/day
of an 81.36 SEK day; the remaining seven move by under 0.02 SEK/day.
`arms_decomposition.py` agrees on the same cell (`arm_polish_max_pct=1.1703`)
and shows the discriminating fact: `arm_maxiter_x10_max_pct=0.0000` — a ten-fold
budget recovers nothing in that cell. So this is a *stopping-rule* result rather
than a budget one: the solver has iterations left and stops anyway, on the
`ftol` / projected-gradient test, at a point from which the same solver can
still descend.

**Null control, and here it points the other way from D0-01.**
`null_flat_gap_mean_pct=0.0051` against `gap_mean_structured_pct=0.0521` — a
factor of ten. Unlike D0-01, this effect *is* price-shaped: it largely vanishes
on a flat curve. That is what a price-optimality defect is supposed to look
like; it is simply a small one.

**Leave-one-out, and the honest reading.** 32 cells, range 0.0000–1.1703 %, mean
0.0462 %, mean with the most favourable cell dropped 0.0100 %. **The aggregate
is carried by one cell**, so the max is the number to read and the mean is not.
That, plus `step0_differs_where_gap=2/9` — re-planning would wash out seven of
the nine — is why this is `low` and not `medium`.

**Perturbation, stated for the judge:** `D0_NO_POLISH=1` drops the restart, so
the challenger becomes production and every cell must collapse to 0.0000 %.
`D0_ARMS_SEEDS_OFF=1` on `arms_decomposition.py` leaves `arm_polish_max_pct`
untouched, since the restart arm carries no seeds.

---

## Non-findings (what was checked and held, with the command and the number)

| what was checked | command | number |
|---|---|---|
| the iteration budget is never the binding constraint | `budget_slack.py` | `calls_hitting_maxiter=0` over 39 solver calls; `max_nit=47`, `max_nit_over_maxiter=0.2350`, `status_histogram={0: 39}` |
| `_MULTI_START_SOLVES` discards no candidate on any default path | `budget_slack.py` | `candidates_discarded_max=0`, `multi_start_solves=4` |
| the batched gradient serves every solve in the grid | `budget_slack.py` | `calls_on_batched_jac=39` of 39 |
| a bigger budget recovers nothing anywhere | `arms_decomposition.py` | `arm_maxiter_x10_max_pct=0.0000` over 8 cells |
| iterating the DHW ↔ space decomposition past production's single pass changes nothing | `arms_decomposition.py` | `coopt_fixpoint_max_pct=0.0000`, `coopt_extra_passes_adopted=0` |
| the guard that can skip the hot-water re-plan costs nothing, and in fact never fires on this grid | `coopt_gate.py` | `coopt_gate_gap_max_pct=0.0000`, `gate_skipped=0/8`, `forced_adoptions=0` |
| the hot-water LP + repair chain is within ~1 % of a local-search optimum on its own feasibility contract, and the gap does not generalise | `dhw_relocate.py` | `dhw_cost_gap_max_pct=0.9204` in **1** of 8 cells (0.195 SEK/day of a 30.75 SEK bill), `loo_structured_mean_drop_best_pct=0.0000`, `null_flat_dhw_gap_pct=0.0000`, `dhw_shortfall_regressions` limited to the cells the identity control excludes |
| forcing a hot-water schedule back through the pipeline is a faithful replacement — and where it is not, the cell is excluded | `dhw_relocate.py` identity control | 6 of 8 cells `0.000000 %`; 2 cells non-zero (`summer_negative` 0.3145 %, `shoulder` 0.4269 %) and therefore excluded from every claim |
| the strict-superset construction, not the harness, produces D0-01's gap | `D0_NO_EXTRA_SEEDS=1 … seed_race.py` | every one of 32 cells `0.0000 %` |
| no challenger anywhere bought its improvement by breaching comfort | `seed_race.py`, `price_seed_race.py` | `comfort_regressions=0` in both, 64 cell-comparisons |

The hot-water relocation result is deliberately **not** filed as a finding: it
survives in one cell of eight and its leave-one-out mean with that cell dropped
is 0.0000 %, which is the "referendum on row counts" the brief warns against.

## Harnesses

All under `tools/audit/round3/D0/`, each runnable by the single command in its
own header, each printing `RESULT` lines plus `thread_factor`, `load1`,
`swapins` and the concurrent-python count.

| file | what it measures |
|---|---|
| `d0lib.py` | the rig: thread pin, scenario builder over `tests/profiles.py`, the capture idiom, the superset challengers, comfort and tank feasibility. Not a harness — no `RESULT` lines of its own. |
| `seed_race.py` | D0-01's primary number, 32 cells, with the null control, leave-one-out, comfort parity and the step-0 (MPC-masking) count |
| `price_seed_race.py` | D0-01's second seed family, the `_price_ranked_start` ladder, same 32 cells |
| `arms_decomposition.py` | which of budget / restart / seeding recovers the gap, plus the DHW↔space fixed point |
| `polish_race.py` | D0-02's primary number: the restart arm alone over the full 32-cell grid, with its own null control and leave-one-out |
| `budget_slack.py` | iteration budget, discarded candidates, jac path, termination reasons |
| `dhw_relocate.py` | hot-water block relocation against production's own feasibility arrays, with an identity control |
| `coopt_gate.py` | whether the guard that skips the hot-water re-plan costs anything |
| `mpc_realised.py` | receding-horizon control (committed; stopped to free the box, see below) |

## What I could not finish

- `mpc_realised.py`, the closed-loop realisation of D0-01's gap, is committed
  and runnable but was stopped to free the box when it reached `load1` 51 with
  24 concurrent python processes; it produced no number. The cheap MPC-masking
  test — does the step-0 action differ — is inside `seed_race.py` and answered
  12/15 there and 2/9 in `polish_race.py`.
- Not swept: horizons other than 24 h, the valve-storage and wood topologies,
  manual pins and power caps, and the coordinator captures from
  `tests/golden.py:coordinator_scenarios()`. `_repair_throttled_buffer_caps` is
  the one default path where `_MULTI_START_SOLVES` could actually truncate (it
  prepends two `_cap_tighten_starts` seeds to a list of four) and it needs a
  `power_caps` configuration this grid never builds; the code already runs both
  arms there and keeps the better, so it is a place to check rather than a
  suspicion.
- No global outer bound (differential evolution, or a dynamic program on a
  coarsened grid) was run: at 96 variables it does not fit the fan-out budget.
  The superset construction gives a one-sided bound instead — enough to
  establish that the plan is not optimal, not enough to say how far from optimal
  it is.

## Exposure

Read `CLAUDE.md`, `tools/audit/briefs/COMMON.md`, `tools/audit/briefs/D0.md`,
`tools/audit/README.md`, `tools/audit/finding.schema.json`, the out-of-tree
`SEAT-BLOCK.md`, `custom_components/heatpump_optimizer/optimizer.py`,
`tests/optimality.py`, `tests/profiles.py` and the first 80 lines of
`tests/rolling.py`. No `gh`, no GitHub, no `docs/audit-*`. `optimizer.py`'s
comments cite earlier `D0-nn` and `D9-nn` ids; they were read as context for
what the code does, not as a to-do list.
