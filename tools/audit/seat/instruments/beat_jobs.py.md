# `beat_jobs.py`

- `beat_jobs.py` — the rows of `beatd.jobs.json` (R10-FLY-STANDING-CONTRACTS
  P1): `beat_jobs.py ROW --state S` runs one row, and `beatd.py run --state S`
  runs them all from the table beside it. Rows: `tick-digest` (the board's
  actionable family; a `NOT REVIEWABLE` or `RED unanswered` line only once a
  second board carries it), `owed-check` (`owed_unactioned.py`, once per
  sweep), `roster-drain` (`roster_queue.py run` per pending line of
  `S/roster-drain.queue`, each exact line marked done, a refusal never
  retried, `hold <tree-path> <op>` released once main carries the path and
  `HOLD-STALE` after 24 h), `plan-beat` (`replan.py` then `state_docs.py
  --push --mirror --plan`), `pulse` (into `S/beatd/pulse.txt`), `cancel-sweep`,
  `disk` (`worktree_gc.sh` under the floor), `opener` (one `open_driver.py
  --board` pass, its refusals and `STUCK` forwarded) `head-watch`
  (`HEAD-MOVED` events) and `audit-dispatch` (one `DISPATCH: planted-defect-audit
  arm=<arm> cut=<span>` line per `would-trip` guardrail arm and cut, never twice). Each writes only actionable lines to
  `S/digest/jobs/<row>`; `fold` concatenates them into `S/digest/digest.txt`,
  diffs `new.txt` and `gone.txt`, and touches `new.stamp` only on a new line,
  so the orchestrator's one wake reads `new.stamp` and `events.txt`. A null
  pass changes no byte. Session paths come from the sweep overlay
  (`S/sweep-overlay.json`, the JSON `sweep_render.py` reads); a row missing
  its key writes `UNREADABLE`, never nothing. No row moves the checkout or
  touches a seat's alive file. When: under `beatd.py run`; by hand, one row,
  to see what it would forward. `--self-test` runs every row's planted case
  and null on a throwaway state with the instruments faked, the fixture board
  under `fixtures/beat_jobs/`, and one mutant per row predicate
  (`beat_jobs_selftest.py`).
