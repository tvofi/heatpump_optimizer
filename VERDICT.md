Fix review: merge 3520a10703629e3fb5bd4af8e8f7cad97c993168

#1835 card tiles two across, round 2 (delta plus a main merge). Code head measured: 3520a107. PR head a9861b00 is 3520a107 plus docs/delivery/1835.md only (git diff --stat: 1 file), so this verdict carries to it. git merge-tree --write-tree origin/main(1aefd2d0) a9861b00: rc 0.

Round-1 block cleared by e2cb41e9 (tests/card.mjs only):
- The repeat(4) guard is now /\.(tiles|hl-stats)\b[^{]*\{[^}]*repeat\(4/.
- A new check opens the dialog Plan page, clicks the second [data-stat="score"], and requires role=button, _scoreOpen true and a score-breakdown in the dialog.

Main merge (1aefd2d0, which includes UX-1 #1830): the card .js delta against main is the round-1 change unaltered. card_claimed_drift.txt keeps UX-1's 39 lines, and each gains this PR's reason ("card tiles: two across, plan page tiles"). docs/dashboard-card.md keeps UX-1's narrative wording and adds this PR's text. VERSION, the manifest and RELEASE_NOTES are untouched against main.

RESULT card.mjs at 3520a107: rc 0, ALL CARD CHECKS PASSED.
RESULT card_drift.mjs at 3520a107: rc 0, "39 state(s) moved and claimed, 1 identical".
RESULT mutants (mutants.py, card.mjs as the harness): all six are KILLED.
- M1: .tiles back to repeat(4).
- M2: stats removed from the plan page.
- M3: a min-width rule widening .hl-stats to repeat(4) (round 1: survived).
- M4: the same rule on both rows.
- M5: score wiring on the first copy only (round 1: survived).
- M6: overflow-wrap back to anywhere.

CI on a9861b00 at review time: no red. mutation, budget-raise-gate, pr-contract, policy-docs, delivery-status and nightly-status are green. fast, browser, coverage, typing and env-matrix are still running. The merge seat merges only on green.

Not verified: Safari or WebKit rendering. card_browser is Chromium only.
