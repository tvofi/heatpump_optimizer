# Honest starts and contiguous runs: price a start as one start, ship runs the pump can run

Outside proposal. The design below was written before any code, against tvofi/main `fc2a7edcf2` (v7.1.11), and every line it cites is at that SHA; the build this pull request carries is recorded in the last two sections, at base `870238eb21`. The production files cited are unchanged since `14f227c5b`, where the report was taken. No finder harness: outside report. The "Spike" figures are from a throwaway script on the golden profiles: they show the shape, they are not acceptance evidence.

## Finding (Bankaifan, 2026-11-12, alpha innotec LWDV 91-1/3, Luxtronik 2.1)

Install: 600 l combi store (`dhw_combi_tank_enabled`, 504 l around a 40 l coil), `single_tank_valve`, floor heating on a slab, `space_setpoint_unit: return`, `flow_min_lift_k` 0.5, controller hysteresis 0.5 K heating and 4 K hot water, `wear_autotune_enabled` with a wear price of 0.25 per start. The metered running draw is 1.1 to 3.3 kW. The datasheet minimum of 0.53 kW is never held: under about 1 kW the compressor cycles. Day: flat prices 0.34 to 0.45 per kWh, house at 24.1 °C, band 21.5 to 25.5 °C.

| | modulation / min power / cycling cost | Plan for 24 h | Published saving | What is wrong |
|---|---|---|---|---|
| 1 | modulating / 0.53 / 10 | space at 0.13 to 0.37 kW for hours; hot water in 7 charges of 15 to 30 min, each 51 to 52 °C; about 7 kWh | -0.24 | the plan shows almost no start, the pump cycles all day |
| 2 | on_off / 1.1 / 10 | 1.1 kW nearly without a pause, 25 kWh | -6.27 | running through is cheaper than one stop |
| 3 | on_off / 1.1 / 0.25 | 16 blocks, 11 of them hot water (11.1 of 12.8 kWh) | -1.44 | the store is charged through the hot-water channel, one start per block |

No setting yields a few long runs in the cheap hours. Four causes, each read off the code:

1. **The start term prices swing, not starts.** `cycling_penalty_batch` (`optimizer.py:1620`) is `cost * sum|dP| / (2 * p_max)` over the combined draw (`optimizer.py:4834`). A constant level under the floor has no swing and is free, while each such step ends in a stop (row 1). A start to level P costs `P / p_max` of the configured cost, a third at 1.1 of 3.3 kW, so the number is not "per start-stop cycle". A level change inside a run is charged though nothing starts. `count_compressor_starts` (`optimizer.py:1578`) books a start at step 0 whether or not the compressor already runs.
2. **The projection raises, step by step.** `_onto_band` (`thermal_model.py:1700`) lifts every value in `(0, p_min)` to `p_min` on its own step: the energy there grows by the factor `p_min / P`, or the solve avoids it and leaves single steps (rows 2 and 3). `_relaxed_starts` (`optimizer.py:195`) adds one candidate; nothing bundles.
3. **The metered floor never reaches the plan.** `solve_band` (`draw_range.py:637`) learns the top only. `DrawRange.observed` (`draw_range.py:229`) already holds the low end, for diagnostics.
4. **Hot-water starts are priced nowhere.** `_plan_dhw_min_cost` (`dhw_planner.py:1326`) is a linear program without a start term, and on a combi store `_co_optimize` returns `_combi_flux_exchange`'s re-plan unscored (`optimizer.py:3360`). Reading, to confirm on the replay: the exchange re-plans hot water against the space side's drain with the space plan held, so the heat the house takes from the store is re-bought on the hot-water channel (row 3).

## Scope: four parts, one owning seam each

| Part | What | Owner | Callers |
|---|---|---|---|
| P1 | the start count | new pure module `runs.py`, beside `wear.py` | `_grid_terms` (`optimizer.py:3462`), the published count (`optimizer.py:5129`) |
| P2 | commit and dispatch: plans in `{0} ∪ [floor, cap]` as bundled runs | `runs.py` (commit), `optimizer.py` (dispatch, selection) | `_optimize_space_only` (`:4891`), `_optimize_with_dhw` (`:5154`) |
| P3 | the metered floor in the solve band | `draw_range.py` | `coordinator._solve_band` (`coordinator.py:2442`), unchanged |
| P4 | duty changes and hot-water charges as part of a run | `dhw_planner.py`; the term is P1's | `_co_optimize`, `_combi_flux_exchange` |

