# Flow board

Window ends 2026-11-12T14:32:37+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 2 / 1.0 | 25 / 24.0 |
| fly-ins closed | 0 | 1 |
| main moves: group-carrying / record / roster-edit / fly-in | 2 / 1 / 0 / 0 | 42 / 5 / 0 / 1 |
| first-pass fix-review yield | 0/0 (-) | 15/32 (0.47) |
| blocked-class mix | head-moved:1, introduced-red:1 | body-not-applied:1, carry-dismissal-unsupported:1, carry-missing:2, census-misclassified:2, class-open:5, findings-unresolved:1, harness:2, harness-vacuous:1, head-moved:1, introduced-red:1, mutation-vacuous:6, null-control-leak:1, prior-findings-open:1, regression:1, regression-unmeasured:1, scope-overlap:1, trace-gap:1 |
| lead time per size (h, n/p50/max) | L n=1 p50=36.53 max=36.53; S n=1 p50=4.60 max=4.60 | L n=5 p50=19.22 max=36.53; M n=12 p50=20.49 max=105.45; S n=25 p50=14.52 max=28.30 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 45 | 6 | 0 |

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
