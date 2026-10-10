R9-UX-6, money and memory (the Savings tab), per DESIGN-UX.md section UX-6 and PRE-STUDY-UX.md item 3. Part of #201. Requested by **tvofi**.

This recovers the orphaned `handoff/r9-ux-6` — the work existed but no PR was ever opened for it — onto current `origin/main` (`7cd5a588c`), re-deriving the tree-dependent figures at the merged head (each in `## Figures`). Two edges of the roster's `after` list have merged since the handoff was cut: #2025 (`R9-EG-B11`, the stacked base it was cut from) and #2010 (`R9-UX-5`, its third after-edge). Nothing this branch adds is on `main` in another shape: `restate_total`, `BILLED_LINES`, `book_capacity`, `note_promise`, `plan_replay`, `capacity_peak_kw` and `receiptHtml` are absent from `main` (`git grep` over `custom_components`, `tests`, `docs`), and `dev/programme/carries/carry-1795.json` carries the sibling UX sub-lanes only.

What changes:

1. **Defect, failing test first.** A receipt's `total_sek` added every line except the reasons, so it counted spot again under `space` and `dhw`, which split it, and under `savings_baseline` and `savings_actual`, which compare it. The fixture month cost 194.5, and the receipt published 709.5. The total now adds `ledger.BILLED_LINES` (spot, grid fee, capacity, immersion, wear) and nothing else, and names them in the receipt's new `basis` list. A receipt stored with the old sum is restated from its own lines on load (`ledger.restate_total`), because the lines were always right.
2. **The freeze moves into `ledger.py`.** `freeze_month_report` and `roll_receipts` are pure functions there. The coordinator keeps `_roll_month` and `_freeze_month_report` as thin callers, so `seam_map.json` needs no change.
3. **The capacity charge is booked.** `MonthlyLedger.book_capacity` restates the month's `capacity` line every settlement as billed peak times price, and keeps the billed peak in the month's meta. The tracker wipes its peaks at month change, and the line keeps the last statement made before that. The receipt carries `capacity_peak_kw`.
4. **Every receipt kept (24) is published.** It is the `receipts` attribute on the enabled monthly-savings sensor, unrecorded (`_unrecorded_attributes`), because 24 receipts exceed the recorder's 16 KB attribute limit.
5. **The day-ahead promise (U2).** `AccuracyTracker.note_promise` keeps the first plan solved in the local midnight hour as the day's promise: the room trajectory and the cumulative cost over 24 h, two days kept, persisted with the accuracy history. A plan solved after that hour is not a promise. `AccuracyTracker.replay` pairs yesterday's promise with the measured samples, and the result is published unrecorded as `plan_replay` on the same sensor.
6. **The Savings tab** shows the latest receipt: total, saving against a thermostat, billed lines with their basis, unpriced wear as "not priced", and the covers note. Beside it, "Where the money went" shows one-hue bars by reason. Below, "Yesterday: the plan against reality" draws the promise dashed and the measurement solid on a shared time axis, in the house and price colours of record (`--hpo-series-house_temp`, `--hpo-series-price`). The monthly table and its estimate badge are unchanged below. The page's styles ship with the page, so no other card state moves.
7. The `_learning_view` comment no longer describes the #110 heat-loss defect, which is fixed.

## Head

`10b4ae172271e090a8a10810a5f0622f1d07f0ca`, measured against `origin/main` `7cd5a588c` (three-dot), 2026-10-10. The three commits above the recovered handoff are the two `origin/main` merges (conflicts resolved by keeping both sides: `AccuracyTracker` gains both `promises` and `draw`; `store.py`'s `_ACCURACY` keeps both key sets; `tests/features.py` keeps the R9-UX-6 block and main's appended blocks) and the re-recorded `coord_*` captures.

## Mutation proof

The UX-6 checks are a block at the end of `tests/features.py`, run alone with the in-tree block runner `tools/audit/seat/features_block.py` (landed on `main` since the handoff). Each mutant was applied to the head and then restored:

- M0, the head unmodified: `ALL 19 FEATURES BLOCK PASSED`.
- M1, `billed_total` adds every line (the defect restored): 5 fail. These are "a receipt's total is the money the month cost, not its splits again" (709.5), "ledger.freeze_month_report totals the billed lines and names them", "a receipt frozen by the old sum is restated from its own lines on load", "the store admits the receipt's basis and refuses a line it does not bill", and "a receipt stored with the old total loads with the billed total".
- M2, `_roll_month`'s `book_capacity` disabled: 3 fail ("the capacity line is the billed peak times the tariff while the month is open", "March's receipt names the capacity charge after the tracker reset", "the grid view publishes every receipt kept, oldest first").
- M3, the promise-hour guard removed: 2 fail ("a plan solved after the midnight hour is not the day's promise", "the next day replays the promise against the 24 h it covered").
- M4, `restate_total` dropped from `_async_load_ledger`: 1 fails ("a receipt stored with the old total loads with the billed total").

