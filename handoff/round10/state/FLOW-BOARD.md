# Flow board

Window ends 2026-11-12T09:23:57+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 2 / 1.0 | 21 / 24.0 |
| fly-ins closed | 0 | 1 |
| main moves: group-carrying / record / roster-edit / fly-in | 5 / 0 / 0 / 0 | 35 / 4 / 0 / 1 |
| first-pass fix-review yield | 0/2 (0.00) | 21/42 (0.50) |
| blocked-class mix | mutation-vacuous:1, regression:1 | body-not-applied:1, carry-dismissal-unsupported:1, carry-missing:3, class-open:5, harness:3, harness-vacuous:1, mutation-survivor:1, mutation-vacuous:10, null-control-leak:1, part-topic-collision:1, regression:1, regression-unmeasured:1, root-cause-unanswered:3, scope-overlap:1, trace-gap:1 |
| lead time per size (h, n/p50/max) | M n=2 p50=17.45 max=31.49; S n=3 p50=20.31 max=24.09 | L n=2 p50=18.17 max=19.22; M n=11 p50=15.77 max=105.45; S n=22 p50=14.13 max=25.71 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 47 | 9 | 0 |

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
