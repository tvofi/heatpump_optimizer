Re-review reviewer for PR #2651, roster ops only, no group, head 91e37c0964e6c203108ae53814dcf1f0a0761bf1. Review against the PR body and say so. The previous verdict, probe/rev-2651-4c449d57, was merge at 2bb638af. The relay then merged batch 22 (bb7c6eb27) in. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(1) The three-dot diff of dev/programme/rosters/wave-r10-groups.json against origin/main equals batch 21 (as verified at 2bb638af) plus exactly three carries: R10-FLY-CARRY-DISPOSITION 3c8cf18ca, R10-FLOW-DESIGN-STAGES ad0c114f5, R10-FLY-RELAY-REVIEW-FF bb7c6eb27. Each matches its "### Triage" text in the PR body's ops list, and none of the three groups is done or absorbed.
(2) 167 -> 168 groups; none is removed.
(3) The body's figures (13 ops, 61 insertions and 10 deletions) re-derive at the head.
(4) brief_lint TOTAL 0, ref_privacy --check 0 refused, and carry_audit pr 2651 reports 0 unrouted.
(5) CI from one bulk check-runs read.

Model for this review: claude-sonnet-5-5.
bus-nonce: 1d6b263f3cd8c61f9744e55b6ce5008e
