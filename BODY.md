R11-HOTFIX-MAIN-SELFTEST-DRIFT-2: commit main run 44048908427's measured self-test table for main's red

Hotfix for a red main: push run 44048908427 at 8f39313a44 (v10.0.3 stamp), job governance / instrument-self-tests, step "Refuse a self-test read set the committed table misses" (`selftest_scope check`: 20 UNDER-SCOPED refusals). Merges since the last re-record (#3698) added reads no pull request re-measured (#3639, #3628, #3630, #3678 among them; e.g. CODE_OF_CONDUCT.md and tools/audit/seat/shell_hazard.py). This commits that run's `selftest-closures` artifact as tools/ci/selftest_closures.json: the committed table unioned with the run's Linux strace measurement (`union_record`), 206 lines added, 15 removed (entries re-sorted into the compact form, no read dropped).

## Head

f6199de7b95463547ed4cb8b6d5c4da60d2694a3

## Mutation proof

n/a: data-file re-record; the instrument's own self-test is the proof and is untouched. prepr: passed rc=0 at f6199de7b95463547ed4cb8b6d5c4da60d2694a3

## Null control

At 8f39313a44, `selftest_scope.drift(committed table, artifact entries, workflow_steps())` returns 20 refusals before this commit; with this table it returns 0. `selftest_scope.py static` reports 122 gated steps, 0 problems. Artifact: run 44048908427.

## Figures

none

## Red checks

governance / instrument-self-tests on main, the drift step (20 UNDER-SCOPED). Cause: a merge adding a read to a gated self-test step need not update tools/ci/selftest_closures.json, and the drift check runs only on a push to main. R11-RCA-SELFTEST-TABLE-DRIFT (#3684) is the countermeasure in flight (Carry: R11-RCA-SELFTEST-TABLE-DRIFT).

## Forward-carry

none

## Friction

none
