# BLOCKED: r10-min-power-floor handoff body refused on unlanded carries

Code head f60b4d8c0f5c219e6b8c6d506f4874ce4c8f2a0a is pushed to `handoff/r10-min-power-floor`, after a clean `tools/pr/prepr.sh <body>` run (`PRE-PR: f60b4d8c0 ... rc=0`).

`tools/audit/seat/body_push.sh r10-min-power-floor <body>` refused with `CARRY-LANDED: 5 missing`. Each `## Forward-carry` item must already be in its group's brief or carries on the round's roster branch (`carry_audit.py land-ops`). The brief lets this seat write only its return refs and `handoff-wip/r10-min-power-floor[-body]`, so it cannot push `handoff/audit-r10-roster`. body_push kept the refused body at `handoff-wip/r10-min-power-floor-body` (903bff2c8).

Question for the orchestrator: land the five ops below on `handoff/audit-r10-roster` with `roster_edit.py`, then push the kept body with `body_push.sh r10-min-power-floor`. Or tell this seat it may do so.

Output of `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster land-ops --body <body> --topic r10-min-power-floor` at head f60b4d8c0:

```
append-carry R10-I18N-DE 'From r10-min-power-floor, body item c7e2fe29: The new option'\''s German label: no German translation file exists at base. Owed to R10-I18N-DE'\''s roster brief (item 9980b124), which the orchestrator writes, since a fixer seat writes no roster. Carry: R10-I18N-DE (items c7e2fe29)'
append-carry R10-USER-DOCS-VERIFY 'From r10-min-power-floor, body item cc1cca91: The docs row "Compressor runs below min power" in `docs/configuration.md` is a claim that `tests/doc_claims.py` may pin. Owed to R10-USER-DOCS-VERIFY'\''s roster brief (item df23e57c). Carry: R10-USER-DOCS-VERIFY (items cc1cca91)'
append-carry R10-MIN-POWER-FLOOR 'From r10-min-power-floor, body item a4565419: The reply on 3289 names the option: the reporter picks `on_off` unless their surface is switch plus setpoint, where the probe already clamps and only the DHW projection moves (item 052fa8fb). The orchestrator answers the issue. Carry: R10-MIN-POWER-FLOOR (items a4565419)'
append-carry R10-MIN-POWER-FLOOR 'From r10-min-power-floor, body item de37a181: Re-read #3297'\''s `probe_install` and `InstallCapability` at its merge. If it changes `can_duty_cycle` or `fully_metered`, revalidate the `on_off` early return and the block'\''s checks before this merges (item df5196cc). Carry: R10-MIN-POWER-FLOOR (items de37a181)'
append-carry R10-MIN-POWER-FLOOR 'From r10-min-power-floor, body item b8c2d996: After R10-GENERIC-HEAT-CURVE merges, re-measure the `option_doc_coverage.py` EXPECTED counts at the merge (+1 field from each side). `option_fields_undocumented` must stay 0 (item 3c867235). Carry: R10-MIN-POWER-FLOOR (items b8c2d996)'
```
