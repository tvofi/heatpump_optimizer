A TERM, INT, HUP or SIGKILL of a running `update_pr.sh`, sent to the run alone or to its whole process group, no longer frees the branch lock while the run's push is still running. Every self-test arm waits on a condition, and the lock is read by trying it, never through a holder pid.

**The defect, at the base `da12aa37d`.** `pr_branch_lock`'s holder (a `python3` child of the run) exited when its parent died (`os.getppid()` polled every 2 s) and had no handler for TERM or HUP. That left two gaps:
- a SIGKILLed run's lock was freed while the push it had started kept running in the worktree;
- a signal to the whole process group ended the holder beside the push it was meant to guard.

#2469's round 4 tried to close the first gap by draining the run's process group. In this container, whose PID 1 reaps orphans late, that drain counted zombies and failed 7 of 7.

**The fix** (`tools/audit/seat/pr_args.sh`):
- The holder ignores TERM, INT and HUP. It lets go on USR1 from `PR_AFTER_REAP`, which `pr_exit_trap` runs after its reap, or when its parent is gone. Before it exits it blocks on the push's own lock, `<lock>.push`, and its lock line's third field reads `drain` meanwhile.
- `pr_push_hold` takes that push lock. Each push runs as `{ pr_push_hold; <push> & } 9>>"$PR_PUSH_LOCK"`. The shell opens fd 9 before the fork, so every process of the push inherits it. The kernel frees a flock when the last fd on it closes, and a process closes its fds at exit, before it is reaped. So a zombie never holds the lock, and neither `ps` nor a group walk is needed.
- `pr_stopped` maps a 75 seen under errexit to exit 1, so only `pr_lock_busy` can say BUSY.
- On a stop with no `pgrep` on PATH, `pr_reap` prints that it could not reap.
- A BUSY caused by a draining run names that run's push.

`update_pr.sh` runs its push under `pr_push_hold`. It also leaves its worktree detached in `PR_AFTER_REAP`, after `pr_push_ended` and before the lock is freed. That is never under a running push and never under the next run. `open_pr.sh` runs both of its pushes under `pr_push_hold`. **`open_pr.sh` is outside this group's `files`**: it is the other caller of `pr_branch_lock`, so the class rule below reaches it.

Alternatives considered:
- (a) Drain the run's process group by `ps`. This is #2469 round 4's approach: it counts zombies and needs `ps`.
- (b) Keep the holder alive for a fixed window. That is a window, not a condition.
- (c) Give the run's shell the push fd. Every child of the shell would inherit it, which is #2469 round 1's detached `git gc --auto` again.

The fd lock is the one option that reads the kernel's own liveness of the push.

Part of #2502.

## Head

`af05e52e49f1eb2f601ddc861ad474520a9dcf86`, cut from origin/main `da12aa37dee15b9e9567bd6c848493436f2592dd`, the dispatch head. Measured 2026-10-25 between about 17:10Z and 17:58Z.
- origin/main has since moved to `dfcd8d9be1dab28cfe52f684764befd1e19291de`.
- `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the branch was not merged (`fixer.md` step 6).

## Mutation proof

Each `# mut:<name>` line is a predicate. The self-test deletes it from a copy and requires its arm to fail; all of these arms pass in the `109 checks, 0 failed` run at the head:

| mutant | what goes red |
|---|---|
| `mut:drain` | `mutant mut:drain (its line deleted): the holder lets go once the run is gone, while the push runs` |
| `mut:pushhold` | `mutant mut:pushhold (its line deleted): the push holds no lock, so the holder lets go while it runs` |
| `mut:holdsig` | `mutant mut:holdsig (its line deleted): the group's TERM ends the holder, which never drains` |
| `mut:busy75` | `mutant mut:busy75 (its line deleted): that step's 75 reaches the caller, which would read it as BUSY` |
| `mut:nopgrep` | `mutant mut:nopgrep (its line deleted): the run stops without saying its tree was not reaped` |
| `mut:detach` | `mutant mut:detach (its line deleted): the worktree still holds fix/x` |
| `mut:watch` | `mutant mut:watch (the holder's wait line deleted): the holder lets go at once, so the run never holds the lock and refuses` |
| `mut:stop` | `mutant mut:stop: and the lock stays held while that push runs, so the next run is BUSY (the drain, not the reap, guards it)` |

