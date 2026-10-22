A stopped pusher must not leave its work running, and no pusher, or launcher of one, may join the tree without the same guarantee.

A shell does not forward TERM, INT or HUP to a foreground child. So a stopped pusher exited, its subtree was reparented, and the subtree kept burning CPU. On 2026-10-20 six survivors were swept up, aged 26 to 62 minutes, on a box at load 77 on eight cores. The review of `9629ae17` blocked on `tools/audit/seat/train.sh`. The launcher for `merge_train.py batch` forwarded no signal. A TERM to the pid in its own `train.pid` ended the launcher and removed the pidfile, and the train's whole tree kept running, which let a second train start on the same state dir. This round fixes train.sh. It also extends the class rule so that it returns every caller of a runner and every Python child a seat script launches, and it dispositions each seam that rule returns.

**The rule (the census, level 1).** `tools/audit/seat/pr_args.sh --pushers [<rev>]` defines a pusher as any tracked `tools/` script (`*.sh`, `*.py`, `*.mjs`, `*.js`) that names `app_push.sh` or `push.sh`. The test is the census's `git grep -lE '(^|[^A-Za-z0-9_])(app_)?push\.sh'`. Every path the grep returns needs exactly one disposition in `PR_PUSHERS`:
- `runner`: the script installs `pr_exit_trap`, and every line running `"$_push"` or `"$prepr"` runs it asynchronously.
- `runner-py`: the script TERMs its tool rather than SIGKILLing it, and its entry calls `stop_on_signal()`.
- `retired`: `push.sh`.
- `mention`: the script names a pusher but runs none, and the entry gives the reason.

The census prints `OPEN` and exits 1 in three cases: a path the grep returns with no entry, an entry the grep no longer returns, and a runner that lacks either property. `pr_args.sh --self-test` runs the census on the tree, and CI runs that self-test (the `open_pr.sh` and `update_pr.sh --self-test` steps).

**Level 2: who launches a runner, and which Python children a seat script starts.** These two rules are new in this round. Each is a command, and `## Figures` dispositions every file each one returns. The level-2 rule now also returns callers of the runner-py `merge_train.py`, and callers that name a runner through a `${VAR:-default}` path, which is how `tick_loop.sh` names `cloud_relay.sh`. The Python-child rule returns every non-comment line of a `tools/audit/seat/*.sh` or `tools/pr/*.sh` script that starts `python` or `python3`.

**The mechanism is one EXIT trap.** `pr_exit_trap [<command>]` sets an EXIT trap that runs `<command>`, then `pr_reap`, then `$PR_AFTER_REAP`. bash runs the EXIT trap when TERM, INT or HUP ends the shell, as well as on every other exit. Each push runs asynchronously and the shell `wait`s on it: an untrapped INT waits for a foreground child, while all three signals interrupt `wait`. `pr_reap` walks `pgrep -P` from `$$` and TERMs each pid. It KILLs whatever outlives a 2 s grace (`# mut:grace`), and it ignores further stop signals while it runs (`# mut:sigign`). Every signal goes to a numeric pid the walk returned, never to a pattern or a group.

**New in this round: the lead.** Some runners have a child that is itself a runner. Such a runner names that child `PR_REAP_LEAD`. `pr_reap` takes its walk first, while the tree is still attached. It then calls `pr_lead_stop  # mut:lead`, which TERMs the lead alone and waits up to `PR_REAP_LEAD_TENTHS` (default 300, so 30 s) for the lead to stop its own tree in its own order. After that it TERMs, and after the grace KILLs, every pid of the walk that is still alive, orphans included.
- `pr_lead_stop` signals the lead only when the walk returned it (`# mut:leadwalk`). A stale `PR_REAP_LEAD`, whose pid a later process may now hold, is never signalled.
- `train.sh` sources `pr_args.sh` and calls `pr_exit_trap`, with the pidfile removal in `PR_AFTER_REAP`. It runs `merge_train.py` exec'd in its subshell, asynchronously, as the lead. So a TERM, INT or HUP to the pid in `train.pid` lets `merge_train.py` run its own stop first: `stop_on_signal()` raises `SystemExit`, `Train._run` TERMs the tool, and `batch`'s `finally` releases the train's hold and worktrees. The reap then ends whatever is left, and only then is the pidfile removed.
- `cloud_relay.sh` makes `update_pr.sh` itself its lead. Before this, a stopped relay's reap TERMed the whole tree at once, including `update_pr.sh`'s branch-lock holder. The holder has no handler, so it exited and freed the lock while a TERM-ignoring child of the push could live through the 2 s grace. That was #2502's TERM property broken one level up. The relay now TERMs `update_pr.sh` alone, which frees the lock only after its own reap has ended the push.
- Alternatives considered:
  - TERM the whole tree at once with a 30 s grace (`PR_REAP_TENTHS=300` in train.sh). It is one line, but it ends a lock holder beside the push it guards, so it repeats the cloud_relay defect at any runner that runs a locking runner.
  - Forward the TERM to the child only. Once the child is gone its orphans are no longer under the launcher, so nothing reaps the stub tree the finder measured (5 of 5 survive).
  - A process-group kill. `pr_kill` deliberately never signals a group, because on a shared box a group can hold other seats' processes.

