R10-HOTFIX-SELFTEST-SCOPE-TABLE. Replaces tools/ci/selftest_closures.json with the measurement the red push run on main took, so the drift check on main passes again.

The red was NOT reproduced locally. `selftest_scope.py check --traces` needs strace traces and `record` is Linux+strace only (tools/ci/selftest_scope.py header, #201 comment 6707834331); this seat runs on Darwin with no strace, and the job log was not yet served. Evidence in its place: artifact `selftest-closures` of CI run 43448248435 (job 131963716179, failing step "Refuse a self-test read set the committed table misses"), measured at origin/main 154dbb4c61652135381ce66646d23f7109d1c142. Run through the instrument's own `drift()` against the committed table, that measurement yields 33 UNDER-SCOPED refusals over 114 gated steps (pr_args.sh, legacy_control_files.json, tests/entities.py and others, tick-loop index and objects flags). The table is the downloaded artifact, byte for byte; nothing is hand-edited. Origin/main was still 154dbb4c61 when this was handed off.

## Head

Code head f0da2186d46da385994d8f61e915314673b6d682 (f0da218); the measurement was taken at origin/main 154dbb4c61 (run 43448248435).

## Mutation proof

Revert the table to origin/main's: `drift()` over the artifact prints `selftest_scope check: 114 gated step(s), 33 refusal(s)`. With the artifact table: 0 refusals. `python3 -I tools/ci/selftest_scope.py static` reports 114 gated steps, 0 problems; `--self-test` 107 checks, 0 failed.

## Null control

The unmodified tree is the 33-refusal state above. A re-run of the drift check on the live push is the real control and runs only on the next push to main.

## Figures

none

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Red checks

none of the branch's own. Main's red is `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses". Cause: several merged PRs each added reads (the diff names 33 entries, spread over more than one PR) without the table being re-measured. Why each merging PR stayed green: the drift step runs only when `SELFTEST_TRACE` is set, which governance.yml line 300 sets only for `github.event_name == 'push'`; on a pull request the job runs scoped steps untraced and the drift step is skipped, and the scope selection itself reads the stale table, so an under-scoped entry cannot show there. Cheaper detector: none exists below the push run. Catching it at PR time needs strace on every step of every PR, which is the full untraced-to-traced cost the scoping removed; the push-time re-measure is the designed detector (main goes red within one merge, CLAUDE.md rule 1). Standing cost of the status quo: one red main per drift until the artifact is committed.

## Forward-carry

none

## Friction

none
