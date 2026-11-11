# Design: R10-ADVISOR-STEADY-START — the what-if's steady-start estimator (#2257)

**Round 3 (targeted amendment)** of the note approved at d2d663c32a87a546e956c57aef56384d5303a0bb, under the orchestrator's ruling of 2026-11-11T06:21:01Z (mandate 6715477401) on the fixer's blocked stop c966138ad5fa. Base: origin/main a7628041dc02e298c5399003d4c0576391dd5c4e. Built work: handoff-wip/r10-advisor-steady-start, estimator head 273079db5 on merge base 8f97247fc; `git diff --stat 8f97247fc a7628041` over this note's hot files prints nothing, so every line cited at 273079db5 stands at the base. Sections A1-A6 below amend the note; the round-2 text follows unchanged and stands wherever A1-A6 do not replace it. The appendix carries the measuring script as text, which takes the file past designer.md's two pages; the amendment itself is A1-A6.

## A0. Re-measured
- At a7628041 (no estimator on main): `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif` prints `whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0` and caps `plan 18/36 settled 1/36`.
- At 273079db5, the appendix script with `none` on the coordinator fixture (`_solve_coord`, tests/features.py:30660 at 273079db5; hours 01..23 step 2, one frozen instant each, minute 07): `degree rows 24 steady_wrong 6 (minus_1@05, 07, 09, 11, 19, 21) held_wrong 0 settled_wrong 11 plan_wrong 2 | cap rows 12 steady saving(<-1) 0`. The fixer's six rows, to the row.

## A1. Which candidate carries the residue (brief item 1)
One perturbation per run, same fixture, same 24 degree figures, the built estimator otherwise untouched. The solves run in the probe's own process (the worker seam answered in place), or a patch never reaches them: a first pass through the process worker printed the unperturbed count for every arm, which is this table's own null.

| perturbation | wrong of 24 | rows |
|---|---|---|
| none | 6 | minus_1 at 05, 07, 09, 11, 19, 21 |
| settlement caps lifted (room and slab to 99) in the reported settlement only | 6 | the same six |
| the same lift in the objective's terminal cost too | 7 | the six and minus_1 at 17 |
| both sides settled at the live schedule's caps | 19 | worse on both asks |
| comfort floor lowered below the reachable range (`min_temp` 12 on both sides) | **0** | none |
| solver basin: each held solve re-run with the other side's plan as an extra candidate (the optimizer's previous-plan seam, `_warm_start_starts`) | **4** | 05 and 07 turn right; 09, 11, 19, 21 stay |
| refill price of the settlement at the horizon's mean, then its maximum (a fourth candidate, not in the brief) | 3, then 0 | |

**The caps do not carry it**: lifting them moves no row. **The floor and the solver basin carry it together.** With the floor out of reach the two held plans are the same plan a kelvin apart (spend differs by 0.00 to 0.20 a day on 11 of 12 minus rows) and the figure reads -24.7 to -32.0 at every hour: whatever basin the solver lands in, both sides land in it and it cancels. With the floor in reach the cooler schedule meets it first (the tile ask lowers every comfort level and leaves `min_temp`, price_tiles.py `specs`), the two sides stop being translates, and each lands in its own local optimum: the cooler side's objective reads 44.2 against 32.5 at 05 and 27.1 against 25.6 at 07, and the seed moves its spend plus deferred by 0.68 and 1.21 a day where the whole figure is about 1 a day per kelvin. The pair, measured: floor alone 6 to 0; basin alone 6 to 4; the seed changes no row once the floor is out (already 0). The refill price moves the count because it re-weights the stored kelvin the two starts differ by, which is a bias, not a repair: at the maximum it reads 0 wrong by over-crediting every cooler start.

**Restarting each side from its own plan's end does not repair it** (measured, rejected): one restart reads 12 of 24 wrong, two read 13. The restarted plans start where they end (settlement near 0), and the cooler plan, 0.25 to 0.70 K colder on average, still spends 0.19 to 2.22 a day *more* on 9 of 12 rows. That is the solver's local-optimum spread, about 1 a day (3 to 4 % of a 25 a day spend), on a signal of 0.3 to 1 a day. No difference of two independent solves' money is sign-safe on this fixture.

## A2. The amended estimator (brief item 2)
What survives the basin is the temperature each plan holds: on all 120 degree rows measured (the none, floor, basin, one-restart and two-restart runs) the cooler side's mean room temperature is 0.25 to 0.91 K below the live side's and the warmer side's 0.71 to 1.04 K above. So the steady figure prices **the kelvins the plan delivers, at the thermostat's price per kelvin**:

