Main-red hotfix: `governance / instrument-self-tests` red on main at 5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb (run 42780661829, job 129709886308).

## Head

`245ddf7876bf9662937d4e9077172e1e3cd2275a` is this PR's head, unchanged.

## Mutation proof

Pinned in-tree by `tools/ci/selftest_scope_mutants.sh`.

## Null control

At 5d09dedf6 (no `settle`), four records differed.

## Figures

- Self-test, 109 checks, 0 failed, at 9679946bc.

## Red checks

none

## Forward-carry

- Class R10-RCA-MAIN-SELFTESTS-RED shape 2 (a read set that moves between runs of one tree): here the moving part was the index state the checkout left, and this PR builds that countermeasure (`settle`). The one environment-dependent read seen beside it, `tools/policy/fixtures/required-contexts.json`, was measured only locally, and the committed CI entry does not hold it. Carry: dismissed: R10-RCA-MAIN-SELFTESTS-RED is resume.stage done, and the countermeasure lands in this PR

## Friction

none
