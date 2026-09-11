# D0 panel — verifier 3 of 3

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, the same standalone export
the finder used. 8-core Apple M1, python 3.11.5, numpy 2.4.6, scipy 1.17.1,
OpenBLAS, all five thread variables pinned to `"1"` before the numpy import
(inherited from `d0lib.py`, which every harness of mine imports first).

**No production or test file was touched.** Every hook is `unittest.mock`.
Verified by byte comparison against the worktree at
`/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/12-dimension-repo-audit-9e1d6b`
after all runs: `compared=192 differing=0` over every `.py`, `.mjs`, `.json`,
`.sh`, `.md` and `.txt` under `custom_components/` and `tests/`. My instruments
are all new files under `tools/audit/round3/D0/verify-3/`, raw output under
`tools/audit/round3/D0/verify-3/out/`.

**Contention.** `load1` ranged 7.23 to 47.79 across my runs and `thread_factor`
stayed in 0.895–1.000 in every one, so no BLAS thread leaked. Every number in
this report is an objective value, a SEK figure computed from a plan, a call
count or a ratio of call counts. **There is no wall-clock, CPU or RSS number
here**, so nothing is provisional and no re-take on a quiet box is owed.

## Votes

| finding | vote | severity | `stop_rule_class` | my number |
|---|---|---|---|---|
| **D0-01** | `weaken` | `low` (finder: `medium`) | `hygiene` | `fair_gap_mean_pct = 0.0241`, **0.0004 %** dropping the most favourable cell — what the extra starting points are worth once production's own starts get the same solver budget; they recover **83.11 %** of the gap at **less** simulation work |
| **D0-02** | `weaken` | `low` (finder: `low`) | `hygiene` | `polish_null_flat 0.0273 / structured 0.0431` = **1.6x** at the shipped comfort band, against the claimed **10x** at the rig's band; the gap itself reproduces exactly at 1.1703 % / 9 of 32 |

Both numbers are executed and both harnesses reproduce bit-exactly. The three
attacks that produced them are §2 (budget fairness), §4 (a 30-cell grid sharing
no tariff, weather or pump with the finder's) and §6 (the shipped comfort band).

---

## 1. Re-running the two harnesses from their headers

| harness | command | my number | finder's | `load1` | `thread_factor` |
|---|---|---|---|---|---|
| `seed_race.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/seed_race.py` | `gap_max_pct=1.0430` `cells_with_gap=15` `gap_mean_two_zone_pct=0.1465` `gap_mean_single_zone_pct=0.1411` `null_flat_gap_mean_pct=0.1570` `null_structured_gap_mean_pct=0.1419` `comfort_regressions=0` `step0_differs_where_gap=12/15` | identical | 7.23 | 0.919 |
| `polish_race.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/polish_race.py` | `gap_max_pct=1.1703` `cells_with_gap=9` `gap_mean_pct=0.0462` `null_flat_gap_mean_pct=0.0051` `gap_mean_structured_pct=0.0521` `loo_mean_drop_best_pct=0.0100` `comfort_regressions=0` `step0_differs_where_gap=2/9` | identical | 9.93 | 0.999 |

Both reproduce to the last printed digit. Contention did not move a figure, as
two seats before me found.

`seed_race.py`'s `EXPECTED` header is wrong on **four of its four** headline
numbers, not three: `gap_max_pct` 0.5618 ±0.02 against 1.0430,
`cells_with_gap` 8 ±1 against 15, `gap_mean_two_zone_pct` 0.2107 ±0.02 against
0.1465, `gap_mean_single_zone_pct` 0.0000 ±0.0005 against 0.1411. Every one is
outside its own stated tolerance. `polish_race.py`'s header, by contrast,
matches its run exactly on all eight numbers. The instrument defect is filed
and is not a reason to discard `seed_race.py`; it is a reason to read D0-01's
prose, which was written against those stale figures, with care.

---

## 2. My own measurement and metric definition

**The question two seats have not closed: is the comparison fair?** D0-01's
challenger is a *strict superset* of production's starts with
`_MULTI_START_SOLVES` lifted so every candidate is refined. That arm cannot
lose — but it also is not the same search at the same price. I measured what
each arm spends and then gave production's own starts the same money.

`tools/audit/round3/D0/verify-3/budget_fairness.py`, four arms per cell over
the finder's own 32-cell grid, identical objective closure, bounds, `args`,
`maxiter`, `ftol`, `eps`, `fd_eps` and jac path in all four:

- **P** production.
- **S** the finder's D0-01 arm (production's four starts + five constant-power
  starts, every scored candidate refined).
- **E** the same nine starts but `_MULTI_START_SOLVES` capped at the number of
  candidates production itself passed, so E performs **exactly** production's
  refinement count, call for call. This is the deployable shape of D0-01:
  change which starts get refined, spend nothing more.
- **B** **production's own starts only**, given at least S's refinement budget:
  every production candidate refined, then each refined point restarted from
  itself until it stops descending (max two), then the best point restarted
  again (max twice). **No new starting point is introduced anywhere** — every
  restart begins where production's own search already arrived.

