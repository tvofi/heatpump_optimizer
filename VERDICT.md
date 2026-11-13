Fix review: blocked ef7e3373e763942a38982c679541c5aa750b3935 introduced-red: instrument-self-tests selftest_scope self-test fails under GITHUB_BASE_REF (static, ids and select over a fresh table)

bus-nonce: a13a694bcd2efeba65e0dbb9b8fb5b92

Round: 2, a delta review over the reviewed head 552638f8dc3a1c7f270448163d44df992c62dac2. The delta is `git diff 552638f8dc ef7e3373e7`: tools/ci/selftest_scope.py and tools/ci/selftest_scope_mutants.sh. I measured at ef7e3373e7 in a detached worktree, and the PR head ref is still ef7e3373e7.

## Block

This head introduces a red step in `governance / instrument-self-tests` (job 131898295736, run on refs/pull/3551/merge = 6d60943f67, a merge of this head). It is red at the head and not at the merge base, so it is INTRODUCED and blocks under fix-review.md step 11:

- `FAIL static, ids and select over a fresh table`, then `selftest_scope self-test: 141 checks, 1 failed`. The mutants step that follows it prints `BASELINE RED: the unmutated self-test fails` (ev/ci_selftest_scope_tail.txt).
- Cause: the delta makes `table_base` return an `UNRESOLVED base origin/main` problem when a named base doesn't resolve. CI is a pull_request event, so `GITHUB_BASE_REF=main` is set. The self-test's fresh-table fixture is a scratch repository with no `origin/main`. It calls `main(["static"], <fixture>)` with the ambient environment, so it now gets one extra problem line. The new `static_at` helper only sets and removes `SELFTEST_BASE`. Nothing clears `GITHUB_BASE_REF` for the older fixture.
- Reproduced locally at this head: `GITHUB_BASE_REF=main python3 -I tools/ci/selftest_scope.py --self-test` gives the same FAIL, 141 checks, 1 failed, rc 1 (ev/selftest_with_GITHUB_BASE_REF.txt). Without the variable it gives 141 checks, 0 failed (ev/selftest.txt), which is the figure the body quotes. That figure is true only off CI.
- Null controls under the same `GITHUB_BASE_REF=main`: the reviewed head 552638f8dc gives 136 checks, 0 failed (ev/selftest_prev_with_GITHUB_BASE_REF.txt). The merge base 3b9749dac5 gives 117 checks, 0 failed (ev/selftest_base_with_GITHUB_BASE_REF.txt). The red is the delta's.
- To clear it: make the self-test hermetic. Run every fixture `static`/`main` call with `GITHUB_BASE_REF` and `SELFTEST_BASE` removed from `os.environ`, or point them at a resolvable base. Add a check that the self-test passes with `GITHUB_BASE_REF` set to a ref the fixture lacks. That pins this regression, so it can't come back off CI. The production change itself (an unresolvable named base is a problem, not a pass) is what round 1 asked for, and its CI behaviour on the live tree is fine: the job checks out with fetch-depth 0.

## Findings

none. Every round-1 item is resolved at this head (see Evidence), and the only open item is the block above.

## Evidence

- ev/HEAD.txt: ef7e3373e763942a38982c679541c5aa750b3935. The PR body `## Head` names this head and the code head 6a1966196c (step 7 ok). `git ls-remote origin refs/pull/3551/head` printed ef7e3373e7 at verdict time.
- Round-1 item 1 (prune CLI writes nothing): resolved. My driver (ev/run2.py, mine, built for this review) prints `KILLED prune-cli-no-write :: 141 checks, 1 failed`.
- Round-1 item 2 (prune CLI accepts unknown drops): resolved. `KILLED prune-cli-ignores-unknown :: 141 checks, 1 failed`.
- Round-1 item 3 (probe kept by listed directory): resolved. `KILLED probe-dir-ancestor-removed :: 141 checks, 1 failed`.
- Round-1 item 4 (fail-open on an unresolvable named base): resolved in production code. Mutants `unresolved-is-no-problem`, `unresolved-falls-through-to-first-parent`, `static-ignores-unresolved` and `merge-base-only-first-cand` are all KILLED. Its test fixture is the cause of the block above.
- RESULT own mutants at head (ev/own_mutants.txt): 24 run, 23 killed, 1 survived. The survivor is `table-untouched-skip-removed`, which round 1 judged equivalent: the untouched table compares equal to itself, so it only costs one `git show`. Not a finding. The 24 are the 3 round-1 survivors, the equivalent one, 9 reconstructed round-1 killed mutants (all still KILLED), and 11 new delta mutants over table_base/static/prune (all KILLED).
- RESULT `sh tools/ci/selftest_scope_mutants.sh` at head, locally without GITHUB_BASE_REF: 25 `== ` lines, 25 `self-test rc 1`, `SELFTEST-SCOPE MUTANTS: every mutant refused` (ev/selftest_scope_mutants.txt). This matches the body's 25. In CI the same step is BASELINE RED, because of the block.
- RESULT `SELFTEST_BASE=origin/main python3 -I tools/ci/selftest_scope.py static` at head: `114 gated step(s), 0 problem(s)`, rc 0 (ev/static.txt). This matches the body.
- The body says "No check of this branch's history was red at a read this seat made". That isn't true at this head, where instrument-self-tests is red (above).
- CI: `merge_train.py classify ef7e3373e7 --pr 3551` printed rc 2, `REFUSE selftests: the base's governance / instrument-self-tests job 131921846003 is in_progress ... (fail closed)`, at 13:47 and again at verdict time (ev/classify.log, ev/classify_final.txt). So classify was unreadable. I established the introduced red directly instead: CI log at the head, plus local base and previous-head controls (above).
- `merge_train.py owed-reds` (ev/owed_reds.txt) doesn't list `governance / instrument-self-tests`, so no `## Red checks` answer is owed. The block rests on step 11's INTRODUCED exception, not on owed-reds.
- `git merge-tree --write-tree origin/main ef7e3373e7`: rc 0, merges cleanly (ev/mergetree.txt).
- Step 12 scope: the delta is instrument and test only (tools/ci/), with no custom_components/ change, so the review isn't widened.
- Step 5 and step 14: the delta touches no VERSION, manifest, notes, claim file, budget or closure table.
- Full CI job log: ev/ci_instrument_selftests_head.log.gz. Relevant tail: ev/ci_selftest_scope_tail.txt.
- Earlier return on this ref: c367d9f40e (13:32 UTC, same nonce) holds `Fix review: merge ef7e3373e7` with `pending-ci: governance / instrument-self-tests`. That check had already concluded `failure` at 13:13 UTC (job 131898295736). This verdict supersedes it. I stacked it as a fast-forward child of c367d9f40e, not a force-push, so the earlier return stays readable in the ref's history.
