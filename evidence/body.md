<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
R9-UX-6, money and memory (the Savings tab), per DESIGN-UX.md section UX-6 and PRE-STUDY-UX.md item 3. Part of #201. Requested by **tvofi**.

This is the repair of the blocked review at `72b696d96700e0509d03e06479464b5f71c95241` (verdict class `root-cause-unanswered`): the fix's substance stands as the reviewer established it. The last handoff was refused at the push (`REFUSE ancestry reds RED UNANSWERED (arch-score closures coverage-ratchet fast (3.14) mutation mutation-autofix nightly-ha (stable))`) because the body did not name `coverage-ratchet`; this body answers every name that arm enumerates, seven, each with the head it stands red at, the check's own output, and its repair or why it does not bind at this head (`## Red checks`). Nothing this branch adds is on `main` in another shape (`restate_total`, `BILLED_LINES`, `book_capacity`, `note_promise`, `plan_replay`, `capacity_peak_kw`, `receiptHtml` each have 0 hits by `git grep <sym> 6be88834e -- custom_components tests docs`, main tip `6be88834e`, 2026-10-10T19:33Z).

What changes (unchanged from the reviewed fix, then the repair):

1. **Defect, failing test first.** A receipt's `total_sek` added every line except the reasons, so it counted spot again under `space` and `dhw`, which split it, and under `savings_baseline` and `savings_actual`, which compare it. The fixture month cost 194.5, and the receipt published 709.5. The total now adds `ledger.BILLED_LINES` (spot, grid fee, capacity, immersion, wear) and nothing else, and names them in the receipt's new `basis` list. A receipt stored with the old sum is restated from its own lines on load (`ledger.restate_total`), because the lines were always right.
2. **The freeze moves into `ledger.py`.** `freeze_month_report` and `roll_receipts` are pure functions there — and since this repair, `roll_receipts` actually is: it **returns** the receipts to keep and whether a month closed, instead of writing into the coordinator's `_month_reports` from a collaborator module. The coordinator keeps `_roll_month` and `_freeze_month_report` as thin callers.
3. **The capacity charge is booked.** `MonthlyLedger.book_capacity` restates the month's `capacity` line every settlement as billed peak times price, and keeps the billed peak in the month's meta. The tracker wipes its peaks at month change, and the line keeps the last statement made before that. The receipt carries `capacity_peak_kw`.
4. **Every receipt kept (24) is published.** It is the `receipts` attribute on the enabled monthly-savings sensor, unrecorded (`_unrecorded_attributes`), because 24 receipts exceed the recorder's 16 KB attribute limit. The two new keys are in #373's pinned attribute surface (see `## Red checks`, the `mutation` entry).
5. **The day-ahead promise (U2).** `AccuracyTracker.note_promise` keeps the first plan solved in the local midnight hour as the day's promise: the room trajectory and the cumulative cost over 24 h, two days kept, persisted with the accuracy history. `AccuracyTracker.replay` pairs yesterday's promise with the measured samples, published unrecorded as `plan_replay` on the same sensor.
6. **The Savings tab** shows the latest receipt: total, saving against a thermostat, billed lines with their basis, unpriced wear as "not priced", and the covers note. Beside it, "Where the money went" shows one-hue bars by reason. Below, "Yesterday: the plan against reality" draws the promise dashed and the measurement solid on a shared time axis. The page's styles ship with the page, so no other card state moves.
7. The `_learning_view` comment no longer describes the #110 heat-loss defect, which is fixed.

**The repair itself (five commits over the reviewed head).** `fix(R9-UX-6)` makes `roll_receipts` pure and moves `_roll_month`'s seam-map entry `core -> grid`; `record:` writes `seam_cut_total` 762 -> 756; `test(R9-UX-6)` repairs the two red baselines the mutation lane drives; `ci: re-record closures` is the closures-autofix bot's own commit at the reviewed head, merged; the last commit is that merge.

## Head

