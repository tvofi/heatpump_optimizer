RCA, the vanishing update worktree. It hit 2026-10-19 ~22:10Z on `fix/r10-deeplink-handlers` and 2026-10-20 ~00:03Z on `fix/r10-ci-layout-p0`, and recurred at 01:32Z on #2471.

What this PR changes:
- `update_pr.sh` takes a per-branch kernel lock, held by one holder process, and keeps it until nothing the run started is still running: after a normal end, a stop (TERM, INT, HUP) or a SIGKILL.
- A second run on that branch exits 75 (BUSY) and changes nothing.
- `cloud_relay.sh`'s handoff arm reads 75 as "retry on the next pass", and writes the body it hands over somewhere prepr accepts.

**Mechanism.** `update_pr.sh` keeps one worktree and one log per branch, at fixed paths: `$HPO_STATE_DIR/pr/upd-<branch>` and `upd-<branch>.log` (`tools/audit/seat/update_pr.sh:23` at the base). At the base, line 35 (`[ -d $WT ] && git worktree remove --force $WT`) runs at the start of every run and never asks whether another run is using that worktree. Line 36 then adds it back. So a second update of the same branch force-removes the first run's worktree while the first run's `app_push.sh` → `prepr.sh` works inside it. The first run then fails in one of two ways:
- its cwd is a deleted inode: `fatal: Unable to read current working directory`, plus node crash tails;
- its relative `tools/...` paths now point into a deleted or half-repopulated checkout: `can't open file 'tools/policy/agreement_py.py'`, `bash: tools/pr/prepr.sh: No such file or directory`, `no pinned grader found`.

**Who the second run was.** It was the handoff arm of `cloud_relay.sh pass`, which `tick_loop.sh` runs every tick (`tools/audit/seat/cloud_relay.sh:199-200` at the base). For each open PR whose `handoff/<topic>` is not inside the PR head, the arm runs `update_pr.sh <branch> <code-sha> <BODY.md>`. That is exactly the state of a PR the orchestrator is about to update by hand, so a relay pass that fires during such an update overlaps it. The relay's own records match the incidents:
- `cloud-handoff-failed` lists exactly the incident topics: `r10-policy-instruments`, `r10-deeplink-handlers`, `r10-setpoint-boost`, `r10-ci-layout-p0`.
- Its log has `OWED 2026-10-19T22:07:48Z handoff-update 2452 r10-deeplink-handlers …` and `OWED 2026-10-20T00:04:16Z handoff-update 2464 r10-ci-layout-p0 …`, minutes from the incidents.

**Why the relay's update never succeeded, and the body path.**
- The relay wrote the body it hands to `update_pr.sh` with `mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX"` (`cloud_relay.sh:197` at the base). That is a file directly in a shared temp root, which prepr's body-path check (`shared_root`) refuses: `REFUSE body path …/T/cloud_body.… sits directly in a root other seats write to`.
- So every relay update failed at prepr: #2469 at 01:19Z, #2471 at 01:32Z. Each one still raced the manual run it overlapped and removed that run's worktree.
- Both runs also send their push output to the same `upd-<branch>.log` (`update_pr.sh:58` at the base). That is why the log the orchestrator read for its own update (body `…/upd/b2464/body.md`) showed the relay run's prepr naming `$TMPDIR/cloud_body.*`.

**Suspects cleared.**
- `worktree_gc.sh` removes a branch worktree only on an API-read MERGED pull request (class A). It removes a detached one only when it is clean, a proper ancestor of main and older than an hour (class B). An open PR's `upd-` worktree is kept.
- `merge_train.py --free-holders` only detaches a clean holder; the holder's files stay.
- `state_docs.py` and `roster_edit.py` use their own worktrees.
- `git worktree prune` drops only entries whose directory is already gone.

**Fix: the lock.**
- `update_pr.sh` starts one holder process (`python3 -I`; macOS has no `flock(1)`). The holder opens `upd-<branch>.lock`, takes `flock(LOCK_EX|LOCK_NB)`, writes `<run pid> <holder pid>`, and waits.
- The run goes on only once it reads its own two pids back, before any fetch or worktree change.
- If the lock is held, the holder exits 75, and the run prints `update_pr: BUSY: another update_pr.sh run (pid N) …` and exits 75 having changed nothing. Any other holder failure is a REFUSE.

**Fix: no fd of the run's shell (round 1).** The round-0 lock was an fd of the run's shell, which every command the run starts inherits. A `git gc --auto` that git detached kept that lock after the run ended. The holder's file is non-inheritable (PEP 446), so no child of the run holds the lock.

