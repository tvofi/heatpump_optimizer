# R10-CI-LAYOUT-P2 U10: bots (merge-main dispatch, follower retired)

Part of #2495. Stacked on U5's head `fbc994804d3e4358e412399edca8c9f6ee6144a3` (carries U0c and U9a). Code head: `c2143e8e8`.

## Unit
U10 bots. `git diff --stat fbc994804..c2143e8e8`: 12 files, 85 insertions, 507 deletions (about 85 net added production and test lines against the 100 / 40 row).
- `.github/workflows/merge-main.yml`: job `if: github.ref == 'refs/heads/main'`; one `gh workflow run ci.yml --ref "$branch" -f pr="$pr" -f base="$base"` per pushed branch, replacing the four dispatches (`tests`, `hassfest`, `validate`, `codeql`); `dry_run=true` prints that command per branch and runs no approve step; the approve step stays (M-3 default) and reads the four-field lines.
- `tools/pr/merge_main_bot.py`: `pushed_line()`; `--pushed-file` lines are `<branch> <sha> <pr> <base>`, also written under `--dry-run` (the planned pushes). Self-test +1 check, 42 pass.
- Deleted: `.github/workflows/pr-contract-rerun.yml`, `tools/pr/contract_rerun.py`, with their wiring: `governance.yml` self-test step, `prepr.sh` step 3f2, two `CODEOWNERS` lines, `tests/closures.json` (2 entries), `tests/layout.json` (1 retired entry), `tests/entities.py` (`_PR_WORKFLOW_NAMES`, `_crr_defects`, the follower pin and its two null controls, the `_NON_GATE_WORKFLOWS`, `_GOV_FILES` and `_PT_EXEMPT` entries), `governance_cost.py` GOV member `rerun-stale-contract` (the entities pin demands GOV name only defined jobs), and the deleted workflow's name in `orchestrator_tick.py`'s comment and fixture string (its `SUPERSEDED` rule is generic and unchanged).
- New pin in `tests/entities.py`: `_mm_defects` over `merge-main.yml`.

## Interface
- Consumes U0c's `ci.yml` `workflow_dispatch` inputs `pr` and `base` (`git show origin/handoff-body/r10-ci-layout-p2-u0c:BODY.md`, "## Interface") and U5's identical autofix dispatch form.
- Exports `merge_main_bot.pushed_line(branch, sha, pr, base) -> str`; `pushed.txt` format `<branch> <sha> <pr> <base>`.
- No check name added, removed or renamed.

## Static map
`unitcheck2.py static` over merge-main.yml, base head against this head: `STATIC rows 10->10 lost 0 gained 0 changed 3 (mapped 0) misplaced 0 rc 1`. The three changed rows are the job (its `if:`), the dispatch step and the approve step's read line, the intended edits; rc 1 is the tool's code for changed rows. The unit adds and removes no check name.

## Controls
- Failing test first: `merge_main_bot.py --self-test` with the `pushed_line` check and no function: `NameError: name 'pushed_line' is not defined`; after: `merge_main_bot self-test: 42 checks, 0 failed`.
- `tests/entities.py` pin, plus null control, `ok` at this head: "merge-main dispatches ci.yml once per pushed branch ...", and "each of a missing ref guard, a second dispatch, a dispatch without pr/base and a two-field reader is refused". The pin first failed on its own regex (it matched the dry-run `echo` line); fixed to match command lines only.
- Entities, full run, `PYTHONPATH=tests/hastub` under the venv python, base `fbc994804` against this head: base 11 failed of 2400, head 10 failed of 2398. `diff` of the sorted FAIL lines: the only differences are the removed follower pin and timing noise in `hb:positive_control` / `a8:register_once` lines. The remaining 10 reds exist at the base and belong to units not yet stacked (autofix, merge_group and dispatch pins on `tests.yml`); none is a U10 line.
- `orchestrator_tick.py --self-test`: 199 checks, 0 failed. `selftest_wiring.py --check`: 86 self-testing, 86 wired, 0 unwired. `structure.py`: PASSED. `doc_claims.py`: ALL 203 checks PASSED. `layout.py --guard`: 0 refusals. `tmp_paths.py --check`: 0 refused. `throwaway_git.py --check`: 0 refused. `bash -n prepr.sh` ok; YAML of both edited workflows parses.
- Reader census for the deleted names: `git grep -n 'pr-contract-rerun\|contract_rerun'` outside `dev/audit/`, `dev/programme/` and `dev/archive/` prints exactly one line, `dev/README.md:204`, the `[retired-by: R10-CI-LAYOUT-P2]` marker that `doc_claims.py` reads and tolerates for an absent path; it belongs to the group's closing record and stays until the group completes.
- Scoped gate: `closure.py select --diff fbc994804` prints `MODE: FULL` (reason: no recorded closure mentions the deleted workflow; measured, with `PREPR_SKIP_CLOSURES=1`). CI owns the closures. I ran the scripts naming the touched files directly (list above), not the full suite.

