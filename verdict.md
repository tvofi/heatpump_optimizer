Fix review: merge 6790e09663bac8b9ba15e7f9ba91fbc7afdac78b

bus-nonce: 80ebf57831457d6d92cb5931ebbc00ad

## Scope

This is round 3, the delta round of the fix review of #3220 (R10-HOTFIX-SAV-ESTIMATE). It reviews head 6790e09663bac8b9ba15e7f9ba91fbc7afdac78b from a detached worktree at that SHA. The previous verdict is `merge 1d114ed62a582faeb04211104ebb118ec30bd6c9` (verdict/3220).

`review_carry.py 1d114ed6 6790e096` prints `FRESH-REVIEW`, because `67e54f8d204a69c7a0e1ce37e7afeb17ddc4d3df is not the automatic merge of its parents`. That commit is the `ledger.py` conflict resolution with #3195. Its branch-only commits are 6f8dfe831, 67e54f8d2, 5dc4cd6e0, 359caf94c, 5a0fef27b, a1a7b2a6b, b85a88dc0 and 6790e0966 (ev/review_carry.txt).

The scope is exactly the brief's five items. Nothing the 1d114ed6 verdict judged is re-reviewed. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so this contract is current.

## Evidence

- RESULT head note: 6790e0966 is the merge of origin/main 788e8ceed into b85a88dc0.
  - `git merge-tree --write-tree b85a88dc0 788e8ceed` gives tree 1d1984c3ac117a508cf3a6fed6776f8ec67f125c, which equals the head's tree. So the main merge is automatic and adds no resolution.
  - `git diff b85a88dc0 6790e0966` touches none of `ledger.py`, the savings files or `tests/structure_budgets.json`. Its 7 files are main's `tools/pr/` and policy changes.
- RESULT item 1, the resolution against both parents (ev/ledger_vs_reviewed.diff, ev/ledger_vs_main.diff):
  - Head's `ledger.py` less main 788e8ceed is exactly the hotfix's own hunks: `REFERENCE_BASIS_META`/`REFERENCE_BASIS`/`OLD_REFERENCE_BASIS`, the unclipped `savings_pct`, `migrate_ledger_v1`, the first-booking stamp in `add_savings_settlement`, `savings_months(..., wood_configured=False)`, the wood floor `calibration = max(1.0, calibration)` and `old_basis` with its dash.
  - Head less 1d114ed6 is exactly #3195's hunks: `SAVINGS_STORED_LINE`, `STEADY_COP_META`, `SETTLEMENT_KEYS`, `SAVINGS_COMFORT_LINE`, `settle_interval_savings` folded into `observe_settlement`, the stored and comfort bookings, the `stored_sek`/`comfort_sek` terms and the coverage factor on all four, plus the docstring.
  - So neither side was taken wholesale and no line of either was lost.
- RESULT the estimate is still fixed. The finder's census is `dev/audit/harnesses/r10_rca_sav_estimate.py`, sha1 04b644563c84d26378cad42a603dc050e7e5fd88, the same file at all three trees and run from one scratch copy with the same inputs:
  - At head 6790e096: `census: 6 of 6 cells ran, 0 out of band: -`, rc 0.
  - At reviewed 1d114ed6: `census: 6 of 6 cells ran, 0 out of band: -`, rc 0.
  - At main 788e8ceed: `census: 6 of 6 cells ran, 4 out of band: valve-at-curve valve-charged wood-warm wood-hot`, rc 1. The four read 0.00 there and 1.00 at both other ends.
  - Logs: ev/census_H.log, ev/census_R.log, ev/census_M.log.
- RESULT #3195's behaviour is kept. These are #3195's own checks inside `tests/features.py`, run on a copy of the head with a comment-only change (the null):
  - The run printed `ALL 4855 FEATURE CHECKS PASSED`, rc 0 (ev/mutant_null.log).
  - The R10-SAV-COMFORT checks pass. `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price` goes red when main's side is dropped (mutant `stored_drop` below).
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head printed `ALL 2631 ENTITY CHECKS PASSED`, rc 0 (ev/entities_H.log).
  - `tests/typing_ruler.py` (source checks) printed `ALL 12 typing-ruler source checks PASSED`, rc 0 (ev/typing_ruler_H.log). The `--mypy` run was not taken here. CI's `tests / typing` is green on this head.
