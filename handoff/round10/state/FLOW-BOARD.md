# Flow board

Window ends 2026-11-05T06:10:15+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 0 / 1.0 | 28 / 24.0 |
| fly-ins closed | 0 | 8 |
| main moves: group-carrying / record / roster-edit / fly-in | 1 / 0 / 0 / 0 | 17 / 1 / 0 / 8 |
| first-pass fix-review yield | 0/0 (-) | 10/37 (0.27) |
| blocked-class mix | ci-red:2 | body-stale:1, ci-cancelled:2, ci-red:12, ci-red-cancelled:1, citation-wrong:1, claim-refuted:2, class-open:9, defect:2, figures-uncited:1, harness:1, metric-gamed:1, mutation-vacuous:5, owner-stale:1, pr-closed:1, ratchet-grown:1, root-cause-detectable:2 |
| lead time per size (h, n/p50/max) | M n=1 p50=93.08 max=93.08 | M n=5 p50=17.70 max=93.08; S n=12 p50=12.32 max=83.83 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 58 | 2 | 3 |

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
