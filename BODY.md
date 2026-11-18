R11-OUTSIDE-SELF-SETTING-PUMP, rebuilt on the round-3 design (`design.md` at 0acbbc8b910c57256696e0d8ff56649b71eb8bbc of design/R11-OUTSIDE-SELF-SETTING-PUMP; `Design review: approve 0acbbc8b910c57256696e0d8ff56649b71eb8bbc`, design-verdict at 7062403121b7d5399ed6fea3eff6638b18168348). It answers `Fix review: blocked 1134fe365519ce1334aa95960e19f908bb2b4f53 class-open` (verdict at ba984f3567823b3b5f0b2297aff35e6be6185fd7). Owner ruling D4 (tvofi, 2026-11-15) stands: the self-setting pump residual of #3593 is fixed, not accepted. The first body's carry answers (carries 0 to 4 of this group on handoff/audit-r10-roster) are unchanged except where a section below says so.

prepr: passed rc=0 at 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7

By roster carry (`carry` of R11-OUTSIDE-SELF-SETTING-PUMP in `dev/programme/rosters/wave-r11-groups.json` on handoff/audit-r10-roster at 3df132ea51, 0-based); this repair changes no production line, so each status is the one the earlier heads measured:

- **Carry 0** (owner ruling D4, the self-setting pump residual of #3593): built, as `## What ships` and `## The block, answered` state; harness rows under `## Figures`.
- **Carry 1** (departure 1, the release behind the freeze gate): kept, and extended to the restore and to the dither (frozen and unread cycles read no row, check "two admitted rows then a frozen cycle, an unread one ..."), as the orchestrator ruled.
- **Carry 2** (departure 2, a replay does not feed the capacity envelope): kept, not owed, as the orchestrator ruled; its control "a replayed interval folds the scale and not the capacity envelope ..." passes inside the gate's `ALL 5870 FEATURE CHECKS PASSED`.
- **Carry 3** (a release bounded per cycle) and **Carry 4** (the overstated-minimum floor): not built; the owner ruled "Accept both" (2026-11-16). Residuals under `## Forward-carry`. Carry: dismissed: owner ruling 2026-11-16 accepts both as residuals
- **Carry 5** (body item 0b01d5fd, a heat-led install whose admitted intervals are never consecutive never decides), **Carry 6** (06cb4f11, a re-priced plan restarts the probe without end) and **Carry 7** (26742487, fabric replays priced at the dither level): this pull request's own findings, open and unchanged at this head, stated with their controls under `## Forward-carry`; each is the note's follow-up item, which the design verdict routed to the orchestrator. Carry: R11-OUTSIDE-SELF-SETTING-PUMP

## Two measured costs the owner should see first

The class the block names is closed, and every acceptance line the note marks is met. Two heat-led rows that learned at the base and at the blocked head do not learn here, each by a rule the approved note states; both are under `## Forward-carry` with their controls:

- `repriced_heat1.2_true_0.8_x672` (a plan re-pricing its ask against the scale): 377/672 folded to 0.800 at both earlier ends; 0 folded, pending, 56 probes here. The note names this as its open risk, unmeasured; this is the measurement.
- `sub_min_true_0.6_x1440` (two asks in three under the duty floor): 470/1440 folded to 0.599 at both earlier ends; 0 folded, pending here.

## The block, answered

The block: the heat-ask probe took its regressor's span from the scale's own folds, the folds from the draw, so a self-setting draw swinging on its own over 64 to 96 cycles latched `follows` and the scale walked to 0.500.

What closes it: the regressor no longer comes from the draw. While the verdict is pending nothing folds, and the only scale movement is a dither whose order a seeded coin draws per pair of intervals (`accuracy.ScaleDither`). The verdict is the mean of the pair contrasts against `FOLLOW_SLOPE_MIN`, three standard errors clear (`FOLLOW_BOUND_Z`).

Measured at this head (`## Figures`):

- The reviewer's seven rows, by the reviewer's own generator and now in the harness over seeds 1 to 5 (`selfset_2.2_swing*_s<seed>`, `selfset_2.2_mix*_s<seed>`): 35 of 35 read `does_not_follow` and end at 1.000. At the blocked head 1134fe3655 the same rows read 20 `follows` at 0.500 and 15 `does_not_follow`; at the base 367c3b9cac, 35 at 0.500.
- The reviewer's map driver (19 cells, seeds 1 to 5) reads `follows=0/5` in every cell, and the reviewer's sweep driver (60 rows) reads 60 `does_not_follow` at 1.000; both ran unchanged from the verdict commit ba984f3567.
- The domain sweep, `dev/audit/harnesses/cop_scale_probe_sweep.py` (the repair seat's `sweep.py`, committed, with periods of 2, 3 and 4 cycles added): 0 of 2370 self-setting rows latch `follows`, every latched one ends at 1.000, and 0 of 360 heat-led rows read `does_not_follow`.
- Null control 1 (the dither's amplitude forced to zero, `--null`): 2730 of 2730 rows stay pending. The verdict comes from the instrument.

## The owner's three decisions

1. **Active dither, ±7.2 %, about a day per probe.** Built. `ScaleDither.levels` is the base times `FOLLOW_ASK_SPAN` to the ±½ (0.9325 and 1.0724 of 1.0); where a centred level would pass a clamp the levels are the base and one full step to the open side. A decided probe takes 50 admitted rows: 2 before its first pair and 24 pairs (`MIN_SAMPLES`). The harness's `band` column is the furthest the scale sat from a running probe's base, in steps: 0.500 on every centred row, 1.000 only on the one-sided rows near the 0.5 clamp.
2. **Nothing folds while the verdict is pending.** Built as hold, not fold: an admitted interval joins `MeasuredCop.held` whatever its ratio and reads `COP_REFUSED_NO_EVIDENCE`. Once the probe reads `follows` the hold folds, each row against the scale it was read under; on `does_not_follow` it is dropped. A row that leaves the hold while the probe is still pending (older than `COP_HOLD_HORIZON_S`, or past `WINDOW` rows) is dropped, never folded by base's rule. Reading disclosed under "Readings of the note" below.
3. **At the window cap: stop, return to base, stay pending, re-arm after `COP_HOLD_HORIZON_S`.** Built. The `WINDOW`-th admitted row parks the probe (`ScaleProbe.parked_at`); the next cycle returns to the base and a parked probe reads no row. It re-arms once the horizon has passed, or where the wait is unknowable (the park stamped ahead of the clock, `fixer.md` step 16). The park is not stored: a restart starts the probe over.

## What ships

- `accuracy.ScaleDither`: the pairs, the coin, the contrasts and the bound. `accuracy.ScaleProbe`: the verdict, the base, the scale owed each cycle (`owed_scale`), the park, the reset and the stored form. `MeasuredCop` holds one `ScaleProbe` and stays the only caller.
- `coordinator._fold_measured_cop`: the `take_restore` statement is replaced, not joined, by `if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None: self._apply_cop_scale(owed)`. `_apply_cop_scale` stays the only writer of the scale.
- `store.py`: one key, `measured_cop/scale_base`, beside `measured_cop/scale_response`. A pending verdict loads the stored base and the first cycle returns to it.
- `draw_range.py` is byte-identical to origin/main: `step_response`, `draw_response` and `_span` are gone.
- `dev/audit/harnesses/cop_duty_floor.py` gains rows and two stats columns; `dev/audit/harnesses/cop_scale_probe_sweep.py` is the committed sweep.

## Design verdict items, one by one

- **1b98ae3f** (a re-priced pair gives no contrast). Built: a pair whose heat asks moved by less than `FOLLOW_SLOPE_MIN` of the step in the coin's direction is void (below that, a perfect follower would itself read under the threshold). Harness row `repriced_heat1.2_true_0.8_x672` reads pending, 0 folded, never `does_not_follow`. Finding under `## Forward-carry`: it starts 56 probes in 672 cycles.
- **1ff86b5f** (held rows ageing out under a pending probe). Stated: held for replay. The aged-out exit drops instead of folding while the probe is pending or still owes a scale (check "release: no fold lands on a pending heat-ask probe however long it lasts"). The largest one-cycle move, re-measured as asked: `heatled_true_0.68_flat_max_cycle_move=0.308` (0.241 at the base and at the blocked head) beside `true_0.6_max_cycle_move=0.292`, identical at all three ends.
- **76b936b7** (the scale on a cycle that admits no row). Stated and pinned: the level for the next interval is set before that interval's row is judged, so the first cycle with no row still runs a dither level; from the second on the scale is at the base, for any length of idle. After a frozen or unread cycle the next live cycle returns to the base. Checks "mid-probe, a pump that goes off" and "mid-probe, a frozen cycle".
- **5bb6a355** (a reset while pending). Built: the reset makes the base owed and it is applied in the same cycle; that cycle's interval, read under the dither level, is held and folds next cycle against its own scale. Check "a reset mid-probe returns the scale to the base in the same cycle".
- **ffb019e7** (stored learner values under the dither). Measured where the instrument reaches, under `## Figures`; the rest is read, not measured, and carried.
- **740366bf** (pending cells). Named with counts under `## Figures`, "The sweep".
- **7aa61215** (probes per row). The `probes` column: 1 on every sweep row and every harness row but two, `selfset_2.2_flat_reload70_400_lost` (2, a reload without the stored key) and `repriced_heat1.2_true_0.8_x672` (56, asks that alternate between spanning and flat).
- The three items the verdict routed to the orchestrator (carry 1 extended to the dither; the follow-up group's roster entry; carries 1 to 4 restated) are not this seat's to rule. Carry 1 as built: the owed scale sits past the freeze gate, so a frozen cycle keeps the level it had. Carry: R11-OUTSIDE-SELF-SETTING-PUMP

## Readings of the note, disclosed for the reviewer

1. **Hold, then replay.** The note's fixer line says every `_admit` caller "must hold, not fold, while pending"; the owner's line says an admitted row "folds nothing". Built as the tree's existing hold: rows wait in `held` and fold on `follows`. The alternative, dropping them, was built first and measured: `held_full_heatled_true_0.8` read 45/96 at 0.851 against the note's 0.807; with the hold it reads 96/96 at 0.810.
2. **`draw_range.py` returns to main exactly.** The note says "main's shape plus the merge's `_verdict`". With `step_response` and `draw_response` gone `_verdict` had one caller, and main's file needs no ledger change: `git diff origin/main HEAD -- custom_components/heatpump_optimizer/draw_range.py` prints nothing.
3. **Two classes beside `MeasuredCop`.** The note names `MeasuredCop` as the one owner. The probe's state inside it took the class to 368 lines and `class_excess_loc` 68 over its budget; `ScaleProbe` and `ScaleDither` carry it instead, `MeasuredCop` holds the probe, and the budget is unmoved.
4. **`unsettled`.** An interval judged on a cycle where the probe moved the scale, or still owes its base, ran under another scale than the one in force. It is held, by whichever evidence judges it, and folds from the hold against its own scale. This is the note's priced-scale alignment applied to the cycle's own row.
5. **Null control 3 does not hold on four rows**, and cannot under decision 2. `sub_min_true_0.6_x384` and `_x480` read 118/384 at 0.611 and 150/480 at 0.603 at the blocked head and 0 folded, pending, here; `held_filling_heatled_true_0.8` reads 96/96 at 0.810 there and 0/96, pending, here; `selfset_flat` (96 intervals) ends pending at a dither level. Each has fewer than 50 admitted rows between the window turning unobtainable and the row's end. The `sub_min` rows are also a finding (`## Forward-carry`): they never decide at any length.

## Head

`454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7` is the code head of this body-only repair of `Fix review: blocked 9894911a81cdceb51eecec093a2527f93576d34e red-check` (verdict on review/3662). It is the merge-main bot's `ci: merge main` over the reviewed 9894911a81; this repair adds no commit, so the diff the verdict judged is unchanged. Merge base 1da13aafb7c23cf34fbda51bb27cb95132b4089b. Measured 2026-11-18 01:16 UTC; at that time origin/main is 7ae657e0e2bf42731c902f5aebf1d20d3e76d348 and `git merge-tree --write-tree origin/main 454d4fc425` reports no conflict (rc 0), so main is not merged. `merge_train.py classify 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 --pr 3662` printed `RED ... pending: none red: gate` and no INTRODUCED line; `gate` (job 134495927170 of run 44196634218) failed only on `FAIL budget-raise-gate / budget-raise-gate: cancelled (this run)`, which this seat re-ran (`rerun_failed_jobs` on run 44196634218), not repaired. The diff only lowers `tests/structure_budgets.json`. The verdict's block, the stale `scope-line` figure block, is answered by re-rendering it at this head (`figure_block.py refresh`, through `body_push.sh`); `pr-contract / pr-contract` passed at this head in run 44194991877 (job 134492768870) on the body the orchestrator's script had already refreshed.

`a3bc90e2a8ea633c69f901aced0f84ce804a7b2b` (the code head of this repair) is 948e07753393792a54faa69232562620db057365 plus one commit adding six checks to `tests/features.py` and no production line (`git diff 948e077533 a3bc90e2a8 --stat` lists that file alone). Merge base 30991a6b0d4caaf796847956ebc9977cb4656505. Measured 2026-11-17 12:22 UTC; at that time origin/main is 8f39313a44a4baec18b239ba925f6e164eb26bd2 and `git merge-tree --write-tree origin/main HEAD` reports no conflict (rc 0), so main is not merged. Since the previous body's head 0cbea8f970: 4725dffbfa and 948e077533 are `mutation-autofix` pin commits and afa6a3619b the merge-main bot's merge of origin/main 30991a6b0d. Figures other than `### Lane survivors`, the first item of `### Gate and ratchets` and `## Red checks` were taken at the earlier heads they name.

Earlier head record, as written for 0cbea8f970:

`0cbea8f970dabd8d6fae1ea44f988a16f2208a5e` merges the authored code head `e1fa50dd751679423507796b6ac938a79df7d791` and then merges origin/main `b425502da8` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0cbea8f970dabd8d6fae1ea44f988a16f2208a5e` re-keys 1 `## Unpinned sites` line(s) the main merge moved from `e1fa50dd751679423507796b6ac938a79df7d791`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/coordinator.py:5331 GUARD_OFF -> custom_components/heatpump_optimizer/coordinator.py:5337 GUARD_OFF.

e1fa50dd751679423507796b6ac938a79df7d791 (the code head; the gate, the sweeps and the hand mutants ran at 4fee736fbeccfc47be137c7093445b6ab8e0a060, whose production files are this head's: `git diff 4fee736fbe HEAD --stat -- custom_components` prints nothing), on merge base 6f422812d5d8b918beace0283419c153f6df66ce (origin/main). Measured 2026-11-16 21:21 UTC. At that time origin/main is b08346b222, and `git merge-tree --write-tree origin/main HEAD` reports no conflict (rc 0), so main is not merged; the train re-proves the head on the current main. The branch contains the repair seat's merge of origin/main 6f422812d5 (b7a77e86dd).

## Mutation proof

Failing test first. The block from `R.section("COP learner duty floor keys` to `R.section("R10-COP-GATE (#2262)` of `tests/features.py`, run by `tools/audit/seat/features_block.py` behind its `--emit-prelude` prelude, prints `ALL 110 FEATURES BLOCK PASSED` at this head. This head's `tests/features.py` on the blocked head's production files (a detached worktree at 1134fe3655) fails the check "(s) a pump drawing 2.2 kW +-15 % over 64 cycles, +-30 % over 96, or a daily plus five-day swing at phase pi ... ends at the configured scale" with every row at `(0.5, 'follows')`, fails the pending-probe hold checks, and stops at `AttributeError: 'collections.deque' object has no attribute 'dither'`. Two more failures there are not this diff's: that tree predates #3659, whose checks on `ask_evidence`'s level rule the block contains.

Hand mutants. Each was applied alone to this head's production files in a detached copy, the block run, and the file restored. The unmutated copy prints `ALL 110`. Every mutant fails at least one check; the first is named.

| mutant | failing check (first) |
|---|---|
| `coin_sign_dropped` | killed: (h) with a window that never reaches evidence the heat ask is probed, nothing folds whil ... |
| `follows_bound_strict` | killed: the verdict waits for 24 pairs, then reads follows where the mean contrast less 3 standa ... |
| `follows_bound_dropped` | killed: the verdict waits for 24 pairs, then reads follows where the mean contrast less 3 standa ... |
| `ignored_bound_strict` | killed: the verdict waits for 24 pairs, then reads follows where the mean contrast less 3 standa ... |
| `ignored_bound_dropped` | killed: the verdict waits for 24 pairs, then reads follows where the mean contrast less 3 standa ... |
| `min_pairs_dropped` | killed: a draw that ignores a varying ask is refused as off-ask, and under a flat ask it folds n ... |
| `hold_while_pending_dropped` | killed: a departure is held, and reads as awaiting evidence, only while the evidence is pending: ... |
| `hold_while_unsettled_dropped` | killed: a draw that follows the heat ask: the first row sets the base, the dither runs from the  ... |
| `return_to_base_on_follows_dropped` | killed: a draw that follows the heat ask: the first row sets the base, the dither runs from the  ... |
| `cap_never` | killed: a re-priced plan (the heat ask flat under the dither) builds no contrast and never reads ... |
| `cap_one_late` | killed: a re-priced plan (the heat ask flat under the dither) builds no contrast and never reads ... |
| `void_unstepped_pair_dropped` | killed: a re-priced plan (the heat ask flat under the dither) builds no contrast and never reads ... |
| `live_ignores_read` | killed: two admitted rows then a frozen cycle, an unread one, or one refused under the duty floo ... |
| `live_ignores_admitted` | killed: a parked probe re-arms after COP_HOLD_HORIZON_S and no sooner: 6 cycles whose last is at ... |
| `admitted_never_cleared` | killed: two admitted rows then a frozen cycle, an unread one, or one refused under the duty floo ... |
| `reset_owes_nothing` | killed: a reset mid-probe returns the scale to the base in the same cycle and folds nothing in i ... |
| `release_folds_while_waiting` | killed: release: no fold lands on a pending heat-ask probe however long it lasts -- under unobta ... |
| `release_ignores_owed` | killed: (h) with a window that never reaches evidence the heat ask is probed, nothing folds whil ... |
| `release_ignores_pending_probe` | killed: release: no fold lands on a pending heat-ask probe however long it lasts -- under unobta ... |
| `low_clamp_level_dropped` | killed: the dither's two levels are one FOLLOW_ASK_SPAN apart, centred on the base; where a cent ... |
| `high_clamp_level_dropped` | killed: the dither's two levels are one FOLLOW_ASK_SPAN apart, centred on the base; where a cent ... |
| `rearm_unknowable_wait_dropped` | killed: a parked probe re-arms after COP_HOLD_HORIZON_S and no sooner: 6 cycles whose last is at ... |
| `rearm_never` | killed: a parked probe re-arms after COP_HOLD_HORIZON_S and no sooner: 6 cycles whose last is at ... |
| `rearm_at_once` | killed: a re-priced plan (the heat ask flat under the dither) builds no contrast and never reads ... |
| `stored_base_not_loaded` | killed: a reload mid-probe returns to the base: 70 cycles in, the scale is a dither level and th ... |
| `stored_base_unclamped` | killed: a stored base loads beside a pending or absent verdict where the clamps admit it (0.5 an ... |
| `base_not_stored` | killed: a reload mid-probe returns to the base: 70 cycles in, the scale is a dither level and th ... |
| `reseed_base_dropped` | killed: (s) a probe whose first row is read at the clamp owes the configured scale (0.9) and tak ... |
| `restore_unclipped_lazy_read_dropped` | killed: (n) the restore target is the configured scale, not the default and not the walked one:  ... |
| `frozen_cycle_reads` | killed: two admitted rows then a frozen cycle, an unread one, or one refused under the duty floo ... |
| `unread_cycle_reads` | killed: two admitted rows then a frozen cycle, an unread one, or one refused under the duty floo ... |
| `owed_scale_not_applied` | killed: (h) with a window that never reaches evidence the heat ask is probed, nothing folds whil ... |
| `moved_never` | killed: (h) with a window that never reaches evidence the heat ask is probed, nothing folds whil ... |
| `parked_probe_reads` | killed: a re-priced plan (the heat ask flat under the dither) builds no contrast and never reads ... |
| `pair_order_ignores_second` | killed: (h) with a window that never reaches evidence the heat ask is probed, nothing folds whil ... |
| `ignored_restore_dropped` | killed: (h) with a window that never reaches evidence the heat ask is probed, nothing folds whil ... |
| `void_on_gap_dropped` | killed: a pair whose second row was refused is void, not stretched to the row after the gap: thr ... |
| `clamp_reseed_dropped` | killed: (s) a probe whose first row is read at the clamp owes the configured scale (0.9) and tak ... |
| `probed_state_not_verdict` | killed: release: with no window the hold empties by base's rule -- the row clearing the nameplat ... |

The design's targets are in it: the coin's sign in the contrast (`coin_sign_dropped`), both bound comparisons (four rows), the hold while pending (`hold_while_pending_dropped`, `release_folds_while_waiting`, `release_ignores_pending_probe`), the return to base (`return_to_base_on_follows_dropped`, `reset_owes_nothing`, `stored_base_not_loaded`), the cap (`cap_never`, `cap_one_late`). A first run left two alive, `ignored_bound_strict` and `void_on_gap_dropped`; each got a check (a 36-pair set whose mean plus three standard errors is 0.5 to the bit, and "a pair whose second row was refused is void, not stretched") and is killed in the table.

### Diff mutants

`tools/pr/prepr.sh` step 6 (`mutant_run.py --diff 6f422812d5...HEAD`, the first 40 mutants of the added production lines, the block driver as its command) at 4fee736fbe left 5 `SURVIVED` lines, all in `ScaleDither`:

- `DITHER_SEED = 3663` (CONST_SWAP): killed at this head by the check "a fresh dither hands out the same levels on every run", which pins the order of the first twelve pairs.
- `if base / half <= COP_SCALE_MIN:` and `if base * half >= COP_SCALE_MAX:` (CMP_BOUND): killed at this head by two added cases of "the dither's two levels are one FOLLOW_ASK_SPAN apart", the bases 0.5361902647381804 and 1.492007693184502, whose centred level lands on the clamp to the bit.
- `[(coin >= 0) != second]` (CMP_BOUND): equivalent, the coin is -1 or 1 and never 0. Triage `ScaleDither.step.CMP_BOUND.113f2cbb`.
- `... > FOLLOW_SLOPE_MIN * step:` (CMP_BOUND): equivalent, no double ratio has a logarithm equal to that product (the doubles either side of it measured with `math.nextafter`, for both coins). Triage `ScaleDither.take.CMP_BOUND.d29ee146`.

The same step at this head (e1fa50dd75, inside the prepr run that printed rc=0) leaves 2 `SURVIVED` lines, the two triaged comparisons above, and kills the other 38 it draws.

### Lane survivors

`tests / mutation` at 948e077533 refused the table: `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` printed `MUTATION TABLE REFUSED -- 2134 unpinned site(s) against 2127 at the ratchet base ..., 7 of them added by this diff`, five `ADDED UNPINNED` anchors (two hold two mutants each), the survivors of `mutation-autofix`'s pin drive. The same command in this seat, at 948e077533 against the ratchet base 30991a6b0d, printed the same five anchors. Each got a check in the block, at a3bc90e2a8. Each mutant was then applied by hand, alone, to `accuracy.py` at a3bc90e2a8, the block run (`features_block.py` behind its `--emit-prelude` prelude) and the file restored. The unmutated block prints `ALL 116 FEATURES BLOCK PASSED` both before and after the seven runs (null control); each mutant prints `1 of 116` or `2 of 116 FEATURES BLOCK FAILED`:

| site | mutant | failing check |
|---|---|---|
| `accuracy.py:989` BOOLOP | `if second or first is not None:` | "two rows taken under one first-of-pair reading make no pair ..." (a contrast 2.058 under the first-of-pair reading; `AttributeError` under the second) |
| `accuracy.py:1069` CMP_BOUND | `COP_SCALE_MIN <= row.cop_scale` | "a probe's first row read exactly at COP_SCALE_MIN or COP_SCALE_MAX ..." and the existing "(s) a probe whose first row is read at the clamp ..." |
| `accuracy.py:1069` CMP_BOUND | `row.cop_scale <= COP_SCALE_MAX` | "a probe's first row read exactly at COP_SCALE_MIN or COP_SCALE_MAX ..." (base 1.6 kept) |
| `accuracy.py:1114` CLAMP_DROP | `scale = float((configured()))` | "a due restore owes the configured scale clamped ..." (2.0 owed as 2.0) |
| `accuracy.py:1121` GUARD_OFF | `if False:` | "where no probe runs ... owes no scale and starts no dither" (`TypeError`) |
| `accuracy.py:1124` CMP_BOUND | `0.0 < utc_elapsed_seconds(...)` | "a parked probe still holds its base on the instant it parked ..." (unparked at 0 s) |
| `accuracy.py:1124` CMP_BOUND | `... < COP_HOLD_HORIZON_S` | same check (unparked at exactly 7 days) |

`ScaleProbe.owed_scale` with no base is reached in production only with `dither.admitted` false (every admitted row sets the base first), so its check builds that state directly: it pins the guard's contract, not a path a cycle walks. The added lines are under `tests/` only, so `mutant_run.py --diff` draws none of them. The pins are `mutation-autofix`'s (`ci-autofix.md`).



## Null control

- No swing: `selfset_2.2_swing0_control_s1` reads `does_not_follow` at 1.000, and so do seeds 2 to 5 of the reviewer's driver.
- The true-follow rows the pull request already pinned still latch `follows`: `heatled_true_0.68_flat_x672` 0.680, `heatled_true_0.8_flat_x672` 0.800, `heatled_true_0.68_flat_from0.5` 0.680, `heatled_true_0.45_flat_from0.5` 0.500 (its true scale is past the clamp).
- Amplitude zero (null control 1): harness rows `null_dither0_heatled_true_0.8` and `null_dither0_selfset_2.2` read pending, 0 folded, band 0.000; the `--null` sweep reads 2730 of 2730 pending; the features check "with the dither's amplitude forced to zero" pins both pumps.
- Any state but unobtainable, a measured-heat install, and no window (invariants k and l): checks (k) and (l) drive pending, follows and ignored windows with the probe admissible and not; judgements and releases are identical and the probe reads no row. In the harness every row outside the list under "Harness, three ends" prints the same line at the blocked head and here, `true_0.6_max_cycle_move=0.292` among them.
- The mutation driver's own null: the unmutated head fails no check of the block.

## Figures

<!-- figure-block: scope-line mb=1da13aafb7c23cf34fbda51bb27cb95132b4089b head=454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

### Harness, three ends

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, this head's harness file (sha1 5e1dbe0d5ec1259b82d7dd4895b771f6bde30659) on the production tree of the base 367c3b9cac, of the blocked head 1134fe3655 (detached worktrees with that file copied in) and of this head. `folded/intervals scale`, verdict (`-` at the base, which has none). 4 kW, flat asks of 1.5 kW ±2 %, open loop:

| row | base | blocked head | this head |
|---|---|---|---|
| `selfset_flat` | 0/96 1.000 | 0/96 1.000 | 0/96 1.072 |
| `held_full` | 96/96 0.582 | 47/96 1.000 | 0/96 1.000 |
| `held_filling` | 96/96 0.650 | 53/96 1.000 | 0/96 1.072 |
| `sub_min_true_0.6_x384` | 118/384 0.611 | 118/384 0.611 | 0/384 1.000 |
| `sub_min_true_0.6_x480` | 150/480 0.603 | 150/480 0.603 | 0/480 1.000 |
| `sub_min_true_0.6_x1440` | 470/1440 0.599 | 470/1440 0.599 | 0/1440 1.000 |
| `selfset_2.2_flat_x96` | 92/96 0.500 | 48/96 1.000, does_not_follow | 0/96 1.072, pending |
| `selfset_2.2_flat_x672` | 668/672 0.500 | 48/672 1.000, does_not_follow | 0/672 1.000, does_not_follow |
| `selfset_1.6_within_x672` | 672/672 0.500 | 138/672 1.000, does_not_follow | 47/672 1.000, does_not_follow |
| `selfset_1.4_within_x672` | 672/672 1.600 | 130/672 1.000, does_not_follow | 47/672 1.000, does_not_follow |
| `heatled_true_0.68_flat_x672` | 668/672 0.680 | 668/672 0.680, follows | 667/672 0.680, follows |
| `heatled_true_0.8_flat_x672` | 672/672 0.800 | 672/672 0.800, follows | 672/672 0.800, follows |
| `heatled_true_0.68_flat_max_cycle_move` | 0.241 | 0.241 | 0.308 |
| `selfset_2.2_flat_from0.5` | 668/672 0.500 | 90/672 1.000, does_not_follow | 0/672 1.000, does_not_follow |
| `selfset_1.6_within_from0.5` | 672/672 0.500 | 138/672 1.000, does_not_follow | 47/672 1.000, does_not_follow |
| `selfset_2.2_flat_from0.7` | 668/672 0.500 | 48/672 1.000, does_not_follow | 0/672 1.000, does_not_follow |
| `selfset_1.6_within_from0.7` | 672/672 0.500 | 138/672 1.000, does_not_follow | 47/672 1.000, does_not_follow |
| `heatled_true_0.45_flat_from0.5` | 672/672 0.500 | 664/672 0.500, follows | 657/672 0.500, follows |
| `heatled_true_0.68_flat_from0.5` | 0/672 0.500 | 616/672 0.680, follows | 663/672 0.680, follows |
| `selfset_2.2_flat_reload70_400` | 661/672 0.500 | 48/672 1.000, does_not_follow | 0/672 1.000, does_not_follow |
| `selfset_2.2_flat_reload70_400_lost` | 661/672 0.500 | 142/672 1.000, does_not_follow | 0/672 1.000, does_not_follow |
| `selfset_2.2_swing0.3_p2_s1` | 668/672 0.500 | 48/672 1.000, does_not_follow | 0/672 1.000, does_not_follow |
| `selfset_2.2_swing0.4_p3_s1` | 226/672 0.500 | 50/672 1.000, does_not_follow | 3/672 1.003, pending |
| `selfset_2.2_swing0.3_p4_s1` | 433/672 0.500 | 54/672 1.000, does_not_follow | 7/672 0.994, pending |
| `repriced_heat1.2_true_0.8_x672` | 377/672 0.800 | 377/672 0.800, pending | 0/672 0.933, pending |
| `null_dither0_heatled_true_0.8` | - null_dither0_selfset_2.2=- | - null_dither0_selfset_2.2=- | 0/672 1.000, pending |
| `null_dither0_selfset_2.2` | (no such row) | (no such row) | 0/672 1.000, pending |
| `held_full_heatled_true_0.8` | 96/96 0.811 | 96/96 0.811 | 96/96 0.810 |
| `held_filling_heatled_true_0.8` | 96/96 0.810 | 96/96 0.810 | 0/96 1.072 |

Rows that differ between the blocked head and this head, by rule `diff <(grep ^RESULT blocked) <(grep ^RESULT head)`: the table's rows and the 35 swing and mix rows counted under "The reviewer's rows" below; no other. `repriced_heat1.2_true_0.8_x672` is in the table: it folds 377/672 to 0.800 at the base and at the blocked head, and nothing here (the first finding under `## Forward-carry`).

### The sweep

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_scale_probe_sweep.py 3 > OUT`, then `--sum OUT`, at this head:

~~~text
RESULT heatled_scale0=0.5: wrong=0/180 latched_off_configured=0
RESULT heatled_scale0=None: wrong=0/180 latched_off_configured=0
RESULT selfset_scale0=0.5: wrong=0/15 latched_off_configured=0
RESULT selfset_scale0=0.7: wrong=0/15 latched_off_configured=0
RESULT selfset_scale0=None: wrong=0/2340 latched_off_configured=0
RESULT pending_rows=382/2730 widest_band=1.000 most_probes=1
~~~

Pending cells (740366bf). All 382 pending rows are self-setting, in swings of 2 to 16 cycles; none is heat-led. Per cell, of 20 seeds and phases, the same at 1.6, 2.2 and 3.0 kW unless a count is given: period 2 at ±15/30/40 %: 5, 10, 10; period 3 at ±30/40 %: 15 (16 at 3.0 kW), 20; period 4 at ±30/40 %: 20, 20; period 8 at ±30/40 %: 3, 20; period 16 at ±40 %: 4. A pending self-setting row keeps the scale it had when the window turned unobtainable, inside the band: final scales run 0.889 to 1.106, walked by the few intervals within `COP_ASK_TOLERANCE` that base's rule folds before then. From a persisted 0.5 or 0.7 (30 rows) none is pending: each reads `does_not_follow` at 1.000.

Null control: `... cop_scale_probe_sweep.py 3 --null > OUT`: `pending_rows=2730/2730 widest_band=0.000`.

### The reviewer's rows

In the harness run above: the 35 rows `selfset_2.2_swing*_s<seed>` and `selfset_2.2_mix*_s<seed>` (the seven rows of fix review 1, seeds 1 to 5, by `cop_duty_floor.swing`, which is the reviewer's generator). Counts of (verdict, final scale): base 35 × (`-`, 0.500); blocked head 20 × (`follows`, 0.500) and 15 × (`does_not_follow`, 1.000); this head 35 × (`does_not_follow`, 1.000). The reviewer's own three driver files, taken unchanged from the verdict commit ba984f3567 (sha1 8ff69c0a19f48cc71c3343ac4e736ca32fc10e11, 1f58778072ac944a579b517120ca3f572a6e3b30, e4eff505b7116265399ebd8264ea07dd31a23ad7) and run from this head's worktree root, are not in the tree, so their lines rest on that commit: rows, 7 of 7 `does_not_follow` at 1.000; map, 19 of 19 lines `follows=0/5`; sweep, 60 of 60 `does_not_follow` at 1.000.

### Sibling sites

Rule (the note's): `git grep -n -e "step_response(" -e "draw_response(" -e "take_restore(" -e "_admit(" -e "scale_response" -e "_apply_cop_scale(" -- custom_components`, plus `-e "owed_scale(" -e "probe.admit(" -e "probe.reset("` for the names this diff adds. Code sites at this head, definitions and docstrings apart:

- `step_response(`, `draw_response(`, `take_restore(`, `_admit(`: no site left.
- `MeasuredCop._judge_ratio` (`probe.admit`): holds while pending or unsettled. Closed here (`hold_while_pending_dropped`, `hold_while_unsettled_dropped`).
- `MeasuredCop.release` (`probe.reset`, `scale_response`): holds while pending or owed, drops what leaves. Closed here (three `release_*` mutants).
- `coordinator._fold_measured_cop` (`owed_scale`, `_apply_cop_scale(owed)`): closed here (`owed_scale_not_applied`).
- `coordinator._fold_cop_evidence` (`_apply_cop_scale(new_scale)`): the folds; reached only from the release loop and an unrefused interval, both held while pending.
- `coordinator.__init__` and the store load (`_apply_cop_scale`): the load may install a dither level; the stored base returns it (check "a reload mid-probe returns to the base").
- `accuracy.diagnostics_view` and `MeasuredCop.scale_response` (readers): value only.

### ffb019e7, stored values under the dither

Instrument: `cop_duty_floor.py`'s open loop on `selfset_2.2_flat` (672 intervals), run with the dither and with null control 1, then `coordinator._thermal_learning_payload()` compared key by key. Of 28 stored keys, 2 differ: `measured_cop` (the verdict and base themselves) and `updated_at`. That instrument drives `_learn_measured_cop` alone, so it cannot move a learner outside the COP seam. Read, not measured: `git grep -n -E "compute_cop(_dhw)?\(" -- custom_components` returns 33 sites; the learning-path ones are the counter span close (measured heat, outside admission), `flow_meter.space_reference_cop`, `MeasuredCop.residual`, `_max_pump_rise`, and `thermal_model.simulate_step`, which prices pump heat at COP × power where no heat is measured and is what the house and lower-floor fabric replays run. On an admitted install those replays therefore read the dither level of the interval they replay. No instrument in the tree drives a full learning cycle with fabric replays (`tests/features.py`'s `_df_saves` stubs them out), so which stored fabric value moves is unmeasured. Carried below.

### Gate and ratchets

- Scoped gate at a3bc90e2a8ea633c69f901aced0f84ce804a7b2b (this repair's code head): `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=30991a6b0d4caaf796847956ebc9977cb4656505 PYTHONPATH=tests/hastub ./tests/run.sh` printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` and `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, rc 0. Among them: `ALL 5870 FEATURE CHECKS PASSED`, `ALL 2731 ENTITY CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 30991a6b0d4caaf796847956ebc9977cb4656505` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. `python3 tests/structure.py` at the same head: `STRUCTURE RATCHET PASSED`, no row re-recorded. The items below are the earlier heads'.
- Scoped gate at 4fee736fbeccfc47be137c7093445b6ab8e0a060: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=6f422812d5d8b918beace0283419c153f6df66ce ./tests/run.sh` printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` and `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`. Among them: `ALL 5758 FEATURE CHECKS PASSED`, `ALL 2723 ENTITY CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s)`. Neither claim file is touched.
- The run before it, at 08f94c2d92, was red on two scripts, both this build's and both repaired in 4fee736fbe (`## Red checks`).
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, no row re-recorded by this build. `class_excess_loc` read 17512 against 17444 with the probe inside `MeasuredCop` (368 lines); paid by `ScaleProbe` and `ScaleDither` as classes of their own, no raise.
- `python3 tools/pr/ci_predict.py --base 6f422812d5d8b918beace0283419c153f6df66ce` at the head: `CI PREDICT: no closures, fast, governance or instrument red predicted`, after `--apply-inert` registered `cop_scale_probe_sweep.py` as an inert read of `tests/harness_headers.py`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS -0.0017 WORSENS (inadmissible: coord_footprint 2496->2499)`. Reason under `## Architecture score`.
- At the code head e1fa50dd75, which adds checks, two ledger triages and harness rows to 4fee736fbe and no production line: `PYTHONPATH=tests/hastub python3 tests/features.py` printed `ALL 5759 FEATURE CHECKS PASSED` and `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2723 ENTITY CHECKS PASSED`; the harness at its three ends was re-run with this head's file.

## Architecture score

- `coord_footprint` 2496 -> 2499: three coordinator logic units, two of them the first body's (the measured-heat flag and the statement at the restore site, now the owed scale). The third is `priced`, the scale read before the release loop and the owed scale move it: `CopInterval.cop_scale` is the scale the interval's draw was read under, which the pairs, the void rule and every fold from the hold depend on, and only the coordinator holds the scale at the cycle's start. Payments considered: handing the scale to `MeasuredCop.release` as an argument and reading it back for the row would hide the unit in another object's state and add a field with no other use; reconstructing it inside `ScaleProbe` from the levels it handed out fails on the three cycles where it matters most (a restore, a reset, the first cycle after a load), where the probe did not set the scale in force.

## Unpinned sites

`python3 tools/pr/ci_predict.py --base 6f422812d5d8b918beace0283419c153f6df66ce` names the added sites below, all in `custom_components/heatpump_optimizer/`. Each is left to `mutation-autofix`, whose lane mutates `custom_components/` (`ci-autofix.md`); the block driver killed the hand mutants above and the diff mutants drawn.

- custom_components/heatpump_optimizer/accuracy.py:848 CONST (`FOLLOW_BOUND_Z = 3.0`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:851 CONST (`DITHER_SEED = 3662`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:905 RETURN_DEL (`return float(self.asked_kw) * float(self.cop_scale)`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:951 CMP_BOUND (`if base / half < COP_SCALE_MIN:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:951 GUARD_OFF (`if base / half < COP_SCALE_MIN:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:953 CMP_BOUND (`if base * half > COP_SCALE_MAX:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:953 GUARD_OFF (`if base * half > COP_SCALE_MAX:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:955 RETURN_DEL (`return base / half, base * half`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:964 GUARD_OFF (`if not live:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:966 RETURN_DEL (`return base`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:968 BOOLOP (`if self.ahead is not None and not self.ahead[1]:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:968 GUARD_OFF (`if self.ahead is not None and not self.ahead[1]:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:973 RETURN_DEL (`return self.levels(base)[(coin > 0) != second]`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:985 GUARD_OFF (`if self.reading is None:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:989 BOOLOP (`if second and first is not None:`): survived the lane (`tests / mutation` at 948e077533 named it ADDED UNPINNED); killed at a3bc90e2a8 by the check "two rows taken under one first-of-pair reading make no pair" (`## Mutation proof`, "Lane survivors"); left to mutation-autofix to pin
- custom_components/heatpump_optimizer/accuracy.py:989 GUARD_OFF (`if second and first is not None:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:991 GUARD_OFF (`if coin * math.log(first.heat_ask_kw / row.heat_ask_kw) >= F`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:998 CMP_BOUND (`if 2 * len(self.contrasts) < MIN_SAMPLES:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:998 GUARD_OFF (`if 2 * len(self.contrasts) < MIN_SAMPLES:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1002 CMP_BOUND (`if mean - bound >= FOLLOW_SLOPE_MIN:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1002 GUARD_OFF (`if mean - bound >= FOLLOW_SLOPE_MIN:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1004 CMP_BOUND (`return ASK_IGNORED if mean + bound <= FOLLOW_SLOPE_MIN else`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1004 RETURN_DEL (`return ASK_IGNORED if mean + bound <= FOLLOW_SLOPE_MIN else`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1052 RETURN_DEL (`return self.moved or self.owed is not None`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1066 GUARD_OFF (`if self.response != ASK_PENDING or self.restore_due:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1068 GUARD_OFF (`if self.base is None:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1069 BOOLOP (`if not self.reseeded and not COP_SCALE_MIN < row.cop_scale <`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1069 CMP_BOUND*2 (`if not self.reseeded and not COP_SCALE_MIN < row.cop_scale <`): survived the lane (`tests / mutation` at 948e077533 named it ADDED UNPINNED); killed at a3bc90e2a8 by the check "a probe's first row read exactly at COP_SCALE_MIN or COP_SCALE_MAX" (`## Mutation proof`, "Lane survivors"); left to mutation-autofix to pin
- custom_components/heatpump_optimizer/accuracy.py:1069 GUARD_OFF (`if not self.reseeded and not COP_SCALE_MIN < row.cop_scale <`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1071 RETURN_DEL (`return ASK_PENDING`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1073 GUARD_OFF (`if self.parked_at is not None:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1077 GUARD_OFF (`if self.response == ASK_PENDING:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1078 CMP_BOUND (`if self.dither.rows < WINDOW:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1078 GUARD_OFF (`if self.dither.rows < WINDOW:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1081 GUARD_OFF (`elif self.response == ASK_FOLLOWS:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1086 RETURN_DEL (`return self.response`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1103 BOOLOP (`live = self.dither.admitted and read`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1106 BOOLOP (`self.moved = want is not None and want != self.level`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1108 RETURN_DEL (`return want if self.moved else None`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1112 GUARD_OFF (`if self.restore_due:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1114 CLAMP_DROP (`scale = float(np.clip(configured(), COP_SCALE_MIN, COP_SCALE`): survived the lane (`tests / mutation` at 948e077533 named it ADDED UNPINNED); killed at a3bc90e2a8 by the check "a due restore owes the configured scale clamped" (`## Mutation proof`, "Lane survivors"); left to mutation-autofix to pin
- custom_components/heatpump_optimizer/accuracy.py:1115 GUARD_OFF (`if self.response == ASK_PENDING:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1117 RETURN_DEL (`return scale`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1118 GUARD_OFF (`if self.owed is not None:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1120 RETURN_DEL (`return want`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1121 GUARD_OFF (`if self.base is None:`): survived the lane (`tests / mutation` at 948e077533 named it ADDED UNPINNED); killed at a3bc90e2a8 by the check "where no probe runs (no base, no restore, nothing owed)" (`## Mutation proof`, "Lane survivors"); left to mutation-autofix to pin
- custom_components/heatpump_optimizer/accuracy.py:1123 GUARD_OFF (`if self.parked_at is not None:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1124 CMP_BOUND*2 (`if 0.0 <= utc_elapsed_seconds(now, self.parked_at) <= COP_HO`): survived the lane (`tests / mutation` at 948e077533 named it ADDED UNPINNED); killed at a3bc90e2a8 by the check "a parked probe still holds its base on the instant it parked" (`## Mutation proof`, "Lane survivors"); left to mutation-autofix to pin
- custom_components/heatpump_optimizer/accuracy.py:1124 GUARD_OFF (`if 0.0 <= utc_elapsed_seconds(now, self.parked_at) <= COP_HO`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1127 RETURN_DEL (`return self.dither.step(self.base, live)`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1137 BOOLOP (`self.restore_due = self.restore_due and not measured_heat`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1141 RETURN_DEL (`return {"scale_response": self.response, "scale_base": self.`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1157 BOOLOP (`if isinstance(response, str) and response in (ASK_FOLLOWS, A`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1157 GUARD_OFF (`if isinstance(response, str) and response in (ASK_FOLLOWS, A`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1159 GUARD_OFF (`elif isinstance(raw, dict):`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1161 BOOLOP (`probe.base = base if base is not None and COP_SCALE_MIN <= b`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1161 CMP_BOUND*2 (`probe.base = base if base is not None and COP_SCALE_MIN <= b`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1162 RETURN_DEL (`return probe`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1218 RETURN_DEL (`return self.probe.response`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1257 RETURN_DEL (`return self.probe.owed_scale(configured, now, self.refusal n`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1302 GUARD_OFF (`if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1311 GUARD_OFF (`if verdict == ASK_IGNORED:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1313 GUARD_OFF (`if verdict == ASK_PENDING or self.probe.unsettled:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1316 GUARD_OFF (`if verdict == ASK_FOLLOWS:`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1322 RETURN_DEL (`return COP_REFUSED_NO_EVIDENCE`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1352 GUARD_OFF (`if probed := self._admits(state, draw, measured_heat):`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1356 BOOLOP (`if waits := self.probe.owed is not None or (probed and state`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1356 GUARD_OFF (`if waits := self.probe.owed is not None or (probed and state`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1370 BOOLOP (`return [r for r in rows if not waits and self._base_folds(r,`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1370 RETURN_DEL (`return [r for r in rows if not waits and self._base_folds(r,`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/accuracy.py:1397 RETURN_DEL (`return {"cop": self.cop, "curve_dhw": self.curve_dhw, "dhw_t`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`
- custom_components/heatpump_optimizer/coordinator.py:5337 GUARD_OFF (`if (owed := self._measured_cop.owed_scale(lambda: ctx._confi`): left to mutation-autofix; the block driver kills the hand and diff mutants of `## Mutation proof`

- custom_components/heatpump_optimizer/accuracy.py:973 CMP_BOUND (`return self.levels(base)[(coin > 0) != second]`): equivalent, the coin is -1 or 1; triage `tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.step.CMP_BOUND.113f2cbb.json`
- custom_components/heatpump_optimizer/accuracy.py:991 CMP_BOUND (`if coin * math.log(first.heat_ask_kw / row.heat_ask_kw) >= FOLLOW_SLOPE_MIN * step:`): equivalent, no double ratio reaches the bound; triage `tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.take.CMP_BOUND.d29ee146.json`
- The ledger: main's `killed_by/draw_range.py` pins are restored with main's file (`git diff origin/main HEAD -- tests/mutation_ledger/killed_by/draw_range.py` prints nothing); the 14 `killed_by` pins on lines this build rewrote in `accuracy.py` and `coordinator.py` are deleted (`ci_predict.py` printed each as `STALE PIN`; it prints none now). The equivalence triage `MeasuredCop._judge_ratio.CMP_BOUND.9d967a75` keeps its line unchanged.

## Red checks

Reds at 454d4fc425 (fix review 3, `Fix review: blocked 9894911a81` red-check), each name in `merge_train.py owed-reds` answered:

- `pr-contract / pr-contract`, red at 9894911a81 (run 44147689564) and at 454d4fc425 in run 44195004151 (job 134492004930): the body's `scope-line` figure block named head f52f265d5b / mb 30991a6b0d after the bot's main merges. Green at 454d4fc425 in run 44194991877 once the block was re-rendered; re-rendered again by this body. Cheaper detector: `figure_block.py verify`, which `tools/pr/prepr.sh`'s body check runs in seconds; the red arose because a main merge by the bot moves head and mb after the handoff without re-rendering the body; the live body at 454d4fc425 was re-rendered by the orchestrator's script without a push, and `body_push.sh` renders the block at every handoff. No further countermeasure here.
- `gate`: red at 9894911a81 because pr-contract was; red at 454d4fc425 in run 44196634218 only on `budget-raise-gate / budget-raise-gate: cancelled (this run)`. No cause of its own.
- `budget-raise-gate / budget-raise-gate`, cancelled at 454d4fc425 in run 44196634218 (job 134495994646, 5 min); green at the same head in runs 44194991877 and 44195004151. A cancellation, not a defect: re-run. The diff only lowers `tests/structure_budgets.json` (no raise).
- `tests / nightly-status` and `tests / replay`, red at 454d4fc425 in run 44194991877, are outside `merge_train.py owed-reds`: not answered.

Earlier record, as written for 948e077533:

Reds on this pull request's commits (pr-contract's `red-history` over the 41 commits between origin/main and 948e077533), each name in `merge_train.py owed-reds` answered:

- `tests / mutation`, red at 948e077533 (run 44051675045): `MUTATION TABLE REFUSED`, 7 sites this diff added that `mutation-autofix` could not kill. Repaired at a3bc90e2a8: a check for each, every mutant killed by hand (`### Lane survivors`); the lane pins them on its next pass. Cheaper detector: `prepr.sh` step 6's `mutant_run.py --diff` ran at e1fa50dd75 but draws only the first 40 mutants of the added lines, so these seven were past its cap. The detector that names exactly "no driver the lane runs kills this site" is the lane itself, at its standing cost; none cheaper exists, so no countermeasure.
- `gate`: red at 948e077533 because `tests / mutation` and `pr-contract / pr-contract` were; no cause of its own.
- `pr-contract / pr-contract`, red at 948e077533: the body did not name `governance / env-matrix` or `governance / policy-docs`, and its figure block named 0cbea8f970. Both answered in this body; the block is re-rendered at this head (`figure_block.py refresh`). Cheaper detector: `tools/pr/prepr.sh`'s body check, which runs it before the handoff; this repair ran it (`prepr:` line above).
- `governance / policy-docs` and `governance / env-matrix`, red at 4725dffbfa only (run 44002181411, jobs 133824863879 and 133824864097): `ERROR [budgets] tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md` "has a cap in dev/governance/config/policy_budgets.json's files_tokens but is matched by no POLICY_GLOBS pattern"; env-matrix's `policy_lint` lanes failed on the same two errors. Inherited from main: the caps came in with 0cbea8f970's merge of origin/main b425502da8 (`git show 4725dffbfa:dev/governance/config/policy_budgets.json` names both files, `git show afa6a3619b:dev/governance/config/policy_budgets.json` neither); this diff touches none of those files (`git diff 30991a6b0d...HEAD -- dev/governance/config/ tools/audit/briefs tools/audit/harnesses` prints nothing); both checks are green at afa6a3619b and 948e077533, after the merge of main's repair. The cause is main's, not this branch's: no countermeasure here.
- `governance / instrument-self-tests`, red at 948e077533 on `selftest_scope` (step "Refuse a self-test read set the committed table misses"): inherited, main carries the same red (`tools/ci/selftest_closures.json` misses reads added by recent merges; the re-record hotfix is main's), and `merge_train.py classify 948e077533 --pr 3662` prints no INTRODUCED line. Not repaired here.
- `tests / nightly-status` and `tests / replay`, red at 948e077533, are outside `merge_train.py owed-reds`: not answered.

## Forward-carry

- A heat-led install whose admitted intervals are never consecutive never decides. Its measurement lands in `dev/audit/harnesses/cop_duty_floor.py` (rows `sub_min_true_0.6_*`, stated in its docstring); the finding routes to this group on the round-11 roster on handoff/audit-r10-roster, which this seat does not write. `sub_min_true_0.6_x1440` (min == max == 3 kW, asks 1.9 to 2.55 kW, two in three under the duty floor): 0/1440 folded, pending, 1 probe, where the base and the blocked head fold 470/1440 and end at 0.599. Mechanism: the note's rule "a refused or frozen cycle between them voids the pair", with the scale back at the base after a cycle that admits no row, leaves every admitted row read at the base. Control: the same pump uninterrupted latches `follows` on its 50th row (check "a draw that follows the heat ask"). It is the note's follow-up item "tuning the dither", which has no roster group (the design verdict routed that to the orchestrator). A fix must re-measure `sub_min_true_0.6_*` and the gap checks at its own merge base. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- A heat-led pump under a plan that re-prices its ask against the scale stops learning and restarts the probe without end: `repriced_heat1.2_true_0.8_x672` (same harness file) starts 56 probes, folds 0 and stays pending, inside the band, where the base and the blocked head fold 377/672 and end at the true 0.800. The dither moves the asks by its own step, the window's evidence turns obtainable, the probe resets, the asks go flat again. No cap counts across resets. Control: the same row with the ask pinned (`heatled_true_0.8_flat_x672`) reads `follows`, 1 probe. The note names this as the follow-up's first item (a closed-loop harness). Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- ffb019e7: on an admitted install the fabric replays (`thermal_model.simulate_step` through `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss`) price pump heat at the dither level of the interval they replay; read from the code, unmeasured for want of a full-cycle instrument (`## Figures`). The measurement belongs to the closed-loop harness of the note's follow-up; what it must separate is a stored fabric value under the dither against null control 1 (`ScaleDither.levels` returning the base twice). Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- Fix review 1's finding on the defrost carry (item 0116e1a6 of R11-INTAKE-R10-RESIDUE): the control it asks for now exists at this head. The reviewer's swing rows read `does_not_follow`, and the harness's `selfset_2.2_swing*` rows are that control in the tree. `defrost_inferred_*` are identical at all three ends. Carry: R11-INTAKE-R10-RESIDUE
- Residual: on the cycle the hold folds, the cycle's own interval folds against the scale the hold just moved, as base's release does (`true_0.6` shows it at every end). `heatled_true_0.68_flat_max_cycle_move` reads 0.308 here against 0.241 at both earlier ends. Carry: dismissed: the owner's carry 3 ruling (2026-11-16) accepts an unbounded release as a residual
- Residual: the park and the pairs are not stored, so a restart mid-probe or mid-park starts the probe over (`selfset_2.2_flat_reload70_400` still reads `does_not_follow` at 1.000). Carry: dismissed: the note stores one key, the base
- The first body's residuals on carries 3 and 4 and on the configured-scale restore stand as written there. Carry: dismissed: owner ruling 2026-11-16 accepts both as residuals

## Friction

- seat-brief: stale: the brief names `DESIGN.md` at the design tip; the file there is `design.md`, and `git show <tip>:DESIGN.md` fails. Carry: dismissed: a one-off dispatch text, the file was found by listing the tree
- seat-brief: cost: `multiprocessing` starts workers by forkserver on this interpreter (3.14), so a pool worker does not see flags the parent parsed after truncating `sys.argv`; the first `--null` sweep ran un-nulled and was discarded. The committed sweep hands the flag to its workers. Carry: dismissed: repaired in the instrument this pull request lands

