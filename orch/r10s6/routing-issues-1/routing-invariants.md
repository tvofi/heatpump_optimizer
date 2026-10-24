Routing audit 1 (2026-10-24) found 39 carries stranded in done groups, 32 live groups with no issue and 14 open issues listed only by done groups, and no instrument could tell a consumed carry from a stranded one. The simpler design (size S) extends carry_audit.py, roster_edit.py, roster_sync.py and orchestrator_tick.py and adds no script:

- `roster_edit.py mark-carry` records a carry as implemented, moved or dismissed; `carry_audit.py roster` reports STRANDED (a pending carry on a done group), report-only; legacy carries are exempt, no blanket migration.
- roster_sync sets the existing `carries-open` stage instead of `done` when pending carries remain; no set-stage refusal.
- Invariant 2 (a live group lists an issue) is a warning in brief_lint, not an error; invariant 3 (an open issue has a live owner) is a tick report line from the cached issue list, report-only on push.

Roster group: `R10-ROUTING-INVARIANTS`. Part of #201.
