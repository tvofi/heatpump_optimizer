R11-SEAM-ratchet-raise (ADR-009 part 2): two `tests/structure.py` rows read what they name.

- D7-s1-01: `const_modules_over_50` counted names on `from .const import` statements. `const_names_read()` counts the distinct `.const` names a module reads, by a from-import or by a binding of the module (`const.X`, `c.X`). The repaired row reads 4 (entry_config.py added) against a budget of 3.
- D7-s1-04: no row priced a module's lines outside its classes. `module_excess_loc` sums each module's span (line 1 to the end of its last statement) past `MODULE_LOC_LIMIT` = 2000, built the way `class_excess_loc` is built over class spans.

Both rows are recorded at their values measured at origin/main ae0ed64af8. The commit message gives the reason.

## Head

`0dfa61d887bb9f78c587579680e9e3d53fa21387` is this PR's code head: 382df86816 plus a merge of origin/main 99436a082c and one commit that re-records `module_excess_loc` (21549 -> 21536) and `recorded_at` (ae0ed64af8 -> 99436a082c). Measured against origin/main 99436a082c67ad5dbb4afc293506af010d6ee8df (2026-11-19 08:33 UTC).

## Raise justification

Owner ruling, tvofi 2026-11-18, verbatim "Yes to both": (1) raise `const_modules_over_50` from 3 to the value the repaired count reads at confirmation; (2) the module-span row limit is 2000 lines, and the row is recorded at its value measured now. The ruling was given before this branch was pushed. `module_excess_loc` is a new row, which `budget_raise_gate.py` does not read as a raise.

Payments tried: narrowing entry_config.py's const reads; bringing config_flow.py, thermal_model.py or coordinator.py under 51 names; keeping the from-import count. None was taken, for these reasons:
- Narrowing entry_config.py's reads of `const`: refused by ADR-009's Alternatives. The module reads its configuration keys because it owns that reading. Moving the reads elsewhere hides the fan-out without lowering it.
- Bringing another of the four modules under 51 distinct names: config_flow.py reads 424, thermal_model.py 135 and coordinator.py 100 (the `.const fan-out` table `python3 tests/structure.py` prints). No move of those reads lowers coupling, and re-spelling them is the blindness D7-s1-01 repairs.
- Keeping the from-import count: that leaves the row blind to binding reads, which is the finding itself.

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff origin/main HEAD`).

## Mutation proof

The checks are the two new self-check groups in `tests/structure.py` (`const_self_check`, `module_self_check`), run by `PYTHONPATH=tests/hastub python3 tests/structure.py`:
- Mutant A, `const_names_read`'s binding-read line disabled (`if bindings:` -> `if False:`): `FAIL a from-import re-spelled as a binding read moves no const row`, `FAIL a name read by both spellings counts once`, `2 COUNTING RULE(S) BROKEN`.
- Mutant B, `module_excess` returning `0 * sum(...)`: `FAIL a module-level function past the module limit is priced by its lines`, `FAIL the same lines in a class past the module limit cost the same`, `2 COUNTING RULE(S) BROKEN`.
- Restored: `ok 80 counting rules hold`.

## Null control

The finder's harness is `$EXPORT/dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py` from plan/r11 819aa2e354, sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b. It was run with `PYTHONPATH=tests/hastub` at both ends:
- origin/main ae0ed64af8: `ratchet_const_modules_over_50=3`, `any_spelling_const_modules_over_50=4`, `const_unseen_modules=1`. Under `--perturb const-respell` the ratchet falls to 2 while any_spelling stays at 4. Under `--perturb module-growth`, `coordinator_py_unpriced_loc` goes 2986 -> 4409 with `ratchet_rows_off_budget=0`: the defect.
- HEAD 045f358a4f: `ratchet_const_modules_over_50=4`, `const_unseen_modules=0`. Under `--perturb const-respell` the ratchet stays at 4. Under `--perturb module-growth`, `ratchet_module_excess_loc=22972` and `ratchet_rows_off_budget=1 (module_excess_loc 21549->22972)`. The added 1423 lines are priced.
- At HEAD the harness's `recount_mismatches` reads 1 (`RECOUNT const_modules_over_50 ratchet=4 recount=3 MISMATCH`). The harness recounts with the old from-import rule that this PR replaces, so this line reads the fix rather than a regression.
- The introduced red, failing then passing, on the predicate the four self-test rows reach: `review_packet.structure_at_merge(main, head)`, which `review_packet.py handoff` (run by `body_push.sh`) turns into a refusal. With main = origin/main 99436a082c: head 382df86816 (before) returns `'table with this change, and say in the commit which rows moved.'` (structure.py's IMPROVED tail, a refusal); head 0dfa61d887 (after) returns `None` (no refusal). Command: a three-line script importing `tools/audit/seat/review_packet.py` and printing `structure_at_merge(<main>, <head>)` for each head. The whole `prepr.sh --self-test` was not re-run locally (it ran at ~2 rows a minute on this host); CI's `governance / instrument-self-tests` at the new head is the authority for it.

## Figures

<!-- figure-block: scope-line mb=99436a082c67ad5dbb4afc293506af010d6ee8df head=0dfa61d887bb9f78c587579680e9e3d53fa21387 -->
~~~text
MODE: SCOPED -- 8 script(s) run, 25 scoped out.
~~~
<!-- /figure-block -->
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `const_modules_over_50=4`, `module_excess_loc=21536` (MODULE_LOC_LIMIT 2000), both at budget, at 0dfa61d887 (rc 0). At db0831f278 (382df86816 merged with origin/main 99436a082c, before the re-record) the same command exits 2: `module_excess_loc 21549 -> 21536 BETTER`, `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`. The -13 is main's own: module spans past 2000 lines moved coordinator.py -23, config_flow.py +3, sensor.py +7 between ae0ed64af8 and 99436a082c (an `ast` span count over `git show` of each module at both commits). The four modules over the const limit are config_flow.py, thermal_model.py, entry_config.py and coordinator.py.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: dS +0.0000 NULL.
- Harness figures: see `## Null control`, with the command and sha1 named there.

