R11-OUTSIDE-START-APPROACH. The finding and its series are Bankaifan's (comment 6944433306 on #3670), with thanks: on an on/off install a space run entered from off draws well above its 0.53 kW floor for most of an hour (series D), and the compressor winds down for minutes after the gate write (series H), while the plan booked the floor and an off step. Approved design: design/R11-OUTSIDE-START-APPROACH at 869c3441a3 (Design review: approve, design-verdict 35468574ca). This pull request leaves #3670 open.

What it does. `approach.py` (new, pure) learns the draw by 5-minute age bin after a space-run entry (a step with a space level after one with none) while the ask sits at the floor in force, and after a run's end while nothing is asked; `draw_range.fold` hands it each settled interval (`Span`), a hot-water dwell moving only its clock. `runs.received` reads a plan's space draw through it; the true objective simulates and costs that draw (`optimizer._shipped_and_received`, the stop's share applied after it), the start and switch terms still read the shipped plan, `runs.commit` books the entry's energy on a move out of a pause (`runs.Start`), and both solves publish the received trajectory. On the meter side the coordinator files `draw_range.expect` as the interval's predicted power, the fabric tracking gate reads it, the promise is costed on `draw_range.received_schedule`, and while the interval sits inside the profile the COP judge refuses it (`MeasuredCop.judge_floor`, `COP_REFUSED_OFF_ASK`) and the draw window takes no pair. The plan's band stamp carries the entry energy (`SolveBand.approach_kwh`), shown on the status sensor's `pump_min_power` row.

Base: worktree cut from `origin/main` 0e1eba2b4aafb5dbabbac7e0b0dc31b6ca1ad83e, with the predecessors' pull-request heads merged in as two separate merge commits (pipelined start, orchestrator workaround): #3805 (R11-OUTSIDE-HONEST-DHW-RUNS) at d74d12dd22842adaa5576e06d78f0956ed61f7f4, then #3835 (R11-SEAM-learners) at 7748bdc269efb9758d85b4ee81130a4f60534948, merge commit d972dae309 (two record-text conflicts resolved: `tests/deployment_shape.py` and `dev/audit/rounds/round4/D6/claims.py`, both counting the package's files). Every figure below diffs against d972dae309, so the diff the reviewer reads is this group's alone: `git diff d972dae309...HEAD`. Production files: 8 (`approach.py`, `runs.py`, `draw_range.py`, `store.py`, `optimizer.py`, `coordinator.py`, `accuracy.py`, `sensor.py`), not above eight, so one pull request (orchestrator ruling under mandate 6893738184).

## Head

`23bceb0f279e210da6446fedd9191d294b8d53a5` is this repair's head, measured on `origin/main` `190ffb10c230b6beaf77593b2926d55682e37f47` at 2026-11-27T04:53Z. It adds two commits to `4f7aaaa94b` (which merged `origin/main` `fd93aa3e9b` into `95c0bc2719`): `4070ef1fac` merges `origin/main` `190ffb10c2`, because `git merge-tree --write-tree origin/main 4f7aaaa94b` exits 1, and `23bceb0f27` splits one docstring sentence. Delta for review: `git diff 46cdd1f9191180fc1f420a0d5eedd0f758b947ad 23bceb0f279e210da6446fedd9191d294b8d53a5`, of which this group authored only the `dhw_charges.py` docstring lines; the rest is main's and the merges' record text.

