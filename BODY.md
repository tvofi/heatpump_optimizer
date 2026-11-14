R10-DUTY-SWITCH-RESTART-LEARNING-PR-B, second pull request: the arbiter's split of a step serving both duties reads the learned estimate, as the group's ruling on rule c states. With thanks to Bankaifan, whose pull request 3420 found the duty-switch restart; its split function (order latched per step, the whole step given to the first duty when the second share is shorter than the minimum split plus the learned off time) is the starting point of `DutySwitchLearner.split` and `duty_switch.both_step_duty`, narrowed here by the ruling: the whole-step rule applies only where the plan's next step serves the denied duty, and `n` has a ceiling.

- **The reader and its first caller** (roster carry 0, item 1b22f416). `duty_switch.both_step_duty` takes the pump's record, the step's start, the plan's split and the plan's next step; `_share` in `pump_arbiter.py` delegates to it. The decision is `duty_legs.both_step_legs` under the leg rule `DutySwitchLearner.split` returns, latched on the record per step start; a record not yet loaded splits as before and latches nothing. The arbiter holds no learned state.
- **The rule.** Space goes first only where hot water to space is the one usable direction. The first duty keeps the whole step only when the switch into the second is usable, the second share is under `SPLIT_MIN_MINUTES` plus that direction's median off time, and the next step serves the second duty (or both). With no usable direction the decision is hot water first, not whole: today's split.
- **`n` has a ceiling**, `N_CAP` (twice `N_ON`), held at each booking and on each pass's decay by scaling both counts alike, so `p` does not move. A latched direction with no further episode unlatches just past two half-lives, and the default split re-tests it (verdict item n11).
- **Factory reset voids the duty-switch store** (roster carries 1 and 6, items 3c666f5b and 893e80d2), under the orchestrator's ruling under mandate 6715477401 of 2026-11-12T19:51:09Z. The store joins `_restored_stores` and `_FACTORY_VOID` as voided whole, so the existing mechanism also puts it in the undo point and the undo restores it. The entry is set up again with a new coordinator, whose record loads the voided store empty: that is the in-memory learner emptied in the reset's own step. The planner of R10-DUTY-SWITCH-PLANNER-PRICE, now on main, reads the same record (`planner_fields`), so after a reset it prices from the voided record too. A reversal is the `("duty_switch", None)` row, its `_FR_STORES` line and the reset check.
- **What the reader reads** (roster carries 4 and 5, items 90bc5153 and d088605d). Only the latches and the median off time. It reads no `n`, tally, `span_days` or published key, so a `span_days` of 0 beside non-zero tallies, or evidence accruing faster on one set-point unit, moves the split only through a latch.

**Reconcile round (early, owner ruling 2026-11-14).** This branch contains PR 3561's head 30b069508f194240f90ddd05cb5cfee0613814e1 (R10-HOTFIX-FLOW-SETPOINT-STUCK), merged first, then origin/main at 50373173d486faf394b24637c177ab38b691b394, which merged clean after it. If 3561's head moves before it merges, the successor merges the new head and nothing else.

- **One leg rule for planner and arbiter** (carry c3ad1545, binding the branch that merges second; this one). R10-DUTY-SWITCH-PLANNER-PRICE, now on main through 3561's head, made `duty_legs.py` the owner of the both step's legs; this branch's `split` put a learned order and a whole-step decision in the arbiter. Union: `duty_legs.leg_rule(stop_probability, off_seconds)` returns `(first duty, minutes the second share must clear past SPLIT_MIN_MINUTES, or None)`; `both_step_legs` and `leg_ends` take that rule (and the next step's duty, `leg_ends` reading it from the plan itself); `DutySwitchLearner.split()` is `leg_rule(*planner_pairs())`, the very pairs `planner_fields` hands the solve, so the planner prices the legs the arbiter serves. `switch_weights_batch` weighs the inside switch in the rule's direction, `availability` charges a two-leg step only when hot water goes first, and `switch_ban` under space first bans only the step before heating. With no stop priced the rule is `DEFAULT_RULE` and every array is main's: no golden moves.
- **Order in `pump_arbiter.py`.** 3561 owns the set-point-stuck behaviour (its `_lead_mode`, `_step_duty` and `_served` helpers, kept whole); this group owns the duty-switch delegation inside `_share`, which `_served` calls after the block. Order per pass: planned duty, block, hot-water lease (`_step_duty`), then `_share` → `duty_switch.both_step_duty` → `duty_legs.both_step_legs`, then the block again (`_served`).
- **Superseded deliberately.** main's `if self.n > N_CAP` booking cap gives way to this branch's comparison-free `min()` (reviewed at 29370fdb), also held on decay, so its two ledger pins (`Direction.book` GUARD_OFF and CMP_BOUND 3e106b06) are removed as stale. main's `_share` body (legs read inline) gives way to the delegation. Three planner-price checks that assumed hot water first under the hot-water-to-heating pair alone keep their assertion under a pair priced both ways and state the space-first outcome beside it.

