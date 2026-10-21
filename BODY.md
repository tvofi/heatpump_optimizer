# design-r10-scores: designer seat result (R10-SCORES, size L)

- **Design SHA:** `6f14f9d0bbbbbd09d575dbb6490b23cc970942c6` on `refs/heads/design/r10-scores`. One commit on origin/main `f2fb1b0e9`, adding one file: `dev/programme/designs/R10-SCORES.md` (73 lines).
- **Contract:** designer.md DRAFT at `ddacf9856`. The note is written against design-review.md beside it.
- **Read at:** the R10-ADVISOR handoff head `cd1c837cabe9536b27a7d36d193d5f4e24d23deb` and origin/main `f2fb1b0e950ecd047b7f08b3adef93776a622540`. R10-RATIO-SITES is done at `8c6d940b0`. Main has not changed coordinator.py, sensor.py, payload.py or the card since ADVISOR's base `265d3bf1a`.

## Causes measured
1. **Item 1 is a card defect.** `finiteScore` in `scoreParts` uses `Number(v)`, and `Number(null)` is 0. A sub-score the backend publishes as None therefore renders as `0/100` in both the breakdown and the hover. Measured in node: `finiteScore(null)` returns 0. `tests/card.mjs` misses this because its fixture omits the key rather than publishing it as null.
2. **Item 2:** `_scores_view` grades `heat_loss_coefficient * house_heat_loss_scale`, not `_effective_house_heat_loss`. The latter adds the learned two-zone split and is the figure the Health tab publishes. Nothing gates the grade on convergence or drift.
3. **Item 3:** a None score carries no reason, so each card surface uses its own wording.

## Owning seam
`_scores_view` (coordinator.py) is the single owner of `Scores` (payload.py). `OptimizationScoreSensor` republishes it, and the card's `scoreParts` is its only reader: headline, hover and breakdown all go through it. `Scores` gains `reasons`, with the invariant that a value is None exactly when its key is in `reasons`. The envelope grade reads `_effective_house_heat_loss` and shows a dash on `heat_loss_learning` (`house_loss_confidence`), `heat_loss_drifting` (`_snapshot_ring.alarmed`) or `no_house_model`. The machine score gets one `_watched_cop_buckets()` helper in place of two inline counts that differ on `np.isfinite`. On the card side, only C3's `liveState` and `readNumber` are ported, from 3930b421a.

## Alternatives rejected
- **Compute in sensor.py:** it needs a new read path into coordinator state, which makes two owners.
- **A new scores.py module:** it needs a new tracked-file classification and adds churn outside the seam ahead of R10-LIVESTATE. It belongs to the decomposition programme.
- **The card derives the dash from ModelStatusSensor:** that is a re-implemented rule with two sources.
- **A confidence dash only:** the two-zone inflation stays.

## Sibling sites
- **Card `Number(attrs.*)` without a null guard:** these are in R10-ADVISOR's rows (`current_scale`, `current_setpoint`, `configured_target`). They need propagating to ADVISOR's rework and are not fixed here.
- **UA without the learned split:** battery.py and optimizer.py are correct (single-zone branches only), and sysid `_held_state` is guarded. sysid `HousePlant.of_params` is out of scope, because D2-s3-73 was refuted.

## Evidence plan
- **Failing tests first:**
  - a card.mjs fixture with explicit null sub-scores;
  - a coordinator test on two-zone params where the learned split is not 1.
- **Harness:** the RESEED harness `dev/audit/rounds/round10/study-reseed/live_store.py` run on the owner's bundle, or a new `dev/audit/harnesses/r10_scores_bundle.py`.
- **Null control:** `--ratio-override 1.0` makes the two bases agree, and with `--scale-override 1.0` added every delta is 0.
- **Consistency test:** card.mjs walks every surface for each value and reason.
- **Goldens:** all five `tests/golden/coord_*.json` carry `insight.scores` with envelope 58.3 at zero samples. The dash moves them, which is claimed in `tests/golden/claimed_drift.txt`.
- **Mutation targets:**
  - the null test in `scoreParts`;
  - the `two_zone_enabled` branch as `_scores_view` reads it;
  - the `reasons` invariant;
  - the `isfinite` check in the helper.

## Hot files
- coordinator.py: position 18 of 25 (after SAV-REASONS and ADVISOR; next LIVESTATE and CONFIG-NOTICES).
- heatpump-optimizer-card.js: position 4 of 5 (after ADVISOR; next UX-HEALTH).
- sensor.py: hunks stay inside `OptimizationScoreSensor`, because R10-SENSOR-PAYLOAD follows on that file.
- **Carries owed:** UX-HEALTH renders `reasons` on the Health tab, and the ADVISOR siblings above go to its rework.
- **Carries received:** the RATIO-SITES split and the SAV-BASELINE rule to read figures, not recompute them.
- **Revalidation:** after ADVISOR merges, re-read `_insight_view`'s `price_tiles` line and the card block next to `scoreBreakdownHtml`.

## Blockers and notes
- **Blocker (reported, not designed around):** items 1-3 are owner-reported and have no finder harness. Item 2's magnitude, the drift of about 2.6x and the band calibration can only be measured on the owner's private diagnostics bundle, which this seat does not hold. The note therefore changes nothing on those suspected causes, and any band change goes back as a finding.
- **Process note:** the design commit was made with `git commit --no-verify`. No hook is configured (no `core.hooksPath`, no non-sample hooks), so nothing was bypassed; I am recording it anyway. No tracked file in the main checkout was changed, and no PR was opened.
