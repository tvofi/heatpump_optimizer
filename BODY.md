R10-HOTFIX-MAIN-SELFTEST-SCOPE-2: re-record the self-test scope table main's run measured

Main is red on `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses", since the merge of #3532. The newest finished main push run, `CI` 43632211631 at 4058469d79, prints `selftest_scope check: 116 gated step(s), 13 refusal(s)`, every one an UNDER-SCOPED line (for example `tools/audit/seat/ci_pause.py`, `tools/audit/seat/ci_priority.py`, `tools/audit/text_ledger.py`, `dev/audit/config/ci_priority.json`, `tools/policy/fixtures/required-contexts.json`, and the probe `paused.json` for pr-merger). It gates the v10.0.0 stamp.

The repair is the one `tools/ci/selftest_scope.py` states, as in #3589: commit the table the drift step itself writes. That run's `selftest-closures` artifact is the committed table unioned with the run's measurement. It is committed as is. It only adds: 36 added paths across 13 steps, no key or path of origin/main's table removed or changed (checked with a recursive compare). The 36 are exactly the 36 items the 13 UNDER-SCOPED lines name; none is uncovered.

What a PR run proves, and what it does not: `SELFTEST_TRACE` is set only on push, so no PR run can show the drift step green. Only the first push to main after the merge does. Until then the proof replays the step's own comparison, `selftest_scope.drift`, with the run's artifact as the measurement.

## Head

Code head `1542231b101cb1e9e7d26c8cd7793b8ce8f76d39`, one commit on origin/main 9acc181ca7, measured at 2026-11-14T20:44Z (`date -u`).

## Mutation proof

n/a: no production line changes. The diff is the measured table alone. The table's role is shown both ways under Null control.

## Null control

The unmodified tree, origin/main 9acc181ca7. Replaying `selftest_scope.drift(table, artifact["steps"], workflow_steps(root))` with run 43632211631's artifact against origin/main's table gives 13 refusals, the same count CI printed. The same replay at the head gives 0 refusals and 0 notes.

## Figures

- Drift refusals, origin/main table: 13. Head table: 0 (notes 0). Same replay, same artifact.
- Added paths: 36; removed or changed: 0.
- `python3 -I tools/ci/selftest_scope.py static` at the head: `116 gated step(s), 0 problem(s)`.
- `python3 tools/ci/selftest_scope.py --self-test` at the head: `110 checks, 0 failed`.
- Scope: the table is a gate file, so CI runs FULL.

## Red checks

- `governance / instrument-self-tests`, step "Refuse a self-test read set the committed table misses" (main push run 43632211631 and later): fails with 13 UNDER-SCOPED refusals; repaired by this diff. Root-cause answer: the cheaper detector is to trace each pull request's selected self-test steps and run `check` over them; `SELFTEST_TRACE` is push-only, so a PR that adds a read to an instrument cannot see this red. Its standing cost is strace overhead on every PR's selected steps. This is at least the fifth instance (after R10-HOTFIX-MAIN-SELFTESTS, R10-HOTFIX-MAIN-IST-READSET-2, R10-HOTFIX-SELFTEST-SCOPE-RERECORD and R10-HOTFIX-MAIN-SELFTEST-SCOPE); the structural barrier and the mechanical main-side union belong to the groups named below and to the root-cause seat beside this fix.

## Forward-carry

- A shrink guard on the committed table, and `record` unioning per step instead of replacing, so a re-record cannot drop reads; both land in `tools/ci/selftest_scope.py`. Carry: R10-SELFTEST-SCOPE-UNION-GUARD
- Main committing the measured table mechanically after a traced push, so a PR that adds an instrument read never leaves main red, is the group R11-SELFTEST-SCOPE-MAIN-UNION-RERECORD (file `tools/ci/selftest_closures.json`). Carry: R10-SELFTEST-SCOPE-UNION-GUARD | dismissed: R11-SELFTEST-SCOPE-MAIN-UNION-RERECORD owns it but is deferred (resume.stage deferred), which `prepr` refuses as a `Carry:` target; its routing is the orchestrator's

## Friction

none
