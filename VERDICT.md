Fix review: merge 9cd195065146fcf457bf86d1d9d4d5cbcf4eabe8

R9-UX-2, PR #1836, round 2. Code head 9cd19506 (main 3bd6f122 merged at e335ad27; its tree equals `git merge-tree --write-tree 3bd6f122 6514ed1a` = 5acf2597, so the merge carried no resolution). Live PR head 66477d49 differs from 9cd19506 only by docs/delivery/1836.md (`git diff --name-only 9cd19506 66477d49`), so this verdict carries to it. Body ffab404d names 9cd19506. Contract copy current.

## Round-1 blockers

1. Price of a degree: delivered from the score sensor's `price_tiles` (target_minus_1 saving as the value, target_plus_1 in the detail); "Try in what-if" seeds the what-if comfort with the tile's target and runs it; without tiles it is an "enable to see" row. The body now states the producer exists. Closed.
2. Hot water at 55 °C: `dhwCostPerDay` interpolates between swept candidates; check `the hot water at the off-grid default 55 is priced by interpolation`. Closed.
3. Ranking: the fixture is unordered; R1 (sort removed) is killed. Closed.
4. Carry: `.claude/workflows/carry-1795.json` second entry carries the UX-5 open_schedule -> apply change with control and remeasure; `brief_lint.mjs` TOTAL 0 errors across 45 files. Closed. (The roster's R9-UX-5 brief on handoff/audit-r9-fixplan is the coordinator's copy to update.)

## RESULT lines

- RESULT card.mjs at 9cd19506: rc 0, ALL CARD CHECKS PASSED (card_head_inbox.txt). Disclosed: this container's Home Assistant (2024.3.3) cannot import main's coordinator, so plan_view.py did not run here; card.mjs read the plan payload generated at 6514ed1a in round 1. The inbox checks do not read that payload; CI's card run at the head is the authority for the plan pages.
- RESULT card_drift.mjs vs 3bd6f122: rc 0, "39 state(s) moved and claimed, 1 identical".
- RESULT merge-tree origin/main x 9cd19506: rc 0, no conflict.
- RESULT VERSION, manifest version, RELEASE_NOTES heading: untouched.
- RESULT my mutants (mutants.py, mutants.txt), 11 run: 9 killed (R1 no sort, R3 gap 0, R4 at recommendation, R6 valve rounding, D1 no run, D2 no seed, D3 up tile as target, D4 no interpolation, D6 degree sign).
- Survivors, not blocking: D5 (read attributes on `unavailable` again) is equivalent in production, because Home Assistant publishes none there. D7 (always offer the degree opt-in row) shows a duplicate "turn on" row once the tiles exist; this is the body's stated opt-in departure.
- RESULT CI on 66477d49 at 2026-10-02T02:07Z: no red conclusion. Two cancelled runs (pr-contract, budget-raise-gate) were superseded by green reruns. fast (3.14), closures, coverage and CodeQL python were still running; the merge seat waits for them green.
- Harness: mine (hand mutants in a scratch worktree); a feature PR has no finder harness. The fixer reported stress.py, typing and ha_contract unrun; typing is green in CI.
- Owner gate: tests/card_browser.mjs is code-owned, so this also needs tvofi's approving review at the head.
