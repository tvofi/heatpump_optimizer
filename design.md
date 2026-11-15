# R11-OUTSIDE-SELF-SETTING-PUMP: the COP learner's scale-response evidence under flat asks (architect note, round 2)

Designer seat, round 2, answering `Design review: revise 66aa3023d6` (design-verdict/R11-OUTSIDE-SELF-SETTING-PUMP at bcf0ced159). Base and code read: `5825e1346c14eecace5c87c046558774145a94dc` (origin/main; After: none, so no predecessor head). Since round 1's base ebe83a1b82, nothing changed in accuracy.py, draw_range.py, flow_meter.py, store.py or the harness, and coordinator.py's changes do not reach `_fold_measured_cop`, `_fold_cop_evidence` or `_apply_cop_scale` (`git diff ebe83a1b82 5825e1346c -- custom_components`). No finder harness: owner report (D4). The instrument is `dev/audit/harnesses/cop_duty_floor.py`. Figures marked (spike) come from an uncommitted scratch monkeypatch of `MeasuredCop` and `_fold_measured_cop` implementing the shape below, driving that harness's `coord()` and `main()` at this base. The fixer re-measures every one at both ends.

## The defect, measured

On a 4 kW nameplate, a pump drawing 2.2 kW ±3 % under flat asks of 1.5 kW ±2 % ends at `92/96 0.500` and `668/672 0.500` at this base (`COP_SCALE_MIN`), off 1.000 by more than 5 % for 625 of 672 cycles. The asks never span `FOLLOW_ASK_SPAN`, so `draw_range.ask_evidence` reads `ASK_UNOBTAINABLE` once `MIN_SAMPLES` run-asked pairs exist, and every interval folds against `scale × ask / draw` (`flow_meter.cop_evidence`), a target the draw never answers. Revise point 1's case is the same mechanism inside `COP_ASK_TOLERANCE` (`judge_ratio`'s tolerance arm): 1.6 kW on 1.5 reads `672/672 0.500` at this base, and 1.4 kW on 1.5 walks up to `672/672 1.600` (`COP_SCALE_MAX`). A heat-led pump's draw answers the learner's own scale move; a self-setting pump's does not. With flat asks the regressor that separates them is the heat ask, `asked_kw × cop_scale`, whose span comes from the scale alone; `CopInterval` already stores the scale every row was read at.

## Owning seam

One owner: `MeasuredCop` in `custom_components/heatpump_optimizer/accuracy.py` (`judge_ratio`, `release`). `draw_range.py` is read, unchanged. `coordinator.py` only calls: `_fold_measured_cop` (seam "learning", `tests/seam_map.json`) passes one flag and applies the restore through `_apply_cop_scale`. `store.py` registers one key. No second owner.

## Shape

**Probe state on `MeasuredCop`**: probe rows, a deque bounded at `draw_range.WINDOW` of (heat ask, drawn kW); the verdict, one of pending, follows or ignored; a restore-due flag. No origin float (revise point 2, below).

**Admission (revise point 1, widened).** An interval is admitted when, and only when, the state is `ASK_UNOBTAINABLE`, a window exists (`draw` not None), and the install has no measured heat (`probe_install(config).measured_heat` false, passed by `_fold_measured_cop` to both `judge_ratio` and `release`; fixer note 8f04d6b5). Within `COP_ASK_TOLERANCE` or beyond it alike. In `judge_ratio` it sits after the tracking gate and the `ASK_IGNORED` arm, before the tolerance arm; in `release` it is the unobtainable arm only. At pending a row joins the probe and keeps today's outcome (folds within the tolerance, base's `_base_folds` beyond). Once the probe holds `MIN_SAMPLES` rows whose heat asks span `FOLLOW_ASK_SPAN` (`LOW_PERCENTILE`/`HIGH_PERCENTILE`), the slope of log drawn on log heat ask latches the verdict by `FOLLOW_SLOPE_MIN`: `ask_evidence`'s rule on another regressor, no new constant. At follows every admitted interval folds, as under `ASK_FOLLOWS`. At ignored every interval reads `COP_REFUSED_OFF_ASK`, as under `ASK_IGNORED` (#2262), and the restore is due. `release` admits all its rows first and judges once; on ignored it returns none.

