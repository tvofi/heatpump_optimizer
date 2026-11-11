Fix review: blocked 7c7f06081827bbf9c52da7b2345b3a5a81048649 carry-missing: own-group -- Forward-carry items 2 and 3 route the design's own-seam items pair-other-asks, measured-fields, weekday-day and pv-price to R10-ADVISOR-STEADY-START itself, naming neither a pending ruling nor a split part, and two of them measure as open seams at this head

bus-nonce: a72c56389ad533ec1716b96fdece08b8
pending-ci: gate

Round 1 (first review; no earlier verdict). Measured at 7c7f06081827bbf9c52da7b2345b3a5a81048649, re-read as the head of fix/r10-advisor-steady-start and refs/pull/3481/head when this was written. Base: 61afd4f2db10341ab9b86583944402b206eb4c78 (the merge base with origin/main, which is origin/main here). `git merge-tree --write-tree origin/main <head>` exits 0 (tree 4d3c8b2a1afb): no conflict.

## Block

fix-review.md step 10 and fixer.md ("A finding in your own group's seam is built in this PR, not carried. `Carry: <own group>` only names a pending owner or orchestrator ruling, or a split part the approved plan names").

The body's Forward-carry items 2 (pair-other-asks) and 3 (measured-fields, weekday-day, pv-price) end `Carry: R10-ADVISOR-STEADY-START`, the pull request's own group, and landed on the round roster as that group's carries 6 and 7 (handoff/audit-r10-roster, read at ea774b53f; f4c4044aaa is its ancestor). Neither names a pending ruling or a split part: each says the design item "is not measured". The design note (55f90c7c6) states them as requirements of this fixer: pair-other-asks "confirm the fixture has a tank or measure on one that has, before the docs call that branch an estimate"; measured-fields "state the bound for a schedule ask on a throttling-valve two-tank fixture". The pull request closes #2257, the group's only issue, so no later seat of this group reads those carries.

