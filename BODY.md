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

## Carry dispositions

Numbering follows the review packet (1-based); the brief's own index is one lower.

- Carry 1 (brief 0): built. --live-refs, --in-flight, --measure-sizes, inflow field.
- Carry 2 (brief 1): moved to R10-BODY-CONTRACT.
- Carry 3 (brief 2): built. Absorbed counts as done; advisory.
- Carry 4 (brief 3): built. Liveness by evidence, binding chain, CP slack.
- Carry 5 (brief 4): dismissed, duplicate of carry 2.
- Carry 6 (brief 5): dismissed, duplicate of carry 2.
- Carry 7 (brief 6): dismissed, duplicate of carry 2.
- Carry 8 (brief 7): moved to R10-BODY-CONTRACT.
- Carry 9 (brief 8): built. Critical-path groups start past the slots cap.
- Carry 10 (brief 9): built. Stamp cadence by production group.
- Carry 11 (brief 10): built. Post-closure groups.
- Carry 12 (brief 11): built with carry 11 (same seam).
- Carry 13 (brief 12): built. tools/audit/seat/gantt_drift.py.

## Forward-carry

none

## Friction

none