The four central lines were also deleted from the real `pr_args.sh`, one per detached worktree at `4fd49ab07`. That commit's production code equals the head's; the head adds only the census rule. The whole self-test ran each time and the line was restored:
- `mut:drain`: `107 checks, 2 failed`: `FAIL update_pr: a SIGKILLed run's lock stays held while its push runs`, `FAIL update_pr: and a run meanwhile is BUSY, naming that push`.
- `mut:holdsig`: `107 checks, 2 failed`: `FAIL update_pr: TERM to the run's whole group: the holder outlives it and drains, ...`, `FAIL update_pr: HUP to the run's whole group: ...`.
- `mut:busy75`: `107 checks, 1 failed`: `FAIL update_pr: a step exiting 75 is reported as a stop and exits 1, never 75 (BUSY)`.
- `mut:pushhold`: `107 checks, 3 failed`: the SIGKILL hold arm, its BUSY arm, and `mutant mut:stop: and the lock stays held while that push runs ...`.

Before the external runs, `mut:pushhold`'s deletion emptied its function, which is a syntax error: the arm passed only because nothing ran. The predicate now sits on a `|| rc=$?` line, and the arm also requires the push's tree to have started (`treen = 4`).

**Failing test first.** The new self-test ran against main's production code: `pr_args.sh` above the census, with `update_pr.sh` and `open_pr.sh` at `da12aa37d`, and the head's arms below. Result: `107 checks, 9 failed`. Seven positive arms fail:
- `a step exiting 75 is reported as a stop and exits 1`
- `a SIGKILLed run's lock stays held while its push runs`
- `and a run meanwhile is BUSY, naming that push`
- `TERM to the run's whole group: ...`
- `HUP to the run's whole group: ...`
- `with no ps or pgrep a TERMed run says it cannot reap, and keeps the lock while its push runs`
- `the run leaves its worktree detached`

The SIGKILL and group-signal rows are the defect measured. The group-signal half had been "reasoned from the code, not measured" in the carry. The other 2 failures are mutant arms whose line does not exist at the base.

## Null control

- `null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push`: a holder pid that has died frees the lock.
- `null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`: on a clean run the drain returns at once.
- `update_pr: the lock holder has exited by the time a run returns`, with `mut:unlock` red.
- `open_pr: the null control -- an unrelated sleeper survives`.
- The census null control `the same runner without its branch lock needs no push lock`: the push-lock rule binds only runners that take the branch lock.
- The SIGKILL arm fails at the base (above) and passes at the head: it reads `held` after the `drain` mark, then `free` once the fixture ends the push's pids, and a later run takes the lock.

## Figures

All at `af05e52e4`, merge base `da12aa37d`, Python 3.14.

| command | result |
|---|---|
| `bash tools/audit/seat/pr_args.sh --self-test` | `pr_args self-test: 109 checks, 0 failed` (93 at the base: 16 arms added, 2 rewritten, the `ps`-based zombie check and its `afterreap` sed mutant removed); about 2m13s here against 1m25s at the base |
| the same, three runs at once on 4 CPUs (at `4fd49ab07`) | `107 checks, 0 failed`, three times |
| `bash tools/audit/seat/pr_args.sh --pushers` | rc 0, 19 `ok` lines, no `OPEN` |
| `bash tools/audit/seat/cloud_relay.sh --self-test` (at `4fd49ab07`) | `cloud_relay self-test: 268 checks, 0 failed` |
| `bash tools/audit/seat/handoff_push.sh --self-test` (at `4fd49ab07`) | `handoff_push self-test: 3 checks, 0 failed` |
| `python3 -I tools/audit/seat/ledger.py --self-test` (at `4fd49ab07`) | `ledger self-test: 56 checks, 0 failed` |
| `python3 -I tools/audit/seat/selftest_wiring.py --self-test` (at `4fd49ab07`) | `selftest_wiring self-test: 18 checks, 0 failed` |
| `PYTHONPATH=tests/hastub python3 tests/structure.py` | `STRUCTURE RATCHET PASSED`; no `*_budgets.json` in the diff |
| `python3 tools/audit/archscore/score.py --diff da12aa37d HEAD` | `Architecture score: dS +0.0000 NULL` |
| `python3 tests/closure.py select --diff da12aa37d` | `MODE: SCOPED -- 0 script(s) run, 33 scoped out`; `scope.run` empty |
| `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` | `CI PREDICT: no closures, fast, wave-script or instrument red predicted against da12aa37dee1` |

