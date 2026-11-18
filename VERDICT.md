Fix review: merge 2a374610679c6e56bf3f75a158e60741827451ec

bus-nonce: dbadd4bf531b1ae360b58f8e7a19ccd0

Round 3, scope `delta` over the reviewed head af0616cbe8dbd95e9a0ccb1e8822949f579a7cba (round 2: `Fix review: blocked`, review/3696 dd1cc7e774). Reviewed from a detached worktree at 2a374610679c6e56bf3f75a158e60741827451ec. `git diff af0616cbe8 2a374610679c` touches `tools/audit/seat/loop_ledger.py` alone, 29 added and 2 removed lines, all in `_self_test_reds` and the `MUTANTS` table; no line of the read changes and no `custom_components/` code is in the delta, so the scope is not widened (`ev/delta.diff`). The head is a merge of the code head 44a130aa4e onto af0616cbe8; it brings in nothing else. The contract read is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` does not touch `fix-review.md` (`ev/contract_currency.txt`). No finder harness is named; the mutant driver is this seat's own (`ev/mut.py`).

## Previous verdict's block, at this head

Item 1 (five surviving swaps): resolved. Each swap was applied to the code above `\nMUTANTS = {` only, since the table now quotes every needle. The unswapped copy ran first as the null control and ended `0 failed`. `python3 -I tools/audit/seat/loop_ledger.py --self-test --no-mutants` then failed under every swap (`ev/reviewer_mutants.txt`):

- `event != pull_request`: KILLED, 2 failed (the merge_group and workflow_dispatch null checks);
- `summary product counts machinery`: KILLED, 1 failed;
- `summary product != GREEN`: KILLED, 1 failed;
- `summary machinery != GREEN`: KILLED, 1 failed;
- `unread count over rows`: KILLED, 1 failed (`reds: the summary's unread column counts the reds read ...`).

Four more swaps on the same lines, added by this seat, were also killed: the event test excluding `merge_group` only (killed by the workflow_dispatch fixture), the event test excluding `workflow_dispatch` only (killed by the merge_group fixture), so each of the two new fixtures kills a swap the other does not; `on {len(reds)}`; and the machinery count reading the product verdict. `git status --short` in the worktree was empty after the run (`ev/worktree_status_after.txt`).

Round 1's items stay resolved and were not reopened (delta scope).

## Evidence

- Full self-test at the head: `python3 -I tools/audit/seat/loop_ledger.py --self-test` ends `loop_ledger self-test: 0 failed`, 99 `ok` lines, 35 of them `mutant killed`, no `FAIL` line. The five new `MUTANTS` rows each print `ok    mutant killed` (`ev/loop_ledger_selftest_full.txt`). These match the body's figures.
- CI: `merge_train.py classify 2a374610679c6e56bf3f75a158e60741827451ec --pr 3696` printed `GREEN 2a374610679c6e56bf3f75a158e60741827451ec pending: none red: none`, rc 0 (`ev/classify.txt`).
- Merge: `git merge-tree --write-tree origin/main 2a374610679c` exits 0 with origin/main at ae0ed64af8 (`ev/merge_tree.txt`).
- Head re-read before posting: `pull/3696/head` and the API both report 2a374610679c6e56bf3f75a158e60741827451ec.

Note: carry-audit: `carry_audit.py check` was not run. This seat got no `review-packet:`, and the body is not in the tree. The delta changes no carry line, and the `## Forward-carry` section is paperwork under C5.