- `4070ef1fac`: five record-text conflicts. Main replaced the module counts with structural claims (`docs/architecture.md`, `dev/audit/rounds/round4/D6/claims.py`, `tests/deployment_shape.py`), so each conflict hunk takes main's side; `git diff origin/main 23bceb0f279e210da6446fedd9191d294b8d53a5 -- docs/architecture.md` is the two module-map rows this branch adds (`approach.py`, `dhw_charges.py`), and `claims.py` and `deployment_shape.py` equal main's. `claims.json` and `claims.md` are `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`'s own output on the merged tree, rc 0.
- `tests/structure_budgets.json` `module_excess_loc` is main's 21646. `4f7aaaa94b`'s 21599 credited one move twice: this branch's and main's #3863 moved the same start helpers out of `dhw_planner.py`. The breach this leaves is #3805's (`## Red checks`).
- `23bceb0f27`: `4f7aaaa94b` rewrote `dhw_charges.py`'s module docstring into one sentence over the comment ratchet's 40 words; it is split where #3805's head splits it. Rule: `PYTHONPATH=tests/hastub:tests python3 -c "import comment_ratchet as c; [print(r) for r in c.gate('origin/main')]"`: at `4070ef1fac` `REFUSE scope total: long units 2295 -> 2296` (the new unit: `dhw_charges.py:1`, by a per-file compare of `comment_ratchet.counts` at base and head), at the head pass.
- At the head: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` `ALL 445 checks PASSED`; `node tools/policy/brief_lint.mjs` rc 0; `PYTHONPATH=tests/hastub python3 tests/entities.py` `ALL 2792 ENTITY CHECKS PASSED`, rc 0; `GOLDEN_MODE=drift GOLDEN_REF=190ffb10c2 PYTHONPATH=tests/hastub python3 tests/golden.py` `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`. The claim files differ from `190ffb10c2` only by #3805's two claim lines (`cycling_cost`, `everything_on`) and its two suspended may-drift entries; this group claims nothing. `VERSION`, the manifest and `RELEASE_NOTES.md` are byte-identical to `190ffb10c2` (`git diff --quiet` rc 0).
- At `4070ef1fac` (same production code as the head): `PYTHONPATH=tests/hastub python3 tests/features.py` under coverage 7.17.3 (`coverage run --parallel-mode --source=custom_components/heatpump_optimizer`, threads pinned to 1): `ALL 6332 FEATURE CHECKS PASSED`, rc 0; `approach.py` 97.39 % (115 statements, 3 missed: 173, 218, 227), `runs.py` 100.00 % (171), `comfort_floor.py` 100.00 % (20).
- `tests/closure.py select --diff 190ffb10c2`: `MODE: FULL` (`tools/ci/selftest_closures.json changes the gate itself`: #3805's `dhw_charges.py` entries), so no scoped list exists; the scripts above and `tests/run.sh` (below) are what ran.

The figures from `## Mutation proof` to `## Architecture score` below are the measurements of the heads each one names; this repair changed no production line but the docstring, so none is re-taken.

## Mutation proof

