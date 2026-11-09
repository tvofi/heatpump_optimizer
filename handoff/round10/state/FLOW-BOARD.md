# Flow board

Window ends 2026-11-09T15:40:57+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 1 / 1.0 | 11 / 24.0 |
| fly-ins closed | 1 | 7 |
| main moves: group-carrying / record / roster-edit / fly-in | 2 / 0 / 0 / 1 | 29 / 2 / 0 / 7 |
| first-pass fix-review yield | 0/0 (-) | 16/39 (0.41) |
| blocked-class mix | none | carry-missing:1, ci-cancelled:2, ci-deferral-red:1, ci-incomplete:1, ci-pending:1, ci-red:21, ci-unsettled:1, claim-refuted:1, class-open:4, defect:1, gate-red:1, merge-conflict:3, mutant-survives:1, mutation-vacuous:4, resolution-ungated-step:1, root-cause-unanswered:5, root-cause-unrecorded:1, selftest-scope-ungated:1, semantic-conflict:1 |
| lead time per size (h, n/p50/max) | M n=1 p50=18.31 max=18.31; S n=1 p50=29.55 max=29.55 | L n=2 p50=15.27 max=24.23; M n=13 p50=17.91 max=32.22; S n=14 p50=15.24 max=39.24 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 49 | 11 | 2 |

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
