# `pulse.py`

- `pulse.py` — says whether the programme is still being driven, from origin
  alone: per consumer, an input an off-host producer already delivered that
  the consumer's footprint has not answered within a bound — a handoff with no
  pull request and nothing opened since it arrived (`bus.sh orphans`, invoked),
  a verdict still at its open pull request's head, a main move the round's
  state ref has not followed. When: from where the orchestrator's host is not
  (a scheduled cloud probe seat), and first at any takeover, before the hand
  survey (R10-RCA-ORCH-CONTINUITY). Refusal: an input it could not read is
  `UNREADABLE`, exit 2, never ok; a stamp ahead of the clock is never aged.
  `--dump` keeps the snapshot a `STOPPED` line came from; `--snapshot`
  re-judges it. A `STOPPED` line names the standing seat its input waits on,
  and `--seat-queue SEAT=FILE[:MIN]` judges a standing seat on its session
  queue file (`<epoch> <text>` lines): STOPPED past the seat's cadence, ok
  when empty, `UNREADABLE` when missing.
  `--seat-alive SEAT=FILE[:MIN]` judges a standing seat on its alive file and
  who beat it: the per-process entries live in `FILE.d/<id>` (the launch
  nonce), and the per-role `FILE` alone never makes the role live. Missing
  FILE is `UNREADABLE`; FILE older than MIN (or the seat's cadence) is
  `STOPPED`; two fresh ids print `DUPLICATE seat <role>: <id> <id>`; a fresh
  FILE with no fresh id prints `FOREIGN <role>: unattributed beat`; and with
  `--launch-ledger FILE` (`<ts> <nonce> <role> ...` launch lines, `<ts> <nonce>
  stop` stop lines) a fresh id that is not the role's newest unstopped launch
  prints `FOREIGN <role>: <id> (newest launch <nonce>)`. Each is `STOPPED`,
  never ok (R10-ORCH-BEATD: a 41 h orphan loop kept `merge.alive` fresh with no
  merge seat). `sweep_template.md` step (1b) runs it once per `seat_alives`
  entry of the overlay.
