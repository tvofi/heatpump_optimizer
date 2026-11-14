# Flow board

Window ends 2026-11-14T11:11:40+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 3 / 1.0 | 23 / 24.0 |
| fly-ins closed | 0 | 5 |
| main moves: group-carrying / record / roster-edit / fly-in | 0 / 0 / 0 / 0 | 18 / 2 / 2 / 5 |
| first-pass fix-review yield | 0/0 (-) | 19/37 (0.51) |
| blocked-class mix | carry-missing:1, class-open:2, darwin-red:1, doc-claim-false:2, hold-unrefreshed:1, mutation-survivor:1, mutation-vacuous:8 | body:1, carry-missing:1, ci-red:4, class-open:7, comment-evidence:1, conflict:1, darwin-red:1, doc-claim-false:3, equivalence-refuted:1, evidence-comment:1, harness:1, hold-unrefreshed:1, introduced-red:4, main-conflict:1, merge-conflict:1, mutant-committed:1, mutation-survivor:1, mutation-vacuous:14, red-unanswered:1, reference-basis-unbumped:1, root-cause-unrecorded:1, self-test-red:1, sufficiency:1, under-scoped:1 |
| lead time per size (h, n/p50/max) | none | L n=3 p50=28.75 max=55.38; M n=7 p50=27.23 max=50.97; S n=8 p50=3.99 max=9.39 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 0 | 49 | 4 | 0 |

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
