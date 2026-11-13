Part C of the duty-switch work, with thanks to Bankaifan and pull request 3420: the finding, the install's table and the reasoning that a transition cost needs a term in both solves are theirs. The cycling penalty prices the swing of the combined draw, so a hot water to heating switch at constant draw cost nothing in the plan, while on the contributor's install that switch stopped the compressor. The planner now prices a switch the learner of pull request 3461 says stops the compressor, charges the running time the stop takes, and tries one hot-water placement that avoids it. Built to the approved design `design/R10-DUTY-SWITCH-PLANNER-PRICE` at 439d17c9305b6829c7426faa4c305edab7392d74 (verdict `design-verdict/R10-DUTY-SWITCH-PLANNER-PRICE` at c79ead84f06348feedc75546c1fe72d108a2ffbf).

What is built, by owner:

- `custom_components/heatpump_optimizer/duty_legs.py`, a new pure leaf beside `plan_step.py`: the leg rule moved out of `pump_arbiter._share` with `SPLIT_MIN_MINUTES`, the switch weight (scalar and batch), the availability vector, the delivered draw, the ban mask. `_share` keeps its gates and its clock compare and calls the rule.
- `optimizer.py`: two `OptimizationConfig` fields beside `cycling_cost` (stop probability and off seconds, a pair each, default zeros); the switch term inside the parenthesis the cycling term sits in, in the scalar and the batch objective; lost time on the bound (duty-cycle install) or on the delivered draw (clamped install); one banned hot-water candidate after `_co_optimize`, adopted only on a lower score with its returned requirement held.
- `dhw_planner.py`: one keyword, a placement ban OR'd into `forced_off` and never into `off_steps`.
- `duty_switch.py`: the count cap `N_CAP` in `Direction.book`, and the planner's read (`DutySwitchLearner.planner_pairs`, `planner_fields`), zeros unless a direction is latched.
- `coordinator.py`: one argument in `_solve_hubs`.

## Head

ec56d126d6bd4a4d9ef15c855e05e0e71a07cc54

This head merges `origin/main` at 7eadd75f3c420404aabc83d4b05f9691f3e49136 into 7e68a0f1ca540c1d99292b55db36627d4568a749 (merge commit fb6438b125cab5685cebd4067bcde480d7880eaa, no conflict), so the merge base is now 7eadd75f3c420404aabc83d4b05f9691f3e49136. It adds one commit that removes a ledger row main's nightly drain wrote (caacd43b4e, `ci: record nightly kills`): `optimizer.py:HeatPumpOptimizer._co_optimize CLAMP_DROP f79618d7`, pinned on `headroom = np.maximum(0.0, p_max - dhw_power)`, a line this branch replaced in 4a8115bc10 with `duty_legs.space_headroom(...)`. At the merge, `python3 tools/pr/ci_predict.py --base 7eadd75f3c42 --only mutation` printed `PREDICT ledger STALE PIN ...: disposition names no site the inventory generates`. The site no longer exists, so the row was deleted as ci_predict prescribes, not re-anchored. Its clamp now sits in `duty_legs.space_headroom`, whose two CLAMP_DROP sites are already pinned on this branch. At this head the same command prints no red. Figures below that name 7e68a0f1ca54 or an earlier SHA were taken there.

7e68a0f1ca540c1d99292b55db36627d4568a749

The merge base is 36da41115decd0c1b6375d07c713fcb1c59c4935 (`git merge-base origin/main HEAD`). `origin/main` is at 8a550692da2c80d7ea7f5f26a9c95fc81090a841 (2026-11-13T08:10:33+01:00, read 2026-11-13T07:57Z) and `git merge-tree --write-tree origin/main HEAD` exits 0, so it is not merged again. Every comparison below is three-dot against the merge base.

This head descends from the pull request head e36f8af6f1b1949c5d8b2590c5669a4ded2ff71f: the round-1 handoff 4ac1ef3155f9, the merge of main into it (fc6677a930), the lane's pin commit, and this round's two commits. A figure whose line names 4ac1ef3155f9, ee89d50b2bf9, cade4a8d12e2 or 3af3edaabd9b was taken there and stands as written; every other figure in this body was re-taken at this head.