Determinism: every new wait polls a condition with a bound: the push's 4 recorded pids, the `drain` field, a `lockstate` lock attempt, or the run's own output line. Past the bound the arm fails; the bound is not a window inside which the arm passes. The SIGKILL arm reads the lock right after the `drain` mark. At that point the push's pids are alive by construction, so `held` is the only correct reading. The group arms read the mark after the lock is free. The mark is written before the drain, so its absence at that point means the holder never drained.

**Class (step 8).** The class is "a run holding the branch lock whose push could outlive the run".
- `git grep -n 'pr_branch_lock ' -- tools`, less `pr_args.sh`, returns `open_pr.sh:34` and `update_pr.sh:37`. Both are closed in this diff.
- `git grep -nE 'bash "\$_push"' -- tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh` returns `open_pr.sh:58`, `open_pr.sh:71` and `update_pr.sh:83`. Each runs under `pr_push_hold`.
- The rule is now registered in the self-tested pusher census (`pr_pushers`): a runner that takes `pr_branch_lock` and has a push line without `pr_push_hold` prints `OPEN ... a push under the branch lock holds no push lock`. The census arm and its null control are listed above.
- The other runners (`handoff_push.sh`, `remerge_main.sh`, `tools/pr/app_push.sh`) take no branch lock, so they have no lock that could free early.

The `ps` dependency: `git grep -nw ps -- tools/audit/seat/pr_args.sh tools/audit/seat/update_pr.sh tools/audit/seat/open_pr.sh` returns one comment in `pr_branch_lock` and three self-test lines that build and name the PATH without it. No production line runs `ps`, and no self-test arm calls it. `pgrep` runs only in the reap and the fixture's cleanup. The arm with neither command on PATH passes.

**This group's carries, closed in this diff:**

- #2469 round-4 SIGKILL: closed here (`pr_push_hold`, the drain).
- Group-wide TERM/HUP reaching the holder: closed (`mut:holdsig`).
- 75 under `set -e`: closed (`mut:busy75`).
- R10-ROSTER-OPS's `ps` carry: closed (the arm with no `ps`/`pgrep`).
- `update_pr.sh` leaving its worktree on the branch: closed (`mut:detach`).
- #2549's note that a group signal takes an in-flight relay with it: the lock half is closed, since the holder outlives the group's signal and drains. The relay's `update_pr.sh` itself still stops on its group's signal, which is a stop the reap handles.
- Revision 12, the stale lock: a flock cannot outlive its holder, and a holder that outlives its run is draining and says so (`drain`). It is already guarded by the dead-run null control above, and it is never broken by force while a push runs.

## Red checks

none. This head has no CI run yet; the orchestrator's push is its first.

## Forward-carry

Two are not built here:
- Revision 12's "every self-test runs under a timeout in its own process group, reaped on exit". It reaches CI wiring and every self-test, outside this group's files, and a group kill conflicts with `pr_kill`'s never-a-group rule. Carry: R10-UPDATE-PR-SIGNALS
- The quiet-output convention for `update_pr.sh`, `open_pr.sh` and `merge_train.py`. The roster asks for it to share R10-FLOW-JIDOKA's flag convention for `prepr.sh`, which another seat is building now, and building it in parallel would let the two diverge. It needs an after-edge on R10-FLOW-JIDOKA. Carry: R10-UPDATE-PR-SIGNALS

## Friction

- `fixer.md#2`: unclear: `mut:pushhold`'s first placement emptied its function, a syntax error, and its arm passed because nothing ran. The step's "a vacuous mutation reads exactly like a passing check" caught it only because every mutant arm was also run against the real file. Requiring a mutant arm to show that its fixture reached the mutated code (here `treen = 4`) would make that cheap to catch. Carry: R10-UPDATE-PR-SIGNALS
