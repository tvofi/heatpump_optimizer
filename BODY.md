# Summary

`open_pr.sh` opens a PR with its first push, commits the PR's own delivery row, and pushes a second time. On 2026-10-21 that second push was refused on #2547 and #2548 (and #2549 is left without a row too; repairing the three rows is the orchestrator's follow-up, by rerunning `update_pr.sh` on each, which adds the row when the head lacks it), so `bus.sh dispatch` refused their reviewers. The refusal is `app_push.sh`'s head check: `worktree HEAD (41fd99b0...) is not the committed tip of 'fix/r10-replay-cap' (daac94b4...)`.

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

The code head is `88a352d3be45ef786a475ea4886d6e074dea42fe` (branch `fix/r10-openpr-row-push-r2`), PR #2560's head `f8694ba2d73595da723f0de3ed78c3e05df78b3d` merged with `origin/main` `289426c1f`, plus one commit. Round 2: the first round's reviewer blocked `f8694ba2d` on `ci-red` (below); this round's delta is that one commit, registering `tools/audit/seat/pr_args.sh` in `ref_privacy.py`'s `PUSHERS` as a `fixture`.

## Mutation proof

The self-test (`bash tools/audit/seat/open_pr.sh --self-test`, which runs `pr_args.sh`'s after `delivery_row.sh`'s) builds a scratch origin and a stub `app_push.sh` that makes the same head check the real one makes. Its race arm holds `open_pr.sh` inside its second push, starts `update_pr.sh` on the same branch, then lets the push go. Each new arm sits beside a mutant that deletes its predicate line (`# mut:<name>`) and must fail it:

- `open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin` (update_pr rc 75, open_pr prints `PR=5`, the row is on origin).
- `mutant mut:oplock`: with `open_pr.sh`'s lock line deleted `update_pr.sh` is no longer BUSY, but the row still reaches origin because layer 2 refuses the detach.
- `mutants mut:oplock and mut:unpushed (both deleted)`: the stub prints `app_push: REFUSE: worktree HEAD is not the committed tip of 'fix/r'`, `open_pr` fails with `the push failed`, and the row is not on origin. This is the production defect, reproduced.
- `update_pr: a worktree holding the branch with a commit origin lacks is refused and stays on its branch`, and `mutant mut:unpushed` (the worktree is detached under its commit).
- The existing lock arms (`mut:lock`, `mut:unlock`, `mut:watch`, `mut:stop`) still pass; their lines now live in `pr_branch_lock`.

Round 2: `python3 -I tools/audit/seat/ref_privacy.py --check` at the merge `83021be0c` (before the registry entry) prints `ref_privacy: REFUSE tools/audit/seat/pr_args.sh:353: a push site in a file PUSHERS does not name` and `1 refused`. At the head it prints `0 refused`. Deleting the new `PUSHERS` entry is that first state; the check is not weakened (no rule, scope or pattern changed), only the file is named with its reason, as `app_approve.sh` and `r9_rc_bus_fetchhead.sh` are.

## Null control

Unmodified tree (`origin/main` `43f79c08b`) with only the new `pr_args.sh` copied over it, so the new arms run against the old scripts: `pr_args self-test: 62 checks, 4 failed`. The four are the race arm, `mut:oplock`'s arm, the unpushed-work arm, and the existing BUSY arm (its text changed from "another update_pr.sh run" to "another open_pr.sh or update_pr.sh run"). At the head: `pr_args self-test: 62 checks, 0 failed`.

Clean-repo controls at the head: the race arm's `open_pr.sh` run opens, prints `PR=5 HEAD=... AUTHOR=tvofi`, and its row is on origin; `null control: a worktree whose HEAD origin has is detached as before, and the run reaches its push`; and the existing null controls (`open_pr`/`update_pr` with a valid code sha reach their push) pass.

## Figures

- `bash tools/audit/seat/open_pr.sh --self-test` at `88a352d3b` prints `pr_args self-test: 62 checks, 0 failed` and `delivery_row self-test: 5 checks, 0 failed`; the same command on `origin/main` prints 56 checks, 0 failed (the 6 added arms are this diff's).
- Class search, the rule being every site that detaches, resets or removes a worktree or branch under `tools/audit/seat/` and `tools/pr/`: `grep -nE "checkout -q --detach|reset -q --hard|worktree add -q -B|worktree remove --force|branch -D" tools/audit/seat/*.sh tools/audit/seat/*.py tools/pr/*.sh` (self-test and `app_approve` fixtures excluded). Dispositions:
  - `update_pr.sh` detach and `-B`: closed in this diff.
  - `handoff_push.sh` (`reset --hard origin/$BR`, `worktree remove --force`): its worktree is `${HPO_WT_ROOT:-$(dirname "$M")}/fix-<topic>`, outside `$HPO_STATE_DIR/pr`, so `update_pr.sh`'s detach (filtered to `^$P/`) never reaches it, and it resets only its own worktree. Legacy path (INSTRUMENTS says new work uses `open_pr.sh`/`update_pr.sh`); not the defect.
  - `remerge_main.sh` (`reset --hard origin/$BR` in the worktree the merge train passes it): the train owns that worktree and holds no unpushed work in it by contract (its header: the worktree may be detached). Not the defect.
  - `cloud_relay.sh` lines are its self-test fixtures.
- `python3 -I tools/audit/seat/ref_privacy.py --check` at the head prints `ref_privacy --check at HEAD: 19 file(s) with a push site, 9 guarded, 111 line(s) added since 289426c1fdde judged, 0 refused`; `python3 -I tools/audit/seat/ref_privacy.py --self-test` prints `ref_privacy self-test: 66 checks, 0 failed`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`.

## Red checks

- `instrument-self-tests` (step "Refuse a push that names the host, and an unregistered pusher"): the race arm's stub `app_push.sh` heredoc in `pr_args.sh` is a push site `ref_privacy --check` did not know. Cheaper detector: `python3 -I tools/audit/seat/ref_privacy.py --check`, seconds, run before the push. `tools/pr/prepr.sh` does not run it (`grep -n ref_privacy tools/pr/prepr.sh` finds nothing), and a fixer has no rule naming it, so a diff that adds `git push` text under `tools/` is caught only by CI. Standing cost of wiring it into prepr: one more step on every run; not built here, since the process moratorium (decision 0012) bars new checks and the class has one instance. Named for the root-cause seat if it recurs. Fixed by the registry entry.
- `pr-contract` (`carry_audit.py check --body`: two `## Forward-carry` items unrouted): the two items were notes, not findings for a later stage, and used `Carry:` destinations the audit does not accept. Cheaper detector: `python3 tools/audit/carry_audit.py check --body <body>`, instant; `prepr.sh` does not run it either (`grep -n carry_audit tools/pr/prepr.sh` finds nothing), so the first round learned it from CI. I ran it on this body: `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`. Fixed: the rows follow-up moved into the Summary, the other item is dropped, and `## Forward-carry` is `none`.
- `nightly-status` grades `main`, not this diff.

## Forward-carry

none

## Friction

none
