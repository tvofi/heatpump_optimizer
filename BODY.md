Part C of the duty-switch work, with thanks to Bankaifan and pull request 3420: the finding, the install's table and the reasoning that a transition cost needs a term in both solves are theirs. The cycling penalty prices the swing of the combined draw, so a hot water to heating switch at constant draw cost nothing in the plan, while on the contributor's install that switch stopped the compressor. The planner now prices a switch the learner of pull request 3461 says stops the compressor, charges the running time the stop takes, and tries one hot-water placement that avoids it. Built to the approved design `design/R10-DUTY-SWITCH-PLANNER-PRICE` at 439d17c9305b6829c7426faa4c305edab7392d74 (verdict `design-verdict/R10-DUTY-SWITCH-PLANNER-PRICE` at c79ead84f06348feedc75546c1fe72d108a2ffbf).

What is built, by owner:

- `custom_components/heatpump_optimizer/duty_legs.py`, a new pure leaf beside `plan_step.py`: the leg rule moved out of `pump_arbiter._share` with `SPLIT_MIN_MINUTES`, the switch weight (scalar and batch), the availability vector, the delivered draw, the ban mask. `_share` keeps its gates and its clock compare and calls the rule.
- `optimizer.py`: two `OptimizationConfig` fields beside `cycling_cost` (stop probability and off seconds, a pair each, default zeros); the switch term inside the parenthesis the cycling term sits in, in the scalar and the batch objective; lost time on the bound (duty-cycle install) or on the delivered draw (clamped install); one banned hot-water candidate after `_co_optimize`, adopted only on a lower score with its returned requirement held.
- `dhw_planner.py`: one keyword, a placement ban OR'd into `forced_off` and never into `off_steps`.
- `duty_switch.py`: the count cap `N_CAP` in `Direction.book`, and the planner's read (`DutySwitchLearner.planner_pairs`, `planner_fields`), zeros unless a direction is latched.
- `coordinator.py`: one argument in `_solve_hubs`.

## Head

ee89d50b2bf9da997cb567874cd078c3bf290321

The merge base is 005eed2573da9e946fa4838de147401d0ff36cc1 (`git merge-base origin/main HEAD`), the tip of `origin/main` when this head was measured, holding pull request 3461; this head merges it. `origin/main` has since moved to 870238eb21 (2026-11-12T19:10Z) and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so it is not merged again. Every comparison below is three-dot against the merge base.

## Brief carries

- Carry 0 (from r10-duty-switch-restart-learning, item 3656875b) and Carry 1 (from 3461, item 036facc8), the same finding: done in the tree. The reader is added with its first caller: `duty_switch.planner_fields` is called from `_solve_hubs`, so `tests/structure.py`'s `dead_top_level_symbols` row does not move (Figures). The planner reads no published key: it reads the learner's `Direction.usable`, `.p` and `.median_off_s` through `DutySwitchLearner.planner_pairs`, and an unlatched or never-observed direction reads zeros, which price nothing; the section's check "the read returns zeros while a direction is unlatched, its off times with it" and the mutant "learner: the read ignores the latch" pin it.

## Design items, answered

- c1 (structure payment): paid. The coordinator's one line is paid in the same method: `_solve_hubs` reads the clock once instead of three times. Null control under Null control. The optimizer's and planner's lines are paid by the terms living at module level; `class_excess_loc` is recorded lower in commit 423d666f44, its message naming the two classes that moved.
- c2: no planner method was added. The guard calls the planner's own `_dhw_shortfall` with the draw rates the candidate plan returns, for the incumbent and the candidate alike.
- c5, c7: the cap sits in the pure `Direction.book`, the read beside the registry; `N_CAP` is a named constant from one day on one install, as part A's are.
- c6, r1, r10: the leg agreement runs over the probe grid with the floor unset and set and on the levels a clamped install ships (section checks 11 to 14 in file order).
- c8: every anchor was re-read on the tree that merges the predecessor; the section and the mutants ran on this head.
- c9: the first paragraph.
- r2, r3, r8, r9: the banned candidate is built into locals and assigned on adoption; one exit helper; the guard is on the returned requirement; a candidate with hot water on a banned step no pin forces on is refused before any solve.
- r6, r7, r11, r12, r13: no vector and no delivered-draw call on the null path; the vector is built from the space profile the solve starts from, once per space solve, and rides beside its plan to the publication; `_cost_terms_batch` takes the delivered and the shipped draw apart.
- r14 to r17 (verdict): the relaxed start carrying a vector, the achieved objective on the shipped arrays, the modulating clamped fixture and the batch twin through the row helper each have a section check and a mutant.