## Repair round 2

`tests / mutation` was red on the pull request head e36f8af6f1b1 after the lane's pin commit. `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` there, the job's own command:

~~~text
    ADDED UNPINNED custom_components/heatpump_optimizer/optimizer.py:223 CLAMP_DROP*3: np.minimum(np.clip(start, 0.0, p_max), np.maximum(0.0, p_max - dhw_plan)
MUTATION TABLE REFUSED -- 2526 unpinned site(s) against 2525 at the ratchet base 36da41115decd0c1b6375d07c713fcb1c59c4935, 3 of them added by this diff.
~~~

So the pin commit left exactly one anchor: the three clamps of one line of `_stop_availability`, which the ledger keys as one (`tests/mutation_table.py`, `anchor_sites`: file, scope, operator, line text), and a row is written for an anchor only when every site under it is killed.

- Dropping `np.clip(start, 0.0, p_max)` is an equivalent mutant. The cap beside it is at most `p_max` wherever hot water is not negative; `duty_legs._runs` reads a value under zero as not running; `thermal_model._onto_band` clips under zero and over the cap on a clamped install. Measured before the edit, on the three one-clamp-dropped lines against the original, 20000 random profiles of 3 to 8 steps (starts drawn from under zero to over `p_max` and NaN, hot water from under zero to over `p_max`), each on both install kinds: the dropped clip moved 0 of 40000 readings; null control, the same corpus moved 11481 readings with the outer `np.minimum` dropped and 29816 with the `np.maximum` dropped. The probe was a scratch script; what it measured is in the tree as the grid check below.
- The other two are killable, and the outer one was killed before this round ("a priced install whose plan holds no priced switch builds no candidate" goes red on it). The equivalent twin alone kept the anchor unpinned, which is why the lane pinned every other site and not this one.

A triage record was not the answer, for the reason this body gives for `priced_pair` under Review round 1: the record's key is the anchor, so an `equivalent` verdict on it would cover the two killable clamps beside the clip (`fixer.md` step 14, equal keys). The clip is removed instead: the line is `np.minimum(start, np.maximum(0.0, p_max - dhw_plan))`, holding two clamps a check kills, and no value the callers can produce moves. Two section checks are added to `tests/features.py`:

- "heating asked beside hot water at p_max is no heating leg: nothing is charged; beside a block that leaves room the same start is charged there", the cap's own check.
- "a start outside [0, p_max] reads as the same start clipped into it, on a duty-cycle and on a clamped install; the grid holds starts outside the band and readings that charge a step": `_stop_availability` on each of 625 starts (five values per step, two of them outside the band, four steps) against three hot-water plans on both install kinds, compared with the same call on the clipped start. This is the property the removed clip stated, held by a check instead of by a line no check could see.

The comment over the round-1 check that read "clipped into [0, p_max] before it is read" now reads "capped at what hot water leaves".

Mutation proof of the two checks, each edit made to the line in f29d7543caf3's tree and the section run (`env PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py`), then restored:

~~~text
the line replaced by `(start),` (the cap dropped): exit 1, 3 red
  FAIL heating asked beside hot water at p_max is no heating leg: nothing is charged; beside a block that leaves room the same start is charged there
  FAIL a start outside [0, p_max] reads as the same start clipped into it, on a duty-cycle and on a clamped install; the grid holds starts outside the band and readings that charge a step
  FAIL a priced install whose plan holds no priced switch builds no candidate
the line replaced by `np.minimum(start, (0.0)),` (the floor's first argument): exit 1, 13 red
~~~

Both edits are in the harness's list now (Mutation proof). The ledger: `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` at f29d7543caf3 ended `PIN KILLED: 2 pinned, 0 left unpinned`, both sites killed by `tests/features.py` whole, its null control (`optimizer.py:135 NULL_COMMENT`) surviving every driver; the row is `tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json`.

The dispatch brief for this round says "Do not edit production code beyond what a killing test requires (none expected)". Read as forbidding the one-line removal, it would change `fixer.md` step 14 ("the answer is to change the route until no entry is needed, or to widen the key until the two separate, never to add it and note the risk") and step 17 ("a triage on a killable mutant"): that reading is recorded as pending owner confirmation and not acted on. Read as written, the removal is what the two killing checks require, since no check can hold a pin on an anchor that includes an equivalent site.

## Review round 1, answered

The verdict on ee89d50b2bf9 (`probe/revt-r10-duty-switch-planner-price-3e2877f0`, `verdict.md` at 8d8b28780fd1be89cf61cb8e562066edb5b0438a) blocked on three reviewer mutants that survived the section. Each now fails a section check that drives the production function; the checks are in `tests/features.py`'s section and the three mutants are in the harness's list (Mutation proof).

- R5, `_co_optimize`'s headroom handed no vector: killed by "the co-optimisation reads the charged bound: on a duty-cycle install heating at avail x p_max - dhw in a charged step is pinned, and the replan is built against a full compressor there and nowhere else". The check calls `HeatPumpOptimizer._co_optimize` with a vector on the optimizer and reads the `space_demand` it hands the planner's build. Its null control, "the same heating with no vector, or with the vector on a clamped install whose bound carries no lost time, is under its bound and builds no replan; at the uncharged bound each of the two builds one", also kills the same call handed no duty floor (R5b below, this seat's mutant on the reviewer's line).
- R9, `_stop_availability` classifying with no duty floor: killed by "on a modulating clamped install heating shipped under p_min beside hot water takes no charge: the stop is charged to the heating step after the both step, and no charged step ships heating under the floor", on the reviewer's arrays (heating 1.0 beside hot water 2.0, then heating 2.5; design-verdict item r16). Null control: "with no duty floor (a duty-cycle install) the same arrays charge the both step itself, so the floor is what moved the charge".
- R11, the combi exclusion of `_avoid_priced_switches` removed: killed by "on a combi store the candidate pass asks its planner nothing and returns the incumbent, its requirement and its availability in place, on an incumbent holding a priced switch". Null control: "the same install with the store's hot water in its own tank reaches the banned build". The pass is called directly on a combi `ThermalParameters` with the guard fixture's incumbent, as design test 6's refusal is; no solved combi fixture was looked for.

`python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'env PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py'` at 4ac1ef3155f9, the `old` and `new` of R5, R9 and R11 copied from the reviewer's `ev/reviewer_mutants.py`:

~~~text
SURVIVED NULL
KILLED R5 _co_optimize's headroom ignores the availability vector
KILLED R9 the availability vector is classified with no duty floor
KILLED R11 the candidate pass runs on a combi store
KILLED R5b _co_optimize's headroom is handed no duty floor
KILLED D1 duty_legs.py switch_weights_batch CONST_SWAP: a pump under 1 kW returns early
KILLED D2 optimizer.py _avoid_priced_switches CMP_BOUND: a candidate on the margin is adopted
~~~

The class, not the three: `python3 tools/audit/seat/mutant_run.py --diff 005eed2573da9e946fa4838de147401d0ff36cc1...HEAD --report-only --cmd <the same command>` over every added Python line outside `tests/` and `dev/`, uncapped, run once per file (`--path`) at cade4a8d12e2 (the head holding only the three checks above) and again at 3af3edaabd9b. The rule that enumerates the seams is the driver's own: `--diff ... --list` prints one `MUTANT` line per mutant. Every `SURVIVED` line either run printed, with its disposition:

| survivor (line at the run's head) | disposition |
|---|---|
| `optimizer.py` `_stop_availability`, `if not lost > 0: return None`: GUARD_OFF, CMP_BOUND, RETURN_DEL | the line was dead: `duty_legs.availability` makes the same test first thing. Removed. |
| `optimizer.py` `_stop_availability`, `np.clip(start, 0.0, p_max)` CONST_SWAP | killed at 4ac1ef3155f9: "a start that is idle, or below zero, in the step after a block charges nothing; the same block followed by heating charges that step". The clip is removed in repair round 2. |
| `optimizer.py` `_with_stop_availability`, `if avail is None:` GUARD_OFF, its return RETURN_DEL | killed: "with no vector a space solve gets the two objectives it handed in, the same objects, and today's bound; with one it gets them bound to the vector" |
| `optimizer.py` `_avoid_priced_switches`, the pin threshold `>= 0.5`: CMP_BOUND, CONST_SWAP | killed: "the same candidate with each of those steps pinned at 0.5, which the planner's pin rule forces on, is solved and adopted on its lower score" |
| `optimizer.py` `_avoid_priced_switches`, `plan.schedule[ban & ~forced_on] > 0` CONST_SWAP | killed: "any hot water on a banned step refuses the candidate, 0.8 kW as much as a full block" |
| `optimizer.py` `_avoid_priced_switches`, `score < base - 1e-9`: CONST_SWAP, CMP_BOUND | killed: "a candidate lower by exactly the 1e-9 margin, and so by no more than it, is a tie: refused after its solve, as _co_optimize refuses its own" (D2 above) |
| `optimizer.py` `_avoid_priced_switches`, `temps_of[id(schedule)] = temps` STMT_DEL | killed: "the incumbent's tank is walked once: the read past its excused step is handed the first walk's temperatures" |
| `optimizer.py` `OptimizationConfig.duty_switch_off_seconds`: CONST_SWAP, STMT_DEL; `self._space_avail = None` in `__init__` STMT_DEL | killed: "a configuration that never heard of the learner holds a zero pair in both fields, and an optimizer that has solved nothing holds no vector" |
| `duty_legs.py` `space_headroom`, `np.maximum(0.0, p_max - dhw_kw)` CONST_SWAP | killed: "the bound is what hot water leaves and never under zero: 0.5 kW beside 5.5 of 6, nothing beside 7, with no vector and with one" |
| `duty_legs.py` `switch_weights_batch`, `p_ds <= 0` in the early return, CMP_BOUND | the zero-pair clause was a shortcut no caller needs (zero probabilities weigh zero on the full path; the optimizer calls the leaf only with a priced direction). Removed; the line is `if p_max <= 0:`. |
| `duty_legs.py` `switch_weights_batch`, `if p_max <= 0:` CONST_SWAP (at 3af3edaabd9b) | killed: "a pump under 1 kW weighs its switch like any other: p x draw / p_max at a maximum draw of 0.5 kW" (D1 above) |
| `duty_legs.py` `priced_pair`, `0.0 <= v` CMP_BOUND | the line is rewritten `max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0`: the same values, and no bound a zero can sit on. A triage record was not the answer: the ledger keys a record on file, scope, operator and line text, and this line's other bound (`v <= upper`, killable) has the same key. |
| `duty_legs.py` `leg_ends`, the filler of `np.where(both, space + dhw, 1.0)` CONST_SWAP | equivalent: every reader of the quotient is masked by `both`. No triage record can exist: CONST_SWAP is the driver's operator, the ledger generates no site for it (`tests/mutation_table.py`'s `RATCHETED`), and a record naming no generated site is refused by its completeness check. |
| `duty_switch.py` `Direction.book`, `if self.n > N_CAP:` CMP_BOUND | equivalent: at `n == N_CAP` the body multiplies by `N_CAP / n = 1.0`. Triage record `tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json`; the line holds one bound, so the record's key matches this mutant alone. |
| `duty_switch.py` `planner_fields`: its two statements STMT_DEL, its return RETURN_DEL | outside the section (the coordinator's check is in the lifecycle part of the script): killed by `tests/features.py` whole, O1 to O3 below |
| `optimizer.py` `_combi_flux_exchange`, the replan's `_dhw_build` call STMT_DEL | outside the section (a line this diff re-routes through `_dhw_build`): killed by `tests/features.py` whole, O4 below |
| `coordinator.py` `_solve_hubs`: three mutants | outside the section: the coordinator run below |

The two production lines removed and the one rewritten change no value on any input the callers make; every round-1 harness mutant whose text still exists is killed over them, and both null-control families pass (Mutation proof).

Outside the section, `python3 tools/audit/seat/mutant_run.py --spec <spec> --in-place --cmd 'env PYTHONPATH=tests/hastub python3 tests/features.py'` at 4ac1ef3155f9:

~~~text
# first invocation, O1 to O4; interrupted by a container restart after O2, the mutated file restored with git checkout
SURVIVED NULL
KILLED O1 duty_switch.py planner_fields STMT_DEL: the record lookup
KILLED O2 duty_switch.py planner_fields STMT_DEL: the learner's read
# second invocation, O3 and O4, in a scratch worktree at the same head
SURVIVED NULL
KILLED O3 duty_switch.py planner_fields RETURN_DEL
KILLED O4 optimizer.py _combi_flux_exchange STMT_DEL: the combi replan build
~~~

and `python3 tools/audit/seat/mutant_run.py --diff 005eed2573da9e946fa4838de147401d0ff36cc1...HEAD --path custom_components/heatpump_optimizer/coordinator.py --in-place --report-only --cmd <the same command>`, which prints one line per survivor and nothing for a kill:

~~~text
(the run printed no line and exited 0: none of the three mutants that `--list` prints for the file survives)
~~~

## Brief carries

- Carry 0 (from r10-duty-switch-restart-learning, item 3656875b) and Carry 1 (from 3461, item 036facc8), the same finding: done in the tree. The reader is added with its first caller: `duty_switch.planner_fields` is called from `_solve_hubs`, so `tests/structure.py`'s `dead_top_level_symbols` row does not move (Figures). The planner reads no published key: it reads the learner's `Direction.usable`, `.p` and `.median_off_s` through `DutySwitchLearner.planner_pairs`, and an unlatched or never-observed direction reads zeros, which price nothing; the section's check "the read returns zeros while a direction is unlatched, its off times with it" and the mutant "learner: the read ignores the latch" pin it.
- Carry 2 (from r10-duty-switch-restart-learning-pr-b-p2, item c3ad1545): nothing to resolve at this head, and the rule stands for the merge that comes second. Neither part is on `origin/main`: `git grep -c "def split\|N_CAP" origin/main -- custom_components/heatpump_optimizer/duty_switch.py` prints nothing at 8a550692da2c, and `git merge-tree --write-tree origin/main HEAD` exits 0 (null control: the same grep at this head prints a count, the cap this branch adds). This round is repair only and adds nothing to the cap: it is held at booking, as round 1 built it. If the sibling merges first, the conflict is resolved by merge into this head under the carry's rule (the leg order and the whole-step decision in `duty_legs.py`'s leg rule, the cap held on decay as well as at booking), with the sibling's two section checks as the control; if this merges first, the same rule binds the sibling.

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
- Equivalent mutants: two remain, each under Review round 1, answered: the masked filler in `leg_ends` and the cap bound in `Direction.book`.
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
leaf: the hot-water-to-heating switch reads the other direction: 18 red
leaf: the switch weight takes the larger neighbouring draw: 3 red
leaf: the in-step weight draws the smaller circuit, not the combined draw: 2 red
leaf: the weight is not divided by the maximum draw: 11 red
leaf: a small hot-water share no longer collapses to heating: 9 red
leaf: a small heating share no longer collapses to hot water: 11 red
leaf: the leg classification ignores the duty floor: 5 red
leaf: a pump with no maximum draw is not returned early: 1 red
leaf: a negative learned value is kept: 1 red
leaf: a learned value on its upper bound reads as zero: 25 red
leaf: the early return is one entry per step, not per row: 1 red
optimizer: no priced direction still returns a pair: 1 red
leaf: the charged step is the hot-water block's last step: 9 red
leaf: the delivered draw is keyed on the clamped install: 10 red
leaf: the delivered draw loses only the space share: 3 red
optimizer: the switch term is handed the delivered draw: 2 red
optimizer: the simulation is handed the shipped draw: 3 red
optimizer: the energy cost is handed the shipped draw: 2 red
optimizer: the publication drops the solve's availability vector: 5 red
planner: the placement ban is not OR'd into forced_off: 2 red
optimizer: a candidate short of its requirement is adopted: 1 red
optimizer: a candidate with hot water on a banned step is adopted: 2 red
optimizer: the candidate is adopted on a higher score: 8 red
leaf: the lost share is not capped at one: 1 red
leaf: the lost share ignores the stop probability: 1 red
optimizer: the co-optimisation headroom ignores the availability vector: 1 red
optimizer: the availability vector is classified with no duty floor: 1 red
optimizer: the candidate pass runs on a combi store: 1 red
optimizer: the co-optimisation headroom is handed no duty floor: 1 red
optimizer: the start is read with no cap beside hot water: 3 red
optimizer: the start is capped at zero in every step: 13 red
arbiter: the share serves the legs in reverse order: 3 red
~~~

Against round 1's list: "leaf: the zero-pair early return fires when either direction is unpriced" is gone with the clause it mutated; "leaf: a pump with no maximum draw is not returned early" now moves the bound of the one test left; two mutants of the rewritten `priced_pair` line and the reviewer's three (with R5b) are new. Repair round 2 adds the two clamps of the start's line, "optimizer: the start is read with no cap beside hot water" and "optimizer: the start is capped at zero in every step".

The coordinator's argument is outside the section. Its line `**duty_switch.planner_fields(self),` in `_solve_hubs` is the configuration copy's statement, one of the three mutants of the coordinator run under Review round 1, answered. The two checks that pin it, read at ee89d50b2bf9 by deleting the line in a second worktree and running `tests/features.py` whole (the reviewer re-derived it, `ev/features_coordinator_line_deleted.log`):

~~~text
FAIL the coordinator passes the learner's read to the solve's configuration copy: zeros on a pump never arbitrated, both pairs once latched, and the configured hub keeps its zeros
FAIL the arbiter and the sensor name duty_switch through its report, attach and publish calls and never a read of the estimate; the coordinator names it once, for the planner's read; the module imports none of the three; the pure half of wear stays pure
~~~

`tools/pr/prepr.sh`'s diff pass (`MUTANT_CMD='env PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py'`, the first 40 mutants in file order) is a prefix of the uncapped pass above: at this head it printed four `SURVIVED` lines, the three `coordinator.py` mutants (killed by `tests/features.py` whole, the coordinator run above) and the `leg_ends` filler (equivalent, in the table above).

## Null control

- The harness's first run, "control, no edit", exits 0 with no red check: the unmutated tree passes the section the mutants fail.
- An empty or below-threshold learner, and an install where no switch stops the compressor: the section's "null controls: an empty learner, one under its threshold and a pair that is no probability each leave the plan identical on all three install classes, with no availability vector, no banned build and the planner called as often", and from learner state "an empty learner, one under its on-threshold and an install whose every switch was kept each read a plan identical to today's on all three install classes". Each is followed by the check that the control has something to detect: with the contributor's pair, and with the latched learner's read, the plan moves on every install class.
- The flat-price scenario and every other golden: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` ends `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` against `origin/main`; `git diff --quiet origin/main...HEAD -- tests/golden` exits 0, so no golden and neither claim file is in the diff. `tests/golden/flat_prices.json` is among the fixtures that run reads.
- Acceptance's own control: "null control: a zero pair weighs every one of those plans zero", and at the edges "with a zero pair the same starts return the arrays of a config that never heard of the fields".
- Both ends of the learner's range: zero evidence reads zeros (above); on the clamp, "the decayed count is held at the cap", "from p = 1 at the cap the latch holds after twelve kept episodes and drops at the thirteenth" and "with no episodes a capped direction is latched at 28 days and not the day after".
- This round's checks each carry their control in the section, named under Review round 1, answered: the vector removed and the floor set (R5), the floor removed (R9), the combi flag off (R11), heating present after the block (the idle start), a vector present (the null-path objectives).
- Flat price: no figure in this round's delta is a price or a cost; the round-1 controls above are re-run at this head by the section and by the golden drift run (Figures).
- The structure payment (read at ee89d50b2bf9; the hunk is untouched since): with the `_solve_hubs` clock hunk reverted in a second worktree (the three `dt_util.now()` reads restored, the argument kept), `python3 tests/structure.py` exits 1 on `max_class_loc`, one over its budget; at this head it exits 0.

## Figures

- Acceptance, on the contributor's table (15 min steps, pair (1, 0), off 501 s): `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py` exits 0; the checks "acceptance: priced on the contributor's table the plan carries a lower summed switch weight, on a duty-cycle and on a modulating clamped install" and "at no higher cost under the plan's own objective: the new plan scores no higher than the old plan does under the priced objective" are among those it prints. Null control: the zero-pair checks under Null control.
- Section and whole script: the same command's last line is its all-passed count; `PYTHONPATH=tests/hastub python3 tests/features.py` and `PYTHONPATH=tests/hastub python3 tests/entities.py` exit 0 at this head.
- Golden drift: `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` exits 0 (Null control).
- Structure: `python3 tests/structure.py` exits 0; `dead_top_level_symbols` and `max_class_loc` at their budgets, `class_excess_loc` recorded lower in this branch.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` prints `IMPROVES`, `coord_footprint` down and no row up.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` prints `MODE: SCOPED`. `env -u BASH_ENV GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` exits 0 at this head, the scripts the scope names passed and the scoped-out ones named as not run.
- Mutants: the commands under Mutation proof, Repair round 2 and Review round 1, answered. The uncapped diff pass enumerates 224 mutants at this head (`mutant_run.py --diff 36da41115decd0c1b6375d07c713fcb1c59c4935...HEAD --list`, one `MUTANT` line each); null control: the driver's own NULL mutant must survive (`SURVIVED NULL` in the two spec outputs), and the section harness run with no edit exits 0.

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Unpinned sites

None at this head. `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` at f29d7543caf3 opened with `PIN KILLED -- 2 new unpinned site(s)` and ended `PIN KILLED: 2 pinned, 0 left unpinned`; its row is in this head. Null control: the same table at e36f8af6f1b1 prints the `ADDED UNPINNED` line under Repair round 2 and exits 1. Every other site the diff adds holds a row the lane wrote in e36f8af6f1b1 (`git show --stat e36f8af6f1b1 -- tests/mutation_ledger`).

The diff pass's survivors are dispositioned in the table under Review round 1, answered.

## Red checks

- `mutation` (`tests / mutation`) at 4ac1ef3155f9: red by construction on the sites the diff added with no ledger record; `tools/pr/prepr.sh` step 6d predicted it before any push, and the lane's pin commit e36f8af6f1b1 answered all but one anchor.
- `mutation` (`tests / mutation`) at e36f8af6f1b1, after the pin commit: red on `optimizer.py:223 CLAMP_DROP*3` (Repair round 2). Cheaper detector: it exists and ran. `tools/pr/prepr.sh` step 6d named the site at the round-1 handoff, and the round-1 body answered it "pinned by mutation-autofix", a disposition step 6d accepts for any site and nothing had measured for this one: the lane can write a row only for an anchor whose every site a driver kills, and one of this anchor's three was equivalent. The uncapped diff pass could not show it either, because `mutant_run.py`'s operators do not drop a clamp (its mutant of the same call was a CONST_SWAP, killed). The detector that separates the two cases before a push is the table's own mutants of the site run against the group's section: one section run per site, 33 s measured at this head (`time` of the harness), against a pull-request round and the lane's shard run. Process state (c): the step ran, was followed, and did not produce a pinned site. This is the second anchor in this group shared by a killable and an equivalent site (`priced_pair` in round 1 was the first, found by the diff pass because its operator exists there). No countermeasure is built here; the finding is under Friction with its destination.

## Forward-carry

- Factory reset keeps the duty-switch store, and from this pull request the planner reads the estimate it holds (`custom_components/heatpump_optimizer/duty_switch.py`, `planner_fields`). Pull request 3461 routed the reset question to the owner "before a part does" read it; this part does, and changes nothing about the reset. Control: the section's "with no episodes a capped direction is latched at 28 days and not the day after" bounds how long a kept record prices a switch with no new evidence. Re-measure with the section at the destination's merge base. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- The leg order and the minimum share of a both step have one owner now, `custom_components/heatpump_optimizer/duty_legs.py`: a part that changes the split order or adds a minimum-share rule edits the leaf's leg rule and nowhere else, or planner and arbiter disagree. Control: the harness mutant "arbiter: the share serves the legs in reverse order" turns three section checks red. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B
- `_build_dhw_requirements` in `custom_components/heatpump_optimizer/dhw_planner.py` has a placement-ban channel, `_with_placement_ban`, OR'd into `forced_off` after the Off window's; a group adding its own start ban ORs into the same local at the same point and adds no parameter. Control: the section's "the check tells the two doors apart: the same mask through off_steps moves the disinfection step and zeroes the pinned step". Carry: R10-OUTSIDE-DHW-START-HYSTERESIS

## Friction

- brief-citations.md: cost: `dev/archive/carries/carry-1412.json`'s control cites `custom_components/heatpump_optimizer/optimizer.py:4671` for a line in neither tree; `brief_lint.mjs`'s LEGACY-CONTROL arm read VACUOUS when one added line in `optimizer.py` put an unrelated name inside the cited window, and ok again when the line was removed. Carry: dismissed: an archived carry, observed once and not reproduced at this head
- gate-scoping.md: unclear: `prepr.sh`'s closures step says a full derive is forbidden while step 6d asks for a single-script re-record on every script that reaches a new production module; the loop took about 50 minutes on a cloud container. Carry: dismissed: the price of a measured closure, paid once
- fixer.md: cost: the section harness read a traceback as no red check until it was made to look for the closing line; a crashed section now reads red. Carry: dismissed: repaired in this pull request's harness
- fixer.md: cost: the group was built stacked on its predecessor's open head by ruling, then waited a day for pull request 3461; the merge of main was clean and every figure was re-taken at this head. Carry: dismissed: sequencing decided by the orchestrator, no rule change asked
- fixer.md: unclear: `tests/entities.py` at this head exited 1 once in two whole runs, on "the location is redacted whole, from data and from options, not coarsened" and no other check, and exited 0 on the rerun and at 3af3edaabd9b; the diff touches nothing the check reads, and the first run shared the container with a `git fetch`. Carry: dismissed: one failure in three runs, not reproduced, cause not established
- fixer.md: cost: an in-place `mutant_run.py` run killed by a container restart leaves its mutant in the working tree (one line of `duty_switch.py` here, restored by `git checkout` before anything was committed); the remaining in-place runs were made in a scratch worktree. Carry: dismissed: the driver restores on SIGTERM and SIGINT, and a SIGKILL cannot be caught
- fixer.md: unclear: step 2's `## Unpinned sites` disposition "pinned by mutation-autofix" is accepted for a site with several mutants on one line (`*N` in step 6d's list), where it holds only if every one of them is killable; this group met an equivalent one twice (Red checks). A seat can check it by running the table's own mutants of a `*N` site against its section before choosing the disposition. Carry: dismissed: two instances in one group, under the third-instance threshold of CLAUDE.md's recurring-error rule; a third goes to root-cause with these two named
- fixer.md: cost: `mutation_table.py --pin-killed` on an anchor holding an equivalent site drives it through every driver in play before it can report a survivor, `tests/features.py` whole among them; the drive at e36f8af6f1b1 was stopped by this seat after its null control and replaced by the corpus probe under Repair round 2. Carry: dismissed: the price of proving a survivor, paid once