**Fix: the lock outlives everything the run started (round 2).** `kill <pid>`, `daemonize.py`'s documented stop, freed the round-1 lock at once through the EXIT trap, while the push ran on in `$WT`. Now:
- Every run leads its own process group. A run that is not a group leader re-execs itself under `setpgid(0, 0)`; an interactive shell's job and a `daemonize.py` session already lead one.
- The holder moves to a group of its own, so the run's group is exactly what the run started and has not ended. git's detached gc calls `setsid` and leaves the group, so it holds nothing.
- The push runs in the background under `wait`, so a trapped signal reaches the run at once. Without that, it would wait for a foreground push to finish.
- A normal end: the EXIT trap ends the holder, and the push has already been waited for.
- TERM, INT or HUP: `upd_stop` ignores further stop signals and sends USR2 to the holder. The holder TERMs the run's group (`killpg`), acknowledges, and holds the lock until no process of that group is left (zombies excepted). The run then exits 143.
- SIGKILL, which no trap sees: the holder notices that its parent is gone and does the same wait.
- A BUSY whose recorded run has ended says so: `the lock holder of run N, which has ended but started processes that have not`.

**Fix: the relay.**
- `cloud_relay.sh` writes BODY.md into a per-run directory under its own state dir (`mktemp -d "$state/cloud-body.XXXXXX"`) and removes it on every path.
- An rc of 75 is not written to `cloud-handoff-failed`, and the arm retries on its next pass. Every other non-zero rc is handled as before.

**A relay run against a manual run.** Both runs resolve the worktree and the lock from the same `$HPO_STATE_DIR/pr/upd-<branch>`, so whenever they share a worktree they share the lock. I probed both orders with the real scripts: `cloud_relay.sh pass` running the real `update_pr.sh`, and a manual `update_pr.sh`, on one branch. In each order the run that starts second exits 75, and the first keeps its worktree. Until this merges, the relay runs main's lockless copy.

**Also: `tools/pr/prepr.sh` step 7a2.** It runs pr-contract's carry check on the body; see Red checks.

**Alternatives not taken.**
- A unique worktree path per run: it stops the removal, but two runs would still merge and push one branch at once.
- A `mkdir` lock with pid stealing: it has a check-then-steal race.
- `gc.autoDetach=false`: it fixes only the one child git is known to detach.
- Reading the run's process tree instead of its group: a tree read up to a second old misses a child started just before a SIGKILL, and the round-2 draft of this fix failed its own SIGKILL arm that way. A group needs no snapshot.

## Head

`89f329f6ba7928b51feb29e7a8d4ac7e7c14b0fc` merges the authored code head `a3af24fcf08562d07bd2aaa43cf8cf08eab00e4c` and then merges origin/main `bb5b21a88` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`a3af24fcf08562d07bd2aaa43cf8cf08eab00e4c` is the code head; earlier rounds were `28c7c454abd087e62365ec9239f4157dd68a0358` (2), `75a05f3baa16f13b0bb261f3ed2729f4f26f67cf` (1) and `49577add8c4df47aa24124727fd2f6e250f3434f` (0). origin/main is `bb5b21a88f82e3bcfd1f0a0fdd2ba351aa665703`, and `git merge-tree --write-tree origin/main a3af24fcf08562d07bd2aaa43cf8cf08eab00e4c` is clean.

## Mutation proof

