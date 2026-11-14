# Flow board

Window ends 2026-11-14T19:12:48+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 3 / 1.0 | 27 / 24.0 |
| fly-ins closed | 0 | 4 |
| main moves: group-carrying / record / roster-edit / fly-in | 2 / 1 / 0 / 0 | 24 / 2 / 0 / 4 |
| first-pass fix-review yield | 2/2 (1.00) | 18/32 (0.56) |
| blocked-class mix | none | body:1, body-stale:1, carry-missing:1, ci-red:3, class-open:6, closures-regressed:1, comment-evidence:1, darwin-red:1, doc-claim-false:3, equivalence-refuted:1, evidence-comment:1, evidence-cut:1, figure-mislabelled:1, harness:1, head-moved:1, hold-unrefreshed:1, introduced-red:1, mutant-committed:1, mutation-survivor:1, mutation-vacuous:16, reference-basis-unbumped:1, root-cause-unrecorded:1, sufficiency:1, under-scoped:1 |
| lead time per size (h, n/p50/max) | M n=1 p50=7.23 max=7.23; S n=1 p50=1.50 max=1.50 | L n=3 p50=28.75 max=54.03; M n=10 p50=19.75 max=50.27; S n=11 p50=13.11 max=46.71 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 0 | 36 | 4 | 0 |

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