**The branch lock (from main, kept).** Main's `pr_branch_lock` is the one per-branch lock, shared by `open_pr.sh` and `update_pr.sh`. It hands its unlock to the reap. `PR_REAP_SPARE` keeps the lock's holder out of the walk, and `PR_AFTER_REAP` ends the holder after the reap. So a TERMed, INTed or HUPed run frees the branch only once its push has ended.

Seams treated in this diff: `handoff_push.sh`, `remerge_main.sh`, `merge_train.py`, `cloud_relay.sh`, `train.sh`, and the three pushers named before (`open_pr.sh`, `update_pr.sh`, `app_push.sh`).

Part of #2502, which stays open when this PR merges. That issue's SIGKILL clause, and the Revision-12 self-test isolation the roster puts on this group, are routed under `## Forward-carry`.

## Head

`a01627177715d6f363eee2f8add5b19f7a97945d` merges the authored code head `f1e7b88956f6da2407f0cadcf7c6cac1fa340e87` and then merges origin/main `dcf12f490` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`f1e7b88956f6da2407f0cadcf7c6cac1fa340e87` is the code head, and everything below was measured there unless a line names another commit. origin/main was `07fcbee2ed9e38e71d8ca497e1b2470b16baf09f`, read 2026-10-22T03:10:49Z, and it is this head's merge base.

