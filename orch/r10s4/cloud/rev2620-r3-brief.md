Fix reviewer for PR #2620, group R10-CURRENCY, round 3, head 72fbab2a719ce14870aa3284a35d043ea1b9588d. Round 2's verdict is probe/rev-2620-62684c0b (commit 9d0e4c38); read it. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(a) The fix is sound by design, not by budget. seam_cut_total goes to 707 through a real payment, with no raise. The roster O19 carry on R10-CURRENCY says structure.py counts occurrences, so plant an alias and see whether it would move the count, and make sure this diff did not pay that way.
(b) The four _cop_watch sites are pinned and killed in the mutation ledger by tests/features.py checks: coordinator.py BOOLOP and CMP_BOUND at the 9130 area, and CLAMP_DROP and RETURN_DEL at the 9132 area. Use the line numbers at this head. The new bound check drives a bucket at COP_BASELINE_MIN_SAMPLES-1 and at exactly the bound. Mutate each site and show red.
(c) ci_predict at the head predicts no mutation red. ## Unpinned sites reads none, and ## Red checks answers every red at the head.
(d) Fixes #2243 and Fixes #2222 are each right to close.
(e) The pre-existing round-1/2 commits carry footers, and those are not to be rewritten. Judge only this round's commits for footers.

Model for this review: claude-opus-5-5.
bus-nonce: 654004be88378fbedacb0dc55dea4c83
