Fix review: merge 433536b65f2507d47eaeeadebc8b9461bac19013

bus-nonce: 14c317aba55301a82e074d2f203f8a6d
pending-ci: classify prints `WAIT 433536b65f2507d47eaeeadebc8b9461bac19013 pending: gate red: none` (no context named; runs created during the GitHub outage and not yet started)

Round 3, continuation of the finished review at d925d867badb9a3ac12b2a73133174f9a8bc1b4a (previous verdict probe/rev-3479-aeb68873 at f36a81b9, which stands). The head moved to 433536b65f2507d47eaeeadebc8b9461bac19013 by one automatic merge of origin/main; nothing of the earlier review is redone.

## Evidence

- Delta verified as the merge only: `git log d925d867..433536b65 --not origin/main` lists one commit, 433536b65 "Merge remote-tracking branch 'origin/main' into fix/r10-prepr-residue". `review_carry.py d925d867 433536b65` prints CARRY (0 of 1 branch-only commits are non-merge) (ev/review_carry.out). No production, harness or test delta beyond main's own changes, so the earlier verdict's re-runs and mutants carry unchanged (ev/head.out, ev/mutant*.out are from d925d867).
- Merge: `git merge-tree --write-tree origin/main 433536b6...` exit 0, no conflict (ev/merge_tree.out).
- CI: `merge_train.py classify` exits 3 printing `WAIT ... pending: gate red: none`; not a red.
- Carry audit at this head: `carry_audit.py check`: 1 finding item, 1 routed, 0 unrouted, 0 bad destinations (the earlier `#3479 | O1` tokens are dropped: #3479 has no roster owner now, so the dismissal stands alone under its group).

## Findings

- Out of scope: the real outer-prepr step 3h end-to-end path (full prepr run with pool full) is covered only by the cut-function arms plus the static check that the --self-test branch never calls take_slot, not by a whole prepr run. Carry: R10-PREPR-RESIDUE | dismissed: the cut take_slot is the code step 3h calls, the label/join/WARN paths and the self-test branch are each pinned by a mutant that fails, and a full pool-full prepr run is hours of heavy gate for no further discriminating row.
