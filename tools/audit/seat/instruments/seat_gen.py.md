# `seat_gen.py`

- `seat_gen.py` — the generation token and the session lock. `bump <seat>`
  writes `$HPO_STATE_DIR/<seat>.gen` (`<n> <epoch>`, n monotonic, under a
  flock) and prints n for the replacement seat's prompt. `check <seat> <gen>`
  and `check-env` (`$HPO_SEAT_GEN`, `<seat>=<gen>`; unset passes) exit 1 with
  `SUPERSEDED` when a higher generation is held. The wired writers
  (`roster_queue.py run_queue`, `bus.sh dispatch`, `merge_train.py train_add`)
  call it before their first write, so a superseded seat's lingering job writes
  nothing. `lock [--pid N]` records the session binary's pid (the first
  ancestor running `claude`, never `$PPID`) in `$HPO_STATE_DIR/session.lock`
  and exits 1 with `REFUSED`, naming both pids, when another live session holds
  it; a gone pid, or one naming another command, is stale and taken over. The
  resume steps (`handover_prompt.py`) and sweep step (0) run it before the
  first dispatch. `--self-test` prints `seat_gen self-test: N checks, 0 failed`
  and runs the named mutants.
