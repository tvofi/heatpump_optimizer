Fix review: merge 8d965647dd05f2100997493175fb649e8e859b26

bus-nonce: fae76273b6bc2e14aa0f4bd260caa6fe

## Scope

Round 3, delta-scoped (resolution delta, fix-review.md step 12): round-2 verdict `merge` at 07b83e9b28ab3a21e3a1ad8d9b38eea27ee707e0; head 8d965647dd05f2100997493175fb649e8e859b26 is the merge of origin/main 88744e5738c1171bd1432eada1cb75a18a291677 into it. Only the merge resolution was judged. dev/governance/roles/ is unchanged between the merge base and origin/main (contract current).

## Evidence

- RESULT resolution: re-running `git merge-tree --write-tree 07b83e9b2 88744e573` yields tree 6d374b86e9d6, identical to the head's tree; the ledger driver printed `LEDGER-MERGE: resolved tests/structure_budgets.json`. No hand edits in the merge commit (ev/resolution_remerge.txt).
- RESULT structure_budgets: 14 lines differ from the PR side (7 metrics) and 4 lines (2 metrics) from main's side. Every metric equals `python3 tests/structure.py` on the head tree (STRUCTURE RATCHET PASSED, every `ok` line has measured == budget). Against main: class_excess_loc 18217 -> 18209 and max_class_loc 8457 -> 8449 go down; every other metric and recorded_at equal main; nothing rises (ev/structure_head.txt, ev/budgets_vs_main.txt).
- RESULT merge with current origin/main 50af6174f: `git merge-tree --write-tree` exit 0, no conflict (main moved 3 commits, delivery rows only) (ev/merge_tree_vs_main.txt).
- RESULT version: VERSION, the manifest and RELEASE_NOTES.md are untouched against main.
- RESULT CI at this head: pull_request run 40064513091 is green across the board, gate success and pr-contract success (started 06:02:35Z, after every other run concluded). The duplicate workflow_dispatch run 40064519767 has gate=failure whose only line is "run(s) [40064513091] at this head are still being judged; their gate decides" -- a deferral to the run whose gate then passed, not a red on the change, so no root-cause answer is owed (ev/ci_checkruns.txt).
- RESULT head: branch and refs/pull/2683/head both at 8d965647dd05f2100997493175fb649e8e859b26 when posting (ev/head_recheck.txt).
- Mutation proof, harness and claim checks were settled in round 2 and the resolution delta touches no production or test line of the PR side beyond main's own content, so they were not re-run.

## Findings

None.
