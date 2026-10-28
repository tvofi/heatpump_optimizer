Fix review: merge 44281492277f962676e72abb09b2202f872d9273
bus-nonce: 66bb853d4ef7e58b89f20f738a8ece10

# Fix review -- PR #2898, triage: batch 44 -- rule V132-V135 and V137-V140 as P219-P226

Round 1. Reviewed head: 44281492277f962676e72abb09b2202f872d9273, in a detached worktree at
that head. The authored code head is 92138b4a7. `dev/governance/roles/` has no diff between
the merge base and origin/main.

## Results

- Headings: from this batch on, a heading carries no proposal id, which is the contract's
  `## P<n>: <title>` form. Each `Source:` id resolves in `proposals.md`: V132-V135 map to
  P219-P222, and V137-V140 map to P223-P226. The proposal titles match the rulings. There is
  no `## V136` heading.
- The batch 36-40 rewrites change only the eight heading lines and the batch-40 #2886
  sentence. `a0e7664ea` is #2886's merge, and `ee5816b1` is a blob, as the body says.
  `roster_edit.ruling_verdict` reads P204-P211 the same at origin/main and at the head
  (`ev/ruling-verdicts.txt`): DEFER, DEFER, ACCEPT, ACCEPT, ACCEPT, ACCEPT, DEFER, ACCEPT.
- The mutation proof reproduces (`ev/mutation.txt`). `triage_refusal` passes P223's carry.
  It refuses that carry once P223 is mutated to DEFER. It refuses P220 as written and passes
  P220 once it is mutated to ACCEPT.
- Every line citation and count in P220-P226 holds at `e8cb7e683` (`ev/citations.txt`).
  That includes `merge_train.py` (5831 lines; :2516, :2567-2569, :2037-2038),
  `worktree_gc.sh` (701 lines; 388-392, 529, 562-563; lsof 0; fetch 0), `cloud_dispatch.py`
  (:19-36, :334-341), `INSTRUMENTS.md:516-519`, `handover_prompt.py` (280 lines; :46), the
  settings and hooks greps, and the owner groups' stages and carry numbers at roster
  `de410e4c9`.
- `git merge-tree --write-tree origin/main <head>` exits 0 (tree `944fb33f7`, origin/main
  `6e5995e51`) (`ev/merge-tree.txt`).
- Live check-runs at the head (`ev/check-runs.txt`): 55 runs, 38 success, 17 skipped,
  0 failure, 0 pending. There is no red to answer, and the body's `## Red checks` is `none`.
  `VERSION`, the manifest and the notes heading are untouched.

## Findings

- F1 (non-blocking): P223's ACCEPT carry is not yet on `R10-FLY-WORKTREE-GC`. At the roster
  tip `de410e4c9` the group holds 1 carry, and none cites P223. This is the triage contract's
  route, not a missing propagation: the orchestrator appends the carry through
  `roster_edit.py`. That tool refuses the carry until the ruling is on the roster branch or on
  origin/main (`triage_refusal`, 466). The carry text is in the ruling, and its controls are
  stated. Carry: R10-FLY-WORKTREE-GC
- F2 (non-blocking): P220 routes as a reopen of `R10-TRAIN-OVERLAP-GRADE`, which is `done`
  and holds carries 9, 13 and 15 unimplemented, "queued for the roster seat". I cannot see
  that queue entry from the tree. Until the reopen lands, dispatch cannot see the group.
  Carry: R10-TRAIN-OVERLAP-GRADE
- F3 (non-blocking): two P220 and P223 figures are not verified. I could not re-derive the
  s7 `train.log` count (857 lines, one `ALREADY #2876` line), because no train log on this
  machine holds that line. P223's figures (65 worktrees, 10 GiB free) are a snapshot. Neither
  number decides its ruling. Carry: dismissed: snapshot figures, rulings stand on the in-tree citations