`features.py` itself and the mutation lane are CI's. The five `coord_*` sites the block does not reach are dispositions of `## Unpinned sites`.

## Null control

- At the base, the defect check fails with `total_sek=709.5`; its null control, a month with only billed lines, passes at both base and head (194.5 either way), so the check moves only on the double count.
- No capacity tariff means no `capacity` line ("UX-6 null control: without a capacity tariff no capacity line is booked").
- On the promise's own day there is no yesterday to replay (returns None).
- The store probe refuses a receipt whose `basis` names `space`, a line it does not bill; under `_TEXT` it would have been admitted.
- Card drift: with the styles in the shared style block, `card_drift.mjs` against the base reported 39 of 40 states drifted. Scoped to the page, it reports `identical in all 40 states` — the null control for the style scoping.
- Golden: `env_drift.py --all origin/main` reports `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over all 56 scenarios; the five `coord_*` moves it judges are the added `receipts`/`plan_replay` keys, empty list and null. Recording the same capture locally moves 90 pre-existing float leaves (battery and DHW-profile values), which a dev box may not commit; it was not committed.

## Figures

`python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`; `max_class_loc=8745 <= 8745`, `functions_cc_over_25=8`, `max_cc=45`. `main` caps `max_class_loc` at 8818, so the freeze's move out of the coordinator class is a payment of 73, recorded by `ledger_merge`'s both-deltas resolution and confirmed by this run; no cap is raised.

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` — `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.

`python3 tools/audit/seat/features_block.py '# R9-UX-6: money and memory -- the receipt, the capacity line, the replay' '# -- live power clamp, 7a: the metered running draw (draw_range) ------------'` — `ALL 19 FEATURES BLOCK PASSED`.

`node tests/card.mjs` — `ALL CARD CHECKS PASSED`.

`node tests/card_drift.mjs origin/main` — `card_drift: identical in all 40 states`.

`python3 tests/env_drift.py --all origin/main` — `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`; `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.

`python3 tests/env_drift.py --claims-only origin/main` — `claims hygiene: origin/main ok`.

