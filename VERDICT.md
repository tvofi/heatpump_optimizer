Fix review: blocked eb07df9be8dbea332c525525ab538ab3e7c60a41 under-scoped: the wholesale table replacement drops the app-push and throwaway-git-helper objects flags that b06e830153 restored by union and that a Linux strace record at this head measures; commit the base table unioned with the artifact instead

bus-nonce: cc34213f31e8b0b8195c7f23d5c6de34

## Block

The PR replaces `tools/ci/selftest_closures.json` with CI's push-run measurement, byte for byte. That makes main's drift check pass, but it also drops every entry the committed table held beyond what that single CI run read. Those extra entries were not stale over-approximation. `b06e830153` ("union the selftest_closures.json re-record with the merge-base table (restore 9 path entries, 3 git markers, 2 objects flags)") put them back on purpose, because two recordings disagreed. The PR's diff reverses that union:

- app-push: objects True -> False, git [merge-base] -> []
- throwaway-git-helper: objects True -> False, probes 213 -> 0
- tick-loop: index True -> False, objects True -> False
- beatd: index True -> False, probes 2339 -> 18 (beatd is one of the two steps `4a013ff156` names as differing between recordings)

These flags are real. I ran `record` on Linux with strace at this head, kept the traces and ran the governance step's own `selftest_scope.py check --traces`. Over the PR's table it refuses `app-push: it read the objects, the table says not` and `throwaway-git-helper: it read the objects, the table says not`. A step that reads the object store must take every diff, so this table lets a pull request skip those two self-tests on changes they read. The drift check cannot catch that: it only runs on a push to main, where CI's environment does not trigger these reads.

Remedy, measured: union the base table with the artifact, per step (lists unioned, flags OR'd, run_sha from the artifact). That union gives 0 refusals against CI's measurement, so main's red is fixed just the same. Against the local Linux measurement it gives 3 refusals instead of 7, and none of the 3 are flags (they are the `dev/programme/delivery/5.md` probes this seat's environment produced, see Evidence). This repeats `b06e830153`'s method. Re-recording the 3 local-only probes is optional.

## Findings

- Follow-up: the push-time drift check measures in one environment, CI on a push to main. A read that happens only in another environment, such as the objects reads above under a Linux seat `record`, can be dropped by "commit the artifact" (the instrument's documented remedy) with nothing to refuse it. The docstring's instruction to commit that file or re-record should say to union with the committed table, or `check --write` should write the union. Carry: R10-HOTFIX-SELFTEST-SCOPE-TABLE
- Follow-up: `check --write` passes the measurement through `write_table`, whose `compact_probes` drops a probe that sits under a directory the step listed. `drift()` only excuses such a probe if the committed table lists that directory. So drift over the uploaded artifact undercounts the live check by every such probe. That is the 33-versus-34 gap (throwaway-git-helper lists `.`, so its `supply_hold.py/.gitattributes` probe was compacted away). Carry: R10-HOTFIX-SELFTEST-SCOPE-TABLE
- Follow-up: the PR body says the refusals include "tick-loop index and objects flags". CI's 34 refusals contain no flag refusal for any step, and in this diff tick-loop's flags go from True to False, which is the opposite direction. The re-cut body should state the narrowing, not list it as a refusal. Carry: R10-HOTFIX-SELFTEST-SCOPE-TABLE

## Evidence

- Head reviewed: eb07df9be8dbea332c525525ab538ab3e7c60a41. It is still `refs/pull/3557/head` at verdict time. Merge base: 154dbb4c61652135381ce66646d23f7109d1c142. `git merge-tree --write-tree origin/main <head>` is clean (origin/main c67c1933be).
- CI: `merge_train.py classify ... --pr 3557` printed `GREEN eb07df9be8dbea332c525525ab538ab3e7c60a41 pending: none red: none` (ev/classify.log). The head has no owed red, so no `## Red checks` answer is due from the review.
- Orchestrator point (1), the real check on Linux with strace. `record` ran all 116 non-drift steps at the head, every one OK (ev/record-head.log). Traces were kept by ev/record-keep-traces-driver.py, which wraps `record` and only disables its trace deletion. I folded the traces with the step's own command, `python3 -I tools/ci/selftest_scope.py check --traces DIR`:
  - at the head: `selftest_scope check: 114 gated step(s), 7 refusal(s)` (ev/check-head-linux.txt)
  - at the merge base: `selftest_scope check: 114 gated step(s), 8 refusal(s)` (ev/check-base-linux.txt)
  - Both lines use one measurement taken in the head's tree. The two trees differ only in the table and in `dev/programme/delivery/3557.md`. I stopped the separate base-tree record because it could not finish inside the 30-minute job limit.
  - The local base result does not reproduce CI's 34 refusals. This seat's environment reads less than CI does on most steps (hundreds of over-scoped notes), which is consistent with the reads being environment-dependent.
- Orchestrator point (2), 34 versus 33. CI's log (job 131963716179, ev/ci-job-131963716179-drift-step.txt) has 34 UNDER-SCOPED lines. I replayed `drift(base table, artifact-as-measured)` at the base (ev/drift-over-artifact-at-base.txt) and got `114 gated 33 refusals`. The one missing line is `throwaway-git-helper: probes misses ['tests/mutation_ledger/killed_by/supply_hold.py/.gitattributes']`. `write_table`'s `compact_probes` drops it because the measured dirs of throwaway-git-helper include `.`, the ancestor of every path, so the artifact's probes are `[]`. The other 33 lines match CI's line for line, which is consistent with the PR's table being the artifact. I could not check the "byte for byte" claim directly: the artifact's blob host was refused by this seat's egress proxy (403).
- Union check (ev/union-check.txt): head table against CI artifact 0 refusals, against local Linux 7. Union against CI artifact 0, against local Linux 3.
- `VERSION`, the manifest and RELEASE_NOTES.md are untouched. The diff is two files: the table and the delivery row.
- The mutation proof (revert the table to the base and get 33 or 34 refusals; the artifact table gives 0) is confirmed by the replay above. No finder's harness is named, and that fits a hotfix of a measured table.
- Round: first.
