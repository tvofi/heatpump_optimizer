Fix review: merge 10173609c4ac5cebfa00d96c9d5a609f2bb443a6

bus-nonce: 37690fd7831d9a2dc5d5c015be3c5349

## Scope

- Round 2. This is a delta review over the blocked head 5d2c0a30ec65f2d4d4f5976ee50937737e19c089. The delta is `tools/audit/seat/pr_args.sh` only: its self-test now copies the programs under test from a snapshot taken at fixture time (`$seat`), where it used to copy from the live checkout (`$src`). It is a test-instrument delta with no `custom_components/` change, so the scope is not widened (fix-review.md step 12).

## Evidence

- Previous finding (introduced-red on instrument-self-tests step "Show the PR updater ... refusing its own fixtures"): resolved. In the re-rendered packet, `governance / instrument-self-tests` id=131995101638 reads success at this head (ev/review-packet-final.md). `merge_train.py classify 10173609c4ac5cebfa00d96c9d5a609f2bb443a6 --pr 3546` exits 0 with `GREEN 10173609c4ac5cebfa00d96c9d5a609f2bb443a6 pending: none red: none` (ev/classify.txt, ev/classify-poll.log).
- The cause the body claims is confirmed. A scout read at this head found `tools/audit/seat/tick_loop.sh:116` (`git -C "$top" checkout -q --detach origin/main`), with `$top` the real checkout. The rows that reach it run before `HPO_TICK_CODE_DIR` is set at :218. That step (governance.yml:1227) is in the same `instrument-self-tests` job as the background `pr_args.sh --self-test` (governance.yml:418), and runs before `bg_wait update-pr` (:1491).
- Mutation proof, re-run independently. From fresh clones, I ran `bash tools/audit/seat/pr_args.sh --self-test` and moved each clone with `git checkout --detach` to origin/main 154dbb4c61652135381ce66646d23f7109d1c142 45 s into the run; main's `update_pr.sh` has no `upd_figures`. At the previous code head 80efc75a32c24956ba2598c4a7d936f6832e2abf the result is `pr_args self-test: 251 checks, 5 failed`, and the five FAIL rows are the five arms of CI job 131858573499. At the code head b161a5553f540a7cc561640d91b7b05a4457387e the result is `pr_args self-test: 251 checks, 0 failed`, rc 0 (ev/selftest-moved-*.txt, ev/moves.log). Removing the snapshot reproduces the red, so the fix is not vacuous. The body's main SHA (cfa8683946) differs from mine (154dbb4c), but both lack `upd_figures`, and the figures reproduce.
- Remaining `$src` reads in the self-test (`throwaway_git.sh`, `head_note.py`, `gh_comment.py`, `budget_raise_gate.py`, `tests/layout.py`, `prepr.sh` selftest inputs) are not files this PR changes. Main's copies are equivalent for them, which is why the moved checkout did not fail them at either head.
- Red checks: the body's `## Red checks` answers the instrument-self-tests red at 5d2c0a30 with a cause, a process state and a countermeasure. `merge_train.py owed-reds` does not list instrument-self-tests. `pr-contract / pr-contract` id=132018438538 reads success at this head.
- Merge: `git merge-tree --write-tree origin/main 10173609c4ac5cebfa00d96c9d5a609f2bb443a6` with the claimnotes driver installed exits 0 (ev/merge-tree.txt).
- VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff (ev/three-dot-files.txt).
- Head: `git ls-remote origin refs/pull/3546/head` returned 10173609c4ac5cebfa00d96c9d5a609f2bb443a6 just before the push (ev/live-head.txt). The body's `## Head` names the same SHA.
- Not re-derived: the body's `selftest_scope.py record --step update-pr` union figure. I checked only that the snapshot's ten files are files the self-test copies in.
- Closing self-audit: `carry_audit.py check` rc 0, 0 finding items, run over the verdict plus the body's Forward-carry and Friction sections, both `none` (ev/carry-audit.txt). The packet's own carry_audit over the full body at this head also reads 0.
