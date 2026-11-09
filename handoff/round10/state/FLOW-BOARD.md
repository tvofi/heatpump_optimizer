# Flow board

Window ends 2026-11-09T07:34:31+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 2 / 1.0 | 8 / 24.0 |
| fly-ins closed | 0 | 4 |
| main moves: group-carrying / record / roster-edit / fly-in | 4 / 0 / 0 / 0 | 28 / 2 / 0 / 4 |
| first-pass fix-review yield | 0/1 (0.00) | 19/47 (0.40) |
| blocked-class mix | ci-red:4 | carry-missing:1, carry-unmet:1, ci-cancelled:2, ci-incomplete:1, ci-pending:1, ci-red:18, ci-unsettled:1, claim-refuted:1, class-open:5, countermeasure-unsound:1, defect:1, gate-red:1, merge-conflict:3, mutant-survives:1, mutation-survivor:1, mutation-vacuous:3, own-row-not-generated:1, root-cause-detectable:1, root-cause-unanswered:5, rule-conflict:1 |
| lead time per size (h, n/p50/max) | S n=4 p50=35.08 max=39.24 | L n=3 p50=24.23 max=24.59; M n=12 p50=20.17 max=38.55; S n=13 p50=13.01 max=50.20 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 51 | 12 | 3 |

## Rules

- every period is CLOSED at both ends: an event at exactly the window's start or end is counted, so the default window -- which ends at a ref tip's own committer time -- includes the tip's merge.
- roster groups closed: a group whose resume.stage enters roster_lib's DONE_STAGES in the period, counted per first-parent commit of the roster ref; takt is 1.0 group per hour, so the period's demand is its hours.
- fly-ins closed: a first-parent PR merge of the tree in the period whose branch maps to no roster group and is neither a record nor a roster edit.
- main moves: each first-parent PR merge of the tree in the period, by kind -- group-carrying (roster_lib's branch-to-group answer), record (--record-prefix), roster-edit (the merge's diff touches the roster directory), fly-in (the rest).
- first-pass yield: of the PRs whose FIRST bus verdict falls in the period, the share whose first verdict is `merge`; a PR whose first verdict predates the period is not judged in it.
- blocked-class mix: every blocked verdict in the period, by the class word its subject carries.
- lead time per size: merge time minus the earliest commit the group's branch carries, over group-carrying merges whose roster group names a size; n, p50 and max hours.
- WIP by lane: open roster groups at the window's end -- A when in the published critical-path set, F for roster lanes F/FLY, C for C/tooling, B otherwise. A ref that publishes no critical-path file puts no group on it; a file that is there and cannot be read is UNAVAILABLE.
- A source that cannot be read prints UNAVAILABLE with its reason; it is never a zero.
