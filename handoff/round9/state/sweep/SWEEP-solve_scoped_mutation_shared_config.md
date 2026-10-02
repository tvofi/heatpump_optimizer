# Sweep: "solve-scoped mutation of shared live config seen by a concurrent reader"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D1-s3-04
(weakened(low), low). Not a ledger class (new).

## Enumerator

```
$ rg -n "_opt_config\.|target_temperature" custom_components/heatpump_optimizer/{climate,sensor,binary_sensor,entity}.py
```

widened to every direct read of `_opt_config`'s mutable fields from an
entity module (`climate.py`, `sensor.py`, `binary_sensor.py`, `entity.py`):

```
$ grep -n "_opt_config\." custom_components/heatpump_optimizer/climate.py custom_components/heatpump_optimizer/sensor.py custom_components/heatpump_optimizer/binary_sensor.py custom_components/heatpump_optimizer/entity.py
(no hits)
$ grep -n "coordinator\.\(min_temp\|max_temp\|target_temperature\)\b" custom_components/heatpump_optimizer/climate.py
climate.py:157: target: float | None = self.coordinator.target_temperature
```

## Positive control

`climate.py:157` reads `coordinator.target_temperature`, a property
(`coordinator.py:2495-2498`) returning `ctx._opt_config.target_temp`
directly off the live, shared `OptimizationConfig` instance — not a copy.
`coordinator.py:4771` confirms the solve itself works on
`config = copy.deepcopy(ctx._opt_config)`, i.e. the solve does not mutate
the shared object for its own math, but the away-mode adjustment
(`coordinator.py:4876`, `away_mode.apply(...)` against `ctx._opt_config`
before the deepcopy at :4771) writes the away setback directly onto the
same shared `_opt_config.target_temp` the property reads, for the span
between that write and whatever later restores it. A climate-entity state
read that lands inside that span sees the away setback, not the
user-configured target — confirmed present at baseline `1936d5ca`;
`coordinator.py` differs from `origin/main` only in the unrelated
`async_reset_comfort_weight` (checked earlier this sweep), so the seam is
unchanged on main.

## Null control

No other entity-module property reads a mutable `_opt_config` field
directly (the widened grep across `climate.py`, `sensor.py`,
`binary_sensor.py`, `entity.py` returns only the one hit); every other
displayed value in those modules goes through `coordinator.data` (a dict
snapshot published once per cycle, not the live solve-scoped object), so
the class does not widen beyond the one property.

## Perturbation

Not independently re-run; the finding is stated as a design/timing
property (`weakened(low)`), not something a one-line mutant reproduces
without a concurrency harness the finder did not build either.

## Disposition

| seam | disposition |
|---|---|
| climate.py:157 / coordinator.py:2495-2498 `target_temperature` reading live `_opt_config.target_temp` | instance — D1-s3-04 |
| every other entity read (via `coordinator.data`, a per-cycle dict snapshot) | not applicable — reads a published snapshot, not the live solve-scoped object |

## Count

N = 1 verified finding (`weakened(low)`) + 0 sweep-confirmed instances =
**1**. **rca: false**, matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope: publish `target_temperature`
from the same per-cycle `coordinator.data` snapshot every other entity
reads, rather than the live `_opt_config` object — left for the fixer.

## Gate seconds

~0.02s (two grep/rg invocations).
