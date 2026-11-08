Main's required job `governance / instrument-self-tests` went red at 48af0864a (job 128597751217, step 101): "FAIL a settings file whose PreToolUse matcher is no-matcher passes (null control) (got 1, wanted 0)", hook output `SELF-TEST FAILED SessionStart .claude/hooks/session-start.sh 22 passed, 2 failed`. Cause: the hook's `origin/main at:` line is git's relative `%cr`, and `--self-test` compares two or three reports byte for byte ("unset ... not a byte more", "set ... plus one role pack line"). A clock tick between reports ("2 minutes ago" to "3 minutes ago") fails both with no defect in the hook; it is likely only minutes after a merge, which is why 17e115792 passed and a rows-only record merge did not touch the code. Fix at the owner: the self-test pins `GIT_TEST_DATE_NOW` once (a caller's pin stands); the hook's normal output is unchanged. No retry, no skipped row.
Topic r10-hotfix-main-ist-red. Closures were not recorded: prepr.sh's closures stage refused because tests/entities.py needs the homeassistant module, absent in this cloud toolchain; PREPR_SKIP_CLOSURES=1 was used for the final run. VERSION, manifest, RELEASE_NOTES, budgets and claim files are untouched. origin/main moved after the last prepr run (merge-tree reports no conflict); not re-run per the 2026-11-07 owner ruling.

## Head

e8af8dcda5a17ce8d448992848bbbabac8e929d4

## Mutation proof

Reverting the pin in .claude/hooks/session-start.sh and running the self-test under a git shim that advances the clock 70 s per call prints "22 passed, 2 failed" (the exact evidence shape); the new prepr.sh self-check row "the session-start self-test passes while git's clock ticks between its reports (null control)" goes red on it.

## Null control

With the pin, the same shim run prints "24 passed, 0 failed"; three plain runs on an unshimmed checkout printed "24 passed, 0 failed" each (the failure did not reproduce without a tick, which fits a flake). The unmodified tree at this base passes plain runs and fails only under the ticking shim.

## Figures

- unfixed under ticking git: `PATH=<shim>:$PATH bash .claude/hooks/session-start.sh --self-test | tail -1` -> 22 passed, 2 failed
- fixed under ticking git: same command -> 24 passed, 0 failed
- diff-mutant step: skipped by prepr.sh (MUTANT_CMD unset; the changed files are not read by mutants); no survivor count exists to report.

## Red checks

none

## Forward-carry

none

## Friction

none
