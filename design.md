# R11-OUTSIDE-HONEST-STARTS-RUNS: a start priced as one start, and plans shipped as runs the pump can run

Designer seat, round 1. Base and `origin/main`: e23124ff6e45bac1d48b4a775dad555a37965355; every line cited was read at that SHA unless marked. Outside pull request 3529 by Bankaifan read as data at its head 1f9daef4d93f1d669005c448e122ec82980c4cef (`git ls-remote origin refs/pull/3529/head` on 2026-11-13 still answers it), merge base 870238eb21; the finding, the four causes, the commit program and every measured figure quoted are the contributor's, with thanks. Predecessors: R10-DUTY-SWITCH-PLANNER-PRICE and R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE are merged (handoff heads a79a9f8bfa and 390113cc66 are ancestors of the base); R10-OUTSIDE-DHW-START-HYSTERESIS read at handoff 667a8c8302; R10-ADVISOR-STEADY-START at handoff 2d2bea03bd. No finder harness: outside report. Two premises of the brief did not hold and change nothing below: no ref design/R11-OUTSIDE-HONEST-STARTS-RUNS existed, so the contributor's note was read at the pull-request head; and the duty legs are not in `duty_switch.py` but in the leaf `duty_legs.py`, the reader alone is `duty_switch.py:528` (`planner_fields`).

## Finding (re-anchored at the base)

1. `cycling_penalty_batch` (`optimizer.py:1886`) prices the swing of the combined draw: a constant level under the pump's floor is free though every such step ends in a stop, a start to the floor costs floor / p_max of the configured price, and `count_compressor_starts` (`optimizer.py:1844`) books a start at step 0 whether or not the compressor runs.
2. `_onto_band` (`thermal_model.py:1700`) raises each sub-floor step to the floor on its own; nothing bundles steps into runs.
3. `solve_band` (`draw_range.py:637`) learns the top of the band only.
4. `_plan_dhw_min_cost` (`dhw_planner.py:1340`) has no start term.

## Rulings the brief asks for

**(c3) One group or three: three, and this note designs the first.** The pull request's build commit 7eeb7cd676 changes three concerns with three owners; one fixer owning all three is the two-owner case of the designer contract, and the split below is by owner, not by size.

