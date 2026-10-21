# R10-SCORES design note (designer seat, DRAFT contract at ddacf9856)

The group's architect note, extended. It lives on `design/r10-scores` only and is never merged. Size L, issues #2238 and #2258; findings: owner items 1-3 and ARCH2-s5-C3.

**Read at.** Code: R10-ADVISOR's handoff head `cd1c837cabe9536b27a7d36d193d5f4e24d23deb` (PR #2572, in rework). `origin/main` is `f2fb1b0e950ecd047b7f08b3adef93776a622540`. R10-RATIO-SITES is done at `8c6d940b0`. Between the ADVISOR merge base `265d3bf1a` and main, nothing changed in `custom_components/heatpump_optimizer/coordinator.py`, `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/payload.py` or the card. ADVISOR does not touch the code below. It edits `_insight_view`'s `price_tiles` line and the card's `priceTiles` block next to `scoreBreakdownHtml`. Re-read both after it merges (step 9).

## Causes, measured at cd1c837ca

1. **Item 1: a heat-pump score of 0 with no COP evidence is a card defect.** `_scores_view` in `custom_components/heatpump_optimizer/coordinator.py` publishes `machine: None` until one COP bucket has `COP_BASELINE_MIN_SAMPLES`. `OptimizationScoreSensor` in `custom_components/heatpump_optimizer/sensor.py` spreads `None` into its attributes as JSON `null`. The card's `finiteScore` (in `scoreParts`) calls `Number(v)`, and `Number(null)` is `0`. Run in node, `finiteScore(null)` returns `0`, and `finiteScore(undefined)` returns `null`. So both the breakdown and the hover print `0/100`. `tests/card.mjs` misses this because its fixture omits `operation` (undefined) and never publishes it as `null`. ARCH2-s5 C3's `readNumber` is the rule that fixes it.
2. **Item 2: the house score reads the wrong UA basis.** `_scores_view` grades `heat_loss_coefficient * house_heat_loss_scale`. `_effective_house_heat_loss` (same file) is the model's own figure: on a two-zone house it adds the learned lower-floor split. The Health tab publishes that figure as `ModelStatusSensor.heat_loss_w_per_k`. Two more causes are to be measured, not assumed (carry 1): the drift of about 2.6x, and the 20-100 h band. Nothing gates the grade on how far the learner has converged.
3. **Item 3: three surfaces, no shared reason.** The headline value, its hover and the breakdown read the score sensor. The Health tab's waiting row (`HEALTH_WAITING`, `score`) and its model rows read `ModelStatusSensor`. When a score is `None`, nothing says *why*, so each surface invents its own words.

## Owning seam

**`HeatPumpOptimizerCoordinator._scores_view` is the one owner of the score view model** (`Scores` in `custom_components/heatpump_optimizer/payload.py`). `OptimizationScoreSensor` only republishes it. The card's `scoreParts` is the only card reader, and the headline, hover and breakdown all go through it. The Health tab rows belong to R10-UX-HEALTH (carry 3), which consumes the reasons published here. `_close_score_day` keeps the operation EMA, with no change in shape. This needs one owner per concern, so no second owner is required.

## Shape

- `Scores` gains `reasons: dict[str, str]`, holding exactly one code for each key whose value is `None`. The existing numeric keys keep their names and types, so automations do not break. The invariant is that `value is None` if and only if `key in reasons`, and no score is ever `0` for want of evidence.
- Envelope: `loss = _effective_house_heat_loss(ctx._thermal_params, scale)`, the same call the learning view makes. Keep the `max(scale, 0.1)` floor only if the `_apply_*` clamp does not already bound it, and say which in the PR. Dash codes:
  - `heat_loss_learning` while `house_loss_confidence(samples)` is below a threshold the fixer derives from the learner's own constant (no new tuning literal);
  - `heat_loss_drifting` while `_snapshot_ring.alarmed` is set;
  - `no_house_model` when `loss <= 1e-6`.
  The band (20-100 h) moves only if the owner-bundle measurement shows it miscalibrated. A band change is a behaviour no finding names yet, so report it instead of shipping it.
- Machine: one helper, `_watched_cop_buckets()`, replaces the two inline counts. The `cop_health` learning view counts with `np.isfinite`, and `_scores_view` counts without it. The dash code is `cop_watch_learning`.
- Operation: `no_scored_day` before the first close, and `free_price_reset` after a `SCORE_FREE_SPAN_RESET` reset. Overall: `no_evidence`.
- Card: port C3's `liveState` and `readNumber`, and only these, verbatim from `dev/audit/rounds/round10/D7/arch2-s5/patches/C3_reading_rules.patch`. `scoreParts` reads through `readNumber` and carries `reasons[key]`. A null renders as `—` plus `L("score.reason_<code>")` in en and sv. The rest of C3 is out of seam.

```
_scores_view --Scores{values, reasons}--> insight.scores --> OptimizationScoreSensor attrs
   ^ _effective_house_heat_loss (shared with learning view -> ModelStatusSensor)
card scoreParts(readNumber) --> headline value | hover | breakdown ;  UX-HEALTH --> Health rows
```