Budget is metered as `_scoped_minimize` calls (refinements), summed scipy
`nfev`/`nit`, scalar `ThermalModel.simulate_trajectory` calls, and
`simulate_trajectory_batch` **rows** — one row is one 96-step trajectory and
the batched gradient is where essentially all solver CPU goes on this target.

### My metric definition (one line)

> `fair_gap_pct` = (B objective − S objective)/|B objective| × 100 — the
> objective that D0-01's extra *starting points* find and production's own
> starting points cannot find at equal-or-greater solver budget.

The finder's definition is `(production − challenger)/|production|` with the
challenger given 2.4x production's budget. Mine holds the budget and varies
only the start set. They are not the same quantity and the judge should treat
them as different measurements of the same phenomenon.

### The numbers

```
RESULT superset_gap_max_pct=1.0430        RESULT superset_cells_with_gap=15
RESULT refine_ratio_S_over_P=2.4444       RESULT batchrow_ratio_S_over_P=2.4766
RESULT refine_ratio_B_over_P=2.9630       RESULT batchrow_ratio_B_over_P=1.6731
RESULT cells_B_budget_ge_S=30/32          RESULT refine_ratio_B_over_S=1.2121
RESULT fair_gap_max_pct=0.7571            RESULT fair_gap_mean_pct=0.0241
RESULT fair_cells_with_gap=10             RESULT fair_loo_mean_drop_best_pct=0.0004
RESULT prod_starts_budget_gap_max_pct=1.4023
RESULT prod_starts_budget_recovers_pct=83.11 percent_of_S
RESULT equal_refine_gap_max_pct=0.8464    RESULT equal_refine_cells_better=7
RESULT equal_refine_cells_worse=5         RESULT equal_refine_worst_regression_pct=-0.6894
RESULT equal_refine_refine_ratio_E_over_P=1.0000
RESULT equal_refine_batchrow_ratio_E_over_P=0.9503
```

**1. D0-01's arm is a 2.48x-compute comparison, not an equal-budget one.**
S spends **2.4444x** production's refinements and **2.4766x** its
batched-gradient rows.

**2. Production's own four starts, given restarts, get almost all of it.**
Arm B carries **2.9630x** production's refinements — more refinements than S in
**30 of 32 cells** — while spending **less simulation work than S** (1.6731x
against 2.4766x; B's batch rows exceed S's in only 2 of 32 cells). It recovers
**83.11 %** of S's total gap, its own max gap is **1.4023 %** — *larger* than
S's 1.0430 % — and it reaches an objective at least as good as S in **22 of 32
cells**.

**3. What is left over for start selection is one cell.** `fair_gap` mean
**0.0241 %**, and with the single most favourable cell dropped **0.0004 %**.
The finder applies leave-one-out to its own aggregate and reports it honestly;
applied to the fair comparison it annihilates it. Nine of 32 cells have
`fair_gap < 0`: production's own starts beat the superset outright.
`fair_gap_mean_flat_pct = −0.0553` against `fair_gap_mean_structured_pct =
+0.0354` — at flat prices the superset arm is on average *worse* than
production's own starts at comparable budget.

**4. The finder tested the wrong budget axis.** D0-01's "it is not the budget"
rests on `arm_maxiter_x10_max_pct=0.0000`. That is sound about *iterations per
refinement* — `budget_slack.py`'s `max_nit=47` against `maxiter` 200/300 makes
`maxiter` non-binding by construction, so an arm that raises it can only return
zero. The budget that binds is the **number of L-BFGS-B runs**, and that axis
was never given a production-starts-only arm. When it is, it is worth 83 % of
the gap.

**5. The extra refinements, not the extra seeds, carry most cells.** Of the 15
cells with an S gap, **8 have `gap_E ≤ 1e-4`** — nine starting points refined
four at a time recover nothing at all, because production's own starts win the
pre-refinement score and the constant-power seeds are discarded before they are
refined. Arm E recovers **42.53 %** of S's total gap; arm B recovers 76.80 % of
it over the same 15 cells. The finder's `D0_NO_EXTRA_SEEDS=1` perturbation shows
the lift contributes nothing *when there are only four candidates*, which is
tautological; with nine candidates present the lift is load-bearing and my E arm
measures exactly how much.

**My harness's own perturbation, executed.**
`D0V3_NO_EXTRA_SEEDS=1 D0V3_MAXCELLS=8` →
`superset_gap_max_pct=0.0000`, `equal_refine_gap_max_pct=0.0000`,
`equal_refine_worst_regression_pct=0.0000`,
`refine_ratio_S_over_P=1.0000`, `batchrow_ratio_S_over_P=1.0000`,
`equal_refine_batchrow_ratio_E_over_P=1.0000` over all 8 cells —
S and E collapse onto production exactly, both in objective and in metered
budget, and only B (which adds restarts and no starts) still moves, at
`prod_starts_budget_gap_max_pct=0.3001`. `load1=31.16`,
`thread_factor=0.999`. The direction is as stated and the metering is sound.

---

## 3. Attack: is there a fix that pays?

`tools/audit/round3/D0/verify-3/polish_cost.py`, 16 cells (8 price profiles ×
{single, two_zone}, `winter_cold`, 24 h), cost in `simulate_trajectory_batch`
rows because that is the Raspberry-Pi-class currency:

```
RESULT polish_batchrow_ratio=1.0655   RESULT polish_batchrow_ratio_worst_cell=1.2921
RESULT polish_refine_ratio=1.2500     RESULT polish_scalar_traj_ratio=1.0779
RESULT seeds_batchrow_ratio=2.2618    RESULT seeds_batchrow_ratio_worst_cell=2.8000
RESULT seeds_refine_ratio=2.2500      RESULT seeds_scalar_traj_ratio=2.2534
RESULT polish_batchrows_per_gap_point=14941  rows_per_percent
RESULT seeds_batchrows_per_gap_point=129808  rows_per_percent
```

**D0-02's fix costs +6.55 % of the solver's simulation work** (worst cell
+29.21 %, +25 % refinements). **D0-01's fix costs +126.18 %** (worst cell
2.80x). Per point of objective recovered the restart is **8.7x cheaper**
(14,941 rows/percent against 129,808).

**The zero-cost variant of D0-01 is not a fix.** Arm E is *cheaper* than
production (`batchrow_ratio 0.9503`, refinements exactly 1.0000) and is better
in 7 cells, **worse in 5**, worst regression **−0.6894 %**. A change that makes
5 of 32 cells worse is not shippable without a per-cell guard, and the guard is
another objective evaluation.

**Actionability, stated plainly.** D0-01 as written is *not* actionable on this
target: the only arm that delivers its claimed gap costs 2.26–2.48x the solver's
simulation work on a host chosen because it has no CPU to spare, and the free
variant regresses. D0-02 as written *is* actionable, at +6.6 %, and the
generalised form of the same lever (arm B) recovers 83 % of D0-01's gap for
1.67x — still the most expensive thing on the table, but the only arm whose
mechanism is cheap at the margin.

---

## 4. Attack: does either survive a different grid?

### Pilot, rejected before it was read as evidence

`tools/audit/round3/D0/verify-3/disjoint_grid.py`: 4 weather profiles the
finder never used × {6 h, 48 h} × 4 prices. At 6 h on mild/summer weather
**12 of 16 cells have a zero predicted bill** — the objective is minimised at
zero power and there is no basin structure to miss. Its `seeds_cells_with_gap
=0/16` and `polish_cells_with_gap=0/16` are degenerate and I do not count them.
Recorded because a grid that produces zeros for the wrong reason is exactly the
kind of result a panel should not quietly drop.

### The grid I actually built

`tools/audit/round3/D0/verify-3/disjoint_grid2.py`. **Construction rule:** all
eight `tests/profiles.py` price profiles are piecewise-**constant block**
curves, which is the one property a basin-selection result could be an artefact
of, so the tariff axis is replaced with five curves defined in the harness and
absent from the tree — `ramp` (monotone 0.40→2.20, no blocks), `noisy`
(per-hour lognormal, fixed seed 20260911), `steep` (cheap:dear 0.06, steeper
than `winter_extreme`'s 0.12), `duckdeep` (−0.45 for six midday hours, 3.10
evening) and `flat` as the null-control arm carried *inside* the grid. Crossed
with the three `tests/profiles.py` weather profiles the finder never used that
still demand heat (`winter_mild`, `shoulder`, `summer_cool`; `summer_warm` is
dropped on the pilot's evidence) and two pump shapes the finder's grid never
builds (two-zone + DHW at 4.0/0.8 kW; single zone + DHW at 9.0/1.5 kW,
`window_area` 30.0). 5 × 3 × 2 = **30 cells**, zero overlap with the finder's
grid in tariff, weather or pump. Horizon held at 24 h.

```
RESULT cells=30
RESULT seeds_gap_max_pct=2.2358    RESULT seeds_cells_with_gap=12/30
RESULT seeds_cells_gap_100x_ftol=9/30   RESULT seeds_cells_gap_over_0p1pct=4/30
RESULT seeds_loo_mean_drop_best_pct=0.0593
RESULT seeds_null_flat_gap_mean_pct=0.0840  RESULT seeds_gap_mean_structured_pct=0.1438
RESULT seeds_null_flat_gap_max_pct=0.2938
RESULT seeds_step0_differs_where_gap=2/12
RESULT polish_gap_max_pct=1.4342   RESULT polish_cells_with_gap=5/30
RESULT polish_cells_gap_over_0p1pct=2/30
RESULT polish_loo_mean_drop_best_pct=0.0045
RESULT polish_null_flat_gap_mean_pct=0.0008  RESULT polish_gap_mean_structured_pct=0.0650
RESULT polish_step0_differs_where_gap=1/5
RESULT polish_comfort_regressions=1
```

**Both findings survive the grid change in kind.** D0-01's gap rate is 12/30
against 15/32 and its max is *larger* (2.2358 % against 1.0430 %). D0-02's is
5/30 against 9/32, max 1.4342 % against 1.1703 %.

**Three things change, all against the findings:**

1. **MPC masking reverses for D0-01.** `step0_differs_where_gap` is **2 of 12**
   here against 12 of 15 on the finder's grid. On this grid re-planning at the
   next tick walks the two arms onto the same trajectory in 10 of 12 gap cells,
   so the finder's "re-planning does not mask it" does not generalise off the
   grid it was measured on.
2. **The null control fails for D0-01 again, differently.** Flat mean 0.0840
   against structured 0.1438 — smaller here, where on the finder's grid flat was
   *larger* (0.1570 against 0.1419). But 4 of the 6 flat cells still carry a gap,
   up to 0.2938 %, and — see §6 — the single largest money gain in all 30 cells
   is a flat cell. A gain at flat prices is not a gain.
3. **The null control holds for D0-02 on both grids.** 0.0008 against 0.0650
   here (a factor of 81), 0.0051 against 0.0521 on the finder's (a factor of
   10). D0-02 is genuinely price-shaped; D0-01 is not, as its own finder says.

