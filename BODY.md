A TERM, INT, HUP or SIGKILL of a running `update_pr.sh`, sent to the run alone or to its whole process group, no longer frees the branch lock while the run's push is still running. Round 2 adds four things, one per open item of the round-1 block (issue comment 6401966563):
- every self-test of this group's files runs as a session of its own under a deadline, and that whole session is ended when it exits (`pr_bounded`, Revision 12);
- git's auto-maintenance inside a push runs in the foreground, so a `git gc --auto` that a push's `git fetch` starts can no longer outlive the push holding its lock;
- the branch lock's holder leaves `update_pr.sh`'s worktree detached once the push has ended, so a SIGKILLed run's worktree is detached too;
- `cloud_relay.sh` starts the update in a process group of its own, so a signal to the loop's whole group reaches the update only through the loop's reap.

Round 3 closes the round-2 block (issue comment 6402890433): `pr_bounded`'s watchdog now leaves its caller's process group (`os.setsid()` in its fork branch, `# mut:dogsid`), so a SIGKILL to the caller's whole group takes the supervisor but never the watchdog, which reads the pipe's EOF and ends the self-test's session. A new arm group-KILLs the supervisor's caller and requires 0 live processes in either session.

Part of #2502.

**Round 1's mechanism, unchanged** (`tools/audit/seat/pr_args.sh`). The holder ignores TERM, INT and HUP and, once the run has ended, blocks on the push's own lock `<lock>.push` (`pr_push_hold`), an fd every process of the push inherits. The kernel frees that lock when the push's last process exits, so a zombie never holds it and no `ps` or group walk is needed. `pr_stopped` maps a 75 seen under errexit to exit 1, so only `pr_lock_busy` says BUSY.

