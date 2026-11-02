# `tick_loop.sh`

- `tick_loop.sh` — the tick's driver loop (tvofi approved, 2026-10-18): each
  pass runs `cloud_relay.sh pass --confirm` (a relayed verdict posts with no
  hand step) when the tree carries it (#2419; skipped
  and said so before), then `orchestrator_tick.py` with the given args,
  writing the board whole to `--out` (default `$HPO_STATE_DIR/tick.txt`) and
  one `TICK-PASS <utc> relay=<ok|rc=N|running|absent|stale> tick=<rc>
  code=<sha7> behind=<n>` line to stdout. The relay runs detached under the flock `<out>.relay.lock`, waited
  for at most `HPO_TICK_RELAY_WAIT` s (default 30): one still in flight is
  left running, never killed, reported `relay=running`, and no second starts
  while it holds the lock, so a long `update_pr.sh` push never holds the
  board; the next pass reaps it, printing its output and a `TICK-RELAY` line.
  When: run detached (`daemonize.py`) in place of a seat looping the tick;
  `--once` makes one pass, `--interval` defaults to 300 s. Refusal: a
  non-numeric `--interval` or an unknown option; a failing relay pass or tick
  is reported and the loop goes on. `--self-test` drives it over stubs.
  Each pass then calls `heartbeat.sh --once` (the andon, below), bounded at
  60 s; `HPO_TICK_HEARTBEAT` replaces it.
  Before the relay, the freshness check (P14): `git fetch -q origin main`
  and `behind`, the commits in `HEAD..origin/main` touching `tools/audit/seat`,
  `tools/pr` or `tools/audit/carry_audit.py`. Past `HPO_TICK_STALE_BOUND`
  (default 25) or on a commit touching `tick_loop.sh` or `cloud_relay.sh`, it
  restarts between passes, at most once a pass: lock free, tree clean and
  detached, `bash -n` passing on origin/main's copy, then a detached checkout
  of origin/main and an exec with the same args (`TICK-RESTART`). Otherwise
  a `TICK-STALE` line names why, the relay and sweep arms are skipped
  (`relay=stale`) and the board is still written. Never a fast-forward in
  place. `HPO_TICK_CODE_DIR` replaces the checkout.
