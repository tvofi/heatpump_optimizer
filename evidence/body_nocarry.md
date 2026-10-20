RCA, the vanishing update worktree. It occurred 2026-10-19 ~22:10Z on `fix/r10-deeplink-handlers` and 2026-10-20 ~00:03Z on `fix/r10-ci-layout-p0`, and recurred a third time at 01:32Z on #2471. This PR makes three changes:

- `update_pr.sh` takes a per-branch kernel lock, held by one holder process.
- A second run on a branch whose update is still going exits 75 (BUSY) and changes nothing.
- `cloud_relay.sh`'s handoff arm treats 75 as "retry on the next pass", and writes the body it hands over somewhere prepr accepts.

**Mechanism.** `update_pr.sh` keeps one worktree and one log per branch at fixed paths: `$HPO_STATE_DIR/pr/upd-<branch>` and `upd-<branch>.log` (`tools/audit/seat/update_pr.sh:23` at the base). At the base, line 35 (`[ -d $WT ] && git worktree remove --force $WT`) runs at the start of every run and does not check whether another run is using the worktree. Line 36 then adds it back. So a second update of the same branch force-removes the first run's worktree while the first run's `app_push.sh` → `prepr.sh` is working inside it. The first run then fails in one of two ways:
- Its cwd is a deleted inode: `fatal: Unable to read current working directory`, plus node crash tails.
- Its relative `tools/...` paths point into a deleted or half-repopulated checkout: `can't open file 'tools/policy/agreement_py.py'`, `bash: tools/pr/prepr.sh: No such file or directory`, `no pinned grader found`.

**Who the second run was.** It was the handoff arm of `cloud_relay.sh pass`, which `tick_loop.sh` runs every tick (`tools/audit/seat/cloud_relay.sh:199-200` at the base). For each open PR whose `handoff/<topic>` is not inside the PR head, the arm runs `update_pr.sh <branch> <code-sha> <BODY.md>`. That is exactly the state of a PR the orchestrator is about to update by hand. So whenever the relay fires during a manual update of a handoff PR, the two runs overlap. The relay's records match the incidents:
- `cloud-handoff-failed` lists exactly the incident topics: `r10-policy-instruments`, `r10-deeplink-handlers`, `r10-setpoint-boost`, `r10-ci-layout-p0`.
- Its log has `OWED 2026-10-19T22:07:48Z handoff-update 2452 r10-deeplink-handlers …` and `OWED 2026-10-20T00:04:16Z handoff-update 2464 r10-ci-layout-p0 …`, minutes from the incidents.

**Why the relay's update never succeeded, and the body path.** The relay wrote the body it hands to `update_pr.sh` with `mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX"`, a file directly in a shared temp root (`cloud_relay.sh:197` at the base). prepr's body-path check (`shared_root`) refuses exactly that: `REFUSE body path …/T/cloud_body.… sits directly in a root other seats write to`. So every relay update failed at prepr: #2469 at 01:19Z and #2471 at 01:32Z. Each one still raced, and removed the worktree of, the manual run it overlapped. Both runs also redirect their push into the same `upd-<branch>.log` (`update_pr.sh:58` at the base). That is why the log the orchestrator read for its own update (body `…/upd/b2464/body.md`) showed the relay run's prepr, which names `$TMPDIR/cloud_body.*`.

**Suspects cleared.**
- `worktree_gc.sh` removes a branch worktree only on an API-read MERGED pull request (class A), and a detached one only when it is clean, a proper ancestor of main and older than an hour (class B). An open PR's `upd-` worktree is kept.
- `merge_train.py --free-holders` only detaches a clean holder, and the holder's files stay.
- `state_docs.py` and `roster_edit.py` use their own worktrees.
- `git worktree prune` drops only entries whose directory is already gone.

