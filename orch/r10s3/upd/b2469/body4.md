R10-UPDATE-PR-LOCK. `update_pr.sh` keeps one worktree per branch at the fixed path `$HPO_STATE_DIR/pr/upd-<branch>`, and every run starts with `git worktree remove --force` on it. When two runs overlapped on one branch, the second removed the worktree under the first run's prepr. The overlap was the orchestrator's manual update against `cloud_relay.sh`'s handoff arm, which runs `update_pr.sh` for any PR whose handoff is ahead. This hit #2464 and #2452 on 2026-10-19/20 and #2471 at 01:32Z. The relay's own update also failed every time: the body it wrote sat directly in `$TMPDIR`, which prepr's body-path check refuses.

## Fix

`tools/audit/seat/update_pr.sh`, each mechanism with the `# mut:` line that pins it:
- **The lock.** One holder process takes `flock` on `upd-<branch>.lock` before any fetch or worktree change. A run that cannot take it exits 75, `update_pr: BUSY: …`, having changed nothing (`mut:lock`).
- **The shell holds no fd on the lock**, so nothing the run starts can hold it.
- **The run leads its own process group**: a run that does not re-execs under `setpgid(0, 0)` (`mut:pgrp`). The holder moves to a group of its own (`mut:holdgrp`).
- **After a SIGKILL**, the holder keeps the lock while any process of the run's group is left, i.e. until the push it started has ended (`mut:drain`).
- **On a normal end**, the EXIT trap ends the holder before the run returns (`mut:unlock`).
- **TERM, INT and HUP are trapped** (`mut:stop`). bash runs the trap once the foreground push has finished, so a stopped run frees the lock only after its push. `kill <pid>`, `daemonize.py`'s stop, therefore takes effect when the push ends.

`tools/audit/seat/cloud_relay.sh`:
- The handoff arm writes BODY.md into a per-run `mktemp -d` directory, not directly in a shared root, and removes it after the update.
- It treats rc 75 as "retry on the next pass": not recorded in `cloud-handoff-failed`, not logged OWED.

`tools/audit/seat/INSTRUMENTS.md` documents both.

## Head

`98fe31c26da80c46441a32bde66c2c3ef9ac5bc1` merges the authored code head `c9dd299c9d14493d0055cc2e4de25b42f6b2d011` and then merges origin/main `bb5b21a88` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`c9dd299c9d14493d0055cc2e4de25b42f6b2d011` is the code head. origin/main is `bb5b21a88f82e3bcfd1f0a0fdd2ba351aa665703`, and `git merge-tree --write-tree origin/main c9dd299c9d14493d0055cc2e4de25b42f6b2d011` is clean.

## Mutation proof

Every mechanism above, reverted, fails the arm named beside it.

`bash tools/audit/seat/pr_args.sh --self-test` deletes each `# mut:` line from a copy of `update_pr.sh`, and the harness prints `ok` for a mutant that fails its arm:

| mutant | arm it fails |
|---|---|
| `mut:lock` | `update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place` |
| `mut:unlock` | `update_pr: the lock holder has exited by the time a run returns` |
| `mut:stop` | `update_pr: a TERMed run (daemonize.py's stop) keeps the lock until its push has ended; then the next run takes it` |
| `mut:drain` | `update_pr: a SIGKILLed run keeps the lock until its push has ended; then the next run takes it` |
| `mut:pgrp` | the same SIGKILL arm |
| `mut:holdgrp` | the same SIGKILL arm, at its third run |

The shell holding no lock fd is pinned by `update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push`. In that arm, a post-checkout hook leaves a detached child behind. Its revert is the shell-fd lock of `49577add8c4df47aa24124727fd2f6e250f3434f`, and with that `update_pr.sh` the arm prints `FAIL update_pr: a child the run left detached does not hold the lock…`.

`cloud_relay.sh` mutants, each run on a copy with `bash tools/audit/seat/cloud_relay.sh --self-test`:

| mutant | failing checks |
|---|---|
| body line back to `mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX"` | `the body update_pr gets passes prepr's body-path check (not directly in a shared root)` and `and that body's directory is removed after the update` |
| final `rm -rf "$bd"` deleted | `and that body's directory is removed after the update` |
| `if [ "$urc" = 75 ]` line deleted | `a busy update is tried again on the next pass`, `and is not recorded failed`, `nor logged OWED` |

With origin/main's `update_pr.sh`, the head's `pr_args.sh` fails the BUSY, TERM and SIGKILL arms (`58 checks, 5 failed`, two of which are mutant arms with no line to delete).

## Null control

- `null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push`.
- In both stop arms, run 3 starts after the push has ended, takes the lock and reaches its push.
- The existing `update_pr with code sha … passes every check, and its failed push names its log` null controls and `cloud_relay.sh`'s existing arms pass.

## Figures

- `bash tools/audit/seat/update_pr.sh --self-test`: `pr_args self-test: 58 checks, 0 failed`, the same on 4 consecutive runs; origin/main has 46.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 74 checks, 0 failed`; origin/main has 69.

## Red checks

`pr-contract` failed on round 0's heads `02369b10` (check-runs 118384376991 and 118384517187) and `d2d361a449f0356f877e49a7ff59521f33739c37` (118384716655 and 118384845043). The cause was `carry_audit.py check` reading `## Forward-carry` as an item, because text followed `none`. That section now reads `none` alone. The cheaper detector is `python3 -I tools/audit/carry_audit.py check --body <body>`, run by hand before the push at the cost of one python spawn; this body passed it.

## Forward-carry

none

## Friction

none
