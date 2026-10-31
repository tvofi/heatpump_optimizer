# Flow board

Window ends 2026-10-31T13:29:02+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 2 / 1.0 | 19 / 24.0 |
| fly-ins closed | 0 | 27 |
| main moves: group-carrying / record / roster-edit / fly-in | 1 / 0 / 0 / 0 | 15 / 7 / 1 / 27 |
| first-pass fix-review yield | 0/1 (0.00) | 32/46 (0.70) |
| blocked-class mix | scope-incomplete:1 | carry-missing:6, ci-pending:1, ci-red:2, class-open:3, figure-wrong:1, gate-red:2, head-moved:1, mutation-survivor:1, mutation-unpinned:1, mutation-vacuous:4, scope-incomplete:1, swap-void-undone:1 |
| lead time per size (h, n/p50/max) | M n=1 p50=14.03 max=14.03 | M n=7 p50=11.56 max=31.77; S n=8 p50=6.47 max=23.60 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 3 | 38 | 3 | 10 |

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
