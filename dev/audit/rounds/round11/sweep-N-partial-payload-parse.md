# Class sweep: N-partial-payload-parse (round 11, PLAN phase D)

Mechanism: a parser reads one part of an external payload and drops a sibling
part the producer delivers. Class is not yet in `dev/audit/config/bugclasses.json`
(new this round). Finding: D2-s3-03.

## Enumerator
`python3 dev/audit/rounds/round11/D14/sweep_partial_payload.py [PACKAGE_DIR]` —
lists each external-payload parsing seam with the sibling keys its producer
writes and flags any sibling the parser never names. Started from D2-s3-03's
seam_rule (`for period in|raw_tomorrow` in price_model.py), widened to every
external-payload parser in the package.

- Positive control: on a copy with `for period in ("today",)` re-planted (the
  finding's state) it reports `INSTANCE prices_from_tibber_payload missing=['tomorrow']`, exit 1.
- Null control: on the register head it reports `instances=0`, exit 0.
- Perturbation: the one-line re-introduction above moves the count 0 -> 1.

## Dispositions (register head 28b864af6d)
| seam | disposition |
|---|---|
| price_model.py `prices_from_tibber_payload` | guarded: iterates `("today", "tomorrow")` (line 720); D2-s3-03's site, already reading both at its own baseline 92d38ecb — the finding measured a planted copy |
| price_model.py `prices_from_entity_attributes` | guarded: reads `raw_today, raw_tomorrow, today, tomorrow` (line 795) |
| open_meteo.py `_fetch_forecast` | guarded: reads `minutely_15` and `hourly`; prefers fine only when it ends within 6 h of coarse, and `forecast_days=3` (~72 h) covers the 48 h solar view, so no horizon loss |
| coordinator.py `_fetch_weather_forecast` | not applicable: `weather.get_forecasts` hourly returns one `forecast` list, no sibling part |
| replay_doc.py redaction keys | guarded: names all four price keys (line 78/316) |

Instances beyond the finding: 0. Proposed barrier: run the enumerator as a
`tests/` check (sub-second).
