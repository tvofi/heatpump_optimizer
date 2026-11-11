# D1-s3 report (round 10, baseline 17f1c55fad1b)

Cells: D1.M5, D1.M6 over `**`. Exposure: none.

## Method
Drove the real `HeatPumpOptimizerCoordinator._fetch_tibber_prices` (FakeHass, fake aiohttp
session returning HTTP 200 bodies) and fuzzed three external parsers with 400 seeded hostile inputs.

## Findings
- D1-s3-01: an HTTP-200 Tibber response with empty `today`/`tomorrow` is accepted as success;
  the 96-row good list is replaced by 0 rows, the outage latch clears, no UpdateFailed.
  `tibber_ingress.py` RESULT empty_ok_wipes=1 (perturbed: 0). The entity path refuses the same case.
- D1-s3-02: Tibber rows with no `startsAt` are admitted with `starts_at=""`; with none parseable,
  `_known_prices_for` falls back to positional hourly placement, stretching each quarter row over
  4 steps. RESULT startless_rows=96, misplaced_steps=95 of 96 (perturbed: 0, 0).

## Non-findings
- `open_meteo._parse_block`, `coordinator._plausible_forecast_rows`: 0 raises, 0 non-finite outputs
  over 400 hostile inputs (`parser_fuzz.py`; perturbation removing the isfinite drop gives nonfinite_om=39).
- `prices_from_tibber_payload` raises on 207/400 shapes (`data: null`, a non-dict home); every one is
  contained by `_fetch_tibber_prices`' generic except into UpdateFailed with one ERROR (latch).

## Unfinished
- D1.M5 (guards): only spot — the Tibber except arm. The full swallow-site inventory with injected exceptions is not done.
- D1.M6: ECL110 MQTT handler, pump-signal states and weather-entity forecast through the real fetch not driven.

## Harnesses
`tibber_ingress.py`, `parser_fuzz.py` (this directory).
