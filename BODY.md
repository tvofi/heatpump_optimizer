Roster for round 10, seventh landing (PR-B of the Lean flow study's two roster pull requests, after #2576). It registers the 23 `R10-FLOW-*` groups from the study's pack at pin `30c57744a`, ten fly-in and playbook groups, the 23 carries the pack adds to existing groups, the carries the fix reviews of #2545, #2554, #2557, #2558, #2561, #2563, #2572, #2577, #2579, #2584 and #2586 owed, and the post-merge stage changes. Part of #201. It closes nothing by keyword and leaves #201 open.

What changes in `dev/programme/rosters/wave-r10-groups.json` (141 groups after, 108 before; the diff against the merge base is this one file):

- 33 new groups: the 23 `R10-FLOW-*` groups; the fly-ins `R10-FLY-RELAY-REVIEW-FF`, `R10-FLY-CAP-LINE`, `R10-FLY-CARRY-DISPOSITION`, `R10-FLY-OPENPR-ATOMIC`, `R10-FLY-ORPHANS-REWRITTEN`, `R10-FLY-CARRY-DOC-CONTEXT`, `R10-FLY-ROW-HEAD-CARRY`, `R10-FLY-DEPGRAPH-STALE`, `R10-FLY-GH-READ-RETRY`; and `R10-ROUND-PLAYBOOK`. Each went in through `tools/audit/seat/roster_edit.py append-group`, which refuses an unknown after-group.
- 27 existing groups changed: carries appended through `append-carry` with the text read from a file, `R10-SCORES` gains `payload.py` in its files, `R10-ORCH-MACHINERY` gains `tools/audit/seat/orchestrator_tick.py` and the edges `R10-TICK-OWED-LEVEL`, `R10-FLOW-MAIN-GATE` and `R10-CI-LAYOUT-P1`, and `R10-FLY-CARRY-DISPOSITION` gains `bus.sh` and an edge on `R10-FLY-ORPHANS-REWRITTEN`.
- Stage changes for merged work, each set at its merge commit: `R10-CI-RATCHET-RED` (#2531), `R10-REPLAY-CAP` (#2548), `R10-I5-DOCS` (#2521), `R10-FREQ-DEFROST` (#2527), `R10-TICK-OWED-LEVEL` (#2547), `R10-CI-LAYOUT` (#2529).
- `R10-FLOW-RECHAIN` is registered and set done: its substance merged as #2576.
- The carry of #2554's replay item went to `R10-REPLAY-LANE`, not `R10-REPLAY-CAP`, because `R10-REPLAY-CAP` is done.

Every edit passed the tool's lint gate (brief_lint from a fresh origin/main checkout, `TOTAL: 0 error(s)`) before it was pushed to `handoff/audit-r10-roster`. Four pack briefs needed a symbol rewritten with hyphens so brief_lint found no unresolved identifier (`ci-critpath`, `review-strength`, `flow-metrics`, `plan-model`); their meaning is unchanged.

## Head

`4ece7ca854d695360d53471aaa8e6fb6569fce45` is the authored code head, the tip of `handoff/audit-r10-roster`. Every figure below was taken at it. `git diff --name-only $(git merge-base origin/main 4ece7ca854d695360d53471aaa8e6fb6569fce45)...4ece7ca854d695360d53471aaa8e6fb6569fce45` prints `dev/programme/rosters/wave-r10-groups.json` and nothing else.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The roster on `origin/main` has the same bytes it had at the merge base `23ef06dc6`, so nothing main wrote since is overwritten. `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster sweep` prints `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`. The critical path is unchanged by this landing: `python3 tools/audit/seat/plan_table.py --roster-ref origin/main` and the same command with `--roster-ref 4ece7ca854d695360d53471aaa8e6fb6569fce45` both print 8 wave(s) and the path `R10-ADVISOR -> R10-SCORES -> R10-LIVESTATE -> R10-PARAMS-OWNER -> R10-HEAT-METER -> R10-COP-GATE -> R10-UX-HEALTH -> R10-ARCH-DOCS`.

## Figures

- 141 groups after, 108 before, 33 new, 27 changed: `python3 tools/audit/seat/plan_table.py --roster-ref 4ece7ca854d695360d53471aaa8e6fb6569fce45` for the group and open counts.
- 8 waves on both sides: `python3 tools/audit/seat/plan_table.py --roster-ref origin/main`.

## Red checks

- `nightly-status` and `ci-ratchet` grade `main`, not this branch. This diff changes only `dev/programme/rosters/wave-r10-groups.json`, and neither reads it. Per `defect-root-cause.md` they are the orchestrator's on main: the ratchet's `critical_path_minutes` finding is carried to `R10-CI-LAYOUT-P2` in this very roster.
- `rerun-stale-contract` runs on main's tip show `cancelled`; the concurrency group superseded them, and none concluded failure.

## Forward-carry

none

## Friction

none