- RESULT item 2, one floored scale. This is my own probe, `ev/scale_probe.py`, which books 48 one-hour intervals into a closed month and reads `savings_months` (ev/probe_H.log, ev/probe_R.log, ev/probe_M.log).
  - The scale, from the code: `calibration = meter_calibration(month)`, which is metered kWh over planned kWh, or None. With `wood_configured` it is floored by `max(1.0, calibration)`. Then `scale = 1.0 if calibration is None else calibration`.
  - The three terms are:
    - thermostat: `savings_baseline.sek * scale`
    - stored: `scale * stored_kwh_th / cop * (actual.sek / actual.kwh)`, which is 0 when there is no COP or `actual.kwh <= 0`
    - comfort: `savings_comfort.sek * scale`
  - Each of the three is a modelled quantity on the thermostat's side: a modelled kW draw, a modelled stored-heat change at the modelled COP, and a modelled comfort draw. The calibration corrects the model against the meter, so one scale for all three is consistent. The floor's premise (a meter under the plan on a wood house is the fire, not a model over-read) applies equally to all three, so I find no term that should leave the shared scale.
  - Null control, flat price 1.0, calibration 1.0, no stored or comfort: `baseline_sek=96.0 actual_sek=96.0 savings_sek=0.0 savings_pct=0.0` at the head, at 1d114ed6 and at main, with wood and without.
  - Units and sign, each term at calibration 1:
    - stored +0.6 kW_th over 48 h at COP 3 reads 9.6 SEK, which is 28.8 kWh_th / 3 x 1.0 SEK/kWh.
    - stored -0.6 reads -9.6.
    - COP 1.5 / 3 / 6 reads 19.2 / 9.6 / 4.8, inverse in COP.
    - comfort 0.3 kW over 48 h reads 14.4.
    - Under alternating 0.5 / 1.5 prices the stored term is priced at the row's metered mean, 1.0.
  - Floor boundary, wood configured, stored 0.6 and comfort 0.3:
    - calibration 0.999: savings 9.70 with wood against 9.59 without, `meter_calibration` 1.0 against 0.999.
    - At 1.0 and at 1.001 the two rows are identical (9.60, and 9.61 with `meter_calibration` 1.001).
    - The floor is exactly at 1, it applies only below 1, and it applies only with wood.
  - Zero and tiny scale:
    - Without wood, calibration 0 and 1e-9 give baseline 0.0, `savings_pct` None, and every term 0.
    - With wood, calibration 1e-9 floors to 1.0 and reads stored 9.6, comfort 14.4 and baseline 105.6.
    - With wood and calibration exactly 0 (a month with no metered kWh), the stored term drops to 0.0 while the thermostat and comfort stay floored at 96.0 and 14.4. See Findings.
  - A case that moves if the floor is wrong: calibration 0.5 with wood gives baseline 105.6, saving 57.6, 54.5 %. With the floor removed it gives 52.8, 4.8, 9.1 %. With the floor on the thermostat only (mutant `split_scale`) it gives 100.8, with stored 4.8 and comfort 7.2.
