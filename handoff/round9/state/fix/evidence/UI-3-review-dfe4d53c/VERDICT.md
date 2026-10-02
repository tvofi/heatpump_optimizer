Fix review: merge dfe4d53cb355f3637449ab61d52bcf7928bd32e0

Round 2 of R9-UI-3. This round judges the delta a0fe0243..dfe4d53c (one commit, parent a0fe0243, three files: the card, tests/card.mjs and tests/card_browser.mjs). The transport tip d4b77749 differs from dfe4d53c only under tools/audit/handoff/.

## The round-1 block is cleared

The tiles, the headline stats and the idle pill now take their text from --hpo-ink and --hpo-ink-2. Those are literals, switched by the same darkMode that switches --hpo-surface-2. The .tile and .hl-stat rules also re-point --hpo-text and --hpo-text-2 at the ink literals, so every descendant (tile-k, tile-u, hl-caveat) is paired with the surface it sits on.

RESULT (my own probe, theme_probe.mjs, dfe4d53c, darkMode false):

| theme variables | tile-k, tile-u, idle pill, hl-label | tile-n, hl-value |
|---|---|---|
| dark | 4.56:1 | 15.26:1 |
| HA default light | 4.56:1 | 15.26:1 |

At a0fe0243 the dark case measured 2.63:1 and 1.24:1.

## The new check is not vacuous

I ran the head's tests/card_browser.mjs against a0fe0243's card. Two checks fail, rc 1:
- R9-UI-3 tile, headline-stat and pill text clears 4.5:1 with dark theme variables, darkMode false
- the same check with light theme variables and darkMode true

Restoring dfe4d53c's card makes both pass.

## Re-run at dfe4d53c

- card.mjs: ALL CARD CHECKS PASSED.
- card_drift.mjs origin/main: 39 states moved and claimed, 1 identical, so the claim file still covers the delta.
- card_browser.mjs with HPO_BROWSER_SCOPE=full: rc 0, ALL BROWSER CHECKS PASSED.

Round 1's re-run (structure.py rc 0, entities.py rc 0, 18 of 18 JS mutants killed, 20 of 25 UI-3 checks failing at base) stands. The delta adds no seam those cover differently, and the two ink pairs join the card.mjs token contrast check.

## Other checks

- `git merge-tree --write-tree origin/main dfe4d53c` exits 0 against main c4f1c263.
- The fix-review contract is current: the briefs diff since the merge base is empty.
- There are no resume files in the code-head ancestry.
- VERSION, the manifest and the notes heading are untouched.
- The live branch head at posting time is d4b77749, a transport commit above dfe4d53c.

Not run: the full gate and the mutation table. The merge seat cites the head's CI (fix-review.md step 11). No Python changed, so typing_ruler and ha_contract have no site.