Forward-carry item 1 (the ruling's real high-spread price day, roster carry 5) is not part of this block: it reports an unmet condition of the 2026-11-11 owner-side ruling, which is the orchestrator's to rule on, and the range that condition could trigger is built unconditionally.

The deferral is not harmless. I measured two of the deferred items with a probe of my own (ev/probe.py, ev/probe2.py: the reviewer's instrument, not the finder's; it builds the figure the way the finder's harness `_steady` does, from `whatif.schedule_days`, `price_tiles.schedule_figure` and `price_tiles.monthly_deltas(steady=)`, on tests/profiles.py houses, and does not go through `async_simulate`). Both read against the body's first sentence ("no longer moves with where the house starts or with the plan's age, and a schedule ask reads on its own side of 0") and against docs/dashboard-card.md:480 ("Either way the figure does not move with where the house happens to be when you ask"). They are the first two bullets under Findings; what unblocks is each of the four items measured in this pull request and either fixed or disclosed in the docs paragraph with its control, or the orchestrator's ruling that splits them out by name. Carry: R10-ADVISOR-STEADY-START

## Findings

- Open seam, item weekday-day: with weekend comfort temperatures configured (`comfort_temp_day_weekend` 22.0, `comfort_temp_night_weekend` 20.0) the schedule figure of one ask moves with the weekday it is asked on. Same prices and weather every day, asked 09:00 Monday to Sunday: a degree warmer by day reads +68.2 +68.2 +68.2 +68.2 +55.1 pair +3.7; a degree cooler by night reads -1.8 -1.8 -1.8 -1.8 +0.0 pair +0.0 ("pair": the next 24 h hold no changed setpoint, so the ask leaves the schedule branch). Null control, no weekend comfort: +68.2 and -1.8 on all seven days. Across a Friday (2026-01-09) at hours 01..23 step 2, 18 of 90 schedule rows are not strictly on the ask's side of 0 (all read 0.0 with differing setpoints) and 6 read the pair (ev/reviewer_probe.log, ev/reviewer_probe2.log). The figure prices the next 24 hours' setpoints and multiplies by 30.4; no sentence in docs/dashboard-card.md, price_tiles.py, whatif.py or `reference_day` says so, and no check in tests/features.py or either steady harness uses a weekend temperature or a start other than a Wednesday. Carry: R10-ADVISOR-STEADY-START
- Open seam, item pair-other-asks: on a tanked house (tests/profiles.py `house(dhw=True)`) the steady pair's figure for a hot-water ask alone moves with the measured tank temperature and turns sign with the hour. `dhw_setpoint` 55 to 50, by start (rooms at target, rooms coasted, tank 44, tank 58): 01:00 +29.1 +29.1 +20.0 +4.9; 09:00 +25.3 +25.3 +19.8 -12.7; 17:00 -14.4 -14.4 -17.3 -7.7. `dhw_setpoint` 55 to 60: 01:00 -8.0 -8.0 -11.5 -11.5; 17:00 +32.2 +32.2 +26.4 +42.8. Null control: the room and slab start moves it 0.0 on every row (columns 1 and 2), so the held start does what it claims and the tank is what moves the figure; spread by tank start up to 37.9 a month (ev/reviewer_probe.log). The card labels this figure "in steady state" and the docs disclose only the wood tank's charge. Carry: R10-ADVISOR-STEADY-START
- Surviving mutant, mine, not one the body names: custom_components/heatpump_optimizer/services.py `handle_simulate_plan` calling `coord.async_simulate(overrides)` without `steady=True` leaves tests/features.py at the control's count (1 of 5278 red on a copy with no .git, the same one as the unmutated copy) and tests/entities.py, tests/deployment_shape.py, tests/doc_claims.py, tests/debug_collect.py, tests/manual_plan.py, tests/config_flow_steps.py and tests/finite_boundary.py green, and tests/dst_checks.py at the unmutated head's own count (ev/mut/f_service_no_steady.log, ev/mutant_f_worktree.log, ev/mutant_f_other_scripts.log). That argument is the only thing that puts the steady key in the answer the card reads, so with it gone every what-if in the panel shows no money and the suite stays green; a dropped keyword argument is not an operator of the `mutation` lane, so CI does not draw it. Carry: R10-ADVISOR-STEADY-START
- Residual: on the two-zone house the schedule figure moves by up to 0.30 a month across five measured states (rooms, slab, tank and buffer varied), 0.00 on the single-zone one (ev/reviewer_probe.log, first four RESULT lines); tests/features.py "the day energy does not move with the measured house" reads a single-zone house only. Two thermostat passes do not fully settle the two-zone model. Carry: R10-ADVISOR-STEADY-START
- Residual: the body's suite line is stale. It says tests/features.py is 1 of 5278 red at the head (main's combi census); at this head, which holds the merge of main, it prints `ALL 5278 FEATURE CHECKS PASSED` (ev/features_head.log), and the Red checks entries for `tests / fast (3.14)` and `governance / instrument-self-tests` describe reds that are green on this head's runs. Carry: R10-ADVISOR-STEADY-START
- Residual: `tests / mutation` is red at this head and the body answers it (32 unpinned sites, `mutation-autofix`, detector `tools/pr/ci_predict.py`); `tests / mutation-pins (1..7)` were still in progress when read, and the bot's pin commit will move the head off the one this verdict names. Carry: dismissed: the relay refuses a verdict whose head moved, and the next round is the delta

## Evidence

Everything below is at 7c7f06081827bbf9c52da7b2345b3a5a81048649 unless a base is named; logs are under ev/.

Step 1, mutation proof (ev/mut/*.log, ev/mutants_summary.txt, driver ev/mut.py: one edit on a `git archive` copy of the head, then tests/features.py; the unmutated control copy is 1 of 5278 red, the #363 `recorded_at` check a copy without .git fails). Red checks counted over the control's one:
- `whatif.schedule_days` returns None always: 10 red (body: 9 more than the copy's own).
- `reference_day` on the horizon's own weather (M3): 4 red.
- `reference_day`'s second pass without `start=`: 7 red (body: six).
- sides exchanged in `schedule_figure` (M6): 7 red.
- second pricing at the mean price: 2 red.
- the pair also solved on a schedule ask (M9): 5 red.
- mine: mean price replaced by the horizon's first price 2 red; `if inputs.held_start` switched off 4 red; the kept live side reused whatever the key 2 red; the fuse advisor reading the settled key 3 red; the cap tile asked without `steady` killed; wood's `extra` dropped from `schedule_figure` 3 red; the shifted price's finite-and-positive guard dropped 2 red.
- card (ev/card_mutants.log, driver ev/cardmut.py, tests/plan_view.py then `node tests/card.mjs`; control ALL CARD CHECKS PASSED): the basis always `whatif.basis_plans` 3 red, the three "#2257:" titles the body lists; money falling back to `monthly_cost_delta` 1 red, the title the body lists; the range replaced by its larger end 3 red.
- The body's M2, M7 and M8 mutants I did not re-run.

Step 2, the finder's harness dev/audit/harnesses/r10_advisor_residue.py `whatif`, each tree's own copy:
- base 61afd4f2d: `RESULT whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0`; caps `plan 18/36 settled 1/36`; no steady line (the base's copy has none).
- head: `RESULT whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0`; `RESULT whatif steady rows 24 steady_moves_by_start 0 degree figures against the held sign 0/36 cap figures reading a saving (< -1) 0/36 cap range -0.7..+46.0`; caps `plan 18/36 settled 1/36`.
- head `steadysign`: `RESULT steadysign rows 48 steady_wrong_sign 0 held_wrong_sign 0`.
- The harness's steady column is the fixer's addition to the finder's harness (`_steady`, `arm_steadysign`): it rebuilds `async_simulate`'s branch from `whatif` and `price_tiles` calls and does not call `async_simulate`. The base's copy cannot run on the head (it imports `_SIM_OVERRIDE_CONFIG_CASTS`, which moved). The answer's own key is read by the carrier's `built` line and tests/features.py.
- Not re-run: `steady_wrong_sign 1` at 20da1edf6.

Step 3, null controls re-run: `PRICES=flat` bracket prints the three pricings within 0.2 a month on 96 of 96, both ratios 1.000..1.000; `PRICES=peaks` prints ratio mean-price / realised-price 2.104..3.136 above 1.5 on 96 of 96, minimum-price ratio 3.190, against the ask 0, range on 96; `reference_day` median 2.0 ms a call on this box (max 3.7 and 5.7 ms). Carrier `AGE=2 STEP=4`: `built: schedule figures 96 against the ask 0, solved once on 96; no-schedule asks 36 on the pair (2 or 3 solves) 36, zero ask exactly 0.0 on 12 of 12, cap below -1 on 0`; `off` 18, `at` 3, `offm` 24, `atm` 0, `m2` -11.8..-2.6; `ERRORS 0`. The other bracket series (sawtooth, diurnal, spread2) and the other four carrier points I did not re-run.

Step 4: `python3 tests/env_drift.py --all origin/main` prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`; the diff touches nothing under tests/golden and neither claim file.

Step 5: `git diff <base> <head> -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty.

Step 6, other configurations (ev/reviewer_probe.log): the schedule branch on single-zone and two-zone houses, with and without a hot-water tank, six asks at hours 01..23 step 2: 72 rows each, against the ask 0 on all four houses. The body names no enumeration rule; #2257's remaining item is one seam (the panel's money line), and the two open seams above are the design's own deferred items, not a rule's output.

Step 7: the body's `## Head` names 7c7f06081827bbf9c52da7b2345b3a5a81048649.

Step 8, figures I could not or did not re-derive: the archscore dS (+0.0273, stated as taken before a later edit and not re-run by the fixer either; `arch-score / arch-score` and `tests / arch-instrument` are green on this head's runs), the closures re-recording, the Pi-class wall estimate, the solve counts beyond the carrier's `built` line.

Step 10: roster group R10-ADVISOR-STEADY-START on handoff/audit-r10-roster at ea774b53f holds 8 carries; 2 to 4 are marked dismissed as duplicates of 5 to 7, as the dispatch said. Carries 5 to 7 are the body's three items verbatim, each with its control or its "not measured" statement.

Step 11, live check runs at the head (72 runs read, not the body's account): `tests / mutation` failure, named and answered in the body; `tests / replay`, `tests / nightly-status` and `CodeQL` failure, none in `merge_train.py owed-reds`' set; an earlier `gate` run failure and a later `gate` run in progress; every other required context success. `merge_train.py classify` printed `WAIT 7c7f06081827bbf9c52da7b2345b3a5a81048649 pending: gate red: none` from 21:54Z to 22:53Z (ev/classify.log, ev/classify_final.txt); I stopped waiting there, hence the pending-ci line.

Step 14: tests/structure_budgets.json moves nine metrics, all down, none up (`python3 tests/structure.py` prints STRUCTURE RATCHET PASSED; `budget-raise-gate` success). The mechanism is the what-if's state, override casts and branch moving to custom_components/heatpump_optimizer/whatif.py; I did not remove it as a null control or plant a like move.

Step 15: no `homeassistant` import in whatif.py or price_tiles.py's additions; state is a per-coordinator WeakKeyDictionary; `reference_day` reads no instance state `optimize` stashes (`_compute_baseline_power`, `_build_comfort_bounds`, `_thermostat_held_state` read `self.model` and `self.config` only). Departures from the design note are the three the body lists.

Suite: `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/features.py` prints ALL 5278 FEATURE CHECKS PASSED; tests/entities.py ALL 2705 ENTITY CHECKS PASSED. The scoped gate and the mutation table are CI's and were not re-run. tests/dst_checks.py prints 8 of 137 red on this container at the base and at the head alike, the same eight titles (ev/dst_base.log, ev/dst_head.log): this box's timezone environment, not the diff.
