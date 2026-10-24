RCA, the vanishing update worktree (recurred twice: 2026-10-19 ~22:10Z on `fix/r10-deeplink-handlers`, 2026-10-20 ~00:03Z on `fix/r10-ci-layout-p0`). `update_pr.sh` now takes a per-branch kernel lock held by one holder process, and a second run on a branch whose update is still going exits 75 (BUSY) having changed nothing. `cloud_relay.sh`'s handoff arm reads 75 as "retry on the next pass", not as a failure.

**Mechanism.** `update_pr.sh` keeps one worktree and one log per branch at fixed paths, `$HPO_STATE_DIR/pr/upd-<branch>` and `upd-<branch>.log` (`tools/audit/seat/update_pr.sh:23` at the base). Line 35 at the base, `[ -d $WT ] && git worktree remove --force $WT`, runs at the start of every run, and nothing checks whether another run is still using that worktree. Line 36 then adds it again. A second update of the same branch therefore force-removes the first run's worktree while the first run's `app_push.sh` → `prepr.sh` is running inside it. The first run then reads its cwd from a deleted inode (`fatal: Unable to read current working directory`, plus node crash tails), or it reads relative `tools/...` paths in a checkout that has been deleted or is still half re-populated (`can't open file 'tools/policy/agreement_py.py'`, `bash: tools/pr/prepr.sh: No such file or directory`, `no pinned grader found`).

**Who the second run was.** It was `cloud_relay.sh pass`'s handoff arm (`tools/audit/seat/cloud_relay.sh:199-200` at the base), which `tick_loop.sh` runs every tick. For every open PR whose `handoff/<topic>` is not inside the PR head, the arm runs `update_pr.sh <branch> <code-sha> <tmp BODY.md>`. That is exactly the state of a PR the orchestrator is about to update by hand, so a manual update of a handoff PR overlaps a relay pass whenever the relay fires during it (four topics in about two hours, per the ledger below). The relay's own failure ledger, `cloud-handoff-failed`, lists exactly the incident topics (`r10-policy-instruments`, `r10-deeplink-handlers`, `r10-setpoint-boost`, `r10-ci-layout-p0`). Its log has `OWED 2026-10-19T22:07:48Z handoff-update 2452 r10-deeplink-handlers …` and `OWED 2026-10-20T00:04:16Z handoff-update 2464 r10-ci-layout-p0 …`, minutes from the two incidents.

**The body path.** The relay writes the body it hands to `update_pr.sh` with `mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX"` (`cloud_relay.sh:197`). Both runs redirect their push to the same `upd-<branch>.log` (`update_pr.sh:58` at the base). So the log the orchestrator read for its own run (body `…/upd/b2464/body.md`) held the relay run's prepr output, and that output names `$TMPDIR/cloud_body.*`. The relay's prepr was the one whose worktree the orchestrator's later run removed, which is why the body-path refusal and the missing-file REFUSE lines appear together.

**Suspects cleared.** `worktree_gc.sh` removes a branch worktree only when an API read shows a MERGED pull request (class A), and removes a detached worktree only when it is clean, a proper ancestor of main and older than an hour (class B). An open PR's `upd-` worktree is a branch worktree with an open PR, so it is kept. `merge_train.py --free-holders` only detaches a clean holder (`free_holder`) and leaves its files where they are. `state_docs.py` and `roster_edit.py` work in their own worktrees. `git worktree prune` only prunes entries whose directory is already gone.

**Fix.**
- `update_pr.sh` starts one holder process (`python3 -I`; macOS has no `flock(1)`) that opens `upd-<branch>.lock`, takes `flock(LOCK_EX|LOCK_NB)`, writes `<run pid> <holder pid>` and waits. The run goes on only once it reads its own two pids back, which happens before any fetch or worktree change. If the lock is held, the holder exits 75, and the run prints `update_pr: BUSY: another update_pr.sh run (pid N) …` and exits 75 having changed nothing. Any other holder failure is a REFUSE.
- **Why a holder, not a shell fd (round 1).** The round-0 lock was an fd of the run's shell, and every command the run starts inherits such an fd. A `git gc --auto` that git detaches kept the lock after the run ended, so the next run got a false BUSY naming a dead pid. The holder's file is non-inheritable (PEP 446), and the holder starts nothing, so no child of the run can hold the lock. The kernel frees the lock when the holder dies, and the holder dies with the run: the run's EXIT trap kills and reaps it, and it also exits by itself within 2 s once its parent is gone (a SIGKILLed run). A BUSY whose recorded run pid is dead says so: `the lock holder of run N, which has ended (the holder exits within 2 s)`.
- `cloud_relay.sh`: rc 75 is not written to `cloud-handoff-failed`, and the arm retries on its next pass. Every other non-zero rc is handled as before.
- Alternatives not taken:
  - A unique worktree path per run stops the removal, but two runs would still merge and push one branch at once.
  - A `mkdir` lock with pid stealing has a check-then-steal race.
  - Turning off `gc.autoDetach` would fix only the one child git is known to detach.
