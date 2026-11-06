# Flow board

Window ends 2026-11-06T23:56:06+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 0 / 1.0 | 13 / 24.0 |
| fly-ins closed | 1 | 10 |
| main moves: group-carrying / record / roster-edit / fly-in | 0 / 0 / 0 / 1 | 11 / 5 / 2 / 10 |
| first-pass fix-review yield | 0/1 (0.00) | 6/28 (0.21) |
| blocked-class mix | citation-false:1, mutation-vacuous:1, policy-unapproved:1 | beyond-card:1, carry-unanswered:1, ci-red:5, citation-false:1, class-open:6, figures-uncited:2, instrument-broken:1, mutation-vacuous:11, over-fire:1, owner-ruling-contradicted:1, owner-words:2, policy-unapproved:2, regression:1, root-cause-detectable:1, selftest-red:1, wait-cycle:1 |
| lead time per size (h, n/p50/max) | none | M n=5 p50=10.12 max=45.63; S n=6 p50=7.74 max=19.10 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 1 | 58 | 5 | 2 |

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
