Fix review: merge 2a374610679c6e56bf3f75a158e60741827451ec

bus-nonce: none supplied: this round's dispatch carried no nonce, so no probe/rev-3696-<nonce8> ref was pushed and the bus has not confirmed this verdict. Carry: dismissed: the orchestrator's relay owes the nonce, not this verdict

Round 3, scope `delta` over the reviewed head af0616cbe8dbd95e9a0ccb1e8822949f579a7cba (tvofi 2026-11-09). Reviewed from a detached worktree at 2a374610679c6e56bf3f75a158e60741827451ec. The delta is 44a130aa4e, one authored commit on `tools/audit/seat/loop_ledger.py` (self-test and `MUTANTS` table only, no line of the read changes), and the merge 2a374610679c6e56bf3f75a158e60741827451ec of it onto af0616cbe8, whose tree equals 44a130aa4e's. No production (`custom_components/`) delta, so the scope is not widened. The mutant driver is the reviewer's own (`ev/mut_delta.py`, round 2's `mut.py` with each swap applied above `def _self_test_reds` only, because the new `MUTANTS` rows quote each needle). No finder harness is named.

## Previous verdict's block, at this head

Resolved. The five survivors, each run through `python3 -I tools/audit/seat/loop_ledger.py --self-test --no-mutants`, against an unmutated control that ends `0 failed` (`ev/delta_mutants.txt`):
- `event != pull_request` on the column's event test: KILLED, 2 failed (`NULL reds: a merge_group run ...`, `NULL reds: a workflow_dispatch run ...`).
- product count reading the machinery verdict: KILLED, 1 failed (`reds: the summary counts a verdict red only where it reads red ...`).
- product `!= GREEN`: KILLED, same check.
- machinery `!= GREEN`: KILLED, same check.
- unread count over `rows`: KILLED, 1 failed (`reds: the summary's unread column counts the reds read, never a run with no job listing`).
Each has a `MUTANTS` row naming the killing check. The full self-test ends `loop_ledger self-test: 0 failed`, rc 0, 99 `ok` lines, 35 of them `mutant killed` (30 at af0616cbe8), no `FAIL` (`ev/loop_ledger_selftest_full.txt`).

## Evidence

- CI: `merge_train.py classify 2a374610679c6e56bf3f75a158e60741827451ec --pr 3696` printed `GREEN 2a374610679c6e56bf3f75a158e60741827451ec pending: none red: none` (`ev/classify_last.txt`). No red is owed a `## Red checks` answer.
- Merge: `git merge-tree --write-tree origin/main 2a374610679c6e56bf3f75a158e60741827451ec` exits 0 with origin/main at the SHA in `ev/merge_tree.txt`; no driver line on stderr.
- The body's `## Head` names 2a374610679c6e56bf3f75a158e60741827451ec and 44a130aa4e as the code head. Its merge-tree sentence names origin/main at 99a4010e47, older than the main this review measured; both merge cleanly. Note: stale-body: merge-tree figure measured at an older origin/main. Carry: dismissed: paperwork at a clean merge, re-measured here
- Head re-read via the pulls API before posting: 2a374610679c6e56bf3f75a158e60741827451ec (`ev/HEAD.txt`). The worktree was restored after the swaps (`git status --short` empty).
- Not re-run in this delta round: the structure ratchet, `tests/entities.py`, archscore and the enumerator list in `## Unpinned sites`; the delta touches only self-test lines, and CI's heavy runs are cited instead.
