R11-OUTSIDE-SELF-SETTING-PUMP, built on the approved design (`design.md` at b31718e61835180b4062ae882da0615e1d6e819f of design/R11-OUTSIDE-SELF-SETTING-PUMP; `Design review: approve b31718e61835180b4062ae882da0615e1d6e819f`, design-verdict at c875d70e1a). Owner ruling D4 (tvofi, 2026-11-15): the self-setting pump residual of #3593 is designed and fixed, not accepted as a known limit. `Carry N` below is entry N (0-based) of this group's `carry` list on handoff/audit-r10-roster at 3b6de29be6.

Owner ruling on the decisions the design routed (tvofi, 2026-11-16, verbatim choices): the clamp remedy, "A: re-seed at clamp"; carries 3 and 4, "Accept both". Orchestrator rulings on departures 1 and 2: both taken as the design states them (the release and the restore run behind the freeze gate; a replay does not feed the capacity envelope).

By carry:

- **Carry 0** (owner ruling D4, the self-setting pump residual of #3593): built, as "What ships" below. Harness rows under `## Figures`.
- **Carry 1** (departure 1, the release behind the freeze gate): kept and extended to the restore, as the orchestrator ruled. Control: the mutant "the restore above the `_learning_frozen` gate" fails check (o), and the R10 check "a frozen cycle and one with no power reading release nothing and fold nothing; the next live cycle releases the held interval" passes at the head (`## Mutation proof`).
- **Carry 2** (departure 2, a replay does not feed the capacity envelope): kept, not owed, as the orchestrator ruled. Its control "a replayed interval folds the scale and not the capacity envelope; the same evidence folded live feeds the envelope (control)" passes at the head, inside `ALL 5736 FEATURE CHECKS PASSED`.
- **Carry 3** (a release bounded per cycle) and **Carry 4** (the overstated-minimum floor): not built; the owner ruled "Accept both". Each is stated as a residual under `## Forward-carry`. Carry: dismissed: owner ruling 2026-11-16 accepts both as residuals

What ships:

- **The probe.** `MeasuredCop` in `accuracy.py` admits an interval when `draw_range.ask_evidence` reads `ASK_UNOBTAINABLE`, a window exists, and the install has no measured heat (`probe_install(config).measured_heat`, passed by `_fold_measured_cop` to `release` and `judge_ratio`). An admitted row adds (drawn kW, heat ask = `asked_kw × cop_scale`) to `MeasuredCop.probe`, which is bounded at `draw_range.WINDOW`. Once `MIN_SAMPLES` rows have heat asks that span `FOLLOW_ASK_SPAN`, `draw_range.draw_response` latches `scale_response`. That is `ask_evidence`'s own slope rule, split out of it so both read one function; `ask_evidence` stays bit-identical. Under `ASK_FOLLOWS` every admitted interval folds. Under `ASK_IGNORED` every interval reads `COP_REFUSED_OFF_ASK`, and the restore falls due. While pending, an admitted row keeps base's outcome.
- **Reset first.** `release` reads the state before anything else. Where admission does not hold, it clears the probe, the verdict and the re-seed flag, and its existing arms run unchanged. Where admission holds, it admits every held row and then judges once: none fold under ignored, all fold under follows, and base's rule applies while pending.
- **The restore.** Right after the release loop in `_fold_measured_cop`, past the `_learning_frozen` gate, `if self._measured_cop.take_restore(): self._apply_cop_scale(ctx._config.cop_scale)` runs. The target is the configured scale.
- **The clamp, remedy A.** If the first row of a probe was read at `COP_SCALE_MIN` or `COP_SCALE_MAX`, no row is kept, the restore falls due, and the probe starts again from the configured scale. This happens once per reset (`MeasuredCop.reseeded`), so a configured scale at a clamp keeps base's rule.
- **Persistence.** `MeasuredCop.as_dict` gains `scale_response`, and `store.py` registers `measured_cop/scale_response` as a choice domain. `from_dict` reads the verdict separately from the measurement. An absent or unreadable verdict loads as pending and keeps the COP. A stored `does_not_follow` loads with the restore due, which closes the save-between-latch-and-restore window (verdict item a62de31a). The probe rows and flags are not persisted. `accuracy.diagnostics_view` publishes `scale_response`.
- **Verdict item 8d483cf3, the order.** A reset clears the verdict, not the debt: a restore that is due survives a reset by a window that has evidence, and is paid on that same cycle. It does not survive measured heat, because heat-measured folds are not this ratio's.
- **Payments.** The ratio refusal's `_LOGGER.debug` moved from `_fold_measured_cop` into `MeasuredCop.judge_ratio`, where the refusal is decided (the design's candidate, item 5e1c2a90). The no-draw case of the duty floor moved into `MeasuredCop.judge_floor`, which owns the floor: `drawn_kw` None returns None.

