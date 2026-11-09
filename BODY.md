R10-FLY-REPLAN-TOP-TIER: outside requests share replan's top tier with the critical path, behind main and hotfixes, unordered between them (height decides within the tier).

Ruling: tvofi 2026-11-07 put accepted OUTSIDE issues and PRs first. #3304 (R10-OUTSIDE-FIRST) implemented that as a strict order, hotfix, outside, then critical path. This PR does not duplicate it: it reads the later stated intent ("outside requests and the critical path, all top priority, in no particular order", 2026-11-08) as one tier. `dispatch_tier` returns TIER_TOP for either; `dispatch_key` drops the critical-path-first term; `roster_lib.dispatch_rank` becomes RANK_HOTFIX / RANK_TOP / RANK_OTHER; `gate_priority` maps them to bands 2/1/0; `orchestrator_tick` orders OWED lines by that rank, then PR number. The critical path still starts past the slot cap.

## Head

09260b7af5bc828627026b2e36a00591427061f2

## Mutation proof

replan.py self-test arm `top-tier-unordered` (pick restricted to the critical path) turns the "within the top tier height orders" check red; the existing `tier-critical-path` arm still bites; the stale outside-only arm from #3304 was already dropped as a duplicate. Run: `python3 tools/plan/replan.py --self-test` (0 failed).

## Null control

Same production group with no outside source stays tier 4 and starts after the outside group; a roster with no outside group orders as before (critical path first by height).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