**The same cell carries both findings on both grids.** On the finder's grid
`summer_negative/single` is the max for seeds (1.0430) *and* for polish
(1.1703). On mine `duckdeep/summer_cool/1z_big_pump` is the max for seeds
(2.2358) *and* for polish (1.4342). Two findings whose extreme cell coincides
on two disjoint grids, whose mechanisms my arm B shows to be 83 % the same
lever, are one defect reported twice.

---

## 5. Attack: is the severity earned by consequence?

### 5a. The in-horizon bill is not the bill

Every money figure in D0's report — the finder's per-cell SEK/day table — and
in my own harnesses is a delta of `OptimizationResult.predicted_cost`. That
field's own docstring says it **excludes** `deferred_energy_cost`, "the cost of
restoring heat the plan left unstored at the end of the horizon … charged
against the savings so borrowed heat is not counted as a saving". A plan that
ends the horizon colder shows a cheaper in-horizon bill while owing the
difference to the next one. No D0 money figure so far has added it back.

`tools/audit/round3/D0/verify-3/deferred_check.py`, on the 11 cells the
findings are actually claimed on:

```
RESULT seeds_raw_bill_net_sek=1.327        RESULT seeds_settled_bill_net_sek=3.103
RESULT seeds_raw_cells_cheaper=8/11        RESULT seeds_settled_cells_cheaper=10/11
RESULT seeds_settled_worst_cell_sek=-0.297 RESULT seeds_deferred_shift_net_sek=-1.776
RESULT polish_raw_bill_net_sek=0.902       RESULT polish_settled_bill_net_sek=0.611
```

The two headline rows of the finder's money table both move by more than their
own size:

| cell | finder's raw SEK/day | settled SEK/day |
|---|---|---|
| `flat` two-zone — the biggest quoted gain | **+2.354** | **+0.975** |
| `winter_moderate` two-zone — "the objective improves while the bill rises" | **−3.487** | **−0.297** |

58 % of the biggest gain was heat borrowed from the next horizon; 91 % of the
biggest loss was heat *stored* for it. **The finder's money table is not the
saving in either direction**, and neither is mine. Settled, the seeds arm is
net **+3.103 SEK/day** over these 11 cells — *better* than raw, which runs for
the finding and I record it as such — of which **+0.975 is the flat-price
cell**; the 10 structured cells settle at **+2.128 SEK/day**, about 0.21
SEK/day per cell against bills of 11–112 SEK.

**This is a proxy and it is outranked.** `deferred_energy_cost` is a modelled
restoration charge, not a realised bill. The closed-loop receding-horizon
number the panel already has (net −9.71 SEK/day over 128 cells, 22 cells dearer
against 16 cheaper; 3 of 5 cells dearer under 24 h closed-loop MPC) is the
authoritative consequence measure and it points the other way. **The two
disagree, so no sign is established for D0-01's money.** That is the honest
state: not "it saves money", not "it costs money", but "the panel has two
measures of opposite sign and the closed-loop one wins".

### 5b. On the finder's own grid, the in-horizon money is one flat-price cell

