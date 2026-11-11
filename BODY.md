The root-cause document owed by `pr-contract`'s red on PR 3424 at `f9c7952b` (run 42953123178, job 130312858296): `dev/audit/rca/r10-rca-restore-base-skew.md`. Cause: every check-source restore pins `github.event.pull_request.base.sha` while the job checks out the merge commit, so restored files (`roster_lib.py` at `d08ed31049`) and unrestored callers (`carry_audit.py` at `c620ebba96`) come from two mains. Process state (c): the `tests/entities.py` base-restore census (`e55be57447`) asserted the expression's value, the payload base, not the tree it yields, and covered `governance.yml` and `tests.yml` only. The countermeasure, that census's pull_request arm reading the merge commit's first parent over every workflow, is built by R10-HOTFIX-RESTORE-BASE-SKEW; this branch changes no workflow and no test.

## Head

`8e807ee1f1f1718ce63245cf58ad5dcd3ff40bec`, cut from `origin/main` `dbd1ab5b07`; measured 2026-11-11 05:05Z.

## Mutation proof

n/a: the diff is one analysis document, no check or production line; the detector's failing/passing pair is the hotfix's mutation proof (document section 5).

## Null control

Restoring `roster_lib.py` from the merge commit's first parent `c620ebba96` instead of the payload base reads `carry_receivable` present (`True`) and the replayed carry check exits 0; the three open PRs whose payload base is current main read 0 restore files differing.

## Figures

- payload base 53 commits, 19 merges, behind the merge commit's first parent: `git rev-list --count d08ed31049..c620ebba96`, with `--merges`
- `carry_receivable` absent at the payload base, present at the first parent: `git merge-base --is-ancestor e08425e904 d08ed31049` (false), `... c620ebba96` (true)
- restored `roster_lib` lacks `carry_receivable` (`False`) from `d08ed31049`, has it (`True`) from `c620ebba96`, in a detached worktree at `427c4ca8` after `git checkout <src> -- tools/audit/seat/roster_lib.py`: `python3 -I -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_lib; print(hasattr(roster_lib,'carry_receivable'))"`
- the full step replayed, `exit=1 attributeerror=True` from `d08ed31049` and `exit=0 attributeerror=False` from `c620ebba96`, rests on the sibling hotfix's harness at its WIP ref `5ab1c861c8` (its restore-base-skew harness), not in this tree; it lands with that group
- 22 `PINNED` restore sites: `grep -n 'PINNED:.*base.sha\|PINNED=.*base' .github/workflows/*.yml`
- 17 of 23 open PRs with a payload base lacking `e08425e904`, the same 17 with restore files differing from main: `git merge-base --is-ancestor e08425e904 <base.sha>` and `git diff --name-only <base.sha> dbd1ab5b07 -- <pr-contract restore pathspec>` over each open PR's `base.sha`
- 57 of 231 first-parent merges on main touching the restore set, 9 touching `roster_lib.py`, since 2026-11-04: `git log --first-parent --since=2026-11-04T00:00Z -m origin/main -- <pathspec>`
- 13 ms per resolver pair: `time` over 100 `git rev-parse HEAD^1` plus `git merge-base --is-ancestor` pairs
- 64.6 min from run creation to its failed re-run's end: run 42953123178 `created_at` 03:29:46Z, `updated_at` 04:34:20Z

## Red checks

none

## Forward-carry

none

## Friction

none