- schedule shift = the what-if side's reference-schedule mean over the horizon less the live side's, both read off the steady pair's results (a new float on the optimizer's result, see A3);
- thermostat = the what-if's `baseline_cost` less the live's (the held figure's numerator, price_tiles.py `monthly_deltas`);
- delivered = the mean of the steady what-if result's `room_temp_trajectory` less the mean of the steady live result's;
- **when the schedule shift is at least 0.05 K in magnitude and thermostat is not 0: figure = thermostat x delivered / shift, plus the what-if's spend outside its solve**; otherwise (a cap, a floor, a weight, hot water: the thermostats agree) the figure is the built one, the steady pair's spend plus `deferred_energy_cost`, what-if less live.

Both branches read only the two held-start solves and the two thermostats, so the figure cannot move with the measured start. The sign of the first branch is the sign of thermostat times the sign of delivered over shift; it is wrong only if the plan under a cooler schedule runs warmer on average than the plan under the warmer one.

Measured on the amendment built in the scratch worktree (never pushed):
- coordinator fixture: `degree rows 24 steady_wrong 0 () held_wrong 0 | cap rows 12 steady saving(<-1) 0`; minus_1 reads -34.1 to -22.0, plus_1 +24.1 to +43.6, the cap +7.8 to +31.4 (the cap rows are the built figure, unchanged to the cent).
- held-figure null control: 0 of 24 wrong, in every run of A1.
- `r10_advisor_residue.py whatif`: `steady rows 24 steady_moves_by_start 0 degree figures against the held sign 0/36 cap figures reading a saving (< -1) 0/36 cap range -0.7..+46.0`.
- `r10_advisor_residue.py steadysign` (the fixer's arm): `rows 48 steady_wrong_sign 0 held_wrong_sign 0`; it read 1 of 48 at 273079db5.
- floor out of reach: 0 of 24, -38.5 to -28.6 against the pair's own -32.0 to -24.7 there. **Stated, not hidden:** where the pair can be trusted the amended figure reads up to a fifth larger, because the thermostat buys its kelvin at the hours it falls and the plan at cheaper ones. The docs sentence of A3 says what the figure is.

**Cost.** No solve is added. Counted on the fixture: 3 solves on a first what-if against a plan, 2 on a memo hit, before and after, which is the round-2 bound. Wall on this cloud box with four probes sharing four cores: first ask mean 2.77 s (max 4.05), memo hit mean 0.88 s (max 2.09); the amendment adds two list means and one division. The Pi bound stays count times per-solve wall, the fixer's to state; `SIMULATE_MIN_INTERVAL_SECONDS` and the background path are untouched.

**Decided here, with its cost.** An ask that moves the schedule *and* something else (a degree and a cap in one panel ask) is priced through the kelvins it moves only; the cap's own timing cost is not added. Adding the pair's money back re-admits the residue of A1. The three tile asks and the fuse advisor are single asks.

## A3. What of the built work survives (brief item 3); all at 273079db5
| file, function | | change |
|---|---|---|
| optimizer.py: `SolveInputs.held_start`, `_held_reference`, `_stash_buffer_seed`, the held-start branch of `optimize`, `_start_gap_cost` on the shared reference | KEEP | |
| optimizer.py: `OptimizationResult` | CHANGE | one float, default nan: the mean over the horizon of the reference schedule the thermostat holds (`_baseline_targets` over `comfort_targets`, default `config.target_temp`), written on every solve where `comfort_targets` is built. Named by the fixer; this note uses no name for it. |
| price_tiles.py: `monthly_deltas` | CHANGE | the steady key's value per A2; signature unchanged (`steady` pair). The 0.05 K bound is a module constant beside `MONTH_HOURS`. Module docstring's cap paragraph: add that a schedule ask reads delivered kelvins at the thermostat's price. |
| price_tiles.py: `monthly_figure`, `specs` | KEEP | |
| whatif.py (whole module: `scratch_copies`, `WhatIfState`, `limited_answer`, `steady_pair`, the one-slot live memo, `STEADY_KEY`) | KEEP | |
| coordinator.py: `async_simulate(steady=)`, `_whatif_solve`, `_maybe_run_fuse_advisor` reading `whatif.STEADY_KEY`, the cap-tile call | KEEP | |
| payload.py, services.py, const.py | KEEP | |
| heatpump-optimizer-card.js `summary`, strings.json and en, sv, de | KEEP | |
| docs/dashboard-card.md | CHANGE | the what-if section says: a comfort change is priced as the degrees the plan would actually hold in steady state, at what a thermostat pays per degree, so it reads less than the tile where the comfort floor stops the plan following the schedule down; anything else is priced on the two steady plans' spend. |
| docs/configuration.md, docs/how-it-works.md | KEEP | |
| r10_advisor_residue.py `arm_steadysign`, the steady column of `arm_whatif` | KEEP | they read `monthly_deltas`, so they follow the amendment |
| tests/features.py: the `_st_` block | CHANGE | (a) the numbers check on `monthly_deltas` ("the steady figure is the held pair's spend plus deferred...") gains the schedule branch with stub results; (b) the 07:07 sign check stays and turns green; (c) the new every-second-hour check of A5; (d) `_st_optimizer` per A4a; (e) the fuse stub per A4b. |
| tests/structure_budgets.json (eight recorded down) | KEEP, re-measure | the result field and the branch add lines to optimizer.py and price_tiles.py; if a cap is met, pay or report before the push, never raise. |
| BLOCKED.md on the ref | DROP | |

## A4. The fixer's two side findings (brief item 4)
- **(a) Two-tank fixture.** `two_tank_modelled` (thermal_model.py:417) is `topology_layout == TOPOLOGY_TWO_TANK_4WAY`, and `topology_layout` is a derived property with no setter: the assignment in `_st_optimizer` (tests/features.py:31423 at 273079db5) cannot build one, and `_grad_parity`'s config key sets nothing. Build it the way dev/audit/harnesses/r10_sav_wood_reference.py:104 does: a throttling valve, two zones, and a configured wood tank in the config (`wood_furnace_enabled`, `wood_tank_volume`, `wood_tank_top_entity`), then assert `params.two_tank_modelled` as the precondition (that harness's line 115). Should the fixture need the layout pinned, the stored field is `topology_layout_override`. The check on it is round 2's point-2 check unchanged: on a held-start solve the start gap reads 0 within 1e-9, the start's `wood_tank_temperature` equals the measured state's, its buffer equals the valve hold, and `_initial_buffer_temp` equals that buffer. Mutants unchanged (drop `_sharing_wood_side`; skip the re-stash).
- **(b) Fuse-advisor stub.** `_fake_simulate` (tests/features.py:19261 at 273079db5) answers `monthly_settled_cost_delta` 12.0 and the advisor reads `whatif.STEADY_KEY`. A cap moves no schedule, so under the amendment the advisor's figure is still the pair's spend plus deferred: the stub answers the steady key with 12.0 and keeps the settled key at a *different* value (so a fallback to it is red), and the check reads 12.0. A second stub with no steady key publishes `cost_delta_sek_month` None (round 2's failure rule).

## A5. Evidence added (round 2's list stands)
- **Failing first, new** (tests/features.py, `_st_` block): over `_solve_coord` at hours 01..23 step 2, one frozen instant each, `async_simulate(spec, steady=True)` for the three tile asks: 24 degree figures, each strictly on the held figure's side of 0, and 12 cap figures none below -1. Red at 273079db5 (6 of 24), green at the amendment. Its null: the held figure 0 of 24 wrong in the same loop. Twelve seeding solves plus 84 what-if solves, about 70 s here: the fixer states the wall and, if `tests/features.py`'s budget refuses it, runs every fourth hour in the suite (01, 05, 09, 13, 17, 21: four of the six red rows) and keeps all twelve in the harness arm below.
- **Finder's harness.** The appendix script lands as dev/audit/harnesses/r10_advisor_steady_carrier.py (classified in tests/closure.py with the other harnesses); `arm_steadysign` stays.
- **Mutants a reviewer runs against the amendment, and what each must show.** (1) the schedule branch reverted to the pair's spend plus deferred: the new check red at 6 of 24. (2) `delivered / shift` dropped (figure = thermostat): the numbers check red; on the fixture every minus row then equals its held figure. (3) delivered read off the measured pair in place of the steady pair: round 2's spread-by-start check red. (4) the 0.05 K bound removed: the cap rows divide by 0 and the cap check is red. (5) the cap sent down the schedule branch (bound ignored, shift forced to 1): cap figures read 0.0 and the fuse check is red. (6) the reference mean taken as `config.target_temp`: on the fixture's day 21 / night 19.5 schedule the result's mean is not 21, and a day-hours-only ask reads shift 0; a check on the published mean is red.
- **Null control for the carrier claim**: the caps arm of A1 (6 to 6).

## A6. Carries added
Carry: R10-ADVISOR-STEADY-START (item worker-patch) - a perturbation patched in the test process never reaches a solve the process worker runs; the appendix script answers the worker seam in place and its first, unpatched pass is the control.
Carry: R10-ADVISOR-STEADY-START (item mixed-ask) - the mixed-ask rule of A2 is a decision of this note; the docs sentence states it, and no tile or advisor ask is mixed.
Carry: R10-ADVISOR-STEADY-START (item two-zone-mean) - delivered is read off `room_temp_trajectory`, the average room; confirm on a two-zone fixture that it is the zone mean and not one floor.
Carry: dismissed: measured and rejected in A1, restart from own end (item periodic-restart)
Carry: dismissed: measured in A1, caps move no row (item settlement-caps)

Seat tokens: not reported by the harness.

---
# The round-2 note (d2d663c32), unchanged; A1-A6 above replace its steady figure's definition in section 1, the fixture named in its point-2 check, and add to section 5

## Round 2: Design: R10-ADVISOR-STEADY-START — the what-if's steady-start estimator (#2257)

Base: 45adb0c3b425dc44e72fd9ce4ef51f480b5a3af6; every line below is cited at it. No predecessor (`after` is empty), so no handoff head. origin/main at seat time is d08ed31049cd, 36 commits ahead; `git diff --stat 45adb0c3b d08ed3104` over this note's hot files prints one changed line, in the card.
Round 2 of the note: answers the four revise points of `design-verdict/R10-ADVISOR-STEADY-START` 971a9ca7ace7 on e29f9b4a49af. By the orchestrator's ruling (mandate 6715477401, 2026-11-11) the approved `design/R10-ADVISOR-WHATIF` 3494759764e7 is this group's `async_simulate` shape. §1-§2 restate that shape at this base and mark each thing this note **adds** or **changes**; the fixer reads this note alone.

### 0. Re-measured at the base
`PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif` prints `whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0`, caps `plan 18/36 settled 1/36`, and the wrong-sign settled rows (varying 00:00 target_minus_1 +24.6, target_plus_1 -25.5). The brief's 19/36 and 3/36 did not reproduce on this box at 92588d581 either (round 1): box variance, not drift. Not re-measured this round: the round-1 spike (both plans from a held start, settled: `moves_by_start 0`, degree signs wrong 0, cap saves 0/36, cap rows in the null -0.7 to -0.3) and its wall times. That spike held at `config.get_comfort_temp`; the fixer's harness arm (§5) re-measures through the helper of §1.

### 1. Owning seam
`async_simulate` (coordinator.py:11160-11387, tests/seam_map.json:224 `core`) owns the estimator and calls:
- **optimizer.py, the held start (taken from WHATIF; replaces round 1's public wrapper).** `SolveInputs` (optimizer.py:2450-2458, a frozen `kw_only` dataclass) gains a held-start flag, default False; `optimize` (3657) resolves it. One new method, the held-reference helper, taking `(state, weather, comfort_targets)`, is exactly the expression at optimizer.py:5751-5754: `_sharing_wood_side(_thermostat_held_state(self.model, state, weather, _baseline_target(comfort_targets, 0, self.config.target_temp)), state)`. `_start_gap_cost` (5731-5762) calls it in place of those lines; the held-start branch of `optimize` calls it to rebind `initial_state` after `_build_comfort_bounds` returns `comfort_targets` (3789-3790) and before `_solve` builds `_Horizon` (3833-3834). **Revise point 1:** the target is the solve's own `comfort_targets` at step 0, so weekday overrides and the away band (`_whatif_banded`) are in it by construction; no caller derives a target and `config.get_comfort_temp` is not read.
- **The tanks (revise point 2; decided here, the fixer has no choice left).** Behind a throttling valve the steady plan starts with the **buffer at the valve hold** when the held need is positive (`_thermostat_held_state`, optimizer.py:612) and as measured otherwise, and the **wood tank as measured**: `_sharing_wood_side` (558-560) puts back what `_NO_WOOD_TANK_C` (555, written at 619) removed. Both sides start from the same measured wood tank, so stored wood heat is on both. Consequence, stated in the docs: on a two-tank install the figure is invariant to the room and slab start but not to the wood tank's charge, which no schedule holds. `_initial_buffer_temp` (written at 4083 in `_stash_price_horizon`, called at 3725; read at 5430 in `_settlement_caps`) is re-stashed from the rebound state: the write at 4083-4088 is extracted to a stash helper called from both places. `_compute_baseline_power` (5591) keeps its bare `_thermostat_held_state`. Flag False: byte-identical.
- **price_tiles.py, the figure.** `price_tiles.monthly_deltas` (94-109) gains an optional steady pair and then emits the steady key (WHATIF's name: monthly_steady_cost_delta): per_month of what-if spend + deferred + wood, less live spend + deferred. Pure.
- **Added by this note: where the memo lives.** WHATIF caches the live steady solve but names no home, and `python3 tests/structure.py` reads `coordinator_attrs`, `max_class_loc` and `class_excess_loc` all at their caps at this base, so a new coordinator attribute is refused. One per-coordinator what-if state object, in a new module, replaces `_last_simulation` and `_simulation_cache` (coordinator.py:4029-4030; attrs down by one), holds the one-slot memo, and takes the rate-limit gate (11187-11196) moved verbatim. `_start_gap_cost` shrinking and one extracted solve-inputs builder called three times pay the optimizer and coordinator class lines; if they do not, that is a design finding reported before the push, never a raise.

### 2. Shape
`async_simulate(overrides, *, limited=True, base=None, steady=False)`. **Changed from round 1: the default is False** (WHATIF's), so doubles, harnesses and `_whatif_solves` (tests/features.py:31179) keep their solve counts. With `steady=True`, after the measured what-if solve (`_await_optimize`, coordinator.py:11271) has returned, two more solves run with the held-start flag: the live configuration and the what-if one, same horizon, solve instant and mode block.

**Revise point 3, each stated:**
- *Instance.* The live steady solve runs on a fresh scratch `HeatPumpOptimizer(ThermalModel(copy.deepcopy(params)), copy.deepcopy(config))` built from the `config, params, state` async_simulate already holds (11211-11215), copied before any override. Never `SolveRecord.optimizer()` (2396-2397), never `_warm_seeded` (2354-2374).
- *Await seam.* Both steady solves go through `_await_off_loop` (2142-2164): `ProcessWorkerUnavailable` falls to the executor (2160-2162) and the #783 streak is untouched. `_await_optimize` (2309-2351; bump 2340, clear 2349) is called once per what-if, as today.
- *Results.* The steady results and the memo feed only the answer: never assigned to `_optimization_result` (one writer, 6422), never a seed, never a `SolveRecord`. The memo holds the object `self._optimization_result` refers to when async_simulate reads it (or `base`), plus the solve instant, and hits on `is`.
- *Failure.* The pair has its own `except Exception`, which also takes the `ProcessWorkerTimeout` that `_await_off_loop` re-raises (2157-2159): the steady key is dropped, nothing is memoised, and the rest of the answer is returned. Then the panel shows no money line; `price_tiles.monthly_figure` (price_tiles.py:140-143) returns None for a cap and never falls back to `monthly_settled_cost_delta`; the fuse advisor publishes `cost_delta_sek_month` None (payload.py:393 already allows it). If the measured solve fails first, the existing `except` (11329-11331) returns the error answer and no steady solve runs.

| caller | steady | reads after | reason |
|---|---|---|---|
| card, `handle_simulate_plan` (services.py:767) | True | the steady key, in `summary` (heatpump-optimizer-card.js:13318, today `result.monthly_cost_delta`) | owner's ruling |
| fuse advisor (`_maybe_run_fuse_advisor`, call coordinator.py:8971, `limited=False`, base) | True | the steady key, read directly into `cost_delta_sek_month` (9003) | a cap must not save; settled saves 1/36 |
| cap tile (`_maybe_refresh_price_tile`, call 10698) | `"power_cap_kw" in overrides` | `monthly_figure` picks the steady key | as above; shares the record's memo |
| degree tiles (same call) | False | `monthly_held_cost_delta`, unchanged | spread 0.00, sign right; re-pricing re-opens #2572/#2834 |
| `_solver_smoke` (debugger.py:323) | False | `cost_delta`, unchanged | it times one solve |

`monthly_cost_delta`, `monthly_held_cost_delta` and `monthly_settled_cost_delta` keep their meaning (a service response is a published contract). No what-if TypedDict exists and none is added; `PriceTile.monthly_cost_delta` (payload.py:334) keeps its key, a cap tile's value becoming the steady mean. **Decided here (kept from round 1):** tile and panel differ by design, about -54 against -31 per degree in the null: the tile prices a degree held by a thermostat, the panel the plan. Invariants: the slot is spent once, before the first solve (#1448, #1753); `limited=False` never touches slot or card cache; overrides reach only scratch copies (#240); an error answer carries no figure.

**Cost.** User what-if: 1 solve before; after, 3 on the first call against a scheduled plan and 2 on a memo hit, at most one start per `SIMULATE_MIN_INTERVAL_SECONDS`. Degree tile 1 (unchanged). Cap tile and fuse advisor 2 or 3 per scheduled record, sharing the memo: the cap tile every third interval, the fuse advisor weekly. Earlier measurements on the cloud box, 24 h at 15 min: measured solve mean 623 ms; steady pair mean 1.02-1.20 s, max 1.84 s. The fixer measures solve count (a counter wrapping both await seams) and wall per what-if before and after, and states the Pi bound as count times per-solve wall.

### 3. Alternatives (lost)
- **Round 1's public wrapper holding at `config.get_comfort_temp`**: a second expression of `_start_gap_cost`'s reference; the gap is non-zero wherever they differ, and it drops the wood side.
- **Memo on a new coordinator attribute, or inside the `_simulation_cache` dict**: the first is refused by `coordinator_attrs`; the second mixes a solver result into the answer the limiter returns to the card.
- **State object in price_tiles.py** (no new module): that module is pure figures; it would gain mutable per-coordinator state and the rate limiter.
- **Steady unsettled** (3/12 degree signs wrong, 30/36 caps save, WHATIF §0); **panel reads the held figure** (0 for every cap); **steady default True** (adds solves to every caller passing nothing); **disclosure only** (owner, 2026-11-01).

### 4. Sibling sites (revise point 4)
`git grep -n "monthly_cost_delta\|monthly_settled_cost_delta\|monthly_held_cost_delta\|cost_delta_sek_month\|async_simulate(" -- custom_components docs tests/entities.py`: the callers and readers of §2; price_tiles.py:105-107, 142, 188; card 9966/9979/9980 (PriceTile, stays) and 13318. The fuse figure changes meaning (settled to steady) under an unchanged key at payload.py:393 (its comment is updated), store.py:448 (numeric schema, no change) and tests/entities.py:467 (a fixture value, no change).
Cost claims, found by `git grep -n -i "extra solve\|full solve" -- docs custom_components`, all false for a cap tile after this change and all rewritten:
- docs/configuration.md:498 "Off by default because each tile is a full extra solve." becomes "Off by default because each tile costs extra solves: one for a degree tile, up to three for the power-cap tile."
- docs/how-it-works.md:1278 "so the whole set costs at most one extra solve per interval" becomes "so a refresh costs one extra solve for a degree tile and up to three for the power-cap tile".
- strings.json:914 `price_tiles_enabled` ("a full extra solve of real CPU") and line 914 of translations/en.json, sv.json and de.json: the same sentence as configuration.md.
docs/how-it-works.md:115 ("extra full solve", the multi-start count) is another subject and stays.

### 5. Evidence plan, by file
- **Failing first** (tests/features.py, beside `_whatif_solves`): (a) the steady key from `async_simulate(..., steady=True)` spreads 0 over the finder harness's three starts (dev/audit/harnesses/r10_advisor_residue.py:106 "for room, slab in deg.STARTS"); red at the base (key absent; `monthly_cost_delta` moves 24/24). (b) sign: a degree warmer > 0, cooler < 0, no cap below -1 (0 fails on solver noise, §0). (c) tests/card.mjs: `summary()` renders money only from the steady key, with the steady-state wording; no key or no draft result renders no money and no caveat.
- **Point 1 checks.** On a held-start solve, `_start_gap_cost` (wrapped to record its return) reads 0 within 1e-9 at the three starts, on a weekday-override config and with away on; and the start the solve used has every zone at `_baseline_target(comfort_targets, 0, ...)` of that solve. Mutants: the held-start branch passing `self.config.target_temp` in place of `comfort_targets` (first check red on the override and away configs); `+ 0.5` inside the helper (second check red). **Changed from WHATIF:** its `+ 0.5` mutant was assigned to the gap check, but with one helper on both sides the gap stays 0 under it (the helper is idempotent), so it needs the second check.
- **Point 2 check.** Fixture from `_grad_parity(True, wood=True, valve="manual")` (tests/features.py:6386) with `two_tank_modelled` and `buffer_is_store` asserted True as a precondition: the gap reads 0, the start's `wood_tank_temperature` equals the measured state's, its buffer equals `valve_hold_temperature`'s, and `_initial_buffer_temp` equals that buffer. Mutants: drop `_sharing_wood_side` from the helper (wood reads 0.0); skip the re-stash.
- **Point 3 checks, each with its mutant.** Every optimizer passed to `_await_off_loop` `is not` any instance `SolveRecord.optimizer()` or `_warm_seeded` returned in the test (mutant: live side on `_warm_seeded(self, record.optimizer())`). After a steady what-if `coord._optimization_result` is the same object with an unchanged `power_schedule` (mutant: assign the memo's result). With the worker raising `ProcessWorkerUnavailable`, one what-if bumps the streak by exactly 1 (mutant: pair through `_await_optimize`). With `ProcessWorkerTimeout` on the pair only: the answer carries `monthly_cost_delta` and no steady key, `monthly_figure` on the cap spec is None, the fuse cost is None, the memo is empty (mutants: `monthly_figure` falling back to settled; fuse reading settled; memoising a failed pair).
- **Cost and callers.** Solve counter over both seams: 3 then 2 on a repeated user what-if; a tile rotation counts 2 steady solves on the cap spec and 0 on the degree specs; "5 calls, 1 solve" (features.py:31213) holds; the fuse `cost_delta_sek_month` equals the answer's steady key. Mutants: `steady=True` on every tile spec; memo ignoring the record; live side from the measured state; deferred term dropped from the steady key; card falling back to `monthly_cost_delta`.
- **Finder's harness.** `arm_whatif` (dev/audit/harnesses/r10_advisor_residue.py:92) gains a steady column solved with the held-start flag and read from `price_tiles.monthly_deltas`, no re-implemented formula; run at the base and the head.
- **Null control.** Held spread 0.00 on every row; the null series reads one steady figure at all starts, before and after; the idle panel renders nothing; the two-tank precondition assert is that fixture's own null.
- **Goldens.** `git grep` finds no monthly key under tests/golden; if the cap tile or fuse figure moves a fixture, `GOLDEN_MODE=drift` and a claim per `claim-files.md`, never a re-record.
- **Docs.** docs/dashboard-card.md:619-622: the one-off sentence becomes "that panel prices the change in steady state, both plans started as if each schedule had been held, so its figure leaves out the one-off coast or heat-up a change starts with"; the what-if section (451) calls the money line a steady-state monthly estimate, says why it is about half the tile's, and carries the wood-tank sentence of §1. Card strings in en, sv and de.

### 6. Hot files, position
coordinator.py, optimizer.py, price_tiles.py, payload.py, heatpump-optimizer-card.js, strings.json and the three translations, docs/dashboard-card.md, docs/configuration.md, docs/how-it-works.md, tests/features.py, tests/card.mjs, r10_advisor_residue.py, tests/closure.py and the new module. After: none. R10-WHY-NOW-WIDGET holds the card and coordinator.py hot; the fixer rebases on whichever merges first and re-runs `fixer.md` steps 2-8. Closes #2257; `fixes` must list 2257. `design/R10-ADVISOR-WHATIF` is retired at closeout; nobody builds from it.

### Notes for the fixer
Carry: R10-ADVISOR-STEADY-START (item recite) - every line here is at 45adb0c3b; re-cite at your merge base.
Carry: R10-ADVISOR-STEADY-START (item fuse-key) - the fuse advisor reads its key directly at coordinator.py:9003; changing `monthly_figure` alone does not move it.
Carry: R10-ADVISOR-STEADY-START (item fuse-none) - confirm the card's fuse row renders a None `cost_delta_sek_month` as no money, with a test; this note did not read that renderer.
Carry: R10-ADVISOR-STEADY-START (item tile-callsite) - the three tiles share the one call at coordinator.py:10698; pass `steady` per spec.
Carry: R10-ADVISOR-STEADY-START (item memo-key) - never key the memo on `id(...)`, and never on the object a solve hands back: `_optimization_result` is assigned a `replace(...)` copy (coordinator.py:6422).
Carry: R10-ADVISOR-STEADY-START (item test-attrs) - tests write the two attributes directly (tests/features.py:19280-19281, 26068-26069, 31080, 31198; tests/dst_checks.py:1831); the state object edits each, and the moved gate still spends the slot before the first solve.
Carry: R10-ADVISOR-STEADY-START (item stubs) - tests/debug_collect.py and dev/audit/harnesses/r9_dbg2_selftest_price.py mimic the async_simulate signature; doubles replacing `_await_optimize` in tests/config_flow_steps.py miss the steady pair, and `WORKER_SEAMS` in tests/deployment_shape.py already lists `_await_off_loop`.
Carry: R10-ADVISOR-STEADY-START (item locales) - `whatif.same_cost`, `whatif.cheaper_per_month`, `whatif.dearer_per_month` in en, sv and de (card 615-619, 1479-1485, 2239-2241).
Carry: R10-ADVISOR-STEADY-START (item module-docs) - the new module is a line in docs/architecture.md's tree (137 is price_tiles.py's), which `design/R10-ARCH-DOCS` holds hot; classify the module in tests/closure.py and serialise the docs line with that group.
Carry: dismissed: decided in section 1, wood tank as measured (item wood-start)
Carry: dismissed: decided in section 1, target from comfort_targets (item away-target)
Carry: dismissed: decided in section 2, tiles stay held (item tile-panel-gap)
Received: carry 0 of this group (from R10-ADVISOR-WHATIF, #2963); this note implements all of it.

Seat tokens: not reported by the harness.

---
# Appendix: the measuring script, as run (to land as dev/audit/harnesses/r10_advisor_steady_carrier.py)

Run from the tree root at 273079db5 or later: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_carrier.py <arm> [out.json]`, arm one of none, caps_report, caps_all, caps_common, floor, basin, refill_mean, refill_max, amend1, amend2 (the last two are the rejected restart). It prints one RESULT line per pass.

```python
"""Scratch probe: the steady figure's sign on the coordinator fixture, with one perturbation.

Run from the worktree root:
  PYTHONPATH=tests/hastub:tests:custom_components python3 probe.py <pert> [out.json]
pert: none | caps_report | caps_all | caps_common | floor | basin | refill_mean | refill_max
"""
from __future__ import annotations

import ast
import asyncio as _asyncio
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

import numpy as np
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass, FakeState, with_config
from homeassistant.util import dt as dt_util

import heatpump_optimizer.coordinator as cmod
import heatpump_optimizer.optimizer as omod
from heatpump_optimizer import price_tiles, whatif
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

PERT = sys.argv[1] if len(sys.argv) > 1 else "none"
OUT = sys.argv[2] if len(sys.argv) > 2 else None

# The fixture, sliced out of tests/features.py by name: no check runs.
_src = Path("tests/features.py").read_text()
_want = {"_SolveHass", "_solve_coord", "_solve_record_now"}
_ns = globals()
for node in ast.parse(_src).body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in _want:
        exec(compile(ast.Module([node], []), "features-slice", "exec"), _ns)  # noqa: S102
        _want.discard(node.name)
assert not _want, _want

Opt = omod.HeatPumpOptimizer


async def _no_worker(hass, fn, *args):
    return fn(*args)  # in-process, so a perturbation patched here reaches the solve


cmod._await_process = _no_worker
_flag = {"settling": False}
_real_caps = Opt._settlement_caps
_real_settle = Opt._settle_horizon
_real_def = Opt._deferred_energy_cost
LIVE_TARGET = 21.0


def _settle(self, h, weather, reference_targets, baseline_end, optimized_end, *a, **k):
    self._probe_end = optimized_end
    a = (h, weather, reference_targets, baseline_end, optimized_end, *a)
    _flag["settling"] = True
    try:
        return _real_settle(self, *a, **k)
    finally:
        _flag["settling"] = False


def _caps(self, *a, **k):
    if PERT == "caps_common" and _flag["settling"]:
        # both sides settled at the live schedule's caps
        keep = self.config.target_temp
        self.config.target_temp = LIVE_TARGET
        try:
            return _real_caps(self, *a, **k)
        finally:
            self.config.target_temp = keep
    caps = _real_caps(self, *a, **k)
    if PERT == "caps_all" or (PERT == "caps_report" and _flag["settling"]):
        caps = {**caps, "room": 99.0, "slab": 99.0}
    return caps


def _deferred(self, baseline_end, optimized_end, prices, *a, **k):
    if PERT.startswith("refill_") and _flag["settling"]:
        f = {"refill_mean": np.mean, "refill_max": np.max, "refill_min": np.min}[PERT]
        prices = np.full_like(np.asarray(prices, dtype=float), float(f(prices)))
    return _real_def(self, baseline_end, optimized_end, prices, *a, **k)


_real_optimize = Opt.optimize
SOLVES = {"n": 0}


def _optimize(self, *a, inputs=None, **k):
    from dataclasses import replace as _rep
    SOLVES["n"] += 1
    result = _real_optimize(self, *a, inputs=inputs, **k)
    if PERT.startswith("amend") and inputs is not None and inputs.held_start:
        for _ in range(int(PERT[5:6])):
            SOLVES["n"] += 1
            result = _real_optimize(self, *a, inputs=_rep(inputs, held_start=False, state=_rep(self._probe_end)), **k)
    return result


Opt.optimize = _optimize
Opt._settle_horizon, Opt._settlement_caps, Opt._deferred_energy_cost = _settle, _caps, _deferred

# Basin: the what-if's held solve gets the live held plan as an extra candidate
# and the live one the what-if's (second pass), through the optimizer's own
# previous-plan seam.
_seed = {"plan": None}
_real_ws = Coord._whatif_solve


def _whatif_solve(self, overrides, config, params, state, horizon, solve_at, held_start):
    opt, inputs, extra = _real_ws(self, overrides, config, params, state, horizon, solve_at, held_start)
    if PERT == "basin" and held_start and _seed["plan"] is not None:
        opt._prev_shipped_plan = np.asarray(_seed["plan"], dtype=float)
    return opt, inputs, extra


Coord._whatif_solve = _whatif_solve

_cap = {}
_real_md = price_tiles.monthly_deltas


def _md(live, sim, extra, horizon_hours, steady=None):
    _cap["last"] = (live, sim, steady)
    return _real_md(live, sim, extra, horizon_hours, steady)


price_tiles.monthly_deltas = _md


def _res(r):
    if r is None:
        return None
    room = r.room_temp_trajectory
    return {
        "spend": r.predicted_cost, "deferred": r.deferred_energy_cost, "baseline": r.baseline_cost,
        "obj": r.objective_value, "kwh": float(np.sum(r.power_schedule)) * 24.0 / len(r.power_schedule),
        "room0": room[0], "roomN": room[-1], "room_min": min(room), "room_mean": float(np.mean(room)),
        "slab0": r.slab_temp_trajectory[0], "slabN": r.slab_temp_trajectory[-1],
        "power": [round(float(x), 4) for x in r.power_schedule],
        "room": [round(float(x), 3) for x in room],
    }


async def _one(hour, extra):
    coord = _solve_coord()  # noqa: F821
    if extra:
        with_config(coord, extra)
        getattr(coord, "_ctx", coord)._opt_config.min_temp = extra["min_temperature"]
    coord._fuse_advisor_at = dt_util.now()
    await coord.async_run_optimization()
    record = _solve_record_now(coord)  # noqa: F821
    asks = price_tiles.specs(record.config, record.params.max_electrical_power)
    print("CONFIG", hour, "min_temp", record.config.min_temp, "target", record.config.target_temp, "horizon", record.config.horizon_hours)
    rows = []
    for name, overrides in asks:
        passes = 2 if PERT == "basin" else 1
        best = None
        for p in range(passes):
            whatif.state(coord).last_at = None
            if PERT == "basin":
                whatif.state(coord).live_steady = None
                # pass 0 unseeded; pass 1: both sides seeded with the other side's pass-0 plan
                _seed["plan"] = None
            if PERT == "basin" and p == 1:
                # seed live with the what-if plan, then the what-if with the live plan
                live_plan, sim_plan = best["live_s"]["power"], best["sim_s"]["power"]
                order = iter([sim_plan, live_plan])
                real = _real_ws

                def seeded(self, o, c, pa, s, h, at, hs, _order=order):
                    opt, inputs, ex = real(self, o, c, pa, s, h, at, hs)
                    if hs:
                        opt._prev_shipped_plan = np.asarray(next(_order), dtype=float)
                    return opt, inputs, ex

                Coord._whatif_solve = seeded
            t0 = time.monotonic(); n0 = SOLVES["n"]
            answer = await coord.async_simulate(dict(overrides), steady=True)
            wall = time.monotonic() - t0
            if answer.get("monthly_held_cost_delta") is None:
                print("ANSWER", {k: v for k, v in answer.items() if not isinstance(v, (list, dict))})
                raise SystemExit(2)
            Coord._whatif_solve = _whatif_solve
            live, sim, steady = _cap["last"]
            row = {
                "hour": hour, "ask": name, "pass": p, "wall_s": round(wall, 3), "solves": SOLVES["n"] - n0,
                "steady": answer.get(whatif.STEADY_KEY), "held": answer.get("monthly_held_cost_delta"),
                "settled": answer.get("monthly_settled_cost_delta"), "plan": answer.get("monthly_cost_delta"),
                "live": _res(live), "sim": _res(sim),
                "live_s": _res(steady[0]) if steady else None, "sim_s": _res(steady[1]) if steady else None,
            }
            best = best or row
            rows.append(row)
    return rows


def main():
    extra = {"min_temperature": 12.0} if PERT == "floor" else None
    allrows = []
    for hour in range(1, 24, 2):
        dt_util.freeze(dt_util.now().replace(hour=hour, minute=7, second=0, microsecond=0))
        try:
            allrows += _asyncio.run(_one(hour, extra))
        finally:
            dt_util.freeze(None)
    last = max(r["pass"] for r in allrows)
    for p in range(last + 1):
        rows = [r for r in allrows if r["pass"] == p]
        deg = [r for r in rows if r["ask"].startswith("target_")]
        cap = [r for r in rows if not r["ask"].startswith("target_")]
        want = {"target_minus_1": -1.0, "target_plus_1": 1.0}
        wrong = [r for r in deg if r["steady"] is None or r["steady"] * want[r["ask"]] <= 0.0]
        held_wrong = [r for r in deg if r["held"] * want[r["ask"]] <= 0.0]
        settled_wrong = [r for r in deg if r["settled"] * want[r["ask"]] <= 0.0]
        plan_wrong = [r for r in deg if r["plan"] * want[r["ask"]] <= 0.0]
        for r in deg + cap:
            print(f"ROW {PERT} pass {p} {r['hour']:02d} {r['ask']:15s} steady {r['steady']!s:>8} held {r['held']:+8.1f} "
                  f"settled {r['settled']:+8.1f} plan {r['plan']:+8.1f} wall {r['wall_s']} solves {r['solves']}")
        print(f"RESULT {PERT} pass {p} degree rows {len(deg)} steady_wrong {len(wrong)} "
              f"({', '.join(f'{r['ask'][7:]}@{r['hour']:02d}' for r in wrong)}) held_wrong {len(held_wrong)} "
              f"settled_wrong {len(settled_wrong)} plan_wrong {len(plan_wrong)} | cap rows {len(cap)} "
              f"steady saving(<-1) {sum(1 for r in cap if r['steady'] is not None and r['steady'] < -1.0)} "
              f"settled saving {sum(1 for r in cap if r['settled'] < -1.0)} plan saving {sum(1 for r in cap if r['plan'] < -1.0)}")
    if OUT:
        Path(OUT).write_text(json.dumps(allrows))


main()
```