Departures from the note, disclosed for the reviewer:

1. `draw_range.py` is touched. The note reads it unchanged; here `ask_evidence`'s span and slope lines move into `draw_range.draw_response`, which the probe calls, so the rule exists once and not as a copy in `accuracy.py`. `ask_evidence` returns what it did: every harness row reading the window's evidence (`selfmod_*`, `selfset_*` of #3593, `p4_*`, `true_*`) prints the same line at both ends.
2. Measured heat resets the probe and drops a due restore. The note resets only on "any state but unobtainable". An install that gains a thermal entity or heat counter after a latched ignored would otherwise load a stored ignored with the restore due and undo heat-measured folds. The check "(l) an install with a thermal power entity reading no heat probes nothing" and the mutant "measured-heat guard" pin this route.
3. `judge_floor` takes a `None` draw. That is the payment for `functions_cc_over_15`, under `## Figures`, "Gate and ratchets".

One existing check changed its expectation: "(h) with a window that never reaches evidence every interval base folds is folded". Its 2.6 kW-asked, 3.2 kW-drawn rows are a self-setting pump, so the design moves them (`held_full`, `held_filling`). (h) now pins its own claim on the design's control, heat-led twins of true 0.8 (96 of 96 behind both windows, 40 of 40 still held part-way), and pins the self-setting rows at the configured scale with `does_not_follow`.

## Head

1787779ba56897cbafacb7194a6bf3b5f073cfa3, on merge base 31255c328918573ef29007dac22d7184a0f0247c (origin/main at the cut). Measured 2026-11-16 09:55 UTC. At that time origin/main is 030a4d377f9f26f5b8befe5721d86aea454f29e0, and `git merge-tree --write-tree origin/main HEAD` reports no conflict (rc 0), so main is not merged; the train re-proves the head on the current main.

## Mutation proof

Failing test first. The block from `R.section("COP learner duty floor keys` to `R.section("R10-COP-GATE (#2262)` of `tests/features.py`, run by `tools/audit/seat/features_block.py` behind its `--emit-prelude` prelude, stops at `AttributeError: 'MeasuredCop' object has no attribute 'scale_response'` on the base's production files and prints `ALL 85 FEATURES BLOCK PASSED` on this head. Behaviourally, the harness rows under `## Figures` read the defect at the base.

Hand mutants. Each was applied by hand, alone, to the production files of e3769873a0 (whose production code is this head's, apart from the two lines named under "Diff mutants" below), driven by that block, and restored. The unmutated tree prints `ALL 85` there and `ALL 88` at this head. Every mutant fails at least one check. The first failing check is named.

| mutant | failing check (first) |
|---|---|
| admission state guard: `state == ASK_UNOBTAINABLE` to `state != ASK_IGNORED` | (k) under pending, follows and ignored evidence the probe admits nothing |
| admission window guard: `draw is not None` dropped | (l) with measured heat, or with no window, 60 flat departures ... read base's rule |
| admission measured-heat guard: `not measured_heat` dropped | (l) an install with a thermal power entity reading no heat probes nothing |
| `_admit`: `MIN_SAMPLES` to 2 | release: where the evidence is unobtainable the hold empties by base's rule |
| `_admit`: the span refusal dropped (latches on an unspanned probe) | (n) a pump drawing 2.2 kW whatever is asked ... ends at the configured scale |
| `release`: reset before admit dropped | (p) the verdict holds over 200 more flat cycles ...; a reset ... clears the verdict and the probe |
| `judge_ratio`: a latched verdict folds (`return None`) | (h) ... the fixed 3.2 kW draw latches does_not_follow and ends at the configured scale |
| `release`: the latched verdict not applied before return | a release under unobtainable evidence folds nothing once the draw ignores the heat ask |
| restore target: `self._cop_scale` for the configured scale | (n) ... ends at the configured scale |
| the restore above the `_learning_frozen` gate | (o) a latched ignored restores the configured scale on the next unfrozen cycle only |
| clamp re-seed (remedy A) dropped | (s) a probe seeded at the clamp re-seeds once ...; true 0.68 from a persisted 0.500 reaches 0.680 |
| re-seed once: the `reseeded` guard dropped | (s) |
| reset clears a due restore | (p) ... a restore already due is still paid |
| `from_dict`: a stored ignored loads with no restore due | (p) a reload between the latch and the next cycle keeps ignored and the restore it owes |
| `from_dict`: the verdict not read | (p) a reload between the latch and the next cycle keeps ignored ... |
| `from_dict`: any non-None stored value read as the verdict | (q) an unreadable or absent stored verdict loads pending beside the measured COP |

That is 16 mutants. A first run left "`release`: the latched verdict not applied before return" alive. The check "a release under unobtainable evidence folds nothing once the draw ignores the heat ask, every row once it follows, and base's rule while pending" was added before the first commit, and the same driver now kills it.

Departure 1's control, re-run here: the mutant "the restore above the `_learning_frozen` gate" fails (o). The R10 check "a frozen cycle and one with no power reading release nothing and fold nothing; the next live cycle releases the held interval" passes at the head.

### Diff mutants

`python3 -I tools/audit/seat/mutant_run.py --diff 31255c3289...5ea07c1b63 --cmd <driver> --max-mutants 100 --report-only` drew every mutant `--list` generates on the diff's added production lines (56 at 5ea07c1b63; `MUTANT_MAX` lifted so that none past 40 goes undrawn). The driver emits the prelude from the tree it runs on (`features_block.py --emit-prelude`), runs the block above, and exits 1 on any failure. It printed rc 0 and two `SURVIVED` lines:

- `accuracy.py` `release`, `self.restore_due = self.restore_due and not measured_heat` STMT_DEL. Killed at this head by the check "measured heat drops a restore a stored does_not_follow made due: the scale stays 0.7, and the verdict resets" (block reads `1 of 88 FEATURES BLOCK FAILED` on the mutant).
- `draw_range.py` `draw_response`, `.reshape(-1, 2)` to `.reshape(-2, 2)` CONST_SWAP. Both callers already hand (n, 2) rows, so the reshape was a no-op. It is deleted at this head rather than pinned: `--list` draws 55 there, and the harness output is byte-identical with and without it (`diff` printed nothing, then `HARNESS_UNCHANGED_BY_RESHAPE_REMOVAL`).

An earlier run, stopped at the session's 30-minute background limit, had printed two other survivors. Both are killed in e3769873a0: `_admit`'s `len(self.probe) >= MIN_SAMPLES` to `>` by "the heat-ask verdict waits for 48 admitted rows (draw_range.MIN_SAMPLES) and latches on the 48th", and `judge_ratio`'s `if refusal is not None:` to `if False:` by "judge_ratio logs a refusal with its code and the interval, and a fold not at all". Each was applied by hand and reads `1 of 87 FEATURES BLOCK FAILED`.

## Null control

- Harness: `diff` of the base and head outputs of `dev/audit/harnesses/cop_duty_floor.py` (both runs from the head's harness file) lists the R11 rows, which are new in this diff, plus `held_full` and `held_filling`, the two the design names as moving. Every row #3593 shipped prints the same line otherwise. That includes carry 3's `true_0.6_max_cycle_move=0.292` and carry 4's `min3_running_warm_own_folded=3/15`, `fixed3_duty50_warm_own=0/5_scale=1.000` and `fixed3_duty70_warm_own=0/5_scale=1.000`.
- The harness extension alone, on the base's production files: the rows that existed before this diff print byte-identically under the base's harness file and under the head's (`diff <(grep -v <new rows> new) <(grep RESULT old) && echo HARNESS_OLD_ROWS_IDENTICAL` printed `HARNESS_OLD_ROWS_IDENTICAL`).
- The heat-led twins of the `held_*` rows read `held_full_heatled_true_0.8=96/96_scale=0.811` and `held_filling_heatled_true_0.8=96/96_scale=0.810` at both ends. A heat-led pump behind those windows is unchanged.
- Admission off: check (k) drives pending, follows and ignored windows with the probe admissible and not admissible. Judgements and releases are identical and the probe stays empty.
- The mutation driver's own null: the unmutated head fails no check of the block.

## Figures

<!-- figure-block: scope-line mb=31255c328918573ef29007dac22d7184a0f0247c head=1787779ba56897cbafacb7194a6bf3b5f073cfa3 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

### Harness, both ends

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`. The head's harness file (sha1 09e6f53dfaf95ef5d961eff047b002f96c93784b) ran on the base's production tree (a detached worktree at merge base 31255c3289 with that file copied in) and at the head. The rows that differ, `folded/intervals scale`, with the lowest and highest scale, the cycles off 1.000 by more than 5 %, and the verdict (`-` at the base, which has none). All rows use 4 kW, flat asks of 1.5 kW ±2 %, 672 intervals unless named, and are open loop:

| row | base | head |
|---|---|---|
| `selfset_2.2_flat_x96` | 92/96 0.500, 49 off | 48/96 1.000, lowest 0.730, 6 off, does_not_follow |
| `selfset_2.2_flat_x672` | 668/672 0.500, 625 off | 48/672 1.000, lowest 0.730, 6 off, does_not_follow |
| `selfset_1.6_within_x672` | 672/672 0.500, 644 off | 138/672 1.000, lowest 0.766, 111 off, does_not_follow |
| `selfset_1.4_within_x672` | 672/672 1.600, 651 off | 130/672 1.000, highest 1.311, 110 off, does_not_follow |
| `heatled_true_0.68_flat_x672` | 668/672 0.680 | 668/672 0.680, follows |
| `heatled_true_0.8_flat_x672` | 672/672 0.800 | 672/672 0.800, follows |
| `selfset_2.2_flat_from0.5` | 668/672 0.500, 672 off | 90/672 1.000, 90 off, does_not_follow |
| `selfset_1.6_within_from0.5` | 672/672 0.500, 672 off | 138/672 1.000, 111 off, does_not_follow |
| `selfset_2.2_flat_from0.7` | 668/672 0.500, 672 off | 48/672 1.000, lowest 0.511, 53 off, does_not_follow |
| `selfset_1.6_within_from0.7` | 672/672 0.500, 672 off | 138/672 1.000, lowest 0.537, 139 off, does_not_follow |
| `heatled_true_0.45_flat_from0.5` | 672/672 0.500 | 664/672 0.500, highest 0.997, follows |
| `heatled_true_0.68_flat_from0.5` | 0/672 0.500 | 616/672 0.680, follows |
| `selfset_2.2_flat_reload70_400` | 661/672 0.500 | 48/672 1.000, lowest 0.730, 6 off, does_not_follow |
| `selfset_2.2_flat_reload70_400_lost` | 661/672 0.500 | 142/672 1.000, lowest 0.636, 92 off, does_not_follow |
| `held_full` | 96/96 0.582 | 47/96 1.000 |
| `held_filling` | 96/96 0.650 | 53/96 1.000 |

- `heatled_true_0.45_flat_from0.5` is remedy A's cost, which the owner ruled for. It is a heat-led pump whose true scale is past the clamp: re-seeded to the configured scale, it walks back to 0.500 and passes through 0.997. `heatled_true_0.68_flat_from0.5` is A's gain: base never folds its 1.1 kW draw (under the 1.33 kW nameplate third) and stays at the clamp.
- `_reload70_400_lost` is the cost the stored key saves. Without it, each reload re-probes and the scale walks again (lowest 0.636 against 0.730).
- The design's spike figures agree with these to the third decimal, except two. `heatled_true_0.68_flat_x672` ends 0.680 against the note's 0.679, and the lost-verdict row folds 142 against the note's 95: the harness seeds its noise differently from the designer's scratch spike. The head's harness is the instrument.
- Re-seeds across a reset (verdict item 7aa61215): one per reset, not one per install. Check (s) drives a clamp row twice, resets, and drives it twice again. It reads `[(0, True), (1, False), (0, True), (1, False)]`: (probe length, restore taken) per row, so the first row of each probe life re-seeds and the second is kept. In the harness runs no reset happens, so `heatled_true_0.45_flat_from0.5` re-seeds once in 672 cycles.

### Sibling sites

The rule is the design's, extended by the two names this diff adds: `git grep -n -e "ask_evidence(" -e _base_folds -e "_measured_cop.release(" -e "judge_ratio(" -e ASK_UNOBTAINABLE -e "_apply_cop_scale(" -e "_config.cop_scale" -e "draw_response(" -e "judge_floor(" HEAD -- custom_components`. Code sites at this head (definitions and docstrings apart), each with its disposition:

- `MeasuredCop._admits` and `_admit` (`ASK_UNOBTAINABLE`, `draw_response`): closed in this diff (admission and span mutants).
- `MeasuredCop._judge_ratio`, which reads `ask_evidence` and `_base_folds`: closed in this diff (latch mutant, (k), (l)).
- `MeasuredCop.release`, which reads `ask_evidence` and `_base_folds`: closed in this diff (reset and release mutants, (r)).
- `draw_range.ask_evidence`, which calls `draw_response`: unchanged in value, and the #3593 harness rows are identical at both ends.
- `draw_range.follows_ask`, which reads `ask_evidence`: value unchanged (the note's out-of-scope list).
- `coordinator._fold_measured_cop`: the release loop, `take_restore` with `_apply_cop_scale(ctx._config.cop_scale)`, `judge_floor` and `judge_ratio`, all closed in this diff ((n), (o), the restore mutants, and (l) for the flag).
- `coordinator._fold_cop_evidence`'s `_apply_cop_scale(new_scale)`: these are the folds the restore undoes. Covered by (n) and (p).
- `coordinator._async_learn_heat_span`'s `judge_floor(close.asked_kw, close.elec_kw, ...)` (span close, measured heat): `elec_kw` is a float there and its guard `coord._measured_power is not None` is unchanged. Already guarded, and outside admission (measured heat).
- `coordinator.__init__`'s read of `_config.cop_scale` and its `_apply_cop_scale(self._cop_scale)`: out of scope as the note states (nothing judged). Its value is the restore target.

### Verdict item e98d0ab9, the defrost derate's inferred estimator

Measured, unchanged by this diff, routed under `## Forward-carry`. The instrument is the harness's `defrost_inferred_*` rows (`derate()` in `dev/audit/harnesses/cop_duty_floor.py`). They run the real `_settle_defrost` with no defrost flag (window unobserved) on cop_duty_floor.py's model, at 4 kW with flat asks of 1.5 kW ±2 %, for 96 intervals:

- `defrost_inferred_selfset_2.2_2C=factor=0.684_count=96` (self-setting 2.2 kW ±3 %, frost band). Control, draw equal to the ask: `defrost_inferred_matched_2C=factor=1.000_count=96`. Outside the band, `defrost_inferred_*_8C` reads `count=0` for both. All four lines are identical at the base and the head.
- The estimator reads ask over draw (`accuracy.delivered_ratio`), so on a pump that sets its own power it learns a frost derate of 0.684 where there is no frost. That is the same mechanism this PR closes for the COP scale, in the defrost seam. The fix leaves `_settle_defrost` untouched, so base and head read alike.

### Gate and ratchets

- Scoped gate at 5ea07c1b63: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=31255c328918573ef29007dac22d7184a0f0247c ./tests/run.sh` printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` and `1 TEST SCRIPT(S) FAILED`, rc 1. Among the rest: `ALL 5735 FEATURE CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`, `STRUCTURE RATCHET PASSED`.
  - The one failure is `tests/entities.py`, `1 of 2723 ENTITY CHECKS FAILED`, on "orchestrator_tick.py --self-test passes (it reads roster_lib's closed set)". It is inherited, not this diff's: `python3 tools/audit/seat/orchestrator_tick.py --self-test` stops with `NameError: name 'SEAT_WINDOW_MIN' is not defined` (`outside_chain_idle`) both at the merge base 31255c3289 (a detached worktree) and at this head, and this diff touches nothing under `tools/`.
  - The first gate run, at 312380fc2c, failed one more `tests/entities.py` check: "and every mark still names a mutant this tree generates, pin and all (#1217)", stale `MeasuredCop.judge_ratio CMP_BOUND 9d967a75`. 5ea07c1b63 repairs it, under `## Red checks`.
- Since 5ea07c1b63, only `tests/features.py` and `draw_range.draw_response`'s reshape have changed: `git diff --stat 5ea07c1b63 HEAD` lists `custom_components/heatpump_optimizer/draw_range.py` and `tests/features.py`. At this head, `PYTHONPATH=tests/hastub python3 tests/features.py` printed `ALL 5736 FEATURE CHECKS PASSED`, and the harness and `tests/structure.py` were re-run (above, and `STRUCTURE RATCHET PASSED`).
- `python3 tools/pr/ci_predict.py --base 31255c328918573ef29007dac22d7184a0f0247c` at this head: `CI PREDICT: no closures, fast, governance or instrument red predicted against 31255c328918`, with no `STALE PIN` line.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`. Two rows moved down and are re-recorded in fdbf2db2ab: `max_class_loc` 7885 to 7883 and `class_excess_loc` 17446 to 17444. They moved because the debug log left the coordinator class (`git diff 31255c3289...HEAD -- tests/structure_budgets.json` holds those two and `recorded_at`). `functions_cc_over_15` read 27 against 26 with the restore's `if` in `_fold_measured_cop` (cc 15 to 16). It is paid by moving the no-draw case into `MeasuredCop.judge_floor`: 26 at the head, with no raise.
- `python3 tools/audit/archscore/score.py --diff origin/main` at the head: `Architecture score: dS -0.0012 WORSENS (inadmissible: coord_footprint 2496->2498)`. Reason under `## Architecture score`.
- Goldens, in the gate run at 5ea07c1b63: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 31255c328918573ef29007dac22d7184a0f0247c` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. Neither claim file is touched.

## Architecture score

- `coord_footprint` 2496 -> 2498: the two coordinator logic statements the approved design prescribes. One is the measured-heat flag `_fold_measured_cop` passes to `release` and `judge_ratio` (`params, measured_heat = ...`). The other is the restore (`if self._measured_cop.take_restore():`). The flag is install capability, which only the coordinator's `_config` reads (`probe_install`), and the restore writes `_cop_scale`, which only the coordinator owns. Moving either into `MeasuredCop` would put a config read or a coordinator write below the glue (`fixer.md` step 17). Payments considered: the debug-log move (the design's candidate) is a delegation, which the footprint already counts as plumbing, so it moved `max_class_loc` and not this metric. Splitting the flag's assignment from `params` counts the same one logic statement. Inlining `probe_install(...)` into both calls would hide the statement and compute it twice.

## Unpinned sites

`python3 tools/pr/ci_predict.py --base 31255c328918573ef29007dac22d7184a0f0247c` names 47 added sites, all in `custom_components/` (`accuracy.py`, `coordinator.py`, `draw_range.py`, `store.py`). Each is left to `mutation-autofix`, whose lane mutates `custom_components/` (`ci-autofix.md`). The full local diff-mutant run above (every mutant `--list` draws, beyond the `MUTANT_MAX` cap) killed every site at this head: its two survivors are killed or deleted (`## Mutation proof`, "Diff mutants"). There is no triage, except the moved equivalence triage below.

- custom_components/heatpump_optimizer/accuracy.py:959 BOOLOP (`if drawn_kw is not None and min(asked_kw, drawn_kw) < power_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:959 CLAMP_DROP (`if drawn_kw is not None and min(asked_kw, drawn_kw) < power_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:959 CMP_BOUND (`if drawn_kw is not None and min(asked_kw, drawn_kw) < power_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:959 GUARD_OFF (`if drawn_kw is not None and min(asked_kw, drawn_kw) < power_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:986 RETURN_DEL (`return state == ASK_UNOBTAINABLE and draw is not None and no`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:999 GUARD_OFF (`if self.scale_response != ASK_PENDING or self.restore_due:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1001 CMP_BOUND*2 (`if not self.probe and not self.reseeded and not COP_SCALE_MI`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1001 GUARD_OFF (`if not self.probe and not self.reseeded and not COP_SCALE_MI`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1003 RETURN_DEL (`return ASK_PENDING`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1005 BOOLOP (`if len(self.probe) >= MIN_SAMPLES and (state := draw_respons`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1005 CMP_BOUND (`if len(self.probe) >= MIN_SAMPLES and (state := draw_respons`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1005 GUARD_OFF (`if len(self.probe) >= MIN_SAMPLES and (state := draw_respons`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1007 RETURN_DEL (`return self.scale_response`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1012 RETURN_DEL (`return due`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1019 GUARD_OFF (`if refusal is not None:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1025 RETURN_DEL (`return refusal`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1053 CLAMP_DROP (`if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1053 CMP_BOUND (`if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1053 GUARD_OFF (`if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1056 GUARD_OFF (`if state == ASK_IGNORED:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1061 BOOLOP (`if self._admits(state, draw, measured_heat) and (verdict := `): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1061 GUARD_OFF (`if self._admits(state, draw, measured_heat) and (verdict := `): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1063 GUARD_OFF (`if abs(ratio - 1.0) <= COP_ASK_TOLERANCE or state == ASK_FOL`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1065 GUARD_OFF (`if state == ASK_PENDING:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1067 RETURN_DEL (`return COP_REFUSED_NO_EVIDENCE`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1068 RETURN_DEL (`return None if self._base_folds(row, params) else COP_REFUSE`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1094 GUARD_OFF (`if not self._admits(state, draw, measured_heat):`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1097 BOOLOP (`self.restore_due = self.restore_due and not measured_heat`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1098 GUARD_OFF (`elif rows:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1101 GUARD_OFF (`if verdict != ASK_PENDING:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1158 BOOLOP (`if isinstance(response, str) and response in (ASK_FOLLOWS, A`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1158 GUARD_OFF (`if isinstance(response, str) and response in (ASK_FOLLOWS, A`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1160 RETURN_DEL (`return record`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1176 BOOLOP (`if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is Non`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1176 CMP_BOUND (`if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is Non`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1176 GUARD_OFF (`if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is Non`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1178 GUARD_OFF (`if (temp is not None and not np.isfinite(temp)) or (raw.get(`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/accuracy.py:1180 RETURN_DEL (`return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp, at=at)`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/coordinator.py:5331 GUARD_OFF (`if self._measured_cop.take_restore():`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/coordinator.py:5333 GUARD_OFF (`if refusal := MeasuredCop.judge_floor(commanded, self._measu`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/coordinator.py:5359 BOOLOP (`if heat_kw is None and (refusal := self._measured_cop.judge_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/coordinator.py:5359 GUARD_OFF (`if heat_kw is None and (refusal := self._measured_cop.judge_`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/draw_range.py:494 RETURN_DEL (`return draw_response(pairs)`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/draw_range.py:508 CMP_BOUND (`if high < FOLLOW_ASK_SPAN * low:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/draw_range.py:508 GUARD_OFF (`if high < FOLLOW_ASK_SPAN * low:`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/draw_range.py:513 CMP_BOUND (`return ASK_FOLLOWS if slope >= FOLLOW_SLOPE_MIN else ASK_IGN`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")
- custom_components/heatpump_optimizer/draw_range.py:513 RETURN_DEL (`return ASK_FOLLOWS if slope >= FOLLOW_SLOPE_MIN else ASK_IGN`): left to mutation-autofix; killed by the block driver in the full diff-mutant run (`## Mutation proof`, "Diff mutants")

- The ledger: the 27 `killed_by` pins this diff left stale (each names a line it rewrote or moved, `ci_predict.py` `STALE PIN`) are deleted in 5ea07c1b63, as #3593's were; the lane re-pins the killed sites. The equivalent `CMP_BOUND` triage of the ask-tolerance comparison keeps its verdict and reason. Its line moved unchanged from `MeasuredCop.judge_ratio` to `MeasuredCop._judge_ratio`, so its file and anchor are re-keyed to `MeasuredCop._judge_ratio.CMP_BOUND.9d967a75`.

## Red checks

- `tests / mutation`, predicted, not yet run: the 47 sites under `## Unpinned sites` have no ledger pin at this head, so the check reads them as added unpinned sites until `mutation-autofix` pins the ones it kills (`ci-autofix.md`: once a pull request exists, wait for the bot commit and do not duplicate it). The cheaper detector already ran: the local diff-mutant run over every mutant the diff draws (`## Mutation proof`, "Diff mutants") killed every site at this head. Pinning is that lane's job by contract, so no countermeasure is owed: the finding is that none exists beyond the run already made.

No CI run exists at this head. The red local check this branch had, `tests/entities.py`'s "and every mark still names a mutant this tree generates, pin and all (#1217)" at 312380fc2c, is repaired in 5ea07c1b63. Whether a cheaper detector could have run: yes. `python3 tools/pr/ci_predict.py` prints the same stale anchor as `STALE PIN` in seconds, and it is a step of `tools/pr/prepr.sh`, which this branch had not run yet. The gate run found it first only because it ran first. That is the process followed in a different order, not a missing detector: no countermeasure.

## Forward-carry

- Verdict item e98d0ab9: the defrost derate's inferred estimator (`coordinator._settle_defrost` with `accuracy.delivered_ratio`, `defrost.DefrostModel.observe`) learns a frost derate of 0.684 on a pump that sets its own power, under flat asks in the frost band with no defrost flag. The control, a draw equal to the ask, stays at 1.000 (`## Figures`). It is the same ask-over-draw mechanism in the defrost seam, which no live group owns. Its measurement lands in `dev/audit/harnesses/cop_duty_floor.py` (rows `defrost_inferred_*`, whose docstring names the item). The finding is routed to R11-INTAKE-R10-RESIDUE, the round-11 holding group that re-homes a residual to its seam's owner, on the round-11 roster on handoff/audit-r10-roster, which this seat does not write. A fix needs this PR's verdict (`MeasuredCop.scale_response`) or the window's evidence read before folding the ratio, and must re-measure with the probe recipe above at its own merge base. Carry: R11-INTAKE-R10-RESIDUE
- Residual, the owner's carry 3 (ruled "Accept both", 2026-11-16): a release is not bounded per cycle. `true_0.6_max_cycle_move` reads 0.292 at both ends. Carry: dismissed: owner ruling 2026-11-16 accepts it as a residual
- Residual, the owner's carry 4 (ruled "Accept both", 2026-11-16): the overstated-minimum floor is unchanged. `min3_running_warm_own`, `fixed3_duty50_warm_own` and `fixed3_duty70_warm_own` read the same at both ends. Carry: dismissed: owner ruling 2026-11-16 accepts it as a residual
- Residual, stated by the design: a latched does_not_follow also undoes folds made during an earlier ASK_FOLLOWS period on the same install, because the reset into that period cleared its probe. The latched verdict says the draw does not follow the heat ask, so those folds were read under evidence it now contradicts. Carry: dismissed: the approved design states it as the restore's intended scope
- Residual (verdict item 76771913): the configured-scale restore assumes every move since configuration came from this ratio fold. An install that once had a thermal entity or heat counter and later removed it holds heat-measured folds in `cop_scale`, and a later latched does_not_follow undoes them. While the heat entity is still configured, departure 2 above keeps the restore off. Carry: dismissed: no stored record says which folds were heat-measured, and keeping one is a new store field this finding alone does not justify

## Friction

none
