# D8-s3 — round 10, steps D8.M4 and D8.M5 (baseline 17f1c55fad1b)

Exposure: none.

## Method
`first_hour.py` builds the ordinary install (the #1335 recipe of tests/entities.py:
`_honest_coordinator` config + injected 48 h prices/forecast/sun), collects all six
platforms through the real `async_setup_entry` (81 entities, 61 enabled), parses the
card's full dependency set (literal ids, DEFAULTS, every `statEntity/statNumber/derive`
suffix and the HEADLINE/ADVISOR/HEALTH suffix tables: 27 ids) and the README, and
prints one RESULT per violation class (M5: deterministic, no network).

## Findings
None.

## Non-findings
- Every card-addressed id resolves to a constructed entity: card_missing=0.
- card_disabled=3 (dhw_temperature, lower_floor_temperature, valve_target_recommendation),
  each unavailable on the ordinary install and gated on its configured input (DHW probe,
  lower-floor probe, throttling valve mode); the card treats them as optional probes /
  advisors. Perturbation `--perturb` (ConfiguredInputMixin default forced True) moves
  card_disabled 3 -> 2, so the harness is live.
- Enabled but named by neither card nor README: 1, climate.heat_pump_optimizer, a
  harness gap (it has no translation-key name; README mentions the thermostat).

## Leads
- tests/entities.py `_card_ids` (#1335 check): the narrow parse sees 10 of the card's
  27 dependency ids (narrow_parse_ids=10); ADVISOR/HEALTH suffixes and statEntity/derive
  literals (e.g. `_learning_model_status`, `_optimization_status`) are unprotected — a
  flip to disabled would pass. Owner D3.

## Harnesses
- dev/audit/rounds/round10/D8/s3/first_hour.py