`bash tools/audit/seat/pr_args.sh --self-test`: the harness's line-deletion mutants on a copy of `update_pr.sh` each fail their arm, which the harness prints as `ok`:
- `# mut:lock` (the line refusing an unlocked run): `mutant mut:lock (its line deleted) removes the in-flight run's worktree`.
- `# mut:unlock` (the EXIT trap): `mutant mut:unlock (its line deleted): the holder outlives the run and the next run is BUSY`.
- `# mut:stop` (the TERM/INT/HUP trap): `mutant mut:stop (its line deleted): a TERMed run frees the lock while its push still runs`.
- `# mut:drain` (the holder's wait for the group): `mutant mut:drain (its line deleted): a SIGKILLed run frees the lock while its push still runs`.
- `# mut:pgrp` (the re-exec into the run's own group): `mutant mut:pgrp (its line deleted): the run shares its caller's group, and the lock goes under a live push`.

The new stop arms use branch `fix/t`, whose push stub lingers 2 s when TERMed and otherwise ends after 6 s. Run 1 is signalled mid-push, then:
- run 2 starts at once after a TERM, or 3 s after a SIGKILL, past round 2's 2-s self-exit, and must be BUSY;
- run 3 starts after the stub has ended, and must take the lock.

The round-2 review's surviving mutant, the holder's parent watch replaced by `while True`, now fails `update_pr: a SIGKILLed run's lock is held until the push it started has ended; then the next run takes it` (`pr_args self-test: 56 checks, 3 failed`).

Test first, with the head's `pr_args.sh`:
- Round 2's `update_pr.sh`: `FAIL update_pr: a TERMed run (daemonize.py's stop) keeps the lock until its push has ended; then the next run takes it` and `FAIL update_pr: a SIGKILLed run's lock is held …`, `56 checks, 2 failed`.
- origin/main's `update_pr.sh`: those two, plus `FAIL update_pr: a branch whose update is in flight refuses BUSY (75) …` and `FAIL   mutant mut:unlock …`, `56 checks, 4 failed`.

`cloud_relay.sh` mutants, each on a copy:
- The body written as at the base: `FAIL the body update_pr gets passes prepr's body-path check (not directly in a shared root)` and `FAIL and that body's directory is removed after the update`, `74 checks, 2 failed`. The same with `TMPDIR` unset.
- The final `rm -rf "$bd"` deleted: `74 checks, 1 failed`.
- The `if [ "$urc" = 75 ]` line deleted: `FAIL a busy update is tried again on the next pass`, `FAIL and is not recorded failed`, `FAIL nor logged OWED`.

Offline reproductions with the real scripts (a scratch origin, `gh` stubbed, a push stub sleeping in the worktree):
- **`daemonize.py` stop (the round-2 finding).** A started under `daemonize.py`, then `kill <printed pid>` mid-push. A was gone 0.3 s later (`run alive? no`), its push printed `push TERMed, finishing`, and B started then got `rc=75` with `BUSY: the lock holder of run …, which has ended but started processes that have not`. Once the push printed `push ended`, C took the lock (`rc=0`).
- **SIGKILL.** `kill -9` mid-push: runs 0.2 s and 2.5 s later both got `rc=75` while the push still ran.
- **Two manual runs.** At origin/main: `run A: cwd LOST: fatal: Unable to read current working directory: No such file or directory`. At the head: `B rc=75`, `run A: cwd intact`.
- **Relay against manual, both orders.** The second run is BUSY, the first keeps `cwd intact`, `cloud-handoff-failed` stays empty, and no `cloud-body.*` directory is left.

## Null control

- `null control: a lock left by a dead run (the kernel freed it) does not block; the run reaches its push`.
- In each stop arm, run 3 (started after the push ended) takes the lock and reaches its push.
- The detached-child arm's two runs both reach their push (`update_pr: REFUSE: the push failed`, the fixture's offline stop).
- The existing `update_pr with code sha … passes every check, and its failed push names its log` null controls pass with the lock in the path.
- `cloud_relay.sh`'s existing arms (no body ref does nothing; the body handed over is the handoff-body BODY.md; an rc-1 update is tried once and logged OWED) pass.
- `pr_args.sh --self-test` passed on each of 4 consecutive runs at the head.

## Figures

- `bash tools/audit/seat/update_pr.sh --self-test`: `delivery_row self-test: 5 checks, 0 failed`, `pr_args self-test: 56 checks, 0 failed`. origin/main: 46 checks. The 10 new checks:
  - the BUSY arm and its mutant;
  - the dead-run null;
  - the detached-child arm and its mutant;
  - the TERM arm and its mutant;
  - the SIGKILL arm and its two mutants.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 74 checks, 0 failed`. origin/main: 69.

## Red checks

- `pr-contract` failed on round 0's heads `02369b10` (check-runs 118384376991, 118384517187) and `d2d361a449f0356f877e49a7ff59521f33739c37` (118384716655, 118384845043), read from the check-runs API.
  - Cause: `carry_audit.py check` read round 0's `## Forward-carry` as an item (`UNROUTED … (## Forward-carry)`), because a sentence followed `none`.
  - Repair: the section reads `none` alone.
  - Round 2's head `2351c1c7` had no red run.
- Cheaper detector: prepr ran no carry check, and round 0 edited the body after prepr passed. This PR adds `tools/pr/prepr.sh` step 7a2, which runs `python3 -I tools/audit/carry_audit.py check --body <body>`, the command pr-contract runs last. It costs one python spawn per body. This body went through prepr as published, with no edit after the run.

## Forward-carry

none

## Friction

none
