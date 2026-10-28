Fix review: merge ba4bba59b10245d6264290f48652cfcddf85374a
bus-nonce: 8d61db24de854ef9399e5a1f5a28a9c4

# Fix review -- PR #2901, record: delivery rows for #2898 (autofix)

Round 1. Reviewed head: ba4bba59b10245d6264290f48652cfcddf85374a, in a detached worktree at that
head, against origin/main b9e286254. `dev/governance/roles/` has no diff between the merge base and
origin/main. The PR was opened by `app/hpo-author`.

## Results

- The three-dot diff touches two files: `dev/programme/delivery/2898.md` changes 1 line, and
  `dev/programme/delivery/2901.md` is a new 1-line file (`ev/diff.txt`). Both are row files, so the
  diff holds no code and no claim file. `VERSION`, the manifest and the notes heading are untouched.
- The row matches the API. `2898.md` reads `**merged `b9e2862`**`. The GitHub API reports #2898 as
  `MERGED` at 2026-10-28T02:12:50Z, with merge commit `b9e286254e152b6647b37b5612bd340dd39daca0`
  (`ev/api-2898.txt`). `2901.md` reads `**open**`, which is true: #2901 is open at this head.
- Window: the merges in `e8cb7e683..origin/main` are #2897 (`6e5995e51`) and #2898 (`b9e286254`).
- `python3 -I tests/delivery_status.py --require-rows` at the head prints
  `DELIVERY STATUS OK -- 2 rowed, 0 pending, 0 overdue` and `every merge in the window carries a
  row`, rc 0 (`ev/delivery_status.txt`).
- `record_row.py --automerge-check --pr 2901 --head ba4bba59b...` prints
  `AUTOMERGE OK #2901 at ba4bba59b10245d6264290f48652cfcddf85374a`, rc 0 (`ev/automerge-check.txt`).
  It ran with `SSL_CERT_FILE` set to certifi's bundle and `GH_TOKEN` from `gh auth token`.
- `git merge-tree --write-tree origin/main <head>` exits 0 (`ev/merge-tree.txt`). The packet refuses
  nothing, and `carry_audit` routes 0 items.
- Live checks at the head (`ev/check-runs.txt`): no failure. The body's `## Red checks` answers
  `record`, `nightly-status` and `delivery-status` as main-graded, which is how `fix-review.md` step
  11 treats them.

## Findings

- F1 (non-blocking): #2897's own row, which is on main and outside this diff, still reads
  `**open**`. The API reports #2897 `MERGED` at `6e5995e51`. `delivery_status.py` counts it as rowed,
  because it classifies on the row's presence and not on the word. That is the gap
  `delivery-status-tracking.md` already records ("a row is a claim, not a reading"). This PR's own
  rows are true. Carry: dismissed: documented gap in delivery-status-tracking.md; not this diff
- F2 (non-blocking): the rewritten `2898.md` drops the `(R10-FLY-WORKTREE-GC)` group tag that the
  open row carried, and uses the beat's neutral phrasing. That is consistent with the body.
  Carry: dismissed: by the beat's design

## Check state at this head

Final read, at about 02:53Z (`ev/check-runs.txt`): 55 runs, 36 success, 19 skipped, 0 failure and 0
pending. `gate` and `pr-contract` concluded success.
