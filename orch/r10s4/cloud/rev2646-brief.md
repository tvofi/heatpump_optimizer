Fix reviewer for PR #2646, group none (roster batch 20, roster ops only), head bd74ad8c23f88c5a1ef19565d1eb9b38e2bde210. There is no group; review against the PR body and say so. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(1) The three-dot diff of dev/programme/rosters/wave-r10-groups.json against origin/main changes exactly 11 groups: ARCH-PLANNER done at f38f9185; RECORD-API-BUDGET done; the LOOP-CPU resume (pr 2632, 577ec62d); the 4 toolkit-measure carries re-homed; the NO-FOOTERS carry; and the P-D, P-E and P-F carries on R10-FLY-OPENPR-ATOMIC, R10-FLY-RELAY-REVIEW-FF and R10-POLICY-LINT-FAMILY. Nothing else changes.
(2) Each "done" commit is an ancestor of origin/main.
(3) Stages are done 90 and in-progress 10. No group is added or removed.
(4) Main's roster equals the merge base.
(5) brief_lint TOTAL 0 and ref_privacy --check 0 refused.
Read CI at the head with one bulk check-runs read, not per-check calls.

Model for this review: claude-sonnet-5-5.
bus-nonce: 6d30140f90503ca22c2def0ea6b1c122
