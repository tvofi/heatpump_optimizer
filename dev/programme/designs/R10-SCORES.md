# R10-SCORES design note (designer seat, DRAFT contract at ddacf9856)

The group's architect note, extended. It lives on `design/r10-scores` only and is never merged. Size L, issues #2238 and #2258; findings: owner items 1-3 and ARCH2-s5-C3. Revision 1 answers the design review of `6f14f9d0b` (`design-verdict/r10-scores`).

**Read at.** Code: R10-ADVISOR's handoff head `cd1c837cabe9536b27a7d36d193d5f4e24d23deb` (PR #2572, in rework). `origin/main` is `f2fb1b0e950ecd047b7f08b3adef93776a622540`. R10-RATIO-SITES is done at `8c6d940b0`. Between the ADVISOR merge base `265d3bf1a` and main, nothing changed in `custom_components/heatpump_optimizer/coordinator.py`, `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/payload.py` or the card. ADVISOR does not touch the code below. It edits `_insight_view`'s `price_tiles` line and the card's `priceTiles` block next to `scoreBreakdownHtml`. Re-read both after it merges (step 9).

## Causes, measured at cd1c837ca

1. **Item 1: a heat-pump score of 0 with no COP evidence is a card defect.** `_scores_view` in `custom_components/heatpump_optimizer/coordinator.py` publishes `machine: None` until one COP bucket has `COP_BASELINE_MIN_SAMPLES`. `OptimizationScoreSensor` in `custom_components/heatpump_optimizer/sensor.py` spreads `None` into its attributes as JSON `null`. The card's `finiteScore` (in `scoreParts`) calls `Number(v)`, and `Number(null)` is `0`. Run in node, `finiteScore(null)` returns `0`, and `finiteScore(undefined)` returns `null`. So both the breakdown and the hover print `0/100`. `tests/card.mjs` misses this because its fixture omits `operation` (undefined) and never publishes it as `null`. ARCH2-s5 C3's `readNumber` is the rule that fixes it.
2. **Item 2: the house score reads the wrong UA basis.** `_scores_view` grades `heat_loss_coefficient * house_heat_loss_scale`. `_effective_house_heat_loss` (same file) is the model's own figure: on a two-zone house it adds the learned lower-floor split. The Health tab publishes that figure as `ModelStatusSensor.heat_loss_w_per_k`. Two more causes are to be measured, not assumed (carry 1): the drift of about 2.6x, and the 20-100 h band. Nothing gates the grade on how far the learner has converged.
3. **Item 3: surfaces with no shared reason or predicate.** The headline value reads the score sensor's *state* (`plan.statNumber("_plan_optimization_score")` in the card). Its hover and the breakdown read the sensor's attributes through `scoreParts`. The Health tab's waiting row (`HEALTH_WAITING`) and model rows read `ModelStatusSensor`, whose `native_value` says `learned` once `house_heat_loss_learned`, which the learning view sets at `_house_heat_loss_samples > 0`. A convergence dash on any other threshold would show "learned" on Health beside "still learning" on the envelope.

## Owning seam

**`HeatPumpOptimizerCoordinator._scores_view` is the one owner of the score view model** (`Scores` in `custom_components/heatpump_optimizer/payload.py`). `OptimizationScoreSensor` only republishes it. The card has two readers of it: `statNumber` for the headline (sensor state, `overall`) and `scoreParts` for the hover and the breakdown (attributes). The **house-loss convergence predicate** has one owner too: a module-level `house_loss_converged(samples)` beside `house_loss_confidence` in `coordinator.py`, read by both `_scores_view` and the learning view's `house_heat_loss_learned`, so `ModelStatusSensor` and the envelope cannot disagree. The Health tab rows belong to R10-UX-HEALTH (carry 3). `_close_score_day` keeps the operation EMA, with no change in shape. Which group owns learner *progress* (phase, ETA, "waiting for") is the orchestrator's call (asked in the result); this group publishes a reason *code*, never progress copy.

## Shape

