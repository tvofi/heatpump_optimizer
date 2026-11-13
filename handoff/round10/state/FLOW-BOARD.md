# Flow board

Window ends 2026-11-13T18:56:54+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 2 / 1.0 | 31 / 24.0 |
| fly-ins closed | 1 | 17 |
| main moves: group-carrying / record / roster-edit / fly-in | 3 / 1 / 0 / 1 | 31 / 6 / 4 / 17 |
| first-pass fix-review yield | 1/1 (1.00) | 22/37 (0.59) |
| blocked-class mix | ci-red:1, red-unanswered:1 | architecture-unsound:1, ci-red:1, claim-false:1, class-open:7, conflict:1, dropped-entries:1, introduced-red:3, main-conflict:1, merge-conflict:1, mutation-survivor:1, mutation-survivors:1, mutation-vacuous:5, red-unanswered:1, self-test-red:1 |
| lead time per size (h, n/p50/max) | L n=1 p50=55.38 max=55.38; S n=2 p50=1.80 max=9.39 | L n=2 p50=26.19 max=55.38; M n=11 p50=22.08 max=53.48; S n=18 p50=5.52 max=18.31 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 0 | 37 | 4 | 0 |

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
