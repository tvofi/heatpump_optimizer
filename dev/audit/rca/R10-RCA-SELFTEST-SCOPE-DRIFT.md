# R10-RCA-SELFTEST-SCOPE-DRIFT: re-records dropped reads main measures

Class `R10-SELFTEST-TABLE-SHRINK` in `dev/audit/config/bugclasses.json`. Part C
of the analysis (the barrier) is R10-SELFTEST-SCOPE-UNION-GUARD; part A (main
re-records mechanically) is ruled to round 11.

## Cause

`tools/ci/selftest_closures.json` is measured, but repaired by hand. At the
commit before this group, `selftest_scope.py record` ended by starting from the
old entries only under `--step`, else from an empty dict, then updating with the
new measurement: a recording replaced the step's entry. A re-record taken at a
base that main had since moved past therefore dropped reads main measures.
Merges #3409, #3419 and #3506 dropped 660, 8 and 10 entries; 6 of the 20 drift
refusals at f47250150a were such drops.

## Process state

(d): the re-record was sound against the checkout it ran in; its precondition,
that the table it replaces is the table main holds, changed underneath it. The
countermeasure makes the process notice the change instead of adding a rule.

## Countermeasure

1. `record` unions every measurement over the committed entry (both modes); a
   read leaves only by `prune --step ID --drop KIND:ITEM`.
2. `static`, which governance.yml already runs in the scope's self-test step on
   every pull request that touches the table (the table is a gate file, so that
   run is FULL), refuses every item the head's entry drops against the base's,
   unless the same diff deletes the path. Cost: one `git show` and one
   `git diff` on a diff that touches the table, none otherwise.

Both are pinned by self-test fixtures and by mutants in
`tools/ci/selftest_scope_mutants.sh`. The null control over the merge history
is in the pull request body.