## Live checks owed
1. Dry-run `merge-main` dispatch (`dry_run=true`, on main's ref): its step summary prints one `gh workflow run ci.yml --ref <branch> -f pr=<n> -f base=<base>` per DIRTY-and-resolvable branch, and nothing is pushed or approved. If no PR is DIRTY, `pushed.txt` is empty and it prints `nothing pushed`; plant a DIRTY draft PR on a probe branch for the positive arm. Null: a dispatch on a non-main ref starts no job (the ref guard).
2. M-3(b): a held `ci.yml` run beside a green dispatched `gate` at one head, read with the same two readers as M-2 (`statusCheckRollup` contexts, `commits/<sha>/check-runs?check_name=gate&filter=latest`). Plan §5 default stays: keep the approve steps unless (a) finds none held.

## Wiring
none. (I edited `governance.yml` only to remove the step that ran the deleted `contract_rerun.py --self-test`; no `instrument-self-tests` step was added.)

## Red checks
None read: this unit is offline and I made no GitHub reads. The entities reds listed under Controls are the base's, not this head's additions.

## P2a defect
none found.

## Forward-carry
- U9p policy text still names the follower where it does: `ci-autofix.md`, `orchestrator.md` section 11, `nudge.md` (recorded in the plan's U9p row; this seat edited no policy file).
- `.github/workflows/merge-main.yml` and `tests/entities.py` edits are code-owned paths; the owner's approving review is needed at merge.

## Head
`c2143e8e8b680ff5a1589fba2d1b5c6eb9870c99`, measured with `git rev-parse HEAD` on 2026-10-23T05:49Z. Base: `fbc994804d3e4358e412399edca8c9f6ee6144a3`.

## Mutation proof
Predicate mutated, not the tail: deleted the job's `if: github.ref == 'refs/heads/main'` line from `merge-main.yml`, ran `tests/entities.py`: `FAIL merge-main dispatches ci.yml once per pushed branch ... [defects: ['job merge-main has no main ref guard']]`. Restored (`git checkout`, clean tree). The `pushed_line` change was proved red first (`NameError`, see Controls). No local `stress.py` per mutant.

## Null control
The pin's own null control plants four altered copies (no ref guard, a second dispatch, no `-f pr/-f base`, a two-field reader); each yields a non-empty defect list, `ok` at this head. The pin's null on the base's workflow: the unaltered file yields `[]`. The reader census null: `git grep -n 'pr-contract-rerun\|contract_rerun'` ran on the base tree prints the deleted files' readers (34 lines outside `dev/audit/`, `dev/programme/` and `dev/archive/`, counted in a worktree at `fbc994804` with `| wc -l`); at this head it prints only `dev/README.md:204`.

## Figures
- Added/deleted lines: `git diff --numstat fbc994804..HEAD | awk '{a+=$1;d+=$2}END{print a,d}'` prints `85 507`.
- Entities failures: `python3 tests/entities.py | tail -2`, base `11 of 2400`, head `10 of 2398` (under the venv python, `PYTHONPATH=tests/hastub`, 2026-10-23).
- Self-tests: `merge_main_bot.py --self-test` 42/0; `orchestrator_tick.py --self-test` 199/0; `doc_claims.py` 203 passed.

## Friction
none
