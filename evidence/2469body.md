R10-UPDATE-PR-LOCK. `update_pr.sh` keeps one worktree per branch at a fixed path, `$HPO_STATE_DIR/pr/upd-<branch>`, and every run starts by force-removing it. When two runs overlapped on one branch, the second removed the worktree from under the first run's prepr. The second run was `cloud_relay.sh`'s handoff arm, which runs `update_pr.sh` for any PR whose handoff is ahead, racing the orchestrator's manual update. This hit #2452 and #2464 on 2026-10-19/20, and #2471.

The relay's own update also failed every time: the body it wrote sat directly in `$TMPDIR`, which prepr's body-path check refuses.

This PR is the split the three-round rule calls for. Holding the lock across a SIGKILLed run's orphaned push moves to R10-UPDATE-PR-SIGNALS (see Forward-carry).

## Fix

`tools/audit/seat/update_pr.sh`, each mechanism with the `# mut:` line that pins it:
- One holder process takes `flock` on `upd-<branch>.lock` before any fetch or worktree change. A run that cannot take it exits 75 (`update_pr: BUSY: …`), having changed nothing (`mut:lock`).
- The shell holds no fd on the lock, so nothing the run starts can hold it.
- On a normal end, the EXIT trap ends the holder before the run returns (`mut:unlock`).
- TERM, INT and HUP are trapped (`mut:stop`). bash runs the trap once the foreground push has finished, so a stopped run, such as one stopped by `kill <pid>` (`daemonize.py`'s stop), frees the lock after its push.
- The holder lives until its parent is gone (`mut:watch`), so a SIGKILLed run leaves no stale lock. The holder exits within 2 s.

`tools/audit/seat/cloud_relay.sh`:
- The handoff arm writes BODY.md into a per-run `mktemp -d` directory, not directly in a shared root, and removes it after the update.
- It treats rc 75 as "retry on the next pass": it is neither recorded in `cloud-handoff-failed` nor logged OWED.

`tools/audit/seat/INSTRUMENTS.md` documents both.

## Head

`931e9a0f567584657ecaed2b61e61c857bdd2135` is the code head. origin/main is `a65438c463203966474d2edf1c02462a31ac5eee`, and `git merge-tree --write-tree origin/main 931e9a0f567584657ecaed2b61e61c857bdd2135` is clean.

## Mutation proof

Every mechanism above, reverted, fails the arm named. `bash tools/audit/seat/pr_args.sh --self-test` deletes each `# mut:` line from a copy of `update_pr.sh`, and prints `ok` for a mutant that fails its arm:

| revert | arm it fails |
|---|---|
| `mut:lock` | `update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place` |
| `mut:unlock` | `update_pr: the lock holder has exited by the time a run returns` |
| `mut:stop` | `update_pr: a TERMed run (daemonize.py's stop) keeps the lock until its push has ended; then the next run takes it` |
| `mut:watch` (the holder exits at once) | the same TERM arm: the lock is not held during the push |
| the holder never exits (`while True: time.sleep(2)`, applied by hand) | `update_pr: a SIGKILLed run leaves no stale lock; a later run takes it` |
| the shell-fd lock of `49577add8c4df47aa24124727fd2f6e250f3434f` | `update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push` |

`cloud_relay.sh` mutants, each run on a copy with `bash tools/audit/seat/cloud_relay.sh --self-test`:

| revert | failing checks |
|---|---|
| body line back to `mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX"` | `the body update_pr gets passes prepr's body-path check (not directly in a shared root)` and `and that body's directory is removed after the update` |
| final `rm -rf "$bd"` deleted | `and that body's directory is removed after the update` |
| `if [ "$urc" = 75 ]` line deleted | `a busy update is tried again on the next pass`, `and is not recorded failed` and `nor logged OWED` |

With origin/main's `update_pr.sh`, the head's `pr_args.sh` prints `56 checks, 3 failed`: the BUSY arm, the TERM arm, and the `mut:unlock` arm, which has no line to delete there.

No arm depends on timing or reaping:
- Each wait is on a condition with a bound: the push stub's start, up to 30 s; run 1's exit; and for SIGKILL, retries up to 20 s until a run is not BUSY.
- The TERM arm's run 2 starts 1 s after the signal, while the stub's push has 5 s left.
- The kernel frees a `flock` when the holder exits, not when it is reaped, so a slow-reaping PID 1 does not delay it.

## Null control

- `null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push`.
- In both stop arms, the run after run 1 takes the lock and reaches its push.
- The existing `update_pr with code sha … passes every check, and its failed push names its log` null controls and `cloud_relay.sh`'s existing arms pass.

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test`: `pr_args self-test: 56 checks, 0 failed` on 8 of 8 runs at the head, 5 sequential and 3 at once under load, on macOS (origin/main: 46). No container run: none is available on this seat.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 74 checks, 0 failed` (origin/main: 69).

## Red checks

`pr-contract` failed on round 0's heads: `02369b10` (check-runs 118384376991 and 118384517187) and `d2d361a449f0356f877e49a7ff59521f33739c37` (118384716655 and 118384845043). `carry_audit.py check` read `## Forward-carry` as an item, because text followed `none`. The cheaper detector is `python3 -I tools/audit/carry_audit.py check --body <body>`, run by hand before the push, which costs one python spawn.

## Forward-carry

- A SIGKILLed run's holder frees the lock within 2 s while the push that run started may still be running in the worktree. Holding it until that push ends needs a drain of the run's process group, and in a container whose PID 1 reaps orphans late that drain's arm failed 7 of 7 runs (#2469 round 4). Carry: R10-UPDATE-PR-SIGNALS
- A signal to the run's whole process group, such as `kill -TERM -- -<pgid>` or SIGHUP when its terminal closes, also reaches the holder. The holder has no handler, so it exits before the push it covers. This is reasoned from the code, not measured here. (SIGINT does not reach it: bash starts the holder in the background, with SIGINT ignored.) Carry: R10-UPDATE-PR-SIGNALS
- Under `set -e`, any command inside `update_pr.sh` that exits 75 reads to the relay as BUSY and is retried rather than recorded. Today only the lock path exits 75. Carry: R10-UPDATE-PR-SIGNALS

## Friction

none
