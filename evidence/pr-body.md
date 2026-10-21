# Summary

`open_pr.sh` opens a PR with its first push, commits the PR's own delivery row, and pushes a second time. On 2026-10-21 that second push was refused on #2547 and #2548 (and #2549 is left without a row too), so `bus.sh dispatch` refused their reviewers. The refusal is `app_push.sh`'s head check: `worktree HEAD (41fd99b0...) is not the committed tip of 'fix/r10-replay-cap' (daac94b4...)`.

**Cause (measured with git, not the error text).** The error text suggests a stale local branch. The reflogs and lock files say the writer of that state was `update_pr.sh`:

- #2548: the PR worktree's reflog has `commit: record: the delivery row for #2548` at 12:15:36 on the branch, then `checkout: moving from fix/r10-replay-cap to HEAD` (a detach) at 12:26:31. `upd-fix-r10-replay-cap.lock` was written at 12:26:29, two seconds before.
- #2547: row commit 11:58:53, detach 12:05:21, `upd-fix-r10-tick-owed-level.lock` written 12:05:19.
- The detach is `update_pr.sh`'s line that detaches every clean worktree under the state root holding the branch, then `git worktree add -B <branch> <its own worktree> origin/<branch>`, which moves the local branch to origin's head (or to the update's own row commit, `90bab078d` on #2547). The PR worktree's HEAD is then a detached commit that is not the branch tip, so the row's push is refused.
- `open_pr.sh` held no lock; `update_pr.sh` took `upd-<branch>.lock` for its own worktree only. `cloud_relay.sh` runs `update_pr.sh` when a handoff is ahead of its PR, which is how it ran minutes after the PR opened.
- #2549 shows no detach (its worktree is on the branch with the row commit as tip); its `p2.log` stops in the middle of prepr, so its original stop is not established here. This fix addresses the two instances whose evidence names the cause.

**Fix (two layers).**
1. `open_pr.sh` takes the same per-branch lock as `update_pr.sh` (`upd-<branch>.lock`), from before its worktree until it returns, so an `update_pr.sh` that starts in between exits 75 BUSY and changes nothing (`cloud_relay.sh` already retries 75 on its next pass). The lock code moved out of `update_pr.sh` into `pr_args.sh`'s `pr_branch_lock` (both scripts source it), so there is one copy.
2. `update_pr.sh` no longer detaches a worktree whose HEAD origin lacks: it refuses, naming the worktree. Before, the detach plus `-B` silently dropped any unpushed commit a sibling instrument held. A clean worktree whose HEAD is on origin is detached as before.

No `VERSION`, claim file or budget is touched.

## Head

`f8694ba2d73595da723f0de3ed78c3e05df78b3d` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2560.md`. The authored code head is `e8bf2f03d94b50c035e5e92c8c77bad03417df44`.

`90d21fe9709a7a53f75cad66fcb14ec337886e75` merges origin/main `03b49e152` into the authored code head `e8bf2f03d94b50c035e5e92c8c77bad03417df44` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

The code head is `e8bf2f03d94b50c035e5e92c8c77bad03417df44` (branch `fix/r10-openpr-row-push`, one commit on `origin/main` at `43f79c08b`).

## Mutation proof

The self-test (`bash tools/audit/seat/open_pr.sh --self-test`, which runs `pr_args.sh`'s after `delivery_row.sh`'s) builds a scratch origin and a stub `app_push.sh` that makes the same head check the real one makes. Its race arm holds `open_pr.sh` inside its second push, starts `update_pr.sh` on the same branch, then lets the push go. Each new arm sits beside a mutant that deletes its predicate line (`# mut:<name>`) and must fail it:

- `open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin` (update_pr rc 75, open_pr prints `PR=5`, the row is on origin).
- `mutant mut:oplock`: with `open_pr.sh`'s lock line deleted `update_pr.sh` is no longer BUSY, but the row still reaches origin because layer 2 refuses the detach.
- `mutants mut:oplock and mut:unpushed (both deleted)`: the stub prints `app_push: REFUSE: worktree HEAD is not the committed tip of 'fix/r'`, `open_pr` fails with `the push failed`, and the row is not on origin. This is the production defect, reproduced.
- `update_pr: a worktree holding the branch with a commit origin lacks is refused and stays on its branch`, and `mutant mut:unpushed` (the worktree is detached under its commit).
- The existing lock arms (`mut:lock`, `mut:unlock`, `mut:watch`, `mut:stop`) still pass; their lines now live in `pr_branch_lock`.

## Null control

Unmodified tree (`origin/main` `43f79c08b`) with only the new `pr_args.sh` copied over it, so the new arms run against the old scripts: `pr_args self-test: 62 checks, 4 failed`. The four are the race arm, `mut:oplock`'s arm, the unpushed-work arm, and the existing BUSY arm (its text changed from "another update_pr.sh run" to "another open_pr.sh or update_pr.sh run"). At the head: `pr_args self-test: 62 checks, 0 failed`.

Clean-repo controls at the head: the race arm's `open_pr.sh` run opens, prints `PR=5 HEAD=... AUTHOR=tvofi`, and its row is on origin; `null control: a worktree whose HEAD origin has is detached as before, and the run reaches its push`; and the existing null controls (`open_pr`/`update_pr` with a valid code sha reach their push) pass.

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test` at the head prints `pr_args self-test: 62 checks, 0 failed` and `delivery_row self-test: 5 checks, 0 failed`; the same command on `origin/main` prints 56 checks, 0 failed (the 6 added arms are this diff's).
- Class search, the rule being every site that detaches, resets or removes a worktree or branch under `tools/audit/seat/` and `tools/pr/`: `grep -nE "checkout -q --detach|reset -q --hard|worktree add -q -B|worktree remove --force|branch -D" tools/audit/seat/*.sh tools/audit/seat/*.py tools/pr/*.sh` (self-test and `app_approve` fixtures excluded). Dispositions:
  - `update_pr.sh` detach and `-B`: closed in this diff.
  - `handoff_push.sh` (`reset --hard origin/$BR`, `worktree remove --force`): its worktree is `${HPO_WT_ROOT:-$(dirname "$M")}/fix-<topic>`, outside `$HPO_STATE_DIR/pr`, so `update_pr.sh`'s detach (filtered to `^$P/`) never reaches it, and it resets only its own worktree. Legacy path (INSTRUMENTS says new work uses `open_pr.sh`/`update_pr.sh`); not the defect.
  - `remerge_main.sh` (`reset --hard origin/$BR` in the worktree the merge train passes it): the train owns that worktree and holds no unpushed work in it by contract (its header: the worktree may be detached). Not the defect.
  - `cloud_relay.sh` lines are its self-test fixtures.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

- The #2547, #2548 and #2549 rows are not repaired by this diff. The stale worktrees under `$HPO_STATE_DIR/pr/<topic>/wt` and the local branches `fix/r10-replay-cap` and `fix/r10-tick-owed-level` still point at the commits above; rerunning `update_pr.sh` on each (it adds the row when the head lacks it) lands the rows. Carry: orchestrator
- `app_push.sh`'s head check cannot say why HEAD is not the tip. Not changed here (the check is right: it refused to push a branch the seat is not on). Carry: none

## Friction

none

