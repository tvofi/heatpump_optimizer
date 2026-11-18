# Class sweep: N-event-misattribution (round 11, PLAN phase D)

Class status: not yet in `dev/audit/config/bugclasses.json` (new this round; finding D2-s3-08 `class_guess: new`).

## Enumerator
`bash dev/audit/rounds/round11/D14/enum_event_misattribution.sh [pkg]` — greps every seam that labels a discrete
event from a sensor signature and books it into a counter or statistic (draw folds, charge-settle classify/advance,
start-counter edges, defrost event counts, immersion/external-heat/outage detectors), seeded from D2-s3-08's seam_rule.

- **Positive control**: lists `dhw_learning.py:468` (`charge=started_heated or settling`), `:120 advance`, `:480 async_fold_draw_stats` — the D2-s3-08 site; its harness `m5_tankfall.py` re-reproduces booked_kwh_long_max=3.0160 kWh (short 0.0389).
- **Null control**: on a clean one-function fixture the enumerator returns 0 lines.
- **Perturbation**: adding the one line `f(charge=started_heated or settling)` to that fixture moves it 0 -> 1. The finding harness under `--perturb-skip-heated` moves 3.0160 -> 0.0000 kWh.

## Disposition of every seam returned (21 lines)
| seam | disposition |
|---|---|
| dhw_learning.py `async_fold_draw_stats`, `ChargeSettle.advance`, call at :468 | **instance** = D2-s3-08 site (probe: m5_tankfall.py, 3.016 kWh on zero draw). Not beyond the finding. |
| dhw_learning.py `ChargeSettle.classify` | part of the same instance (it feeds `advance`); not counted separately |
| dhw_learning.py `async_learn_usage` | guarded: returns on `heated`, and the caller skips `settling` intervals; deferred falls reach it only after ChargeSettle releases them |
| dhw_draws.py `DrawStats.fold` | guarded downstream sink: books what the caller labels; the misattribution is upstream (instance above) |
| wear.py `StartCounter.hear` / `fold` | guarded: `EDGE_DEBOUNCE_S` 30 s debounce, `RiseHold` two-refresh hold (S7), `None` edge never books a start |
| defrost.py `observe_duty` / `duty_events` (:430, :648) | guarded: events are the pump's own reported defrost starts, not inferred from a signature |
| coordinator.py `_detect_immersion` (:9087, :9108) | guarded: two agreeing samples latch, two clear release; booster books on rising edge only |
| coordinator.py `_update_external_heat_detection` | guarded: stale wood-furnace probes map to absence via InputReader; rise inputs take probes only, never the plan's seed |
| coordinator.py `_detect_outage` | not applicable: a tick gap is a direct timestamp measurement, not a sensor-signature label |
| draw_range.py `fold` | not applicable: folds running-power samples (frozen/distorted/defrost excluded), no event label |
| heat_curve.py `classify` | not applicable: compares a read-back against our own written value; no physical event inferred |
| driving_grade.py, price_model.py, price_tiles.py `fold` | not applicable: price/grade arithmetic, no sensor event |

## Result
One instance, the judged site itself; **0 instances beyond the finding**. No barrier exists (`barriered: false`).
Proposed barrier: promote `m5_tankfall.py` (long-charge cell, identity 0 kWh) into a `tests/` script on the DHW closure.