The group's roster carries, by index:

- Carry 0 (item 1b22f416): implemented; `both_step_duty` is the reader and `_share` its first caller, and `dead_top_level_symbols` does not move.
- Carry 1 (item 3c666f5b): implemented per the ruling in Carry 8; the store is voided by a factory reset.
- Carry 2 (item ef5d3875): settled in part 1 (`N_ON` is a decayed weight); the split reads the latch it sets and adds nothing.
- Carry 3 (item c7d068a1): settled in part 1 (the publication's resolution); the ceiling now also bounds the published `n` at 10.
- Carry 4 (item 90bc5153): implemented; the reader reads no `span_days` and no published key, pinned by "the split reads the latches and nothing published…".
- Carry 5 (item d088605d): implemented; the reader reads no `n`, so a unit gating fewer switches moves the split only through a latch, same check.
- Carry 6 (item 893e80d2): implemented by the void; the planner's read (`planner_fields`, now on main) reads the same record, voided alike.
- Carry 7 (item b30e2dd2): implemented in this round: the order and the whole-step rule are `duty_legs.leg_rule`, read by `both_step_legs`, `leg_ends`, the weights, the charge and the ban; the harness mutant "arbiter: the share serves the legs in reverse order", re-anchored on `both_step_duty`, turns 3 section checks red.
- Carry 8 (the orchestrator's ruling of 2026-11-12T19:51:09Z): implemented with its owed failing-first test and its restart null control.
- Carry 9: as Carry 6; this pull request voids the store, so the planner's read is of a voided record after a reset.
- Carry 10: as Carry 7, implemented in this round.

Alternatives. Keeping the time-share in `_share` and passing the coordinator to the reader: `tools/audit/archscore/score.py --diff` read that as `coord_footprint` 2506 -> 2517, refused by the gate, and it kept learned decisions in a coordinator-handed function. Putting the order latch on `ArbiterState`: the approved design keeps learned state off the arbiter's record. Voiding the store by a separate `duty_switch` call in the reset: that is a parallel path beside `_FACTORY_VOID`, and the undo would not restore it.

## Head

`5e1fac78adb59b0d5b4b86ffc7dce58f55936155`, on `handoff/r10-duty-switch-restart-learning-pr-b-p2`: the PR head 3ab3d5b5ab4b21d147977652f14d5cf0de280006 with origin/main 237fad44532d1927cf65612d395cc5833c60ce99 merged into it (no rebase). Main had moved by PR 3562 (round-10 user-facing strings), which conflicted with this head in four files; everything else merged clean (`tests/closures.json` by the ledger driver, `tests/features.py` auto-merged).

- **The conflict.** One key, `options.step.entities.sections.indoor.data_description.space_setpoint_unit`, in `strings.json` and in `translations/en.json`, `de.json` and `sv.json`. Read against the merge base 0f37833e2194739b431656a70c652b0679c8fa58: this head changed its last sentence from "this integration never recommends a space set-point" to "the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one" (with the German and Swedish equivalents, and sv "framledningsentitet"); PR 3562 made the same change word for word and appended one sentence, "With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity." (likewise in de and sv). The union is main's text, taken in all four files; no wording of this head is lost, and the appended sentence agrees with this head's `space_setpoint_entity` text.
- **Read back.** The four files after the merge are byte-identical to origin/main's; their flattened key sets agree (1509 keys each, including main's new `issues.dhw_legionella_off_step` title and description), and `strings.json` equals `en.json`.
- **Body.** The previous body carried a spliced duplicate (a broken "## Red checks`)." heading followed by an older copy of Mutation proof, Null control, Figures and Unpinned sites, whose sites the reviewed head 56b43dea already pinned); it is dropped, so each section appears once. No other section changes. The merge leaves `duty_switch.py` and `duty_legs.py` as this head had them and `_share`'s delegation in `pump_arbiter.py` untouched; main's own changes to `pump_arbiter.py`, `optimizer.py`, `coordinator.py` and the card auto-merged beside them, and the scoped gate below reran what they reach.

Before this merge: `3ab3d5b5ab4b21d147977652f14d5cf0de280006` was this PR's head, its code already in it and main at that time merging cleanly, so the orchestrator's script set the body without a push.

b142bcaacee1781eeb99086587c644cb823bd34f, on `handoff/r10-duty-switch-restart-learning-pr-b-p2`: the PR head 56b43dea847ee980c67604ccd7798dc88084d071 (the reviewed head 29370fdbb59aeb18da82ebe9612e7c036e9dc29c, a merge of main at the v7.1.13 stamp, the delivery row and "ci: pin killed mutants"), merged with PR 3561's head 30b069508f194240f90ddd05cb5cfee0613814e1, then origin/main 50373173d486faf394b24637c177ab38b691b394.

Delta against the reviewed head 29370fdb, file by file (this round's own changes; the rest is main's and 3561's):

- `custom_components/heatpump_optimizer/duty_legs.py`: `LegRule`, `Legs`, `DEFAULT_RULE`, `leg_rule`; `both_step_legs` and `leg_ends` take the rule and the next step; `switch_weights_batch`, `switch_weight`, `availability`, `switch_ban` take the rule.
- `custom_components/heatpump_optimizer/duty_switch.py`: `split()` returns the leg rule from `planner_pairs()`; `planner_pairs` and `planner_fields` (main's) kept; `both_step_duty` takes the step's two draws, width and next duty and latches the legs; the record's `order` holds legs; docstrings merged.
- `custom_components/heatpump_optimizer/pump_arbiter.py`: `_share` delegates to `both_step_duty` with `PLAN_STEP_MINUTES`; 3561's `_lead_mode`, `_step_duty`, `_served` kept; the module docstring names the leg rule.
- `custom_components/heatpump_optimizer/optimizer.py`: `_leg_rule(opt)` from the priced pairs, passed to the availability, the switch cost, the candidate gate and the ban.
- `custom_components/heatpump_optimizer/coordinator.py`: 3561's `supply_hold` import beside `duty_switch`.
- `tests/features.py`: the readers check names the coordinator's `planner_fields` and `record_for`; the censored-bound check reads the leg rule; new checks "planner and arbiter read one leg rule…" and "one leg rule in the leaf…"; three planner-price checks re-stated (above); the price section's fake coordinator carries an unloaded record.
- `dev/audit/harnesses/r10_duty_switch_price_section.py`: four mutants re-anchored on the merged lines.
- `tests/mutation_ledger/`: fifteen stale pins removed (`Direction.book` 3e106b06 twice, and the thirteen listed under `## Red checks`).

## Mutation proof

This round, each applied alone to `duty_legs.py`, both section harnesses run, restored after:

- `switch_ban` ignoring the rule: 2 of 95 planner-price checks fail.
- `leg_ends` ignoring the rule's order: 1 of 71 duty-switch and 5 of 95 planner-price checks fail.
- No whole step in `leg_ends`: 1 of 71 fails ("planner and arbiter read one leg rule…").
- The inside switch always weighed hot water to heating: 2 of 95 fail.
- `availability` charging every two-leg step: 4 of 95 fail.
- `leg_rule` never serving space first: 3 of 71 and 3 of 95 fail.
- `r10_duty_switch_price_section.py --mutants` on the four re-anchored mutants: 3, 3, 1 and 3 red, control 0 red, `mutants_not_killed=0`.

From the reviewed head (unchanged in kind; `split`'s order and whole-step mutants now land on `leg_rule` and `both_step_legs`):

Each mutant applied alone, then `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`, restored after (70 section checks at the head):

- `split` order: space first whenever hot water to space is usable (`"dhw_space" in usable`): 6 fail, among them "null control, an empty learner…", "the first duty keeps the whole step only when…", "the split is latched per step…", "a record whose store is not read yet…" and "with the whole-step rule active…" (with both directions usable, space now goes first).
- `split` order: space first where only space to hot water is usable: 2 fail, "where only hot water to space is usable the both step serves space first…" and "the split reads the latches and nothing published…".
- The next-step condition dropped: 1 fails, "the first duty keeps the whole step only when…".
- The off time dropped from the whole-step bound: 5 fail.
- The whole-step bound made inclusive (`<=`): 1 fails, "the first duty keeps the whole step only when…" (its 150 s row sits on the bound).
- The ceiling at booking dropped (`scale = 1.0`): 1 fails, "n has a ceiling…".
- The share's end made inclusive (`<=`): 1 fails, "on the bounds…".
- A censored direction counting one second off (`or 1.0`): 1 fails, "on the bounds…".
- The ceiling on decay dropped: 1 fails, "n has a ceiling…" (the record stored over the cap).
- `both_step_duty` ignoring `whole`: 5 fail.
- An unloaded record latching: 1 fails, "a record whose store is not read yet splits as today and latches nothing…".
- The latch decided on every read: 2 fail, "the split is latched per step…" and "null control, an empty learner…".
- `("duty_switch", None)` dropped from `_FACTORY_VOID`, then the factory-reset block by `tools/audit/seat/features_block.py` from `from heatpump_optimizer import const as _fr_const` to `R.section("Runtime parameter updates")`, its prelude from `--emit-prelude`: 2 of 32 fail, "a learners reset drops every learned key…" and "a learners reset leaves no stored duty-switch estimate and no latch…".

The reset check was failing first: at the commit before the coordinator change it failed with the stored record and its latch read back after the reset (`after (True, 6.0)`), while its null control (a plain restart keeps both) passed.

## Null control

- Below the threshold and on an install where no switch stops: an empty learner, one at `N_ON - 0.1` with p = 1, and one holding `N_CAP` of kept episodes split as today (`dddddddd` then `sssssss`) and write identical commands, with and without a stop on the install; the flat-price scenario `tests/golden/flat_prices.json` the same, both steps for all three. Non-vacuity: a latched learner splits the same step whole.
- The latch: the re-solved plan and empty learner read from the step's start split as today, where the latched run stays whole.
- Delivery: with the whole-step rule active, room and tank summed over the denied step and the next equal the plan's sum, the next step serving the denied duty whole. Per duty the two steps do not balance: the first duty is served the denied share and the denied duty gets back only its planned next step. This is the ruling's "delivery moves one step", not a per-duty catch-up.
- Factory reset: a plain restart keeps the stored record, its weight and its latch.
- No golden moves and neither claim file is touched.

## Figures

<!-- figure-block: scope-line mb=237fad44532d1927cf65612d395cc5833c60ce99 head=5e1fac78adb59b0d5b4b86ffc7dce58f55936155 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

- At the merge head 5e1fac78 on macOS (seat venv venv-ci), `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=237fad44 ./tests/run.sh`: 23 of 27 scripts pass, `env_drift.py --all` (no golden drift) included; 4 fail, and none reads a line this merge resolved. Three reproduce identically at origin/main 237fad44532d1927cf65612d395cc5833c60ce99, run alone in a detached worktree as the control: `tests/optimality.py` (1 of 84, "one|summer_negative|shoulder: a recorded claim still has a gap": the claim reads closed at a 0.0000% gap under this machine's BLAS), `tests/stress.py` (2 of 116, "the interned-table fill perturbation lands" and "shoulder: cheaper than holding the setpoint [4.67 vs 3.96]") and `node tests/card.mjs` (V8 "JavaScript heap out of memory" after "the census records through the navigation surface the card loaded against"; the same at the head run alone). The fourth, `tests/entities.py` (1 of 2724, "a measured script's late-writing descendant is waited for, not recorded as nodata"), is a timing check on the gate's metrics run while three other gates loaded this machine; it was not re-run, and main's push CI for 237fad44 is green on `tests / fast (3.14)`. CI is the authority for all four.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at the merge head. `node tools/policy/policy_lint.mjs`: 0 errors. `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh`: rc=0, claim files byte-identical to origin/main, CI PREDICT: no closures, fast, governance or instrument red.

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`: all section checks pass at the head; the mutants above as listed.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` at the head; `coord_footprint 2506 -> 2517` WORSENS at the commit where `_share` kept the time-share and the reader took the coordinator, the control.
- `python3 tests/structure.py`: the ratchet passes; `class_excess_loc` read +1 before `_restored_stores`' tuple went back to two lines, paid by that.

## Unpinned sites

Each killed by `MUTANT_CMD` in `prepr.sh` (both section harnesses), which listed none of these as a survivor at this head; each is pinned by `mutation-autofix` once the head is pushed. The reviewed head's sites were pinned by 56b43dea.

- custom_components/heatpump_optimizer/duty_legs.py:61 BOOLOP: the space-first condition; killed by "one leg rule in the leaf…" and "where only hot water to space is usable…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:61 CMP_BOUND*2: the space-first thresholds; killed by "one leg rule in the leaf…" and "planner and arbiter read one leg rule…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:63 CMP_BOUND: the into-direction's stop test; killed by "the first duty keeps the whole step only when…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:63 RETURN_DEL: the leg rule; killed by "one leg rule in the leaf…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:89 CMP_BOUND: the whole-step bound; killed by "the first duty keeps the whole step only when…" (its 150 s row); pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:89 GUARD_OFF: the whole-step precondition; killed by "the first duty keeps the whole step only when…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:91 RETURN_DEL: the two legs in the rule's order; killed by "where only hot water to space is usable…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:126 GUARD_OFF: the planner's whole-step branch; killed by "planner and arbiter read one leg rule…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:130 CMP_BOUND: the planner's whole-step bound; killed by "planner and arbiter read one leg rule…" (the off-on-the-bound case); pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:136 RETURN_DEL: the planner's leg ends; killed by the planner-price section's leg-agreement checks; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:289 GUARD_OFF: the ban under space first; killed by "one leg rule in the leaf…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:410 RETURN_DEL: the learner's leg rule; killed by "where only hot water to space is usable…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:561 CMP_BOUND: the first leg's end; killed by "on the bounds…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:561 RETURN_DEL: the served leg; killed by "null control, an empty learner…" and the price section's leg agreement; pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:235 RETURN_DEL: the availability vector; killed by the planner-price section's availability checks; pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:370 CMP_BOUND: the candidate gate's weight; killed by "a priced plan with a priced switch tries exactly one more hot-water plan…"; pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:370 GUARD_OFF: the candidate gate; killed by "a priced plan with a priced switch tries exactly one more hot-water plan…"; pinned by mutation-autofix

Survivors of that run on lines the diff touches, none of them a behaviour:

- custom_components/heatpump_optimizer/duty_legs.py:41 STMT_DEL and custom_components/heatpump_optimizer/duty_legs.py:43 STMT_DEL: the `LegRule` and `Legs` type aliases; read only in annotations, which `from __future__ import annotations` never evaluates, so no runtime check can kill them; `tests / typing` (mypy) refuses the undefined name.
- custom_components/heatpump_optimizer/coordinator.py:1448 STMT_DEL: the `_FACTORY_VOID` statement, outside both section harnesses; the factory-reset block (`tools/audit/seat/features_block.py`, the reviewed head's second `MUTANT_CMD`) fails on it, as the reviewed head's mutation proof records for its `("duty_switch", None)` row; this round does not change the line.

## Red checks

- `tests / fast (3.14)`, predicted by `prepr.sh` at this head: `tests/features.py`'s check "a charge-start dip that recovers is learned as neither a draw nor usage…" fails, and it fails identically at origin/main 50373173d486faf394b24637c177ab38b691b394 run in the same environment (`PYTHONPATH=tests/hastub python3 tests/features.py` in a detached worktree of main: the same single FAIL line), so it is main's, inherited by the merge and not made by this diff; the PR head 56b43dea's `tests / fast (3.14)` ran green in CI. Every other features check passes here, the 30-minute-step pin (R10-PROD-RESIDUE-PINS #2365) included after the step-width fix. Cheaper detector: none on this branch, since the red is reproduced on main before any of this round's commits; its own detector is main's push gate.
- `tests / mutation`: the sites this round adds in `duty_legs.py`, `duty_switch.py` and `optimizer.py` carry no ledger pin yet (each under `## Unpinned sites`, each killed by the section harnesses), which `mutation-autofix` pins once the head is pushed (`ci-autofix.md`). Cheaper detector: `prepr.sh`'s prediction step, which named every site locally before the handoff; none cheaper exists. The fifteen pins the merge made stale (main's `Direction.book` GUARD_OFF and CMP_BOUND 3e106b06, and the thirteen prepr's ledger prediction listed) are removed here.

## Forward-carry

none

## Friction

none

