# `proof_watch.py`

- `proof_watch.py` — watches one named check-run at one pinned head of one
  pull request and, once it completes `success` beside green required contexts
  and a valid merge verdict at that exact head, merges through `merge_pr.sh`.
  When: a long validating run whose green-to-merge window would otherwise sit
  unattended (the 4.5 h proof misread as failed, P8). Refusals: a head that
  moved off the pin, a named check that completed not-success, an exceeded
  `--budget`, a red required context (the ruleset's list, read through
  `merge_train.required`), an unmergeable pull request and a head
  `app_approve --dry-run` does not verdict — each aborts with a logged report
  and no merge; one instance per pinned head (flock), and `--dry-run` passes
  every guard and touches nothing. `--mode owner` hands `merge_pr.sh` its
  `--mandate <comment-id>`, and refuses at launch without one.
