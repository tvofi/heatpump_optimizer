The `instrument-self-tests` job is cut off by its own `timeout-minutes`, not by a failing step. On `main`, 3 of the last 7 completed push attempts were cancelled at the 90-minute cap, with no step failing. On pull requests a FULL self-test run (any diff touching `tools/ci/selftest_closures.json`) sits on the 30-minute cap: one run passed just under it and two runs of #3880 were cancelled just over it, each at a different step. This raises the cap in `.github/workflows/governance.yml` only: push 90 -> 120 minutes, pull request 30 -> 45. No step, scope or grader changes.

This is a hotfix for a red required check on `main` (instrument-freeze exemption); the permanent cost cut for non-production diffs is #3885's own pull request, which does not edit this line.

## Head

850c7241fc9080ed0c21c8b22e6986677472b957

## Mutation proof

n/a: a timeout value has no branch to mutate; the control is the cancelled runs below, which this cap would have let finish.

## Null control

At the fork point 3210fcd7 the caps read 90 (push) and 30 (pull request), and the runs cited in the commit message were cancelled at those caps with every finished step passing.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
