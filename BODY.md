A stopped pusher must not leave its work running.

A shell does not forward TERM/INT to a foreground child. `open_pr.sh`, `update_pr.sh` and
`app_push.sh` each ran their push (or prepr) as a foreground child, so a stopped pusher exited and
the subtree reparented to launchd and kept burning CPU: six survivors were swept up on 2026-10-20,
aged 26 to 62 minutes, on a box already at load 77 on eight cores, and each kill needed a second
pass two levels further down. The slot pool could not see them, because they hold no slot once
their parent is gone.

`tools/audit/seat/pr_args.sh` already owns the shared stop for `open_pr.sh` and `update_pr.sh`
(`pr_trap`'s ERR report), so the reap belongs there: `pr_descendants` walks children by parent pid,
`pr_reap` TERMs each by pid and KILLs whatever outlives a two-second grace, and `pr_signal_traps`
(installed by `pr_trap`) ends the tree on TERM/INT/HUP before the shell exits. Bash defers a trap
while a foreground child runs, so the three pushers now run that child asynchronously and `wait`
on it (`pr_wait`), which a trapped signal interrupts; `app_push.sh` sources the same module and
installs the same traps, and its own prepr call is asynchronous for the same reason. EXIT reaps
too -- `update_pr.sh`'s lock trap and `app_push.sh`'s cleanup call `pr_reap` -- which is the
backstop when a signal is not trapped at all: measured on this box's bash 3.2, an untrapped fatal
signal still runs the EXIT trap. Never a pattern kill: every signal goes to a numeric pid above 1
that the walk returned, never to a group and never to a command line.

SIGKILL stays out of scope: no trap runs, so a SIGKILLed pusher's tree survives. The self-test's
KILL arm therefore asserts only that its lock does not go stale.

## Head

`6ff10e62b3f7b8d38fd3ecab5e23aa71a9f3553d` -- everything below was measured at that head (merge base `df6ca4bc6858f2796f694035e6f53e46e237e33b`, the tip of `origin/main` at 2026-10-21T08:40Z).
`prepr` ran with `PREPR_SKIP_CLOSURES=1` (tvofi, 2026-10-21), so its closure derivation was skipped; the scoped gate was derived separately and is in `## Figures`.

## Mutation proof

Two, each made on a copy of the head's `tools/audit/seat`, `tools/pr` and `tests/throwaway_git.sh` (the self-test reads its scripts from its own directory), so the worktree stays byte-identical to the committed head.

- The reap's kill line (`pr_kill`'s `kill -"$1" "$2"`, marked `# mut:stop`) replaced by `:`: `bash tools/audit/seat/pr_args.sh --self-test` printed `62 checks, 2 failed`, the failures being `open_pr: TERM reaps the whole descendant tree, and the pusher is gone` and `update_pr: TERM reaps the whole descendant tree, and the pusher is gone`; the unmutated copy prints `62 checks, 0 failed`.
- The by-pid rule: `pr_reap` widened by a pattern, `PR_REAP_PIDS[${#PR_REAP_PIDS[@]}]=$(pgrep -f "$REAP_DIR/unrelated-sleep" 2>/dev/null || :)` placed after `pr_descendants $$`: the self-test printed `62 checks, 2 failed`, the failures being `open_pr: the null control -- an unrelated sleeper survives` and `null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`. The survivor arms stayed green and the run printed its own tally and exit status -- a reddening, not a crash.

Failing test first: the head's self-test arms run against the merge base's `open_pr.sh`, `update_pr.sh` and `app_push.sh` (the head's `pr_args.sh` carries the arms) printed `62 checks, 3 failed` -- `open_pr: TERM reaps the whole descendant tree, and the pusher is gone`, `update_pr: TERM reaps the whole descendant tree, and the pusher is gone` and `update_pr: after the stop the lock is free, so the next run takes it`; at the head they print `0 failed`.

## Null control

The unmodified scripts leave the stub's whole tree alive after TERM: the three failing arms above are that measurement (the stub records its pids, the arm counts the survivors and asserts 0, and the base scripts leave them alive with the pusher's trap never run). At the head the same arms pass. A run that succeeds (the stub exits 0) leaves nothing behind either, and a bystander sleeper started outside any pusher's tree survives both the TERM and the successful run, so the reap kills only what it started -- those are the two null-control arms, which pass at the base scripts as well.

## Figures

All commands run at `6ff10e62b` in the worktree; the script's own last line and exit code.
- `MODE: SCOPED -- 0 script(s) run, 33 scoped out` -- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` (four changed files under `tools/`; no recorded closure names any of them)
- `pr_args self-test: 62 checks, 0 failed` at this head, `3 failed` for the same arms against the merge base's pushers (Mutation proof) -- `bash tools/audit/seat/pr_args.sh --self-test`
- `app_push self-test: 135 checks, 0 failed` -- `bash tools/pr/app_push.sh --self-test`
- `STRUCTURE RATCHET PASSED` -- `python3 tests/structure.py`
- `ALL 124 closure shrink pins PASSED` -- `python3 tests/closure.py selftest`
- `claims hygiene: df6ca4bc6858f2796f694035e6f53e46e237e33b ok` -- `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`
- `tmp_paths: 0 refused, 0 stale allow entries at HEAD` -- `python3 -I tools/audit/seat/tmp_paths.py --check`
- Survivor rule, not a number: an arm counts the pids the stub recorded still alive and asserts exactly 0 after TERM; the base scripts leave them alive -- `bash tools/audit/seat/pr_args.sh --self-test`

## Red checks

- `pr-contract`, at the previous head: three `UNROUTED` items under `## Forward-carry` and `## Friction` (a `none -- ...` line is an item, and the friction lines carried no `Carry:` marker), while this section said none. The cheaper detector is `python3 -I tools/audit/carry_audit.py check --body <body>`, which this body now passes; `tools/pr/prepr.sh` does not call it, so only `pr-contract` ran it. Standing cost of running it by hand before a push: one local command that reads the roster ref. The recurring class is open as #2428.
- `nightly-status`: grades `main`, not this branch. The nightly `slow` lane's `loop_cpu_ratio` is over budget, and the separate `r10-replay-cap` work fixes it. This diff touches only `tools/audit/seat/` and `tools/pr/` pushers, which that lane does not read.

## Forward-carry

none

## Friction

- daemonize-instrument: cost: `daemonize.py` treats any `--self-test` in its argv as its own self-test, so `--log L -- bash tool --self-test` ran the launcher's self-test and silently skipped the command; put the child in `bash -c` around it. Carry: R10-ORCH-MACHINERY
- entity-classification: unenforced: the shared `.git/info/exclude` carries a `seat/` pattern, so `git add tools/audit/seat/<new file>` refuses as ignored while tracked files still stage -- a new instrument there would silently not be added. Carry: dismissed: a per-clone exclude entry on this box, not tracked repository state, so no tree change can fix it
