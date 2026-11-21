R11-SEAM-ratchet-raise (ADR-009 part 2): two `tests/structure.py` rows read what they name.

- D7-s1-01: `const_modules_over_50` counted names on `from .const import` statements. `const_names_read()` counts the distinct `.const` names a module reads, by a from-import or by a binding of the module (`const.X`, `c.X`). The repaired row reads 4 (entry_config.py added) against a budget of 3.
- D7-s1-04: no row priced a module's lines outside its classes. `module_excess_loc` sums each module's span (line 1 to the end of its last statement) past `MODULE_LOC_LIMIT` = 2000, built the way `class_excess_loc` is built over class spans.

`module_excess_loc` is recorded at the value measured on this head merged with origin/main, as the owner's 2026-11-18 ruling for this row directs; each re-record's reason is in its commit message.

## Head

`b278df39d6856cceab26584eb3f3dd112dc8a28c` is this PR's code head: a one-commit fast-forward of the PR head 430bc6bfad (merge-main bot, origin/main 689f33e265), re-recording `module_excess_loc` 21633 -> 21694 (+61) and `recorded_at` -> 689f33e265. At 430bc6bfad the plain run failed `module_excess_loc 21694 > 21633 (+61)`; the 61 lines are optimizer.py's, from #3736, and no line of this PR moved the figure. No main merge was made: `git merge-tree --write-tree origin/main HEAD` reports no conflict against origin/main 78d3b40221 (measured 2026-11-21 UTC).

prepr: passed rc=0 at b278df39d6856cceab26584eb3f3dd112dc8a28c

## Raise justification

The one raise is `const_modules_over_50: 3 -> 4` (entry_config.py, now counted for its binding reads `const.X`). `module_excess_loc` is this PR's new row, absent on main, so `budget_raise_gate.py` reads none of its re-records as a raise. The owner's ruling (tvofi 2026-11-18) covers both rows; the orchestrator judged the raise approvable under mandate 6893738184 (2026-11-20T20:41Z).

