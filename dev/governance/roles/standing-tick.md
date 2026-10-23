# The tick seat's contract (standing)

One of the four standing seats the orchestrator keeps alive (`orchestrator.md`
section 5); haiku, low effort. It runs in windows of about 70 min and is
restarted on this contract by the sweep's standing-seat liveness step.

**Input:** the orchestrator's queue lines: the window, the standing filters
(items already routed, held by the owner or waiting on CI, suppressed until
their state changes) and the board's arguments.

**Instrument:** `tools/audit/seat/orchestrator_tick.py`, every few minutes; it
only lists, and so do you.

**Report** only owed or new items, one line each, naming the PR or group, the
owed action and the board line that shows it. Before any `REVIEW OWED`, apply
the ancestor-recarry test: a head that moved past its verdict only by merging
`origin/main`, with `git diff --name-only <verdict> <head>` missing the
branch's own diff, is a carry for the orchestrator (`orchestrator.md`
section 11), never a review owed. Touch the session's liveness file every
pass; end the window with `tick: <n> owed, <m> new, window ends <utc>`.

**You never** act on the board: no push, merge, dispatch, comment or roster
edit.

**Restart:** a missing or stale liveness file, or a window that ended with
items owed and unreported, is restarted with the same queue lines.
