Fix review: merge 5d88dea6aa3e86ed6296ad016bba197f31bc1cd4

bus-nonce: 1c7f5d56ddd687b033ba49245e41ae91

## Evidence

- Round 1 review of #2783 (roster batch, record lane), measured at head 5d88dea6aa3e86ed6296ad016bba197f31bc1cd4; the head was still 5d88dea6aa3e86ed6296ad016bba197f31bc1cd4 on origin when this was written. Contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Three-dot diff against merge base 662a3809c (= origin/main): two files, `dev/programme/rosters/wave-r10-groups.json` (+3/-3 net, two hunks) and `dev/programme/delivery/2783.md` (the PR's own row). VERSION, the manifest, the notes heading and both claim files untouched (ev/diff_merge.txt).
- Op shape: replaying `roster_edit.op_set_stage(R10-STRUCTURE-ALIAS, done, 5c0ee109305fc4f377c9326c712156b9ceb0e638)` and `op_append_carry(R10-FLOW-AUTOTRAIN, <text>)` on the merge-base roster and dumping with the tool's canonical form gives the head file byte for byte (RESULT: replay == head bytes: True, ev/op_replay.txt). No other group or key moved.
- Handoff parity: the R10-STRUCTURE-ALIAS and R10-FLOW-AUTOTRAIN group objects at the head equal those on `origin/handoff/audit-r10-roster` at 2381e1121 and at its current tip 2124781cf. 5c0ee1093 is on main (merge of #2711, fix/r10-structure-alias).
- Restored carry: it reaches R10-FLOW-AUTOTRAIN as carry index 9 of 10 with its text intact ("From R10-TRAIN-UPGRADE (handoff/r10-train-upgrade b1cba1ac; finding-propagation.md). ... Re-measure against the merged train, not the b3dceb5ca base."). That matches the body's "exact match at index 9". The text was never on main (`git log -S` on main is empty), so "restored" means carried over from the roster handoff ref, which is what the body says ("missing from main").
- JSON valid (`python3 -m json.tool`). `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json`: TOTAL 0 error(s), rc=0 (ev/brief_lint.txt).
- Body figures: f626833e5 has a single parent 9d0ddf8af (merge of #2776), as stated. The head merges origin/main 662a3809c, as stated. Mutation proof and null control are n/a: there is no code line, so there is no mutant to draw.
- Merge: `git merge-tree --write-tree origin/main 5d88dea6aa3e86ed6296ad016bba197f31bc1cd4` exits 0 (tree 5ee1b8ecc), no conflict.
- CI at this head (check-runs API, 01:19Z): one `arm` skipped; prelude/refresh/cancel-superseded for runs 40149424514 and 40149424362 still queued since 01:08Z. No check is red, so step 11 owes no answer. pr-contract had not reported, so the body check is not yet evidenced by a run.

## Findings

- The PR body names an out-of-tree source by an absolute home path that contains an account name (the out-of-tree carry-train-upgrade-autotrain.md, cited under a macOS home directory). A later seat cannot resolve that file, and the brief rules out host or home paths. The roster data itself is unaffected, and the provenance is fully established by the in-tree ref 2381e1121, which I verified. Carry: dismissed: body text only, not in the tree; the in-tree provenance (handoff/audit-r10-roster 2381e1121) verifies independently.
