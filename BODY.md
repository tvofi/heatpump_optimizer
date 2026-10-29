R10-FLY-ABORT-OWN-MERGE (triage P276, `dev/programme/triage/s6-batch59.md` "P276"): the two tools that start a merge in a worktree now abort that merge when it fails, so a conflicted merge no longer keeps the PR's branch checked out.

- `tools/audit/seat/remerge_main.sh` (the merge train's recarry): on a failed reset-and-merge it runs `git -C "$W" merge --abort`, falling back to `reset -q --hard origin/$BR` when no merge is in progress, and only then prints `MERGE CONFLICT` (`# mut:remergeabort`). The worktree is left clean at `origin/$BR`, so `merge_train.py`'s unforced `release_worktrees` removes it and the next recarry's `worktree add -B` finds the branch free (#2935, #2936).
- `tools/audit/seat/pr_args.sh`, `pr_branch_lock`'s holder with `detach` (update_pr.sh's `$WT`): when the worktree has a `MERGE_HEAD` it runs `git merge --abort` (`# mut:holdabort`), then the existing `checkout -q --detach` (`# mut:detach`), which refuses a conflicted index on its own (#2917's `upd-fix-r10-cop-gate`). Only the run's own worktree, as before.
- Nothing is lost: remerge_main's merge starts at `reset --hard origin/$BR` and update_pr's at `worktree add ... origin/$BR`, and both merge only remote refs (the code sha from `origin/handoff/<topic>`, `origin/main`).
- The header comments of `remerge_main.sh` and `update_pr.sh`, the `pr_branch_lock` comment, and `instruments/pr_args.sh.md` and `instruments/remerge_main.sh.md` state the new behaviour.

Alternatives: `merge_train --free-holders` forcing dirty holders (P193 keeps it clean-only, and the triage rejected it as options (a) and (b)), and `worktree_gc.sh` sweeping conflicted worktrees after the fact; both treat the symptom in another seat's tool, where the abort removes the cause in the tool that started the merge. Both are out of scope by the brief.

## Head

`332661e994a98887fb3937925c24f46a1e2a9787`, cut from origin/main `66974d47312caa46e9817b9aeae7186e9764e560` (merge base; `git merge-base origin/main HEAD`). Every figure below was taken at this head.

## Mutation proof

In-tree mutants in `pr_args.sh --self-test` (its `copyin` and the new `rmrun` delete the line ending `# mut:<name>`), run at this head:
- `mut:holdabort` deleted: `ok     mutant mut:holdabort (its line deleted): the conflicted merge stays, and the worktree still holds fix/k`, i.e. the arm `update_pr: a run whose merge stops conflicted leaves its worktree clean, detached at origin/fix/k, and fix/k free for a second worktree` reads red under the mutant.
- `mut:remergeabort` deleted: `ok     mutant mut:remergeabort (its line deleted): the conflicted merge stays, and the worktree is not released`, i.e. the arm `remerge_main: a conflicting main is named MERGE CONFLICT and leaves the worktree clean at origin/rk, released unforced, rk free` reads red under the mutant.
- Failing test first: the same self-test at the merge base's production lines with the new arms added (commit not pushed; the arms only) printed `FAIL update_pr: a run whose merge stops conflicted ...` and `FAIL remerge_main: a conflicting main is named MERGE CONFLICT ...` (tally `pr_args self-test: 151 checks, 3 failed`; the third was the first wording of the update_pr null control, which asserted HEAD == the code sha and so ignored ensure_row's row commit on top; it now asserts the code sha is an ancestor of HEAD, a property of the test, not of the fix).
- The existing `mut:detach` arms (SIGKILL and plain run) still go red under their mutant: `detach` stays its own line after the split.

## Null control

- `null control: a run whose merge is clean keeps the merged code head under its HEAD, nothing aborted or reset` (update_pr.sh on fix/x with `$code`): ok at this head.
- `null control: remerge_main on a clean merge keeps that merge (HEAD's parents origin/rc and origin/main), nothing aborted`: ok at this head.
- The unmodified tree on a conflict: the two FAIL lines above (the worktree kept its branch with a conflicted index).

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test` at this head: its tally line reads 151 checks, 0 failed (the rule: one `ck` per line, `n` counted in `pr_args_self_test`); at the merge base with the new arms only, 151 checks, 3 failed (above).
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run`; the changed files are tools/audit/seat scripts and instrument pages, whose self-tests run in governance's `instrument-self-tests` job (`pr_args.sh --self-test`, `update_pr.sh --self-test`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at this head.
- `tools/pr/prepr.sh <body>` on this committed head: every step ok or skip except `closures`, refused for want of the seat venv in this container (see Friction); `ci predict`, `carry`, `pr-body` and `figures` ok.
- Class seams, by the rule `grep -nE '\bmerge (-q |--no-edit |--no-ff |-m )*[^-]' -r tools/audit/seat tools/pr --include='*.sh' --include='*.py'`, less `merge-base`/`merge-tree`/`gh pr merge`, comments and self-test fixtures (the production `git merge` calls that run in a seat worktree):
  - `remerge_main.sh` (the recarry merge): closed in this diff.
  - `update_pr.sh` `$G merge ... $C` and `$G merge ... origin/main`: closed in this diff (the lock holder's abort).
  - `open_pr.sh` `merge -q --no-edit origin/main`: open, not in this diff. A conflict there stops the run and `pr_release_wt` KEEPs the worktree as dirty on its branch, by design ("a worktree that is dirty is kept"); changing that rule is `pr_release_wt`'s seam, not the lock holder's. See Forward-carry.
  - `handoff_push.sh` update path (`checkout --force -B ... && merge $CODE && merge origin/main`) and open path (`merge origin/main` under `MM`): open, not in this diff; the next run's `checkout --force` / `worktree remove --force` clears it, but between runs the worktree holds the branch conflicted. See Forward-carry.

## Red checks

none

## Forward-carry

- The two open seams in Figures (`open_pr.sh`'s main merge; `handoff_push.sh`'s code and main merges) are this class outside the brief's two tools: a conflicted merge left in a worktree that holds a PR's branch. Both end in `pr_release_wt`, whose "a worktree that is dirty is kept" rule reads a conflicted index as authored work; the ruling owed is whether a conflicted index the run's own merge made is aborted there. R10-FLY-OPENPR-ATOMIC owns `open_pr.sh` and `pr_release_wt` (P-D, P64, P72). This seat writes no ref but its return refs, so the roster carry is the orchestrator's to land. Carry: R10-FLY-OPENPR-ATOMIC

## Friction

- dev/governance/roles/fixer.md: cost: (step 5) `prepr.sh`'s `closures` step refused in this cloud container ("no interpreter that parses the tree"): `tools/audit/seat/seat_venv.sh` asks uv for cpython-3.14.7, which the container's uv index does not offer (3.14.6 is the newest 3.14 listed), and the ambient python is 3.11. Not worked around; CI re-executes the step, and this diff changes no `.py`. Carry: dismissed: container interpreter availability, re-executed by CI
