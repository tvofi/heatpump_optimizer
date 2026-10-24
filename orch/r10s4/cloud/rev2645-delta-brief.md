Delta re-check reviewer for PR #2645, group R10-FLOW-TOOLKIT-MEASURE, head 42cb7d1692680f3ebb41477d86be68bcc0a36321. Review the delta only. The train refuses to carry the 05b9c1d5 verdict because 42cb7d16 merges 6d3770f39, a conflict-resolution merge that is not on main. The verdict line covers 42cb7d16 only. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names (read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json), never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(1) The tree of 42cb7d16 equals the git merge-tree of 05b9c1d5 and 57b7b4994, except for the removal of the three conflict markers in tools/audit/seat/INSTRUMENTS.md.
(2) Both the flow_metrics.py row (#2645) and the gh_read.py row (#2639) are kept, with no duplicate rows, and every row names a file present at the head.
(3) CI at 42cb7d16 from one bulk check-runs read, including entities.
(4) carry_audit pr 2645 reports 0 unrouted.

Model for this review: claude-sonnet-5-5.
bus-nonce: 09bb1e7be482a702394c58c21efbf7b5