- RESULT mutants on the resolution. Each mutant ran the full `tests/features.py` on a copy of the head with one exact replacement (ev/mutants.py, ev/mutants_summary.txt, ev/mutant_*.log). OPENBLAS_CORETYPE=Haswell.
  - `null` (comment only): `ALL 4855 FEATURE CHECKS PASSED`, rc 0.
  - `floordel` (`calibration = max(1.0, calibration)` becomes `pass`): KILLED, 2 of 4855. It fails `with wood configured a meter under the plan earns its saving: the calibration does not cancel it` (`{1.0: 50.0, 0.5: 50.0, 0.25: 50.0}`) and `with wood configured a model that under-reads the meter is still corrected ...`. This is the body's row exactly.
  - `floormin` (`max` becomes `min`): KILLED, 2 of 4855, by the same two checks.
  - `stored_drop` (`+ stored_sek` dropped from `baseline_sek`, main's side lost): KILLED, 1 of 4855, by `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price` (baseline 20.0). This is the body's row exactly.
  - `oldbasis_off` (`old_basis = False`): KILLED, 4 of 4855, by the old-basis and migration checks.
  - `split_scale` (stored and comfort take the unfloored calibration, the thermostat keeps the floor): SURVIVED, `ALL 4855 FEATURE CHECKS PASSED`. See Findings.
  - `stored_unscaled` and `comfort_unscaled` (the term drops `scale`): SURVIVED at the head, and SURVIVED at main 788e8ceed (`ALL 4830 FEATURE CHECKS PASSED`, ev/mutantsM_summary.txt). That gap is #3195's own, inherited and not this resolution's. See Findings.
- RESULT item 3, the body's figures re-run at the merged head 6790e096. The fixer's extended harness `dev/audit/harnesses/r10_sav_wood_reference.py` is sha1 23f17afe540f2cc82f7f5d5e1f4d4fe51b36d736, from a scratch copy, OPENBLAS_CORETYPE=Haswell, two days (ev/woodext_H_*.log).
  - Every row equals the body's `## Figures` table:

    | arm | pct | `--no-settlement` | stored_heat_sek | comfort_sek | baseline / actual |
    |---|---|---|---|---|---|
    | valve-flat | +0.56 | +4.18 | -6.32 | 5.50 | 167.15 / 166.22 |
    | valve-vary | +25.26 | +28.50 | -9.09 | 7.11 | 200.64 / 149.95 |
    | wood-cold | +0.47 | +4.24 | -6.57 | 5.49 | 166.90 / 166.12 |
    | wood-stale | +4.07 | +7.20 | -5.66 | 5.60 | 167.82 / 160.99 |
    | wood-coast | +19.34 | +22.40 | -6.58 | 4.93 | 166.89 / 134.62 |
    | wood-fire | +37.37 | +38.54 | -3.23 | 5.65 | 170.24 / 106.62 |
    | wood-unforeseen | +40.42 | +42.82 | -6.99 | 5.53 | 166.49 / 99.20 |
    | wood-full | +92.99 | +92.61 | +9.32 | 2.18 | 182.80 / 12.82 |

  - The default arms read `first: SOUND`, `valve-flat: SOUND`, `valve-vary: SOUND` and `arms run 3, defect 0`, rc 0, both with and without the flag.
  - The residuals are unchanged by the flag: -3.90, -8.02, -3.57 and -3.61 %.
  - No figure moved between the body's measuring trees (67e54f8d2 and 5dc4cd6e0's tree) and the merged head.
  - The original harness (sha1 0f98bbb397a62d65a07448e934e0e100e49359da) at the head and at 1d114ed6 reads `valve-flat: SOUND` pct +4.18 residual -3.90 %, and `valve-vary: SOUND` pct +28.50 residual -8.02 %, rc 0. That is the 1d114ed6 verdict's figures. At main 788e8ceed it reads `first: DEFECT` (`step0/mean 0.000 ... BAD`), then `TypeError: MonthlyLedger.savings_months() got an unexpected keyword argument 'wood_configured'`, rc 1. These are the body's both-end figures (ev/woodorig_*.log).
  - wood-fire, wood-unforeseen and wood-full first hit my own 3000 s timeout under CPU contention (rc 124). They were re-run alone to completion, and the table rows are from that re-run.
- RESULT item 4, `class_excess_loc`:
  - `python3 tests/structure.py` at the head prints `ok class_excess_loc 17589 <= 17589` and `STRUCTURE RATCHET PASSED`, rc 0 (ev/structure_H.log).
  - The three-dot budget diff against merge base 788e8ceed is `class_excess_loc` 17617 -> 17589 plus `recorded_at`. That is downward, with nothing raised and no other `*_budgets.json` or governance config touched (ev/budgets_diff.txt).
  - 17589 is main's 17617 less the hotfix's -28 that the 1d114ed6 verdict judged (17618 -> 17590), rebased by the ledger driver.
  - The round's payment, 5dc4cd6e0, rewrites `savings_months`' docstring from 5 lines to 4. Its content shrinks from 329 to 294 characters, because the duplicated "(owner ruling, 2026-11-04)" citation and "both scaled as the thermostat is" become one "(owner rulings, 2026-11-04 ...)". The lines widen to 81 columns. `ledger.py` has no line-length limit and already holds 37 lines over 81. The payment is a real if small deduplication and not a relabelling. See Findings on the instrument.
  - `python3 tools/audit/archscore/score.py --diff 788e8ceed` at the head prints `Architecture score: dS +0.0000 NULL`, rc 0 (ev/archscore_H.log). The body quotes the same against 0ae75bf31.
