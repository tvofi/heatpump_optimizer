R11-HOTFIX-SELFTEST-CURRENCY-DIR: record the four self-test reads the currency.py triage directory added

Hotfix for a red main: push run 44408012370 at 1723f9fdc9, job governance / instrument-self-tests (135169523494), step "Refuse a self-test read set the committed table misses" (`selftest_scope check: 127 gated step(s), 4 refusal(s)`). The same four refusals stand in runs 44396653830 (5bc69f9b94) and 44398362437 (fd847a550c). The last green main run of that job is 44379511133 at 107988b792.

Cause: #3724 (merge 5bc69f9b94, R11-SEAM-kernel-layering), through its commit 9049a4a81e, added `tests/mutation_ledger/survivor_triage/currency.py/@module.GUARD_OFF.e1433e05.json`. That is the first file under the new directory `tests/mutation_ledger/survivor_triage/currency.py/`. Four gated steps walk survivor_triage/ and now list that directory too, and the committed table did not hold it:
- dependency-graph-census, `dirs`: the directory
- self-tests-outside-seat, `dirs`: the directory
- prepr, `dirs`: the directory
- temp-or-machine-path, `probes`: `currency.py/.gitattributes`

The four items come from run 44408012370's own measurement, its `selftest-closures` artifact. Each is inserted in sorted order into tools/ci/selftest_closures.json, which is the only file changed (4 lines added). The artifact is not committed verbatim. Its compacted probe lists repeat some `**` globs (for example `tools/audit/round4/**` and `.cursor/**`) that the committed table holds once. Set-wise the artifact adds nothing else, so this change does not carry those duplicates.

## Head

912b87c0359e1b39432236551688deae0976f681

One commit on origin/main 1723f9fdc9.

## Mutation proof

n/a: a data-file record. The instrument and its own self-test are untouched. Removing any one of the four items brings back its own UNDER-SCOPED line in the null control below.

## Null control

At origin/main 1723f9fdc9, `selftest_scope.drift(main table, artifact entries, workflow_steps())` returns exactly the four UNDER-SCOPED refusals CI printed, and no STALE, UNMEASURED or EXTRA line. With this table it returns 0. The table holds every list item and flag the artifact holds, and every run_sha is unchanged. `python3 -I tools/ci/selftest_scope.py static` gives 127 gated steps and 0 problems. `--self-test` gives 118 checks and 0 failed.

prepr: hotfix mode, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`. CI is the authority.

## Figures

none

## Red checks

governance / instrument-self-tests on main: step "Refuse a self-test read set the committed table misses" (4 UNDER-SCOPED at run 44408012370).

Cause: a merge that adds a read to a gated self-test step does not have to update tools/ci/selftest_closures.json, and the drift check runs only on a push to main. Here the new read is a new directory under a listed one. This is the same class as the earlier main-selftest-drift hotfixes, and its countermeasure is R11-RCA-SELFTEST-TABLE-DRIFT (#3684). Carry: R11-RCA-SELFTEST-TABLE-DRIFT

## Forward-carry

none

## Friction

none