P1 and P2 are best landed together: they move the same three goldens. P4's switch price is the planned item R10-DUTY-SWITCH-PLANNER-PRICE and waits for part A (#3461); its hot-water half waits for R10-OUTSIDE-DHW-START-HYSTERESIS (#3440). `pump_arbiter.py` is not touched by any part.

**Engaged.** A solve is engaged when a start has a price (`_effective_cycling_cost() > 0`, `coordinator.py:10477`) or the install cannot duty-cycle (`levels_clamped`, `thermal_model.py:1573`). An unengaged solve takes today's path with a zero start term and is byte-identical: its owner has said a start costs nothing and the probe says a sub-floor average is deliverable.

## Shape

```
coordinator: running now (StartCounter.running), band (solve_band, P3), learned switch (duty_switch, P4)
   -> optimize: hot-water plan (LP, then runs.commit in P4)
   -> relaxed space solve: multi-start as today, objective scores the levels as solved, start term = P1
   -> engaged and not realizable?  runs.commit -> masks -> dispatch each (pinned bounds) -> lowest objective ships
   -> result: every running step in [floor, cap]; compressor_starts = P1's integer count
```

**P1, the count.** With `q` the combined draw, `f` the band's floor and `r[k] = min(1, q[k] / f)` the share of step k the compressor runs:

`starts(q) = sum over k of r[k] * (1 - r[k-1])`, with `r[-1]` 1 if the compressor runs at solve time, else 0.

On a plan whose steps are all off or at the floor or above, this is the integer number of off-to-on edges. A trickle at share `r` costs `r * (1 - r)` per step and is never free. A level change inside a run costs nothing. A run that continues from the measured state costs nothing, so a re-solve does not charge a running pump for staying on and does charge it for stopping and coming back. The term is `cycling_cost * starts`, zero at zero cost as today. One formula serves the gradient and the selection: products of clipped linear terms, with a batch twin through `row_sums` like every other term. `SolveInputs` (`optimizer.py:2457`) gains `compressor_running: bool = False`; the coordinator fills it from `_start_counter.running` (`coordinator.py:3908`).

**P2, commit and dispatch.** The relaxed solve drops the projection from its objective: `_realize_draw`, `_realize_joint`, `_published_levels`, `_scores_rounded`, `_relaxed_starts`, `_levels_relaxed` and with them `project_planned_levels`, `_onto_band` and `project_space_against` go. If the relaxed plan is realizable (no running step under the floor), it ships as it is. Otherwise:

- `runs.commit(q, prices, floor, caps, start_cost, band, running, forced) -> mask` is a dynamic program over the steps with the state (on or off, energy balance). The balance is the committed energy less the relaxed plan's up to that step, in quarters of one floor step, held inside `±band` floor steps and within half a floor step at the end. An on step runs at `max(q[k], floor)` and costs its price; an off-to-on edge costs `start_cost`. Pins, off windows, blocks and a cap under the floor are forced. The balance is what replaces "raise": a step lifted to the floor is paid for by a step left out, so the plan's energy stays the relaxed plan's.
- Three bands (2, 6 and 24 floor steps: tight tracking to "same energy, any time") give at most three distinct masks. Each is dispatched: `_apply_pins_to_bounds` (`optimizer.py:1851`) with the mask as pins gives on steps `[floor, cap]` and off steps `(0, 0)`, the bounds a manual plan already produces, and one warm `_lbfgsb_run` with its polish sets the levels. The lowest objective ships. Beside a fixed hot-water plan a step it already runs is forced on and the space floor there is the floor less `dhw[k]`, the rule `project_space_against` has today.
- Run and pause lengths: on the 15-minute grid every run and pause is at least one step, above `early_cutoff.MIN_ON` and `MIN_OFF` (`early_cutoff.py:90`). `commit` takes both as step counts, so a shorter plan step keeps them.

