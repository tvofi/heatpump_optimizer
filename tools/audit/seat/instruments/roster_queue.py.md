# `roster_queue.py`

- `roster_queue.py` — the standing roster seat's queue runner: `run FIRST LAST`
  applies each queue line (`<op> <group> [arg] [--flag value]`, so `drop-carry G --match TEXT` works) through `roster_edit.py --push`,
  linting from a clone it owns and detaches at `origin/main` before every
  attempt (up to four, when main moved or a clean-lint push lost a race), and
  never moving the orchestrator's checkout. `readback SHA GROUP FILE` prints
  whether the roster at SHA holds the file's text as exactly one carry entry
  (exit 1 when none). When: the roster seat works a queue file; run it alone
  to replay a range. Refusal: a refused op is reported as `refused rc=N`, never
  forced; `append-carry @file` reports FAILED when the read-back cannot find the
  text. `--self-test` drives it offline over a stub editor and a scratch repo.
