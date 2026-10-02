Fix review: merge d1ac968a6cc66d1c8bc877bee6f45fb10cb3f5a8

Round 2 of R9-UI-4 (#1817). This covers code head b7ab9278bf36c7df7b378a7722f3a55c9a8a78df, which is the round-1 head 6277884f plus one tests-only commit, and the merge delta b7ab9278..d1ac968a (main 0bfb8883 merged in, plus the delivery row). Round 1's findings at 6277884f stand for everything this delta does not touch (evidence dir UI-4-review-6277884f).

Delta 6277884f..b7ab9278: tests/card.mjs only, +91 lines. It adds panelEscapes(), which checks that every series path and dot, the actioned band, the shared-step hatch, the estimated wash (one per panel) and every vertical grid rule stay inside their own panel. It runs in three scenarios (estimated prices, shared steps, actioned slots) and refuses an empty sweep or a panel count other than 3. A separate check asserts that an emptied panel is dropped.

RESULT card.mjs @b7ab9278: ALL CARD CHECKS PASSED, and all 4 new checks ok
RESULT card_drift.mjs 661d56f4 @b7ab9278: 39 state(s) moved and claimed, 1 identical

Round-1 mutants re-applied at b7ab9278, one at a time (mutants.py), all killed by card.mjs:
- MA baseOf returns plotB: 3 checks red (the three panel-escape checks)
- MB actioned band at plotB: 1 red (actioned slots)
- MC shared hatch spans plotT..plotB: 2 red
- MD dark outdoor = dark house: 4 red (colour vision)
- ME estimated wash in the first panel only: 1 red
- MF now-temp label at the top: 1 red (top-strip rows)
- MG one full-height vertical rule: 3 red
- MH hidden panels keep their height: 1 red (emptied-panel check)
These match the fixer's counts (3, 1, 2, 4, 1, 1, 3, 1).

Merge delta b7ab9278..d1ac968a:
- merge-tree(0bfb8883, b7ab9278) gives tree b1eed544, which equals the merge commit's tree.
- Card JS, card_claimed_drift.txt, docs/img and docs/dashboard-card.md are byte-identical to b7ab9278.
- tests/card.mjs: the merge's change hunks equal main's own change since 661d56f4 (merge_delta_card.patch, compared hunk for hunk), and panelEscapes plus its 4 checks are present at d1ac968a.
- RESULT card.mjs @d1ac968a: ALL CARD CHECKS PASSED, and all 4 panel checks ok
- RESULT card_drift.mjs 0bfb8883 @d1ac968a: 39 state(s) moved and claimed, 1 identical

Lane colours are unchanged, and the body records why. Not blocking, as in round 1.

CI on d1ac968a was queued at review time and is not cited. The merge seat merges only on CI green at this head.
