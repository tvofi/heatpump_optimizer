R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py, plus the tracked Gantt-drift instrument (carry 12). Measures the roster/plan semantics only; no production code.

Carries built: 0 (live-refs, in-flight, measure-sizes, inflow), 2 (absorbed is done, advisory), 3 (liveness by evidence, binding chain and CP slack, uncalibrated-sensitivity note), 8 (critical-path groups start past the slots cap, exempt), 9 (stamp cadence 3 by group, comment-only diffs ignored), 10 and 11 (post-closure groups), 12 (tools/audit/seat/gantt_drift.py).
Carries 1 and 7 were moved to R10-BODY-CONTRACT; 4, 5 and 6 are dismissed as duplicates.

Process note: the seat ran under the session's frugal routing hook; discovery was done through subagents.

## Head

dcf19d037df104cf2d06fc0d899c2dd80a36c818 (origin/main unmoved at 28482eceeb6b since the clean prepr.sh run, so no second run).

## Mutation proof

`python3 tools/plan/replan.py --self-test` kills every mutant (about 20 new, including cp-first-in-tier, overflow-exempt, absorbed-done, post-closure, stamp-by-PR, design-credit, inflow, measure-sizes). `python3 -I tools/audit/seat/gantt_drift.py --self-test` kills 15 mutants.

## Null control

Each arm has a null: no in-flight file or inflow 0 reproduces today's plan byte for byte; a non-critical group still waits at a full cap; a production group with no stamp dependency stays in the closing stamp's carries; the sizes null re-derives the old model's S 13.1, M 11.4, L 20.1 from a fixture window.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
