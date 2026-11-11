R10-CARD-COLLAPSE, the owner's request of 2026-11-09. The headline's per-reason breakdown ("Plan by reason") and the "Why now" panel are folds, collapsed by default. Each has a native `<button>` header carrying `aria-expanded`, a one-line summary that stays visible while folded, and a body left unrendered until opened. The series chips and the dashed-line notes render only in the expanded dialog's Plan page. New strings are in the card's own `STRINGS` table in en, sv and de. The `translations/*.json` files hold no card strings, so this branch leaves them unchanged.

Design decisions, each with its reason:
- **The body is unrendered while folded, not hidden.** This follows the dialog's existing hidden-page rule.
- **No `id`/`aria-controls`.** The headline renders twice in one shadow root (card and Plan page), so an id would be minted twice (the #558 C2 defect class). The body follows its own button directly.
- **Fold state lives on the card instance (`_folds`), not in storage.** It survives every hass-driven rebuild, as `_scoreOpen` does, and resets to folded on page load, which is the requested default.
- **Focus returns to the rebuilt copy of the pressed header**, the dialog's copy when the dialog's was pressed. The shadow root is replaced on every render, so without this a keyboard user's Enter would drop focus.
- **The folded card keeps the visibility the dialog's chips last saved.** The chips write that state, and the dialog is now the only place to change it.

Polish of the non-expanded card. Each change is listed with why. The ordering review is on the light and dark screenshots of `tests/card_browser.mjs` `cardCollapse` (written under `HPO_NL_OUT`).
- **Fold summaries wrap rather than ellipsise.** A clipped summary hides the one line a folded section is reduced to.
- **A divider under the last fold closes the headline off from the chart.** Without it, the open Why-now rows ran straight into the price panel.
- **The time axis keeps a clamped end label's neighbour at least half the gap the centred labels get.** At the folded tile's width the clamped "06:00 AM" sat against "08:00 AM" as one run of text. The neighbour is now dropped and its gridline stays (`timeAxis`, `clampedGap`).
- **Ordering: the savings and score, the two folds, then the chart.** The folds are text summaries of the plan the tiles total, so they sit with the tiles. The chart stays last because it was the reason for expanding.

## Head

e277484c38bf3349ab534340c6880274bf404d69, on merge base a7628041dc02e298c5399003d4c0576391dd5c4e (origin/main's tip; measured 2026-11-11 08:08 UTC).

## Repair round 1

The first review blocked `pin-missing` at b55fc8eb5bfce6a3c2022314116d0b19d1a901e6: the reviewer's mutants R1 (`set hass` resets `_folds`) and R2 (the focus lookup by `[data-fold="${key}"]`, which lands on the card copy behind the open dialog) survived `tests/card.mjs`. Production code is unchanged in this round; two checks now kill them, and the class sweep below pins or reworded every other claimed behaviour.

## Claim sweep

Every behaviour this body claims, against the check that pins it (all in `tests/card.mjs`'s R10-CARD-COLLAPSE block unless a lane is named) and the mutant that check kills:

| claim | pinning check | mutant killed |
|---|---|---|
| both folds collapsed by default, native button with `aria-expanded` | `collapse: both folds render a header button, collapsed by default` | M1 |
| body unrendered while folded | `collapse: a folded section renders no body` | M1 |
| narrative summary is the kWh and cost total, visible while folded | `collapse: the narrative summary is the rows' kWh and cost total, visible while folded` | M7 |
| why-now summary is the strongest driver | `collapse: the why-now summary is its strongest driver, visible while folded` | reviewer's R4 |
| unpaired lines summarise as the first line; no why_now as no data | `collapse: unpaired lines summarise as the first line; no why_now as the no-data line` | — (value check on the fallback branch) |
| a click opens only its own fold; a second click folds it | `collapse: a click opens its own fold and only that one`, `collapse: a second click folds it again` | M2 |
| the toggle does not open the dialog | `collapse: the toggle does not reach the card's open-on-click` | M5 |
| focus returns to the rebuilt header | `collapse: focus returns to the rebuilt header` | M4 |
| focus returns to the dialog's copy when that copy was pressed | **new** `collapse: focus returns to the dialog's copy of the pressed header` | R2 |
| fold state survives a hass-driven rebuild | **new** `collapse: a hass refresh rebuilds the card and keeps each fold as it was` | R1 |
| no `id`/`aria-controls` in the doubly rendered headline | **new** `collapse: the doubly rendered headline mints no id and no aria-controls` | M11 |
| chips and dashed-line notes only in the dialog | `collapse: the folded card renders no series chip and no legend`, `collapse: the expanded dialog carries the chips and the legend` | M3 |
| the folded card keeps what the dialog's chips last saved | **new** `collapse: the folded card keeps the visibility the dialog's chips last saved` | M10 |
| strings in en, sv and de; headers speak the card language | `collapse: every fold string has its twin in en, sv and de`, `collapse: the headers speak the card language` | M7 |
| fold summaries wrap rather than ellipsise | **new** `collapse: the fold summary wraps and never ellipsises` | M9 |
| a divider under the last fold | **new** `collapse: a rule under the last fold closes the headline off from the chart` | M8 |
| ordering: savings, folds, chart | **new** `collapse: the folds sit after the savings figure and before the chart` | M12 |
| clamped axis label's neighbour keeps half the usual gap | `the ... time axis spaces a clamped label at least half its usual gap` | M6 |
| Enter, Tab and Space work in a real browser, light and dark | `tests/card_browser.mjs` `cardCollapse` | not re-run this round (no scope selects the lane; CI's `tests / browser` runs it) |
| `translations/*.json` unchanged | `git diff --quiet a7628041dc02e298c5399003d4c0576391dd5c4e...HEAD -- custom_components/heatpump_optimizer/translations && echo "translations: no change"` printed `translations: no change in three-dot diff` | — (a diff fact) |

Claims reworded rather than pinned: the old "survives every plan-refresh rebuild" now names what the new check drives (a hass-driven rebuild). The old ordering bullet named "header, tiles" and said the order was "kept". The check pins savings, then folds, then chart, so the bullet now states that order only. The old wrap bullet attributed the refusal to the P9 grid's clip rule. That rule measures clipping by an ancestor, not ellipsis itself (`unreachable()` in `tests/card_browser.mjs`), so the attribution is withdrawn and the stylesheet check carries the claim.

## Mutation proof

Each mutant edits the card at this head, then `PYTHONPATH=tests/hastub node tests/card.mjs` runs and the file is restored with `git checkout`. M1-M7 were measured at d7c39135839ea0a985796105ebfda170cdd6d505 and re-created by the round-1 reviewer at b55fc8eb5bfce6a3c2022314116d0b19d1a901e6, all killed. This round changes no production line.
- M1, folds open by default (`_folds` initialised true): `collapse: both folds render a header button, collapsed by default`, `collapse: a folded section renders no body`, `collapse: a click opens its own fold and only that one`, `collapse: the why-now fold opens to its rows`, `collapse: a second click folds it again`.
- M2, the toggle is a no-op (the `this._folds = {...}` line deleted): `collapse: a click opens its own fold and only that one`, `collapse: the why-now fold opens to its rows`, plus every narrative and why-now content check that opens its fold through the header.
- M3, the inline legend restored in the card: `collapse: the folded card renders no series chip and no legend` and five legend checks.
- M4, no focus return (the `again.focus()` line deleted): `collapse: focus returns to the rebuilt header`.
- M5, no `stopPropagation` in the fold click: `collapse: the toggle does not reach the card's open-on-click`.
- M6, the axis threshold back to `minLabelGap` beside a clamp: the five `time axis spaces a clamped label at least half its usual gap` checks.
- M7, no total summary (`const summary = false`): `collapse: the narrative summary is the rows' kWh and cost total, visible while folded`, `collapse: the headers speak the card language`.

Round 1, measured at e277484c38bf3349ab534340c6880274bf404d69 (R1, R2 and NULL re-run there; M8-M12 at its parent, whose card file is identical):
- NULL, a comment edit beside the fold handler: 0 FAIL, rc 0.
- R1, `this._folds = { narrative: false, whynow: false };` added to `set hass`: 1 FAIL, `collapse: a hass refresh rebuilds the card and keeps each fold as it was`.
- R2, `const again = this.shadowRoot.querySelector(`[data-fold="${key}"]`);` replacing the index lookup: 1 FAIL, `collapse: focus returns to the dialog's copy of the pressed header`.
- M8, the `.hl-fold:last-child` border rule deleted: 1 FAIL, `collapse: a rule under the last fold closes the headline off from the chart`.
- M9, `.hl-fold-sum`'s `overflow-wrap: anywhere` replaced by `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`: 1 FAIL, `collapse: the fold summary wraps and never ellipsises`.
- M10, the chart's `visible: !hidden[def.key]` replaced by `visible: true`: 6 FAIL, among them `collapse: the folded card keeps the visibility the dialog's chips last saved`.
- M11, `id="hl-fold-head"` added to the fold header: 2 FAIL, `collapse: both folds render a header button, collapsed by default`, `collapse: the doubly rendered headline mints no id and no aria-controls`.
- M12, the `hl-stats` block moved after the why-now fold in `headlineHtml`: 1 FAIL, `collapse: the folds sit after the savings figure and before the chart`.

## Null control

There is no finder harness, because the group is an owner request, not an audit finding. The before and after is this branch's `tests/card.mjs` block, run at both ends.

At the merge base the base renders no `[data-fold]` element, so the block fails its default-state checks and throws at the first header click. M3 is the chip arm's control, M6 the axis check's. On the unpaid rule, a clamp's neighbour sits under half the typical gap at five of the six horizon and size pairs, so the axis check does not pass vacuously. Its sibling `the ... chart really does clamp a label to the plot edge` stays green at this head.

Each new check asserts its own precondition, so it cannot pass on an empty read:
- The hass-refresh check requires the new savings figure (98.76) present and the old one (12.34) gone, so the card did rebuild.
- The dialog-focus check requires 4 fold heads before and after the press.
- The id check requires 4 fold heads in the dump it scans.
- The order check requires every index found (`>= 0` for the savings figure and the chart's `chartwrap`).
- The chip check reads the starting visibility rather than assuming it, and requires the chip to flip it.

## Figures

- `PYTHONPATH=tests/hastub node tests/card.mjs` at e277484c38bf3349ab534340c6880274bf404d69: `ALL CARD CHECKS PASSED`, rc 0.
- `python3 tests/closure.py select --diff a7628041dc02e298c5399003d4c0576391dd5c4e --workdir "$D"`: `MODE: SCOPED`. Each script in `scope.run` exits 0 with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`, `tests/card_drift.mjs` among them. So do the `run_always` lines `python3 tests/env_drift.py --claims-only origin/main` (`claims hygiene: origin/main ok`) and `python3 tests/closure.py selftest`. This was run at the round's first test commit; the second commit adds checks to `tests/card.mjs` only, re-run above.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff a7628041dc02e298c5399003d4c0576391dd5c4e`: `Architecture score: dS +0.0000 NULL`. An earlier head read `card_clone_copies` 103 -> 108. That was paid by merging the narrative summary into `narrativeParts`, adding one `weightOf` helper, and passing one `{score, narrative, whynow}` disclosure argument to `headlineHtml`.
- `git diff --quiet a7628041dc02e298c5399003d4c0576391dd5c4e...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json && echo untouched`: printed.
- `tests/card_browser.mjs` (exit 0, no `FAIL` line, `cardCollapse` and the P9 grid's `folds_open` cell included) and the regenerated `docs/img/card` figures were measured at d7c39135839ea0a985796105ebfda170cdd6d505. This round touches only `tests/card.mjs`, and CI's `tests / browser` re-runs the lane.

## Red checks

none

## Forward-carry

none

## Friction

none
