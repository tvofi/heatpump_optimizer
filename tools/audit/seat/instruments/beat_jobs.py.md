# `beat_jobs.py`

- `beat_jobs.py` — the rows of `beatd.jobs.json` (R10-FLY-STANDING-CONTRACTS
  P1): `beat_jobs.py ROW --state S` runs one row, and `beatd.py run --state S`
  runs them all from the table beside it. Rows: `tick-digest` (the board's
  actionable family; a `NOT REVIEWABLE` or `RED unanswered` line only once a
  second board carries it), `owed-check` (`owed_unactioned.py`, once per
  sweep), `roster-drain` (`roster_queue.py run` per pending line of
  `S/roster-drain.queue`, done or refused read from the exact line
  `roster_queue.py --mark` rewrites, a refusal never retried, an op neither
  reported nor marked `UNRUN` and pending, a refusal by a worktree on no origin
  ref pending under one `CASCADE` line, `hold <tree-path> <op>` released once
  main carries the path and `HOLD-STALE` after 24 h), `plan-beat` (`replan.py`
  then `state_docs.py --push --mirror --plan`, and `PLAN MOVED` when the
  mirrored `PLAN.html` changed), `gantt` (`sweep_gantt.py`'s `GANTT-SLIP` and
  `GANTT-BASELINE` lines), `verdict-audit` (`verdict_audit.py`'s `UNHELD`
  lines), `pulse` (into `S/beatd/pulse.txt`), `cancel-sweep`,
  `disk` (`worktree_gc.sh` under the floor), `opener` (one `open_driver.py
  --board` pass, its refusals and `STUCK` forwarded) `head-watch`
  (`HEAD-MOVED` events) and `audit-dispatch` (one `DISPATCH: planted-defect-audit
  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run). Each writes only actionable lines to
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