## Red checks

- `budget-raise-gate / budget-raise-gate`: red by design until tvofi approves at the head, because `const_modules_over_50` goes 3 -> 4. The owner's ruling of 2026-11-18 is quoted under `## Raise justification`. This is no defect, so the root-cause question does not arise: the gate is the cheapest detector, it is the one that fired, and it waits on the owner's review.
- `governance / instrument-self-tests` (step "Show the pre-PR self-check refusing its own fixtures") at 382df86816: introduced by this PR, and fixed at 0dfa61d887. Cause: on the PR merged with main, `tests/structure.py` exited 2 (`module_excess_loc` IMPROVED AND NOT YET RECORDED, 21549 -> 21536, a gain main made after the row was recorded at ae0ed64af8). `review_packet.py handoff` refuses a head whose merge with main `tests/structure.py` refuses, and `body_push.sh` runs it, so four body_push rows of `prepr.sh --self-test` failed (`566 passed, 4 failed`): "and pushes a body the lint passes", "and that body's commit names the handoff head ... (V147)", "and refuses a body whose carry its group does not hold ... (CARRY 11)", "and pushes, saying so, when the roster cannot be read". Fix: the re-record commit 0dfa61d887. Proof under `## Null control`. The cheaper detector exists and fired: `python3 tests/structure.py` on the merged tree, which the fixer contract runs before every push; the head 382df86816 was a `ci: merge main` push made without re-running it.
- `tests / fast (3.14)` at 382df86816: the same cause (`FAILED python3 tests/structure.py`, exit 2, IMPROVED AND NOT YET RECORDED), fixed by the same commit.
- `governance / env-matrix` at 382df86816: cancelled at its 10-minute `timeout-minutes` (started 06:01:57Z, cancelled 06:12:11Z), not a failure this PR introduced. The PR's diff (tests/structure.py, tests/structure_budgets.json, its delivery row) reaches nothing the environment matrix builds. The re-run at the new head is the answer.
- Inherited from main, not from this diff: `tests / nightly-status`, `code-scanning alert 57 (py/overly-permissive-file)`, `code-scanning alert 58 (py/overly-permissive-file)`, `code-scanning alert 59 (js/insecure-temporary-file)`, `code-scanning alert 60 (js/file-system-race)`, `code-scanning alert 61 (py/insecure-temporary-file)`, `code-scanning alert 62 (py/insecure-temporary-file)`, `code-scanning alert 63 (py/insecure-temporary-file)`, `code-scanning alert 64 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 65 (py/incomplete-url-substring-sanitization)`, `code-scanning alert 66 (py/overly-permissive-file)` and `code-scanning alert 67 (py/overly-permissive-file)`. Each alert's most recent instance is on refs/heads/main, in tools/audit/seat/postmerge.py, tools/audit/seat/roster_lib.py or a dev/audit/rounds/round11/ harness, none of which this diff touches (`git diff --stat 99436a082c...0dfa61d887`: dev/programme/delivery/3735.md, tests/structure.py, tests/structure_budgets.json). The cheaper detector is the CodeQL scan that raised them, which already runs on main.

## Forward-carry

none

## Friction

none


