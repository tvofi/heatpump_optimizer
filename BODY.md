R10-START-COUNTER-EDGES: part D of pull request #3420. Thanks to Bankaifan, who reported that the compressor start counter misses short cycles: a compressor that stops and restarts between two samples counts no start. Built on the approved design (`design/R10-START-COUNTER-EDGES` at 18655c84b6; `Design review: approve` at `design-verdict/R10-START-COUNTER-EDGES` 9900aa0068).

The counter used to sample the meter once per refresh in `_record_accuracy` and needed `START_HYSTERESIS_SAMPLES` (2) consecutive samples. It now folds the confirmed edges of `running_signal.py`, a new HA glue module. That module is the one owner of the running signal for a pump in every duty mode, duty mode off included, from the coordinator's construction (`__init__`, after the unload registration) to its release (`_release_registrations`). It owns the state listener, `wear.EdgeTracker`'s debounce, a confirm timer at `EDGE_DEBOUNCE_S`, and the subscribers: the start counter always, and the duty-switch learner while the arbiter listens. The sampled path is deleted, not kept beside it. The coordinator gains no attribute (`coordinator_multiassigned_attrs` 108 -> 107).

- **Stored counts continue.** `lifetime`, `months` and `running` keep their stored shape and `from_dict` reading, so no migration is owed. A counter is unrestored until `_async_load_ledger`'s `finally` restores it. Until then it queues edges, and the restore replays them over the stored `running`: a compressor running across the upgrade is not counted again, and an edge before the read is neither lost nor counted twice.
- **No signal counts nothing.** An unavailable, unknown or non-numeric reading is a `None` class, and the last known class holds across it. On the meter source the reader reads `None` while the immersion element runs: by the coordinator's latch, or by the reading itself being over `thermal_model.immersion_over`, now the one owner of what over means for the latch, the carve-out and the reader.
- **Premise correction (design section 4).** `_effective_cycling_cost` reads `_wear_price` (replacement cost over rated starts) and no count. The counted starts feed the wear ledger line (only at a nonzero price), the month receipt's `compressor_starts` and the insight payload. So the plan is unchanged by construction, and the count is where the null control sits.
- **Source change on an install with both a frequency sensor and a meter**: the counter now reads the frequency sensor, as part A's learner does. The retired path read the meter.
- **Release frees the coordinator.** `running_signal.detach` drops the subscribers and the reader. Both close over the coordinator, which is the weak key of the table holding them. Without that, a released coordinator was never collected (features.py's "a released coordinator is collected" read 8 referrers at the first head of this branch).
- The module's import set is `wear`, `drift`, `entry_config`, `freq_control`, `inputs` and `thermal_model` (design-review carry v2). `duty_switch` imports it; it imports neither `duty_switch` nor `pump_arbiter` (pinned in features.py).

Carry 0 (owner ruling 2026-11-13, part D fired now; to round 11 if not merged when the stamp is ready): no stamp is held on this branch. origin/main was merged in twice: at 5b8f05ba4e (e8d71a241f), and at 4058469d79 (43227286fc, pull request 3532's leg rule), where `git merge-tree --write-tree origin/main HEAD` reported conflicts in `duty_switch.py` and `tests/features.py`; see `## Head`. `git merge-tree --write-tree origin/main 43227286fc` at 4058469d79 reports no conflict. It was merged a third time, at e901e9ef29 (7d3ab93eed), after the fix review's block; see `## Head`.

Carry 1 (body item 6a12a74d, S7 measured for the owner's decision): answered under `## Forward-carry`, the S7 item, which stays this group's carry pending the owner's ruling.

## Head

5831759301bb8ecabf97feeca3238c2d5ebaef5b. This round answers the fix review at 43227286fc (`Fix review: blocked`, probe `probe/revt-r10-start-counter-edges-12272296`), whose one block was the survivor `running_signal.py:178` `delay = 0.0`: the confirm timer fires at once, so every meter blip shorter than `EDGE_DEBOUNCE_S` counted a start. Three commits on 43227286fc:

- 1d15eb6bdb adds features.py's check "a meter blip shorter than the debounce counts no start (5 s and one second under it), and one second over it counts one; no timer outlives either". It drives the production coordinator over the fake bus with the revert landing while the confirm timer is still armed, which no earlier trace did (each read at 60 s or longer). No production line changes.
- 7d3ab93eed merges origin/main at e901e9ef29 (`git merge-tree` reported conflicts). Main's R10-ADVISOR-STEADY-START added `whatif.py`, and this branch adds `running_signal.py`, so each side counted one module more than the base. Four conflicts, all counts, each resolved to both modules: `docs/architecture.md` (93 modules, 33 importing `homeassistant` at module level, `whatif.py` doesn't import it; both map lines kept), the round-4 D6 register `claims.py` (`arch_modules_on_disk` and `arch_map_listed` 93, with both modules in the history), `claims.md` regenerated by running `claims.py` (C32 to C35 true at 93 and 33), and `tests/deployment_shape.py`'s note (112 package files). `tests/structure.py` passes on the merge.
- 5831759301 adds the survivor to the tracked mutation proof `dev/audit/harnesses/start_counter_edges_mutants.py` (`timer-delay-zero`).

Previous head: 43227286fc18822b7955e54aa5323cc61feab39e, a merge of origin/main at 4058469d79a3 (pull request 3532, R10-DUTY-SWITCH-RESTART-LEARNING-PR-B part 2: `duty_legs.LegRule`, `Legs`, `leg_rule`, `DutySwitchLearner.split`, `both_step_duty` latching the legs in `_Record.order`) into e8d71a241f, which had merged origin/main at 5b8f05ba4e. Two conflicts, each resolved as the union of both sides:

- `duty_switch.py`, the package import: main added `duty_legs` beside `wear`; this branch replaced `wear` with `running_signal`. Merged: `from . import duty_legs, pump_mode, running_signal` (the module reads `wear` nowhere after this branch). Every other change merged without conflict, `_Record` and the module docstring included, which both sides edited: `_Record` holds this branch's `signal` and main's `order`, and none of the retired `tracker`, `reader`, `unsub`.
- `tests/features.py`, the check naming duty_switch's readers: main's wording and lists (`both_step_duty`, `planner_fields`, `record_for`; the coordinator's `_restored_stores` reads `record_for`) without `Reader`, which this branch retired, plus this branch's clause that the running signal imports none of them nor duty_switch.

Read-back of the merged files, not the diff: an AST pass over base 5b8f05ba4e, both parents and the merge finds every definition each side added or changed in `duty_switch.py` present and identical in the merge (branch: `attach`, `detach`, `note_mode_write`, `note_pass`, `record_for`; main: `DutySwitchLearner.split`, `both_step_duty`, `Direction.book`, the `timedelta` import), the removed ones (`Reader`, `note_signal`, the listener imports) absent, and only `_Record` and the docstring changed on both sides. A sorted-line multiset read-back of `tests/features.py` finds each side's 564 and 331 added lines present except the two lines each of the one resolved check, which the three merged lines replace, and no line either side removed still present. Pinned at 43227286fc: features.py's blocks for part A and 3532's leg rule (71 checks), R10-DUTY-SWITCH-PLANNER-PRICE (96) and this build (15) pass alone (`tools/audit/seat/features_block.py`); `tests/structure.py` passes with no budget file changed by the merge; `dev/audit/harnesses/start_counter_edges.py` gives the head figures below unchanged. One mutant per side of each resolved hunk, run with `tools/audit/seat/mutant_run.py --spec` over part A's block, is killed: the import without `duty_legs` and without `running_signal` (each a `NameError`), a function-local `from . import duty_switch` in `running_signal.py` and `_restored_stores` without the duty-switch store (each fails the readers check).

Earlier rounds: bec79845e8613cdec77cc8c53427a4e765a51c79, on merge base 237fad44532d1927cf65612d395cc5833c60ce99 (origin/main at the time of the run). The mutation proof and the whole-script features.py run were taken at 0845038530 and the structure, score and golden figures at 0845038530 too; the commits after it change no production behaviour and no features.py line outside the build's own block, which passes alone at this head (closures, the two harnesses, the round-4 D6 register, deployment_shape.py's note, the timer helper's rename to `_arm_timer`, which `closure.py no-copies` asked for, and one more check in the build's block), so the tree those figures describe is this head's package and suite. The harness rows were re-taken at bec79845e8.

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py` breaks each line below in turn and runs the build's features.py block and part A's block alone (`tools/audit/seat/features_block.py`). The unmutated tree passes both blocks first (`BASELINE [(0, False), (0, False)]`). Result at 5831759301: 22 killed, 0 survived. One representative failing check per mutant:

- count condition (`running and not self.running` -> `running`): "the stored lifetime and month counts continue across the change ..."
- `None` guard in `StartCounter.fold`: "an unavailable, unknown, empty or non-numeric frequency counts nothing ..."
- queue replay (`restore` returns `[]`) and queueing while unrestored: "an edge confirmed before the ledger load lands survives the restore ..."
- `finally` dropped (restore after the try): "the control trace ... counts one start per on phase ..." and 8 more
- released guard in `_book_starts`; the save on a counted start: "an edge confirmed before the ledger load lands survives the restore ..."
- element, instantaneous term dropped: "the immersion element on a meter-only install: ... (S1) ... (S5) ..."; latch term dropped: same check, S3
- element applied to both sources: "the element rule is the meter source's only ..."; reader guard off: the S1/S5 check
- timer never armed: "in duty mode off a frequency held at 40 Hz ... confirmed by the timer ..." and 2 more
- timer armed with no delay (`delay = 0.0` at `running_signal.py:178`, the fix review's survivor at 43227286fc): "a meter blip shorter than the debounce counts no start ...". Reproduced first with `tools/audit/seat/mutant_run.py --spec` over the build's block at 43227286fc: `SURVIVED NULL`, `SURVIVED timer-delay-zero`; at 1d15eb6bdb and again at the merge 7d3ab93eed: `SURVIVED NULL`, `KILLED timer-delay-zero`. The check's three blips read `{5: (0, 0), 29.0: (0, 0), 31.0: (1, 0)}` (starts, timers left) unmutated; under the mutant they read `{5: (1, 0), 29.0: (1, 0), 31.0: (1, 0)}` (`1 of 16 FEATURES BLOCK FAILED`), as the review's probe found for 5 s to 29 s.
- timer not cancelled at detach; subscribers not cleared at detach; detach not called on release: "the release drops the listener, the timer of a change still pending and the subscribers ..."
- per-refresh re-read deleted: "a refresh re-reads the signal against an unchanged meter ..."
- attach not called in `__init__`: the control-trace check and 2 more
- `running_now` ignoring a pending change: the 40 Hz timer check, and part A's "a pending change of the running class opens no episode"
- duty-switch subscribe, unsubscribe and pass confirm: 14, 2 and 20 of part A's checks respectively

## Null control

Instrument: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/start_counter_edges.py`. It replays the same synthetic meter traces through the production coordinator: at the merge base (a `git archive` export) through the sampled path, at the head through the edge path, with a refresh every `DEFAULT_OPTIMIZATION_INTERVAL`.

- **Control** (every on and off phase spans at least two refresh periods, no start within one period of a month boundary): `control=3` at the base and `control=3` at the head. The same count, and so the same wear lines and month receipt.
- **Perturbation** (one 5-minute stop and restart inside one refresh period): `perturbed=3` at the base, `perturbed=4` at the head. Exactly one more.
- **Lifecycle** (one start before the ledger read lands, stored lifetime 7): `restored=7` at the base, where `from_dict` overwrote the sampled start, and `restored=8` at the head.

The features.py block asserts the head side of each with the production symbols (red at the base, where `running_signal` and `StartCounter.fold` do not exist). Plan invariance is pinned there as a regression ("the counted starts are what the cycling cost and the plan never read"), not claimed as a control. No missed-start figure for real installs is claimed. The sampled path's cadence is a rule, not a measurement: one sample per refresh (`optimization_interval`, default `DEFAULT_OPTIMIZATION_INTERVAL`, plus any requested refresh), two consecutive samples per class change. So any run or stop shorter than about two refreshes was invisible. The contributor's own count was not verifiable from anything in the tree (design carry n4).

## Figures

- Edge path vs sampled path, all five harness rows: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/start_counter_edges.py`, run at the head and at a `git archive` export of the merge base: control 3 / 3, perturbed 3 / 4, restored 7 / 8, s7_60s 0 / 5, s7_30s 0 / 5 (base / head).
- Mutation proof: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py` at 5831759301: 22 mutants, 22 killed, `RESULT survived=0` (21 at 43227286fc, plus `timer-delay-zero`). prepr's diff mutants then left `wear >= 0` and `kwh=1.0` in `_book_starts` alive. The new check "a counted start books money, never energy, and only at a nonzero price" kills both: run with each mutant applied, the block reads `1 of 15 FEATURES BLOCK FAILED`, against `ALL 15 FEATURES BLOCK PASSED` unmutated.
- Whole script: not run on this seat; the build's features.py block passes alone at 5831759301 (`ALL 16 FEATURES BLOCK PASSED`, `tools/audit/seat/features_block.py`), and the whole script is CI.s to read. The earlier rounds quoted no whole-script result either.
- Structure: `python3 tests/structure.py`: every row within budget. Recorded lower in this branch, with the reasons in the commit messages: `class_excess_loc` 17469 -> 17462, `max_class_loc` 7916 -> 7909, `coordinator_multiassigned_attrs` 108 -> 107. At 5831759301 against origin/main e901e9ef29 the same three rows read 17453 -> 17446, 7894 -> 7887 and 106 -> 105, and `seam_cut_total` 416 -> 416 (421 at the first base), because the counter's subscription sits in `_init_grid` beside the counter, so the ledger seam gains no crossing.
- Architecture score: `python3 -I tools/audit/archscore/gate.py --base 237fad44532d --head 0845038530 --body BODY.md`: `dS +0.0133 IMPROVES`, no gate metric rose. `python3 -m tools.audit.archscore.vector .` at both ends: `coord_footprint` 2504 -> 2504 (the design expected a fall; the coordinator class gains 3 logic statements and `duty_switch.detach` loses 3). `layer_violations`, `private_cross_module`, `coordinator_private_reach`, `import_cycle_modules` and `dead_members` are flat.
- Goldens: `GOLDEN_MODE=drift GOLDEN_REF=237fad44532d PYTHONPATH=tests/hastub python3 tests/golden.py`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 237fad44532d1927cf65612d395cc5833c60ce99` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. Neither claim file is touched.
- Home Assistant floor: `python3.13 tests/ha_floor.py record --cache <dir>`: `RECORDED tag=2025.2.0 answers=210 true=187 false=23 undecidable=0`. It adds `name:homeassistant.helpers.event:async_call_later: true`, and drops `name:homeassistant.helpers:device_registry`, which production no longer reaches at the base. Every module was answered from the `homeassistant==2025.2.0` wheel's own sources, laid out in the record's cache. A stand-in `gh` answered 404 for paths the wheel lacks, because this seat's `gh` may not read `home-assistant/core` (see Friction). The nightly floor `verify` re-answers each question with Home Assistant itself.
- Closures: `python3 tools/pr/ci_predict.py` at bec79845e8: `no closures, fast, governance or instrument red predicted against 237fad44532d`. `running_signal.py` joins the 22 closures whose recording opens it: `tests/derive_closures.sh --single tests/block_duty.py`, then `--scripts-from` over the other 21 with `--record-only`, merged by `tests/closure.py merge --partial --allow-failures` (entities.py's recording failed only on the closure checks this merge answers, and ran to its end), then `--single tests/entities.py`, rc 0. The round-4 D6 register (`dev/audit/rounds/round4/D6/claims.py`) and deployment_shape.py's selection-cost note now count the new module: 93 modules beside main's `whatif.py`, 33 importing `homeassistant` at module level, 112 package files.
- Stub contract: `PYTHONPATH=tests/hastub python3 tests/ha_contract.py`: the new `async_call_later` stub entry's contract passes (stub-only).

<!-- figure-block: scope-line mb=e901e9ef295471f85c4f86e84ee0686c38400bc6 head=5831759301bb8ecabf97feeca3238c2d5ebaef5b -->
~~~text
MODE: SCOPED -- 32 script(s) run, 1 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `mutation` at 5831759301bb (as at 43227286fc18 and bec79845e861): red by construction on the 41 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. The cheaper detector is this body's own mutation harness, already run (22 of 22 killed); for a site the diff adds, none cheaper exists.
- `main-conflict`: the handoff at e8d71a241f no longer merged into origin/main at 4058469d79 (`duty_switch.py`, `tests/features.py`), which `body_push.sh`'s predictor refused. The cheaper detector is `git merge-tree --write-tree origin/main HEAD`, run before the body push; answered by the merge at 43227286fc, after which it reported no conflict. Main moved again: at e901e9ef29 `git merge-tree` reported conflicts in `docs/architecture.md`, the round-4 D6 register and `tests/deployment_shape.py` (both sides added a module), answered by the merge at 7d3ab93eed (`## Head`); `git merge-tree --write-tree origin/main 5831759301` reports none.

## Unpinned sites

Each is a production site the diff adds, or re-indents (the five in `_async_load_ledger`, now under its `try`). The `coordinator.py` line numbers are re-read at 5831759301: main's merge at 7d3ab93eed moved every one of them up by 26, with the line text unchanged. Disposition for every one: pinned by `mutation-autofix` (its `custom_components/` lane) after the push; the lines the mutation harness breaks are shown killed above.

- `custom_components/heatpump_optimizer/coordinator.py:8304 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8312 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8325 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8330 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8330 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:9103 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:10482 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:10482 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:10484 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/duty_switch.py:473 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:73 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:88 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:91 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:91 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:93 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:95 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:100 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:121 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:123 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:129 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:134 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:140 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:151 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:155 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:164 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:164 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:166 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:169 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/running_signal.py:178 CLAMP_DROP`: equivalent, not pinned by a check. Dropping the `max(0.0, ...)` changes the delay only when the pending change is older than `EDGE_DEBOUNCE_S` at arm time, and a negative delay to `async_call_later` fires on the next loop pass as 0 does. `mutant_run.py --spec` at 5831759301 reports `SURVIVED clamp-drop`. The debounce itself is pinned by the `timer-delay-zero` kill above, which the fix review found this disposition had stood in for.
- `custom_components/heatpump_optimizer/thermal_model.py:1958 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1971 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1972 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/thermal_model.py:1973 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:121 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:123 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:124 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:126 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:127 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:132 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:135 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/wear.py:142 RETURN_DEL`: pinned by `mutation-autofix`

prepr's diff mutants (`MUTANT_CMD` running the build's block and part A's block) left 17 survivors on lines this diff only re-indents (the ledger riders in `_async_load_ledger`, now under its `try`) or edits one argument of (the immersion evidence line, now reading `params.max_electrical_power`; the carve-out call, now reading `immersion_level_kw`). The two-block check does not reach them by design. They are the whole features.py's to kill, as it pinned five of the riders before the re-indent (the `killed_by` rows this diff drops). Disposition for each: pinned by `mutation-autofix` on CI's mutation lane, or a written triage if that lane leaves one alive.

- `custom_components/heatpump_optimizer/coordinator.py:8308 GUARD_OFF` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8315 GUARD_OFF` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8323 CONST_SWAP` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8325 GUARD_OFF` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8330 GUARD_OFF` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8331 CONST_SWAP` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8306 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8309 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8322 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8323 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8324 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8326 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8331 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8332 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:8334 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:9108 STMT_DEL` (diff mutant): pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:10368 STMT_DEL` (diff mutant): pinned by `mutation-autofix`

## Forward-carry

- The running class for a coordinator is `running_signal.running_now(running_signal.signal_for(coord))`, not the duty-switch record's tracker, which this build removed. It returns `None` before the first confirmed edge, with no source configured, while the entity is unavailable or non-numeric, on the meter while the element rule holds, and while a change is pending; the sibling keeps its executing-step fallback for `None` (design note n8). Lands in `dev/programme/rosters/wave-r10-groups.json`, group R11-OUTSIDE-HONEST-STARTS-RUNS's brief. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS
- S7, measured, for the owner's decision between the residual and a refresh-held start (design note n6, review carry v5). On a meter that reports its window's average, an element cut-in with the compressor off gives one partial report between the on-threshold and the over level. That report holds for one report period, at least `EDGE_DEBOUNCE_S`, and so is confirmed as a start before over arrives. Harness rows `s7_60s` and `s7_30s`: 5 of 6 offsets count a false start on each (the sixth fills its window and is over from its first report); the sampled path counted 0. Pending owner ruling; lands in `dev/programme/rosters/wave-r10-groups.json`, this group's carry. Carry: R10-START-COUNTER-EDGES

## Friction

- ha_floor.py: cost: `ha_floor.py record` fetches upstream sources with `gh api repos/home-assistant/core/...`, which this cloud seat's GitHub scope refuses; re-recorded from the same tag's PyPI wheel through the record's own cache, with a 404 stand-in for absent paths (Figures). Carry: dismissed: worked around in this seat with the tag's own sources; the nightly floor verify re-answers every recorded question
- D6-claims-harness: stale: `dev/audit/rounds/round3/D6/claims.py` raises `TypeError: restore_session() missing 3 required positional arguments` in `store_probe.build_every_store` before any claim runs, at the merge base 237fad4453 as at this head, so C-RM-58's re-point (off the retired `START_HYSTERESIS_SAMPLES` onto `power_guard.HYSTERESIS_SAMPLES`) was checked directly: `power_guard.HYSTERESIS_SAMPLES` is 2. Carry: dismissed: a round-3 audit record broken at the base by an unrelated signature change, outside this group's seam