**Round 2** (`tools/audit/seat/pr_args.sh`, `update_pr.sh`, `cloud_relay.sh`; the seat mutant harness):
- `pr_bounded <name> <command...>` (`pr_args.sh`, section "the self-test bound"). It execs a Python supervisor, which forks the self-test into a new session (`setsid`) and a watchdog outside that session. The watchdog is a session of its own too (round 3), out of reach of a signal to the caller's group, and ends the self-test's session (every live pid whose session id is the self-test's, by pid, KILL) at `PR_SELFTEST_SECONDS` (default 1200; exit 124 and a `BOUND:` line), or when its pipe from the supervisor reads EOF, which happens when the supervisor is gone, a SIGKILLed one included. When the self-test exits, the supervisor ends whatever of the session is left, prints how many it ended, and keeps the self-test's status. A TERM, INT or HUP to the supervisor ends the session too. `pr_args.sh --self-test`, `update_pr.sh --self-test` and `cloud_relay.sh --self-test` re-exec themselves through it once (`PR_BOUND` guards the second entry). `open_pr.sh --self-test` runs `pr_args.sh --self-test`, so its long part is bounded too.
- Why a session kill is sound here when `pr_kill` never signals a group: the session belongs to the self-test alone, while a pusher's group is shared with its caller. `sigrun`'s fixture now takes a process group (`setpgid`) rather than a session, so it stays inside the bound. The bystander sleeper lives as long as the bound (it was 3600 s in round 1, up from 300), and the bound's session ends it at the latest.
- `pr_push_hold` exports `gc.autoDetach=false` and `maintenance.autoDetach=false` through `GIT_CONFIG_COUNT`, appended once (`PR_FG_GC`). It runs before the fork, so the push inherits them. This is the reviewer's option (a). A gc in the foreground is part of the push: the reap reaches it, the drain waits for it, and the BUSY line ("the push of run N") is true while it runs.
- `pr_branch_lock <lock> <branch> <worktree> detach`: after the drain, still holding the branch lock, the holder runs `git -C <worktree> checkout -q --detach`. That is never under a push and never under the next run, and it runs whether the run's trap ran or not. `update_pr.sh` passes `detach`; `open_pr.sh` does not, so its behaviour is unchanged. `update_pr.sh`'s `PR_AFTER_REAP` detach and `pr_push_ended` are deleted: the holder covers both.
- `pr_own_group <command...>` execs a command as the leader of its own process group. `cloud_relay.sh`'s update launch line runs through it. The update is still the reap's lead (`PR_REAP_LEAD`, found by parent pid), so a stopped relay TERMs it alone and in order. A group-wide TERM or HUP to the loop reaches the update only through that reap, and a group-wide KILL leaves the update to finish under its own lock.

Alternatives considered:
- (a) For the gc, close fd 9 in git's daemonized child. git exposes no hook for that.
- (b) For the gc, set `gc.auto=0` for the push. That turns maintenance off where the reviewer asked for it to be counted.
- (c) For the self-test bound, `timeout(1)` per CI step. It covers neither a local run (the 8.6 h orphan was local) nor a SIGKILLed parent.
- (d) For the detach, detach on the next run's start. That leaves the branch held between runs, which is exactly when the merge train's recarry reads it.

## Head

`cfc707961b4ae68311eb9711b3d4b5e4076ed000` (code), one commit on the PR head `ab80907a81e63997094f60c2adf62f059c2c9938`, which already contains `origin/handoff/r10-update-pr-signals` (`0ca3e5b71`), so the push is a fast-forward of that ref. Merge base with origin/main `c9cbe6b458a7053f914649eb02d5296d6cd8c0f4`. origin/main was `f3ffb1c635327365841ad430ce8fad7488a02d61` at 2026-10-25T20:45Z, and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged (`fixer.md` step 6). The round-3 figures were measured 2026-10-25 between 20:20Z and 20:50Z, git 2.43.0. Round 2's figures below that are not re-stated were taken at `0ca3e5b71`; round 3 changes only `PR_BOUND_PY`'s watchdog branch, its comment and the self-test.

## Mutation proof

Each `# mut:<name>` line is a predicate. The self-test deletes it from a copy and requires its arm to fail. All of these arms pass in the head's `123 checks, 0 failed` run. Round 3's mutant first:

| mutant | what goes red |
|---|---|
| `mut:dogsid` (round 3) | `mutant mut:dogsid (its line deleted): the group kill takes the watchdog too and the self-test runs on` |
| `mut:fggc` | `mutant mut:fggc (its line deleted): git detaches that gc, which keeps the push's fd 9 once the push has ended` (git prints `Auto packing the repository in background`) |
| `mut:detach` (now the holder's line) | `mutant mut:detach (its line deleted): the SIGKILLed run's worktree still holds fix/t`, and the clean-run arm `the worktree still holds fix/x` |
| `mut:dogend` | `mutant mut:dogend (its line deleted): the bound passes and nothing ends the self-test, which runs on`; `... the SIGKILLed supervisor's self-test runs on` |
| `mut:boundreap` | `mutant mut:boundreap (its line deleted): the child outlives the self-test` |
| `cloud_relay-29` (`dev/audit/harnesses/r10_seat_selftests_mutants.py`: `pr_own_group "${upd[@]}"` back to `"${upd[@]}"`) | `KILLED rc=1 \| cloud_relay self-test: 270 checks, 2 failed`, the two failing being `a TERM to the relay's whole process group reaches the update only through the relay's reap, which TERMs it alone first` and `a KILL to the relay's whole process group leaves the in-flight update to finish under its own lock` |

`mut:dogsid` was deleted from the real `pr_args.sh` (a `git archive` copy of the head, `grep -v '# mut:dogsid$'`, one line differing) and the whole self-test run: `pr_args self-test: 123 checks, 1 failed`, rc 1, the one failure `FAIL pr_bounded: a SIGKILL to its caller's whole group still ends the self-test, 0 survivors in either session`. That run is also round 3's failing test first: without the line, the production code is round 2's.

Round 2, at `0ca3e5b71`: `mut:fggc` and `mut:detach` were also deleted from the real `pr_args.sh`, each in its own detached worktree at the head, and the whole self-test was run:
- `mut:fggc`: `pr_args self-test: 121 checks, 1 failed`: `FAIL update_pr: the push's git gc --auto runs in the foreground, as part of the push, so nothing it starts outlives the push holding its lock`
- `mut:detach`: `pr_args self-test: 121 checks, 2 failed`: `FAIL update_pr: the SIGKILLed run's worktree holds the branch while its push runs, and its lock's holder leaves it detached once the push has ended`, `FAIL update_pr: the run leaves its worktree detached, so no worktree holds the branch`

Round 1's mutants (`mut:drain`, `mut:pushhold`, `mut:holdsig`, `mut:busy75`, `mut:nopgrep`, `mut:watch`, `mut:stop`, `mut:unlock`) still have their arms. All of them pass in the head run.

**Failing test first (round 2).** Round 2's self-test was run against round 1's production code (`ecf96c46d`): its `pr_args.sh` up to the pusher census, with the head's self-test below it, and `update_pr.sh` at `ecf96c46d`. It ran with `PR_BOUND=1`, since `pr_bounded` does not exist there. Result: `pr_args self-test: 121 checks, 8 failed`. The 5 positive arms that fail are the defect measured: `the SIGKILLed run's worktree holds the branch while its push runs, and its lock's holder leaves it detached once the push has ended`, `the push's git gc --auto runs in the foreground ...`, `a self-test past its bound is ended ... exits 124 saying so`, `a self-test that exits leaving a child is reaped on exit, keeping its status` and `a SIGKILLed supervisor's self-test is ended all the same, by its watchdog`. The other 3 failures are mutant arms whose line does not exist at that base (`mut:dogend` twice and `mut:boundreap`).

A round-1 lesson, now pinned: `mut:fggc`'s first placement spanned two lines with a `\` continuation. `copyin` deletes one line, so the copy was broken and the arm read it as a pass. The new arm `every # mut: line is a whole statement, never one continued from the line above` refuses that shape, and its null control names a synthetic continued line.

## Null control

- The group-KILL arm runs the caller as a session of its own (`os.setsid()` then exec), so its `kill -KILL -- -<pgid>` reaches nothing of the running self-test; its mutant arm reads `held`, so a group kill that ended nothing would not read as a pass.
- The real command at both ends, with my own probe `grpkill.sh` (`pr_args.sh --self-test` started as a session of its own, its caller's group KILLed 15 s in, every session it made counted 3 s later through `/proc`, zombies excluded): at `ab80907a` the self-test's session held `11` live processes (the reviewer's figure reproduced), at the head every session held `0`.
- `pr_bounded: a self-test that exits leaving a child is reaped on exit, keeping its status`. Its status 3 comes back unchanged, so the bound changes no verdict.
- `null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`. The bystander sleeper survives (`unrel = alive`).
- `update_pr: the push's git gc --auto runs in the foreground ...` reads git's own message. Run outside the push, with the same fixture repository and git, `git -c gc.auto=1 gc --auto` prints `Auto packing the repository in background for optimum performance.` That is git's default, and it is what the arm must not see.
- The SIGKILL worktree arm reads `branch` at the drain mark, while the push runs, and `detached` only after the push lock is free. So the detach is never made under a push.
- `with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order` and the per-pid TERM arms still pass. The relay's reap order is unchanged.
- Stopping two of this session's own bounded self-test runs (`update_pr.sh --self-test` and a mutant `pr_args.sh --self-test`) through the task runner left no process of either. `ps -eo pid,ppid,etimes,stat,args` afterwards listed only the separate, unbounded failing-first run, whose sleeper was still alive under its own shell as expected.

## Figures

All at the head `cfc707961`, merge base `c9cbe6b45`, unless a row says otherwise.

| command | result |
|---|---|
| `bash tools/audit/seat/update_pr.sh --self-test` (bounded; runs `delivery_row.sh`'s, then `pr_args.sh`'s inside the same session) | `delivery_row self-test: 6 checks, 0 failed`, `pr_args self-test: 123 checks, 0 failed`, rc 0 |
| `bash tools/audit/seat/pr_args.sh --self-test` | `pr_args self-test: 123 checks, 0 failed`, rc 0, real 2m44s |
| `bash tools/audit/seat/cloud_relay.sh --self-test` | `cloud_relay self-test: 270 checks, 0 failed`, rc 0 |
| `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-29` | `== cloud_relay-29 cloud_relay.sh: KILLED rc=1 \| cloud_relay self-test: 270 checks, 2 failed`, `RESULT survivors=0` |
| `bash tools/audit/seat/pr_args.sh --pushers` | rc 0, no `OPEN` |
| `python3 tests/throwaway_git.py --check` | `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD` |
| `python3 -I tools/audit/seat/ref_privacy.py --check` | `0 refused` |
| `python3 -I tools/audit/seat/tmp_paths.py --check` | `tmp_paths: 0 refused, 0 stale allow entries at HEAD` |
| `PYTHONPATH=tests/hastub python3 tests/structure.py` | `STRUCTURE RATCHET PASSED`; no `*_budgets.json` in the diff |
| `python3 tools/audit/archscore/score.py --diff c9cbe6b45 HEAD` | `Architecture score: dS +0.0000 NULL` |
| `PYTHONPATH=tests/hastub python3 tests/entities.py`, at the head and at the merge base `c9cbe6b45` in its own worktree | `2 of 2445 ENTITY CHECKS FAILED` at both, the same two: `gate-sweep.yml: on CI's completion, no concurrency, ...` and `graders-head-copy's delivery_status step is red only when ...`. Both drive CI workflow steps this diff does not touch, and they fail identically without it, so they are this container's, not this PR's; it is why `prepr.sh`'s closures step refused (`failed while being recorded: tests/entities.py (exit 1)`), left to CI, which ran `tests/entities.py` green at `ab80907a` |
| `python3 tests/closure.py select --diff c9cbe6b45` | `MODE: SCOPED -- 0 script(s) run, 33 scoped out`; `scope.run` empty |
| `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` | `CI PREDICT: no closures, fast, wave-script or instrument red predicted against c9cbe6b458a7 (a data-file read is not seen)` |

Determinism: every new wait polls a condition, and its bound only decides how fast a broken tree fails:
- the bound arms wait on the child's mark file, then read the child's lock by trying it, never by pid;
- the supervisor-KILL and caller-group-KILL arms wait for that lock to free, with a 5 s bound below the child's 20 s sleep, so a session that nothing ends still reads `held`;
- the gc arm reads git's own detach message;
- the relay arms wait on the update's pid file and its `done` mark.

### Carries, item by item

- **[0] #2469 round-4 split.**
  - SIGKILL frees the lock early: met in round 1 (`mut:drain`, `mut:pushhold`). The reviewer measured it from the real file.
  - A group signal reaches the holder: met (`mut:holdsig`, the grpTERM and grpHUP arms).
  - 75 under `set -e`: met (`mut:busy75`).
- **[1] Revision 12.**
  - Lock half: shown not to apply, as the round-1 review accepted. A flock cannot outlive its holder, and a holder that outlives its run is draining and says `drain`. A lock left by a dead run is covered by the null control `a lock left by a dead run (the kernel freed it) does not block`.
  - Self-test half: met by `pr_bounded` (`pr_args.sh`, section "the self-test bound"). It is wired into the entries of `pr_args.sh`, `update_pr.sh` and `cloud_relay.sh`, with arms for the bound, the exit reap, a SIGKILLed supervisor and a SIGKILL to the supervisor's caller's whole group (`mut:dogend`, `mut:boundreap`, `mut:dogsid`). The sleeper now lives as long as the bound, not 3600 s.
  - The class: `git grep -lE -- '--self-test' -- 'tools/audit/seat/*.sh'` returns 16 files.
    - Bounded here: `pr_args.sh`, `update_pr.sh` and `cloud_relay.sh` (this group's files), and `open_pr.sh`, whose long part is `pr_args.sh --self-test`.
    - Not bounded: the other 12 (`body_patch.sh`, `bus.sh`, `ci-watch.sh`, `cloud-setup.sh`, `delivery_row.sh`, `failure_logs.sh`, `handoff_push.sh`, `heartbeat.sh`, `merge_pr.sh`, `seat_venv.sh`, `tick_loop.sh`, `train.sh`). They are outside this group's files, and none of them is the instance Revision 12 measured. `delivery_row.sh`'s self-test runs inside the bound when it is reached through `update_pr.sh` or `open_pr.sh`. They are routed in Forward-carry.
- **[2] The worktree left on the branch.** Met for every stop, SIGKILL included: the holder's detach (`pr_args.sh`, `pr_branch_lock`'s `detach` line), the arm `update_pr: the SIGKILLed run's worktree holds the branch while its push runs, and its lock's holder leaves it detached once the push has ended`, and `mut:detach`. The clean-run arm `update_pr: the run leaves its worktree detached` still passes.
- **[3] Quiet output.** Not built. The roster ties its flag convention to `prepr.sh`'s, which R10-FLOW-JIDOKA owns and has not landed (`git log origin/main -- tools/pr/prepr.sh` shows no quiet flag). It is routed to that group in Forward-carry, so it does not close with this one.
- **[4] #2549's relay half.** Met: `cloud_relay.sh`'s launch through `pr_own_group`, the two group arms, and the harness mutant `cloud_relay-29`. `git grep -iE 'setsid|pgid|process group' -- tools/audit/seat/cloud_relay.sh tools/audit/seat/update_pr.sh` is now non-empty: the launch comment and the self-test.
- **Round-1 block 2, the detached `git gc --auto`.** Met by `pr_push_hold`'s export (`mut:fggc`, real-git arm with auto-maintenance turned on).
  - The class is "a process the push starts that outlives it holding fd 9". `git grep -nE 'start_new_session|os\.setsid|daemoniz|nohup|disown' -- tools tests`, less `pr_args.sh`, `daemonize.py` and comments, returns `tests/entities.py:15586`, `tests/gate_lock.py:887` and `tools/audit/judge_batch.py:275`. Each is a `subprocess.Popen` with `close_fds` left at its default (true; `gate_lock`'s `pass_fds` names its own fds), so none of them inherits fd 9.
  - `git grep -n daemonize -- tools/pr/app_push.sh tools/pr/prepr.sh tools/pr/app_mint.sh` is empty.
  - git's own auto-detach is the remaining seam, and it is closed here.

## Red checks

none. This head has no CI run yet. At `ab80907a` every completed gate check was green; `governance / delivery-status` was red on main's own overdue rows (#2780, #2749, #2775, #2797, #2762, #2795), not this PR's (the diff adds only `dev/programme/delivery/2825.md`), and it is not a required check.

## Forward-carry

- The quiet-output convention (roster carry [3]) for `tools/audit/seat/update_pr.sh`, `tools/audit/seat/open_pr.sh` and the per-car progress of `tools/audit/seat/merge_train.py` follows `prepr.sh`'s quiet flag once that lands: one result line per step, the failing step's tail, the full output in a printed log, a verbose switch, and every key line kept. It has the same controls (a seeded failure's tail in quiet mode, equal exit codes, a mutant per rule). `update_pr.sh` already sends the push's whole output to `$WT.log` and prints its refusal or the log's last 20 lines (`pr_push_failed`), so the remaining work there is the switch and the step lines. Carry: R10-FLOW-JIDOKA
- Self-test hygiene, to sit beside that group's items (a)-(d): a seat self-test enters through `pr_args.sh`'s `pr_bounded`, which ends its whole session on exit, at `PR_SELFTEST_SECONDS` or when its supervisor is gone, a supervisor SIGKILLed alone or with its caller's whole process group: the bound's watchdog is a session of its own, so a group KILL never takes it with the supervisor (round 2's watchdog shared the caller's group and left 11 unbounded survivors). A bound adopted another way must survive that group KILL too. 12 seat self-tests outside this group's files do not enter through it yet: `body_patch.sh`, `bus.sh`, `ci-watch.sh`, `cloud-setup.sh`, `delivery_row.sh`, `failure_logs.sh`, `handoff_push.sh`, `heartbeat.sh`, `merge_pr.sh`, `seat_venv.sh`, `tick_loop.sh`, `train.sh`. Carry: R10-FLOW-JIDOKA

## Friction

- `fixer.md#2`: unclear: a `# mut:` predicate continued from the line above (`\`) is broken by a one-line deletion, and its arm read the broken copy as a pass (`mut:fggc`'s first placement). The step's "a vacuous mutation reads exactly like a passing check" did not name this shape. It is now pinned in this group's self-test by the `mutshape` arm, but other in-file mutant harnesses have no such check. Carry: R10-FLOW-JIDOKA
