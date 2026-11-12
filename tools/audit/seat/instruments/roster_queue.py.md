# `roster_queue.py`

- `roster_queue.py` — the `roster-drain` beat row's queue runner: `run FIRST LAST`
  applies each queue line (`<op> <group> [arg] [--flag value]`, so `drop-carry G --match TEXT` works) through `roster_edit.py --push`,
  linting from a clone it owns and detaches at `origin/main` before every
  attempt (up to four, when main moved or a clean-lint push lost a race), and
  never moving the orchestrator's checkout. `readback SHA GROUP FILE` prints
  whether the roster at SHA holds the file's text as exactly one carry entry
  (exit 1 when none). When: the roster seat works a queue file; run it alone
  to replay a range. Refusal: a refused op is reported as `refused rc=N`, never
  forced; a `drop-carry` or `mark-carry` keyed by index is refused unrun on
  both paths (`replay_unsafe`), because a replayed line re-resolves the index
  on the list its first run shifted (R10-RCA-ROSTER-DRAIN-REPLAY): queue it
  `--match TEXT`; `append-carry @file` reports FAILED when the read-back cannot find the
  text. `--self-test` drives it offline over a stub editor and a scratch repo.
  The editor is `--editor` or the `roster_edit.py` beside the script, one file for
  `run` and `run --batch` (`resolve_editor`); the runner sets `HPO_ROSTER_LANE` in
  the editor's environment, which `roster_edit.py` requires for its structural ops.
  `show [GROUP] [--ref R] [--stage S]` and `diff REF_A REF_B` read the roster at a
  ref with `git show` and write nothing (`diff` exits 1 when the refs differ).
