R11-SEAM-ratchet-raise (ADR-009 part 2): two `tests/structure.py` rows read what they name.

- D7-s1-01: `const_modules_over_50` counted names on `from .const import` statements. `const_names_read()` counts the distinct `.const` names a module reads, by a from-import or by a binding of the module (`const.X`, `c.X`). The repaired row reads 4 (entry_config.py added) against a budget of 3.
- D7-s1-04: no row priced a module's lines outside its classes. `module_excess_loc` sums each module's span (line 1 to the end of its last statement) past `MODULE_LOC_LIMIT` = 2000, built the way `class_excess_loc` is built over class spans.

`module_excess_loc` is recorded at the value measured on this head merged with origin/main, as the owner's 2026-11-18 ruling for this row directs; each re-record's reason is in its commit message.

## Head

`3e1e9141e40f6452f44adf3ab58b417d5851c0e8` is this PR's code head: c4faf32b98 merged with origin/main a8efe1d1c2 (#3830), with no conflict and no further commit. c4faf32b98 is predecessor head b278df39d6 merged with origin/main e698fc8ac3, with no conflict (`git merge-tree --write-tree origin/main b278df39d6` printed a tree and no conflict line). Two commits follow. bd58b7341e re-records `module_excess_loc` 21694 -> 21718 (+24) and sets `recorded_at` to e698fc8ac3. c4faf32b98 splits the two docstring sentences in tests/structure.py that `tests/doc_claims.py`'s 40-word comment ratchet refused at bd58b7341e (`REFUSE tests/structure.py: long units 34 -> 36`). At c4faf32b98 that check reads `long_units_base=2443 long_units_head=2443`, rc 0. On the merge commit 161fc37b8f the plain run failed `module_excess_loc 21718 > 21694 (+24)`; the 24 lines are sensor.py's (`RoomSeparabilitySensor` and its setup line, #3616 phase 3a, merged to main by #3711 at b486fe58fd), and no line of this PR moved the figure. Per-module attribution: `module_excess()` from tests/structure.py applied to each `custom_components/` module at b278df39d6 and at 161fc37b8f, printing every module whose excess differs: `sensor.py 1181 -> 1205`, totals `21694 21718`; no other module moved (the script prints any that does). Per main commit: b278df39d6's tests/structure.py run over main's first parents reads 21694 at 78d3b40221, 05657b6898 and 42809bec34, and 21718 at b486fe58fd (#3711), 86859b9594 and e698fc8ac3. At 3e1e9141e4 (merge base a8efe1d1c2) `PYTHONPATH=tests/hastub python3 tests/structure.py` reads `module_excess_loc=21718`, `STRUCTURE RATCHET PASSED`, rc 0; #3830 moves no module, so `recorded_at` stays e698fc8ac3, where the figure was measured.

Paying the +24 was tried and not taken (`## Raise justification`, second payment list).

prepr: passed rc=0 at 3e1e9141e40f6452f44adf3ab58b417d5851c0e8

## Raise justification

The one raise is `const_modules_over_50: 3 -> 4` (entry_config.py, now counted for its binding reads `const.X`). `module_excess_loc` is this PR's new row, absent on main, so `budget_raise_gate.py` reads none of its re-records as a raise. The owner's ruling (tvofi 2026-11-18) covers both rows; the orchestrator judged the raise approvable under mandate 6893738184 (2026-11-20T20:41Z).