- Residual, not this incident's class: a SIGKILL of the `update_pr.sh` shell's pid alone orphans its running push, and the lock is freed within 2 s while that push may still be running. Carry: dismissed: daemonize.py runs every detached update as a session leader, so a kill of its group ends the push with it, and neither incident involved a kill

## Head

`a0273d930bd126f6378d04e7ed61a92f8ba8a505` merges the authored code head `75a05f3baa16f13b0bb261f3ed2729f4f26f67cf` and then merges origin/main `2bd48adfa` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`75a05f3baa16f13b0bb261f3ed2729f4f26f67cf` (the code head; round 0's was `49577add8c4df47aa24124727fd2f6e250f3434f`), origin/main `2bd48adfab7e5beb27c55ce7572de41d64465145`; `git merge-tree --write-tree origin/main 75a05f3baa16f13b0bb261f3ed2729f4f26f67cf` is clean.

## Mutation proof

- `bash tools/audit/seat/pr_args.sh --self-test` uses the harness's line-deletion mutants on a copy of `update_pr.sh`:
  - `# mut:lock` (the line that refuses an unlocked run): `ok     mutant mut:lock (its line deleted) removes the in-flight run's worktree`.
  - `# mut:unlock` (the EXIT trap that ends the holder): `ok     mutant mut:unlock (its line deleted): the holder outlives the run and the next run is BUSY`.
- Test first, on the head's `pr_args.sh`:
  - With round 0's `update_pr.sh` (the shell-fd lock): `FAIL update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push`, `pr_args self-test: 51 checks, 1 failed`. That is the reviewer's finding reproduced: the arm's post-checkout hook leaves a detached `sleep` that inherited the lock fd.
  - With origin/main's `update_pr.sh` (no lock): `FAIL update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place`, `pr_args self-test: 51 checks, 2 failed`.
- `cloud_relay.sh` with the `if [ "$urc" = 75 ]` line deleted: `FAIL a busy update is tried again on the next pass`, `FAIL and is not recorded failed`, `FAIL nor logged OWED`, `cloud_relay self-test: 72 checks, 3 failed`.
- Reproduction outside the self-tests: two real `update_pr.sh` runs on one branch, offline (scratch origin, `gh` stubbed, an `app_push.sh` stub that sleeps 6 s in the worktree, B started 2 s after A).
  - At origin/main: `run A: cwd LOST: fatal: Unable to read current working directory: No such file or directory`, the 22:10Z incident's message.
  - At the head: `B rc=75` with `update_pr: BUSY: another update_pr.sh run (pid …)`, and `run A: cwd intact`, `A rc=0`.
  - SIGKILL probe: A was killed by `kill -9` mid-push. A run started 0.2 s later got `BUSY: the lock holder of run …, which has ended (the holder exits within 2 s)`, and a run 2.5 s later took the lock.

## Null control

- `null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push`.
- The detached-child arm's first run and second run both reach their push (`update_pr: REFUSE: the push failed`, the fixture's offline stop).
- The two existing null controls (`update_pr with code sha … passes every check, and its failed push names its log`) still pass with the lock in the path.
- `cloud_relay.sh`'s existing rc-1 arms (`a failed update is tried once`, `and logs OWED handoff-update`) are unchanged and pass.

## Figures

- `bash tools/audit/seat/update_pr.sh --self-test`: `delivery_row self-test: 5 checks, 0 failed`, `pr_args self-test: 51 checks, 0 failed` (origin/main: 46 checks; the 5 new checks are the BUSY arm and its mutant, the dead-run null, and the detached-child arm and its mutant).
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 72 checks, 0 failed` (origin/main: 69).

## Red checks

- `pr-contract` (check-runs 118384716655 and 118384845043 on round 0's PR head `d2d361a449f0356f877e49a7ff59521f33739c37`, read from the check-runs API; every other completed run on that head was success or skipped). Cause: `carry_audit.py check` read round 0's `## Forward-carry` as an item (`UNROUTED … (## Forward-carry)`), because a sentence followed `none`. Repair: the section now reads `none` alone.
- Cheaper detector: prepr did not run the carry check. Round 0 edited the body after prepr passed, and prepr has no step that runs `carry_audit.py check` (the step this body was first going to name). This PR folds one in: `tools/pr/prepr.sh` step 7a2 runs `python3 -I tools/audit/carry_audit.py check --body <body>`, the command pr-contract runs last. It costs one python spawn per body. The step's first run on this body refused this section's own first draft (`UNROUTED body item 94936287 [lead]`, the residual above, routed since).

## Forward-carry

none

## Friction

none