Payments tried: moving owned constants beside their module, narrowing entry_config.py's reads, keeping the from-import count; each measured at b278df39d6 with `tests/structure.py`'s own `const_names_read()` over every module under `custom_components/heatpump_optimizer/` but const.py (the count the row reads):
- Move each over-limit module's own constants (those no other module reads) beside it, as fixer.md step 17 places a constant. Row after the move: entry_config.py 120 -> 120 (0 of its 120 names are read by it alone), thermal_model.py 137 -> 120 (17 its own), coordinator.py 99 -> 62 (37 its own), config_flow.py 425 -> 306 (119 its own). All four stay above 50, so no move of owned constants pays the row; the null control is the same command naming 119 exclusive names for config_flow.py, so the exclusive arm can read non-zero.
- Narrow entry_config.py's reads: refused by ADR-009's Alternatives. entry_config.py is the typed reader of the entry's options, and each field reads its `DEFAULT_*` because it owns that reading; every one of its 120 names is shared with another module (above), so they belong in const.py, and moving the reads elsewhere hides the fan-out without lowering it.
- Keep the from-import count: that leaves the row blind to binding reads, which is the finding itself.

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` at b278df39d6; the diff touches no file under `custom_components/`, which is all the score reads). Null control: the same command over a scratch commit on b278df39d6 that adds `from homeassistant.core import HomeAssistant` to thermal_model.py reads `dS -1.8365 WORSENS (inadmissible: layer_violations 6->24; unused_boundary_imports 0->1)`.

## Mutation proof

The checks are the two self-check groups in `tests/structure.py` (`const_self_check`, `module_self_check`), run by `PYTHONPATH=tests/hastub python3 tests/structure.py` at b278df39d6, each mutant in a scratch worktree, exit 1 each:
- Mutant A, `const_names_read`'s binding-read line disabled (`if bindings:` -> `if False:`): `FAIL a from-import re-spelled as a binding read moves no const row`, `FAIL a name read by both spellings counts once`, `2 COUNTING RULE(S) BROKEN`.
- Mutant B, `module_excess` returning `0 * sum(...)`: `FAIL a module-level function past the module limit is priced by its lines`, `FAIL the same lines in a class past the module limit cost the same`, `2 COUNTING RULE(S) BROKEN`.
- Restored: `ok 80 counting rules hold`.


## Null control

The finder's harness is `$EXPORT/dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py` from plan/r11 819aa2e354, sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b, run with `PYTHONPATH=tests/hastub` at both ends:
- origin/main ae0ed64af8: `ratchet_const_modules_over_50=3`, `any_spelling_const_modules_over_50=4`, `const_unseen_modules=1`. Under `--perturb const-respell` the ratchet falls to 2 while any_spelling stays at 4. Under `--perturb module-growth`, `coordinator_py_unpriced_loc` goes 2986 -> 4409 with `ratchet_rows_off_budget=0`: the defect.
- HEAD 045f358a4f: `ratchet_const_modules_over_50=4`, `const_unseen_modules=0`. Under `--perturb const-respell` the ratchet stays at 4. Under `--perturb module-growth`, `ratchet_rows_off_budget=1`: the added lines are priced.
- At HEAD the harness's `recount_mismatches` reads 1 (`RECOUNT const_modules_over_50 ratchet=4 recount=3 MISMATCH`): the harness recounts with the old from-import rule this PR replaces.

The introduced `instrument-self-tests` red, before and after, on the predicate its four failing rows reach (`review_packet.structure_at_merge(main, head)`, which `review_packet.py handoff`, run by `body_push.sh`, turns into a refusal), with main = origin/main 78d3b40221: head 430bc6bfad returns `"message: main's history keeps it and never a pull-request body."` (structure.py's breach tail, a refusal); head b278df39d6 returns `None`. Command: a three-line script importing `tools/audit/seat/review_packet.py` and printing `structure_at_merge(<main>, <head>)` for each head.

## Figures

<!-- figure-block: scope-line mb=689f33e2653f90ef0abeb10d1fc45be83a2d01cd head=b278df39d6856cceab26584eb3f3dd112dc8a28c -->
~~~text
MODE: SCOPED -- 8 script(s) run, 25 scoped out.
~~~
<!-- /figure-block -->
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at b278df39d6: `const_modules_over_50=4`, `module_excess_loc=21694`, both at budget, `STRUCTURE RATCHET PASSED`, rc 0. On `git merge-tree --write-tree origin/main b278df39d6` (origin/main 78d3b40221, 2026-11-21 UTC; tree 33a82ec31f) the same command prints byte-identical output (`diff` of the two outputs exits 0), so `module_excess_loc` reads 21694 on both and no re-record is owed. Null control: at 430bc6bfad (the same tree before the record) the run exits 1, `FAIL module_excess_loc 21694 > 21633 (+61)`.
- `bash tools/pr/prepr.sh --self-test`: `570 passed, 0 failed`, rc 0, the four rows CI failed at 430bc6bfad (`and pushes a body the lint passes`, `... Code: trailer (V147)`, `... (CARRY 11)`, `... when the roster cannot be read`) each `ok` at b278df39d6; at the merge base 689f33e265 `570 passed, 0 failed`, rc 0.
- The figure block above is the registered `scope-line` instrument rendered at this PR's recorded base 689f33e265 (body_push.sh's base, the one pr-contract verifies with). Rendered with origin/main 78d3b40221 as base it reads `MODE: FULL` (`reason: tests/closure.py changes the gate itself`: the instrument checks the base's tests/closure.py into the head's tree, and main changed that file after 689f33e265). The head's own program, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at b278df39d6, reads `MODE: SCOPED -- 8 script(s) run, 25 scoped out`; each run with `PYTHONPATH=tests/hastub`: all eight rc 0 (arch_score, arch_score_head, doc_claims, entities, features, harness_headers, stress, structure).
- `python3 tools/audit/archscore/score.py --diff`: see `## Raise justification`.

## Red checks

At 430bc6bfad:
- `tests / fast (3.14)` (job 136821023605): `tests/structure.py` failed, `module_excess_loc 21694 > 21633 (+61)`, main's optimizer.py growth from #3736 arriving through the bot's main merge. Fixed by b278df39d6. Cheaper detector: `python3 tests/structure.py` on the merged tree, which already exists and costs about a minute; the bot's `ci: merge main` push does not run it, and the head it produced is the first place the merged tree is measured, so CI is the cheapest detector the bot path has. No countermeasure built: the row moves with main on every main merge until it lands, which is what the ruling's measure-at-merge recording answers.
- `pr-contract / pr-contract` (job 136822821865): `ERROR [figure-block] ... names head=de84aa9bf9cc ... this run is head=430bc6bfad17`, the stale body. This body's figure block is refreshed at b278df39d6. Cheaper detector: `figure_block.py verify`, which `prepr.sh --body-check` runs; it ran at the body's own head, and the bot's head move is what stales it, so no cheaper detector exists.
- `budget-raise-gate / budget-raise-gate` (job 136821054454): `RAISE tests/structure_budgets.json: const_modules_over_50: 3 -> 4`, refused because the approval is on 8f34cd23e0, not this head. Not a defect: the gate is the detector and waits on the approval at the new head (mandate 6893738184).
- `governance / instrument-self-tests` (job 136821023253, `566 passed, 4 failed`, not in the owed set): the four body_push rows of `prepr.sh --self-test`, from the same breach through `review_packet.structure_at_merge`; fixed by b278df39d6 (`## Null control`).
- `tests / nightly-status` and the open code-scanning alerts are inherited from main; this diff touches only dev/programme/delivery/3735.md, tests/structure.py and tests/structure_budgets.json.

## Forward-carry

none

## Friction

none