## Findings for the orchestrator and the reviewer

- `DEFAULT_CYCLING_COST` is 0.0 and the term is `cycling_cost` times the weight, so on an install that left the cycling cost at its default the price and the banned candidate are inert; only the lost running time is charged. The acceptance checks run at a cycling cost of 0.3. Whether the contributor's install prices a cycle is not something the tree can answer.
- On the fixed-speed fixture the priced solve keeps every hot water to heating switch: a charged step delivers a part-power step the pump cannot otherwise make, and the score falls. The switch weight there is unchanged by pricing. This is the design's delivered draw doing what it says; reported, not altered. The acceptance check therefore names the duty-cycle and the modulating clamped install, not the fixed-speed one.
- Design test 6's refusal runs on the due-disinfection fixture with the heating placed by hand after the run-up, calling the candidate pass directly: no solved fixture was found whose own plan holds a priced switch there.
- Equivalent mutants: dropping the zero-pair clause of `switch_weights_batch`'s early return turns no check red, because zero probabilities weigh zero; the harness records it as a comment, not an entry. Three more of the same kind are under Mutation proof.
- `docs/how-it-works.md`'s objective table is left as it is: the switch term sits inside the cycling row's parenthesis. The reviewer may want a sentence there.
- This is the first part that reads the estimate, and factory reset keeps the duty-switch store (pull request 3461's forward-carry, routed to R10-DUTY-SWITCH-RESTART-LEARNING-PR-B with "the owner rules before a part does"). Nothing here changes the reset. Effect at this head: after a factory reset a latched direction keeps pricing its switch until its evidence decays (the section's 28-day check bounds it with no episodes). Under Forward-carry.

## Alternatives (fixer step 17)