- RESULT gate scope: `python3 tests/closure.py select --diff 788e8ceed` at the head prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`, the body's figure (ev/closure_select_H.log).
- RESULT merge with origin/main: `git merge-tree --write-tree origin/main 6790e096` at origin/main 7af0c2a79 exits 0 and prints `LEDGER-MERGE: resolved tests/closures.json`, with no `refused` marker and no conflict (ev/mergetree_main.txt).
- RESULT version: the three-dot diff touches none of `VERSION`, `manifest.json` or `RELEASE_NOTES.md`. `VERSION` is 7.1.1, and both claim files read `claims-for: 7.1.1`.
- RESULT claim files: `card_claimed_drift.txt` is byte-identical three-dot. `claimed_drift.txt` differs only by the hotfix's R10-HOTFIX-SAV-ESTIMATE claims, which the 1d114ed6 verdict judged. This round's commits touch no `tests/golden/` file.
- RESULT item 5, CI on this head, run 42024722714. `get_check_runs` gave total 46 on one page of 100. Each red was read from its own job log (ev/ci_reds_6790e096.txt):
  - `tests / mutation`: `MUTATION TABLE REFUSED -- 3099 unpinned site(s) against 3093 ... 8 of them added by this diff`. The eight `ADDED UNPINNED` sites are exactly the body's `## Unpinned sites`. `mutation-pins` pins them (`ci-autofix.md`), and the body answers it.
  - `governance / delivery-status`: the OVERDUE rows are #3205, #3216, #3193, #3181, #3191, #3201, #3206, #3189, #3204, #3203, #3202, #3174, #3091, #3089 and #3192, none of them #3220. It is inherited, as the body says.
  - `tests / nightly-status`: `NIGHTLY FAILED: slow failed last night`, scheduled run 41943946464 on main 499162c. It is inherited, as the body says, and the diff does not reach what it reads.
  - `tests / replay`: `FAIL owner-2026-10-30-away.json: cycle_cost [1 offender(s): loop_cpu_ratio 0.1238: budget 0.249 cannot see a 2x cycle; re-record 0.1751]`, 1 of 194. The body does not name this red. See Findings.
    - I ran the fixture myself, `tests/replay.py --fixture tests/replay/owner-2026-10-30-away.json`, at the head and at main 788e8ceed, concurrently on this host (ev/replay_away_H.log, ev/replay_away_M.log). Both print `ok owner-2026-10-30-away.json: cycle_cost` and `ALL 173 replay checks PASSED`.
    - The solve's `cpu_ratio` is flat: 237.72 at the head against 236.51 at main.
    - `loop_cpu_ratio` reads 0.1411 against 0.2212, but its normaliser `loop_ref_ms` moved from 161.1 to 236.8 between two concurrent runs on one host. So the loop ratio carries that much timing noise.
    - CI's 0.1238 needed 0.1245 (half of 0.249) and missed by 0.6 %. Main's own push run on 788e8ceed (42022036882) skipped `tests / replay`, so it gives no CI comparison.
    - I judge this a timing red at the fixture budget's edge and not this diff: the diff does not move the solve's cost on this fixture.
  - CI wait: `merge_train.py classify 6790e096... --pr 3220` was re-run at least 60 s apart from 12:3x to 14:30:27Z. It ended at rc 1, `RED 6790e09663bac8b9ba15e7f9ba91fbc7afdac78b pending: none red: gate` (ev/ci_wait.log, ev/ci_classify_final.txt).
    - The gate is job 127305450394 in run 42024724099. Its whole verdict is `FAIL tests / mutation: failure (run 42024722714)`: it is red on the added unpinned sites alone, which the body names and `mutation-pins` records.
    - `pr-contract / pr-contract` jobs 127304963464 (14:25:31Z) and 127306447546 (14:28:08Z) both concluded success. They started after every red on this head had concluded (mutation 12:10Z, replay 12:27Z, delivery-status 12:11Z, nightly-status 12:10Z), so by step 11 the body check is green.
    - Green on this head: typing, fast (3.14), coverage, browser, closures, arch-instrument, lane-proofs, graders-head-copy, coverage-ratchet, mutation-pins 1 and 2, arch-score, budget-raise-gate, policy-docs, instrument-self-tests, env-matrix, wave-script, codeql (python, js, actions), hassfest and validate-hacs.
    - The head was re-read at 14:3xZ: `refs/pull/3220/head` is still 6790e09663bac8b9ba15e7f9ba91fbc7afdac78b.
    - This `merge` asserts the patch at 6790e096. A red CI never carries: the train must see the gate green after the pin commit, which `review_carry` should read as CARRY.