`271373ad592134828d25ed6bd080d9f48d34b177` merges the authored code head `631cca06f902768975e939664db0e34aa6676166` into this PR's previous head, which carried its own row `dev/programme/delivery/2119.md`. The PR tree is that code head plus the row.

`631cca06f902768975e939664db0e34aa6676166`, measured against merge base `7cd5a588cbbb` (three-dot); `origin/main`'s tip at this measurement is `6be88834e` (#2125 landed), 2026-10-10T19:33Z, and the merge base is unchanged by that move — main's newer commits are not ancestors of this head. Every figure below is a function of that head and that tip; the figures re-taken against the new tip are the golden/claims/card/predict quartet and the grep above, all re-run 2026-10-10T19:33Z and unchanged in value. The authored code head is `5d809cdb7`; `96eaf4a00` is the `closures-autofix` bot's commit (`changed -- nothing owed to a human`), merged rather than duplicated. The code head is unchanged from the previous handoff: no figure that is a function of the head alone was re-taken.

## Mutation proof

The UX-6 checks are a block at the end of `tests/features.py`, run alone with the in-tree block runner `tools/audit/seat/features_block.py`. Each mutant was applied to the head and then restored:

- M0, the head unmodified: `ALL 19 FEATURES BLOCK PASSED`.
- M1, `billed_total` sums every line it is handed, not `BILLED_LINES` (the defect restored): 4 fail -- "a receipt's total is the money the month cost, not its splits again" (709.5), "ledger.freeze_month_report totals the billed lines and names them", "a receipt frozen by the old sum is restated from its own lines on load", "a receipt stored with the old total loads with the billed total".
- M2, `_roll_month`'s `book_capacity` arm disabled: 3 fail ("the capacity line is the billed peak times the tariff while the month is open", "March's receipt names the capacity charge after the tracker reset", "the grid view publishes every receipt kept, oldest first").
- M3, the promise-hour/first-plan guard in `note_promise` turned off: 3 fail ("a plan solved after the midnight hour is not the day's promise", "the promise is the first midnight plan's: 24 h of room and cumulative cost", "the next day replays the promise against the 24 h it covered").
- M4, `restate_total` dropped from `_async_load_ledger`: 1 fails ("a receipt stored with the old total loads with the billed total").
- M5, the adoption dropped (`_, closed = roll_receipts(...)` -- the repair's own line): 1 fails ("March's receipt names the capacity charge after the tracker reset" reads `{}`).
- M6, `kept = reports` in `roll_receipts` (the pre-repair shape, a collaborator mutating the coordinator's mapping): `ALL 19 FEATURES BLOCK PASSED` -- the repair is architectural, not behavioural, and this is its null control: what moves is `arch-score`, not a check.

Card mutant: `receiptHtml`'s `basis` replaced by every key of `lines` fails 2 card checks ("the receipt shows the backend's total and the lines it adds", "the note names what the total covers"); restored, `node tests/card.mjs` reports `ALL CARD CHECKS PASSED`.

`tests/features.py` itself and the mutation lane are CI's (see `## Red checks`).

## Null control

- At the base, the defect check fails with `total_sek=709.5`; its null control, a month with only billed lines, passes at both base and head (194.5 either way), so the check moves only on the double count.
- No capacity tariff means no `capacity` line ("UX-6 null control: without a capacity tariff no capacity line is booked").
- On the promise's own day there is no yesterday to replay (returns None).
- The store probe refuses a receipt whose `basis` names `space`, a line it does not bill; under `_TEXT` it would have been admitted.
- Card drift: with the styles in the shared style block, `card_drift.mjs` against the base reported 39 of 40 states drifted. Scoped to the page, it reports `identical in all 40 states` -- the null control for the style scoping.
- M6 above is the repair's own null control: reverting `roll_receipts` to the mutating shape leaves every UX-6 check green, so the payment the repair makes is measured by `arch-score`'s own output, not asserted.
- Golden: `env_drift.py --all origin/main` reports `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over all 56 scenarios (re-taken against tip `6be88834e`, 2026-10-10T19:33Z). Recording the same capture locally moves 90 pre-existing float leaves (battery and DHW-profile values), which a dev box may not commit; it was not committed.

## Figures

`python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`; `max_class_loc=8745 <= 8745` (the coordinator class span is unchanged by the repair), `seam_cut_total=756 <= 756` (recorded down from 762 in commit `b19106207`), `functions_cc_over_25=8`, `max_cc=45`. `main` caps `max_class_loc` at 8818; the freeze's move out of the coordinator class remains a payment of 73 and no cap is raised.

`python3 -I tools/audit/archscore/gate.py --base $(git merge-base origin/main HEAD) --head HEAD --body <this body>` (re-run 2026-10-10T19:33Z; the merge base `7cd5a588cbbb` is unchanged by main's move to `6be88834e`) -- `Architecture score: dS +0.0073 IMPROVES / coord_footprint 2586 -> 2573 +0.0073 / PASS: dS +0.0073 IMPROVES, no gate metric rose`.

`python3 -c` over `tools/audit/archscore/metrics/shared_inplace_writes.py` at base and head exports -- `shared_inplace_writes` 22 at the merge base and 22 at the head; the three `ledger.py:421/429/433 _month_reports` sites the reviewed head added are gone, and no other site moved.

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -- `MODE: SCOPED -- 29 script(s) run, 4 scoped out`.

`python3 tools/audit/seat/features_block.py '# R9-UX-6: money and memory -- the receipt, the capacity line, the replay' '# -- live power clamp, 7a: the metered running draw (draw_range) ------------'` -- `ALL 19 FEATURES BLOCK PASSED`.

`python3 tests/entities.py` -- `ALL 2250 ENTITY CHECKS PASSED` (at the reviewed head this was `2 of 2250 FAILED`; see `## Red checks`).

`python3 tests/features.py` at the head -- `1 of 4005 FEATURE CHECKS FAILED`, `R9-F2.1 P3`, the BLAS float margin; the same script at a clean worktree of the merge base (`7cd5a588c`) on this box reports `1 of 3986 FEATURE CHECKS FAILED`, the same check with the same figures (`shipped 110.4366, seeded with the half-price plan 110.1297`). At the reviewed head this script did not reach its summary: it died at line 18661 on `AttributeError: 'types.SimpleNamespace' object has no attribute 'power_schedule'`, which is this diff's and is fixed.

`node tests/card.mjs` -- `ALL CARD CHECKS PASSED`. `node tests/card_drift.mjs origin/main` (re-taken against tip `6be88834e`, 2026-10-10T19:33Z) -- `card_drift: identical in all 40 states`. `node tests/md_tables.mjs` -- `doc_misrendered_lines=0`.

`python3 tests/env_drift.py --all origin/main` (re-taken against tip `6be88834e`, 2026-10-10T19:33Z) -- `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`; `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. `python3 tests/env_drift.py --claims-only origin/main` (same re-take) -- `claims hygiene: origin/main ok`.

`python3 tests/finite_boundary.py` -- `ALL 84 FINITE BOUNDARY CHECKS PASSED`. `python3 tests/deployment_shape.py` -- `ALL DEPLOYMENT SHAPE CHECKS PASSED`. `python3 tests/doc_claims.py` -- `ALL 160 checks PASSED`. `python3 tests/typing_ruler.py` -- `ALL 11 typing-ruler source checks PASSED`. `python3 tests/harness_headers.py` -- `ALL 109 HARNESS HEADER CHECKS PASSED`. `python3 tests/guard_pins.py` -- `ALL 50 GUARD PIN CHECKS PASSED`. `python3 tests/arch_score_head.py` -- `ALL 15 ARCHITECTURE SCORE HEAD CHECKS PASSED`. `python3 tests/arch_score.py --smoke` -- `ALL 257 ARCHITECTURE SCORE CHECKS PASSED`.

`python3 dev/audit/rounds/round4/D6/claims.py` -- `claims_extracted=125`, `claims_true=123`, `claims_false=0`, `claims_unverifiable=2`, `arch_modules_on_disk=75`, `arch_map_listed=75` (the merged tree reads 75 where the handoff's stacked base read 74: main's own `draw_range.py` is the extra module).

`python3 tools/pr/ci_predict.py --base origin/main` (re-taken against tip `6be88834e`, 2026-10-10T19:33Z) -- `39 unpinned site(s) the diff adds` and `no closures or fast red predicted against 7cd5a588cbbb (a data-file read is not seen)`.

## Architecture score

The gate's own output at this head (re-run 2026-10-10T19:33Z, merge base unchanged): `PASS: dS +0.0073 IMPROVES, no gate metric rose`. No metric rises, so there is nothing to explain; the reviewed head's rise is paid in code, not re-recorded:

- `shared_inplace_writes 22 -> 25` at the reviewed head is back to `22`: `roll_receipts` returns `(kept, closed)` and `_roll_month` adopts the mapping by rebinding its own slot, so a collaborator module no longer writes into coordinator-held state.
- `seam_cut_total` moves 762 -> 756 (down, recorded in `b19106207`): the adoption needs `_roll_month` to write `_month_reports`, a grid-seam attribute, and `_roll_month` books the capacity charge into the ledger, freezes the money receipts and schedules the ledger save -- all grid-seam state (`_ledger`, `_month_reports`, `_capacity_tariff`, `_schedule_ledger_save`) -- so its seam-map entry moves `core -> grid` and six crossings go. This is a design choice stated where the check encodes it: `tests/seam_map.json` line for `_roll_month`.

## Red checks

Every check that stands red on any commit this branch has pushed (`origin/main...origin/fix/r9-ux-6`, check-runs read 2026-10-10T19:20Z from the API, status completed, conclusion failure): seven names, each answered. Three heads of the branch carry reds — `10b4ae172` (the coord-capture test commit), `72b696d96` (the reviewed head) and `96eaf4a00` (the `closures-autofix` bot's pushed commit); all three predate the repair, whose code (`5d809cdb7`, `b19106207`, `5d7d82475`) is on this publishing head `631cca06f` and has not yet run CI. Each entry names the head, quotes the check's own output, and states the repair or why it does not bind here.

- **`arch-score`** -- red at all three heads (`10b4ae172`, `72b696d96`, `96eaf4a00`); the check's own line at `96eaf4a00`: `Architecture score: dS -0.9549 WORSENS (inadmissible: shared_inplace_writes 22->25)`, `FAIL: dS -0.9549 WORSENS; unexplained: shared_inplace_writes 22->25`. Cause: the fix's extraction moved three receipt writes into `ledger.py`, and the score prices a collaborator module's write into coordinator-held state -- it also made this body's earlier "pure functions" claim false for `roll_receipts`. Process state: **(c)** -- the fixer ran `arch_score.py --smoke` (257 checks over the scorer's own fixtures) but never the gate against the merge base, which is the check that prices a diff. Cheaper detector: `python3 -I tools/audit/archscore/gate.py --base $(git merge-base origin/main HEAD) --head HEAD --body /dev/null`, ~30 s local, zero standing cost. Repaired in code, not re-recorded: `5d809cdb7` makes `roll_receipts` return `(kept, closed)` (`shared_inplace_writes` back to 22) and `b19106207` moves `_roll_month`'s seam `core -> grid`; the gate's own line at this head, re-run 2026-10-10T19:33Z: `PASS: dS +0.0073 IMPROVES, no gate metric rose`.
- **`closures`** -- red at `72b696d96` only; its own output: `UNDER-SCOPED: tests/guard_pins.py really reads 1 file(s) the committed closure does not list: custom_components/heatpump_optimizer/ledger.py`. This is `closures-autofix`'s, and it acted -- `closures-autofix: changed -- nothing owed to a human`, commit `96eaf4a00 ci: re-record closures` pushed to the branch, at which head `closures` is green; that commit is merged into this publishing head rather than duplicated. The cheaper detector is `ci_predict.py`, which named it before any push. (Main's own `closures` red the same day -- `INERT READS UNDER-APPROXIMATED` at `969c3a5c8` -- was main-side, repaired by #2125; it is not one of this branch's reds and no answer is owed here.)
- **`coverage-ratchet`** -- red at `72b696d96` (91.03 %) and `96eaf4a00` (90.99 %); its own output at `72b696d96`: `COVERAGE RATCHET BREACHED -- package coverage 91.03 % < 96.0 %. 1900 of 21183 statements are uncovered`, `config_flow.py 99.90 % < 100.0 %`, `28 module(s) below the 95.0 % per-module floor`. Why: the coverage job's own log at that head reads `ran tests/features.py exit=1 wall=288s` -- `tests/features.py` died at line 18661 on the `AttributeError` below, so the package's broadest driver (4005 checks over every module) never exercised roughly 1800 statements and the coverage artifact under-measured. Main's green run the same hour (at `969c3a5c8`, check-run 114265441982) read `ok package coverage 98.59 % ... every module >= 95.0 % (0 below)`; no diff of this size moves 91 -> 98.6. Repaired by the same baseline repair that answers `fast (3.14)`: `5d7d82475` gives `_fake_plan` the three fields, and `tests/features.py` at this head reaches its summary (see `## Figures`). The ratchet re-measures at this head when CI runs; nothing is owed beyond that, and if it re-fires there with a green `features.py` that is a genuine new red, not this one. Process state: **(c)** -- the failing script was already named under `fast (3.14)`, and the process followed produced a second red from the same cause that only the coverage lane's own artifact reveals. Cheaper detector: the coverage lane's own `ran <script> exit=1` lines -- a red script inside the coverage job is a precondition of the artifact meaning anything.
- **`fast (3.14)`** -- red at `72b696d96` and `96eaf4a00` (`2 TEST SCRIPT(S) FAILED`: the run's own lines, `FAILED python3 tests/features.py` and `FAILED python3 tests/entities.py`); the two baselines `mutation`'s entry names, repaired in `5d7d82475`: `ALL 2250 ENTITY CHECKS PASSED` and `features.py` reaches its summary at this head, failing only the BLAS margin that fails at the merge base on this box.
- **`mutation`** -- red at all three heads; its own line: `MUTATION TABLE REFUSED -- 4641 unpinned site(s) against 4608 at the ratchet base d3dbf2c3f, 41 of them added by this diff`. Two causes, both addressed. (1) The pin lane could not measure at all: `mutation-pins` printed `MUTATION TABLE INCONCLUSIVE` because the baseline was red in `tests/entities.py` (MonthlySavingsSensor's new `receipts` and `plan_replay` were not in #373's pinned surface: `[removed []; added ['plan_replay', 'receipts']]`, `[308 pinned vs 310 published]`) and in `tests/features.py` (`_fake_plan` lacked the three fields `_file_lead_predictions` now reads, so the run died at line 18661 instead of summarising), so `mutation-autofix` reported `skip-measure-failed` and pushed nothing. Both are fixed in `5d7d82475`. (2) The diff's 39 new sites (this head's count) still owe ledger dispositions. Process state: **(b)** -- `ci-autofix.md` was not followed to its letter: the body wrote "left to `mutation-autofix`", but the bot pins only what a driver kills; a site no driver kills needs a killing check or a `survivor_triage`, and that triage is a human's. Cheaper detector: `python3 tools/pr/ci_predict.py --base origin/main` (seconds, predicted all of them) and `python3 tests/entities.py` (~2 min local) -- both existed and neither was run at the head. Countermeasure (built): the two baseline repairs, which unblock the CI pins lane at the next push; dispositions are under `## Unpinned sites`. Recorded refusal: this seat does not hand-write `survivor_triage` rows without a measurement, and the pin drive cannot run here -- `tests/features.py`'s BLAS margin is red on this macOS/Accelerate box (numpy reports `blas: accelerate`), which makes every mutant verdict `INCONCLUSIVE`; the container lane is CI-only since 2026-10-04. The killed sites are the autofix's at the pushed head, now that the baseline it drives is green.
- **`mutation-autofix`** -- red at `72b696d96` and `96eaf4a00` (`shards merged: skip-measure-failed`, `mutation-autofix: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`): the same cause (1) as `mutation` -- a red baseline is not a status the bot can repair. Answered by the same two fixes; nothing is owed to the bot.
- **`nightly-ha (stable)`** -- red at `96eaf4a00` only, on a dispatched nightly lane (the lane is `skipped` on push and pull_request events; both its lanes were green on dispatch at other heads the same day); its own output: `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`. `hb:positive_control` failed as `a 600 ms spin read as 600.4 ms; dump names the spin: True; py-spy rc=0 names it: False`, with `py-spy did not run: TimeoutExpired: Command '['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid', '1']' timed out after 30 seconds` -- the container's profiler timed out; the spin itself was detected and named. `run:exit_status` reads `the container exited 1`. The other 62 checks passed, including every integration-behaviour lane (entry loaded, 79 entities registered, reload, recovery, no blocking calls): the red is the container's py-spy instrumentation, not integration behaviour and not code this diff touches (the diff touches nothing the lane's harness reads). No repair: it does not bind at this publishing head, where the lane has not run; if it re-fires there the same way, that is the nightly lane's own infrastructure red, worth its own seat, not this diff's.
- **`pr-contract`** (not one of the ancestry names -- the arm excludes it -- but red at `10b4ae172` and `72b696d96`, so answered): `check 'arch-score' is red and '## Red checks' does not name it` and the `mutation` twin -- the verdict's own class; this section names both and every other red above.

## Forward-carry

none. U3, the household power budget, stays deferred beyond round 9, and U1's notifications and U5's screenshots are the sibling UX lanes' (`carry-1795.json`).

## Unpinned sites

`ci_predict.py` lists 39 sites this diff adds (`accuracy.py` 25, `ledger.py` 13, `coordinator.py` 1; re-taken against main tip `6be88834e`, 2026-10-10T19:33Z, same 39). Each disposition below states what was actually driven at this head; the pin lane (`mutation-pins`/`mutation-autofix`, `ci-autofix.md`) records the `killed_by` rows once the baseline it drives is green, and a site no driver kills owes a `survivor_triage` -- recorded here as owed, not faked.

Mutant driven at this head (the block runner, mutants above):

- `custom_components/heatpump_optimizer/ledger.py:320 RETURN_DEL` -- `billed_total`'s sum: M1, 4 UX-6 checks fail
- `custom_components/heatpump_optimizer/coordinator.py:10234 GUARD_OFF` -- `_roll_month`'s `book_capacity` arm: M2, 3 fail
- `custom_components/heatpump_optimizer/accuracy.py:218 GUARD_OFF` -- the promise hour: M3, 3 fail

Read by a named UX-6 value check (the check that fails when the site is broken; the mutant drive is the pin lane's, not claimed killed here):

- `custom_components/heatpump_optimizer/ledger.py:153 BOOLOP` -- `book_capacity`'s refused-input guard ("the capacity line is the billed peak times the tariff while the month is open")
- `custom_components/heatpump_optimizer/ledger.py:153 GUARD_OFF` -- the same guard, same check
- `custom_components/heatpump_optimizer/ledger.py:330 GUARD_OFF` -- `restate_total`'s non-dict guard ("a receipt stored with the old total loads with the billed total")
- `custom_components/heatpump_optimizer/ledger.py:333 RETURN_DEL` -- `restate_total`'s restated return, same check
- `custom_components/heatpump_optimizer/ledger.py:394 GUARD_OFF` -- `freeze_month_report`'s `mean_spot_price` arm ("March's receipt names the capacity charge after the tracker reset")
- `custom_components/heatpump_optimizer/ledger.py:396 RETURN_DEL` -- `freeze_month_report`'s return, same check
- `custom_components/heatpump_optimizer/accuracy.py:221 GUARD_OFF` -- `note_promise`'s no-promise arm ("a plan with an unpriced step makes no promise rather than a wrong one")
- `custom_components/heatpump_optimizer/accuracy.py:231 GUARD_OFF` -- `replay`'s no-promise arm ("UX-6 null control: on the promise's own day there is no yesterday to replay")
- `custom_components/heatpump_optimizer/accuracy.py:550 BOOLOP`, `custom_components/heatpump_optimizer/accuracy.py:550 CMP_BOUND`, `custom_components/heatpump_optimizer/accuracy.py:550 GUARD_OFF`, `custom_components/heatpump_optimizer/accuracy.py:552 CLAMP_DROP`, `custom_components/heatpump_optimizer/accuracy.py:553 BOOLOP`, `custom_components/heatpump_optimizer/accuracy.py:553 CMP_BOUND*2`, `custom_components/heatpump_optimizer/accuracy.py:553 GUARD_OFF`, `custom_components/heatpump_optimizer/accuracy.py:557 GUARD_OFF`, `custom_components/heatpump_optimizer/accuracy.py:563 BOOLOP`, `custom_components/heatpump_optimizer/accuracy.py:563 GUARD_OFF` -- `plan_promise`'s input guards and clamps ("the promise is the first midnight plan's: 24 h of room and cumulative cost")
- `custom_components/heatpump_optimizer/accuracy.py:584 CMP_BOUND*2`, `custom_components/heatpump_optimizer/accuracy.py:588 GUARD_OFF`, `custom_components/heatpump_optimizer/accuracy.py:599 GUARD_OFF`, `custom_components/heatpump_optimizer/accuracy.py:603 RETURN_DEL`, `custom_components/heatpump_optimizer/accuracy.py:608 GUARD_OFF` -- `replay`'s span and the promises' store round trip ("the next day replays the promise against the 24 h it covered"; "the promises are bounded, persisted beside the accuracy history and restored")
- `custom_components/heatpump_optimizer/accuracy.py:617 BOOLOP`, `custom_components/heatpump_optimizer/accuracy.py:617 CMP_BOUND`, `custom_components/heatpump_optimizer/accuracy.py:618 CMP_BOUND`, `custom_components/heatpump_optimizer/accuracy.py:621 RETURN_DEL` -- the stored-promise shape guard ("a naive or ragged stored promise is dropped, not loaded")
- `custom_components/heatpump_optimizer/accuracy.py:50 CONST` -- `PROMISE_HOUR`, read by "a plan solved after the midnight hour is not the day's promise"
- `custom_components/heatpump_optimizer/accuracy.py:51 CONST` -- `PROMISE_SPAN_H`, read by "the promise is the first midnight plan's: 24 h of room and cumulative cost"
- `custom_components/heatpump_optimizer/accuracy.py:53 CONST` -- `PROMISE_DAYS`, read by "the promises are bounded, persisted beside the accuracy history and restored"
- `custom_components/heatpump_optimizer/ledger.py:384 CMP_BOUND` -- `freeze_month_report`'s `reasons_reconcile` kWh tolerance (the flag is published, not asserted; no UX-6 check states the 0.05 figure)
- `custom_components/heatpump_optimizer/ledger.py:385 CMP_BOUND` -- the same tolerance's SEK arm, same disposition
- `custom_components/heatpump_optimizer/ledger.py:420 BOOLOP` -- `roll_receipts`'s month predicate ("the grid view publishes every receipt kept, oldest first")
- `custom_components/heatpump_optimizer/ledger.py:420 CMP_BOUND` -- the same predicate's bound, same check
- `custom_components/heatpump_optimizer/ledger.py:440 CLAMP_DROP` -- the retention trim; no kept receipt ever exceeds `KEEP_MONTHS` in the fixtures, so the block reads flat: a genuine `survivor_triage` candidate
- `custom_components/heatpump_optimizer/ledger.py:442 RETURN_DEL` -- `roll_receipts`'s return; M5 drove its caller (the adoption, 1 check fails), the return site itself is the pin lane's

The card mutant above (`receiptHtml`'s `basis` arm) is `tests/card.mjs`'s value check and is not in `ci_predict.py`'s inventory (it is JavaScript).

## Friction

none

