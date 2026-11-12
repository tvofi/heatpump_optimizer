Fix review: merge c3857c8fbc220dbe2466662e8233f2c3ebb4d999

bus-nonce: 5a48fdb126203eae707c479705aa7f5f

## Scope

This is round 1, a fresh review. `review_carry.py 2f618844 c3857c8f` prints FRESH-REVIEW. The diff is three-dot against merge base 19baca7618 and touches only `tests/card_browser.mjs` and `dev/programme/delivery/3509.md`. It changes no production line, `VERSION`, manifest, notes heading, claim file, budget or closure.

## Evidence

- Head measured: c3857c8fbc220dbe2466662e8233f2c3ebb4d999. Re-read at post time with `git ls-remote origin refs/pull/3509/head`, and it is unchanged (ev/head-at-post.txt). The body's head line names this SHA.
- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main c3857c8f` returns rc 0, with no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify c3857c8f --pr 3509` printed `GREEN c3857c8fbc220dbe2466662e8233f2c3ebb4d999 pending: none red: none` (ev/classify.txt). `tests / nightly-status` is red from a cancelled scheduled run. It is outside the `owed-reds` set, so no `## Red checks` answer is owed.
- RESULT clean head: `HPO_ONLY=1 node tests/card_browser_only.mjs` ran only `themeMismatch` and `themeLiveSwitch`. It printed 19 ok of 19 (12 themeMismatch, 7 themeLiveSwitch), `ALL BROWSER CHECKS PASSED`, rc 0 (ev/run-head-clean.txt). This matches the body's "all 7 ... and all 12".
- RESULT mutation proof: I planted the released row shape. `.health-row, .fact-inbox-row` keep `--hpo-surface-2` but lose the ink re-point (ev/mutant.txt). Exactly 4 checks fail, rc 1 (ev/run-head-mutant-released-rows.txt):
  - both mismatched arms of `themeMismatch`: 65 runs under 4.5:1 each, Advisor rows at 1.24:1 and 1.11:1;
  - both `between HA's theme write and its hass update` checks: 40 of 59 runs, at 1.24:1 and 1.11:1.

  Every figure the body quotes re-derives exactly (59, 40, 65, 1.24, 1.11). After the run the card was restored with `git checkout`.
- RESULT null control: under the same mutant these stay ok: both matched arms (tile, chart and dialog), both `after the card's re-render` checks, both reach checks and the start check. That matches the body's null-control list.
- Figure re-derived: the card has 0 `@media ... prefers-color-scheme` rules and 2 `matchMedia(` calls, at lines 2976 `(pointer: coarse)` and 2991 `(prefers-reduced-motion: reduce)`.
- Refactor check: `hpoContrastKit.sweep` is the removed inline sweep moved verbatim. `skipDialog` is `view === "tile"`, and labels are `view`, as before. The tile and chart checks in all four arms stay green at the clean head and under the mutant.
- Harness (step 9): the finder's harness is the browser lane itself. The packet names no separate finder's harness, and this PR adds checks to that committed lane rather than an out-of-tree instrument. The scratch driver that both the fixer and I used only filters which functions run (ev/scratch-driver.diff). It is disclosed as the reviewer's own and is not owed to the tree.
- Class (step 6): one seam. The defect class is own text on a surface-2 block under the mismatched theme/darkMode pairing. `themeMismatch` sweeps every own-text run on the tile and on every dialog page in both mismatched arms. The live switch's "between" frame is that same pairing, and its reach check shows it, so it adds reach rather than a new population. No seam is left outside the diff.
- Forward-carry: the body says none, and this test-only PR changes no later stage. The carries it settles (0 and 1) were not in a tree carry file. A scout search found `R10-HOTFIX-CARD-HEALTH-TEXT` in no carry JSON or roster entry, so I judged them against the body's own statement of them.
- Not re-derived: the body's full-lane `ALL BROWSER CHECKS PASSED` at e1361b108c. I cite CI's green `tests / browser` at this head instead and did not re-run the full lane.

## Findings

none

## Friction

none
