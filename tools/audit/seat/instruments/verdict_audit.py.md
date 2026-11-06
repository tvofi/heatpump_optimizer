# `verdict_audit.py`

- `verdict_audit.py` — maps every open PR to its latest verdict and the
  holder it is owed, and prints one `UNHELD` line per PR whose next step
  nobody visibly holds: a merge verdict only main-merged since (owed to the
  merge train), a blocked verdict (owed a repair fixer, or `update_pr` then a
  reviewer once the handoff moved on), or no verdict ref (owed a first
  reviewer). Held means queued in a train log modified within 3 h, or a fire
  line in the last 12 h naming the PR or its topic; `--skip FILE` lists
  `#<N> <ruling>` lines for PRs held by an owner ruling. Owner ruling (tvofi
  2026-11-06): no PR waits unheld. When: every second pass of
  `sweep_runner.sh`, or by hand from a checkout with origin fetched. Reads
  only (`gh pr list`, `git ls-remote`, `git fetch`, `git show`).
  `--self-test` drives each owed state beside its held null control.
