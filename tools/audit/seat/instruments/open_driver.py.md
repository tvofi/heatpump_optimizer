# `open_driver.py`

- `open_driver.py` — one pass of the open arm: reads a tick board's
  `handoff-no-pr refs/heads/handoff/<topic> <sha>` lines (stdin or `--board`),
  drops a moved handoff, a missing `handoff-body/<topic>`, a topic `ledger.py
  landed` finds on main, one with a `fix/<topic>[-pr]` branch and a (topic, sha)
  already opened, orders the rest and launches `open_pr.sh` detached, at most
  `open-cap.txt` at once (default 2). Topic to group: `open-titles.json`, then
  `triage-s<N>-batch<M>` to `R10-TRIAGE-S<N>` (else `R10-TRIAGE-B<M>`), then the uppercased topic, the
  topic less one `-p<N>`, the topic less one `-<N>`, each checked against the
  roster; the exact match wins, and a stripped one opens only when the first
  three lines of the handoff body name the group as a whole name, else
  `NEEDS-TITLE` and nothing opens. Order: `open-priority.txt` for what it lists;
  a hotfix topic, then an outside (`roster_lib.is_outside`) or critical-path
  one, one class, is never behind a topic of a later class (owner rulings
  tvofi 2026-11-07, triage P420, and 2026-11-08); an omitted topic slots by
  default class (hotfix `R10-HOTFIX-*`, outside or critical,
  `triage-*`/`roster-*`, the rest). State under `$HPO_STATE_DIR/open-driver/`: a (topic, sha) is seen only
  on rc=0, a failed one retries after 5 min doubling to 2 h and prints `OWED
  <utc> open-refused <topic> <sha8> rc=<n> <reason>` each pass. Prints `START`,
  `RESULT`, `SKIP`, `NEEDS-TITLE`, `STARVED <topic> <sha8> <h>h` (unstarted
  over 2 h). When: each tick, after the board is written. Not here yet (the
  next part of R10-OPENER-REUSE): the tick printing the OWED lines, and the
  handoff-update arm, which stays with `cloud_relay.sh`. Mutants:
  `dev/audit/harnesses/r10_open_driver_mutants.py`.