This head is the reviewed head `9629ae174f1099e11c6b17f80fe935ae6cba698b` plus seven commits:
- `a69446c35` adds train.sh's stop arm (arm 9) alone, the failing test (`## Mutation proof`).
- `dabd93cfc` adds the lead to `pr_args.sh`'s `pr_reap`, `train.sh`'s `pr_exit_trap` and asynchronous `merge_train.py`, `cloud_relay.sh`'s update as the lead, and the `pr_args.sh` and `cloud_relay.sh` lead arms.
- `7d732e31d` and `2c9cc6815` silence the shell's job-status line in arm 9. They change only the test's stderr.
- `8cd8c89a2` merges origin/main `3976515a`.
- `174333c88` adds train.sh arm 10 (the lead's order in the train) and `pr_args.sh`'s stale-lead arm (`mut:leadwalk`).
- `f1e7b8895` merges origin/main `07fcbee2`.

Both merges were clean, and neither changed this PR's ten files or the files their self-test fixtures source (`prepr.sh`, `head_note.py`, `delivery_row.sh`, `pr_cap.py`, `tests/throwaway_git.sh`, `ci_predict.py`). The checks: `git diff --quiet 7d732e31d 8cd8c89a2 -- <those>` and `git diff --quiet 174333c88 f1e7b8895 -- <those>` both exited 0.

`prepr` runs with `PREPR_SKIP_CLOSURES=1` (the owner's ruling). The scoped gate was derived separately and is in `## Figures`.

## Conflict resolution

This round's two merges of origin/main were clean (`## Head`). Earlier rounds resolved these hunks, and the code still carries each resolution:
- `pr_branch_lock`: main's own `trap … EXIT` and `trap 'exit 143' TERM INT HUP` would overwrite the caller's EXIT trap. They are replaced by `PR_AFTER_REAP` (`# mut:unlock`) and `PR_REAP_SPARE=$LKP`. SPARE and ORDER below pin that the lock is freed only after the reap.
- `update_pr.sh`: main's `pr_branch_lock` replaces this PR's inline flock, `pr_exit_trap` sits on the line before it, and main's `--row-only` (`# mut:rowonly`) passes through the asynchronous push.
- `handoff_push.sh`: main's `push_app` seam and its `# mut:push-update/open/row` anchors are kept. The push inside `push_app` is asynchronous, on one line ending in ` &`, so the census can read it.
- `app_push.sh`: main's `row_only_checks` gate runs after the asynchronous prepr, unchanged.

## Mutation proof

**Failing test first.**
- train.sh arm 9 (`a69446c35`) runs the finder's two-level stub tree (5 pids) under a `merge_train.py` stub and signals the pid in `train.pid`.
  - At `a69446c35`, whose `train.sh` production lines are the reviewed head's, `bash tools/audit/seat/train.sh --self-test` printed `TERM to the train (pid …, launcher …) left 5 of 5 pids of its tree alive (pidfile removed, early)` in 3 of 3 runs, rc 2.
  - At this head it prints `train.sh self-test: ok (… a stop reaps the tree, merge_train.py first)`.
- The cloud_relay lead arm: I restored the reviewed head's two update lines (`{ …; } >&2 &` and `wait $! || urc=$?`) into `cloud_relay.sh`, otherwise at `dabd93cfc`. `bash tools/audit/seat/cloud_relay.sh --self-test` then printed `cloud_relay self-test: 83 checks, 1 failed`, `a relay TERMed mid-update TERMs the update alone first …`, in 3 of 3 runs. With the line restored to the fix it prints 83 checks, 0 failed.

**This round's mutants**, each applied by a scratch `mut.py` that asserts its anchor occurs exactly once, in a fresh detached worktree at `174333c88`. Each ran `train.sh`, `cloud_relay.sh` and `pr_args.sh --self-test`, and the worktree was removed afterwards. From `174333c88` to this head the delta is one clean merge that touches none of these files (`## Head`).
- **M0 (no change):** train `ok`; `cloud_relay self-test: 83 checks, 0 failed`; `pr_args self-test: 90 checks, 0 failed`.
- **TR-TRAP, train.sh's `pr_exit_trap` line deleted:** train refuses: `left 5 of 5 pids of its tree alive (pidfile present, none)`.
- **TR-AFTER, train.sh's `PR_AFTER_REAP='rm -f "$pidfile"'` deleted:** train refuses: `left 0 of 5 … (pidfile present, none)`.
- **TR-LEAD, train.sh's `PR_REAP_LEAD=$!` renamed to a plain variable:** train refuses at arm 10: `a TERMed train did not stop merge_train.py first (alive 0, marks 'G early ', pidfile removed)`.
- **TR-FG, train.sh's launch back in the foreground (` &` dropped):** train refuses at arm 4: `the stubbed --ignore-red run did not succeed`.
- **PA-LEAD, `pr_lead_stop  # mut:lead` deleted:** train refuses at arm 10; `cloud_relay self-test: 83 checks, 1 failed` (the lead arm); `pr_args self-test: 90 checks, 2 failed` (the lead arm, and the `mut:leadwalk` arm, whose line no longer runs).
- **PA-LEADTERM, `pr_lead_stop`'s `pr_kill TERM "$PR_REAP_LEAD"` deleted:** train refuses at arm 10; cloud_relay 83/1; pr_args 90/1 (`a lead (PR_REAP_LEAD) is TERMed alone …`).
- **PA-LEADWALK, `pr_lead_stop`'s walk-membership `return 0` emptied:** pr_args 90/1: `a PR_REAP_LEAD outside the walk (a stale or reused pid) is never signalled; …`.
- **CR-LEAD, cloud_relay.sh's `PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD"` turned back into `wait $!`:** cloud_relay 83/1, the lead arm.

**The earlier rounds' mutants, re-run at this head** by a scratch `mut2.py` (same exact-once anchor assertion, fresh detached worktree at `f1e7b8895`, removed afterwards). Each ran the self-test named:
- **STOP, `pr_kill`'s kill line (`# mut:stop`) emptied:** pr_args 90/9: the open_pr TERM and INT arms, handoff_push, remerge_main, update_pr, the KILL-after-grace arm, and three lead arms.
- **RECURSE, `pr_descendants "$k"` emptied:** pr_args 90/7.
- **GRACE, the KILL loop (`# mut:grace`) emptied:** pr_args 90/1, `the reap KILLs a child that ignores TERM once the grace is spent …`.
- **SIGIGN, `trap '' TERM INT HUP` (`# mut:sigign`) emptied:** pr_args 90/1, the same arm.
- **EXITREAP, `pr_exit_trap`'s trap line emptied:** pr_args 90/15.
- **SPARE, `PR_REAP_SPARE=$LKP` emptied:** pr_args 90/2 (`mutant mut:unlock …`, `update_pr: a TERMed run whose push outlives the TERM keeps the lock until the reap has ended it`).
- **ORDER, `pr_exit_trap`'s order reversed:** pr_args 90/1, the `heldrun` arm.
- **M1, handoff_push.sh's `pr_exit_trap` dropped:** pr_args 90/4.
- **M2, handoff_push.sh's push in the foreground:** pr_args 90/2, both census arms.
- **M3, remerge_main.sh's `pr_exit_trap` dropped:** pr_args 90/3.
- **M5, cloud_relay.sh's `pr_exit_trap` dropped:** cloud_relay 83/2 (the reap arm and the lead arm).
- **M6, app_push.sh's `pr_exit_trap cleanup` dropped:** `app_push self-test: 186 checks, 11 failed`.
- **M6B, the same line as `trap cleanup EXIT`:** app_push 186/1, `and leaves none of prepr's tree alive (R10-PUSHER-REAP) (got '3', want '0')`.
- **M7, `Train._run`'s `p.terminate()` turned into `p.kill()`:** `merge_train self-test: 200 checks, 1 failed`.
- **M8, `main`'s `stop_on_signal()` call deleted:** pr_args 90/2, both census arms.
- **M9, the handler's `raise SystemExit(128 + signum)` turned into `return None`:** merge_train 200/1.
- **OPENFG, open_pr.sh's first push back in the foreground (its ` &` dropped):** killed. pr_args hit `timeout 600` (rc 124) with 9 arms already failed, among them `open_pr: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it` and both census arms.
- **UPDFG, update_pr.sh's push back in the foreground:** killed. pr_args hit `timeout 600` (rc 124) with 6 arms already failed: both census arms, `update_pr: after the stop the lock is free, so the next run takes it`, the SIGKILL no-stale-lock arm, the dead-lock null control, and the detached-child arm.

**Built-in mutants.** `pr_args.sh`'s self-test runs each of these on copies of the scripts, and each arm passes only when its mutant shows the defect: `mut:exitreap`, `mut:grace`, `mut:sigign`, `mut:stop`, `mut:unlock`, `mut:watch`, `mut:lock`, `mut:oplock`, `mut:unpushed`, `mut:rowonly`, the sed mutant `afterreap`, and this round's `mut:lead` and `mut:leadwalk`. All of them pass in M0.

**The finder's harness at both ends.** The review's `evidence/harness_reviewer/train/run_train.sh` (sha1 `35c7d548`), with its `stub.sh` (`64758b0b`) and its `C/tools/audit/seat/merge_train.py` (`04cc1898`), comes from `origin/review/2524`. It ran against each end's `train.sh` beside that end's `pr_args.sh`:
- Base, `9629ae17:tools/audit/seat/train.sh` (sha1 `66552e34`): `survivors=5/5` and `pidfile=removed`, 3 of 3 runs.
- Head, `train.sh` (sha1 `311e19e7`): `survivors=0/5` and `pidfile=removed`, 3 of 3 runs.
- The same harness with its `kill -TERM` replaced by `kill -$SIG`:
  - INT: base `launcher=alive … survivors=5/5`; head `launcher=gone pidfile=removed survivors=0/5`.
  - HUP: base `survivors=5/5`; head `survivors=0/5`.
  - Each 3 of 3 runs.

**Unpinned.** One line has no killing test. TR-EXEC deletes train.sh's `exec ` before `python3 -u tools/audit/seat/merge_train.py`, and all three self-tests stay green. On this container's bash 5.2.21 the mutant is equivalent: bash execs a subshell's last simple command itself, measured with `bash -c '( cd /tmp || exit 2; sleep 3 ) & p=$!; …; ps -o cmd -p $p'`, which printed `sleep 3` with no child under it. The explicit `exec` is for macOS's `/bin/bash` 3.2, which forks there, and then the lead would be a bare subshell that dies on TERM without forwarding it. No test can tell the two apart on a bash that execs anyway. `ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against 07fcbee2ed9e`.

## Null control

- **The bystander.** An unrelated sleeper outside any pusher's tree survives every TERM arm and the successful-run arm. The reap goes by pid only. The finder's train harness, run at the head with a `sleep 60` started outside it, printed `survivors=0/5 bystander=alive` in 3 of 3 runs.
- **The stale lead.** The `staleld` arm sets `PR_REAP_LEAD` to a sleeper outside the host's tree. That sleeper survives the host's reap, and the host's own child does not. Its mutant (`mut:leadwalk`) shows the probe can see the sleeper TERMed.
- **The lead arms' probe.** Each lead arm's child G writes a mark when TERMed, and the lead, once TERMed, writes `early` if G was marked before the lead ended it. With the lead removed (PA-LEAD, TR-LEAD, CR-LEAD) the arm reads `early`, so the probe can see a whole-tree TERM. With `9629ae17`'s cloud_relay update lines restored, the cloud_relay lead arm failed in 3 of 3 runs.
- **train.sh arm 9's pidfile probe** reads `early` when the pidfile is gone while a tree pid lives. At `a69446c35` it read `early`. At this head it reads `none`.
- **The census.** On a scratch tree the census refuses three plants: an undispositioned `new_pusher.sh`, a deleted `pr_exit_trap`, and a dropped `&`. These are self-test arms. At the merge base, `--pushers 07fcbee2` reports 6 OPEN, so the census sees the tree without this PR.
- **No vacuous reap arm.** Every reap verdict first requires that the tree started: 4 recorded pids (`treen`) in pr_args, 5 in train.sh arm 9 (`tn`), 2 in the lead arms.

## Figures

All measured at `f1e7b88956f6da2407f0cadcf7c6cac1fa340e87`, with origin/main at `07fcbee2ed9e38e71d8ca497e1b2470b16baf09f` (read 2026-10-22T03:10:49Z), unless a line names another commit.

- **Level 1, the pusher census.** Rule: `bash tools/audit/seat/pr_args.sh --pushers <rev>`, the git grep above with the dispositions in `PR_PUSHERS`.
  - At this head, `bash tools/audit/seat/pr_args.sh --pushers HEAD | awk '{print $1}' | sort | uniq -c` printed `16 ok`, and the census exited 0.
  - `--pushers 9629ae174 | grep -c OPEN` printed 0. `--pushers 07fcbee2ed9e | grep -c OPEN` printed 6.

  | seam | disposition |
  |---|---|
  | `tools/audit/seat/handoff_push.sh`, `remerge_main.sh`, `open_pr.sh`, `update_pr.sh`, `tools/pr/app_push.sh` | runner, closed in this diff |
  | `tools/audit/seat/merge_train.py` | runner-py, closed in this diff |
  | `tools/pr/push.sh` | retired: decision 0011's retired author path; the level-2 rule returns no caller of it |
  | 9 `mention` paths: `pr_args.sh`, `handover_prompt.py`, `ref_privacy.py`, `app_approve.sh`, `approve_held_runs.sh`, `head_note.py`, `check-wave-script.mjs`, `friction_issues.mjs`, `policy_lint.mjs` | mention, each with its reason in `PR_PUSHERS` |

- **Level 2, who launches a runner (extended this round).** Rule:

      git grep -nE '(bash|exec|python3?)([[:space:]]+-[A-Za-z]+)*[^#|;]*(handoff_push|open_pr|update_pr|remerge_main|cloud_relay)\.sh|\$\{[A-Za-z_]+:-[^}]*(handoff_push|open_pr|update_pr|remerge_main|cloud_relay)\.sh|python3?([[:space:]]+-[A-Za-z]+)*[^#|;]*merge_train\.py|tool\("(remerge_main|app_push)"\)' <rev> -- 'tools/*.sh' 'tools/*.py'

  It returns 28 lines in 9 files at this head, 27 lines in 9 files at `9629ae17`, and 24 lines in 9 files at the merge base. The previous round's rule returned 6 files and missed `train.sh` and `tick_loop.sh`. Each file's disposition at this head:
  - `train.sh`, 1 line (`exec python3 -u tools/audit/seat/merge_train.py batch`): **closed in this diff**. train.sh is a runner of `merge_train.py` with it as the lead (arms 9 and 10).
  - `cloud_relay.sh`, 4 lines. Line `bash "$HERE/update_pr.sh" … >&2 &` runs update_pr: **closed in this diff**, with update_pr as the lead (the lead arm), on top of the round-2 reap arm. Its 3 other lines are its own self-test running `cloud_relay.sh`.
  - `tick_loop.sh`, 1 line (`relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}`): **left running by documented choice, no code**. The relay runs detached under a flock holder. The header says that a relay still in flight when the pass's wait ends "is left running, never killed (its update_pr.sh may be mid-push)". A stopped tick_loop.sh therefore leaves a relay running on purpose, and that relay reaps its own tree when it is stopped.
  - `merge_train.py`, 6 lines. 2 are `tool("remerge_main")` and `tool("app_push")` runs, which are runner-py and census-checked: `Train._run` TERMs the tool and waits up to `TOOL_STOP_SECONDS`. 4 are its docstring's usage lines.
  - `orchestrator_tick.py`, 4 lines: self-test `procs` stub strings naming `merge_train.py`. It launches nothing.
  - `pr_args.sh`, 9 lines: its self-test fixtures.
  - `handoff_push.sh`, 1 line: main's self-test fixture, which runs the script's copy in a scratch clone.
  - `r9_rc_bus_fetchhead.sh`, 1 line: a round-9 measurement harness that runs `handoff_push.sh` in a scratch fixture.
  - `tmp_paths.py`, 1 line: a self-test string.
- **Level 2-py, every Python child a seat script starts (new this round).** Rule: `git grep -nE '(^|[^A-Za-z0-9_./-])python3?([[:space:]]|$)' <rev> -- 'tools/audit/seat/*.sh' 'tools/pr/*.sh' | grep -vE '^[^:]*:[^:]*:[0-9]+:[[:space:]]*#'`.
  - It returns 153 lines in 20 files at this head and at `9629ae17`.
  - A child is long-lived when the program it runs polls. The test is `grep -cE 'time\.sleep|\.wait\(|while True'` on each module the lines name, and on the inline programs in the file. The modules that test returns non-zero for are `merge_train.py` (6), `tests/gate_lock.py` (28), `tests/closure.py` (1), `tests/layout.py` (1) and `tools/pr/contract_rerun.py` (1). The inline programs are `pr_args.sh`'s lock holder, `tick_loop.sh`'s `RELAY_HOLDER`, `train.sh`'s self-test stub, and `app_approve.sh`'s self-test `RUN_TIMEOUT_PY`. `ci_predict.py`, `ref_privacy.py`, `pr_cap.py`, `orchestrator_tick.py` and `gh_comment.py` each print 0.
  - Each file's disposition:
    - `open_pr.sh` (3 lines), `update_pr.sh` (1), `handoff_push.sh` (6), `remerge_main.sh` (1), `app_push.sh` (32): runners. Their reap walks every descendant, Python children included. Already guarded, and closed in this diff.
    - `train.sh` (3): its `merge_train.py` is long-lived and **closed in this diff**. Its other 2 lines are self-test refusal strings.
    - `pr_args.sh` (4): the branch-lock holder is long-lived by design. It is spared by the reap and ended by `PR_AFTER_REAP`, and it exits within 2 s of its parent's loss (`# mut:watch`). The other lines are self-test fixtures and `pr_cap.py --self-test`.
    - `tick_loop.sh` (2): `RELAY_HOLDER` is long-lived and detached by documented choice, as at level 2. `orchestrator_tick.py` is one read-only pass whose module prints 0 on the long-lived test.
    - `prepr.sh` (47): `gate_lock.py`'s slot wait, `closure.py`, `layout.py` and `contract_rerun.py` poll. When a pusher runs prepr, it runs asynchronously under that runner's reap (app_push's `bash "$prepr" … & prepr_pid=$!`). Run directly by a seat, a TERM leaves its foreground check running. **A distinct finding already routed**: R10-FLOW-JIDOKA's roster carry from #2528 (R10-PREPR-CAP) states this seam ("tools/pr/prepr.sh steps 3 to 3h run heavy work in the foreground, so a KILL or TERM to prepr during step 3h leaves the self-test or mutants drive running") and its fix shape.
    - `body_push.sh` (2), `bus.sh` (2), `ci_predict_replay.sh` (1), `merge_pr.sh` (4), `wt_sync.sh` (3), `app_comment.sh` (10), `approve_held_runs.sh` (3): finite. Each runs `ci_predict.py`, `ref_privacy.py`, `gh_comment.py` or an inline JSON filter, and each prints 0 on the long-lived test.
    - `app_approve.sh` (15): finite JSON filters, plus a self-test `RUN_TIMEOUT_PY` that bounds its own child with `p.wait(timeout=secs)`.
    - `cloud-setup.sh` (5) and `seat_venv.sh` (8): one-shot environment builds (`pip install`, `uv python install`, version reads) that run to completion.
    - `push.sh` (1): retired.
- **Self-tests at this head** (`PREPR_SKIP_CLOSURES=1`, each under `timeout 1500`):

  | command | result |
  |---|---|
  | `bash tools/audit/seat/open_pr.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `pr_args self-test: 90 checks, 0 failed` |
  | `bash tools/audit/seat/update_pr.sh --self-test` | the same two lines |
  | `bash tools/audit/seat/handoff_push.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `handoff_push self-test: 2 checks, 0 failed` |
  | `bash tools/pr/app_push.sh --self-test` | `app_push self-test: 186 checks, 0 failed` |
  | `bash tools/audit/seat/cloud_relay.sh --self-test` | `cloud_relay self-test: 83 checks, 0 failed` |
  | `python3 tools/audit/seat/merge_train.py --self-test` | `merge_train self-test: 200 checks, 0 failed` |
  | `bash tools/audit/seat/train.sh --self-test` | `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag, a stop reaps the tree, merge_train.py first)` |
  | `bash tools/audit/seat/tick_loop.sh --self-test` | `tick_loop self-test: 8 checks, 0 failed` |
- **The scoped gate.**
  - `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`.
  - `PYTHONPATH=tests/hastub python tests/entities.py` (python 3.13.16 with `tests/requirements-ci.txt`; this container has no 3.14) printed `1 of 2382 ENTITY CHECKS FAILED`. A clean worktree of origin/main `07fcbee2` printed the same line on the same interpreter. `diff <(grep -E '^\s*(ok|FAIL)' main.txt | sed 's/\[.*//') <(grep -E '^\s*(ok|FAIL)' head.txt | sed 's/\[.*//') > /dev/null && echo IDENTICAL-CHECK-SEQUENCE` printed `IDENTICAL-CHECK-SEQUENCE` over 2463 check lines. So the failure is main's on 3.13 and is not this diff's. CI's `fast (3.14)` is the run that decides it. At `9629ae17` (the same entities.py inputs; this diff touches no entities input) it concluded success.
- **Checks before push:**
  - `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed `Architecture score: dS +0.0000 NULL`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` printed `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
  - `python3 -I tests/throwaway_git.py --check` printed `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
  - `git diff $(git merge-base origin/main HEAD)...HEAD | grep -nE '^\+.*\bgit\b.*\b(init|clone)\b'` printed nothing (rc 1).
  - `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against 07fcbee2ed9e`.
- **prepr.** `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash tools/pr/prepr.sh <this body>` printed `PRE-PR: f1e7b88956f6da2407f0cadcf7c6cac1fa340e87 00010000000000000000000`. Its one REFUSE is the `policy_lint` step, main's budget red (`## Red checks`). `preflight` and `pr-body` printed ok, and figures printed `FIGURES: 27 resolved, 16 not verified, 0 refused`.
- **Rule 3 / rule 4.** `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E 'VERSION|manifest|RELEASE_NOTES|claimed_drift'` printed nothing (rc 1). `git diff --stat $(git merge-base origin/main HEAD)...HEAD` printed `10 files changed, 734 insertions(+), 77 deletions(-)`.
- **Carry.** `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` printed `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`.

## Red checks

Read per commit from the Actions runs API (`list_workflow_runs` on branch `fix/r10-pusher-reap`, 47 runs; then `list_workflow_jobs` for each failed `Tests` run). Every non-success conclusion, by commit:
- **`6fd073c9`.** `PR contract` failure, twice. `CodeQL`, `Governance` and `Tests` were cancelled by the newer push. That is `cancel-superseded`, not a red.
- **`50571afa`.** `PR contract` failure, twice: `carry_audit.py` refused 3 unrouted body items. `Tests` failure: the one failing job is `nightly-status`.
- **`c071fa5f`.** `PR contract` failure, twice: the same carry_audit refusal. `Tests` failure: the one failing job is `nightly-status`.
- **`9629ae17`.** `Tests` failure: the one failing job is `nightly-status` (step `Report the last scheduled run's conclusion`). Every other job is success or skipped.

Answers:
- **`pr-contract` at `6fd073c9`, `50571afa` and `c071fa5f`.** The body caused it, not the code: carry_audit refused unrouted items. A cheaper detector exists, `carry_audit.py`'s own `check --body`, which runs in seconds offline. It is run on this body before the push (`## Figures`, Carry). I am naming the trigger; its analysis belongs to `root-cause.md`'s seat.
- **`nightly-status` at `50571afa`, `c071fa5f` and `9629ae17`.** It reports the last scheduled run on `main`, not this branch. This diff (ten `tools/` and record files) does not reach anything it reads. No cheaper detector applies to a red this branch did not cause.
- **Predicted at this head: `policy_lint`'s budget cap.** prepr's `policy_lint` step refuses with `ERROR [budgets] tools/audit/briefs/orchestrator.md: about 4515 tokens across its lines exceeds its cap of 4513 tokens (files_tokens)`. A clean worktree of origin/main `07fcbee2` printed the same error and `TOTAL: 1 error(s) across 43 policy file(s)` from `node tools/policy/policy_lint.mjs`. `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -c orchestrator.md` printed 0, so the red is main's, not this diff's. I know of no fix for it to port. The file is policy, a change to it needs the owner's review, and this PR does not widen to it.
- This round's commits have no CI yet. The orchestrator's push is their first run.

## Forward-carry

- #2502's SIGKILL clause: "a TERM, INT, HUP or SIGKILL of a running update must not free the branch lock while its push still runs". This PR meets TERM, INT and HUP (the `heldrun` arm, plus the lead for a relay or a train above `update_pr.sh`). It does not meet SIGKILL. A SIGKILLed run runs no trap, and its holder exits within 2 s of losing its parent (`pr_branch_lock`'s getppid watch, `# mut:watch`), while the push that run started may still be running. Meeting it needs the holder to keep the lock until the run's former tree is gone, and that drain must be deterministic across containers. The group's own roster carry records that #2469's round-4 drain arm failed 7 of 7 runs in a container whose PID 1 reaps orphans late. So #2502 stays open after this PR, and the clause stays with the group that owns it. Roster append (the roster is frozen until #2588 merges), to `R10-UPDATE-PR-SIGNALS.carry`: "Revision (fixer, PR #2524 round 3): #2524 meets TERM/INT/HUP, including a runner above update_pr.sh (PR_REAP_LEAD); #2502 stays open. Owed: SIGKILL of a running update must not free the branch lock while its push still runs -- the holder keeps the lock until the run's former tree is gone, by a drain that waits on a condition, never a fixed window, and passes in a container whose PID 1 reaps late." And keep `resume.stage` at `in-progress` past #2524's merge. Carry: R10-UPDATE-PR-SIGNALS
- The roster's Revision-12 prevention item on this group: "every self-test runs under a timeout in its own process group, reaped on exit". This PR does not do it. The self-tests it touches are bounded only by their callers (CI's step timeout, or `timeout` in a seat's own run). A self-test whose own shell dies leaves whatever fixture process it started, which is the 8.6 h spin the revision names. Doing it for "every self-test" reaches files outside this group (merge_train.py, app_push.sh, prepr.sh's self-tests), and a process-group kill is a design question against `pr_kill`'s never-a-group rule, which a bound held inside the self-test's own shell may answer instead. Roster append, to `R10-UPDATE-PR-SIGNALS.carry`: "Still owed after #2524: the Revision-12 self-test isolation (a timeout and a reap on exit for every self-test); #2524 did not build it." Carry: R10-UPDATE-PR-SIGNALS

## Friction

none