`python3 tests/finite_boundary.py` — `ALL 84 FINITE BOUNDARY CHECKS PASSED` (the handoff recorded 83; the count grew with main's own additions).

`python3 tests/deployment_shape.py` — `ALL DEPLOYMENT SHAPE CHECKS PASSED`.

`python3 tests/doc_claims.py` — `ALL 160 checks PASSED`.

`python3 tests/typing_ruler.py` — `ALL 11 typing-ruler source checks PASSED`.

`python3 tests/harness_headers.py` — `ALL 109 HARNESS HEADER CHECKS PASSED` (a first run on a box at load average ~106 failed 12 on one D7 audit harness; see `## Red checks`).

`python3 tests/features.py` at the clean `origin/main` worktree `7cd5a588c` — `1 of 3986 FEATURE CHECKS FAILED`, the `R9-F2.1 P3` BLAS margin; see `## Red checks`.

`python3 tests/guard_pins.py` — `ALL 50 GUARD PIN CHECKS PASSED`.

`python3 tests/arch_score_head.py` — `ALL 15 ARCHITECTURE SCORE HEAD CHECKS PASSED`.

`python3 tests/arch_score.py --smoke` — `ALL 257 ARCHITECTURE SCORE CHECKS PASSED`.

`node tests/md_tables.mjs` — `doc_misrendered_lines=0`.

`python3 dev/audit/rounds/round4/D6/claims.py` — `arch_modules_on_disk=75`, `arch_map_listed=75`, `ha_module_level_importers=27`, `claims_true=123`, `claims_false=0`. The merged tree reads 75 where the handoff's stacked base read 74: main's own `draw_range.py` is the extra module, and `claims.py`'s header already records it.

`python3 tools/pr/ci_predict.py --base origin/main` — `39 unpinned site(s) the diff adds` (`accuracy.py` 25, `ledger.py` 13, `coordinator.py` 1) and `1 predicted red` (`closures` UNDER-SCOPED on `ledger.py`).

## Red checks

- `tests/features.py` fails exactly one check at the merge base: `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it [shipped 110.4366, seeded with the half-price plan 110.1297]` — `1 of 3986 FEATURE CHECKS FAILED`, reproduced on a clean `origin/main` worktree at `7cd5a588c` (`python3 tests/features.py`). It is a BLAS float margin, the known defect group `R9-RC-BLAS-KERNEL-RED`, not this diff; the same script's closure recording is truncated by the recorder's own per-driver timeout on this seat, which is what makes `prepr.sh` step 6b refuse the `features.py` recording. The check is not weakened and `features.py` is left to CI, where the canonical environment runs it.
- The closures refusal, both arms, named. `prepr.sh` step 6d (`ci_predict.py`) predicts `closures` UNDER-SCOPED: `store.py` imports `ledger.py` (`BILLED_LINES`, the receipt basis domain) and `tests/guard_pins.py`'s recorded closure lists `store.py` without `ledger.py` (verified in `tests/closures.json`, not taken from the prediction). `closures-autofix` owns the repair (`ci-autofix.md`: the Linux recordings are the ones to merge; a Darwin `--single` of a recording CI will make is the wrong one). The cheaper detector is `ci_predict.py`, which named it before any push. `prepr.sh` refuses on this prediction, which is the expected pre-push state for a real under-scope.
- `tests/harness_headers.py` failed 12 of 109 on its first run, all one harness — `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`, `rc=124, wall limit 900s exceeded` — on a box at load average ~106. A re-run reports `ALL 109 HARNESS HEADER CHECKS PASSED`, so the failure was the seat's load, not the tree: the cheaper detector for a load-induced timeout is a re-run, and the harness is outside this diff with its header unchanged.

## Forward-carry

none. U3, the household power budget, stays deferred beyond round 9, and U1's notifications and U5's screenshots are the sibling UX lanes' (`carry-1795.json`).

## Unpinned sites

39 sites the diff adds, as `ci_predict.py` lists them (`accuracy.py` 25, `ledger.py` 13, `coordinator.py` 1). `mutation-autofix` pins the ones a driver kills after the push (`ci-autofix.md`); the value checks are the in-tree ones that pin the money-bearing sites, and the rest are a written triage left to that lane, not claimed killed here.

Value check, `tests/features.py`'s UX-6 block (mutants M1–M4 above):

- `custom_components/heatpump_optimizer/ledger.py:320 RETURN_DEL` — `billed_total`'s sum (M1)
- `custom_components/heatpump_optimizer/ledger.py:394 GUARD_OFF` — `freeze_month_report`'s `mean_spot_price` arm (M1)
- `custom_components/heatpump_optimizer/ledger.py:396 RETURN_DEL` — `freeze_month_report`'s return (M1)
- `custom_components/heatpump_optimizer/ledger.py:330 GUARD_OFF` — `restate_total`'s non-dict guard (M1/M4)
- `custom_components/heatpump_optimizer/ledger.py:333 RETURN_DEL` — `restate_total`'s restated return (M1/M4)
- `custom_components/heatpump_optimizer/ledger.py:153 BOOLOP` — `book_capacity`'s refused-input guard (M2)
- `custom_components/heatpump_optimizer/ledger.py:153 GUARD_OFF` — the same guard (M2)
- `custom_components/heatpump_optimizer/coordinator.py:10235 GUARD_OFF` — `_roll_month`'s `book_capacity` arm (M2)
- `custom_components/heatpump_optimizer/accuracy.py:218 GUARD_OFF` — the promise hour (M3)
- `custom_components/heatpump_optimizer/accuracy.py:221 GUARD_OFF` — `replay`'s no-promise arm (M3)
- `custom_components/heatpump_optimizer/accuracy.py:231 GUARD_OFF` — `replay`'s no-cost arm (M3)

Value check, `tests/card.mjs` (the card mutant): `receiptHtml`'s `basis` replaced by every key of `lines` fails 2 card checks ("the receipt shows the backend's total and the lines it adds", "the note names what the total covers").

Written triage, left to `mutation-autofix`:

- `custom_components/heatpump_optimizer/accuracy.py:50 CONST`
- `custom_components/heatpump_optimizer/accuracy.py:51 CONST`
- `custom_components/heatpump_optimizer/accuracy.py:53 CONST`
- `custom_components/heatpump_optimizer/accuracy.py:550 BOOLOP`
- `custom_components/heatpump_optimizer/accuracy.py:550 CMP_BOUND`
- `custom_components/heatpump_optimizer/accuracy.py:550 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:552 CLAMP_DROP`
- `custom_components/heatpump_optimizer/accuracy.py:553 BOOLOP`
- `custom_components/heatpump_optimizer/accuracy.py:553 CMP_BOUND*2`
- `custom_components/heatpump_optimizer/accuracy.py:553 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:557 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:563 BOOLOP`
- `custom_components/heatpump_optimizer/accuracy.py:563 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:584 CMP_BOUND*2`
- `custom_components/heatpump_optimizer/accuracy.py:588 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:599 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:603 RETURN_DEL`
- `custom_components/heatpump_optimizer/accuracy.py:608 GUARD_OFF`
- `custom_components/heatpump_optimizer/accuracy.py:617 BOOLOP`
- `custom_components/heatpump_optimizer/accuracy.py:617 CMP_BOUND`
- `custom_components/heatpump_optimizer/accuracy.py:618 CMP_BOUND`
- `custom_components/heatpump_optimizer/accuracy.py:621 RETURN_DEL`
- `custom_components/heatpump_optimizer/ledger.py:384 CMP_BOUND`
- `custom_components/heatpump_optimizer/ledger.py:385 CMP_BOUND`
- `custom_components/heatpump_optimizer/ledger.py:413 BOOLOP`
- `custom_components/heatpump_optimizer/ledger.py:413 CMP_BOUND`
- `custom_components/heatpump_optimizer/ledger.py:432 CLAMP_DROP`
- `custom_components/heatpump_optimizer/ledger.py:434 RETURN_DEL`

## Friction

none