**P3, the floor.** `solve_band` books `min_kw = max(configured, learned floor)`, never above the top. The learned floor is the 10th percentile (`LOW_PERCENTILE`) of the window's running samples whose ask was at or under the floor in force (within `AGREE_TOLERANCE`), once `MIN_SAMPLES` of those exist: the pump was asked for its least and drew more. Restricting to those asks is the guard that matters: a cold week of high asks would otherwise raise the floor to the draw of those. It only raises, and only by more than `AGREE_TOLERANCE`, so a pump that draws what it is asked keeps its figure. It lapses like the ceiling store, is keyed to the configuration like the latch, and stays out where `plan_writes_power()`. It moves the band on engaged solves only; `SolveBand` gains the floor's source and sample count.

**P4, duties and hot water.** The start count takes both series and adds, for each duty change inside a run, that direction's learned stop probability (`Direction.p` while `usable`, #3461), in the order `step_duty` and `_share` serve them (`pump_arbiter.py:492`, `:1680`): a both step is hot water first, so it holds one change into space. `median_off_s` cuts the next step's headroom in `_solve_space` (`optimizer.py:4372`), as the R10 note sketched. The hot-water schedule passes through the same `runs.commit` inside `_build_dhw_requirements` (`dhw_planner.py:951`), accepted only if the planner's own tank walk holds every floor and ceiling the uncommitted plan held and every run meets the planner's start rule (#3440's rebuild); the disinfection step is forced. Where the space plan is known (the `_co_optimize` re-plan and each round of the combi exchange), a charge that begins right after a space run pays only `p(space to hot water)` of a start, so hot water joins the end of a run. On a combi store that is the "one charge": the run is formed and priced on the store's total draw, and the split inside it only chooses the COP curve and the mode written.

## Alternatives

- **Scale the swing term, or add a penalty on levels under the floor.** A local method does not move a block across off steps: the trickle stalls at partial levels, and the flat band `_relaxed_starts` was written for returns.
- **Minimum run time as constraints (MILP).** `OptimizationConfig`'s own comment rules it out for the hardware; the commit program is the same decision on a separable surrogate, with the true objective choosing among its answers.
- **Keep the projection, repair it with a bundling pass.** Two owners of what ships, and the objective would still score a plan the repair then changes.
- **Sigma-delta rounding of the relaxed plan.** It keeps the energy and spreads the pulses evenly: the most starts, not the fewest.
- **Enforce runs in the arbiter or the supply gate (#3456) alone.** The plan would still price heat it does not get; the gate guards writes, it cannot move energy.

## Sibling sites

`git grep -n -E "cycling_penalty|count_compressor_starts|project_planned_levels|project_space_against|_onto_band|_realize_|_relaxed_starts|_scores_rounded|_published_levels" -- 'custom_components/heatpump_optimizer/*.py'` prints `optimizer.py` and `thermal_model.py` only. Covered: both solve paths, the published count, the batch twin. Kept: `duty_floor_kw` (`optimizer.py:3316`) and `planned_draw_runs`' floor argument, which the arbiter reads. Out of scope: the two-zone continuation in `move_starts`, the valve-schedule comparison (`optimizer.py:4028`; commit runs on each candidate or once on the winner, the fixer measures), the stratification of a combi store (#3398).

## Open pull requests

Read on 2026-11-12 from the pull-request list (35 open), the threads of #3440, #3456 and #3461, and the heads by git.

| PR | State | Relation |
|---|---|---|
| #3456 supply minimum run and pause | open; accepted as R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE, timing to move to the switch's own state | builds on. Its open owner decision (a planned run that ends inside the minimum is skipped, "a trade between delivered heat and compressor starts") meets a committed plan only off the grid: commit keeps every planned run and pause at or above the gate's minimums, so the plan no longer books heat the gate would skip |
| #3457 stale step write | open; its change is on main as #3478 | builds on |
| #3461 duty-switch learning, part A | open, draft | builds on. P4's switch price is the item that body names R10-DUTY-SWITCH-PLANNER-PRICE; it adds the reader and its first caller, as the body asks of the first part that reads the estimate. R10-DUTY-SWITCH-RESTART-LEARNING-PR-B (order latch, minimum share) stays the arbiter's: a committed plan holds no both step into the costly direction, so B acts on unengaged installs and on leases. Edges into the start counter (part D of the design review's split) would feed `compressor_running` better than the per-cycle counter |
| #3440 start hysteresis | open; to be rebuilt as R10-OUTSIDE-DHW-START-HYSTERESIS after its own design note | complements, and P4 goes after it (`dhw_planner.py`). The maintainer's ruling there makes the start condition a rule the planner follows when it places a run, against the temperature written to the pump. `runs.commit` on the hot-water schedule takes that rule as its feasibility check, so the two do not place runs twice. The maintainer measured 64 of 114 planned hot-water runs starting within 4 K of the set-point, mostly short top-ups: the same shape as row 1. The raised heating lift becomes the one value for the write and the plan's pricing there; P3 is the metered check beside it, not a second source |
| #3439 disinfection hold; #3497 R10-OUTSIDE-DISINFECTION-SETPOINT | open | `pump_arbiter.py` and `setpoint_check.py` only. P4 forces the disinfection step, so no commit moves or drops it |
| #3434, #3435 learners | open; #3444 and #3468 on main touch the same learners | no planner file either way |
| #3481 R10-ADVISOR-STEADY-START | open | conflict in text only: it also adds a `SolveInputs` field |
| the other open pull requests | | checked by diff for every head from #3000 that is not on main: none touches `optimizer.py`, `dhw_planner.py`, `draw_range.py`, `wear.py` or `thermal_model.py` (#3356 does, and is on main as #3372) |

Already on main and relied on: #3308 (replaced by P2), #3405 and #3433 (the feedback loop is no longer asked to hold a level under the pump's floor), #3358 and #3398, #3372.

## Evidence, by file

`tests/features.py`, failing today:
1. Start count: integer edges on a realizable plan; a constant sub-floor level costs more than zero; a level change inside a run costs zero; a start to the floor and a start to the maximum cost the same; a running compressor continues free; batch rows equal the scalar.
2. Commit: every on step in `[floor, cap]`; forced steps kept; end balance within half a floor step where one exists; identity on a realizable input; run and pause lengths.
3. Floor: high asks alone never raise it; `MIN_SAMPLES` floor asks drawing 1.1 against a configured 0.53 raise it to 1.1; a pump drawing its ask keeps the configured figure; lapse and reconfiguration drop it.
4. P4: a both step and a hot-water-then-space boundary each count `p`; with no usable direction the count is P1's; a committed hot-water plan holds the uncommitted plan's floors.

Null controls: (a) at zero cost on an install that can duty-cycle, every plan is byte-identical: 53 of the 55 value goldens. (b) An empty duty-switch learner against one saturated at p = 1 with a zero cost: identical plans. (c) A relaxed plan that is already realizable ships unchanged.

Goldens that move, claimed with direction in `tests/golden/claimed_drift.txt`: `cycling_cost` and `everything_on`, the two solver goldens that price a start (`coord_all_features` also prices one, but its capture does not solve); their plans hold 9 and 11 sub-floor steps today (first two, measured). `runs.py` enters a measured closure in `tests/closures.json`; the deleted projection pays `tests/structure_budgets.json`.

Replay: the reporter's day as `tests/replay/bankaifan-2026-11-12.json` (`hpo-replay/1`, from the debug bundle), run with modulating, 0.53 kW configured and the wear price. Acceptance on it:
- at most 4 compressor starts in 24 h, no planned run or pause under 10 min, no planned level between 0.1 kW and the band's floor;
- plan energy not above the relaxed plan's by more than one floor step (no running through as in row 2), and the published saving not negative: cost at or under the plan's own reference;
- room inside 21.5 to 25.5 °C and tap temperature at or above 47 °C throughout.

**Spike** (golden house, no hot water, floor 1.1, max 3.3, start cost 2.5, 96 steps; commit as above, dispatch through pins; script `dev/audit/harnesses/honest_starts_spike.py` on the branch `spike/honest-starts-and-runs` of Bankaifan/heatpump_optimizer, which never merges):

| Profile | Today, modulating | Today, on_off | Relaxed, no start term | Committed |
|---|---|---|---|---|
| shoulder weather, flat prices | 18 sub-floor steps, 0.86 kWh | 1 run, 5.78 kWh | 16 sub-floor steps, 5.79 kWh | 1 run, 5.98 kWh, same lowest room temperature, objective without starts 9.58 against 9.60 |
| shoulder weather and prices | 15 sub-floor steps, 1.03 kWh | 1 run, 4.40 kWh | 16 sub-floor steps, 7.20 kWh | 1 run, 6.33 kWh (wins at this cost) or 2 runs, 7.26 kWh |
| mild winter, typical prices | realizable | realizable | realizable, 2 runs | unchanged |

## Solve time

Measured on the golden scenarios: a space solve makes 8 `_lbfgsb_run` calls today (4 starts, each with its polish). An unengaged solve gains nothing but a boolean. An engaged one gains the commit program (2 to 63 ms in plain Python in the spike, the widest band the slowest; states are 96 × 2 × at most 193) and 2 calls per distinct mask, at most 6, warm and mostly at a bound. An on_off install loses the rounded scoring's flat band and the `_relaxed_starts` run. In the spike the three candidates, each re-solved through the whole `optimize`, added 0.10 to 0.62 s to a 0.08 to 0.52 s solve on x86; that is an upper bound. `tests/stress_budgets.json` decides.

## Decisions for the owner

1. A priced start engages bundling on a modulating install too, which moves the three goldens. Engaging on on_off alone would leave row 1 as it is.
2. P3: the learned floor moves the plan (proposed), or stays a notice beside the configured figure.
3. Whether P4's hot-water half joins R10-DUTY-SWITCH-PLANNER-PRICE or R10-OUTSIDE-DHW-START-HYSTERESIS or is a group of its own, and whether P1 and P2 land as one group.

## As built in this pull request

Base `870238eb21` (v7.1.12, with #3461 merged). Where the build differs from the sections above, this section is the record.

- **P1, the count.** `runs.start_count` and its batch twin count `a[k] * (1 - r[k-1])`, with `a[k] = min(1, q[k] / MIN_RUNNING_DRAW_KW)` (the step runs at all) and `r` as above. The form proposed above, `r[k] * (1 - r[k-1])`, charges a trickle at most a quarter of a start per step, and on the reporter's install a trickle plan won the comparison against a plan of runs. Now a step under the floor leaves its successor the start that step is. On a plan whose steps are all off or at the floor or above, both forms are the integer edge count. `SolveInputs.compressor_running` is the duty-switch learner's settled running signal where one is listened to, else the metered draw against `on_threshold_kw`, else the executing step; the start counter follows one sample per optimization interval and is no reading for it. `compressor_starts` publishes the shipped plan's integer edge count.
- **P2, commit.** The relaxed multi-start runs with the start term off (`_start_term_off`). The count is bilinear in neighbouring steps, and a descent priced with it stayed where its start lay: a trickle it did not leave, or one run it did not break. `_commit_runs` then builds the candidates (`_run_plans`): the per-step projection, raised and rounded; each band's `runs.commit` mask (`BANDS`, widening to the whole horizon; a balance outside its band is penalised by `OUT_OF_BAND`, never refused); the relaxed plan where it already runs. It scores all of them in one `objective_batch` call on the true objective with the start term, re-solves the levels of the best two inside their runs, polishes the better one (`_pinned_runs`) and ships the lowest score. So no plan ships worse than the projection, and a failure anywhere in the stage ships the projection. A committed space step runs at the floor or above on its own, also beside a hot-water charge: the plan stays one the pump can run when the combi exchange moves the charge afterwards. On an install that can duty-cycle, a step capped under the floor still cycles; on one that cannot, it stays off.
- **P3, the floor.** The floor store admits only asks at or under the configured floor × (1 + `AGREE_TOLERANCE`), and each sample lapses on its own age, so an engaged plan cannot ratchet the floor: it lapses back to the configured figure and is learned again. Persisted as `draw/floor`.
- **P4, hot water.** `runs.commit_store` is a program on the planner's linear store (`runs.Store`, 0.25 K grid). A charge runs whole steps at the run power and may end inside its last step where the store is full: the pump runs at its level and stops, so that step is no level under the floor (a tail). A charge that starts in the step it ends in is a whole run and must last `MIN_ON`. On an install that cannot duty-cycle a tail stays at the floor or above, the level contract `clamp_planned_levels` has today. A step without a charge is not bound by the charge ceiling, because a combi store's space side heats it past, and stops at the store's rating, as `thermal_model.store_step` does. Without those two rules the program had no feasible path in most exchange rounds on the reporter's install and the planners' trickle plan shipped. What a charge pays besides its energy follows the compressor (`_charge_costs`): a start where it is off, the learned share of one for each duty change where the space plan runs. The hot-water plan that ships is the cheaper, in energy at the planning prices plus starts, of the committed plan and the planners' own plan with every step under the floor run at the floor (`_commit_charges`); so an engaged plan holds no charge step under the floor but a tail. Limit: the program charges at the run power only, so a modulating pump's long part-load charge comes from the second candidate.
- **Combi store.** The space plan is not re-solved after the flux exchange. Charges move the store in whole steps, the space side's flux moves with the store, and the rounds need not settle: `_held_round` keeps the round whose store, walked by the model, falls least under the requirement, and of those the cheapest. `_settled` then settles the space plan against that hot-water plan. The space plan was solved around the first hot-water plan; the exchange's charges hold the store afterwards; the space runs still carry heat for a store those charges had not warmed (measured on the reporter's install: one hour at 3.4 to 3.5 kW into a store at its 55 °C limit), and a charge that left its step leaves a pause in the space run it sat in. Each space run is tried switched off and lower (`_TRIM_SHARES`), each pause run through at the floor. A candidate is kept only where the pair's objective on the model's own walk is lower and the store falls no further under the hot-water requirement, the promise a free re-solve cannot make. An unengaged solve does not run this stage and is byte-identical; its plans hold the same double heating, a finding for R10-COMBI-TANK that this pull request does not act on.
- **Duty-switch price** (R10-DUTY-SWITCH-PLANNER-PRICE). `duty_switch.planner_reading` is the reader and the coordinator its one caller: per direction `Direction.p` while `usable`, else 0.0, into `OptimizationConfig.duty_stop_to_space` and `duty_stop_to_dhw`, priced by the start count and by the charge program. The `median_off_s` headroom cut is not built.
- **`dhw_floor_breach_c`** is published under a block always, and on a solve that plans runs when a cap leaves some step under the pump's floor and the tank falls short.
- **Tried and dropped, measured.** A store-hold term in the space objective (the space channel carries the store through the hot-water window): 16 % cheaper in the model, L-BFGS-B up to 24 s, and on a stratified combi store heating mode does not raise the top sensor. A hot-water re-plan pass on every priced solve with a separate tank: the same starts and costs on eight golden variants, more solve time.
- **Not built**: the previous plan's mask as a candidate; #3440's start rule; the reporter's replay file.
- **Run and pause minimums** `MIN_ON`, `MIN_OFF` live in `runs.py`; `early_cutoff` imports them.

**Measured on the reporter's install.** Config entry of 2026-11-12 (504 l store around a 40 l coil, 0.53 kW configured and 1.1 kW metered floor, 3.5 kW, manual valve at 24 °C, hot water 47 °C minimum and 52 °C set-point in a 06:00 to 18:00 window, wear price 0.25 per start), the day-ahead prices of 12 and 13 November, synthetic weather, 24 h at 15 minutes. Script outside the tree; base `870238eb21` → head, one machine. A start is a running step after a step under the floor; "under the floor" excludes a charge's tail.

| Day | Variant | Starts | Steps under the floor | kWh | Cost | Store at the end, °C |
|---|---|---|---|---|---|---|
| 12 Nov | modulating, 0.53 kW, 0.25 | 35 → 5 | 32 → 0 | 14.52 → 12.17 | 5.61 → 4.80 | 55.0 → 54.8 |
| 12 Nov | modulating, 1.1 kW, 0.25 | 34 → 6 | 30 → 0 | 14.97 → 12.24 | 5.85 → 4.87 | 55.0 → 55.0 |
| 12 Nov | on_off, 1.1 kW, 0.25 | 10 → 7 | 0 → 0 | 17.60 → 12.33 | 7.11 → 4.90 | 55.0 → 55.0 |
| 12 Nov | modulating, 0.53 kW, 10 | 77 → 1 | 76 → 0 | 11.33 → 11.00 | 4.63 → 4.56 | 51.9 → 43.0 |
| 13 Nov | modulating, 0.53 kW, 0.25 | 26 → 1 | 21 → 0 | 11.92 → 9.61 | 4.01 → 3.31 | 49.5 → 43.0 |
| 13 Nov | modulating, 1.1 kW, 0.25 | 32 → 5 | 29 → 0 | 12.65 → 10.48 | 4.23 → 3.48 | 48.9 → 43.5 |
| 13 Nov | on_off, 1.1 kW, 0.25 | 8 → 6 | 0 → 0 | 15.51 → 10.65 | 5.34 → 3.55 | 55.0 → 43.5 |
| 13 Nov | modulating, 0.53 kW, 10 | 14 → 1 | 10 → 0 | 11.32 → 9.60 | 3.70 → 3.30 | 43.8 → 43.0 |

Tap temperature inside the window is 47.0 °C or above on every row, base and head; the room trajectory is the same on every row (22.2 to 24.1 °C), since the valve feeds the floor from the store. Read the cost column with the last one: where the head ends the day with a colder store, part of the saving is heat not bought for the next day, which the objective's terminal term prices and a rolling re-solve never executes. The rows with the same end state are the first three: 14 to 31 % less cost. Part of what the base plans there is energy into a store at its limit, which a real pump would refuse, so the metered saving will be smaller than the modelled one.

**Measured on the golden scenarios with runs planned** (the two goldens that price a start, and twelve variants of others with `cycling_cost` or `clamp_planned_levels` set; base → head): starts 2 to 29 → 2 to 8; steps under the floor up to 28 → none but four charge tails; the tank's worst shortfall 0.56 K at most → 0.42 K at most; lowest room between 0.54 K under and 0.32 K over the base's. Cost moves between −15 % and +9 %, and on `shoulder` at 0.5 per start from 3.33 to 6.96: the base plan there is 28 steps under the floor that the pump cannot deliver, and the base's own on_off projection of that scenario costs 7.39. The 54 goldens that price no start and can duty-cycle are byte-identical (`tests/env_drift.py --all`).

## Solve time, as built

One machine (2 cores, x86), base → head, wall seconds for one `optimize`. The fourteen golden variants above sum to 15.8 → 15.3: `cycling_cost` 1.04 → 0.20, `everything_on` 3.00 → 3.43, `winter_two_zone_dhw` 1.25 → 1.46, `valve_storage` 4.01 → 4.61, `shoulder` as on_off 0.96 → 1.76. The reporter's install: 0.8 to 3.8 → 1.5 to 1.8 at 0.25 per start, 5.3 to 6.4 → 1.5 to 1.8 at 10. The relaxed solve without the start term converges sooner than the priced one did; the commit stage adds two warm L-BFGS-B runs and one polish; `_settled` adds about twenty walks of the pair at about 3 ms each. `tests/stress.py` passes.

## Notes for the fixer

- 2, 6, 24 and the quarter-step balance grid are constants from the spike, not measured thresholds; name them.
- The start count's floor needs a guard for a configured floor of 0 (`MIN_RUNNING_DRAW_KW`, `thermal_model.py:1194`).
- Dispatch must not go through `h.space_pins`: the safety release of manual pins would report committed steps as released.
- `_batch_fd_gradient` should skip fixed variables on a committed mask; most of the 96 are fixed.
- The previous plan's mask, shifted by the elapsed steps, is a free fourth candidate and keeps ties from moving a standing run.
- A commit that finds no mask inside any band (caps, pins) ships the tightest band's best effort and says so in the status; it never falls back to raising.