**Fix.**
- **The lock.** `update_pr.sh` starts one holder process (`python3 -I`; macOS has no `flock(1)`). The holder opens `upd-<branch>.lock`, takes `flock(LOCK_EX|LOCK_NB)`, writes `<run pid> <holder pid>` and waits. The run goes on only after it reads its own two pids back, which happens before any fetch or worktree change. When the lock is held, the holder exits 75, and the run prints `update_pr: BUSY: another update_pr.sh run (pid N) …` and exits 75 having changed nothing. Any other holder failure is a REFUSE.
- **A holder, not a shell fd (round 1).** The round-0 lock was an fd of the run's shell. Every command the run starts inherits such an fd, and a `git gc --auto` that git detaches kept the lock after the run ended, so the next run saw a false BUSY naming a dead pid. The holder's file is non-inheritable (PEP 446) and the holder starts nothing, so no child of the run can hold the lock. The kernel frees the lock when the holder dies, and the holder dies with the run in either of two ways:
  - The run's EXIT trap kills and reaps it.
  - It exits by itself within 2 s once its parent is gone, which covers a SIGKILLed run.

  A BUSY whose recorded run pid is dead says so: `the lock holder of run N, which has ended (the holder exits within 2 s)`.
- **The relay.** `cloud_relay.sh` writes BODY.md into a directory of its own per run, `mktemp -d "$state/cloud-body.XXXXXX"` under its state dir, and removes it on every path. An rc of 75 is not written to `cloud-handoff-failed`, and the arm retries it on its next pass. Every other non-zero rc is handled as before.
- **A relay run against a manual run.** Both runs resolve the worktree and the lock from the same `$HPO_STATE_DIR/pr/upd-<branch>`. So whenever the two share a worktree, they share the lock. Probed in both orders with the real scripts: the relay's `cloud_relay.sh pass` running the real `update_pr.sh`, against a manual `update_pr.sh` on one branch. The run that starts second exits 75, and the first keeps its worktree. Until this merges, the relay runs main's lockless copy, so the race stands until then.
- **`tools/pr/prepr.sh` step 7a2.** It runs pr-contract's own carry check on the body (see Red checks).
- **Alternatives not taken.**
  - A unique worktree path per run stops the removal, but two runs would still merge and push one branch at once.
  - A `mkdir` lock with pid stealing has a check-then-steal race.
  - Setting `gc.autoDetach=false` would fix only the one child git is known to detach.
- **Residual, not this incident's class.** A SIGKILL of the `update_pr.sh` shell's pid alone orphans its running push, and the lock is freed within 2 s while that push may still be running.

## Head

`2351c1c7bb6d71e455a7fd164f42f67091491d0f` merges the authored code head `28c7c454abd087e62365ec9239f4157dd68a0358` and then merges origin/main `52011c69a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`28c7c454abd087e62365ec9239f4157dd68a0358` is the code head (round 1's was `75a05f3baa16f13b0bb261f3ed2729f4f26f67cf`, round 0's `49577add8c4df47aa24124727fd2f6e250f3434f`), at origin/main `2bd48adfab7e5beb27c55ce7572de41d64465145`. `git merge-tree --write-tree origin/main 28c7c454abd087e62365ec9239f4157dd68a0358` is clean.

## Mutation proof

- `bash tools/audit/seat/pr_args.sh --self-test`, through the harness's line-deletion mutants on a copy of `update_pr.sh`:
  - `# mut:lock` (the line that refuses an unlocked run): `ok     mutant mut:lock (its line deleted) removes the in-flight run's worktree`.
  - `# mut:unlock` (the EXIT trap that ends the holder): `ok     mutant mut:unlock (its line deleted): the holder outlives the run and the next run is BUSY`.
