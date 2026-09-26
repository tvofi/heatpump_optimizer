# Sweep: "whole-entity availability gated on an optional input"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D8-s2-01
(weakened(medium), medium). Not a ledger class (new).

## Enumerator

```
$ grep -n "def available" -A8 custom_components/heatpump_optimizer/climate.py custom_components/heatpump_optimizer/switch.py custom_components/heatpump_optimizer/button.py | grep reading_ok
```

widened to every `available` override in the same three files:

```
$ grep -n "def available" -A8 custom_components/heatpump_optimizer/climate.py custom_components/heatpump_optimizer/switch.py custom_components/heatpump_optimizer/button.py
climate.py:122  -- gates on flags.get("upper_floor_temperature")
button.py:83    -- gates on `not self.coordinator.optimization_running`
button.py:112   -- gates on `not self.coordinator.system_identification_active`
switch.py       -- no `available` override found
```

## Positive control

`climate.py:122-131`: `available` returns
`bool(super().available and flags.get("upper_floor_temperature"))` where
`flags = (self.coordinator.data or {}).get("reading_ok") or {}` — the
**entire climate entity** (thermostat control: set mode, set temperature,
present hvac_action) goes unavailable whenever the indoor thermometer
(an optional configuration input) has not read this cycle, rather than
only the temperature-reporting attribute going unknown. Confirmed present
at baseline `1936d5ca`; `climate.py` is unchanged on `origin/main`.

## Widened candidates, dispositioned

`button.py:83` and `:112` are **not applicable**: both gate on a
*coordinator-state* condition (`optimization_running`,
`system_identification_active`), not on an *optional configuration input*
going stale/unread — a fundamentally different mechanism (temporarily
suppressing a duplicate action request vs. losing an entire control
surface because one optional sensor is unconfigured). `switch.py` has no
`available` override at all in this file, so nothing to disposition there.

## Null control

The two `button.py` hits confirm the widened grep is not vacuous (it does
find other `available` overrides); both are genuine non-matches on
inspection, not false negatives of the enumerator.

## Perturbation

Not independently re-run; the finding's own seam_rule already demonstrates
the mechanism directly (the `reading_ok` flag gate cited above), and
`tests/entities.py` (the finding's second "files" entry) is the ratchet
that must be updated alongside any fix, not a separate seam to disposition.

## Disposition

| seam | disposition |
|---|---|
| climate.py:122-131 `available` gated on `reading_ok["upper_floor_temperature"]` | instance — D8-s2-01 |
| button.py:83 `available` (optimization_running) | not applicable — coordinator-state gate, not an optional-input gate |
| button.py:112 `available` (system_identification_active) | not applicable — same, different mechanism |
| switch.py | not applicable — no `available` override present |

## Count

N = 1 verified finding (`weakened(medium)`) + 0 sweep-confirmed instances =
**1**. **rca: false**, matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope: drop the whole-entity gate and
let `current_temperature` alone go `None`/unknown when the indoor
thermometer has not read, the way every other optional-input-backed
attribute already does, keeping `hvac_mode`/`set_temperature` control
available — left for the fixer.

## Gate seconds

~0.02s (one grep invocation).
