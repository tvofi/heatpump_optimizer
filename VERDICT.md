Fix review: merge dafcc5759950c7ec3faab4bf993723a758a94710

bus-nonce: 5715e29922a87f5d33585c43adaa854f

Scoped re-check (round 3) at the unchanged head; round 2's four content checks stand.

## Evidence
- Head not moved: `git ls-remote origin refs/pull/3074/head` prints dafcc5759950c7ec3faab4bf993723a758a94710.
- Red checks (1): the body's `## Red checks` now names `governance / instrument-self-tests` with its cause. Verified against the failing job log (job 124883634097): it holds `Security violation: Requested utility \`unrelated-sleep\` does not match executable name` and `pr_args self-test: 158 checks, 2 failed`. `tools/audit/seat/pr_args.sh:627` builds the `unrelated-sleep` wrapper. The body's claim that main run's job 124813746788 shows the same is confirmed (3 occurrences each of the violation line and the 158/2 line). The three-dot diff touches only HANDOVER.md and delivery/3074.md; `git diff origin/main...head` on pr_args.sh, open_pr.sh and update_pr.sh is empty. Whole check-run set read (68 runs): the only failures are instrument-self-tests and the older-body pr-contract run 41293942755; run 41317541410 (current body) shows pr-contract and gate success.
- (2) pr-contract at the current body: success (job 124882096578, 14:50Z); its log shows carry_audit `CARRY-AUDIT: 0 finding item(s)`; packet carry_audit also 0.
- (3) `merge_train.py classify dafcc5759950c7ec3faab4bf993723a758a94710`: GREEN, pending none, red none (rc 0).
- `git merge-tree --write-tree origin/main dafcc5759950c7ec3faab4bf993723a758a94710` exits 0.
- governance / instrument-self-tests is red at this head; it is not a required check and does not block.
