Fix review: blocked 05158ac25eba0015cc0eb365592a11711f9b249e body-not-applied: the repaired carry 16 split is in BODY.md 6b5bdd4d but the PR's own body still dismisses carry 16 whole

bus-nonce: 60cfbc157357690ad94753ef0edd093a

## Block

Scoped re-check of carry 16 only, at head 05158ac25eba0015cc0eb365592a11711f9b249e. The repair is correct **as written** in BODY.md at handoff-body/r10-standing-contracts-p2-p4 6b5bdd4d. Part (1), judge every loop, stays open with `Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it`, the same valid shape as carries 21-24 and 27. Part (2), hooks, is dismissed as implemented at f0c6bbfd7. The roster (handoff/audit-r10-roster b600ca7d) leaves carry[16] unmarked, so part (1) really is open there. **That repair has not reached the pull request.** The live PR #3492 body (last updated 06:08:15Z) still reads "Carry 16: dismissed. ... Carry: dismissed: implemented at f0c6bbfd7", which is the dismissal the earlier verdict blocked. Its ## Red checks also still reads "none", not BODY.md's version. BODY.md was committed at 06:10:01Z, after the PR's last update, so the body was never set from it (ev/pr_body_carry16.txt). The body that merges is the PR's, so the defect stands at the merge. Cure: set the PR body from BODY.md 6b5bdd4d and do nothing else. The code needs no change, and this verdict's checks of the code still hold.

## Findings

- Survivor (carried unchanged from verdict 6b86eca5): the self-test pins only step (3). Restoring main's steps (2), (4) or (6) leaves sweep_render --self-test at 37 checks, 0 failed. Carry: dismissed: the carry's control names one mutant; optional hardening at the fixer's discretion

## Evidence

- Head reviewed: 05158ac25eba0015cc0eb365592a11711f9b249e (ev/HEAD.txt). It is e199f727 plus a merge of main (2ced371c) and dev/programme/delivery/3492.md. Its three-dot diff against merge-base, excluding dev/programme/delivery/, is byte-identical to e199f727's diff (cmp), so the earlier review of the code stands unchanged.
- Merge with main: git merge-tree --write-tree origin/main 05158ac25eba0015cc0eb365592a11711f9b249e exits 0 (ev/merge_tree.txt).
- BODY.md delta 6b5bdd4d: ev/body_6b5bdd4d.diff. The carry 16 split is as dispatched, and the other carry lines are unchanged.
- CI: classify at review end is in ev/classify.txt (WAIT, gate red: none, at the first read). It was not waited on, because the block is body-only and does not depend on CI.
- Everything else in verdict 6b86eca5 stands, per the dispatch.
