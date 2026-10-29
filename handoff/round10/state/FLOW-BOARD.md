# Flow board

Window ends 2026-10-29T21:13:44+01:00 (a function of the refs, not of when this ran). Takt 1.0 roster group per hour.

Sources: tree `origin/main`, roster `origin/handoff/audit-r10-roster`, bus `origin/review/*`

| measure | last 1 h | last 24 h |
|---|---|---|
| roster groups closed vs takt | 1 / 1.0 | 19 / 24.0 |
| fly-ins closed | 0 | 23 |
| main moves: group-carrying / record / roster-edit / fly-in | 1 / 0 / 0 / 0 | 13 / 5 / 2 / 23 |
| first-pass fix-review yield | 2/2 (1.00) | 21/31 (0.68) |
| blocked-class mix | body-stale:2, carry-missing:4, figure-false:1 | body-claim-wrong:1, body-figure:1, body-head-stale:2, body-stale:2, carry-dest-done:1, carry-missing:27, ci-red:6, ci-unconcluded:3, claim-drift:2, claims:1, class-open:18, class-rule-missing:4, conflict:2, contract-incomplete:1, control-missing:1, countermeasure-silenced:1, duplicate-ruling:1, figure-false:3, figure-wrong:1, figures-unverified:1, harness:4, harness-nondeterministic:1, head-moved:2, merge-conflict:2, metric-gamed:1, mutation-survivor:5, mutation-survivors:2, mutation-vacuous:9, nondeterministic-arm:1, pin-wrong:1, pr-contract-refused:1, ratchet-unrecorded:1, regression:2, released-early:1, retry-rule-unsound:1, root-cause-detectable:1, root-cause-unanswered:1, root-cause-unrecorded:1, ruling-change:1, ruling-incomplete:1, ruling-misrouted:1, ruling-refuted:2, ruling-unsound:1, verdict-word:2 |
| lead time per size (h, n/p50/max) | M n=1 p50=3.98 max=3.98 | M n=3 p50=9.19 max=19.93; S n=10 p50=5.97 max=36.68 |

### WIP by flow lane (snapshot at the window's end)

| A critical path | B product | C process | F fly-in |
|---|---|---|---|
| 3 | 40 | 6 | 11 |

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
