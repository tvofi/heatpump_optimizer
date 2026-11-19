# Class sweep N-no-expiry, round 11 (D14 method steps 3-4)

Mechanism: a last-known value is published and booked as current, with no age
bound, once its source stops updating. Ledger status at intake: `barriered`
(R10). The barrier is `tests/entities.py` "R10 N-no-expiry barrier", and it
covers only `bisect_right(...) - 1` lookups (family B below).

Judged findings: D1-s2-02, D1-s2-03, D14-s2-02, D7-s3-03.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-N-no-expiry/enumerate.py`

It reads the whole package by AST and puts each seam in one of four families,
counted once per (family, module, function):

- **A**: `hass.states.get` outside `inputs.py`, in a function that names an
  age-bounded slot (`const.INPUT_MAX_AGE_MINUTES`) or a meter, power or PV
  entity, and never calls `age_of`, `state_age`, `InputReader` or `read_state`.
- **B**: `bisect_right(...) - 1`, the entry covering now.
- **C**: a constant `[0]` read of a held forecast, weather, rows or series
  container.
- **D**: a feed success branch that clears its stale latch
  (`*_fetch_recovered()`).

Controls, from `--self-test`, which reads `SELF-TEST PASS`:

- **Positive control**: it re-finds 5 of 5 finding sites. D7-s3-03 has two
  sites.
- **Null control**: a clean fixture lists 0 seams.
- **Perturbation**: one planted line in each family moves the count by exactly
  +1 (A, B, C and D each read 1).

## Dispositions (15 seams)

| fam | seam | disposition |
|---|---|---|
| A | `running_signal.py::source` / `reader` | **instance, beyond the findings.** The meter is read with `state_power_kw(states.get(meter))`. The 30-min limit is never applied, so a frozen 2.0 kW meter books the compressor as running on every refresh. Probe P1 fails. |
| A | `early_cutoff.py::_plant_exempt` | **instance, beyond the findings.** A defrost flag stuck at `on` past its 30-min limit exempts the plant from early cutoff for as long as it stays stuck. The sibling `pump_arbiter._lit` reads the same slot fresh-only. Probe P2 fails. |
| A | `coordinator.py::_pv_measured_production` | instance: D1-s2-02 |
| D | `coordinator.py::_fetch_weather_forecast` | instance: D1-s2-03 |
| C | `coordinator.py::_current_weather` | instance: D14-s2-02 |
| B | `early_cutoff.py::_planned_room` | instance: D7-s3-03 |
| B | `pump_arbiter.py::_planned_room` | instance: D7-s3-03 |
| B | `coordinator.py::_covering_index` | guarded: its end bound is `now < starts[i] + span` (R10 #2229), and the R10 barrier pins it |
| B | `pump_arbiter.py::_step_index` | guarded: it returns `None` past the last step (#2492) |
| B | `pump_arbiter.py::_share` | guarded: it runs only for `duty == "both"`, which comes from `step_duty`, and that is `None` past the plan end. It is on the barrier's reasoned list. |
| B | `coordinator.py::_weather_series` | not applicable: it builds the future horizon, and padding past the last row is documented extrapolation that is never published as current. The staleness of its input is D1-s2-03's seam. |
| C | `coordinator.py::forecast_outdoor_now` | guarded: it indexes through `_covering_index`, and `[0]` is the before-first branch. D14-s2-02 measures it at 0 of 72 mismatches. |
| D | `coordinator.py::_fetch_tibber_prices` | guarded: the D1-s2-03 harness drives it with a reply that no longer covers now, and it holds |
| C | `optimizer.py::_thermostat_held_state` | guarded by construction: step 0 of the weather series is the step covering now, built by `_weather_series`. Whether that row's source is stale is D1-s2-03's seam. |
| C | `notifier.py::_manual` | not applicable: `rows[0]["reason"]` labels a manual-plan release event and is never a value booked as current |

## Probes for the instances beyond the findings

`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round11/D14/sweep-N-no-expiry/probes.py`

| state age | P1 | P2 | result |
|---|---|---|---|
| 1440 min (stale) | FAIL, `kw=2.0` | FAIL, `reason=defrost` | `stale_values_used=2 of 2` |
| 0 min (null control) | PASS-null | PASS-null | 0 |

## Barrier proposal

`barriered: false`. The R10 barrier covers family B only. Families A, C and D
let two production instances through in this round.

The proposed barrier is a `tests/entities.py` check that runs this
enumerator's families A, C and D against a reasoned allow-list, in the same
shape as `_R10_COVERING_ALLOWED`. It would be AST-only, about 0.2 s of gate
time.

The fix route for both new instances is the same: read the slot through
`InputReader` (as `pump_arbiter._lit` already does for the defrost flag), or
apply `age_of` against `INPUT_MAX_AGE_MINUTES`.
