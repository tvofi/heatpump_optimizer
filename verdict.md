Fix review: blocked 296a0a30d41de41aced099d6c16045cbaefaa1d7 mutation-vacuous: shell_hazard.py NUMERIC.search(line) survives the self-test and excuses a raw wc string compare on any line holding a numeric op

bus-nonce: bc6ee943a248d7ef7873796b7a290c96
pending-ci: gate

## Block

Round 1 (the packet's review scope is `full`: no verdict names the reviewed head 78e5780100). Head reviewed: `296a0a30d41de41aced099d6c16045cbaefaa1d7`, the head the PR body names.

The five mutants the body names all fail the self-test (`ev/mutants.txt`). A sixth predicate the diff adds does not: in `tools/audit/seat/shell_hazard.py` `hazards()`, deleting ` or NUMERIC.search(line)` leaves `--self-test` at `ok`, rc 0. The `-eq` null-control row (`[ "$(wc -l <"$f")" -eq 3 ] || x`) passes because it has no `=`, so STRING_CMP never matches it, not because NUMERIC excuses it. Nothing pins the predicate.

The predicate also has a defect against the module's own rule. NUMERIC searches the whole line, so any `-eq`/`-gt`/`((`/`$((` anywhere on the line excuses a raw string compare elsewhere on that line (`ev/numeric_false_negative.txt`, at this head):
- `st "$(a | wc -l)" 0 "m"` is refused (`wc-compare`). The same line with ` && [ $n -eq 0 ]` appended passes. That is the #3455 instance shape with one numeric test added.
- `[ "$(wc -l <f)" = 3 ]` is refused. `[ "$(wc -l <f)" = 3 ] || exit $((1))` and `... && [ $n -gt 0 ]` pass.

The docstring says "A numeric test (`-eq`, `$(( ))`) is read as a number and passes", which means the compare itself. The code excuses the whole line.

Repair owed (fixer.md steps 2-8 re-run after it): scope the numeric exemption to the compare that holds the substitution, not the line. Add a self-test row that fails when NUMERIC is deleted: a numeric compare that *does* contain a string-compare token, e.g. `[ "$(wc -l <f)" -eq 3 ] || [ "$a" = b ]`. Add a row that fails under the current line-wide search: `st "$(a | wc -l)" 0 m && [ $n -eq 0 ]` refused. Optional, outside the stated rule: `test "$(wc -l <f)" = 3` is not matched (STRING_CMP knows `st`, `[`, `[[`, `case`, not `test`).

## Findings

none beyond the block

## Evidence

- CI at this head: `merge_train.py classify 296a0a30d4 --pr 3639` printed `WAIT 296a0a30d41de41aced099d6c16045cbaefaa1d7 pending: gate red: none` on every run from 16:03 to 16:32 UTC (`ev/classify.log`); stopped after ~30 min per the brief. The block above rests on code and tests, not on CI.
- Merge with main: `git merge-tree --write-tree origin/main 296a0a30d4` rc 0, `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`); no conflict.
- Self-test at head: `shell_hazard self-test: ok` rc 0 (`ev/selftest.txt`).
- Mutation proof (`ev/mutants.txt`), one sed per predicate on the file, `--self-test`, restore. FAIL rows: STRING_CMP 4, EARLY 6, STUB_WC 1, RAW 1, DRAINED 1, SMALL 1, NORMALISE 3, comment-skip 2, line-restriction 2, stub `tr -d` exemption 1, PIPEFAIL 1, diff pathspec 1; NUMERIC 0 (survivor).
- The body's per-mutant counts (5, 7, 2, 2, 2) are each one more than the FAIL rows printed (4, 6, 1, 1, 1). This reads as the summary `FAILED` line being counted too, but I could not re-derive the body's rule for the count.
- Instance null controls reproduce (`ev/instance_controls.txt`): `003f89cf9c` refuses `prepr.sh:2396 wc-compare`; `1386441425` refuses `:2405 wc-stub` and `:2406 wc-compare`; `09b7856fc0` refuses `app_approve.sh:303 early-pipe`, and also `:2038` (`rev-list ... | head -1`), which the body does not name; `cb803e9eed` prints no `app_approve.sh` line, but does print `tools/audit/seat/pr_args.sh:462 early-pipe`.
- Shadow count (`ev/figures.txt`): 2 of 20 (a39627da59 11, dc46b1222f 1) over the window ending at the fixer's merge base 98847b99d7. This reproduces. Over the window ending at this head's merge base e352724335, it is 1 of 20 (315dda8f62, 7 lines). The body's figure is a snapshot of the earlier window.
- Standing cost on this container: `shell_hazard.py --check --base origin/main` 0.055 s real; `inline_scan` 1.031 s real. The body's under-one-second bound does not hold here, which the body's own null control (under 0.1 s headroom) anticipates.
- At head: `selftest_scope.py static` `0 problem(s)`; `fold_ledger.py check` `0 violation(s)`; `check-wave-script.mjs` `249 passed, 0 failed`; the PR's own added shell lines pass its lint (`--check --base origin/main` rc 0).
- VERSION, the manifest and RELEASE_NOTES are not in the three-dot diff. No claim file is touched, and there is no `custom_components/` change.
- Not re-run: `bash tools/pr/prepr.sh --self-test`, which carries the `hazard_line` and `inline_walk_line` rows. I cite CI's `governance / instrument-self-tests` for it (fix-review.md 11).
- Finder's harness: none named (the packet). This is an instrument lane re-cut by triage P761, with the instance commits as its harness; those reproduce above.
