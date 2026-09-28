# Class sweep — "live input with no physical-plausibility bound"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 findings: **D1-s1-03** (verified, medium — `dhw_learning.py`'s draw detector computes
`temp_drop = previous_temp - dhw_temp` and folds it into `energy_kwh` with only a `max(0.0, ...)`
floor at line 389, no ceiling or finite check, so a glitched DHW sensor reading can fold an
arbitrarily large energy figure into the learner) and **D1-s2-02** (verified, medium — the
weather-forecast and ECL110 MQTT parsers accept out-of-range temperature/wind/rain values; the
finder's own harness `tools/audit/round9/D1/s2/parsers.py` measures `poisoned_series` = 8/200 seeded
hostile payloads reaching the solve).

## Enumerator

`tools/audit/round9/D14/sweep/live-input-no-plausibility-bound/enumerate.sh`: family A is the
`temp_drop`/`energy_kwh` grep in `dhw_learning.py`; family B reuses the D1-s2-02 harness
(not re-run here — D3/heavy-rerun rule; its recorded numbers stand); family C widens the seam
rule to every other `float(state.state)`/`float(new_state.state)` parse of a live HA entity
across the package, to check for siblings the two findings did not already cover.

Positive control: family A's grep lines include `dhw_learning.py:389-390` (the finding's own
site); family B is the finder's harness, already re-finding its own seeded instances by
construction.
Null control: family C's widened grep returns exactly the two additional sites below, both of
which already carry a plausibility bound (see disposition) — a fixture with every live-float
parse bound-checked returns 0 `instance` seams.
Perturbation: deleting the `not 0.0 < value <= 100.0` check at `coordinator.py:8248` (or the
`max(0.0, converted)`/`isfinite` check at `:8961-8962`) turns that site into a second family-C
instance under the same grep + a manual bound-presence check — moves 0 → 1.

## Disposition

| seam | disposition | note |
|---|---|---|
| `dhw_learning.py:389-390` (`temp_drop`/`energy_kwh` fold, `max(0.0, ...)` floor only) | **instance** | D1-s1-03 itself — no ceiling or finite check on the computed energy. |
| weather-forecast + ECL110 parsers (D1-s2-02, harness `tools/audit/round9/D1/s2/parsers.py`) | **instance** | D1-s2-02 itself — `poisoned_series=8/200` at baseline. |
| `coordinator.py:8245` humidity entity float parse | **guarded** | Bound-checked two lines down: `not np.isfinite(value) or not 0.0 < value <= 100.0` returns `None`. |
| `coordinator.py:8957` PV production entity float parse | **guarded** | Bound-checked: `isfinite(converted)` check plus `max(0.0, converted)` floor after unit conversion. |

## Count

N = 2 verified findings + 0 additional sweep-confirmed instances (the widened family-C grep found
only two more live-float parse sites, both already guarded). **rca = false** (N=2 < 3, not a
ledger class, not barriered).

## Barrier proposal

Extend `tests/structure.py`'s counting rule (or a new lightweight `tests/live_input_bounds.py`)
to require every function that parses a live entity's `.state` to a float, or that derives a
folded value from two such parses, to be followed (within the same function) by an
`np.isfinite`/range check before the value is stored or fed to a learner. Estimated gate cost:
under 1s (AST scan of `custom_components/heatpump_optimizer/*.py`, no HA boot).
