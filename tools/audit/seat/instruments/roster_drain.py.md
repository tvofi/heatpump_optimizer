# `roster_drain.py`

- `roster_drain.py` — the manual roster-queue drain path: runs the pending
  lines of a queue file through `roster_queue.py run`, marks each line
  `#done` or `#refused` by exact-line match, and prints one line per problem:
  `ROSTER-REFUSED`, `ROSTER-SKIPPED`, `ROSTER-CASCADE`, `ROSTER-UNRUN`.
  Owner ruling (tvofi 2026-10-31): mechanical seat work goes into the sweep
  script. When: a session with no standing roster seat; the beat's
  `roster-drain` row (`beat_jobs.py`) is the unattended path and the two do
  not run together on one queue. Refusal: it never releases a `#held` line,
  and a line holding ` #` is skipped with a notice rather than cut. Run from
  a checkout of the repository. `--self-test` drives each output kind beside
  a clean drain.
