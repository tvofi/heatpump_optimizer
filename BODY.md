R11-HOTFIX-MAIN-SELFTEST-DRIFT: commit main run 43884631892's measured self-test table for main's red

Hotfix for a red main: push run 43884631892 at e352724335 (merge of #3645), job governance / instrument-self-tests (133359880684), step "Refuse a self-test read set the committed table misses" (`selftest_scope check`: 120 gated steps, 27 UNDER-SCOPED refusals). The same 27 refusals have stood on every main push run since 1f7c59ebc4 (merge of #3651). Merges after the last re-record (82e301585d, #3652) added reads no pull request re-measured: #3644 (tools/audit/seat/round_metrics.py, round_metrics_selftest.py), #3625 (dev/governance/dimensions/criteria/, dev/governance/config/machinery_target_budgets.json), #3651 (tools/audit/seat/plan_phases.py, dev/programme/round11/), plus reads of tools/audit/enumerate.py, topic_grammar.py, tools/release/stamp.py, tools/plan/replan.py and tests/throwaway_git.py in older steps. This commits that run's `selftest-closures` artifact as tools/ci/selftest_closures.json: the committed table unioned with the run's Linux strace measurement (`union_entries`), 70 lines added, 0 removed.

## Head

142926ec663e69a2a7371404256b4d4399ebb10a

## Mutation proof

n/a: data-file re-record; the instrument's own self-test is the proof and is untouched.

## Null control

At e352724335, `selftest_scope.drift(committed table, artifact entries, workflow_steps())` reproduces off-Linux the same 27 refusals CI printed; with this table it returns 0, `stale()` is empty, and `selftest_scope.py static` reports 120 gated steps, 0 problems.

## Figures

none

## Red checks

governance / instrument-self-tests on main (drift step, 27 UNDER-SCOPED). Cause: a merge that adds a read to a gated self-test step is not required to update tools/ci/selftest_closures.json, and the drift check runs only on a push to main, so main goes red one merge after the read lands. This is at least the fourth re-record hotfix (#3606, #3629, #3652, this one), so a root-cause seat is owed under defect-root-cause.md. Cheaper detector: a PR-time predictor in ci_predict/prepr that flags a diff adding a path or import that a gated step's scripts newly read, the way step 6d predicts UNDER-SCOPED for tests/closures.json; its standing cost is one static pass per prepr. Building it is tooling, so it goes to the root-cause seat or a proposal, not this hotfix.

## Forward-carry

none

## Friction

none
