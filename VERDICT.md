Fix review: merge 6e8fad157f35ac9023fc5ea42ceea9e2ee89fc07

bus-nonce: 60923d79ed6ee0479f645f4c46b9c314

## Scope

Delta round over the reviewed head e3622cb3d8c4f718370cc687ea1087d09da0da82 (packet: `## Review scope: delta`). The delta is two merges. 669c3f589c (handoff) is the fixer's hand-resolved merge of main 3b9749dac5 into e3622cb. 9713128b61 merges 669c3f5 with an identical tree, and 6e8fad157f is update_pr's clean merge of main cfa8683. No production (`custom_components/`) line of the branch's patch changed, so the scope is not widened. The `custom_components/` files in the delta are main's own content.

## Resolution read-back

- `git show --remerge-diff 669c3f5` reports one conflicted file: `tools/audit/seat/merge_train.py` (`ev/remerge-diff-669c3f5.txt`). `tests/closures.json` was resolved by the LEDGER-MERGE driver as a set. 6e8fad1 has no conflicted file.
- Main's side (#3528) adds `rollup_walk`, which the resolution keeps byte-for-byte.
- The branch's side keeps the whole P436 block (the barrier comment, `BlindRead`, `Busy`) and the reviewed signature `classify(latest, required, busy)`. Main's `busy=()` is not a change on main: the merge base f44e761 already had it. So nothing of main's was dropped by keeping the branch's signature.
- At head, every caller of `merge_train.classify` in `tools/` passes `busy`: merge_train.py lines 838, 2299, 2303, 2341, 2356 and 4072, and orchestrator_tick.py line 1214. The same holds in the `git merge-tree` result against the current origin/main ad95665.
- The branch patch is unchanged. The sorted +/- lines of `diff merge-base(e3622cb, 3b9749d)..e3622cb` and `diff merge-base(origin/main, head)..head` are identical. Both cover the same 13 files, +740/-68 (`ev/branch-patch-reviewed.diff`, `ev/branch-patch-head.diff`).

## Evidence

- `git merge-tree --write-tree origin/main 6e8fad1` (origin/main ad95665) is clean. Its only note is the LEDGER-MERGE set merge of closures.json (`ev/merge-tree-origin-main.txt`).
- At the head, `merge_train.py --self-test` reports 742 checks, 0 failed, rc=0 (`ev/merge_train-self-test.txt`).
- At the head, `dev/audit/harnesses/r10_gate_defer_barrier.py` exits rc=0 (`ev/harness-r10_gate_defer_barrier.txt`).
- Resolution mutant B makes main's `rollup_walk` return only the first page. 4 checks FAIL (the A5 platform and A5 serial checks), so main's clause is pinned at this head (`ev/mutant-B-rollup-walk-onepage.txt`).
- Resolution mutant A takes main's side of the signature line (`busy=()`) and survives: 742 checks, 0 failed (`ev/mutant-A-busy-default.txt`). The mutant is behaviourally equivalent. The barrier judges the `busy` value at run time inside `classify`, and the self-test's "busy omitted" and "busy a literal ()" plants are both refused either way. So either side of that line is safe, and the resolution took the reviewed one.
- CI: `merge_train.py classify 6e8fad1 --pr 3499` returned `GREEN 6e8fad157f35ac9023fc5ea42ceea9e2ee89fc07 pending: none red: none` (rc=0) at 14:54:04Z, after WAIT polls from 14:34Z (`ev/classify-log.txt`). The packet's `required-wait` signal (gate failure in the digest) was superseded by classify, as the brief directs. With no red, there is no Red checks answer to give.
