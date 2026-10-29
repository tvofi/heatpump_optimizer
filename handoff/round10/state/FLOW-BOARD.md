# Flow board

Window ends 2026-10-30T00:39:41+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 2 / 1.0 | 20 / 24.0 |
| fly-ins closed | 0 | 11 |
| main moves: group-carrying / record / roster-edit / fly-in | 2 / 0 / 0 / 0 | 17 / 5 / 2 / 11 |
| first-pass fix-review yield | 2/3 (0.67) | 20/27 (0.74) |
| blocked-class mix | carry-missing:2, mutation-vacuous:2 | body-stale:2, carry-missing:12, ci-red:4, ci-unconcluded:2, class-open:6, class-rule-missing:4, figure-false:2, instrument-broken:4, merge-conflict:2, mutation-survivor:2, mutation-survivors:2, mutation-vacuous:2 |
| lead time per size (h, n/p50/max) | S n=2 p50=3.17 max=8.00 | M n=4 p50=9.19 max=19.93; S n=13 p50=6.61 max=36.68 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 3 | 41 | 6 | 11 |

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
