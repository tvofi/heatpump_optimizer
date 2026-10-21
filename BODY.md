Roster for round 10, sixth landing: the R10-FLOW-RECHAIN re-chain of the coordinator.py `after` edges, as one roster pull request. It also classifies the new evidence directory in `tests/layout.json`. It applies the decision seat's ruling, landed here as `dev/programme/round10/rechain/rechain-decision.md` with its edge lists `rechain-drops.json` and `rechain-adds.json`. Part of #201.

The ruling, applied whole and never in part (the drops land in the same commit as the three required edges):

- 8 drops: R10-RATIO-ANCHOR after R10-NIGHT-FOLDS; R10-INPUT-STALENESS after R10-RATIO-ANCHOR; R10-CURRENCY after R10-INPUT-STALENESS; R10-LOOP-CPU after R10-FREQ-DEFROST; R10-CONFIG-NOTICES after R10-LIVESTATE; R10-PARAMS-OWNER after R10-CONFIG-NOTICES; R10-ARCH-SHAPES after R10-PARAMS-OWNER; R10-LEARNER-ETA after R10-ARCH-SHAPES.
- 3 required edges: R10-PARAMS-OWNER after R10-LIVESTATE; R10-ARCH-SHAPES after R10-LIVESTATE; R10-HEAT-METER after R10-PARAMS-OWNER and R10-ARCH-SHAPES.
- 4 recommended edges: R10-LIVESTATE after R10-LOOP-CPU; R10-LOOP-CPU after R10-NIGHT-FOLDS; R10-PARAMS-OWNER after R10-NIGHT-FOLDS and R10-RATIO-ANCHOR; R10-ARCH-SHAPES after R10-INPUT-STALENESS.
- The orchestrator's addition: R10-HEAT-METER after R10-THERMAL-POWER-OPTION. The two share flow_meter.py, config_flow.py, const.py and coordinator.py, and the ruling listed the pair as unresolved.
- Architect note and brief text, as section 4 of the ruling specifies, in both copies (`architect_note`, and the older copy inside `brief`). The groups whose own `after` changed are R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-LOOP-CPU, R10-CONFIG-NOTICES, R10-LIVESTATE, R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-LEARNER-ETA and R10-HEAT-METER. For each, the coordinator.py clause becomes `coordinator.py (seam-ordered; before you: ...; after you: ...)`, and the start sentence becomes `Start from main.` or `Start from main; your merge follows <predecessors> if both are in one pitch.`. Only the `next:` list changes for R10-NIGHT-FOLDS and R10-FREQ-DEFROST. R10-HEAT-METER's `before you` also names R10-THERMAL-POWER-OPTION. R10-LOOP-CPU's carry naming R10-LIVESTATE stays, because the recommended edge that makes it true is applied.

Each edge was applied by `tools/audit/seat/roster_edit.py`'s own `op_set_after`, which refuses an unknown group, a self-edge, a repeated edge and a cycle. The text edits load and dump the roster JSON through the same tool's `dump`. The one commit passed the tool's lint gate (brief_lint from a fresh origin/main checkout, `TOTAL: 0 error(s)`) before it reached the branch.

This PR also carries the roster branch's commits since #2559 merged:

- `c185c7257`: a carry of #2567's forward-carry (carry_audit beside prepr) onto R10-POLICY-FIXER-MD.
- The merge seat's set-stage commits: `e80c0132a` (R10-ROSTER-OPS to done), `be1b9fa17` (R10-DEPENDABOT-AIOHTTP, its commit) and `5c51bdf6d` (R10-TICK-RELAY-DECOUPLE to done at `e9febe622`).

It leaves #201 open and closes nothing by keyword.

## Head

The authored code head is `f424d993d15f9ba103680ecf88a710539f789bcf` (`handoff/audit-r10-roster`). `git diff --name-only $(git merge-base origin/main f424d993d)...f424d993d` lists five files:

- `dev/programme/rosters/wave-r10-groups.json`
- `dev/programme/round10/rechain/rechain-decision.md` (new)
- `dev/programme/round10/rechain/rechain-drops.json` (new)
- `dev/programme/round10/rechain/rechain-adds.json` (new)
- `tests/layout.json`

The three new files sit under `dev/programme/`, a prefix on `tests/closure.py`'s `INERT` list, and none matches `is_handover`. `tests/layout.json` gains one glob, `dev/programme/round10/**`, beside the existing `dev/programme/round9/**` in the `dev/programme` category. Without it, the layout guard refused the first open with `placement: dev/programme/round10/rechain/rechain-adds.json is in 0 categories of tests/layout.json`. `tests/layout.json` is code-owned (`.github/CODEOWNERS`), so this PR needs the code-owner approval.

## Mutation proof

n/a: roster state and programme evidence only; no production or test code.

## Null control

The 96 roster groups outside the twelve edited ones are unchanged. `python3 -I tools/audit/carry_audit.py --roster-ref origin/main --roster-ref origin/handoff/audit-r10-roster sweep --from-dir <empty dir>` reports `ROSTER-DRIFT` (text that main holds and the branch lacks) for exactly the twelve groups whose note or brief this PR rewrites, and for no other group. Group count is 108 at both ends. Every carry list is unchanged except R10-POLICY-FIXER-MD's (5 to 6, `c185c7257`).

## Figures

- Critical-path depth over the open groups goes from 11 to 8. Run `python3 tools/audit/seat/plan_table.py --roster-ref origin/main` and `python3 tools/audit/seat/plan_table.py --roster-ref f424d993d` and read the swimlane table's last wave column (`roster_lib.depth_of` and `critical_path`). The path after: R10-ADVISOR, R10-SCORES, R10-LIVESTATE, R10-PARAMS-OWNER, R10-HEAT-METER, R10-COP-GATE, R10-UX-HEALTH, R10-ARCH-DOCS.

## Red checks

- `nightly-status`: it grades main (the nightly run), not this branch, so it is red at every head, main's own tip included. This diff changes only `dev/programme/rosters/wave-r10-groups.json`, three new files under `dev/programme/round10/rechain/` and one glob in `tests/layout.json`, and `nightly-status` reads none of them, so the red is not this PR's.

## Forward-carry

none

## Friction

none