| Group | Concern | Owner | Size | Order |
|---|---|---|---|---|
| A, this group | what a start is in a plan, and which runs of the combined draw ship (the note's parts 1 and 2, and the unit of the switch term) | a new pure leaf, the runs module, beside `duty_legs.py` | XL | as the roster has it |
| B, new | hot-water charges as runs: the store commit, the combi hold and settle (part 4's hot-water half) | `dhw_planner.py` | L, design first | after A and after R10-OUTSIDE-DHW-START-HYSTERESIS merge |
| C, new | the metered floor (part 3) | `draw_range.py` | M | independent of A and B |

Reasons in the code. B: the pull request's store program carries a copy of the planner's linear store (decay, drift, heat, bounds) into the runs module, a second holder of the tank dynamics `dhw_planner.py` owns; its combi stage rewrites the rounds of `_combi_flux_exchange` (`optimizer.py:1705`), R10-COMBI-TANK's seam, and the contributor records there "a finding for R10-COMBI-TANK that this pull request does not act on"; and it cannot start before the hysteresis rule it must call is on main. C: its state is `draw_range.py`'s sample store and a persisted key, no line of it is read by A, and it moves no golden. A alone is coherent: the hot-water plan stays the planner's, shipped as today (`project_planned_levels`, `thermal_model.py:1687`, on the tank channel), and A prices its starts on the combined draw, which no code does today.

**(a) Part 6 is dropped.** Not built: the pull request's second reader in `duty_switch.py`, its two scalar config fields, and the hot-water, to-space and to-hot-water arguments of its start count, which re-derive the leg rule without the collapse edges of `both_step_legs` (`duty_legs.py:39`), a duplicated shape (`D7.md`). The values stay `duty_switch_stop_probability` and `duty_switch_off_seconds` from `planner_fields`; the pairs stay `leg_ends` (`duty_legs.py:62`). Composition is in Shape.

**(b) The start hysteresis rule is group B's feasibility check, as a call.** At 667a8c8302 the rule is `startable_steps`, `drop_unstartable` and `place_startable` in `dhw_planner.py` over `dhw_start_below_c` in `thermal_model.py`. B's commit accepts a charge mask only if the planner's own walk holds every floor the uncommitted plan held and every charge begins on a step that rule calls startable; the runs module receives the answer as a per-step boolean and never reads a temperature. Binding on B's designer; A builds nothing of it.

**(c1) A priced start engages on a modulating install too: recommended, decision: owner.** Engaged means `cycling_cost` above zero or `clamp_planned_levels`. Engaging on fixed-speed installs alone would keep two cycling terms alive (swing for one install class, count for the other), give the switch term two units, and leave the finding's first row as it is. Cost: the two goldens below move on a modulating fixture.

**(c2) The learned floor starts as a notice: recommended, decision: owner.** As built the floor store admits only asks at or under the configured floor, and an engaged plan never asks there again once the floor is raised, so the estimate lapses, the plan returns to levels the pump cannot hold, and it is learned again: a limit cycle by construction, which the contributor's note states ("it lapses back to the configured figure and is learned again"). The form first proposed (asks at the floor in force) has no such cycle and no way down. Which is right is a measurement on more than one install. Group C therefore publishes the learned floor, its source and its sample count on `SolveBand` and raises the configured-against-metered notice; the plan moves when the user sets the figure. In the contributor's table the rows configured at 1.1 kW end at 5 and 6 starts and those at 0.53 kW with the learned floor at 1 and 5; those figures are the whole build's, modelled, and A's own are measured by test 5.

## Owning seam (group A)

**The runs module, new, pure (numpy, `row_sums`, `MIN_RUNNING_DRAW_KW` from `thermal_model.py:1194`)** owns: the start count of a combined draw, scalar and batch; the running share of a step; whether a plan is realizable; the commit of a relaxed plan to an on/off mask; and the shortest run and pause, moved from `supply_hold.py:60` because the optimizer may not import that module (it imports Home Assistant, `fixer.md` step 17) and three readers need one figure. **Callers only:** `optimizer.py` (objective closures, candidate selection, publication), `supply_hold.py` and `early_cutoff.py:92` (the two constants), `duty_legs.py` (nothing; it gains one keyword), `duty_switch.py` (one read of the running class), `coordinator.py` (one argument at `SolveInputs`, `coordinator.py:6312`). `tests/seam_map.json` maps coordinator units only; no entry is owed. Not touched: `pump_arbiter.py`, `dhw_planner.py`, `draw_range.py`, `store.py`.

## Shape

**The count.** With q the combined draw, f the larger of the band's floor and `MIN_RUNNING_DRAW_KW`, a[k] = min(1, q[k] / `MIN_RUNNING_DRAW_KW`) and r[k] = min(1, q[k] / f): starts(q) = sum of a[k] x (1 - r[k-1]), r[-1] = 1 when the compressor runs at solve time. This is the contributor's as-built form; the form r[k] x (1 - r[k-1]) lost to a trickle plan on the reporter's install. On a plan whose steps are all off or at the floor or above it is the integer edge count. The term is `cycling_cost` x starts. `cycling_penalty`, its batch twin and `count_compressor_starts` are deleted, not kept beside it: at zero cost they return zero, so no unengaged solve reads them. The published count is the integer edge count of the shipped plan with the same r[-1], so a running pump that keeps running publishes one start fewer than today, on every install.

**The switch term, so one stop is never priced twice.** `switch_weights_batch` (`duty_legs.py:106`) gains one keyword, the level its pairs are weighed at, default the combined draw (today's operands). The optimizer passes p_max x r. A pair then weighs p x min(r before, r after), and p x r inside a two-leg step, in starts. A boundary's start share is 1 - r[k-1] and its switch weight at most p x r[k-1], so their sum never exceeds one start; on a committed plan every boundary is exactly one of start (1), priced switch (p) or neither. The floor argument stays `_duty_floor` (`optimizer.py:142`), so planner and arbiter read the same legs. `_avoid_priced_switches` (`optimizer.py:332`) keeps its candidate and scores it on the same objective; `availability` and `delivered_space` are applied as today, built from the profile the pinned re-solve starts from.

```
coordinator: running now = duty_switch's settled class, else the executing step        -> SolveInputs (one bool)
relaxed multi-start: today's solve; closures built without the start and switch operands, no rounding inside the objective
engaged?  no -> today's path, today's arrays
          yes -> candidates: (1) today's projection of the relaxed plan (_realize_joint)
                             (2) the leaf's commit masks over the bands, forced by pins, off windows, blocks, caps under the floor
                             (3) the relaxed plan itself where realizable
                 one objective_batch call on the true objective (energy, comfort, capacity, cycling_cost x (starts + switch))
                 best two: levels re-solved inside bounds from _apply_pins_to_bounds, mask as pins; the better is polished
                 lowest score ships; any failure in the stage ships candidate (1)
result: every running step in [floor, cap]; compressor starts = integer edges
```

**Commit** is the contributor's program: over the steps, state (on or off, run or pause length, energy balance against the relaxed plan in quarters of a floor step), an on step at max(q, floor) under the cap paying its price, an off-to-on edge paying the start price, a balance outside its band penalised and never refused, the run and pause minimums as step counts. Inside a pinned re-solve every on step is bounded at or above the floor and every off step at zero, so the count is constant and the gradient never differentiates it.

**Invariants.** An unengaged solve builds its objective operand for operand as today. No engaged plan scores above candidate (1) on the true objective. No shipped step lies between `MIN_RUNNING_DRAW_KW` and the floor, except on a duty-cycle install under a cap below the floor. A realizable relaxed plan ships unchanged. The shipped total of a clamped plan stays in {0} or [p_min, p_max], the contract R10-DUTY-SWITCH-PLANNER-PRICE's tests pin. No payload key, no entity attribute and no store key is added; `SolveInputs` (`optimizer.py:2729`) gains one boolean, default false.

## Alternatives

- **Keep the swing term and add the count only for fixed-speed installs:** two owners of what a start costs and a switch weight in two units (ruling c1).
- **The switch probabilities as arguments of the start count (as built):** a second leg rule beside `leg_ends`; part B of the duty-switch work would edit both.
- **A unit flag on the switch weight instead of a level:** prices p in full beside a step that already paid 1 - r of a start, the double charge the brief forbids.
- **The start term inside the relaxed descent:** measured by the contributor: bilinear in neighbouring steps, the descent stayed where its start lay. **A context manager switching the term off on the optimizer (as built):** mutable solve state where two closures built once carry the same fact.
- **The run and pause minimums as two config fields filled by the coordinator:** one more pair of values that can disagree with the gate's; a leaf constant cannot.
- **Minimum run time as constraints in a mixed-integer program:** the comment inside `OptimizationConfig` (`optimizer.py:2402`, "would make it a MILP") rules it out for the hardware.

## Sibling sites

`git grep -n -E "cycling_penalty|count_compressor_starts|project_planned_levels|project_space_against|_onto_band|_realize_|_relaxed_starts|_scores_rounded|_published_levels" e23124ff6e -- 'custom_components/heatpump_optimizer/*.py'` prints `optimizer.py` and `thermal_model.py` only. Covered: `_grid_terms` (`optimizer.py:3731`, both cycling calls), the published count (`optimizer.py:5399`), `_shipped_and_received` (`optimizer.py:254`, loses the rounding), `_relaxed_starts` (`optimizer.py:406`) and `_scores_rounded` (`optimizer.py:192`), both deleted. Kept: the three projection functions in `thermal_model.py` (candidate 1 and the tank channel), `duty_floor_kw`. `git grep -n "SolveInputs(" e23124ff6e -- custom_components` prints `coordinator.py:6312` (covered) and `coordinator.py:11304` (the simulated solve: it passes the same reading, or its plan would charge a start the live plan does not). `git grep -n -w -E "MIN_ON|MIN_OFF|MIN_RUN|MIN_PAUSE" e23124ff6e -- custom_components` prints `supply_hold.py` and `early_cutoff.py`: both import the moved constants. Out of scope with a named owner: the two-zone continuation and the valve-schedule comparison (the fixer measures commit on the winner only and reports), hot-water charges (B), the floor (C).

## Evidence, by file

`tests/features.py`, failing today because the leaf, the keyword and the boolean do not exist:
1. **Count:** integer edges on a realizable plan; a constant sub-floor level costs more than zero; a level change inside a run costs zero; a start to the floor and a start to the maximum cost the same; a running compressor continues free and pays for a stop and a return; batch rows equal the scalar bit for bit.
2. **Composition:** hot water then space at equal draw with p = 1 costs exactly two starts with the steps adjacent and exactly two with an idle step between; over a generated grid of plans every boundary's start share plus switch weight is at most 1; with the keyword omitted `switch_weights_batch` returns today's values.
3. **Commit:** every on step in [floor, cap]; forced steps kept; end balance within half a floor step where a mask inside the band exists; identity on a realizable input; run and pause lengths at a 5-minute step.
4. **Selection:** the shipped score is never above candidate (1)'s; a stage that raises ships candidate (1).
5. **Acceptance,** on a synthetic fixture built from the contributor's table (15-minute steps, 0.53 and 1.1 kW floors, wear price 0.25; no private bundle enters the tree): the shipped plan holds no step between `MIN_RUNNING_DRAW_KW` and the floor, its start count is no higher than that of today's plan counted by the same function, and its energy is within one floor step of the relaxed plan's. No start total and no saving is asserted as a figure: the contributor's are modelled on one install, and the body reports what the fixture measures at base and head.

Null controls, each a full `optimize` twice with arrays compared equal: zero cost on a duty-cycle install; an empty duty-switch learner against a saturated one at zero cost; a realizable relaxed plan; and `python3 tests/env_drift.py --all`, where every golden that prices no start and can duty-cycle reproduces. **Goldens that move:** `tests/golden/cycling_cost.json` and `tests/golden/everything_on.json`, claimed with direction in `tests/golden/claimed_drift.txt` under the `claims-for:` of the version live at build time; the pull request's two claim lines are restated, not merged, no fixture is re-recorded, and the two names leave may-drift while claimed. Group B will claim the same two again. Solve time: `tests/stress.py` against `tests/stress_budgets.json`, base and head on one machine. **Mutation targets:** r[-1]; the 1 - r factor; a against the running rule and not the floor; the guard for a floor of zero; the level keyword's default; min(r before, r after); the engaged predicate, each arm; candidate (1) left out of the batch; the lowest-score choice; the mask-to-bounds call; the fallback; the out-of-band penalty; the end-balance half step; the run and pause counts; the coordinator's argument.

## Hot files, position, carries

After the v10.0.0 stamp, after R10-OUTSIDE-DHW-START-HYSTERESIS merges (it edits `thermal_model.py` and `coordinator.py`) and after R10-ADVISOR-STEADY-START merges (it adds `held_start` to `SolveInputs` at 2d2bea03bd). Hot: `optimizer.py`, `duty_legs.py`, `duty_switch.py`, `supply_hold.py`, `early_cutoff.py`, `coordinator.py`, the new leaf, `tests/features.py`, `tests/closures.json`, `tests/deployment_shape.py`, `tests/golden/claimed_drift.txt`, `docs/architecture.md`, `tests/mutation_ledger/`. The roster's file list also names `draw_range.py`, `dhw_planner.py`, `store.py` and `thermal_model.py`, which A no longer edits. Closures and the deployment shape are re-derived on Linux. No grader is changed, so no p1/p2 split is owed.

## Decisions routed

- decision: owner. Ruling c1, engage on modulating installs (recommended yes).
- decision: owner. Ruling c2, group C ships a notice and the plan moves on the configured figure (recommended), or the learned floor moves the plan.
- decision: orchestrator. Rulings c3 and b: roster groups B and C, B design first with ruling (b) in its brief. Until they exist nothing in the tree carries them; this note is their only record.
- decision: orchestrator. Authorship: commit 7eeb7cd676 holds A, B and C in one commit and `git merge-tree --write-tree origin/main` against the pull-request head conflicts in 11 files, so A cannot be a cherry-pick of it. Either the contributor re-cuts the pull request to A on the base, or a seat rebuilds A crediting Bankaifan and pull request 3529 by name.

## Notes for the fixer

- Every structure metric may only move down (`python3 tests/structure.py`). The payment is real here: the two cycling functions, the old count, `_relaxed_starts`, `_scores_rounded` and the relaxed-levels attribute go, and the candidate stage is module-level functions, not optimizer methods. No payment found is a stop and ask before the push. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n1)
- The pull request deletes 24 pins under `tests/mutation_ledger/killed_by/`, some for functions that survive (`_combi_flux_exchange`, `_batch_fd_gradient`). A pin whose function survives is re-pinned by the autofix lane, never deleted by hand. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n2)
- The bands (2, 6, 24 floor steps), the quarter-step grid, the out-of-band factor and the two re-solved candidates are constants from the contributor's spike on one install: name them as such. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n3)
- Dispatch must not go through the horizon's manual space pins: the safety release would report committed steps as released pins. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n4)
- The running class is the tracker's settled value on the duty-switch record (`wear.compressor_running` debounced, `duty_switch.py:480`); where no reader is attached the fallback is the executing step, never the start counter, which follows one sample per interval. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n5)
- The finite-difference gradient should skip variables a mask fixes; most of the horizon is fixed in a pinned re-solve. Measure before and after with `tests/stress.py`. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n6)
- R10-DUTY-SWITCH-PLANNER-PRICE's clamped-install and edge tests in `tests/features.py` pin shipped totals and scores the commit keeps; one that fails is a finding to report, not a test to rewrite. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n7)
- The previous plan's mask shifted by the elapsed steps is a free fourth candidate that keeps ties from moving a standing run; not in this design, measure it and report. Carry: dismissed: not designed here, a follow-up finding if the fixture shows ties moving runs (item n8)
- The pull-request body thanks Bankaifan by name and pull request 3529. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS (item n9)

Seat tokens: three read-only scouts, 74858, 65587 and 93474 (harness figures); the harness reports none for the main loop.