**Reset first, then admit (fixer note 3c7e91a2).** `release` reads the state before anything else: any state but unobtainable clears the probe, the verdict and the restore flag, and the existing arms run unchanged. So a pending aged-out row folds by base's rule and seeds nothing.

**Restore to the configured scale (revise point 2).** The restore target is `_config.cop_scale` (coordinator.py:3857), not the scale at the first probed row. Where admission applies there is no measured heat, so every move of `cop_scale` since configuration came from this ratio fold, under this version or an earlier one: a scale this learner did not write is the configured one. That covers an upgraded install the released residual already walked (from 0.7 the restore reaches 1.000, below), and a restart mid-probe (the probe re-seeds at the walked scale and the restore still reaches 1.000). One coordinator statement, right after the release loop in `_fold_measured_cop`, past the freeze gate: when `MeasuredCop` reports a restore due, `_apply_cop_scale(ctx._config.cop_scale)`. A verdict `judge_ratio` latches applies at the next unfrozen cycle's release site, one cycle late. `_cop_samples` is not touched. Residual stated: folds made under an earlier `ASK_FOLLOWS` period on the same install are also undone, because a reset (the window's evidence governing again) cleared that period's probe; the latched ignored says the draw does not follow the heat ask, so those folds were read under the evidence this verdict now contradicts.

**The clamp (revise point 2): decision: owner.** An install walked to `COP_SCALE_MIN` (or `COP_SCALE_MAX`) seeds its probe at the clamp, where `_apply_cop_scale`'s clip holds the heat ask flat: the probe stays pending and the install stays at the clamp. Two remedies, both measured below:
- **A (recommended): re-seed at a clamp.** When the probe's first row was read at either clamp, the restore is due before any row is kept; the probe starts again from the configured scale. Cost: a heat-led pump whose true scale is at or past the clamp is moved to the configured scale and walks back (row `true_0.45_flat_4kw_from0.5`: highest 0.997, ends 0.500, follows). Gain beyond D4: a heat-led pump of true 0.68 stuck at the clamp, which base cannot unstick (its 1.1 kW draw is under the nameplate third, `0/672 0.500`), reaches 0.679. A configured scale at a clamp makes A a no-op.
- **B: stated residual.** Installs already at the clamp stay there under flat asks; the remedy is a manual scale reset.

**Persistence.** The latched verdict persists; the probe rows and flag do not (like `held`). `MeasuredCop.as_dict` gains one optional key; `from_dict` reads it leniently (unreadable or absent is pending) and never drops the measurement record for it. `store.py` registers `measured_cop/<key>` as a choice domain beside `measured_cop/cop`. **Diagnostics**: `accuracy.diagnostics_view` gains the verdict beside `draw_follows_ask`.

    _fold_measured_cop: freeze gate -> release(draw, .., measured_heat) [not unobtainable: reset; else admit, judge once]
                        -> fold returned rows (read scale) -> restore due? _apply_cop_scale(_config.cop_scale)
                        -> ... judge_ratio(.., measured_heat) [ignored: COP_REFUSED_OFF_ASK; unobtainable: admit] -> fold

Invariants, each a test: (k) any state but unobtainable is bit-identical to this base; (l) no window, or measured heat, keeps base's rule and probes nothing; (m) a heat-led flat-ask pump latches follows and keeps its folds; (n) a self-setting flat-ask pump, beyond or within the tolerance, ends at the configured scale and then reads `COP_REFUSED_OFF_ASK`; (o) the restore moves the scale only on an unfrozen cycle; (p) a verdict leaves only by a reset, and a reload keeps it; (q) an unreadable stored verdict keeps the measured COP; (r) a pending aged-out row seeds nothing; (s) under A, a probe seeded at a clamp re-seeds once.

