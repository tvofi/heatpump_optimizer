R9-UX-6, money and memory (the Savings tab), per DESIGN-UX.md section UX-6 and PRE-STUDY-UX.md item 3.

**Stacked base, not for opening yet.** This branch is cut from `handoff/r9-eg-entry-config` at `d15fc0ae57da63645d6b8d4381ffe83db3a831de` (R9-EG-B11, PR #2025, approved, not merged), on the owner's decision to start stacked. Every figure below is measured against that base, not `origin/main`. After #2025 merges, `origin/main` is merged into this head (never a rebase), and steps 2 to 8 of `fixer.md` are re-run at the new merge base. That includes this body. R9-UX-5 (#2010), the third after-edge, has not merged either. Its diff does not touch the Savings tab, `ledger.py`, `accuracy.py` or `MonthlySavingsSensor`.

What changes:

1. **Defect, failing test first.** A receipt's `total_sek` added every line except the reasons. That counted spot again under `space` and `dhw`, which split it, and under `savings_baseline` and `savings_actual`, which compare it. The fixture month cost 194.5, and the receipt published 709.5. The total now adds `ledger.BILLED_LINES` (spot, grid fee, capacity, immersion, wear) and nothing else. It names them in the receipt's new `basis` list. A receipt stored with the old sum is restated from its own lines on load (`ledger.restate_total`), because the lines were always right.
2. **The freeze moves into `ledger.py`.** `freeze_month_report` and `roll_receipts` are pure functions there. The coordinator keeps `_roll_month` and `_freeze_month_report` as thin callers, so `seam_map.json` needs no change.
3. **The capacity charge is booked.** `MonthlyLedger.book_capacity` restates the month's `capacity` line every settlement as billed peak times price, and keeps the billed peak in the month's meta. The tracker wipes its peaks at month change, and the line keeps the last statement made before that. The receipt carries `capacity_peak_kw`.
4. **Every receipt kept (24) is published.** It is the `receipts` attribute on the enabled monthly-savings sensor, unrecorded (`_unrecorded_attributes`), because 24 receipts exceed the recorder's 16 KB attribute limit.
5. **The day-ahead promise (U2).** `AccuracyTracker.note_promise` keeps the first plan solved in the local midnight hour as the day's promise. That is the room trajectory and the cumulative cost over 24 h, two days kept, persisted with the accuracy history. A plan solved after that hour is not a promise. `AccuracyTracker.replay` pairs yesterday's promise with the measured samples. The result is published unrecorded as `plan_replay` on the same sensor.
6. **The Savings tab** shows the latest receipt: total, saving against a thermostat, billed lines with their basis, unpriced wear as "not priced", and the covers note. Beside it, "Where the money went" shows one-hue bars by reason. Below, "Yesterday: the plan against reality" draws the promise dashed and the measurement solid on a shared time axis, in the house and price colours of record (`--hpo-series-house_temp`, `--hpo-series-price`). The monthly table and its estimate badge are unchanged below. The page's styles ship with the page, so no other card state moves.
7. The `_learning_view` comment no longer describes the #110 heat-loss defect, which is fixed.

Part of #201. Requested by **tvofi**.

## Head

`e90e57891ef903476d83f72189eab093abb4d9a1`, measured against the stacked base `d15fc0ae57da63645d6b8d4381ffe83db3a831de` (three-dot), 2026-10-07T20:46Z.

## Mutation proof

The UX-6 checks are a block at the end of `tests/features.py`. `features.py` is a heavy script, so it was not run locally. Locally, the identical block ran under a standalone runner: the features prelude, then the block, the same `R.check` calls. The runner is in seat scratch, and landing it as a harness is owed (see below). Each mutant was applied to the head and then restored:

- M0, the head unmodified: `ALL 19 UX-6 BLOCK PASSED`.
- M1, `billed_total` adds every line (the defect restored): 5 fail. These include "a receipt's total is the money the month cost" (709.5), "the store admits the receipt's basis", and "a receipt stored with the old total loads with the billed total".
- M2, `_roll_month`'s `book_capacity` disabled: 3 fail. These include "the capacity line is the billed peak times the tariff" and "March's receipt names the capacity charge after the tracker reset".
- M3, the promise-hour guard removed: 2 fail ("a plan solved after the midnight hour is not the day's promise", "the next day replays the promise").
- M4, `restate_total` dropped from `_async_load_ledger`: 1 fails ("a receipt stored with the old total loads with the billed total"). M4 survived the first test set, and the load-path check was added for it in `26888b75`.
- Card: `receiptHtml`'s `basis` replaced by every key of `lines`: `tests/card.mjs` fails 2 ("the receipt shows the backend's total and the lines it adds", "the note names what the total covers").

`features.py` itself and the mutation lane are CI's. No CI run exists at this head, because nothing was pushed as a PR.

## Null control

- At the base, the defect check fails with `total_sek=709.5`. Its null control, a month with only billed lines, passes at both base and head (194.5 either way). So the check moves only on the double count. Base log: the runner output at `d15fc0ae` with block 1, `1 of 2 UX-6 BLOCK FAILED`.
- No capacity tariff means no `capacity` line ("UX-6 null control: without a capacity tariff no capacity line is booked").
- On the promise's own day there is no yesterday to replay (returns None).
- The store probe refuses a receipt whose `basis` names `space`, a line it does not bill. Under `_TEXT` it would have been admitted.
- Card drift: with the styles in the shared style block, `card_drift.mjs` against the base reported 39 of 40 states drifted. With them scoped to the page, it reports `identical in all 40 states`.

## Figures

- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `max_class_loc` gains (lower) and is not yet recorded. It is recorded after the main merge, at the real merge base, so as not to carry a number from the stacked base. A first draft raised `functions_cc_over_25` by 1 (`AccuracyTracker.from_dict`). That was paid by moving the promise loader into `_stored_promises`, not by a raise.
- `node tests/card.mjs`: `ALL CARD CHECKS PASSED` (needs `PYTHONPATH=tests/hastub python3 tests/plan_view.py` first).
- `node tests/card_drift.mjs d15fc0ae57da63645d6b8d4381ffe83db3a831de`: `identical in all 40 states`.
- `PYTHONPATH=tests/hastub python3 tests/typing_ruler.py`: `ALL 11 typing-ruler source checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 160 checks PASSED`.
- `node tests/md_tables.mjs`: `doc_misrendered_lines=0`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: 13 of 109 fail, all `dev/audit/rounds/round4/D6/claims.py`. That file is a SyntaxError on the local Python 3.11.5 (a 3.12 f-string), and it fails identically at the base. Environment, not this diff. CI's interpreter is newer.
- `python3 tests/closure.py select --diff d15fc0ae57da63645d6b8d4381ffe83db3a831de`: `MODE: SCOPED -- 27 script(s) run, 5 scoped out`. The heavy ones (`features.py`, `golden.py`, `stress.py`, `boost_drift_replay.py`, `entities.py`) are left to CI.
- `python3 tools/pr/ci_predict.py --base d15fc0ae57da63645d6b8d4381ffe83db3a831de` (taken from `origin/fix/r9-ro-11-pr`): 1 predicted closures red and 39 added unpinned sites (below).

## Red checks

Predicted, not yet observed: `closures` UNDER-SCOPED. `store.py` now imports `ledger.py` (`BILLED_LINES`, the receipt basis domain), and `tests/guard_pins.py`'s closure omits `ledger.py`. That is `closures-autofix`'s repair by `ci-autofix.md`. The cheaper detector is `ci_predict.py`, which named it before any push.

## Forward-carry

none. U3, the household power budget, stays deferred. R9-UX-7, the sibling with no edge, edits `sensor.py` and the card in different functions. Whichever merges second merges main, as the roster already says.

## Unpinned sites

39 added sites, as `ci_predict.py` lists them (`accuracy.py` 24, `ledger.py` 13, `coordinator.py` 1, and the rest). The sites M1 to M4 hit are killed above. The rest are left to `mutation-autofix` after the first CI run, and survivors get a value check or a written triage then. Not claimed killed here.

## Owed after #2025 merges

- Merge `origin/main` (never rebase). Re-run steps 2 to 8 at the new merge base, then re-take this body.
- Claim the coordinator captures, add-only, in `tests/golden/claimed_drift.txt`: `coord_*` gain `receipts` and `plan_replay` in the published payload and on `sensors.monthly_savings`. No plan, schedule or solver leaf moves. This is deferred because the claim file's contents and `claims-for:` depend on main at the merge.
- Re-record `max_class_loc` at the merge base, with the reason in the commit message.
- Regenerate the Savings screenshots, light and dark, with the browser test's page-screenshot mode, into `docs/img/card/`. Update the `<picture>` alt text and the product page's gallery slot (DESIGN-SITE.md). The fixture behind the page-screenshot mode needs `receipts` and `plan_replay` for the new sections to appear.
- Land the standalone block runner as a harness (`tools/audit/harnesses/`, which exists on main and not on this base) and classify it.

## Friction

none
