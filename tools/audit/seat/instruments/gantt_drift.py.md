# `gantt_drift.py`

- `gantt_drift.py` — compares the plan JSON `tools/plan/replan.py` writes with
  the real state (open PR heads, handoff refs, the dispatch ledger's FIRED
  lines) and a baseline, and prints one `GANTT-SLIP` line per unacknowledged
  slip: IDLE (a group the plan has started that nothing names; `CP` on the
  critical path, listed first), LATE (a planned finish moved past the
  baseline's by more than `--late-hours`), CLOSURE (the plan closure moved by
  more than `--closure-hours`). Acks are act, defer (silence a key until a
  time) or accept (silence it and re-baseline it into `--out`). When: after
  each replan and plan page render. Refusal: none; a slip is surfaced for the
  owner to act on, defer or accept. `--self-test` runs each slip kind and ack
  kind with its null, and a mutant per arm.
