Fix review: merge a8cf7889ef2cbbb0b913d2e9f5eabb918fef5996
bus-nonce: 96ed35a0a6f885aad0389a51d5f98f90

# Fix review -- PR #2897, record: rewrite the open rows of #2878, #2888, #2889

Round 1. Reviewed head: a8cf7889ef2cbbb0b913d2e9f5eabb918fef5996, in a detached worktree at
that head; the base e8cb7e68302b1d350bb8219fea99e911170af030 in a second detached worktree.
`dev/governance/roles/` has no diff between the merge base and origin/main.

## Results

- Merge facts (REST `pulls/<n>`, `ev/merge-state.txt`): #2878 merged `22a2c9c707c1`, #2888
  merged `939f0c642876`, #2889 merged `6b9bf5b58897`. Each row in the diff names that PR's
  merge sha and the API title. The roster at origin/main maps #2878 to R10-ROSTER-BATCH24 and
  maps #2888 and #2889 to no group, so dropping `(R10-PREPR-CAP)` from #2888 is what the tool
  computes. It is not a hand edit.
- `record_row.py --plan` over the three merges from `--enumerate --since v7.0.4`
  (`ev/plan.txt`): it plans all three at the base and plans `[]` at the head. Each planned line
  is byte-equal to the row file at the head.
- `tests/delivery_status.py --require-rows --since v7.0.4` (`ev/delivery_status.txt`): at the
  head it gives rc 0, `226 rowed, 0 pending, 0 overdue`. At the base it gives rc 1,
  `223 rowed, 3 pending`, and the three pending rows are exactly #2878, #2888 and #2889.
- The diff changes only `dev/programme/delivery/{2878,2888,2889,2897}.md`. The head commit
  adds only the PR's own row, on top of the authored code head `7a8c06a21`, as `## Head` says.
- `git merge-tree --write-tree origin/main <head>` exits 0 (tree `eefa3832a`, origin/main
  `07295d4ea`) (`ev/merge-tree.txt`).
- Live check-runs at the head (`ev/check-runs.txt`): 55 runs, 36 success, 19 skipped,
  0 failure, 0 pending. There is no red to answer. `VERSION`, the manifest and the notes
  heading are untouched.
- No mutation proof applies, because the diff is rows only.

## Findings

- F1 (non-blocking): the body's `## Null control` says `delivery_status.py --require-rows`
  "passes on the base as well as at this head". That is false. At the base it exits 1 with the
  three rows pending, because an `**open**` row counts as no row for a merged PR. The real
  control is stronger than the body claims: the check is red at the base and green at the head,
  and this verdict records that measurement. The body text was written by hand, not by
  `record_row.py`. Carry: dismissed: body prose only; the measured control is in this verdict's ev/delivery_status.txt
- F2 (non-blocking, seat environment): under `python3 -I`, `record_row.py --enumerate`
  failed on this machine with `CERTIFICATE_VERIFY_FAILED` until `SSL_CERT_FILE` pointed at
  certifi's bundle. This is local seat setup, not the PR's. Carry: dismissed: local Python CA setup, not a tree defect