Taken from the design's Alternatives section, each refused there with its reason: a unit price per switch on an indicator (zero slope, and it pays the swing twice against the cycling term); step averages as leg draws (prices a stop the arbiter does not make); a term in the hot-water program (needs a binary per step, and the first plan precedes any space profile); the ban through `off_steps` (moves the disinfection placement and the pin rule; the section's "the check tells the two doors apart" is its control); lost time on the bound only, or a band in the projection (void or under the duty floor on a clamped install); counting switches in `pump_arbiter.py` or re-implementing `_share` in the optimizer (a Home Assistant import under the optimizer, or a duplicated rule). The mechanism of the improvement the architecture score reads is the leaf: remove `duty_legs.py` and the leg rule has two owners.

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py --mutants` at this head's tree. Each mutant is one edit on a private copy of the package and `tests/`; an unmutated copy runs first. The run ends `RESULT mutants_not_killed=0`. Its headlines, one per mutant, with the count of section checks that went red:

~~~text
control, no edit: exit 0, 0 red
optimizer: a candidate is tried with no requirement to hold it to: 1 red
optimizer: a candidate pass that raises is not caught: 1 red
learner: no count cap: 3 red
learner: the cap scales the stops alone: 4 red
learner: the cap is three times the on-threshold: 4 red
learner: the read ignores the latch: 2 red
learner: the read swaps the directions: 3 red
learner: the read hands the off time of the other direction: 3 red
leaf: the hot-water-to-heating switch reads the other direction: 13 red
leaf: the switch weight takes the larger neighbouring draw: 3 red
leaf: the in-step weight draws the smaller circuit, not the combined draw: 2 red
leaf: the weight is not divided by the maximum draw: 10 red
leaf: a small hot-water share no longer collapses to heating: 7 red
leaf: a small heating share no longer collapses to hot water: 10 red
leaf: the leg classification ignores the duty floor: 4 red
leaf: the zero-pair early return fires when either direction is unpriced: 15 red
leaf: a pump with no maximum draw is not returned early: 1 red
leaf: the early return is one entry per step, not per row: 1 red
optimizer: no priced direction still returns a pair: 1 red
leaf: the charged step is the hot-water block's last step: 6 red
leaf: the delivered draw is keyed on the clamped install: 10 red
leaf: the delivered draw loses only the space share: 3 red
optimizer: the switch term is handed the delivered draw: 2 red
optimizer: the simulation is handed the shipped draw: 3 red
optimizer: the energy cost is handed the shipped draw: 2 red
optimizer: the publication drops the solve's availability vector: 5 red
planner: the placement ban is not OR'd into forced_off: 2 red
optimizer: a candidate short of its requirement is adopted: 1 red
optimizer: a candidate with hot water on a banned step is adopted: 1 red
optimizer: the candidate is adopted on a higher score: 7 red
leaf: the lost share is not capped at one: 1 red
leaf: the lost share ignores the stop probability: 1 red
arbiter: the share serves the legs in reverse order: 3 red
~~~

The coordinator's argument is outside the section. Deleting the line `**duty_switch.planner_fields(self),` from `_solve_hubs` in a second worktree at this head and running `PYTHONPATH=tests/hastub python3 tests/features.py` whole fails two checks and no other:

~~~text
FAIL the coordinator passes the learner's read to the solve's configuration copy: zeros on a pump never arbitrated, both pairs once latched, and the configured hub keeps its zeros
FAIL the arbiter and the sensor name duty_switch through its report, attach and publish calls and never a read of the estimate; the coordinator names it once, for the planner's read; the module imports none of the three; the pure half of wear stays pure
~~~

`tools/pr/prepr.sh`'s diff pass, with `MUTANT_CMD='python3 dev/audit/harnesses/r10_duty_switch_price_section.py'`, ran at 423d666f4491bf83e8e17fb0aa5525010934f9e3 and printed nine `SURVIVED` lines. Each is answered:

- `duty_legs.py` early return of `switch_weights_batch`, three survivors (the guard switched off, the return deleted, the shape index swapped): killed by a check added at this head, "a pump with no maximum draw weighs every row zero, one finite entry per row and not per step, on the rows the priced pair weighs above". The harness gains the two mutants that turn it red ("leaf: a pump with no maximum draw is not returned early", "leaf: the early return is one entry per step, not per row"), in the list above.
- `coordinator.py` in `_solve_hubs`, three survivors, all outside the section the diff pass drives. Each was applied alone in a worktree at ee89d50b2b and `PYTHONPATH=tests/hastub python3 tests/features.py` run whole, exit 1 each time: the clock read replaced by `pass` and the configuration copy replaced by `pass` both raise `NameError` inside the solve; the outage guard switched off fails "#1736 post-outage recovery prices a month with no peak reference from zero; outside recovery the term stays off (an infinite threshold)" and no other check.
- Three equivalent mutants in `duty_legs.py`, no check can tell them apart. In `leg_ends`, the filler of `np.where(both, space + dhw, 1.0)` swapped for another constant: every reader of the quotient is masked by `both`. In `priced_pair`, `0.0 <= v` tightened to `0.0 < v`: a zero maps to 0.0 on either branch. In `switch_weights_batch`, `p_ds <= 0` tightened to `p_ds < 0` in the early return: with both probabilities zero the full path sums zeros, the same array. These are owed a triage record by whoever reads the lane's survivor list; none is written here.

## Null control

- The harness's first run, "control, no edit", exits 0 with no red check: the unmutated tree passes the section the mutants fail.
- An empty or below-threshold learner, and an install where no switch stops the compressor: the section's "null controls: an empty learner, one under its threshold and a pair that is no probability each leave the plan identical on all three install classes, with no availability vector, no banned build and the planner called as often", and from learner state "an empty learner, one under its on-threshold and an install whose every switch was kept each read a plan identical to today's on all three install classes". Each is followed by the check that the control has something to detect: with the contributor's pair, and with the latched learner's read, the plan moves on every install class.
- The flat-price scenario and every other golden: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` ends `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` against `origin/main`; `git diff --quiet origin/main...HEAD -- tests/golden` exits 0, so no golden and neither claim file is in the diff. `tests/golden/flat_prices.json` is among the fixtures that run reads.
- Acceptance's own control: "null control: a zero pair weighs every one of those plans zero", and at the edges "with a zero pair the same starts return the arrays of a config that never heard of the fields".
- Both ends of the learner's range: zero evidence reads zeros (above); on the clamp, "the decayed count is held at the cap", "from p = 1 at the cap the latch holds after twelve kept episodes and drops at the thirteenth" and "with no episodes a capped direction is latched at 28 days and not the day after".
- The structure payment: with the `_solve_hubs` clock hunk reverted in a second worktree (the three `dt_util.now()` reads restored, the argument kept), `python3 tests/structure.py` exits 1 on `max_class_loc`, one over its budget; at this head it exits 0.

