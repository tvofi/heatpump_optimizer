# `merge_pr.sh`

- `merge_pr.sh` — merges one PR after its evidence checks. When: a single
  verdicted PR; for more than one, `merge_train.py` below. Owner mode takes
  `--mandate <comment-id>` and reads that #201 mandate live; `--ready` marks a
  draft ready. Refusal: a verdict or head mismatch stops the merge before the
  merge API call; a draft without `--ready`, or owner mode with no mandate in
  force, refuses before anything posts. Before its CI wait it runs
  `merge_train.py unstale` (below) at the head. `--self-test` also drives the whole
  script offline over a scratch clone and a fake `gh`, so the `gh pr merge …
  --match-head-commit` line is pinned: replaced by `exit 0` it records no
  merge and the null control reddens (#2444).