Rule: each target's production line replaced as listed (a scratch driver whose list is this table), the block run, the failing check names printed, the line restored. Block: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("PRELUDE").read())' "R11-OUTSIDE-START-APPROACH: a run's"`, PRELUDE written by the same command with `--emit-prelude PRELUDE` (the `_t2_coord` the coordinator checks read).

| target (design's mutation list) | file: line replaced | checks red |
|---|---|---|
| the floor-ask gate | `approach.py` `ApproachProfile.observe`: `split[0] <= (1.0 + tolerance) * floor_kw` -> `True` | approach learner folds nothing from a frozen, a distorted or a defrost interval, nor an entry asked above the floor |
| the count gate | `approach.py` `_levels`: `len(b) < MIN_COUNT` -> `len(b) < 1` | approach learner: zero evidence and two runs (bins under MIN_COUNT) read no approach; ... |
| the median | `approach.py` `_levels`: `np.median(list(b))` -> `max(b)` | approach learner: ... (the outlier run's first bin) |
| the age reset | `approach.py` `ApproachProfile._clock`: `self.entered_s = start_s` -> `pass` | approach learner: ... |
| the live age at step 0 | `runs.py` `_received_row`: the step-0 age -> `None` | runs.received of a batch is the one-row answer per row, bit for bit, the live age continued at step 0 |
| the max with the shipped level | `runs.py` `_mean_excess`: `max(float(levels[j]) - shipped, 0.0)` -> `float(levels[j])` | runs.received: a 15-minute run from off ...; a charge before a space run ...; runs.received of a batch ... |
| the `p_max` bound | `runs.py` `_received_row`: `min(add, max(p_max - hot - shipped, 0))` -> `add` | runs.received: a 15-minute run from off ... |
| the ramp-down's previous-interval gate | `approach.py` `observe`: `quiet and was and drawn_kw` -> `quiet and drawn_kw` | the first pause interval after a space run folds a ramp sample and no idle reading; ... |
| the true-objective-only guard | `optimizer.py` `_shipped_and_received`: `space if descent else runs.received(` -> `runs.received(` | the true objective's received draw is runs.received of the shipped plan; ... |
| the objective call removed | same line -> `space if True else ...` | the true objective's received draw ...; the published trajectory ... (space-only and hot-water solves) |
| the received order under a priced stop (note s6) | `optimizer.py` `_shipped_and_received`: `delivered_space(received, ...)` -> `delivered_space(space, ...)` | under a priced stop the received draw is the stop's share of the approach's draw; ... |
| the commit action's pause test | `runs.py` `_entry_action`: `(0.0 if ran else entry_kwh)` -> `entry_kwh` | runs.commit: no entry energy leaves the masks equal; with the learned entry ... within half a floor step |
| entry read off the combined draw (case 2) | `runs.py` `_received_row`: `on = shipped[k] > MIN` -> `shipped[k] + hot[k] > MIN` | a charge before a space run leaves the run an entry while the combined draw starts once; the published trajectory ... (hot-water solve) |
| the published trajectory's call, hot-water solve | `optimizer.py` `_optimize_with_dhw`: `_shipped_and_received(...)[2]` -> the shipped-plan `delivered_space` it replaced | the published trajectory ... (hot-water solve) |
| the published trajectory's call, space-only solve | `optimizer.py` `_optimize_space_only`: `_space_traj(_shipped_and_received(...)[2])` -> `_space_traj(optimal_power)` | the published trajectory ... (space-only solve) |
| the window gate inside the profile | `draw_range.py` `fold`: `None if kind else drawn_kw` -> `drawn_kw` | the first pause interval ... no idle reading; the COP fold refuses ...; the expected draw of an entry step ... adds no window pair |
| the ramp gate ahead of the idle store (note s3) | same line, the ramp arm only | the first pause interval after a space run folds a ramp sample and no idle reading; ... |
| the gap reads unknown (note s5) | `approach.py` `_clock`: `gap = seen is None or start - seen > end - start` -> `gap = seen is None` | after a gap the live run's age is unknown and no entry sample is folded across it |
| case 7: the pending power back to `_commanded_power()` | `coordinator.py` `_record_accuracy`: `"power": draw_range.expect(...)` -> `"power": self._commanded_power()` | the coordinator files the expected draw ...; the COP fold refuses ...; the fabric interval ... |
| case 7: the inside-profile flag forced false | `approach.py` `ApproachProfile.expect`: `self.expected_kw = total_kw if inside else None` -> `None` | the COP fold refuses ...; the fabric interval ...; the expected draw of an entry step ... |
| case 7: the promise filed from the shipped schedule | `coordinator.py` `_file_lead_predictions`: `space = draw_range.received_schedule(...)` -> `space = result.power_schedule` | the coordinator files the expected draw ... and the promise costed on the received schedule ... |
| the fabric tracking gate's reference | `coordinator.py` `_interval_space_power`: `inside_approach(...) or commanded` -> `commanded` | the fabric interval of an entry inside the learned approach keeps its metered space figure ... |
| the COP judge's approach arm | `accuracy.py` `MeasuredCop.judge_floor`: `if experiment or approach:` -> `if experiment:` | the COP fold refuses ...; the expected draw of an entry step ... the COP judge refuses it ... |
| the COP judge's wiring | `coordinator.py` `_fold_measured_cop`: `inside_approach(draw) is not None` -> `False` | the COP fold refuses the interval filed inside the approach as off its ask ... |
| the hot-water dwell's clock-only arm | `coordinator.py` `_record_accuracy`: `Span(..., heat_energy.ran_hot_water(...), ...)` -> `Span(..., False, ...)` | **SURVIVED** this block and the R11-SEAM-learners unplanned-charge block (`features_block.py --prelude ... "R11-SEAM-learners: the unplanned-charge evidence" 'R.section("R11-OWNER-CARD-EXTERNAL-HEAT'`, 19 checks pass at both ends). Disposition under `## Unpinned sites` |

## Null control

The unmodified tree (d972dae309) has no `approach` module and no `runs.received`, so every check in the block fails to import there; the block's own nulls are each check's second arm: no learned profile (or a bin under its count) gives `None` and the shipped array itself (`is`), the shipped total as the expected draw, the shipped schedule as the promise, the fabric interval skipped as tracking, the COP judge reading the floor as before, the base masks equal with no entry energy, and the published trajectory equal to the shipped plan. The brief's null: a run already at the floor has no excess (harness arm `approach`, `null, a run at the floor`). `GOLDEN_MODE=drift` against d972dae309: no golden fixture moves (no fixture carries approach evidence), so no claim line is owed and both claim files are byte-identical to d972dae309.

## Figures

Every figure is at the head named above, against base d972dae309 (the predecessor merge), unless a line says otherwise.

- Block, 18 checks: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("P").read())' "R11-OUTSIDE-START-APPROACH: a run's"`, P written first by `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --emit-prelude P "R11-OUTSIDE-START-APPROACH: a run's"`: `ALL 18 FEATURES BLOCK PASSED`. At d972dae309 the block cannot import `approach`, which that tree does not have.
- Whole script: `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 6256 FEATURE CHECKS PASSED`, rc 0 (at 6e6b19d039; the block, rerun at the head, passes 19).
- Harness arm (synthetic; series D's shape as the design states it, not the raw series): `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py approach`. Rule for the excess: sum of (kW - 0.53) x 5/60 over 5-minute means of 1.25 kW falling 12.6 W/min to the floor. Printed: excess 0.373 kWh over 65 min (the design's spike s1 read 0.377 on the raw series); runs from off of 15, 30, 45 and 60 min meter 2.24, 2.06, 1.88 and 1.70 times a plan at the floor; null, a run at the floor: excess 0.000 kWh. Five such runs folded through `draw_range.fold`: entry 0.371 kWh over the floor, ramp level 0.785 kW. A clamped 0.53 to 3.0 kW house at 5 C, solved with no approach and with the learned one: 1.0 off-to-on edges per day each, shipped 9.75 kWh each, received 9.82 and 9.81 kWh, received energy cost 1.210 each, lowest room 19.94 and 19.95 C, 13 steps over a 1.0 kW cap shipped and received each. Null: exit 0 asserts the plan with no approach receives its shipped array itself.
- Structure: `PYTHONPATH=tests/hastub python3 tests/structure.py`: every budget held; re-recorded down (commit 'R11-OUTSIDE-START-APPROACH: re-record two structure rows this change lowered'): `class_excess_loc` and `in_function_copies`, each lowered by the payments below.
- Architecture score: `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff d972dae309`: `Architecture score: dS +0.0000 NULL`. Before the payments it read WORSENS on `shared_inplace_writes`, `duplication_copies`, `params_over_10`, `coord_footprint`, `literal_clone_copies` and `dead_members`. Payments, each its own commit and none a step-17 shape: the expected draw is kept by `ApproachProfile.expect` (an own write, not one into the profile from `draw_range`); `approach.stored_config` is the one parse of a stored record's configured range, `DrawRange.from_dict` reading it too (the clone it formed); `draw_range.Span` carries the experiment flag and `runs.Start` the entry energy, so `fold` and `runs.commit` keep ten parameters; the promise schedule is bound before `note_promise`, which stays a delegation; `_analyze_forecast_trajectory` computes its two identical 12 h decay weights once (paid `optimizer.py`'s lines, design note s4).
- Golden drift: `GOLDEN_MODE=drift GOLDEN_REF=d972dae309 PYTHONPATH=tests/hastub python3 tests/golden.py`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against d972dae309` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. No fixture carries approach evidence, so none may move; `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to d972dae309 (`git diff --quiet d972dae309 HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo IDENTICAL` prints IDENTICAL).
- Closures: `./tests/derive_closures.sh --scripts-from F --record-only --out-dir D`, F the 28 scripts whose committed closure held `draw_range.py` (approach.py's one importer), then `python3 tests/closure.py merge --in-dir D --partial --allow-failures`: 28 closures updated. `PYTHONPATH=tests/hastub python3 tests/entities.py` then reads every tracked file measured; the deployment-shape note reads 124 package files and 191 of 561 pairs at >= 0.80 (the numbers that script derives).
- Comment ratchet: `PYTHONPATH=tests/hastub:tests python3 -c "import comment_ratchet; [print(p, n) for n, p, d in comment_ratchet.gate('origin/main')]"`: long units 2299 at base and head.
- The axis (design note s8), the four roads at d972dae309 and at the head, each `| wc -l` over `custom_components` (R3 and R4 over the files the design names): R1 `git grep -n "_commanded_power()\|_commanded_split()"` 25 and 25, one line's text changed (the pending power, now `draw_range.expect`: E); R2 `git grep -n 'predicted_power_kw\|pending\["split"\]\|pending.get("power")'` 14 and 13, the one gone being `_record_accuracy`'s fold condition, whose attribution moved into the fold call's `Span` on a line R2 already returns; R3 `git grep -n "plan_promise(\|power_schedule"` 19 and 19 (the promise now files `draw_range.received_schedule`: E); R4 `git grep -n 'action.get("power"\|get("dhw_power"'` 10 and 10. Every line keeps the design's disposition (its axis section and the verdict's v2-1); as built, E is the pending power, the fabric tracking gate (`_interval_space_power`, reading `draw_range.inside_approach`) and the promise, and G is the COP judge and the draw window.
- Mutation proof: the table above, 25 targets, 24 red, 1 survivor dispositioned under Unpinned sites.
- Production files: 8, `git diff --name-only d972dae309 HEAD -- custom_components | wc -l`.

## Unpinned sites

- `coordinator.py` `_record_accuracy`, the `Span`'s third field (`heat_energy.ran_hot_water(...)`, whether the settled dwell saw hot water): the hand mutant forcing it `False` survives this block and the R11-SEAM-learners unplanned-charge block. Under the mutant such a dwell reaches `fold`'s other arms; it cannot be a window or idle sample there only where its split asks hot water, and the observable left is the steady-run map's commit timing and an approach sample on a dwell whose split asked space. The arm keeps the base's rule that such a dwell reaches no fold arm but the run clock. A check needs the heat meter's dwell attribution driven to `ran_hot_water`, which no fixture in `tests/features.py` builds today. Disposition: unpinned, stated; `prepr.sh`'s sampled survivors are listed below. Carry: R11-OUTSIDE-START-APPROACH (pending orchestrator ruling: pin by a meter fixture, or accept)

Rule: every site `prepr.sh` step 7d lists for this diff (93), each `file:line KIND` as it prints it. Disposition for each: a production site under `custom_components/`, so `mutation-autofix` pins the ones the suite kills; the hand mutants above already drive the lines that carry the behaviour.

- `custom_components/heatpump_optimizer/accuracy.py:1305 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:35 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:38 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:41 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:43 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:45 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:47 CONST`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:96 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:99 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:101 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:101 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:104 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:104 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:105 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:106 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:106 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:108 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:109 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:115 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:118 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:118 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:120 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:120 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:122 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:124 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:130 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:136 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:138 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:138 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:140 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:156 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:163 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:172 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:172 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:174 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:184 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:189 CMP_BOUND*2`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:189 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:196 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:196 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:197 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:205 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:205 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:207 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:208 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:208 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:211 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:217 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:217 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:219 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:226 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:226 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/approach.py:228 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:5346 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/coordinator.py:9940 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:578 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:905 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:905 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:908 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:966 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:972 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:996 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1001 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1001 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1003 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1020 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1020 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1027 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/draw_range.py:1029 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/optimizer.py:356 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:79 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:79 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:140 CLAMP_DROP*2`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:141 CLAMP_DROP*2`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:142 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:142 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:143 CLAMP_DROP`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:144 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:163 BOOLOP`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:163 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:167 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:169 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:177 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:178 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:180 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:181 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:186 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:189 CLAMP_DROP*2`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:191 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:324 CMP_BOUND`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:324 GUARD_OFF`: mutation-autofix
- `custom_components/heatpump_optimizer/runs.py:326 RETURN_DEL`: mutation-autofix
- `custom_components/heatpump_optimizer/sysid.py:2508 GUARD_OFF`: mutation-autofix (`arm_refusal`'s switch, read from the configuration at the head; the ledger pin on its old text, `arm_refusal GUARD_OFF 2569c66f`, is dropped because the line it named is gone)

`prepr.sh`'s sampled mutants (`mutant_run.py`, the first 40 of the diff's added lines, `MUTANT_CMD` the block above) left 13 survivors at 89316354b5; six now fail the learner-boundaries check (re-driven by the hand-mutant driver: the ask at the tolerance edge, the covered age, the standby draw, the one-interval gap, the gap inside a live run, `MIN_COUNT`). The other seven:
- `approach.py:38`, `:41`, `:43`, `:47` CONST_SWAP (`BINS`, `RAMP_BINS`, `DEPTH`, `_SLACK`): constants from one install's series, named so in the module (design note s2); no value is pinned, by design.
- `approach.py:107` CONST_SWAP (the ramp age's minutes divisor): only the first interval after a run's end is a ramp sample, at age 0, so the bin is 0 under either divisor; equivalent.
- `approach.py:109` RETURN_DEL (`return None` -> `pass`): the implicit return is `None`; equivalent.
- `accuracy.py:1285` CONST_SWAP (`experiment` defaulting `True`): every production caller passes `experiment`; the default is read by none.

## Departures from the architect note

Each raised here for the reviewer and the orchestrator; none changes the approved shape's owners or its axis dispositions.

1. No coordinator accessor beside `_commanded_power`. The expected draw is `draw_range.expect`, called where `_record_accuracy` files the pending prediction (its `"power"`), and the profile keeps it (`ApproachProfile.expected_kw`, by its own method) for the interval's readers when it settles (`draw_range.inside_approach`). Measured: the accessor put the coordinator class over `max_class_loc` and `seam_cut_total` 413 -> 416 (`tests/structure.py`); a pending-dict read in the two readers cost the same two cuts.
2. `accuracy.py` is touched: `MeasuredCop.judge_floor` takes `approach` beside `experiment`, the same `COP_REFUSED_OFF_ASK` for the same reason (drawn over asked is no efficiency reading). `_fold_measured_cop` sat at CC 15, and a gate of its own there crossed `functions_cc_over_15`.
3. The status attribute is a key of the existing `pump_min_power` row (`approach_kwh`, stamped by `draw_range.solve_band` on the plan's `SolveBand`), not a separate attribute: no coordinator payload line.
4. A bin under its count ends the profile (the note: reads as none); the profile is contiguous from age 0.
5. The ramp level is read against the floor, as the entry is.
6. Residue named, not changed: `optimizer.py`'s `predicted_cost` (`paid_cost_of(optimal_power)`) and `_replay_end_state` read the shipped plan (category P: published, no meter in the expression).
7. Spike s1's figures are re-derived from series D's shape as the note states it (1.25 kW falling 12.6 W/min), not the raw series, which is in no tree: 0.373 against the note's 0.377 kWh.

## The note's carried items, as built

- s1: harness arm `approach` prints the figures (Figures). s2: `approach.py`'s constants are named one install's. s3: measured: the series-H interval held at the gate reaches the idle store at the base rule (the ramp check's null arm reads it as an idle reading), so the ramp arm goes ahead of it (`fold` hands `_fold_window` no draw for a ramp interval). s4: paid in the same files (Figures, structure and architecture score). s5: the run's clock is stored (`entered_s`, `ended_s`, `seen_s`, `running`), an interval after a gap longer than itself reads the age unknown, and the expected draw is not stored. s6: pinned (the priced-stop check). s7: credited in every commit and here. s8: Figures, the axis rule. r1: case 7 as the coordinator checks (pending power, promise, fabric gate, COP fold); the defrost derate and `power_ratio` read the pending power through `AccuracySample.predicted_power_kw`, pinned at that power, not at the derate. v2-1: the four R4 lines stay on the shipped split, unchanged. v2-2: `ledger.py`'s `meter_calibration` reads the pending power, pinned at that power.

## Architecture score

- `coord_footprint` 2526 -> 2529 (`python3 tools/audit/archscore/score.py --diff 76dd8811d4` at `c1d1056a0c`, and CI's `arch-score` at `4ded335674`: `Architecture score: dS +3.1822 WORSENS (inadmissible: coord_footprint 2526->2529)`, with `shared_inplace_writes` 2 -> 1) is the predecessor R11-SEAM-learners' (#3835) rise, which this branch merges (`d972dae309`), not this group's. #3835's own body explains it as the evidence plumbing its design places in the coordinator, and its `arch-score` passes on that explanation. Rule: `archscore.metrics.footprint.measure`'s per-function `charged` list at `76dd8811d4` and at `c1d1056a0c` differs only in `_async_learn_heat_span` 4 -> 11, `_observe_heat_energy` 0 -> 1, and the new `_freeze_facts`, `_space_evidence` and `_ceiling_frozen` at 1 each. `git log -G` attributes every one of those to R11-SEAM-learners commits `8143a4dff3` and `77eec1d8b4`. Null control for this group's own delta: `score.py --diff d972dae309` (`## Figures`) reads `dS +0.0000 NULL`. The sysid commit at the head charges no coordinator function.

## Red checks

The owed set is `python3 tools/audit/seat/merge_train.py owed-reds`; of the reds on `46cdd1f9191180fc1f420a0d5eedd0f758b947ad` (run 45770726310) it holds `tests / fast (3.14)`, `tests / coverage-ratchet`, `tests / mutation` and `gate`. Logs read through the GitHub API's job-log read, which serves a log's last 5000 lines; the full log's blob host is refused by this seat's network policy (`curl: (56) CONNECT tunnel failed, response 403`), and `tools/audit/seat/failure_logs.sh 3907` exits 2 with no `gh` here.

- `tests / fast (3.14)` (job 139744834382): `1 TEST SCRIPT(S) FAILED`; the failing script's section sits before the 5000 lines served. At this head, `PYTHONPATH=tests/hastub bash tests/run.sh` (local, at `4070ef1fac`) read `4 TEST SCRIPT(S) FAILED`:
  - `tests/structure.py`: `FAIL module_excess_loc 21695 > 21646 (+49)`. #3805's, not this group's, and not repaired here (the brief). Rule: each module's span past `MODULE_LOC_LIMIT` (2000), summed, as `tests/structure.py`'s `module_excess` reads it, at four trees: `origin/main` 21646; #3805's merge-base `1d3077736d` 21647 and its head `4a6e24c197` 21696 (`optimizer.py` 4768 -> 4808, `dhw_planner.py` 193 -> 202); this head 21695 (`optimizer.py` 4808, `dhw_planner.py` 202, every other module equal to main's). Null control: the same rule at `46cdd1f9191180fc1f420a0d5eedd0f758b947ad`, where `tests/structure.py` reads `STRUCTURE RATCHET PASSED`, because that tree still carried this branch's move of the start helpers, which main's #3863 has since made. This group's own delta on the row is 0. Cheaper detector: `tests/structure.py`, 29 s, which caught it here before any push. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (its +49 is paid or raised on #3805, which merges first)
  - `tests/doc_claims.py`: the comment ratchet, `long units 2295 -> 2296`, from `4f7aaaa94b`'s docstring; repaired at the head (`## Head`). Cheaper detector: `tests/doc_claims.py` itself, 30 s, which `4f7aaaa94b`'s seat recorded as not re-run after its last edit; process state (b), followed now. Carry: dismissed: repaired in this pull request
  - `tests/entities.py`: `FAIL the template arm turns the acceptance red ...` with the real template `rc=1`. Not reproduced alone: `node tools/policy/policy_lint.mjs` rc 0 at this head and at `origin/main`, and `tests/entities.py` alone at the head reads `ALL 2792 ENTITY CHECKS PASSED`. The run.sh pass ran beside a `--pin-killed` run on four cores. Carry: dismissed: not reproduced; CI re-runs entities.py
  - `tests/golden.py`: `55 of 56 GOLDEN SCENARIOS CHANGED` in run.sh's plain mode with no `GOLDEN_REF`; at `origin/main` the same plain call refuses to resolve a base (rc 1), and the drift mode CI runs reads `NO UNCLAIMED DRIFT` at the head (`## Head`). Solver floats do not reproduce across BLAS builds (CLAUDE.md rule 3). Carry: dismissed: a local environment reading, not this tree's
- `tests / coverage-ratchet` (job 139768846478): `FAIL every module >= 95.0 % (3 below)`: `approach.py: 79.13 %`, `runs.py: 83.63 %`, `comfort_floor.py: 90.00 %`. At this head's production code, features.py alone covers them at 97.39 %, 100.00 % and 100.00 % (`## Head`); the ratchet reads the union over the fast stage, which only adds lines, so the floor holds for all three. The same check on #3911 (cut at a recent main) was green, so `comfort_floor.py`'s 90.00 % is not main's either. What lowered CI's figures at `46cdd1f9` is not readable in the 5000 lines served; CI's coverage run re-measures this head. Cheaper detector: the one-script coverage run above (about 20 minutes), which is no cheaper than the gate. Carry: dismissed: the floor holds at this head; CI re-measures
- `tests / mutation` (job 139743769371): `ADDED UNPINNED` sites, this diff's and its predecessors' (`approach.py`, `accuracy.py`, `runs.py`, `draw_range.py`, `coordinator.py`, `optimizer.py`, ...), with `tests / mutation-autofix` reporting `AUTOFIX: skip-measure-failed`. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` at `4070ef1fac`: `PIN KILLED -- 96 new unpinned site(s) against 190ffb10c2`, null control `accuracy.py:66 NULL_COMMENT survived every driver`, then `MUTATION TABLE INCONCLUSIVE -- the baseline is already red in tests/structure.py` (`module_excess_loc 21695 > 21646 (+49)`). No pin is measurable on this tree until #3805's row above is green; `mutation-autofix` is the same measurement and skips on the same baseline. Cheaper detector: `ci_predict.py` in `prepr.sh` step 6d predicts the unpinned sites in seconds; only a mutation run records a pin. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (the pins are measurable once its structure row is green; `--pin-killed` then runs on this branch)
- `gate` (job 139902979067): fails because the two required checks above are red; it has no failure of its own. Carry: dismissed: follows fast and mutation
- `governance / instrument-self-tests` (job 139743769465) is red at `46cdd1f9` and outside the owed set. The scope is `MODE: FULL`, so every step counts as selected; its failing step's name is before the 5000 lines served, and the only `tools/` or `.github/` line this branch changes against `origin/main` is #3805's eight `dhw_charges.py` entries in `tools/ci/selftest_closures.json`. CI re-runs it at this head. Carry: dismissed: unread at the old head; CI measures this one

Reds on earlier commits of this branch, as the previous body answered them (each names the head it was read at):

- `tests / fast (3.14)` (job 139696141460, head `4ded335674`): `FAILED python3 tests/features.py`, `AttributeError: 'SysIdConfig' object has no attribute 'enabled'`, `1 TEST SCRIPT(S) FAILED`. It is the `arm_refusal` defect repaired at the head (`## Head`); the R10-CEILING-PROBE block passes there. Cheaper detector and cost: as for `tests / typing` below. Carry: dismissed: repaired in this pull request.
- `tests / coverage-ratchet` (job 139708276939, head `4ded335674`): `FAIL package coverage 93.30 % >= 96.0 %`, `config_flow.py 99.91 %`, `35 below` per module. The coverage run it reads (`tests / coverage`, job 139696141466) logged `ran tests/features.py exit=1 wall=883s`: features.py died on the same `AttributeError` at the R10-CEILING-PROBE block, so the blocks after it ran no statements. Repaired at the head with that defect; CI's coverage run re-measures. No cheaper detector of its own: the ratchet reads the coverage run, and the crash's detector is the one named above. Carry: dismissed: a consequence of the repaired crash.
- `tests / typing` (job 139696141501, head `4ded335674`): `FAIL errors did not grow [recorded 0, measured 1 (+1)]`, `by_code[attr-defined]`, `sysid.py` 1. Repaired at the head (`## Head`). Cause: two branches each correct alone met at the merge of main with no conflict mark, the same class as #3835's `tests / fast` red. Cheaper detector: the pinned `typing_ruler.py --mypy` run on the merged tree, which `prepr.sh` does not run. Its standing cost is the HA-stub install plus a whole-package strict mypy pass, so no countermeasure is built here. The class is #3835's `## Red checks` finding. Carry: dismissed: the class is recorded where #3835 records it, and this instance is repaired here.
- `arch-score / arch-score` (job 139695941416, head `4ded335674`): `unexplained: coord_footprint 2526->2529`. Answered under `## Architecture score`; the rise is #3835's, inherited by the stacked base. The gate's cheaper detector is `score.py --diff` against `origin/main` rather than the predecessor merge, which this body's figure used. Carry: dismissed: the gate now reads the explanation; the code is unchanged.
- `codeql / Analyze (python)`: red only on commits of the predecessor branches this base merges (#3805 at d74d12dd22, #3835 at 7748bdc269), none on this group's own commits, which have had no CI run yet (a handoff ref runs no job). Its answer is that pull request's; the cause is outside this group, owner the predecessor's pull request.
- `governance / env-matrix`: red only on commits of the predecessor branches this base merges (#3805 at d74d12dd22, #3835 at 7748bdc269), none on this group's own commits, which have had no CI run yet (a handoff ref runs no job). Its answer is that pull request's; the cause is outside this group, owner the predecessor's pull request.
- `governance / policy-docs`: red only on commits of the predecessor branches this base merges (#3805 at d74d12dd22, #3835 at 7748bdc269), none on this group's own commits, which have had no CI run yet (a handoff ref runs no job). Its answer is that pull request's; the cause is outside this group, owner the predecessor's pull request.
- `governance / wave-script`: red only on commits of the predecessor branches this base merges (#3805 at d74d12dd22, #3835 at 7748bdc269), none on this group's own commits, which have had no CI run yet (a handoff ref runs no job). Its answer is that pull request's; the cause is outside this group, owner the predecessor's pull request.
- `tests / briefs`: red only on commits of the predecessor branches this base merges (#3805 at d74d12dd22, #3835 at 7748bdc269), none on this group's own commits, which have had no CI run yet (a handoff ref runs no job). Its answer is that pull request's; the cause is outside this group, owner the predecessor's pull request.
- `tests / fast (3.14)` before `4ded335674`: red only on commits of the predecessor branches this base merges (#3805 at d74d12dd22, #3835 at 7748bdc269), none on this group's own commits, which have had no CI run yet (a handoff ref runs no job). Its answer is that pull request's; the cause is outside this group, owner the predecessor's pull request.
- `tests / mutation`: red on commits of the predecessor branches this base merges (#3805, #3835; the 151 commits between origin/main and this head read as one history), and predicted here by `prepr.sh`'s `ci_predict.py` for this diff: its added sites carry no ledger pin until `mutation-autofix` pins those the suite kills, and six pins on lines this diff rewrote were dropped. Cheaper detector: `ci_predict.py` in `prepr.sh` step 6d, which predicted it here, seconds per run; nothing cheaper records a pin, which only a mutation run measures.
- `tests / closures` UNDER-SCOPED: predicted at 18849164a8 for `approach.py` in `tests/backtest.py`, `tests/edge.py`, `tests/optimality.py`, `tests/stress.py` and `tests/validate.py`, whose committed closures list `draw_range.py`, its one importer; c1d1056a0c adds `approach.py` to those five closures, and `ci_predict.py` at c1d1056a0c predicts no closures red. `closures-autofix` replaces them with CI's Linux recording. Cheaper detector: `ci_predict.py` in `prepr.sh` step 6d, which predicted it.

## Forward-carry

none

## Friction

none
