Fix review: merge 668b6bab3242c23941e368a83593d5739c666471

bus-nonce: 404335a3f37c45a86ab5c31a857ae9b7

Round 2 of #3041 (R10-FLY-TICK-APPROVAL-OWED), head 668b6bab3242c23941e368a83593d5739c666471 (measured and still the head at the CI read).

## Findings

None that this PR leaves open.

## Evidence

- RESULT orchestrator_tick `--self-test` under `env -u BASH_ENV` at the head: 235 checks, 0 failed. RESULT owed_unactioned `--self-test`: 46 checks, 0 failed.
- RESULT the P328 REVIEW STALLED arm is present (`_reviewer_ref_age`, `STALL_MINUTES = 90`, git only: ls-remote, fetch, commit time). Both null controls are present and pass: a dispatch tip 30 min old, and a verdict at the head with a dispatch 100 min old, each print no stall. Also pinned: a dispatch at an older head prints none, and an unreadable ref prints UNREADABLE.
- RESULT mutation proof, 7 mutants of my own, each killed by a named self-test check (ev/mutants.txt; M1 was run by hand): threshold disabled, stall always on, verdict-at-head ignored, dispatched-set ignored, APPROVAL-OWED arm off, `_unsettled` ignored, draft ignored, UNLEVELLED catch-all off. M2 also trips the zero-findings null controls.
- RESULT merge with origin/main: `git merge-tree --write-tree` exit 0, no conflict, no claim file touched.
- RESULT VERSION, the manifest version and the notes heading are untouched (diff touches only the tick, owed_unactioned, two instrument notes and delivery/3041.md).
- RESULT CI: `merge_train.py classify` exited 0, GREEN at this head, pending none, red none (ev/classify.txt). No gate check went red, so no root-cause answer is owed. The packet's carry_audit is 0 findings and its figure_lint is 3 resolved.
- Not verified: the P328 ruling text. dev/programme/triage/s6-batch90.md is not on origin/main, and the roster resume note of the group cites only P294. I checked the arm against the brief's statement of P328 (git-only, dispatch ref older than 90 min, no verdict at the head). I could not read the 70-minute p95 figure in the STALL_MINUTES comment, which I did not re-derive.
- The packet shows no finder's harness for this group. The self-test is the harness for an instrument, so I measured with it at the head; the base side is not applicable for new arms.
