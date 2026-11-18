Fix review: merge 5910da5843e64d0b61dd99eb27c144200d628f75

bus-nonce: 2c628952673446cb83052bca5bc7affc

## Evidence

- Round 1 (full review, no prior reviewed head). Head 5910da5843e64d0b61dd99eb27c144200d628f75; merge base f567988b519a8cb28d6f6ebdf2328fd120d028bd; 0 commits behind origin/main; no role-contract drift since the merge base.
- RESULT CI: `merge_train.py classify` prints `GREEN 5910da5843e64d0b61dd99eb27c144200d628f75 pending: none red: none` (ev/classify.txt). The packet's one red, `tests / nightly-status`, is not in the `owed-reds` set and is not answered.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` returns rc 0, tree 8dbc6323 (ev/merge-tree.txt).
- RESULT control on origin/main's data at the head tree: base grader `293 passed, 0 failed` rc 0, head grader `295 passed, 0 failed` rc 0. This matches the body's figures.
- RESULT perturbation: the body's script is applied to a worktree at the merge base f567988b (the body used 7c2f4c30; both runs give the same counts). Base grader rc 1, `287 passed, 6 failed`, with the six FAIL lines the body names, including `65 vs 70`. Head grader rc 0, `295 passed, 0 failed`. See ev/P-base.log, ev/P-head.log and ev/perturb.py.
- RESULT mutation proof, re-run by me. I replaced each line with a one-occurrence assert and checked the restore with `cmp`:
  - M1 to M5 on the head data each fail `each id reader admits D0, D9, D17, DX0 and refuses 11 near-misses (5 readers)`, naming the reader (brief, quoted, finder, lens, verify).
  - On the perturbed tree, M6 (`DX0_BRIEF = false`) fails the scope and owner_seat checks.
  - M7 (`realOwn = []`) and M8 (`pubScopes = scopes`) each fail the two private-root arms.
  - M9 (DIMS copy unfiltered) fails five checks, both null-control arms among them, with `scopes.json has no seats for DX0`.
  - M1 on the perturbed tree adds the brief, DIMS and owner-only declaration failures.
  - No mutant survived. Logs: ev/M*.log and ev/P-M*.log.
- RESULT class sweep: I grepped the head grader for hand-written dimension-id patterns (`D\d`, `[A-Z]\d`, `D[0-9]`, `^D`). Two sites remain, `/^D4-s\d+$/` and `/^D1-s2's report…/`. Each is a fixed-dimension literal, not a generic id reader, so every generic reader goes through `DIM_ID` (ev/class-sweep.txt).
- RESULT scope: the three-dot diff touches `tools/policy/check-wave-script.mjs` and the delivery line `dev/programme/delivery/3721.md` only. `VERSION`, the manifest version, the release-notes heading, the claim files and every `*_budgets.json` are untouched (ev/diffstat.txt).
- No finder harness is named. The PR is the bootstrap grader half of a group, and the perturbation is the body's own instrument, disclosed as such. My re-run reproduces it.
- The body's head section names this head 5910da58 as unchanged since measurement at aaf7c692 plus a clean main merge. I measured at 5910da58.
- The body's single forward-carry item is routed (`Carry: dismissed: …`). carry_audit at the head reports 1 routed, 0 unrouted.

## Findings

none
