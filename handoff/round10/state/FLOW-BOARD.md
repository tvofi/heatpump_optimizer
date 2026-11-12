# Flow board

Window ends 2026-11-12T02:14:55+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 0 / 1.0 | 22 / 24.0 |
| fly-ins closed | 0 | 6 |
| main moves: group-carrying / record / roster-edit / fly-in | 3 / 1 / 0 / 0 | 27 / 4 / 0 / 6 |
| first-pass fix-review yield | 2/2 (1.00) | 28/52 (0.54) |
| blocked-class mix | harness:1 | carry-missing:4, class-open:6, doc-claim-false:1, flaky-harness:1, harness:2, harness-vacuous:1, mutation-survivor:1, mutation-survivors:2, mutation-vacuous:14, null-control-leak:1, part-topic-collision:1, pin-missing:1, regression-unmeasured:2, root-cause-unanswered:3 |
| lead time per size (h, n/p50/max) | L n=1 p50=19.22 max=19.22; M n=2 p50=3.44 max=105.45 | L n=2 p50=19.22 max=26.88; M n=7 p50=10.91 max=105.45; S n=18 p50=8.15 max=36.09 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 53 | 11 | 0 |

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
