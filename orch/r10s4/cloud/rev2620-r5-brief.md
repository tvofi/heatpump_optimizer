Delta fix reviewer for PR #2620, group R10-CURRENCY, round 5, head ce7ed26bfe4724d99ad43dcfc9c1d679933ce156 (branch fix/r10-currency). The previously reviewed head is 0b9431ba; the earlier verdicts are on review/2620 and verdict/2620. Round 5 adds three commits:
- 9195247d4 merges origin/main a6620c30a, resolving the two coordinator.py conflicts to main's side;
- 5115ddc15 re-records structure_budgets.json and raises seam_cut_total 714 -> 715;
- ce7ed26bf merges that into the PR.

Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder's harness the group brief names (jq the group from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json). Your ev/ MUST contain ev/HEAD.txt holding the full 40-hex head.

Verify:
(1) The merge resolution. Compare `git diff 0b9431ba ce7ed26bf` against what main brought. The deleted `_cop_watch` really has no caller: grep it and its seam_map and killed_by entries. #2620's two features.py checks passing `_rs_advice(coord)` is the right call shape for main's `_scores_view`. Nothing #2620 fixed was silently reverted by taking main's side; check D14-s3-01, the narrative currency fix, by mutation: revert it and the named check goes red.
(2) The four red-on-revert mutants in ## Head reproduce at this head. tests/features.py and tests/entities.py pass at the head with PREPR_SKIP_CLOSURES=1. Record the scoped-gate MODE line.
(3) The budget record. Running `python3 tests/structure.py` at the head reproduces seam_cut_total 715, class_excess_loc 18243 and max_class_loc 8479. Every other metric is at or under main's cap. Check that the +1 cut is #2620's own `self.currency` read in `_narrative_view`: count at main against the head. The raise was ruled under mandate 6329234399. Your job is to check the body's `## Raise justification` facts (each payment's measured figures, archscore dS) and that the section passes the gate's own function: `python3 -c 'import sys; sys.path.insert(0,"tools/policy"); import budget_raise_gate as g; print(g.justification(open(sys.argv[1]).read()))' body.md`. Rule on the raise only if a payment the body missed would improve the architecture. Name it concretely.
(4) The merge-tree against current origin/main is clean, CI at this head is read with one bulk check-runs call (budget-raise-gate is red by design until the approving review), VERSION is untouched and the commits carry no Claude footers.

Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API (bulk-list once, prefer git, stop on a 403); no Claude footers.