Payments tried: moving owned constants beside their module, narrowing entry_config.py's reads, keeping the from-import count; each measured at bd58b7341e with `tests/structure.py`'s own `const_names_read()` over every module under `custom_components/heatpump_optimizer/` but const.py (the count the row reads):
- Move each over-limit module's own constants (those no other module reads) beside it, as fixer.md step 17 places a constant. Row after the move: entry_config.py 120 -> 120 (0 of its 120 names are read by it alone), thermal_model.py 137 -> 120 (17 its own), coordinator.py 99 -> 63 (36 its own), config_flow.py 425 -> 306 (119 its own). All four stay above 50, so no move of owned constants pays the row; the null control is the same command naming 119 exclusive names for config_flow.py, so the exclusive arm can read non-zero.
- Narrow entry_config.py's reads: refused by ADR-009's Alternatives. entry_config.py is the typed reader of the entry's options, and each field reads its `DEFAULT_*` because it owns that reading; every one of its 120 names is shared with another module (above), so they belong in const.py, and moving the reads elsewhere hides the fan-out without lowering it.
- Keep the from-import count: that leaves the row blind to binding reads, which is the finding itself.

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` at bd58b7341e, merge base e698fc8ac3, and again at 3e1e9141e4, merge base a8efe1d1c2; the diff touches no file under `custom_components/`, which is all the score reads). Null control: the same command over a scratch commit on b278df39d6 that adds `from homeassistant.core import HomeAssistant` to thermal_model.py reads `dS -1.8365 WORSENS (inadmissible: layer_violations 6->24; unused_boundary_imports 0->1)`.

Payments tried for the `module_excess_loc` re-record 21694 -> 21718 (a re-record of this PR's own new row, not a raise the gate reads), measured on b278df39d6 merged with origin/main a8efe1d1c2:
- Move `RoomSeparabilitySensor` (the 24 lines #3711 added) out of sensor.py into its own module `sensor_rooms.py`, imported back by sensor.py: `Architecture score: dS -1.5850 WORSENS (inadmissible: import_cycle_modules 0->2)` (`python3 tools/audit/archscore/score.py --diff <merged> <scratch>`), and `tests/structure.py` still reads `module_excess_loc 21698 > 21694 (+4)` with `FAIL import_cycle_modules 2 > 0 (+2)`. The class stands on sensor.py's `HeatPumpOptimizerSensorBase`, so the move makes a cycle; breaking it means moving the sensor platform's entity base, production code outside this ratchet-only seam. Not paid.
- Delete or shorten the class: refused by rule 2 (never delete working functionality merely to fit); the lines are a merged feature under its own review.

## Mutation proof

The checks are the two self-check groups in `tests/structure.py` (`const_self_check`, `module_self_check`), run by `PYTHONPATH=tests/hastub python3 tests/structure.py` at bd58b7341e, each mutant in a scratch worktree, exit 1 each:
- Mutant A, `const_names_read`'s binding-read line disabled (`if bindings:` -> `if False:`): `FAIL a from-import re-spelled as a binding read moves no const row`, `FAIL a name read by both spellings counts once`, `2 COUNTING RULE(S) BROKEN`.
- Mutant B, `module_excess` returning `0 * sum(...)`: `FAIL a module-level function past the module limit is priced by its lines`, `FAIL the same lines in a class past the module limit cost the same`, `2 COUNTING RULE(S) BROKEN`.
- Restored: `ok 80 counting rules hold`.


## Null control

The finder's harness is `$EXPORT/dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py` from plan/r11 819aa2e354, sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b, copied into each scratch worktree and run with `PYTHONPATH=tests/hastub` at both ends:
- merge base e698fc8ac3: `ratchet_const_modules_over_50=3`, `any_spelling_const_modules_over_50=4`, `const_unseen_modules=1`. Under `--perturb const-respell` the ratchet falls to 2 while any_spelling stays at 4. Under `--perturb module-growth`, `coordinator_py_unpriced_loc` goes 2963 -> 4386 with `ratchet_rows_off_budget=0`: the defect.
- HEAD bd58b7341e: `ratchet_const_modules_over_50=4`, `const_unseen_modules=0`. Under `--perturb const-respell` the ratchet stays at 4. Under `--perturb module-growth`, `ratchet_rows_off_budget=1 (module_excess_loc 21718->23141)`: the added lines are priced.
- At HEAD the harness's `recount_mismatches` reads 1 (`RECOUNT const_modules_over_50 ratchet=4 recount=3 MISMATCH`): the harness recounts with the old from-import rule this PR replaces.

The `instrument-self-tests` red, before and after, on the predicate its failing rows reach (`review_packet.structure_at_merge(main, head)`, which `review_packet.py handoff`, run by `body_push.sh`, turns into a refusal), with main = e698fc8ac3: the merge commit 161fc37b8f (before the record) returns `"message: main's history keeps it and never a pull-request body."` (structure.py's breach tail, a refusal); head bd58b7341e returns `None`. Command: a three-line script importing `tools/audit/seat/review_packet.py` and printing `structure_at_merge(<main>, <head>)` for each head.

## Figures

<!-- figure-block: scope-line mb=a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b head=3e1e9141e40f6452f44adf3ab58b417d5851c0e8 -->
~~~text
MODE: SCOPED -- 8 script(s) run, 25 scoped out.
~~~
<!-- /figure-block -->
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at 3e1e9141e4 (merge base a8efe1d1c2 = origin/main, 2026-11-21 UTC): `const_modules_over_50=4`, `module_excess_loc=21718`, both at budget, `ok 80 counting rules hold`, `STRUCTURE RATCHET PASSED`, rc 0. Null control: b278df39d6 merged with origin/main a8efe1d1c2 before any record (scratch d2bc5cb8df) prints `FAIL module_excess_loc 21718 > 21694 (+24)`; at the merge commit 161fc37b8f (e698fc8ac3) the run prints the same breach and `1 STRUCTURE BUDGET(S) BREACHED`.
- `python3 tools/policy/budget_raise_gate.py --base $(git merge-base origin/main HEAD) --head HEAD --pr 3735` at bd58b7341e: `RAISE tests/structure_budgets.json: const_modules_over_50: 3 -> 4`, `RESULT budget_raises=1`, and a refusal that the approval is on 8f34cd23e0, not this head. `module_excess_loc` is not listed, because main has no such row.
- The figure block above is the registered `scope-line` instrument, rendered with `figure_block.py refresh BODY.md --base origin/main --head HEAD` at 3e1e9141e4 (origin/main a8efe1d1c2). `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` names the same eight scripts: arch_score, arch_score_head, doc_claims, entities, features, harness_headers, stress and structure. All eight were run at 3e1e9141e4 with `PYTHONPATH=tests/hastub`: arch_score_head and doc_claims rc 0; arch_score and entities were stopped by a 20-minute local timeout (rc 124) on a machine shared with other seats, with no failure line printed before the stop; the remaining four were still running at the handoff, so CI's scoped gate is the authority for those six. At c4faf32b98, before the merge of #3830, all eight returned rc 0.
- `python3 tools/audit/archscore/score.py --diff`: see `## Raise justification`.

