Fix review: merge a60a65d87376397adc098cbf2b7b2377ccaeca02

bus-nonce: 91e4ef1c8e645e1e33000f667e60fa85
pending-ci: gate

Round: fourth review (round 4) of #3544. This is a body-only re-check at head a60a65d87376397adc098cbf2b7b2377ccaeca02, the head the round-3 verdict blocked. The round-3 block was class `body`, which is mechanical, so no re-cut is owed.

## Findings

none

## Evidence

- Head: ev/HEAD.txt holds a60a65d87376397adc098cbf2b7b2377ccaeca02. The live PR head is the same SHA, and the body's `## Head` names it.
- Scope is delta. The code range `git diff a60a65d873 a60a65d873` is empty (ev/delta.txt), so this round has no code delta and no `custom_components/` delta, and the scope is not widened.
- The round-3 block is resolved. The live body's `## Null control` now states `cloud_relay self-test: 501 checks, 0 failed` at this head. It also records the earlier 465 figure as taken at 8382e2aa25. Re-run at this head in a detached worktree: `bash tools/audit/seat/cloud_relay.sh --self-test` prints `cloud_relay self-test: 501 checks, 0 failed`, rc 0 (ev/selftest-relay.txt).
- I re-derived every other body figure at this head:
  - bus self-test: 202 checks, 0 failed, rc 0 (ev/selftest-bus.txt).
  - ledger self-test: 103 checks, 0 failed, rc 0 (ev/selftest-ledger.txt).
  - `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`, rc 0. `--budgets` exits rc 0 (ev/policy-lint-head.txt).
  - `node tools/policy/brief_lint.mjs`: rc 0, with no VACUOUS line (ev/brief-lint-head.txt).
- Merge with main: `git merge-tree --write-tree origin/main a60a65d873`, against origin/main 50373173d4, prints one tree with rc 0 (ev/delta.txt). The merge base is e23124ff6e. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so this contract is current.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden are untouched on the three-dot range (ev/delta.txt).
- Mutation: the patch is unchanged since round 2, which recorded every production mutant KILLED and NULL SURVIVED. No line changed in this round, so I re-ran no mutant.
- CI: `merge_train.py classify a60a65d873 --pr 3544` read `WAIT ... pending: gate red: none` on every poll from 00:09:43Z to 00:43:23Z (ev/classify.txt). No owed red was reported, and the owed-reds set is in ev/owed-reds.txt. The packet's `introduced-red` refusal (unreadable while `governance / instrument-self-tests` was still running) is in ev/review-packet.md. Classify, which decides, reported no red. The relay posts this verdict only once CI is green at this head.
- Carry audit: the packet's carry_audit over the live body reads `0 finding item(s)`. The closing self-audit ran over the verdict, with the body's verbatim `## Forward-carry` and `## Friction` sections (both `none`) as `--body` (ev/carry-audit.txt).