- Test first, on the head's `pr_args.sh`:
  - With round 0's `update_pr.sh` (the shell-fd lock): `FAIL update_pr: a child the run left detached does not hold the lock; the next run on the branch reaches its push` and `pr_args self-test: 51 checks, 1 failed`. This reproduces the round-1 finding: the arm's post-checkout hook leaves a detached `sleep` that inherited the lock fd.
  - With origin/main's `update_pr.sh` (no lock): `FAIL update_pr: a branch whose update is in flight refuses BUSY (75) and leaves that run's worktree in place` and `pr_args self-test: 51 checks, 2 failed`.
- `cloud_relay.sh` mutants, each on a copy:
  - The body written as at the base (`body=$(mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX")`): `FAIL the body update_pr gets passes prepr's body-path check (not directly in a shared root)` and `FAIL and that body's directory is removed after the update`, `cloud_relay self-test: 74 checks, 2 failed`. The same result with `TMPDIR` unset, as on CI. The arm reads `shared_root` from `tools/pr/prepr.sh` itself.
  - The final `rm -rf "$bd"` deleted: `FAIL and that body's directory is removed after the update`, `74 checks, 1 failed`.
  - The `if [ "$urc" = 75 ]` line deleted: `FAIL a busy update is tried again on the next pass`, `FAIL and is not recorded failed`, `FAIL nor logged OWED`.
- Reproductions outside the self-tests, offline: a scratch origin, `gh` stubbed, and an `app_push.sh` stub that sleeps 6 s in the worktree.
  - Two manual runs on one branch, B started 2 s after A. At origin/main: `run A: cwd LOST: fatal: Unable to read current working directory: No such file or directory`, the 22:10Z incident's message. At the head: `B rc=75`, `update_pr: BUSY: another update_pr.sh run (pid …)`, `run A: cwd intact`.
  - Manual first, then a real `cloud_relay.sh pass`: the relay printed `update_pr: BUSY: …` and `cloud_relay: update_pr busy on fix/x; the next pass retries`. The manual run kept `cwd intact`, `cloud-handoff-failed` stayed empty, and no `cloud-body.*` directory was left.
  - Relay first, then a manual run: `manual rc=75` with BUSY, and the relay run kept `cwd intact`.
  - SIGKILL: A was killed by `kill -9` mid-push. A run started 0.2 s later saw `BUSY: the lock holder of run …, which has ended (the holder exits within 2 s)`, and a run 2.5 s later took the lock.

## Null control

- `null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push`.
- The detached-child arm's first and second runs both reach their push (`update_pr: REFUSE: the push failed`, the fixture's offline stop).
- The two existing null controls (`update_pr with code sha … passes every check, and its failed push names its log`) still pass with the lock in the path.
- `cloud_relay.sh`'s existing arms still pass: a handoff with no body ref does nothing, the body handed over is the handoff-body BODY.md, and an rc-1 update is tried once and logged OWED.

## Figures

- `bash tools/audit/seat/update_pr.sh --self-test`: `delivery_row self-test: 5 checks, 0 failed` and `pr_args self-test: 51 checks, 0 failed`. origin/main has 46 checks. The 5 new checks are the BUSY arm and its mutant, the dead-run null, and the detached-child arm and its mutant.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 74 checks, 0 failed`. origin/main has 69. The 5 new checks are the two BUSY-retry checks, the not-recorded check, the body-path check and the body-cleanup check.

## Red checks

- `pr-contract` failed in check-runs 118384716655 and 118384845043 on round 0's PR head `d2d361a449f0356f877e49a7ff59521f33739c37`, read from the check-runs API. Every other completed run on that head was success or skipped.
  - Cause: `carry_audit.py check` read round 0's `## Forward-carry` as an item (`UNROUTED … (## Forward-carry)`), because a sentence followed `none`.
  - Repair: the section now reads `none` alone.
- Cheaper detector: prepr ran no carry check, and round 0 edited the body after prepr passed. This PR adds `tools/pr/prepr.sh` step 7a2, which runs `python3 -I tools/audit/carry_audit.py check --body <body>`, the command pr-contract runs last, at the cost of one python spawn per body. Its first run here refused this body's own draft (`UNROUTED body item 94936287 [lead]`, the residual above, routed since). This body is checked by prepr as published, with no edit after the run.

## Forward-carry

none

## Friction

none