## Alternatives rejected

- **Score in `custom_components/heatpump_optimizer/sensor.py`.** The sensor would need thermal params and the COP baseline, which opens a new read path into coordinator state and gives the payload a second owner.
- **A new pure module `custom_components/heatpump_optimizer/scores.py` (would be new).** The coordinator would shrink, but this adds a tracked file (closure or `INERT` classification, `tests/entities.py`) and churn outside the named seam while R10-LIVESTATE follows on `custom_components/heatpump_optimizer/coordinator.py`. It belongs to the decomposition programme.
- **The card derives the dash from `ModelStatusSensor`.** That would be two sources and a re-implemented rule, which `tests/README.md` says pins nothing.
- **Confidence dash only, keeping the configured coefficient.** This leaves the measured two-zone inflation (the RATIO-SITES carry) in place.

## Sibling sites (class: None read as 0; UA without the learned split)

- Card `Number(attrs.*)` with no null guard: `advisor.refit_title`'s `Number(attrs.current_scale)`, and `Number(attrs.current_setpoint)` and `configured_target` in the advisor rows. These are R10-ADVISOR's seam, so the orchestrator propagates them to ADVISOR's rework; they are not fixed here. `healthModelHtml`'s `num` is already guarded.
- `heat_loss_coefficient * house_heat_loss_scale` occurs in four other places, and three of them are correct:
  - `custom_components/heatpump_optimizer/battery.py` and `custom_components/heatpump_optimizer/optimizer.py` multiply on their single-zone branches only;
  - `custom_components/heatpump_optimizer/sysid.py` `_held_state` is guarded by `two_zone_enabled`;
  - `custom_components/heatpump_optimizer/sysid.py` `HousePlant.of_params` has no branch, but it is out of scope by the refuted D2-s3-73 (RATIO-SITES carry 1).
- Sensor: `OptimizationScoreSensor.available` already keys on `overall is None`. Keep `waiting_for`.

## Evidence plan

- **Failing tests first:**
  - In `tests/card.mjs`, a fixture with `operation: null` and `machine: null` asserts no `0/100` and the reason text. It reads red on today's `finiteScore`.
  - In the coordinator scores test, a two-zone `ThermalParameters` with `lower_floor_heat_loss_learned != lower_floor_heat_loss` asserts `envelope == f(_effective_house_heat_loss)`. It is red today.
- **Harness at both ends:** the owner-reported items have no finder harness. The RESEED harness `dev/audit/rounds/round10/study-reseed/live_store.py` reads the owner's bundle (never committed) for item 2. The fixer extends it, or adds a new harness `dev/audit/harnesses/r10_scores_bundle.py` (not yet in the tree), to print tau and grade on both bases.
- **Null control:** at split ratio 1.0 (`--ratio-override 1.0`), the two bases agree to 0.0, which separates this from a scale-only drift. At `--scale-override 1.0 --ratio-override 1.0` every delta is 0.
- **Consistency test:** in `tests/card.mjs`, for each score key in {value, `null` + each reason}, walk the headline, the hover and the breakdown, and assert one number or one reason. The Savings and Advisor arms read the ledger figures without recomputing them (carry 2). Any contradiction they find is a new finding; report it, do not design around it.
- **Goldens:** all five `tests/golden/coord_*.json` fixtures carry `insight.scores` (`envelope: 58.3`, zero learner samples). The convergence dash moves `envelope` to `None` and adds `reasons`. This is value-bearing drift, claimed in `tests/golden/claimed_drift.txt` per `dev/governance/rules/claim-files.md`. Card captures may move, which needs `tests/golden/card_claimed_drift.txt`.
- **Mutation proof targets:**
  - the `readNumber` null test in `scoreParts`;
  - the `two_zone_enabled` branch of `_effective_house_heat_loss` as read by `_scores_view`;
  - the `reasons` invariant;
  - the `np.isfinite` in `_watched_cop_buckets`.

## Hot files, serial position, carries

- `custom_components/heatpump_optimizer/coordinator.py` is at position 18 of 25 (after R10-SAV-REASONS and R10-ADVISOR; next R10-LIVESTATE and R10-CONFIG-NOTICES). `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` is at position 4 of 5 (after R10-ADVISOR; next R10-UX-HEALTH).
- `custom_components/heatpump_optimizer/sensor.py` is in the files list but not in `hot_files`. R10-SENSOR-PAYLOAD (`after: R10-SCORES`) edits it too, so keep `OptimizationScoreSensor` hunks inside that class.
- **Owed out:** UX-HEALTH renders `reasons` on the Health tab (its item 5 names "R10-SCORES' dash rule"). The ADVISOR siblings above go to ADVISOR's rework brief, per `dev/governance/rules/finding-propagation.md`, before this merges.
- **Received:** RATIO-SITES carry (the split) and SAV-BASELINE carry (read, do not recompute).

**Blocker (reported, not designed around):** item 2 is quantified only on the owner's private bundle, which this seat does not have. Until the fixer measures it, the band and the drift causes stay suspected, and no change rests on them.
