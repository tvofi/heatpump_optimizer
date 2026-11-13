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

`0e60a6f9a681992f4f983ee79dce2fa2d980c4d5` (fix/r10-card-collapse, the pull request's head ref). It is `b09b5f9c611cba86c63ce4eedeb57c96e9bde984`, this seat's merge of origin/main `4145f2852642fd0b5ccb8b7af60d41e896a5eea3` into the previous head `eda078bac41473246ff7d87a5736de58d64ad97a`, then merged into the PR branch (`a72f090b5b`) and a merge of origin/main `f44e761c19dc07fff222bbd6a323bdc847ea9f04` (the v7.1.13 stamp, `claims-for: 7.1.13` carried by that merge). This seat fast-forwarded to it and wrote no commit of its own beyond `b09b5f9c611cba86c63ce4eedeb57c96e9bde984`. Merge base `f44e761c19dc07fff222bbd6a323bdc847ea9f04`; origin/main's tip at measurement was `f47250150a` (a record-only merge after the stamp); `git merge-tree --write-tree origin/main 0e60a6f9a681992f4f983ee79dce2fa2d980c4d5` exits 0. Measured 2026-11-13 00:17 UTC.

## Merge repair (round 5, `tests/card_browser.mjs`)

`git merge 4145f2852642fd0b5ccb8b7af60d41e896a5eea3` into `eda078bac41473246ff7d87a5736de58d64ad97a` conflicted in `tests/card_browser.mjs` only: this branch added `cardCollapse` and its call, main added `themeLiveSwitch` (R10 live theme switch) and its call, at the same place. Resolution by union: both functions kept whole, one after the other, and both calls kept, `themeLiveSwitch` first. No other line was written by hand.

Read-back of both sides' clauses:
- Branch side: the added and removed lines of `git diff 4145f2852642fd0b5ccb8b7af60d41e896a5eea3 b09b5f9c611cba86c63ce4eedeb57c96e9bde984 -- tests/card_browser.mjs` equal, as sorted sets, those of the branch's own `git diff cbe8d93bd8ef9b59626cfb939436af6e0678680e eda078bac41473246ff7d87a5736de58d64ad97a -- tests/card_browser.mjs` (124 lines each; `cmp` exit 0).
- Main side: the added and removed lines of `git diff eda078bac41473246ff7d87a5736de58d64ad97a b09b5f9c611cba86c63ce4eedeb57c96e9bde984 -- tests/card_browser.mjs` equal, as sorted sets, main's own `git diff cbe8d93bd8ef9b59626cfb939436af6e0678680e 4145f2852642fd0b5ccb8b7af60d41e896a5eea3 -- tests/card_browser.mjs` (181 lines each; `cmp` exit 0).
- Null control: one extra line appended to the merged set makes `cmp -s` exit non-zero.
- Lane: `PYTHONPATH=tests/hastub node tests/card_browser.mjs` at `0e60a6f9a681992f4f983ee79dce2fa2d980c4d5` prints `ALL BROWSER CHECKS PASSED`, rc 0, with both sides' checks among them: 10 `ok` lines containing `collapse` and 7 starting `R10 live` (the six `R10 live light to dark` / `dark to light` checks and `R10 live switch starts on the light default theme with the Health dialog open`).

## Merge repair (round 4, v7.1.12 stamp)

`git merge-tree --write-tree origin/main 089bd3aa5ba3c2d12c49dcb4cfee369b29bc8d44` (claimnotes driver installed: `python3 tests/env_drift.py --install-merge-driver` printed `MERGE-CLAIM: already-installed`) reported two conflicts. Each resolution is listed below; no other line was written by hand.

- `tests/golden/card_claimed_drift.txt`: the driver refused `CONFLICTING CLAIMS` (base 7.1.11, main 7.1.12, branch 7.1.11). The v7.1.12 stamp emptied the claims. Resolution: main's stamped file verbatim (`claims-for: 7.1.12`), with this branch's R10-CARD-COLLAPSE block appended unchanged. The block is the hunk `git diff 0b276e8c0cd4ddbcf5c5e0adfe179af00441e7f3...089bd3aa5ba3c2d12c49dcb4cfee369b29bc8d44 -- tests/golden/card_claimed_drift.txt` adds, a blank line plus 52 non-empty lines. Read-back: `git diff origin/main HEAD -- tests/golden/card_claimed_drift.txt` adds 52 non-empty lines and removes 0. Its added and removed lines equal, as sorted sets, those of the branch's own three-dot diff. The claim set was re-derived at the merged tree rather than copied: after `tests/plan_view.py`, `node tests/card_drift.mjs origin/main` prints `card_drift: 44 state(s) moved and claimed, 1 identical`, rc 0. Null control: with the file restored to `git show origin/main:tests/golden/card_claimed_drift.txt`, the same command exits rc 1. No value-bearing fixture was recorded, and `VERSION` is untouched.
- `docs/index.html`: main rewrote the product page (R10 product page, `32fa499a7a`..`fcc7f07e67`). This branch's only change to the file is one sentence of the card lead (`#card`, `data-src="README.md#dashboard-card"`). Resolution: main's file verbatim, with that one sentence re-applied. Read-back: the added and removed lines of `git diff origin/main HEAD -- docs/index.html` equal, in order, those of `git diff 0b276e8c0cd4ddbcf5c5e0adfe179af00441e7f3 089bd3aa5ba3c2d12c49dcb4cfee369b29bc8d44 -- docs/index.html`, one removed line and one added.
- `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` auto-merged. Read-back: the added and removed lines of `git diff origin/main HEAD` equal, as sorted sets, the branch's own `git diff 0b276e8c0c 089bd3aa5b` for that file. So main's card change is kept, and nothing new was written.
- `tests/closures.json`: `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` re-recorded `tests/entities.py`'s `rc` from 1 to 0, and changed nothing else. It kept `tools/pr/figure_registry.json`, which it reported it would have dropped.

Steps 2-8 were re-run at round 4's head `30f1b6c8fe007b8d4400ba262e51fecd10afb4d2`, giving the round-4 mutants under `## Mutation proof` and the `## Figures` below. Earlier rounds: round 1 (pin-missing, below); round 2 merged origin/main without conflict; round 3 was a merge repair of `card_claimed_drift.txt` and `tests/card_browser.mjs` at `8c45afd38f2378350bd2e532b68da28e7f682f0e`.

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
| Enter, Tab and Space work in a real browser, light and dark | `tests/card_browser.mjs` `cardCollapse` | re-run in round 5: `ALL BROWSER CHECKS PASSED`, 10 `collapse` checks `ok` |
| `translations/*.json` unchanged | `git diff --quiet ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e...HEAD -- custom_components/heatpump_optimizer/translations && echo "translations: no change"` printed `translations: no change in three-dot diff` | — (a diff fact) |

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

Round 2, re-run at 82e14f6d8fb87fc65dd993d1cadbd35883090f07 after the merge (`PYTHONPATH=tests/hastub node tests/card.mjs`, file restored by `git checkout` after each):
- NULL, ` // null` appended to the fold handler's focus line: 0 FAIL, rc 0.
- R1, the `_folds` reset added to the card's `set hass`: rc 1, `collapse: a hass refresh rebuilds the card and keeps each fold as it was`.
- M4, the fold handler's `again.focus()` line deleted: rc 1, `collapse: focus returns to the rebuilt header`, `collapse: focus returns to the dialog's copy of the pressed header`.
- M2, the `this._folds = {...}` toggle line deleted: rc 1, 21 failing checks, the first `headline shows every narrative line`.

Round 4, re-run at 30f1b6c8fe007b8d4400ba262e51fecd10afb4d2 after the v7.1.12 merge (`PYTHONPATH=tests/hastub node tests/card.mjs`, card file restored by `git checkout` after each):
- NULL, ` // null` appended to the fold handler's `again.focus()` line: rc 0, 0 failing checks.
- R1, `this._folds = { narrative: false, whynow: false };` added to the card's `set hass`: rc 1, 1 failing check, `collapse: a hass refresh rebuilds the card and keeps each fold as it was`.
- M4, the fold handler's `again.focus()` line deleted: rc 1, `collapse: focus returns to the rebuilt header`, `collapse: focus returns to the dialog's copy of the pressed header`.
- M2, the `this._folds = {...}` toggle line deleted: rc 1, 21 failing checks, the first `headline shows every narrative line`.

Round 5, re-run at 0e60a6f9a681992f4f983ee79dce2fa2d980c4d5 (`python3 tests/plan_view.py`, then `PYTHONPATH=tests/hastub node tests/card.mjs`, card file restored by `git checkout` after each):
- Unmutated: rc 0, `ALL CARD CHECKS PASSED`.
- NULL, ` // null` appended to the fold handler's `again.focus()` line: rc 0, `ALL CARD CHECKS PASSED`.
- R1, `this._folds = { narrative: false, whynow: false };` added to the card's `set hass`: rc 1, `1 CARD CHECK(S) FAILED`, `collapse: a hass refresh rebuilds the card and keeps each fold as it was`.
- M4, the fold handler's `again.focus()` line deleted: rc 1, `2 CARD CHECK(S) FAILED`, `collapse: focus returns to the rebuilt header`, `collapse: focus returns to the dialog's copy of the pressed header`.
- M2, the `this._folds = {...}` toggle line deleted: rc 1, `21 CARD CHECK(S) FAILED`, the first `headline shows every narrative line`.

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

All at `0e60a6f9a681992f4f983ee79dce2fa2d980c4d5`, merge base f44e761c19dc07fff222bbd6a323bdc847ea9f04, 2026-11-13 00:17 UTC, Python 3.14.7, `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`; each line is the script's last output line.
- `python3 tests/closure.py select --diff f44e761c19dc07fff222bbd6a323bdc847ea9f04 --workdir "$D"`: `MODE: SCOPED -- 12 script(s) run, 21 scoped out.` Every script in `scope.run` exits 0: `tests/arch_score_head.py` `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`, `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`, `tests/doc_claims.py` `ALL 343 checks PASSED`, `env -u BASH_ENV python3 tests/entities.py` `ALL 2709 ENTITY CHECKS PASSED`, `tests/env_drift.py` `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`, `tests/features.py` `ALL 5362 FEATURE CHECKS PASSED`, `tests/golden.py` `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, `tests/harness_headers.py` `ALL 115 HARNESS HEADER CHECKS PASSED`, `tests/md_tables.mjs` `RESULT doc_misrendered_lines=0 count`, `tests/plan_view.py` `plan reason codes, price provenance and slot energy OK`, `tests/card.mjs` `ALL CARD CHECKS PASSED`, `tests/card_drift.mjs origin/main` `card_drift: 44 state(s) moved and claimed, 1 identical`.
- The `run_always` lines: `python3 tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`; `python3 tests/closure.py selftest` printed `ALL 118 closure shrink pins PASSED`; `python3 tests/layout.py` printed `layout self-test: ok`.
- `python3 tests/env_drift.py --all`: `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff f44e761c19dc07fff222bbd6a323bdc847ea9f04`: `Architecture score: dS +0.0000 NULL`.
- `tests/card_browser.mjs`: `ALL BROWSER CHECKS PASSED`, rc 0 (see the round-5 read-back).
- `VERSION` and `card_claimed_drift.txt`'s `claims-for:` both read `7.1.13`, as does origin/main's `VERSION`.

## Red checks

- `tests / fast (3.14)`: main's red, not this branch's. The failing check is `tests/features.py`'s `combi_type_branch census` (vendor hits in `const.py`, `heat_curve.py`, `pump_arbiter.py`, `thermal_model.py`). Control: the same `PYTHONPATH=tests/hastub GOLDEN_MODE=drift python3 tests/features.py` at origin/main ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e prints the identical FAIL line and `1 of 5237 FEATURE CHECKS FAILED`, rc 1; `git diff --name-only ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e...HEAD -- '*.py' | grep custom_components` prints nothing, so this branch touches no file the census reads. Cheaper detector for this PR: none exists, because the branch did not cause the defect; the cause, its process state and countermeasure are owned by #3466 (the repair, on the merge train). Carry: #3466 At this head the same command passes (`ALL 5294 FEATURE CHECKS PASSED`): #3466's repair is on main d72963a719438f2dcf370de92a71f6630804ff2e.

## Forward-carry

none

## Friction

none

