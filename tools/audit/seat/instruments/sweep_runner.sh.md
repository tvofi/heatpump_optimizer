# `sweep_runner.sh`

- `sweep_runner.sh` — the sweep's mechanical steps as one loop, configured by
  `SWEEP_*` environment (`SWEEP_STATE_DIR`, `SWEEP_CHECKOUT`, `SWEEP_REPO`
  required; `SWEEP_ONCE`, `SWEEP_SLEEP` and the roster, ledger, train and
  disk-floor variables optional). Owner ruling (tvofi 2026-10-31): mechanical
  seat work goes into the sweep script. It runs the roster drain, `pulse.py`,
  the superseded-run cancel, the disk floor, and every second pass
  `sweep_gantt.py` and `verdict_audit.py`, and writes only actionable lines
  to `$SWEEP_STATE_DIR/sweep-runner/new.txt` (+ `new.stamp`) for the
  orchestrator's one wake. When: a session runs its recurring sweep. Run it
  from a checkout fetched fresh by the session, never the one `tick_loop.sh`
  or `cloud_relay.sh` run from. Refusal: an unset required variable exits
  non-zero. `--self-test` runs `sweep_runner_selftest.py`.