- RESULT forward-carry: the roster on `origin/handoff/audit-r10-roster` holds four R10-SAV-COMFORT carry items "From PR 3220" (c38cb7d9, e9ced5fc, d7f65c3b, 7f2fa39d). They cover the body's two forward-carry items (the residual, and the uncapped `_apportion_by_steady_demand`). This is from a scout's read of the roster, not from my own read.
- RESULT self-audit: I ran `carry_audit.py check` with this verdict as the comment and an empty body file. It printed `CARRY-AUDIT: 0 finding item(s)`, rc 0 (ev/carry_audit_check.txt). The body side was taken from the packet's own run at the head: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted`, both to R10-SAV-COMFORT.
- RESULT head: the body's `## Head` names 6790e09663bac8b9ba15e7f9ba91fbc7afdac78b, the head I measured.
  - The section then carries a stray paragraph that opens with `a1a7b2a6...` and describes the fixer's handoff, plus a stale "Merge base 0ae75bf31". The merge base is now 788e8ceed.
  - That is a body-shape defect only. Every figure was re-taken at 6790e096 above.

## Findings

- Surviving mutant `split_scale`: no check pins that the stored and comfort terms ride the floored scale on a wood house. Putting the floor on the thermostat alone passes all 4855 feature checks, while my probe moves the row at calibration 0.5 with wood (baseline 105.6 -> 100.8; stored 9.6 -> 4.8, comfort 14.4 -> 7.2). The body claims "all three terms ... ride the one floored scale", so a check owes a wood month with stored and comfort lines under a meter below plan. Carry: R10-SAV-COMFORT
- Surviving mutants `stored_unscaled` and `comfort_unscaled`, inherited from #3195: both survive at main 788e8ceed and at the head. No check books a calibrated month (calibration not 1) with stored or comfort lines, so the "scales as the thermostat does" rule is unpinned. Carry: R10-SAV-COMFORT
- Edge: on a wood-configured house with a month that metered exactly 0 kWh, the stored term reads 0.0 (no metered price to apply), while the floored thermostat and comfort terms stand. Probe at calibration 0 with wood: stored 0.0 against 9.6 at calibration 1e-9. The month row is discontinuous at `actual.kwh == 0`. That is #3195's guard, exposed only because the floor keeps the scale at 1. This is a low-severity edge for the row owner to decide (price the stored heat at the month's mean spot instead, or keep it). Carry: R10-SAV-COMFORT
- Unanswered red: `tests / replay` on this head is red on `owner-2026-10-30-away.json: cycle_cost` (loop_cpu_ratio 0.1238, budget 0.249 needs 0.1245). The body's `## Red checks` does not name it, and it says replay was not red on the earlier heads. My measurement makes this the fixture's loop-cost budget at its edge under timing noise, not this diff: the solve's cpu_ratio is flat head against main, and the loop normaliser swung 47 % between two concurrent local runs. The body owes it a line under `## Red checks` for `pr-contract`. The budget's sensitivity is #3219's fixture's to re-record. Carry: R10-FLY-REPLAY-MASK
- Instrument: `class_excess_loc` counts physical lines, so re-wrapping a docstring to a wider column pays it with no code change. 5dc4cd6e0's one-line payment depends partly on widening to 81 columns: the 294 remaining characters would not fit 4 lines at the old 78-column maximum. The deduplication in that commit is real, and the movement is 1 LOC at zero headroom. The budget itself was earned in round 2 and is not moved by this payment. Carry: dismissed: one line of a real docstring deduplication within the file's existing line widths

## Friction

- The frugal-routing hook refused inline reads and greps after the fifth per prompt, and it did not reset after a delegation. I did not override it (`FRUGAL_ALLOW_INLINE`). I delegated one roster lookup to a scout, and I read my own run outputs through the commands that produced them. The roster carry is the one figure here taken from the scout, not from my own read.
- The brief's "push handoff-wip at each milestone" conflicts with the PROMPT's "push nothing else" beside the probe ref. I followed the PROMPT, so no handoff-wip ref was pushed.
- Job-log blob downloads are refused by the proxy (403), so the CI reds were read through `get_job_logs` tails, not saved whole.
