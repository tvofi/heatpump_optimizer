Fix review: blocked 73028145f27d5460892ad1b975c837a562278973 mutation: two named changes unpinned; the plan-page score wiring and the .hl-stats media guard survive their mutants

Round 1. Head measured: 73028145 (main 8a0ca90a merged in). No PR is open for claude/project-thread-i2vxe4 yet, so there is no CI run to cite.

Meets the ask: yes. Against tvofi's Safari screenshot (a 4-column grid in a narrow column, "SEK/k Wh", "45/10 0"), both rows are now repeat(2) with no viewport rule. The removed @media (max-width: 600px) column override was the viewport-keyed cause. The plan page gets ${stats} above the away strip and chart. tilesHtml and headlineHtml emit no id, so the second copy duplicates no id.

RESULT card.mjs at head: rc 0, ALL CARD CHECKS PASSED (PYTHONPATH=tests/hastub python3 tests/plan_view.py first).
RESULT card_drift.mjs at head: rc 0, "39 state(s) moved and claimed, 1 identical". No unclaimed drift and no stale claim.
RESULT VERSION, manifest and RELEASE_NOTES are untouched (diff --stat 8a0ca90a...head: 8 files, none of them).

Targeted mutants (mutants.py, output mutants.txt), card.mjs as the harness:
- M1 .tiles back to repeat(4): KILLED.
- M2 ${stats} removed from the plan page: KILLED.
- M3 `@media (min-width: 601px) { .hl-stats { grid-template-columns: repeat(4, ...) } }` added: SURVIVED. The new check's name and comment say neither row is widened by a media rule, but its regex guards only `.tiles[^{]*{...repeat(4`. A viewport rule widening .hl-stats alone is the bug's own shape and passes.
- M4 the same rule on `.tiles, .hl-stats`: KILLED.
- M5 the score wiring back to the first [data-stat="score"] only: SURVIVED. The PR names "the score toggle is wired on both copies" as a change. No check clicks or inspects the plan page's copy, so it can silently regress to dead.
- M6 .tile-v back to overflow-wrap: anywhere: KILLED.

To clear the block:
(a) Extend the repeat(4) negative guard to .hl-stats, e.g. /\.(tiles|hl-stats)[^{]*\{[^}]*repeat\(4/, or any selector list containing either.
(b) Add a check that the dialog plan page's [data-stat="score"] carries role="button", and that firing its click toggles _scoreOpen.
Show M3 and M5 killed by the new checks.

Not verified: Safari or WebKit rendering. The fixer's card_browser run was Chromium only, and this review did not re-run it.
