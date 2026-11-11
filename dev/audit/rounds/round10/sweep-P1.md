# Round 10 class sweep — P1 (D14 steps 3–4)

Class P1 (`dev/audit/config/bugclasses.json`): a malformed or out-of-domain value
crosses an input boundary with no guard. Ledger status: store-read seams are
barriered (`QuarantiningStore._sanitize`, `tests/finite_boundary.py` Arm 4); the
live-feed plausibility boundary is not. The surviving finding is live-feed.

Finding: **D1-s3-02** (weakened, low) — Tibber rows with no `startsAt` are admitted
with `starts_at=""`; with none parseable `_known_prices_for` places them by
position as hourly, 95 of 96 steps misplaced. Needs a malformed feed no observed
source sends.

## Seam rule and enumerator

Seam: a function in `custom_components/heatpump_optimizer` that reads a timestamp
key off a row (`starts_at`, `startsAt`, `start`, `datetime`, `time`, `t`, `end`, …).
Flagged `ADMIT` when the read carries a literal `""`/`None` fallback (row kept with
no usable stamp), `POSITIONAL` when the function places raw rows by list position
once none parsed (a `range(4)`/`* 4` hourly stretch, or `_prices[0]`/`forecast[0]`).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P1/p1_ts_seams.py`
→ `seams_total=19`, `seams_flagged=6`.

- Positive control: re-finds both sites of D1-s3-02 (`prices_from_tibber_payload`
  ADMIT, `_known_prices_for` POSITIONAL).
- Null control: `--null` (clean drop-on-unparseable fixture) → `seams_flagged=0`.
- Perturbation: `--perturb` (one line, `r.get("startsAt") or ""`) → `seams_flagged=1`.

## Dispositions (all 19)

| seam | disposition |
|---|---|
| `price_model.prices_from_tibber_payload` | **instance** (finding site) — `D1/s3/tibber_ingress.py` startless_rows=96 |
| `coordinator._known_prices_for` | **instance** (finding site) — same probe, misplaced_steps=95 |
| `coordinator._current_spot_price` | **instance, beyond the finding** — `D14/sweep-P1/probe_spot_head.py`: startless rows, clock 12:00, returns row 0 (1.0) not row 48 (1.48); spot_wrong=1, `--perturb` 0 |
| `coordinator._weather_series` | guarded — positional fallback is hourly-from-now and the fetch requests `"type": "hourly"` (coordinator.py `weather.get_forecasts` call), so the assumption matches the contract asked for |
| `coordinator.forecast_outdoor_now` | guarded — same hourly request; positional entry 0 is the row covering now |
| `away._holiday_span` | not applicable — one calendar event's span, not a row series; a missing start/end is the documented "now" default |
| `price_model.prices_from_entity_attributes` via `_raw_start` | guarded — `start is None` row dropped |
| `price_model._entries_by_day` | guarded — `not starts_at` / `fromisoformat` failure → `continue` |
| `open_meteo._parse_block` | guarded — `fromisoformat` failure → `continue` |
| `coordinator._current_humidity` | guarded — unparseable stamp gets infinite distance, never preferred over a dated row |
| `accuracy.from_dict`, `debugger._repair`, `debugger.feed_health` | guarded — store reads through `stored_instant` / Arm 4 barrier |
| `binary_sensor._plan_outdoor_now`, `notifier._comfort`, `notifier._comfort_cause`, `sensor.extra_state_attributes`, `wood_fuel._wood_slots_error`, `wood_fuel.wood_slots_to_kw` | not applicable — read the integration's own plan/slot rows, not an input boundary |

## Count and barrier

3 instance seams, 1 beyond the finding; all three share one root: the Tibber
ingress admits a row whose `startsAt` does not parse. Proposed barrier: refuse such
rows in `prices_from_tibber_payload` (as `prices_from_entity_attributes` already
does via `_raw_start`), returning a failure reason when none remain; then delete
the price-side positional fallbacks. Fits in `tests/finite_boundary.py` as a
live-ingress arm (dateless row → zero admitted). Not barriered today.
