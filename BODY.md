R11-HOTFIX-MAIN-SELFTEST-DRIFT-2: commit main run 44242125570's measured self-test table for main's red

Hotfix for a red main: push run 44242125570 at 7c2f4c30ca, job governance / instrument-self-tests (134592553541), step "Refuse a self-test read set the committed table misses" (`selftest_scope check`: 33 UNDER-SCOPED refusals). The previous re-record (#3707, artifact of run 44048908427) is already on main; merges after it added reads the table lacks, among them `dev/audit/config/scopes.json` (plan-public, finder-overlap, prepr, app-push and others), `tools/audit/leak_detectors.py`, `tools/audit/regret_oracle.py`, `tools/audit/seat/corpus_mirror.py`, `tools/audit/seat/owner_only.py`, and owner-only-launcher's `dirs` `['.']` (#3679's merge among them). This commits the union of the committed tools/ci/selftest_closures.json with that run's `selftest-closures` artifact 14404437877, attached by the orchestrator on refs/heads/inbox/r11-hotfix-main-selftest-drift-2 (`union_entries`, then `write_table`): 67 lines added, 120 removed, the removals being per-file instrument-card paths and probes that `write_table` compacts into `tools/audit/seat/instruments/**` and listed dirs. tools/ci/selftest_closures.json is the only file changed.

Main's tip has since moved to 83b9012d61 (#3688); its push run 44253992424 had not reached the drift step when this was measured, so it carried no newer artifact.

## Head

2cb38f075df2e6248408ca4e6bed6d83cc9316f3

## Mutation proof

n/a: data-file re-record; the instrument's own self-test is the proof and is untouched.

## Null control

At origin/main 83b9012d61, `selftest_scope.drift(committed table, artifact 14404437877 entries, workflow_steps())` returns the same 33 UNDER-SCOPED refusals CI printed at 7c2f4c30ca, and no STALE, UNMEASURED or EXTRA line; with this table it returns 0. `python3 tools/ci/selftest_scope.py static` reports 127 gated steps, 0 problems.

prepr: passed rc=0 at 2cb38f075df2e6248408ca4e6bed6d83cc9316f3 (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1, the hotfix ruling; CI is the authority).

## Figures

none

## Red checks

governance / instrument-self-tests on main: step "Refuse a self-test read set the committed table misses" (33 UNDER-SCOPED at run 44242125570). Cause: a merge that adds a read to a gated self-test step is not required to update tools/ci/selftest_closures.json, and the drift check runs only on a push to main. The countermeasure in flight is R11-RCA-SELFTEST-TABLE-DRIFT (#3684). Carry: R11-RCA-SELFTEST-TABLE-DRIFT

## Forward-carry

none

## Friction

none
