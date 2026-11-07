# Flow board

Window ends 2026-11-07T10:41:15+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 0 / 1.0 | 13 / 24.0 |
| fly-ins closed | 0 | 6 |
| main moves: group-carrying / record / roster-edit / fly-in | 3 / 1 / 0 / 0 | 14 / 4 / 2 / 6 |
| first-pass fix-review yield | 0/0 (-) | 9/28 (0.32) |
| blocked-class mix | none | architecture-unsound:2, ci-red:8, citation-false:1, class-open:3, defect:1, instrument-broken:1, mutation-vacuous:12, over-fire:1, owner-ruling-contradicted:1, owner-words:2, policy-unapproved:3, root-cause-detectable:1, selftest-red:1, wait-cycle:1 |
| lead time per size (h, n/p50/max) | M n=3 p50=21.99 max=25.85 | M n=7 p50=17.71 max=25.85; S n=7 p50=10.09 max=13.94 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 58 | 5 | 3 |

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
