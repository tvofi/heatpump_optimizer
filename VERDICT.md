Fix review: merge d40cdb8f41733b345ef00d70dd346cc57ae6c9ed

bus-nonce: 8dbdb8f09faef48a964e86cb07d5f00a

Delta review of PR #2612 (R10-SOLVER) from the full-review head `c8dea4651d20089a860e6d8f1e11be2216885905` (verdict `merge`, ref review/2612) to `d40cdb8f41733b345ef00d70dd346cc57ae6c9ed`, measured from a detached worktree at that head. `dev/governance/roles/` has no diff against origin/main.

## Findings

- No new finding. The one finding in the c8dea465 verdict (`tests/optimality.py` `_cert_gaps` literal `"eps": 1e-4`, inert while a jac is supplied) is not invalidated: the delta touches no test or production line. Carry: R10-SOLVER | #2250 | O5 | dismissed: unchanged from the c8dea465 verdict; pre-existing test-side literal, fold into a later instrument tidy

## Evidence

- Carry command re-run: `bash tools/pr/app_approve.sh --carry c8dea465... d40cdb8f41733b345ef00d70dd346cc57ae6c9ed origin/main` printed `CARRY: yes ... only automatic merges from origin/main, ci: commits and the autofix bot's own, and the branch's own diff compares equal`, rc=0 (`evidence/carry.out`). No verdict comment exists at c8dea465, so this delta verdict replaces it at the merge.
- Non-merge commits in the range: `git log --no-merges c8dea465..d40cdb8f41733b345ef00d70dd346cc57ae6c9ed ^origin/main` lists exactly one, `7b42306f7e75af9dfa9c7934ae930fa3240d59ee` (`ci: pin killed mutants`, github-actions[bot]) (`evidence/log_nomerges.txt`). Its diff is four new `killed_by` JSON pin files (24 insertions): `optimizer.py` `@module.CONST`, `_lbfgsb_run.BOOLOP`, `_lbfgsb_run.GUARD_OFF`, `_memoized_value_and_gradient.GUARD_OFF`. They are the four sites the c8dea465 verdict named. No production or test logic (`evidence/ci_commit_stat.txt`).
- Merge: `git merge-tree --write-tree origin/main d40cdb8f41733b345ef00d70dd346cc57ae6c9ed` exits 0 (`evidence/merge_tree.out`).
- Sensitive paths: the three-dot diff from the merge base to the head touches no `VERSION`, `RELEASE_NOTES`, manifest or `tests/golden` file (`evidence/sensitive.txt` is empty).
- CI at the head (one check-runs read, `evidence/check_runs.tsv`): every gate check is success or skipped, including `mutation` (success; it was the red at c8dea465, now pinned), `pr-contract`, `closures`, `typing`, `arch-score`, `budget-raise-gate`, `env-matrix`, `coverage`, `fast (3.14)`. The one failure is `nightly-status`, the known transition red (NIGHTLY ABSENT until the first scheduled Nightly). It is not required and not this PR's, since the diff reaches nothing it reads.
- Not re-run: the mutation proof, harness figures and structure ratchet from the c8dea465 verdict. The delta carries no production or test change, so they stand as measured there.