- `Scores` (in `custom_components/heatpump_optimizer/payload.py`) gains `reasons: dict[str, str]`, holding exactly one code for each key whose value is `None`. The existing numeric keys keep their names and types, so automations do not break. The invariant is that `value is None` if and only if `key in reasons`, and no score is ever `0` for want of evidence.
- Convergence: `house_loss_converged(samples) -> bool` is `house_loss_confidence(samples) >= ` a threshold the fixer derives from `HOUSE_LOSS_ALPHA` (no new tuning literal; one EWMA time constant is the default to argue against). The learning view sets `house_heat_loss_learned` from it, replacing `> 0`; `ModelStatusSensor.native_value` is unchanged and moves with it.
- Envelope: `loss = _effective_house_heat_loss(ctx._thermal_params, scale)`, the same call the learning view makes. Keep the `max(scale, 0.1)` floor only if every write path bounds the scale (the restore and topology paths do not go through the clamp), and say which in the PR. Dash codes:
  - `heat_loss_learning` while `not house_loss_converged(samples)`;
  - `heat_loss_refit_disagrees` while the drift advisor's heat-loss refit (`model_restart_advice(...)["refit"]["scale"]`, the learner's own Newton relation pooled over settled pairs) is non-`None` and departs from the current scale by more than its own `REFIT_BAND_PERCENT`. The bias alarm (`_snapshot_ring.alarmed`) is only the precondition under which the refit is computed; a bias that solar, COP or a sensor raised, and that the refit does not attribute to UA, does not dash the house grade. Read the advice once per cycle; do not run `heat_loss_refit` a second time;
  - `no_house_model` when `loss <= 1e-6`.
  The band (20-100 h) moves only if the owner-bundle measurement shows it miscalibrated. A band change is a behaviour no finding names yet, so report it instead of shipping it.
- Machine: one helper, `_watched_cop_buckets()`, replaces the two inline counts. The `cop_health` learning view counts with `np.isfinite`, and `_scores_view` counts without it. The dash code is `cop_watch_learning`.
- Operation: `no_scored_day` before the first close, and `free_price_reset` after a `SCORE_FREE_SPAN_RESET` reset. Overall: `first_scored_day`, the code the sensor publishes today.
- Sensor: `OptimizationScoreSensor` derives `waiting_for` from `reasons["overall"]` and spells no code of its own, so one `None` has one code. `available` keeps keying on `overall is None`.
- Card: port C3's `readNumber` alone, verbatim from `3930b421a:dev/audit/rounds/round10/D7/arch2-s5/patches/C3_reading_rules.patch`. `liveState` is not ported: its only in-seam reader would be `statNumber`, which already applies the same rule inline, and the other C3 call sites are out of seam. `scoreParts` reads through `readNumber` and carries `reasons[key]`. A null renders as `—` plus `L("score.reason_<code>")` in en and sv. The rest of C3 is out of seam.

```
house_loss_converged ---> learning view (house_heat_loss_learned) --> ModelStatusSensor
        \--> _scores_view --Scores{values, reasons}--> insight.scores --> OptimizationScoreSensor
                ^ _effective_house_heat_loss, model_restart_advice.refit       state | attrs (+waiting_for)
card: statNumber(state) --> headline ; scoreParts(readNumber, reasons) --> hover | breakdown
```

## Alternatives rejected

- **Score in `custom_components/heatpump_optimizer/sensor.py`.** The sensor would need thermal params and the COP baseline, which opens a new read path into coordinator state and gives the payload a second owner.
- **A new pure module `custom_components/heatpump_optimizer/scores.py` (would be new).** The coordinator would shrink, but this adds a tracked file (closure or `INERT` classification, `tests/entities.py`) and churn outside the named seam while R10-LIVESTATE follows on `custom_components/heatpump_optimizer/coordinator.py`. It belongs to the decomposition programme.
- **The card derives the dash from `ModelStatusSensor`.** That would be two sources and a re-implemented rule, which `tests/README.md` says pins nothing.
- **Confidence dash only, keeping the configured coefficient.** This leaves the measured two-zone inflation (the RATIO-SITES carry) in place.
- **Dash on `_snapshot_ring.alarmed` directly.** It is the prediction-temperature bias alarm (`observe_bias`, `BIAS_BAND_C` in `custom_components/heatpump_optimizer/snapshots.py`) and fires on non-UA causes; the owner's "or drifts" names the heat-loss learner, so the refit is the signal.
- **Leave `ModelStatusSensor` on `> 0` for UX-HEALTH to move.** UX-HEALTH owns no backend file; the predicate would live in two groups.

## Sibling sites (class: None read as 0; UA without the learned split)

- Card `Number(attrs.*)` with no null guard: `advisor.refit_title`'s `Number(attrs.current_scale)`, and `Number(attrs.current_setpoint)` and `configured_target` in the advisor rows. These are R10-ADVISOR's seam, so the orchestrator propagates them to ADVISOR's rework; they are not fixed here. `healthModelHtml`'s `num` is already guarded.
- `heat_loss_coefficient * house_heat_loss_scale` occurs in four other places, and three of them are correct:
  - `custom_components/heatpump_optimizer/battery.py` and `custom_components/heatpump_optimizer/optimizer.py` multiply on their single-zone branches only;
  - `custom_components/heatpump_optimizer/sysid.py` `_held_state` is guarded by `two_zone_enabled`;
  - `custom_components/heatpump_optimizer/sysid.py` `HousePlant.of_params` has no branch, but it is out of scope by the refuted D2-s3-73 (RATIO-SITES carry 1).

