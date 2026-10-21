# design-r10-scores — designer revision 1 result

Design SHA: 220192d70 (`refs/heads/design/r10-scores`, fast-forward from 6f14f9d0b; file dev/programme/designs/R10-SCORES.md). Read at cd1c837ca (ADVISOR handoff) and f2fb1b0e9 (origin/main). Verdict read from origin/design-verdict/r10-scores:verdict.md.

## Verdict points

1. :21 shared predicate — **revised.** Module-level `house_loss_converged(samples)` beside `house_loss_confidence` (coordinator.py:1300) is read by `_scores_view` and by the learning view's `house_heat_loss_learned` (replacing `> 0` at coordinator.py:7543), so `ModelStatusSensor.native_value` (sensor.py:2010) moves with the envelope dash; new backend consistency arm in tests/entities.py sweeps samples across the threshold. Goldens: `house_heat_loss_learned` is already false at 0 samples, so it does not move. Carry: R10-SCORES
2. :22 `alarmed` is not heat-loss drift — **revised.** The owner brief does name "or drifts" (roster R10-SCORES item 2), so the dash stays but keys on the heat-loss refit (`model_restart_advice(...)["refit"]["scale"]`, accuracy.py:708 `heat_loss_refit`, the learner's own Newton relation over settled pairs) departing from the current scale by more than `REFIT_BAND_PERCENT` (accuracy.py:649); `alarmed` is only the precondition under which the refit is computed (coordinator.py:1120). Code renamed `heat_loss_refit_disagrees`; the direct-alarm option is now a rejected alternative. Carry: R10-SCORES
3. :19, :66-69 payload.py — **revised** (file listed in "Files touched"; dispatch waits on the edge) + ask below. Note: at f2fb1b0e9 the roster gives R10-LEARNER-ETA `after: ['R10-ARCH-SHAPES']`, not `[]` as the verdict says; still no edge with R10-SCORES. Carry: R10-SCORES
4. :21, :70 learner-progress owner — **revised** (the score publishes a reason code only, never progress copy; the progress owner reads `house_loss_converged`) + ask below. Carry: R10-LEARNER-ETA
5. :49 `waiting_for` — **revised.** Derived: `waiting_for = reasons["overall"]`; the overall code is `first_scored_day`, the token the sensor publishes today (sensor.py:2686, pinned by tests/entities.py:11756); `no_evidence` retired. Carry: R10-SCORES
6. :55 two-zone test — **revised.** Fixture sets `_house_heat_loss_samples` past the threshold and no drift alarm; red only on the UA basis. Carry: R10-SCORES
7. :27 C3 citation / dead `liveState` — **revised.** Cited `3930b421a:dev/audit/rounds/round10/D7/arch2-s5/patches/C3_reading_rules.patch` (absent at f2fb1b0e9, verified); `readNumber` ported alone; `liveState` dropped because `statNumber` (card.js:5871) already applies the rule inline. Carry: R10-SCORES
8. :15 headline via `statNumber` — **revised.** Seam sentence names both readers (`statNumber` at card.js:8568 for state, `scoreParts` for hover/breakdown); consistency walk asserts headline null exactly when `reasons.overall` is present. Carry: R10-SCORES
9. Note on the blocker scope — **revised** the wording: only the bundle-dependent arms (2.6x drift, band) are blocked; item 1 reproduces in node and item 2's basis has RATIO-SITES' `--ratio-override 1.0`. Carry: dismissed scope wording only
10. Owning seam check — no change needed. Carry: dismissed verified no defect
11. Sibling sites check — no change needed. Carry: dismissed no missed site
12. `max(scale, 0.1)` floor — kept with the fixer; wording now says the restore and topology paths bypass the clamp. Carry: dismissed fixer decides evidently
13. Check 5 (design overlap, goldens) — no change needed. Carry: dismissed verified as stated

## Asks (orchestrator's to decide)

- ask: add `custom_components/heatpump_optimizer/payload.py` to R10-SCORES `files`, and an after-edge between R10-SCORES and R10-LEARNER-ETA (both edit `Scores`-adjacent payload.py and the coordinator learning view; LEARNER-ETA has no edge to SCORES). Carry: R10-SCORES
- ask: which group owns learner progress (phase, ETA, "waiting for"): R10-LEARNER-ETA per its brief, with R10-SCORES publishing only a reason code and both reading `house_loss_converged`, is the note's assumption; if the orchestrator gives the predicate to LEARNER-ETA instead, the edge must run LEARNER-ETA before SCORES. Carry: R10-LEARNER-ETA

## Observations

- brief_lint.mjs reads only the JSON plan format and refuses the .md note ("could not be read as JSON"), as for the previous revision; paths were checked by hand at cd1c837ca/3930b421a, all resolve except the two marked "would be new". Carry: dismissed linter not applicable