## Red checks

At 430bc6bfad (the PR head CI last measured; b278df39d6 was never pushed to the PR):
- `tests / fast (3.14)` (job 136821033342): `tests/structure.py` failed with `module_excess_loc 21694 > 21633 (+61)`, which is main's optimizer.py growth from #3736 arriving through the bot's main merge. b278df39d6 recorded it. The same row then breached at +24 on the merge with e698fc8ac3 (sensor.py, #3616), and bd58b7341e records that. Cheaper detector: `python3 tests/structure.py` on the merged tree. It already exists and takes about a minute, but the bot's `ci: merge main` push does not run it, so CI is the cheapest detector the bot path has. No countermeasure is built: the row moves with main on every main merge until it lands, and the ruling's measure-at-merge recording is the answer to that.
- `pr-contract / pr-contract` (jobs 136822821865 and 136838804539): `ERROR [figure-block] line 48: block scope-line names head=de84aa9bf9cc ... this run is head=430bc6bfad17`, which is the stale body. This body's figure block is rendered at bd58b7341e. Cheaper detector: `figure_block.py verify`, which `prepr.sh --body-check` runs. That check ran at the body's own head, and the bot's head move is what made the body stale, so no cheaper detector exists.
- `budget-raise-gate / budget-raise-gate` (jobs 136821054454 and 136821023182): `RAISE tests/structure_budgets.json: const_modules_over_50: 3 -> 4`, refused because the approval is on 8f34cd23e0, not this head. This is not a defect: the gate is the detector, and it waits on the approval at the new head (mandate 6893738184).
- `gate` (jobs 136839786989 and 136825619023): the aggregate of the reds above. It has no cause of its own.
- `governance / instrument-self-tests` (jobs 136821033077 and 136821023253; not in the owed set): the body_push rows of `prepr.sh --self-test`, from the same breach through `review_packet.structure_at_merge`. bd58b7341e fixes them (`## Null control`).
- `tests / nightly-status`: inherited from main; it grades main's nightly run, and this diff touches only dev/programme/delivery/3735.md, tests/structure.py and tests/structure_budgets.json, none of which the nightly reads.
- `code-scanning alert 57 (py/overly-permissive-file)` (tools/audit/seat/postmerge.py:130) and `code-scanning alert 58 (py/overly-permissive-file)` (tools/audit/seat/roster_lib.py:1166): not introduced by this diff, which touches neither file and no chmod or mode line (`git diff $(git merge-base origin/main 3e1e9141e4)...3e1e9141e4` is those three files only). Both alerts' state is `fixed` on refs/heads/main at 05657b6898 (fixed_at 2026-11-21T15:13:20Z); the open instances are on other branches' merge refs. The cheaper detector is the CodeQL scan that raised them, which already runs on main.

## Forward-carry

none

## Friction

none
