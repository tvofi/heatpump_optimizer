Fix reviewer for PR #2655, roster ops only, no group, head fb8351f624a6cbc4602c22828892bc7ce25c52af (row commit fb8351f62). Review against the PR body and say so. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(1) The three-dot diff of dev/programme/rosters/wave-r10-groups.json against origin/main holds ONLY the 4 batch-23 ops: 36c467b39, 976b09c25, 9169bb834 and b9e3a651d. Batch 22 already merged in #2651, so a batch-22 carry appearing in this diff is a block. Expected: 168 -> 169 groups, 1 new, 3 changed, none removed, and done 91 -> 92. Concretely: set-stage done on R10-FLY-GH-READ-RETRY at 57b7b4994 with pr 2639 (36c467b39); the P-H carry on R10-FLOW-ROSTER-FREEZE (976b09c25); the new group R10-STRUCTURE-ALIAS (9169bb834) with its one carry; O19 dropped from R10-CURRENCY (b9e3a651d).
(2) brief_lint TOTAL 0, ref_privacy --check 0 refused, and carry_audit pr 2655 reports 0 unrouted.
(3) No commit in the PR carries an attribution trailer. This is the first opener since #2652's fix.
(4) CI from one bulk check-runs read.
(5) The body's figures re-derive at the head.

Model for this review: claude-sonnet-5-5.
bus-nonce: 2bc0089477583c66bd0cd1840475b099