## Evidence plan

- **Failing tests first:**
  - In `tests/card.mjs`, a fixture with `operation: null` and `machine: null` asserts no `0/100` and the reason text. It reads red on today's `finiteScore`.
  - In the coordinator scores test, a two-zone `ThermalParameters` with `lower_floor_heat_loss_learned != lower_floor_heat_loss`, `_house_heat_loss_samples` set past the convergence threshold and no drift alarm, asserts `envelope == f(_effective_house_heat_loss)`. It is red today on the UA basis alone, and stays green after the dash lands.
- **Harness at both ends:** item 1 reproduces in node without the bundle (`finiteScore` above), and item 2's two-zone basis has RATIO-SITES' measurement (carry 4) with `dev/audit/rounds/round10/study-reseed/live_store.py --ratio-override 1.0`. Only the bundle-dependent arms (the 2.6x drift, the band) need the owner's bundle; the fixer extends `live_store.py`, or adds `dev/audit/harnesses/r10_scores_bundle.py` (not yet in the tree), to print tau and grade on both bases.
- **Null control:** at split ratio 1.0 (`--ratio-override 1.0`), the two bases agree to 0.0, which separates this from a scale-only drift. At `--scale-override 1.0 --ratio-override 1.0` every delta is 0.
- **Consistency test:** in `tests/card.mjs`, for each score key in {value, `null` + each reason}, walk the headline (`statNumber`, state; `null` exactly when `reasons.overall` is present), the hover and the breakdown, and assert one number or one reason. A backend arm in `tests/entities.py` sweeps `_house_heat_loss_samples` across the threshold and asserts `ModelStatusSensor` reads `learned` exactly when `reasons` has no `heat_loss_learning`, and `waiting_for == reasons["overall"]`. The Savings and Advisor arms read the ledger figures without recomputing them (carry 2). Any contradiction they find is a new finding; report it, do not design around it.
- **Goldens:** all five `tests/golden/coord_*.json` fixtures carry `insight.scores` (`envelope: 58.3`, zero learner samples). The convergence dash moves `envelope` to `None` and adds `reasons`. `house_heat_loss_learned` is already `false` at zero samples, so it does not move. This is value-bearing drift, claimed in `tests/golden/claimed_drift.txt` per `dev/governance/rules/claim-files.md`. Card captures may move, which needs `tests/golden/card_claimed_drift.txt`.
- **Mutation proof targets:**
  - the `readNumber` null test in `scoreParts`;
  - the `two_zone_enabled` branch of `_effective_house_heat_loss` as read by `_scores_view`;
  - the comparison in `house_loss_converged`, and the refit-band test;
  - the `reasons` invariant;
  - the `np.isfinite` in `_watched_cop_buckets`.

## Hot files, serial position, carries

- Files touched: `custom_components/heatpump_optimizer/coordinator.py`, `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/payload.py` (not in the roster's `files`; asked) and the card.
- `custom_components/heatpump_optimizer/coordinator.py` is at position 18 of 25 (after R10-SAV-REASONS and R10-ADVISOR; next R10-LIVESTATE and R10-CONFIG-NOTICES). `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` is at position 4 of 5 (after R10-ADVISOR; next R10-UX-HEALTH). R10-LEARNER-ETA (`after: R10-ARCH-SHAPES`) also edits `payload.py` and the learning view, with no edge to this group: dispatch waits on the orchestrator's after-edge.
- `custom_components/heatpump_optimizer/sensor.py` is in the files list but not in `hot_files`. R10-SENSOR-PAYLOAD (`after: R10-SCORES`) edits it too, so keep `OptimizationScoreSensor` hunks inside that class.
- **Owed out:** UX-HEALTH renders `reasons` on the Health tab (its item 5 names "R10-SCORES' dash rule"). The ADVISOR siblings above go to ADVISOR's rework brief, per `dev/governance/rules/finding-propagation.md`, before this merges. Whichever group the orchestrator names owner of learner progress reads `house_loss_converged`.
- **Received:** RATIO-SITES carry (the split) and SAV-BASELINE carry (read, do not recompute).

**Blocker (reported, not designed around):** only the bundle-dependent arms of item 2 (the 2.6x drift magnitude and the 20-100 h band) need the owner's private bundle, which this seat does not have. Until the fixer measures them, those causes stay suspected, and no change rests on them.
