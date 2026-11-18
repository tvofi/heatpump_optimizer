# `merge_pr.sh`

- `merge_pr.sh` — merges one PR after its evidence checks. When: a single
  verdicted PR; for more than one, `merge_train.py` below. Owner mode takes
  `--mandate <comment-id>` and reads that record-issue mandate live; `--ready` marks a
  draft ready. Refusal: a verdict or head mismatch stops the merge before the
  merge API call; a draft without `--ready`, or owner mode with no mandate in
  force, refuses before anything posts. Both modes read whose head the pull
  request is by `tools/pr/outside.py`'s `cross_repository` (unread refuses):
  owner mode refuses a fork head, and app mode merges one only where
  outside.py's `check` at origin/main admits that exact head, its refusal
  printed `OUTSIDE CONTRACT REFUSES ...` before anything posts. outside.py
  runs from origin/main's blob or not at all (the train's rule): it is
  compared before whose head is read, and every file of the train's
  `OUTSIDE_MAIN_COPIES` before the contract; a stale copy refuses `OUTSIDE
  REFUSE: ... is not origin/main's copy`. Before its CI wait it runs
  `merge_train.py unstale` (below) at the head. `--self-test` also drives the whole
  script offline over a scratch clone and a fake `gh`, so the `gh pr merge …
  --match-head-commit` line is pinned: replaced by `exit 0` it records no
  merge and the null control reddens (#2444).
