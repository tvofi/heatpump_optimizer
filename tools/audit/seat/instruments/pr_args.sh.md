# `pr_args.sh`

- `pr_args.sh` — sourced by `open_pr.sh` and `update_pr.sh`: their argument
  checks, the ERR trap that reports every other stop, so neither stops
  silently, and `pr_branch_lock`, the per-branch lock both take. The lock
  outlives the run's push whatever stops the run: its holder ignores TERM,
  INT and HUP, and lets go only once the push's own lock (`pr_push_hold`, an
  fd every process of the push inherits) is free, so a SIGKILLed run's lock
  is held until its push has ended. The lock file reads `<run pid> <holder
  pid> <start epoch>`, and a fourth field `drain` meanwhile. No `ps` and no process-group walk: on a host without `pgrep` a
  stopped run says it could not reap, and its lock is held until its push
  ends. Inside `pr_push_hold` git's auto-maintenance runs in the foreground
  (`gc.autoDetach`, `maintenance.autoDetach` off), so a `git gc --auto` a
  push's fetch starts is part of that push rather than a PID-1 orphan holding
  its lock. With `detach` the holder leaves the run's worktree detached once
  the push has ended, a SIGKILLed run's too. Only the lock exits 75; a step
  that does is reported as a stop and exits 1. `pr_bounded` runs a self-test
  (its own, `update_pr.sh`'s, `cloud_relay.sh`'s) as a session of its own under
  `PR_SELFTEST_SECONDS` (default 1200), and ends that whole session on exit,
  at the bound (exit 124, a `BOUND:` line) or once its supervisor is gone;
  `pr_own_group` starts a command as a process group's leader. When: never by hand; `--self-test` drives both scripts end to end
  in a scratch repository, offline, each refusal arm beside a mutant that
  deletes its predicate line (`# mut:<name>`) and must fail the arm, plus
  null controls that pass every check. Refusal: its self-test's tally.
