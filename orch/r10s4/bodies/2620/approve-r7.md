Approved under mandate 6329234399 (scope all) at head 87f6c34edd9363b8fb0f1fb1ee709d5a36ee22f1, including the budget raise in tests/structure_budgets.json: seam_cut_total 714 -> 715.

Fix review: merge at the reviewed head ce7ed26b, which this recarry merges with main unchanged (probe e353bab9c, nonce 05aee51f; posted). The round-5 merge of main a6620c30a resolves both coordinator.py conflicts to main's side. It deletes the callerless `_cop_watch` with its seam_map entry and four killed_by pins, and D14-s3-01, the narrative currency fix, still goes red when reverted.

Raise ruling: no payment exists that improves the architecture. The body's `## Raise justification` records payments (b) and (b'), each `Architecture score: dS +0.0000 NULL`, which only re-bind the count. Payment (a) has no source data, and the survey for (c) finds no duplicated-computation reach to move. The extra cut is #2620's own instance-currency read in `_narrative_view`. The section passes budget_raise_gate's own `justification()`.

Trailers: the three older branch commits that carry attribution trailers (701448f90, 23392d5d6, 08ba3d9d7) were all authored before the no-footers guard landed (a4b27986, 2026-10-22T23:07Z). They are dismissed, as for #2632, because we do not rewrite a published branch. Round 5's commits carry none.

Recarry check: 87f6c34e has exactly two parents, d29fda65 (the recarry of the reviewed head ce7ed26b I approved as 5628871104) and main 12032c43c (#2663, roster-only). Its tree 5884f19a equals `git merge-tree --write-tree` of those two parents. No commit message carries a trailer.
