R10-PREPR-CAP part 2 (topic r10-prepr-cap-2): carries 5, 6 and 7 of the group's roster entry, the first three #3051 left owed. Carries 1-4 are answered by #3051; carries 8-27 are not in this pull request and are owed by R10-PREPR-CAP part 3 (orchestrator ruling on the split: carry order, one reviewable pull request, none dropped, none deferred to round 11).

## Head

e61a5d4ad44bdf36958f6da1d78c9c7eda9ac574 (origin/main c88d552c76f1ae11a879ce7ccb8d8dc29adabf50 is an ancestor, unmoved since the cut, so no second prepr after a merge is owed).

## Carries

Roster ref origin/handoff/audit-r10-roster 41268f41840367917360b6ba06529a388676a5c7, stage carries-open, 27 carries (1-based).

- 1 (gate-lease wait bound, P206): answered by #3051, `tests/gate_lock.py` `WAIT_BOUND_RC`/`wait_bound_for` and `tests/run.sh` `leased()` `WAIT_UNRUN`. Check: `git diff 239e5e4a6^1 239e5e4a6 -- tests/run.sh tests/gate_lock.py | grep -c 'wait_bound\|WAIT_UNRUN'`.
- 2 (no-copies interpreter, P234): answered by #3051, `copies_line` calls `recorder_python`, resolved once through `PREPR_RECORDER_CACHE`. Check: `git show 239e5e4a6:tools/pr/prepr.sh | grep -n 'py=\$(cd "\$1" && recorder_python)'`.
- 3 (expired lease in flock-wrap, P211): answered by #3051, the `flock_wrap` refresh arm in `tests/gate_lock.py`. Check: `git diff 239e5e4a6^1 239e5e4a6 -- tests/gate_lock.py | grep -n 'refreshed when it is still this label'`.
- 4 (R10-RCA-JIDOKA-YIELD, P309): answered by #3051, `dev/audit/rca/R10-RCA-JIDOKA-YIELD.md`, `OWED_CARRY`/`owed_carry` in `tools/audit/carry_audit.py`, the `carry_audit owed-carry` entry in `tools/policy/field_coverage.mjs`, and the corrected WHY at `carry_line`. Check: `git grep -n 'OWED_CARRY' origin/main -- tools/audit/carry_audit.py`.
- 5 (red-check before the slot, P351): built here. `reds_arm`, step 1a2, `--body-check --pr-branch`, `body_push.sh`.
- 6 (`dq_backticks` heredocs): built here.
- 7 (6g CLAIMS_INPUTS trigger): built here. Re-measure of 6g's cost on such a diff against the 5 s cap: not measured in this pull request; the step already copies CLAIMS_INPUTS, only its trigger widened.
- 8-27: not in this pull request. Owed by R10-PREPR-CAP part 3, in roster order (8 base-pinned grader replay, 9-10 and 19-20 quiet output for prepr and the seat instruments, 11 agreement-lane base copy, 12 stale S36, 13-14 `--body-check` parity and the Forward-carry grammar, 15 instrument-self-tests predict, 16 base field_coverage registry over the head, 17 `tests / fast (3.14)` detector, 18 gate-scoping friction measure, 21 HEAD-ONLY predicting detector, 22 `.gitignore` config/ anchor, 23 and 20 pr_bounded adoption, 24 early `## Head` arm P208, 25 the carry 63 text, 26-27 as the roster states). Carry: R10-PREPR-CAP

## Mutation proof

Three mutants, each run through `bash tools/pr/prepr.sh --self-test` in its own detached worktree at the head, baseline 451 passed, 0 failed:
- Red-check call moved after the slot: FAIL `the main flow runs the red-check arm before the heavy slot is taken (P351)`.
- `dq_backticks` heredoc quote flag forced false: FAIL `a bare backtick in an unquoted heredoc body is reported` and `... also inside double quotes in that body`.
- `CLAIMS_READS` narrowed to README.md and docs: FAIL `6g runs on a diff naming only strings.json`.

## Null control

Each fix has its control row in the self-test: `reds_arm` passes a body answering the red and skips with no check runs; the quoted-heredoc fixture stays unreported and `dq_backticks tools/pr/*.sh` stays empty; a `tests/features.py`-only diff still skips 6g with rc 3. An uncontended prepr with no body, or a body on a branch with no pushed head, takes today's path.

## Figures

- Self-test at the head: `bash tools/pr/prepr.sh --self-test` prints `451 passed, 0 failed`.
- Structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, no budget raised.
- Diff size: `git diff --stat origin/main...HEAD` shows 2 files, 128 insertions, 26 deletions.

## Red checks

none

## Unpinned sites

none

## Forward-carry

Carries 8-27 of the R10-PREPR-CAP entry in dev/programme/rosters/wave-r10-groups.json (the round roster), per the Carries section above. Carry: R10-PREPR-CAP

## Friction

none