From `default_band.py` at band 17 (my reproduction of the finder's grid, §6):
the seeds arm's in-horizon bill is net **+0.26 SEK/day over 32 cells**; drop
the single most favourable cell and it is **−2.09 SEK/day** — the arm becomes a
net cost; restricted to the 28 structured-price cells it is **−0.92 SEK/day**.
The +2.35 SEK that carries the whole net is the **flat** cell. On my disjoint
grid the identical shape appears: net +4.22 SEK over 30 cells, of which +3.43
is `flat/winter_mild/1z_big_pump`; the 24 structured cells total **+0.80
SEK/day**, 0.033 SEK/day per cell.

**On both grids, the single largest money gain D0-01's arm produces is at flat
prices**, where there is no arbitrage to win by construction. The brief's rule
is explicit: a gain at flat prices is not a gain.

### 5c. Threshold sensitivity, re-derived

`ftol = 1e-6` is a *relative*-improvement stopping test, i.e. 1e-4 percent —
numerically identical to the `gap > 1e-4` threshold both harnesses count at. My
own sweep over the per-cell output I produced:

| threshold | D0-01 `seed_race` | D0-02 `polish_race` | D0-01 my grid | D0-02 my grid |
|---|---|---|---|---|
| > 1e-4 % (= `ftol`) | **15/32** | **9/32** | 12/30 | 5/30 |
| > 1e-3 % (10x) | 15/32 | 4/32 | 10/30 | 4/30 |
| > 1e-2 % (100x) | 15/32 | 3/32 | 9/30 | 3/30 |
| > 0.1 % | 10/32 | **2/32** | 4/30 | 2/30 |
| > 0.5 % | 3/32 | 1/32 | 2/30 | 1/30 |

**D0-01's count is not a threshold artefact** — 15/32 is unchanged at 100x
`ftol` and 10/32 survive 0.1 %. **D0-02's is** — 9 collapses to 3 at 100x
`ftol` and to 2 above 0.1 %, and its leave-one-out mean with the best cell
dropped is 0.0100 % (0.0008 % dropping two). This is the one place the two
findings' robustness runs opposite to their severities.

---

## 6. Attack: reachability — is this configuration one a user has?

**The code path is reachable.** These harnesses call
`HeatPumpOptimizer.optimize()` directly, which is exactly what the coordinator
hands to `optimize_in_process` in a real install (`coordinator.py:924`, `:929`).
No `FakeHass`, no executor, no coroutine, so none of the stub hazards apply.

**The configuration is not.** `d0lib.build` — and therefore every D0 number the
finder, both earlier seats and I have produced up to here — constructs
`OptimizationConfig(min_temp=17.0)` and `tests/profiles.py:house()` with
`min_temperature: 17.0`. The shipped default is `const.DEFAULT_MIN_TEMP = 19.0`;
`OptimizationConfig.min_temp`'s own class default is 19.0 and `from_mapping`
falls back to `DEFAULT_MIN_TEMP`, so 19.0 is what a user has until they move the
comfort slider. The objective normalises its pull-to-target term by
`comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)`: **the rig
runs a 4-degree band where a default install runs 2**, and a wide band is
exactly the condition under which cheap bang-bang schedules become competitive
and the objective grows extra basins.

`tools/audit/round3/D0/verify-3/default_band.py` runs the finder's own 32-cell
grid at both bands, moving `house(min_temperature=...)` and
`OptimizationConfig.min_temp` together so the two halves of the seam agree.
**The band-17 run is the control and it reproduces the finder exactly** —
`seeds_cells_with_gap=15/32`, `seeds_gap_max_pct=1.0430`,
`polish_cells_with_gap=9/32`, `polish_gap_max_pct=1.1703`,
`seeds_null_flat 0.1570 / structured 0.1419`, `polish_null_flat 0.0051 /
structured 0.0521`, `step0 12/15` and `2/9` — so the band-19 arm is measuring
the same thing with one variable moved.

| | band 17.0 (the rig) | band 19.0 (**shipped default**) |
|---|---|---|
| seeds `cells_with_gap` | 15/32 | 15/32 |
| seeds `gap_max_pct` | 1.0430 | **1.1509** |
| seeds cells > 0.1 % | 10/32 | 8/32 |
| seeds mean / leave-one-out | 0.1438 / 0.1147 | 0.1013 / **0.0675** |
| seeds null: flat vs structured | 0.1570 / 0.1419 | **0.0999 / 0.1015** |
| seeds `comfort_regressions` | 0 | **1** |
| seeds in-horizon bill, 32 cells | +0.26 (10 cheaper, 5 dearer) | **−3.95 (9 cheaper, 8 dearer)** |
| seeds bill, drop most favourable | −2.09 | **−4.29** |
| seeds bill, 28 structured cells | −0.92 | **−2.56** |
| polish `cells_with_gap` | 9/32 | **14/32** |
| polish `gap_max_pct` | 1.1703 | **0.7624** |
| polish null: flat vs structured | 0.0051 / 0.0521 (**10x**) | **0.0273 / 0.0431 (1.6x)** |
| polish `comfort_regressions` | 0 | **2** |
| polish cells with a *negative* gap | 0 | **1** |

**Four things the judge should take from this.**

1. **Neither finding is fragile — but neither is located where it was found.**
   Both phenomena persist at the shipped band. What does not persist is *where*:
   6 of the 15 seeds-gap cells vanish and 6 new ones appear, 3 of the 9
   polish-gap cells vanish, and **`summer_negative/single` — the single cell
   that is the maximum for both findings at band 17 — goes to exactly 0.0000 for
   both at band 19.** Every per-cell claim in the D0 report, including its whole
   money table, is band-17-specific.
2. **D0-01's null control fails completely at the shipped band.** Flat 0.0999
   against structured 0.1015: the effect is now price-*independent* to two
   decimal places. The finder's own conclusion ("this is not price optimality")
   is confirmed and strengthened.
3. **D0-02's price-shape claim is a band-17 artefact.** Its 10x flat-versus-
   structured separation — the evidence that makes it a *price* finding at all
   under `D0.md`'s rule — collapses to **1.6x** at the band a default install
   ships with. My 30-cell disjoint grid's 81x separation is also a band-17
   measurement. At the shipped configuration D0-02 is the same
   price-independent basin phenomenon as D0-01, and its distinguishing claim
   does not survive.
4. **At the shipped band D0-01's arm makes the bill worse.** −3.95 SEK/day
   summed over 32 cells, dearer in 8 of them, −4.29 with the most favourable
   cell dropped and −2.56 over the structured-price cells alone; the worst
   single cells are `flat/single+dhw` (+1.39 SEK/day dearer),
   `winter_moderate/two_zone+dhw` (+1.18) and `winter_typical/two_zone` (+1.11)
   on bills of 87, 112 and 82 SEK. A change that lowers a synthetic objective
   and raises the electricity bill in a quarter of cells is not a saving.

Both arms also pick up comfort regressions at the shipped band that they do not
have at 17 (seeds 1, polish 2), which is the feasibility-parity gate `D0.md`
requires before any "cheaper" verdict.

---

## 7. Two instrument observations the judge should have

**7a. "`challenger_objective <= production_objective` by construction" is not
established for the quantity measured.** D0-01's report rests its "a gap cannot
be BLAS noise or a lucky arm" on the superset construction. That guarantee holds
*inside* `_multi_start_minimize`, whose return is a `min` over a superset of
starts. It does **not** hold for `OptimizationResult.objective_value`, which is
what both harnesses actually difference: `optimize()` runs further stages after
the space solve, and on DHW-enabled cells a better space plan feeds a different
hot-water re-plan. At the finder's band the guarantee holds empirically — no
negative gap in any of my 32 + 30 cells — but at the shipped comfort band it
breaks (§6), with `summer_typical/two_zone+dhw` returning `polish −0.2226 %`:
the restart arm, which can only improve the space solve, ends **worse** end to
end. I did not instrument which stage inverts it; both cells where it happens
are DHW-enabled, and the valve stage is inert here
(`mixing_valve_mode` defaults to `none`, which `tests/profiles.py:house()` never
overrides). The consequence for the judge: a positive per-cell gap is evidence,
not proof, and the finder's "cannot be a lucky arm" should be read as an
empirical observation on one grid at one comfort band.

**7b. The finder's `D0_NO_EXTRA_SEEDS=1` perturbation cannot see what it is
claimed to see.** The report says that perturbation "also proves the lift on
its own contributes nothing". With the seeds removed there are only four
candidates and `_MULTI_START_SOLVES` is four, so the lift is a no-op by
arithmetic and the arm must return zero whatever is true. The claim needs the
arm that keeps the seeds and drops the lift, which is my E arm: it recovers
**42.53 %** of S's gap against the lift-and-seeds arm's 100 %, and **8 of the
15 gap cells have `gap_E ≤ 1e-4`**. In those eight cells the extra
*refinements*, not the extra *starting points*, are the whole effect — the
constant-power seeds lose the pre-refinement score and are discarded before any
solver touches them.

---

## 8. Verdicts

### D0-01 — `weaken`, severity `low`, `stop_rule_class: hygiene`

**Reproduced exactly** (`gap_max_pct=1.0430`, `cells_with_gap=15`). The
perturbation works. The harness is not void and the objective-value fact is
true: production's returned plan is not a local optimum in 15 of 32 cells.

**What my number changes is the mechanism and the size.** The claim is that
*the shipped candidate set under-covers the basins*. Measured against
production's own starting points at equal-or-greater solver budget, the
start set is worth `fair_gap_mean_pct = 0.0241 %`, and **0.0004 % with the
single most favourable cell dropped** — the finder's own leave-one-out
standard, applied to the fair comparison, leaves nothing. Production's four
starts, restarted from their own answers, recover **83.11 %** of the gap while
spending **less** simulation work than the superset arm (1.67x against 2.48x)
and reaching an objective at least as good in **22 of 32 cells**. The gap is
not a seeding result; it is a stopping-rule result, which is D0-02.

**Severity `medium` is not earned by consequence.** Four measures, and the only
one that is positive is the one taken at a comfort band no default install has:

- the in-horizon bill on the finder's own grid at its own band: +0.26 SEK/day
  over 32 cells, **−2.09 with the most favourable cell dropped**, **−0.92 over
  the 28 structured cells**, and the +2.35 that carries the whole net is the
  **flat-price** cell;
- the same bill at the **shipped comfort band**: **−3.95 SEK/day** over 32
  cells, dearer in 8, **−4.29** dropping the best cell, **−2.56** over the
  structured cells (§6);
- the borrowed heat added back, on the 11 claimed cells: +3.10 SEK/day, of which
  +0.975 is again the flat cell — better than raw, and I record that it runs for
  the finding (§5a);
- the panel's closed-loop receding-horizon measure, which outranks all three:
  **−9.71 SEK/day over 128 cells, 22 dearer against 16 cheaper.**

MPC masking, which the finder measures at 12/15 on its own grid, is **2/12** on
a grid it did not build. And at the shipped band the arm picks up a comfort
regression it does not have at 17.

**Not actionable as written.** The only arm that delivers the claimed gap costs
**+126.18 %** of the solver's batched-gradient rows (worst cell 2.80x) on a
Raspberry-Pi-class target; the free reallocation (arm E, refinements exactly
1.0000x, rows 0.9503x) is better in 7 cells and **worse in 5**, worst
regression −0.6894 %. An unfixable finding is still a finding, and the issue
must say so.

**`hygiene`, not `bug`.** Nothing production returns breaches comfort, hot-water
feasibility, a power bound or a pin; the residual is ≤1 % of a synthetic
objective in a minority of cells, and the realised bill does not move in the
user's favour.

**What the register should carry instead of the title as written:** *the solver
stops at a point from which the same solver can descend further; the extra
starting points are 0.0004 % of it once budget is held equal.* That is D0-02's
sentence, which is the point.

### D0-02 — `weaken`, severity `low`, `stop_rule_class: hygiene`

**Reproduced exactly** on all eight header numbers (`gap_max_pct=1.1703`,
`cells_with_gap=9`, `gap_mean_pct=0.0462`, `null_flat_gap_mean_pct=0.0051`,
`gap_mean_structured_pct=0.0521`, `loo_mean_drop_best_pct=0.0100`,
`comfort_regressions=0`, `step0_differs_where_gap=2/9`), and its `EXPECTED`
header — unlike D0-01's — is accurate. Survives a 30-cell grid that shares no
tariff, weather or pump with the finder's: 5/30, max 1.4342 %.

**Its null control holds at the band it was measured at, and only there.**
Flat 0.0051 against structured 0.0521 on the finder's grid, flat 0.0008 against
structured 0.0650 on my 30-cell disjoint grid — a factor of 81. Both are
`min_temp=17.0` measurements. At the shipped default band the separation is
**0.0273 against 0.0431, a factor of 1.6** (§6). The claim's qualifier —
*price-shaped (flat 10x smaller)* — is what makes this a price-optimality
finding at all under `D0.md`'s rule, and it is a 4-degree-comfort-band artefact.
**This is why the vote is `weaken` and not `verify`**: the number reproduces,
the severity is right, but what the finding establishes is smaller than what it
claims. At a default install it is the same price-independent basin phenomenon
as D0-01.

**It is the only actionable one.** +6.55 % batched-gradient rows on average
(+29 % worst cell, +25 % refinements) against D0-01's +126 %, and **8.7x
cheaper per point of objective recovered** (14,941 rows/percent against
129,808). Its generalised form — restart from every refined point, not only the
best — recovers 83 % of D0-01's gap as well.

**Severity stays `low` and is earned; it is the claim, not the severity, that I
am reducing.** `9 of 32` is a threshold artefact:
`ftol=1e-6` *is* a relative test of 1e-4 percent, the same number the harness
counts at, and above 0.1 % it is **2 of 32** (2 of 30 on my grid). Leave-one-out
with the best cell dropped is 0.0100 % (0.0008 % dropping two). Its in-horizon
bill is +0.77 SEK/day over 32 cells and **+0.09 with the best cell dropped**;
settled over the 11 claimed cells, +0.611 SEK/day. Step-0 differs in 2 of 9
cells, so re-planning washes out the rest. The finder says all of this in its
own report and I confirm every figure of it.

**Two new negatives, one trivial and one not.** On my disjoint grid the restart
arm shows `comfort_regressions=1` where the finder reports 0 — reproduced in a
polish-only re-run of the same grid. The cell is `duckdeep/shoulder/1z_big_pump`:
`above` goes 0.0300 → 0.0307 degree-steps, 0.0007 degree-steps of extra
over-temperature for a 0.0153 % objective gain. Trivial, recorded so the judge
is not surprised by the counter. The one that matters is at the shipped band:
`comfort_regressions=2` and **one cell with a negative gap**
(`summer_typical/two_zone+dhw`, −0.2226 %), where an arm that can only improve
the space solve ends worse end to end (§7a).

**`hygiene`, not `bug`**, for the same reason as D0-01.

### For the panel, not for either finding

**D0-01 and D0-02 are one defect reported twice.** The same cell is the maximum
for both arms on both grids — `summer_negative/single` on the finder's
(1.0430 / 1.1703), `duckdeep/summer_cool/1z_big_pump` on mine (2.2358 / 1.4342)
— and the restart lever recovers 83 % of the seeding lever's gap at less cost.
Filing them as two findings, one `medium` and one `low`, puts the severity on
the arm that costs 2.5x and cannot be shipped, and the `low` on the arm that
costs 6.6 % and can.

---

## 9. Read last: where my metric differs from seat 1's

Opened only after every number above was executed, per `verifier.md`.

**Seat 2's report is not at the path I was given.**
`.../scratchpad/audit-r3/archive/D0/` contains `finder/`, `verify-1/` and
`verify-1.md` and no `verify-2.md`. I cannot say where my definition differs
from seat 2's because I have not seen it, and I did not go looking elsewhere.

**Seat 1's metric** is the **realised daily bill delta**,
`bill = Σ_t price_t · (space_power_t + dhw_power_t) · Δt` computed from each
arm's returned schedules, plus the objective as an **absolute** delta in
objective units; its fairness check is that both arms are re-scored under **one
captured production objective closure** (`closure_mismatch_max=0.000e+00` over
128 cells). **Mine** is `fair_gap_pct`, an objective ratio with the **solver
budget held**, metered in refinements and batched-gradient rows.

These answer two different fairness questions and the judge should not merge
them. Seat 1 closed *"are the two arms priced by the same function?"* — yes,
exactly. I closed *"are the two arms given the same amount of solver?"* — no,
2.48x, and when they are, the start set is worth 0.0004 % after leave-one-out.
Seat 1 states the adjacent fact — "D0-01's one-sidedness is real but comes from
the lift, not from the seeds" — but does not build the arm that hands
production's own starting points the extra budget, which is what produces my
number.

**Two arms that are nearly the same, and one caution.** Seat 1's arm C and my
arm E are the same idea: the five constant starts with `_MULTI_START_SOLVES`
left at 4 so the pre-score prunes. Independently implemented, they agree on
`obj_gap_min_pct = −0.6894 %`, `obj_gap_max_pct = +0.8464 %` and **5 cells made
worse**. They differ in two places, both explained: seat 1 measures ×1.1556
refinements where I measure **×1.0000**, because on the co-optimisation call
production passes a *single* warm-start candidate and a 6-candidate list still
refines 4 unless the cap is lowered per call, which my arm does; and improved
cells are 8 for seat 1 against 7 for me, from the same extra refinements.

**The caution:** seat 1's "recovers 81 % of the headline gap" is a ratio of
*maxima* (0.8464/1.0430) for arm C. My "recovers 83.11 %" is a ratio of *summed
gaps over 32 cells* for arm B — a different arm and a different statistic. The
two numbers are close by coincidence and must not be quoted as agreeing.

**One corroboration and one boundary for §7a.** Seat 1 tested the "strict
superset implies a one-sided bound" claim rather than accepting it and got
`negative_gap_cells=0` for arm S over **128 cells** — all of them at
`min_temp=17.0`. That is exactly the empirical holding I report, on four times
my cell count, and it is the right result at that band. My §7a adds only that
the guarantee is empirical rather than structural: move to the shipped comfort
band and it breaks in one cell (`summer_typical/two_zone+dhw`, polish −0.2226 %).

**Where we converge independently.** Seat 1 refutes D0-02's price-shape claim by
dropping its two carrying cells (flat-over-structured 0.098 → 36.193); I refute
it by moving the comfort band to the shipped default (10x → 1.6x). Two
unrelated perturbations, same conclusion: D0-02 is not price-shaped, and belongs
in the same basin/stopping-rule family as D0-01. That is now three independent
routes to "these are one defect".

---

## Appendix — my instruments, their commands and their environment

All under `tools/audit/round3/D0/verify-3/`, raw output under `.../verify-3/out/`.
Each carries its metric definition, its command and its perturbation in its own
header. None of them edits a production or test file; every hook is
`unittest.mock`.

| file | what it measures | output |
|---|---|---|
| `budget_fairness.py` | the four arms P / S / E / B and the budget each spends; **my own metric** | `out/budget_fairness.txt`, `out/budget_fairness_PERT.txt` |
| `polish_cost.py` | what each proposed fix costs in `simulate_trajectory_batch` rows | `out/polish_cost.txt` |
| `disjoint_grid2.py` | both arms on 30 cells built from five tariffs that are not in the tree | `out/grid2.txt`, `out/grid2_polish_comfort.txt` |
| `disjoint_grid.py` | the rejected 6 h/48 h pilot, kept because its zeros are degenerate | `out/grid_h6.txt` |
| `default_band.py` | both arms at the rig's comfort band and at the shipped default | `out/band17.txt`, `out/band19.txt` |
| `deferred_check.py` | the bill once `deferred_energy_cost` is added back | `out/deferred.txt` |

| run | `thread_factor` | `load1` |
|---|---|---|
| `seed_race.py` (finder's) | 0.919 | 7.23 |
| `polish_race.py` (finder's) | 0.999 | 9.93 |
| `budget_fairness.py` | 0.934 | 23.52 |
| `budget_fairness.py` perturbation | 0.999 | 31.16 |
| `disjoint_grid.py` pilot | 1.000 | 10.16 |
| `disjoint_grid2.py` | 0.995 | 33.09 |
| `polish_cost.py` | 0.992 | 36.56 |
| `default_band.py` band 17 | 0.998 | 35.40 |
| `default_band.py` band 19 | 0.964 | 29.21 |
| `deferred_check.py` | 0.999 | 47.79 |
| `disjoint_grid2.py` polish-only re-run | 0.895 | 24.73 |

`thread_factor` never left 0.895–1.000, so no run leaked a BLAS thread.
`load1` was high because I ran several harnesses concurrently; every figure in
this report is an objective value, a SEK figure computed from a plan, a call
count or a ratio of call counts, so none of them is a timing number and none is
provisional.

**Tree integrity.** Byte-compared after every run against the worktree at
`/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/12-dimension-repo-audit-9e1d6b`:
192 files under `custom_components/` and `tests/` compared, **0 differing**.

**What I did not run.** The closed-loop receding-horizon arm (`mpc_realised.py`
and the panel's 5-cell MPC) — the panel already has it and it is the measure
that outranks my §5a proxy; a global outer bound (differential evolution or a
coarsened dynamic program), so none of my numbers says how far from optimal the
plan is, only that it is not optimal; the valve-storage and wood topologies,
manual pins and power caps, and `_repair_throttled_buffer_caps`, which is the
one default path where `_MULTI_START_SOLVES` could genuinely truncate; and the
horizon axis, after the pilot showed a short horizon on mild weather is
degenerate here.
---
