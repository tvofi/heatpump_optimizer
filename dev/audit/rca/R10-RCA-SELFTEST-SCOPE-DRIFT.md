# R10-RCA-SELFTEST-SCOPE-DRIFT: re-records dropped reads main measures

Class `R10-SELFTEST-TABLE-SHRINK` in `dev/audit/config/bugclasses.json`. The
union `record` is R10-SELFTEST-SCOPE-UNION-GUARD; part A (main re-records
mechanically) is R11-PRE-SHARED-FILES part 1, which absorbs the group
(`dev/programme/triage/r10-round-end.md`, P748, P762, P763).

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
countermeasure removes the precondition instead of adding a rule: a unioned
re-record keeps what main holds whatever base it ran at.

## Countermeasure

`record` unions every measurement over the committed entry (both modes), by
the same `union_entry` that `check --write` uses for the artifact; a read
leaves only by `prune --step ID --drop KIND:ITEM`. Pinned by self-test fixtures
and by mutants in `tools/ci/selftest_scope_mutants.sh`.

A table-shrink guard in `static` (refuse a pull request whose table drops a
read the base names) was built and dropped by the round-end triage (P762): once
main re-records its own table (part A), no pull request edits it, so the guard
has no input.
