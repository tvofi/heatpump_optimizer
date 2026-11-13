Fix review: blocked a60a65d87376397adc098cbf2b7b2377ccaeca02 body: the Null control quotes the cloud_relay self-test as 465 checks at this head, which prints 501

bus-nonce: 41c4643bafddfb0eb74e5513f05f272b

Round: third review (round 3) of #3544. This is a delta review over the blocked head 8382e2aa25cab7c82b6e6ce8e5059412d5e970c3, at head a60a65d87376397adc098cbf2b7b2377ccaeca02.

## Block

1. body: the PR body says "All measurements below are at the head given below". Its `## Null control` then states that at this head `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 465 checks, 0 failed`. At a60a65d873 that command prints `cloud_relay self-test: 501 checks, 0 failed`, rc 0 (ev/selftest-relay.txt). Control: at the previously reviewed head 8382e2aa25 the same command prints `465 checks, 0 failed` (ev/selftest-relay-at-8382e2aa25.txt). So the figure was carried from that head and not re-taken after the main merge. Main's bdf1dc827e and 7d09eae1ba, which the merge brings in, add the 36 checks (ev/delta.txt). The fix is a body edit and no code change: re-take the figure at this head, or scope it to the head where it was taken. This is a mechanical class (`body`) and owes no re-cut. The bus (202) and ledger (103) counts re-derive exactly at this head (ev/selftest-bus.txt, ev/selftest-ledger.txt).

The previous block is resolved (see Evidence). Nothing else blocks.

## Findings

none

## Evidence

- Head: ev/HEAD.txt holds a60a65d87376397adc098cbf2b7b2377ccaeca02, the head the dispatch names. The body's `## Head` names it, merging the authored head 440ae4033125.
- Scope is delta, per the packet's `## Review scope` line. The delta 8382e2aa25..a60a65d873 is a merge of origin/main e23124ff6e and nothing else. The PR's three-dot diff against the new base is identical to its three-dot diff at 8382e2aa25 against the old base 0723540391, once index and hunk-header lines are stripped: 5 files, +202/-36. Neither merge has a resolution of its own: `git show --remerge-diff` prints nothing for 440ae40331 or a60a65d873, and their trees are equal (ev/delta.txt). The delta adds no PR-authored `custom_components/` change, so the scope is not widened.
- The previous block (red-unanswered: `tests / briefs`) is resolved. The body's `## Red checks` now names `tests / briefs` and answers it. Its claim checks out: d65839f2e2 and b4a663ebe5 are not ancestors of 8382e2aa25 and are ancestors of this head (`git merge-base --is-ancestor`). `node tools/policy/brief_lint.mjs` at this head exits 0 with no VACUOUS line (ev/brief-lint-head.txt).
- `node tools/policy/policy_lint.mjs` at this head prints `TOTAL: 0 error(s) across 51 policy file(s)`, rc 0 (ev/policy-lint-head.txt).
- Self-tests at this head, in a detached worktree: bus 202 checks / 0 failed, ledger 103 / 0, cloud_relay 501 / 0. All three are rc 0.
- Merge with main: `git merge-tree --write-tree origin/main a60a65d873` prints one tree, rc 0 (ev/merge-tree.txt). origin/main is e23124ff6e, the merge base. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden are untouched on the three-dot range against e23124ff6e (ev/delta.txt).
- Mutation: the PR's patch is unchanged from 8382e2aa25, where round 2 re-ran every production mutant KILLED with NULL SURVIVED. The merge adds no PR-authored line, so no mutant was re-run.
- CI: `merge_train.py classify a60a65d873 --pr 3544` read WAIT on all 7 polls, from 21:43:38Z to 21:51:22Z (`pending: gate red: none`; ev/classify.txt). This block is a body edit, which does not move the head, so CI was not waited out. The next round re-reads the live checks, including the packet's `introduced-red` refusal on the still-running `governance / instrument-self-tests` (ev/review-packet.md). The owed-reds set is in ev/owed-reds.txt.
