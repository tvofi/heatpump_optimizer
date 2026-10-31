# Class sweep: N-no-expiry (round 10, phase D)

Mechanism: a last-known value is published and booked as current with no age
bound once its source stops updating. Finding: D1-s2-02 (`_current_spot_price`).
Class status in `dev/audit/config/bugclasses.json`: **absent** — the ledger has
`N-staleness` but no `N-no-expiry` entry; the class is unbarriered.

## Enumerator (D14 step 3)

`python3 dev/audit/rounds/round10/D14/sweep_n_no_expiry.py` — AST scan of every
module under `custom_components/heatpump_optimizer/` for `bisect_right(...) - 1`
("the entry covering now"), flagging a function `UNBOUNDED` when no comparison
bounds the found entry in time (`end`, `timedelta`).

| control | command | result |
|---|---|---|
| package | (no flag) | seams=9, unbounded=6 |
| positive | package run | re-finds `coordinator.py:7017 _current_spot_price UNBOUNDED` (D1-s2-02) |
| null | `--null` (clean end-bounded fixture) | unbounded=0 |
| perturbation | `--perturb` (drop `if step_start >= end: break` from `_known_prices_for`, one line) | unbounded 0 -> 1 |

Limits: the seam rule covers bisect lookups only; a last-known scalar cache
without a series is outside it. The `bounded` flag is a heuristic — `_share`
reads bounded on a `timedelta` compare that is not an end bound; its
disposition below rests on its guard, not on the flag.

## Dispositions (D14 step 4)

| seam | flag | disposition |
|---|---|---|
| `coordinator.py:7017 _current_spot_price` | UNBOUNDED | **instance** (the finding) — `D1/s2/stale_price.py`: 4/4 uncovered cycles publish and book |
| `coordinator.py:640 forecast_outdoor_now` | UNBOUNDED | **instance** — `D14/probe_n_no_expiry.py`: 47 h past a forecast's last entry returns 0.0 (finite), written to `outdoor_temperature` when the outdoor sensor is not ok (line 6005) and published as `outdoor_forecast_temperature` (7627) |
| `coordinator.py:1782 _open_loop_plan_value` | UNBOUNDED | **instance** — same probe: 47 h past the plan's end returns 44.5, seeding `dhw_temperature` (6092) and the 6249 seed with no `_plan_is_stale` gate |
| `coordinator.py:6807 _weather_series` | UNBOUNDED | not applicable — builds the future horizon, flat padding past the forecast is its documented extrapolation, never published as a current value; its stalled-forecast case is the `forecast_outdoor_now` instance |
| `coordinator.py:6716 _known_prices_for` | bounded | guarded — `if step_start >= end: break` (the perturbation target) |
| `pump_arbiter.py:348 step_duty` | bounded | guarded — `now - stamps[i] > timedelta(minutes=15)` returns None past the last step |
| `pump_arbiter.py:414 _planned_room` | UNBOUNDED | guarded — called from `desired`/`_space_target` and the DHW lease (720) on a duty from `step_duty`, which is None past the plan end; 687 also gates on `plan_stale` |
| `pump_arbiter.py:997 _share` | bounded* | guarded — runs only on `duty == "both"`, from `step_duty` |
| `early_cutoff.py:249 _planned_room` | UNBOUNDED | guarded — `0 <= i < len(trajectory) - 1` returns [] at and past the last step |

Instances: 3 (1 the finding, 2 beyond it). Proposed barrier: a `tests/` lint
over this enumerator refusing an `UNBOUNDED` seam not on a reviewed allow-list
(the not-applicable horizon builder), plus a covering-slot end bound on the three
instances; cost under one gate second (pure AST).
