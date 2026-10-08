# D8 — Sensor verification and ordering — audit round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), export `~/audit-r6-baseline`. Machine 8-core Apple M1, 8 GB. Counts are deterministic; `thread_factor=1.0`, `load1` 7.3 (shared with D4/D7/D9).

> Reconstructed by the orchestrator from the finder's inline return (REPORT.md write refused; harness matrix.py on disk).

## Method

`matrix.py` builds 5 golden topologies × 8 toggles = 13 cells, 74 entities across 6 platforms, all through the real `async_setup_entry`. Null control `d8_golden_payload_mismatch=0` (reference build equals all five `tests/golden/coord_*.json` field-for-field). Each `D8_PERTURB` arm hooks a named symbol and moves exactly its class off zero, so the clean zeros pin something.

## Finding

### D8-01 (medium, hygiene) — five DHW entities stay enabled-by-default and permanently unavailable with hot water unconfigured

Five of six `_DHWEntityMixin` entities (`dhw_schedule`, `dhw_heating_cost`, `dhw_heating_plan`, `dhw_energy`, `dhw_cost_total`) are enabled by default and `available=False` in every refresh where DHW is unconfigured; only `DHWTemperatureSensor` is disabled-by-default, so the family default is mixed and a no-hot-water user sees five dead entities.

- instrumented symbol: `sensor:_DHWEntityMixin.available` (gates on `data['dhw_enabled']`, but `_attr_entity_registry_enabled_default=True` on five classes).
- Evidence: `matrix.py` — `d8_no_dhw_enabled_unavailable=5`; perturbation (configure DHW) → 0.
- Fix scope: `_attr_entity_registry_enabled_default = False` on the five classes (or on the mixin, with the temperature sensor already off).

## Non-findings (20, each with its executed number)

All type/unit/class/serialisability/staleness classes are 0 across all cells: `state_raises=0`, `enum_not_listed=0`, `measurement_nonnum=0`, `ts_naive=0`, `ts_not_datetime=0`, `unit_on_nonnumeric=0`, `unit_dc_mismatch=0`, `nonjson=0`, `enabled_dead=0`, `golden_payload_mismatch=0`; staleness `stale_indoor/outdoor/tank/price=0`; family ordering 1 run/0 interlopers for all 7 families (plan headline 7 members); `first_hour_disabled=0`; `no_icon=1` (climate, domain default applies); translations 73 entities 0 missing/0 extra (en+sv); narrative template keys 14/14.

Two leads filed as non-findings with gaps named: DHW/learning families split into 2 runs under the **entity_id** sort (platform-prefix residue, absent under name sort); the round-5 #1333 card-headline trap re-measured (the gap is the finder's, not production's). Harness gap: `_capture_coordinator` runs no solve, so `optimization_status=not_run` and 18 plan-derived sensors publish `None` — their values are unexercised, only type/unit/class/serialisability contracts.

## Harnesses
`matrix.py`.

## Exposure
`tools/audit/briefs/D8.md` carries round-5 #1333 (its Traps section). No gh/GitHub.
