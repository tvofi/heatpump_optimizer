# Review packet #3544
head: a60a65d87376397adc098cbf2b7b2377ccaeca02
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=132251724366 in_progress
budget-raise-gate / budget-raise-gate id=132251724588 success
cancel-superseded id=132251457546 skipped
codeql id=132250359629 skipped
codeql / Analyze (actions) id=132251724397 success
codeql / Analyze (javascript-typescript) id=132251724385 in_progress
codeql / Analyze (python) id=132251724364 in_progress
gate id=132250991545 success
governance id=132250423624 skipped
governance / delivery-status id=132251727068 skipped
governance / delivery-status-publish id=132251726628 skipped
governance / env-matrix id=132251724477 in_progress
governance / instrument-self-tests id=132251724348 in_progress
governance / policy-docs id=132251724310 in_progress
governance / record id=132251725979 skipped
governance / wave-script id=132251724512 in_progress
hassfest id=132250418423 skipped
hassfest / hassfest id=132251724235 success
kernel-points id=132251726734 skipped
pr-contract id=132250360765 skipped
pr-contract / pr-contract id=132250601173 success
prelude id=132251455807 success
refresh id=132251458071 skipped
sweep-self id=132251334166 skipped
tests id=132250411388 skipped
tests / arch-instrument id=132252061663 queued
tests / briefs id=132251724382 in_progress
tests / browser id=132252061718 queued
tests / ci-ratchet id=132250339011 skipped
tests / claims-autofix id=132250338182 skipped
tests / closure-scope id=132251724436 success
tests / closures id=132252061757 queued
tests / closures-autofix id=132250338069 skipped
tests / coverage id=132252061633 queued
tests / coverage-ratchet id=132250337894 success
tests / fast (3.14) id=132252061691 queued
tests / graders-head-copy id=132250338100 success
tests / lane-proofs id=132250338950 success
tests / mutation id=132251724467 success
tests / mutation-autofix id=132252107094 skipped
tests / mutation-pins id=132252106409 skipped
tests / nightly-ha id=132252064049 skipped
tests / nightly-status id=132251726561 skipped
tests / replay id=132252064468 skipped
tests / typing id=132252061606 in_progress
validate id=132250423159 skipped
validate / validate-hacs id=132251724226 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132251724348: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  unverified git merge-tree --write-tree origin/main 8382e2aa25
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge origin/main
             `git merge` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 3 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head a60a65d87376397adc098cbf2b7b2377ccaeca02)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at a60a65d87376397adc098cbf2b7b2377ccaeca02
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

## Delta diff: git diff a60a65d87376397adc098cbf2b7b2377ccaeca02 a60a65d87376397adc098cbf2b7b2377ccaeca02

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
