R10-CARD-COLLAPSE, the owner's request of 2026-11-09. The headline's per-reason breakdown ("Plan by reason") and the "Why now" panel are folds, collapsed by default. Each has a native `<button>` header carrying `aria-expanded`, a one-line summary that stays visible while folded, and a body left unrendered until opened. The series chips and the dashed-line notes render only in the expanded dialog's Plan page. New strings are in the card's own `STRINGS` table in en, sv and de. The `translations/*.json` files hold no card strings, so this branch leaves them unchanged.

Design decisions, each with its reason:
- **The body is unrendered while folded, not hidden.** This follows the dialog's existing hidden-page rule.
- **No `id`/`aria-controls`.** The headline renders twice in one shadow root (card and Plan page), so an id would be minted twice (the #558 C2 defect class). The body follows its own button directly.
- **Fold state lives on the card instance (`_folds`), not in storage.** It survives every plan-refresh rebuild, as `_scoreOpen` does, and resets to folded on page load, which is the requested default.
- **Focus returns to the rebuilt copy of the pressed header.** The shadow root is replaced on every render, so without this a keyboard user's Enter would drop focus.
- **The folded card keeps the visibility the dialog's chips last saved.** The chips write that state, and the dialog is now the only place to change it.

Polish of the non-expanded card. Each change is listed with why. The ordering review is on the light and dark screenshots of `tests/card_browser.mjs` `cardCollapse` (written under `HPO_NL_OUT`).
- **Fold summaries wrap rather than ellipsise.** A clipped summary hides the one line a folded section is reduced to. The P9 grid's no-clip rule refused the ellipsis.
- **A divider under the last fold closes the headline off from the chart.** Without it, the open Why-now rows ran straight into the price panel.
- **The time axis keeps a clamped end label's neighbour at least half the gap the centred labels get.** At the folded tile's width the clamped "06:00 AM" sat against "08:00 AM" as one run of text. The neighbour is now dropped and its gridline stays (`timeAxis`, `clampedGap`).
- **Ordering kept: header, tiles, savings and score, the two folds, then the chart.** The folds are text summaries of the plan the tiles total, so they sit with the tiles. The chart stays last because it was the reason for expanding.

## Head

d7c39135839ea0a985796105ebfda170cdd6d505, on merge base dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd (origin/main at the fork; measured 2026-11-11 UTC).

## Mutation proof

Each mutant edits the card at this head, then `PYTHONPATH=tests/hastub node tests/card.mjs` runs and the file is restored with `git checkout`:
- M1, folds open by default (`_folds` initialised true): `collapse: both folds render a header button, collapsed by default`, `collapse: a folded section renders no body`, `collapse: a click opens its own fold and only that one`, `collapse: the why-now fold opens to its rows`, `collapse: a second click folds it again`.
- M2, the toggle is a no-op (the `this._folds = {...}` line deleted): `collapse: a click opens its own fold and only that one`, `collapse: the why-now fold opens to its rows`, plus every narrative and why-now content check that opens its fold through the header, e.g. `narrative: one row per item` and `why-now: a row per known driver, with its mark and signed share, in the published order`.
- M3, the inline legend restored (`${this.legend.html(this._series, "card-")}` back in the card): `collapse: the folded card renders no series chip and no legend`, `the dialog carries its own legend and close button`, `the expanded card renders exactly one legend, the dialog's`, `every note id in the shadow root is unique`, `the legend offers exactly one chip per series`, `legend stays off the savings page`.
- M4, no focus return (the `again.focus()` line deleted): `collapse: focus returns to the rebuilt header`.
- M5, no `stopPropagation` in the fold click: `collapse: the toggle does not reach the card's open-on-click`.
- M6, the axis threshold back to `minLabelGap` beside a clamp: `the inline 12 h / inline 24 h / expanded 24 h / inline 48 h / expanded 48 h time axis spaces a clamped label at least half its usual gap`.
- M7, no total summary (`const summary = false`): `collapse: the narrative summary is the rows' kWh and cost total, visible while folded`, `collapse: the headers speak the card language`.

The browser lane's `cardCollapse` (`tests/card_browser.mjs`) pins the same default, toggle and chip absence in a real Chromium, in light and dark. Its keyboard arm presses Enter on the focused header, then Tab and Space. No scope selects that lane, so it was run here; CI runs it after the handoff.

## Null control

There is no finder harness, because the group is an owner request, not an audit finding. The before and after is this branch's `tests/card.mjs` block, run at both ends.

At the merge base, `tests/card.mjs` with this branch's new `R10-CARD-COLLAPSE` block fails `collapse: both folds render a header button, collapsed by default`, `collapse: a folded section renders no body`, `collapse: the narrative summary is the rows' kWh and cost total, visible while folded` and `collapse: the why-now summary is its strongest driver, visible while folded`. It then throws at the first header click, because the base renders no `[data-fold]` element. M3 is the chip arm's control: the folded card's legend-absence check goes red the moment the card copy renders again. The axis check's control is M6. On the unpaid rule, a clamp's neighbour sits under half the typical gap at five of the six horizon and size pairs, so the check is not passing on an axis with no clamp. Its sibling check `the ... chart really does clamp a label to the plot edge` stays green at this head.

## Figures

- `PYTHONPATH=tests/hastub node tests/card.mjs` at this head: `ALL CARD CHECKS PASSED`.
- `PYTHONPATH=tests/hastub node tests/card_drift.mjs`: every state that renders the card moves and is claimed in `tests/golden/card_claimed_drift.txt`, because the fold rules ride every rendered stylesheet; `editor_schema`, which renders no card, stays identical.
- `NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` at this head: exit 0, no `FAIL` line (the `cardCollapse` lane and the P9 grid's new `folds_open` cell included).
- `python3 tools/audit/archscore/score.py --diff dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd`: `dS +0.0000 NULL`. An intermediate head of this branch read `card_clone_copies` 103 -> 108. It was paid by merging the narrative summary into `narrativeParts`, one `weightOf` helper, and one `{score, narrative, whynow}` disclosure argument to `headlineHtml`; the clone classes at this head equal the merge base's.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. The diff adds no Python.
- `python3 tests/closure.py select --diff dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd --workdir "$D"`: `MODE: SCOPED`. Each script in `scope.run` exits 0 at this head with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`. So do the `run_always` lines `python3 tests/env_drift.py --claims-only origin/main` and `python3 tests/closure.py selftest`.
- `HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs`: regenerated the figures P40 names as stale (tile, plan and plan-why, light and dark) and `pages.json`. The other page PNGs it rewrote were raster-only and were restored to main's bytes.

## Red checks

none

## Forward-carry

none

## Friction

none
