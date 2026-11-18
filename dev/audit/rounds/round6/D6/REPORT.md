# D6 — README and documentation claim verification — audit round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), export `~/audit-r6-baseline`. Machine 8-core Apple M1, 8 GB. All harnesses count-class; `thread_factor=1.0`, `swapins=0`; `load1` 12–22 (provisional, shared box).

> Reconstructed by the orchestrator from the finder's inline return (the Write tool refused REPORT.md for the subagent; its 7 harnesses + claims.tsv are on disk).

## The numbers (claims_table.py)

`claims_extracted=49, claims_checked=44, claims_true=39, claims_false=4, claims_stale=1, claims_unverifiable=5`.

## Findings

### D6-01 (medium) — README tells users to clear ECL110 topics that already ship empty
README L894-895 / L214-215 claim both ECL110 MQTT topics ship non-empty and must be cleared by users without an ECL110. Production ships all three topic options `""`, so nothing is published until one is set (docs/ecl110.md L79-83 states this). `ecl110_topic_defaults.py`: `topics_with_nonempty_default=0` vs `readme_claims_nonempty=2`. Perturbation: default `""→"ecl110/command"` moves 0→1. `tests/nightly_ha.py:2531` repeats the false premise. instrumented_symbol `config_flow:_OPTION_FIELDS`.

### D6-02 (medium) — two of three shipped blueprints default to entity ids this build never creates
`charge_ev_from_grid_headroom.yaml → sensor.heat_pump_optimizer_power_headroom` and `economy_mode_on_price_peak.yaml → sensor.heat_pump_optimizer_current_electricity_price` both omit the `cost_` token the platform actually builds (`sensor.py:365`). `blueprint_default_ids.py`: `blueprint_defaults_missing=2` of 3. Perturbation: prefix → `sensor.hpo_` moves 2→3. stop_rule_class bug.

### D6-03 (low) — the documented entity-id prefix does not follow the entry name
docs/automations.md L7-11 and two blueprint descriptions tell users to change the prefix if they renamed the entry; `sensor.py:365` pins `heat_pump_optimizer` regardless of entry title, so renaming leaves all 59 ids unchanged. `entity_id_prefix.py`: 59 ids with default title, 0 after renaming to "My House". stop_rule_class hygiene.

## Non-findings (each with its number)

Option defaults `doc_default_mismatches=0` (76 rows / 197 fields); services `services_with_field_mismatch=0` (12/12); entity counts 59/5/4/4/1/1 = 74; 12 services, 28 `set_thermal_parameters` fields; 23 options pages; en/sv key parity 1279==1279; physical/tuning constants (stale 60/60/180/30, buffer min 100.0, VVC 20 min, inlet 10.0 C, cooling 0.3 C/h, legionella 7/5 d, 3-peak tariff, wood 0.60×, price tile 0.75×, 168 h, chart 900×380); manifest platinum + requirements — all held. The three unresolved links are the audit/backlog files stripped by construction.

## Stale / unverifiable
- Stale: `docs/dashboard-card.md:572` shows card v6.6.8 vs `CARD_VERSION="6.6.9"`.
- Unverifiable (5): the three stripped files; "solved within one optimization interval" (no cold-solve timing in export); DISCLAIMER savings figures.

## Exposure (also a baseline-construction defect for the orchestrator)
`RELEASE_NOTES.md` is present (kept deliberately). `tools/audit/round3, round4, round5, round5-fix` are PRESENT in the export although `strip_earlier_rounds()` exists to remove them — a baseline-construction defect in this round's manual prep, not a D6 product finding. This seat opened no file under those dirs.

## Not finished
how-it-works/ecl110 numeric claims resolved via tests/entities.py rather than a D6 harness; sv.json key parity only; systematic console-block sweep not attempted.

## Harnesses
`ecl110_topic_defaults.py`, `blueprint_default_ids.py`, `entity_id_prefix.py`, `doc_defaults_vs_code.py`, `services_fields_vs_schema.py`, `claims_table.py`, `claims.tsv`.