## Figures

- Acceptance, on the contributor's table (15 min steps, pair (1, 0), off 501 s): `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py` exits 0; the checks "acceptance: priced on the contributor's table the plan carries a lower summed switch weight, on a duty-cycle and on a modulating clamped install" and "at no higher cost under the plan's own objective: the new plan scores no higher than the old plan does under the priced objective" are among those it prints. Null control: the zero-pair checks under Null control.
- Section and whole script: the same command's last line is its all-passed count; `PYTHONPATH=tests/hastub python3 tests/features.py` and `PYTHONPATH=tests/hastub python3 tests/entities.py` exit 0 at this head.
- Golden drift: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` exits 0 (Null control).
- Structure: `python3 tests/structure.py` exits 0; `dead_top_level_symbols` and `max_class_loc` at their budgets, `class_excess_loc` recorded lower in this branch.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` prints `IMPROVES`, `coord_footprint` down and no row up.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` prints `MODE: SCOPED`. `env -u BASH_ENV GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` exits 0 at this head, the scripts the scope names passed and the scoped-out ones named as not run.
- Mutants: the command under Mutation proof.

<!-- figure-block: scope-line mb=005eed2573da9e946fa4838de147401d0ff36cc1 head=ee89d50b2bf9da997cb567874cd078c3bf290321 -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

Each site below is added by this diff and carries no ledger record; `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only mutation` lists them. The section harness's mutants above are this group's own kills of the same lines' behaviour; the ledger records are the lane's to write.

- custom_components/heatpump_optimizer/coordinator.py:6229 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6229 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/dhw_planner.py:149 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:33 CONST: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:49 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:49 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:51 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:51 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:53 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:58 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:59 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:59 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:80 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:81 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:86 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:95 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:97 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:97 CMP_BOUND*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:98 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:123 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:123 CMP_BOUND*3: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:123 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:133 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:135 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:161 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:161 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:178 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:178 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:183 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:185 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:198 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:199 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:200 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:201 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:213 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:215 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:216 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:230 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:230 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:233 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:233 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_legs.py:236 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:224 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:224 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:390 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/duty_switch.py:528 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:203 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:203 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:216 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:221 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:221 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:225 CLAMP_DROP*3: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:228 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:250 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:252 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:273 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:275 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:292 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:292 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:296 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:298 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:303 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:355 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:355 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:363 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:363 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:373 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:385 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:393 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:398 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:398 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:400 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/optimizer.py:404 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1771 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1771 RETURN_DEL: pinned by mutation-autofix

The diff pass's six remaining survivors, answered under Mutation proof:

- custom_components/heatpump_optimizer/coordinator.py:6229 GUARD_OFF: killed outside the section by `tests/features.py`'s #1736 check; pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6222 STMT_DEL: killed outside the section, a `NameError` in the solve under `tests/features.py`
- custom_components/heatpump_optimizer/coordinator.py:6238 STMT_DEL: killed outside the section, a `NameError` in the solve under `tests/features.py`
- custom_components/heatpump_optimizer/duty_legs.py:79 CONST_SWAP: equivalent, the filler is masked by `both`
- custom_components/heatpump_optimizer/duty_legs.py:97 CMP_BOUND: equivalent, a zero reads 0.0 on either branch
- custom_components/heatpump_optimizer/duty_legs.py:123 CMP_BOUND: equivalent, zero probabilities sum to the same zeros

## Red checks

- `mutation` (`tests / mutation`) at ee89d50b2bf9: red by construction on the sites under `## Unpinned sites`, which the diff adds and no ledger record pins; `tools/pr/prepr.sh` step 6d predicted it before any push. Cheaper detector: step 6d itself, which named every site at no cost beyond the self-check; the kill runs that write a pin are the lane's own (`mutation-autofix` after the pull request exists), and nothing cheaper than them can pin a site.

