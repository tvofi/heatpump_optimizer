# Sweep: N-silent-zero (round 10, PLAN phase D)

Class status in `dev/audit/config/bugclasses.json`: `barriered` -- but the barrier
(`field_coverage.mjs --only census`) covers the **instrument** arm only (registered
count-printing tools). D1-s3-01 is the **production** arm: an ingress parse whose
empty result is stored as success. Nothing in CI reaches that arm.

## Property
An ingress seam (a function reading an HTTP session, a `return_response` service
call, `pull_prices` or an Open-Meteo fetch) that assigns the parsed value to
`self.<attr>` must refuse an empty parse -- the assignment sits under an `if` on
the very value assigned. Otherwise an empty parse replaces held data and the
fetch reads as success (outage/stale latch cleared).

## Enumerator
`python3 dev/audit/rounds/round10/D14/sweep-N-silent-zero/enumerate.py` (AST, whole package).

| arm | command | result |
|---|---|---|
| baseline | `enumerate.py` | seams=4, unguarded=2 |
| positive control | baseline lists `coordinator.py:6386 _fetch_tibber_prices` UNGUARDED | re-finds D1-s3-01 |
| null control | `enumerate.py --null` (guarded fixture) | unguarded=0 |
| perturbation | `enumerate.py --perturb` (drops open_meteo's `if forecast:`) | unguarded=3 (+1) |

## Seams and disposition

| seam | disposition |
|---|---|
| `coordinator.py:6386` `_fetch_tibber_prices` `self._prices = payload` | **instance** (D1-s3-01, judged site). Probe `D1/s3/tibber_ingress.py`: empty_ok_wipes=1, `--perturb` 0. The entity source reaches the same line but is refused upstream (`prices_from_entity_attributes` returns a reason on no rows); the Tibber parser has no such check. |
| `coordinator.py:6487` `_fetch_weather_forecast` `self._weather_forecast = _plausible_forecast_rows(...)` | **instance, beyond the finding.** The guard `if forecast_data:` tests the raw rows, not the filtered output; 48 non-dict rows pass it, filter to `[]`, are stored over a good 48-row forecast and `_weather_fetch_recovered()` clears `_weather_stale_since`. Probe `D14/sweep-N-silent-zero/weather_probe.py`: empty_ok_wipes=1 (before=48, after=0, stale=None); `--perturb` (refuse an empty filtered result) gives 0 with the forecast kept and marked stale. |
| `open_meteo.py:356` `async_refresh` `self._forecast = forecast` | **guarded**: `if forecast:`; `_last_success` set only when `forecast or observed`. |
| `open_meteo.py:360` `async_refresh` `self._observed = observed` | **guarded**: `if observed:`. |

Not applicable (outside the seam definition, checked by reading): `config_flow.py:462`
`resp.json()` validates a token and stores no state; `self._last_attempt = now` /
`_last_success = now` are clocks, excluded by the enumerator.

## Proposed barrier
Move `enumerate.py` into `tests/` as a lint script asserting `unguarded == 0`
after the two instances are fixed (both fixes: refuse an empty parsed list as a
failed fetch -- in `prices_from_tibber_payload` and after `_plausible_forecast_rows`).
Cost: one AST pass, under 1 s gate time. Limit: the guard match is syntactic (an
`if` naming the assigned expression); a seam storing through a helper is not seen.
