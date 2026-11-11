# D10-s2 report — gold axis, D10.M1 + D10.M2 (baseline 17f1c55fad1b)

Method: one executed AST/JSON check per gold rule that the code can decide,
in `gold_rules.py` (command in its header). Docs-only gold rules
(docs-data-update, docs-examples, docs-known-limitations, docs-supported-devices,
docs-supported-functions, docs-troubleshooting, docs-use-cases) were not
measured: reading docs/ is D5/D6 territory; left as `unfinished`.
Rule checklist pages were not fetched (no network use); the rule list is the brief's.

## Tier table (gold)

| rule | status | evidence | result |
|---|---|---|---|
| devices | done | device_info_sites | 1 DeviceInfo( site |
| diagnostics | done | diagnostics_to_redact_present | 1 (TO_REDACT + async_redact_data) |
| discovery / discovery-update-info | exempt | quality_scale.yaml basis | not re-measured |
| entity-translations | done | entity_*_mismatch_{en,sv} | 0 on all 6 platforms |
| exception-translations | done | exc_keys_missing_* | 0 of 24 literal keys, all 3 catalogues |
| icon-translations | done | entity_*_icon_orphans | 0 |
| reconfiguration-flow | done | reconfigure_step_present | 1 |
| repair-issues | done | issue_keys_missing_* | 0 of 18 literal keys |
| entity-category / device-class / disabled-by-default | spot | not separately counted | — |
| dynamic-devices / stale-devices | exempt | device_info_sites=1 (single static device) | consistent |
| docs-* (7 rules) | todo-unmeasured | — | unfinished |

Draft quality_scale.yaml (gold section): identical to the in-tree rows; no row
contradicted by an executed check. No todo rule requires an HA newer than
hacs.json's 2025.2.0.

## Findings
None.

## Non-findings
All counts above, from `PYTHONPATH=tests/hastub <venv python> dev/audit/rounds/round10/D10/s2/gold_rules.py`.
load1 was 31.3 (contended box); counts are contention-immune.

## Exposure
Read only the integration's code and catalogues; no docs/, no GitHub.
