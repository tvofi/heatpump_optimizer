# Sweep: "missing icons.json services block"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D4-s2-08
(verified, low). Not a ledger class (new).

## Enumerator

`enumerate.py` lists every service the production registers
(`hass.services.async_register(DOMAIN, SERVICE_*, ...)` in `services.py`,
resolving each `SERVICE_*` constant to its literal name) and cross-checks
`icons.json`'s `services` block.

```
$ python3 tools/audit/round9/D14/sweep/missing_icons_services/enumerate.py
RESULT registered_services=12
RESULT services_with_icon=0
```

## Positive control

All 12 registered services (`apply_manual_plan`, `apply_schedule`,
`apply_topology`, `assign_entity`, `clear_manual_plan`,
`diagnose_interval`, `restore_learned_snapshot`, `run_optimization`,
`set_away`, `set_mode`, `set_thermal_parameters`, `simulate_plan`) confirmed
missing from `icons.json`, which has no `services` key at all
(`json.load(...).get("services")` is `None`). Matches the finding's "None
of the 12 registered services has an icon".

## Null control

`icons.json`'s `entity` key is present and non-empty (confirmed by
inspection), so the file itself parses and is not simply empty/missing —
the gap is specific to the `services` block.

## Perturbation

Direction check: adding one entry under `services` for any one of the 12
(the fix shape) makes that service's `has_icon` flip to `True` in the
enumerator's own output — the check is a direct membership test against
`icons.json`'s current content, so it moves by construction under that
one-line addition.

## Baseline vs main

`icons.json` and `services.py` are unchanged between `1936d5ca` and
`origin/main`. All 12 seams still exist on main.

## Disposition

All 12 are **instance** (one finding, one mechanism, 12 places it shows,
per COMMON.md's phenomenon-grouping rule). 0 guarded, 0 not-applicable.

## Count

N = 1 verified finding + 0 sweep-confirmed instances (the enumerator
re-finds exactly the 12 the finder already counted, no more, no fewer) =
**1**. **rca: false**, matching the brief.

## Barrier proposal

None built (N < 3). A `tests/` check asserting every registered service
name has a matching `icons.json["services"]` key would be a cheap, direct
detector (same shape as the enumerator above) — left as a lead for the
fixer.

## Gate seconds

~0.01s (two file reads, one JSON parse).
