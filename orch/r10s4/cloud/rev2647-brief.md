Fix reviewer for PR #2647, group R10-SCORES, round 2, head ff6cfdaabc39647855987ae54fed4a3449eb2c47. This is the round-2 fixer of R10-SCORES, on the approved design design/r10-scores (Design review: approve f01e06d24). Round 1's verdict and the design verdict are on the probe/rev-* and design refs for r10-scores; read them. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify against the design:
(a) each of the owner's plan-score items 1-3 is answered, and ARCH2-s5-C3's reading rule is applied at every score site;
(b) the six score sites in the mutation ledger are killed by the new checks; mutate each back and show red;
(c) Part of #2238 and #2258 is right, so that neither issue is closed here;
(d) ## Red checks answers every red at the head.
(e) budget-raise-gate red is expected until the mandate approval. seam_cut_total goes 708 -> 714, with 7 payments tried and dS +0.0105. Judge whether any payment was left untried, and whether the 4 that were taken are sound.

Model for this review: claude-opus-5-5.
bus-nonce: c6edd5b09341e954f6a0552c0ad06492
