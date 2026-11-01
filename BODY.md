R10-PREPR-CAP part 2 (topic r10-prepr-cap-2), round 2: the round-1 verdict (`Fix review: blocked 755949528b55769455419754a8ba57e5154d5cbd mutation-survivor`) is answered by behavioural self-test rows for the two surviving mutants of carry 5's wiring, and the body's diff figure is restated three-dot. Carries 5, 6 and 7 are otherwise unchanged from round 1.

## Head

New handoff head 24bd0ea3e3e29af1f4343da3f4bcec90d28b31c8, one commit on the PR head 755949528b55769455419754a8ba57e5154d5cbd; the authored code head of round 1 is e61a5d4ad44bdf36958f6da1d78c9c7eda9ac574, which the PR head contains. origin/main was 25c46e76e2d7fe504a457a145cadbce33c773662 when measured and `git merge-tree --write-tree origin/main HEAD` reports no conflict (exit 0), so no merge was made.

## Carries

Roster ref origin/handoff/audit-r10-roster, stage carries-open, 27 carries (1-based).

- 1-4: answered by #3051 (see round 1's body: `WAIT_BOUND_RC`/`wait_bound_for`, `recorder_python`, the `flock_wrap` refresh arm, `OWED_CARRY`).
- 5 (red-check before the slot, P351): built in round 1 (`reds_arm`, step 1a2, `--body-check --pr-branch`, `body_push.sh`); this round adds its behavioural pins (the verdict's finding).
- 6 (`dq_backticks` heredocs): built in round 1, unchanged.
- 7 (6g CLAIMS_INPUTS trigger): built in round 1, unchanged. The 5 s cost cap on a strings.json-only diff is UNMEASURED: neither this seat nor the reviewer could time 6g (the claims generator needs scipy/homeassistant, absent from the seat venvs), and this pull request does not claim it. Carry: R10-PREPR-CAP
- 8-27: not in this pull request, owed by R10-PREPR-CAP part 3 in roster order. Carry: R10-PREPR-CAP

## Mutation proof

The two reviewer mutants (`verdict/3150` evidence `mutant-a.diff`, `mutant-b.diff`) were re-applied with `git apply` to detached worktrees at the new head and run through `bash tools/pr/prepr.sh --self-test`:
- Mutant A (step 1a2 `EARLY_REDS_RC=$?` replaced by `EARLY_REDS_RC=0`): 455 passed, 3 failed, rc 2. FAIL `step 1a2 exits nonzero when the arm concluded a red (rc 1) -- before the heavy slot`, `and prints the ancestry reds step line`, `and does not fall through to the heavy steps`.
- Mutant B (`--body-check` guard `if [ "${3:-}" = "--pr-branch" ] ...` replaced by `if false`): 456 passed, 2 failed, rc 2. FAIL `--body-check --pr-branch refuses (line and flag) when the arm concluded a red`, `--body-check --pr-branch passes when the arm returns rc 0 (null control)`.
- Clean head, same command: 458 passed, 0 failed, rc 0 (451 of round 1 plus 7 new rows).
The mutants are restored: the worktrees are discarded and the head is the committed tree.

## Null control

The new rows drive the production text of step 1a2 (the block between `# --- 1a2.` and `# --- 1b0.`) and of the `--body-check` entry up to its `P=$(mktemp)`, extracted with `sed` and evaluated with `reds_arm` stubbed to a chosen rc. rc 1 must exit nonzero with the `ancestry reds` step line and no fall-through; the null controls are the same block with the stub returning rc 0 and rc 3 (no refusal, falls through), and the `--body-check` entry with rc 0 (`ancestry reds ok`, `BODY_CHECK_REDS_RC` unset). The existing textual rows are kept.

## Figures

- Self-test at the head: `bash tools/pr/prepr.sh --self-test` prints `458 passed, 0 failed`.
- Structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget raised.
- Diff size: `git diff --stat origin/main...HEAD` (three-dot, origin/main 25c46e76e2d7fe504a457a145cadbce33c773662, at head 24bd0ea3e3e29af1f4343da3f4bcec90d28b31c8) prints `3 files changed, 169 insertions(+), 26 deletions(-)`: prepr.sh, body_push.sh and the delivery row.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 0 script(s) run`.

## Red checks

none. The whole check-run set of the PR head 755949528b55769455419754a8ba57e5154d5cbd (55 runs, one page, via the check-runs listing) has no run concluded failure, cancelled or timed out; every concluded run is success or skipped.

## Unpinned sites

none

## Forward-carry

Carries 8-27 of the R10-PREPR-CAP entry in dev/programme/rosters/wave-r10-groups.json, per the Carries section above, and the 5 s cost-cap measure of carry 7. Carry: R10-PREPR-CAP

## Friction

none