## Forward-carry

- Factory reset keeps the duty-switch store, and from this pull request the planner reads the estimate it holds (`custom_components/heatpump_optimizer/duty_switch.py`, `planner_fields`). Pull request 3461 routed the reset question to the owner "before a part does" read it; this part does, and changes nothing about the reset. Control: the section's "with no episodes a capped direction is latched at 28 days and not the day after" bounds how long a kept record prices a switch with no new evidence. Re-measure with the section at the destination's merge base. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The leg order and the minimum share of a both step have one owner now, `custom_components/heatpump_optimizer/duty_legs.py`: a part that changes the split order or adds a minimum-share rule edits the leaf's leg rule and nowhere else, or planner and arbiter disagree. Control: the harness mutant "arbiter: the share serves the legs in reverse order" turns three section checks red. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- `_build_dhw_requirements` in `custom_components/heatpump_optimizer/dhw_planner.py` has a placement-ban channel, `_with_placement_ban`, OR'd into `forced_off` after the Off window's; a group adding its own start ban ORs into the same local at the same point and adds no parameter. Control: the section's "the check tells the two doors apart: the same mask through off_steps moves the disinfection step and zeroes the pinned step". Carry: R10-OUTSIDE-DHW-START-HYSTERESIS

## Friction

- brief-citations.md: cost: `dev/archive/carries/carry-1412.json`'s control cites `custom_components/heatpump_optimizer/optimizer.py:4671` for a line in neither tree; `brief_lint.mjs`'s LEGACY-CONTROL arm read VACUOUS when one added line in `optimizer.py` put an unrelated name inside the cited window, and ok again when the line was removed. Carry: dismissed: an archived carry, observed once and not reproduced at this head
- gate-scoping.md: unclear: `prepr.sh`'s closures step says a full derive is forbidden while step 6d asks for a single-script re-record on every script that reaches a new production module; the loop took about 50 minutes on a cloud container. Carry: dismissed: the price of a measured closure, paid once
- fixer.md: cost: the section harness read a traceback as no red check until it was made to look for the closing line; a crashed section now reads red. Carry: dismissed: repaired in this pull request's harness
- fixer.md: cost: the group was built stacked on its predecessor's open head by ruling, then waited a day for pull request 3461; the merge of main was clean and every figure was re-taken at this head. Carry: dismissed: sequencing decided by the orchestrator, no rule change asked