## Alternatives, and why each lost

- **Origin at the first probed row** (round 1): at the clamp the origin is the clamp, and partly walked it freezes the walked scale (verdict point 2).
- **Hold under unobtainable**: loses invariant h for heat-led pumps; true 0.68 would stay at 1.000.
- **`ask_evidence` on the heat ask for every window**: needs a scale per `DrawRange` sample, a second owner in `draw_range.py`, and re-judges the `p4_*` installs on a regressor they do not follow.
- **Judge on the room's thermal response**: the heat-loss learners' seam, two owners.
- **Bound every fold's move**: slows the walk, does not stop it.

## Sibling sites

`git grep -n -e "ask_evidence(" -e _base_folds -e "_measured_cop.release(" -e "judge_ratio(" -e ASK_UNOBTAINABLE -e "_apply_cop_scale(" -e "_config.cop_scale" -- custom_components`. Covered: `judge_ratio`'s tolerance and unobtainable arms, `release`'s unobtainable arm, the release loop and the judge call in `_fold_measured_cop`, `_apply_cop_scale` in `_fold_cop_evidence` (the folds restored over). Out of scope: the load's `_apply_cop_scale` and the constructor's read of `_config.cop_scale` (nothing judged), `follows_ask` (value unchanged), and `selfmod_independent`'s within-tolerance folds under spanning asks before the window's evidence exists (#3593's routed residual: its state is pending, never unobtainable).

## Evidence plan

- **Failing tests first**, `tests/features.py`, a new section after `R.section("R10-COP-LEARNER-DRAW-FLOOR`, on the production symbols: (n) beyond and within the tolerance fail at this base; (m) passes at both ends; (k), (l) including a thermal-entity install whose reading is None for a cycle, (o), (p), (q), (r), (s) each pinned once.
- **Harness rows**, `cop_duty_floor.py`, both ends, each "folded/intervals scale" plus lowest, highest, cycles off by more than 5 %, verdict; base `|` spike A `|` spike B, 4 kW, flat asks 1.5 kW ±2 %:
  - self-setting 2.2 kW, 96 and 672: `0.500` (625 off) `|` `48/96 1.000` and `48/672 1.000`, lowest 0.730, 6 off `|` as A.
  - within tolerance 1.6 kW, 672: `672/672 0.500` `|` `138/672 1.000`, lowest 0.766, 111 off `|` as A. And 1.4 kW: `1.600` `|` `130/672 1.000`, highest 1.311 `|` as A.
  - heat-led true 0.68 and 0.8, 672: `0.679`, `0.799` at all three, verdict follows at the spike (fixer note b52a0e7c: measured, under the widened admission).
  - persisted 0.500, self-setting 2.2 kW: `0.500` `|` `90/672 1.000` `|` `0.500`, pending. Within tolerance: `0.500` `|` `138/672 1.000` `|` `0.500`.
  - persisted 0.7, self-setting 2.2 kW: `0.500` `|` `48/672 1.000`, lowest 0.511 `|` as A. Within tolerance: lowest 0.537, `138/672 1.000` at A and B.
  - persisted 0.500, heat-led true 0.45 and 0.68: `0.500`, `0/672 0.500` `|` `664/672 0.500` (highest 0.997), `616/672 0.679` `|` as base, pending.
  - reload at tick 70 and 400 keeping the verdict: `48/672 1.000`, lowest 0.730, at A and B; losing it (the cost the stored key saves): `95/672 1.000`, lowest 0.636.
  - Rows moving by design: `held_full` `96/96 0.582` → `47/96 1.000`, `held_filling` `96/96 0.650` → `53/96 1.000` (a fixed 3.2 kW draw is a self-setting pump). Invariant h's control becomes heat-led twins of true 0.8: `96/96 0.807` and `0.806` at base and spike.
- **Null control**: the full harness output at this base against spike A and spike B differs in the two `held_*` lines only (`diff`), widened admission included; spike A and B outputs are identical.
- **Goldens**: none expected to move; one that does is claimed under `claim-files.md`, never re-recorded.
- **Mutation targets**: the three admission guards (state, window, measured heat); the span and slope comparisons; reset before admit; the latch refusing within-tolerance intervals; release judging before return; the restore target (configured, not current); the restore site above the freeze gate; the clamp re-seed (A); `from_dict`'s leniency.

## Carries this group holds

- **Carry 0 (D4)** is this note.
- **Carry 1, departure 1: kept, extended to the restore. decision: orchestrator.** A frozen cycle and one with no power reading release, restore and hold nothing. Control re-run at this base: the mutant "the release ahead of the freeze gate" (the release loop moved above the `_learning_frozen` gate) against `a frozen cycle and one with no power reading release nothing and fold` in `tests/features.py`; result in `## Control re-run` below.
- **Carry 2, departure 2: kept, not owed. decision: orchestrator.** A replayed row has no heat reading, so the envelope's figure would be modelled COP × ask, the plan's own heat, which in-tolerance near-nameplate intervals already feed. Control: "a replayed interval folds the scale and not the capacity envelope".
- **Carry 3, release bounded per cycle: not bounded (recommended). decision: owner.** `true_0.6_max_cycle_move` 0.292 at this base and at spikes A and B (identical harness line); beside it the excursion rows above (lowest 0.730 beyond, 0.766 within the tolerance). A bound of N × `COP_LEARNING_MAX_STEP` shrinks the excursion and lengthens both the heat-led catch-up and the probe.
- **Carry 4, overstated-minimum floor: unchanged. decision: owner.** `draw_range.power_floor_kw` is untouched; `min3_running_warm_own`, `fixed3_duty50_warm_own` and `fixed3_duty70_warm_own` read the same at this base and both spikes (the null control's diff).

## Hot files, serial position

`accuracy.py`, `coordinator.py` (`_fold_measured_cop`), `store.py`, `tests/features.py`, `dev/audit/harnesses/cop_duty_floor.py`. After: none. No grader registration, no p1/p2 split. Sibling designs: round 1's verdict found none claiming this seam; R11-OUTSIDE-HONEST-METERED-FLOOR leaves `ask_evidence` unchanged, and its pinned asks only enlarge the flat-ask population served here.

## Notes for the fixer

- `max_class_loc` and `class_excess_loc` sit at zero headroom (`python3 tests/structure.py`); this adds the restore statement and the flag argument to two coordinator calls. Candidate payment: move `_fold_measured_cop`'s ratio-refusal `_LOGGER.debug` into `MeasuredCop.judge_ratio`, where the refusal is decided. Measure with `tools/audit/archscore/` before and after. Carry: R11-OUTSIDE-SELF-SETTING-PUMP (item 5e1c2a90)
- Do not apply the restore in `_learn_measured_cop`, the #1523 class check's census key that refused #3593's first call site. Carry: R11-OUTSIDE-SELF-SETTING-PUMP (item 7b3d9f14)
- The harness's `run()` keeps the ask fixed whatever the scale (open loop); the live plan re-prices its ask unless pinned, and flat asks are the pinned case. Say so in the docstring beside the new rows, and add a persisted-scale parameter to `run()` for the from-0.500 and from-0.7 rows. Carry: R11-OUTSIDE-SELF-SETTING-PUMP (item a40c6e72)
- Implement only the remedy the owner rules for the clamp; under B, drop invariant (s) and the re-seed mutant, and the from-0.500 rows pin the residual. Carry: R11-OUTSIDE-SELF-SETTING-PUMP (item c4e81d27)

## Control re-run

Departure 1's control, at this base: the block from `R.section("R10-COP-LEARNER-DRAW-FLOOR` in `tests/features.py` prints 37 `ok` lines unmutated; with the release loop moved above the `_learning_frozen` gate it prints 36 and one `FAIL`, `a frozen cycle and one with no power reading release nothing and fold nothing; the next live cycle releases the held interval`. The fixer re-runs it at the head with the restore statement placed under the same gate.
