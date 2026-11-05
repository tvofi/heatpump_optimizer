Fix review: merge 1c42ca3fda183b63a6c3579071bef9a8e354acef

bus-nonce: 1c35ce5e6f4dbda9e80b75a2643114b4

CI-only re-check of the head that the earlier verdict blocked on ci-red only (cancelled codeql / Analyze (python), a ci_priority.py pause). The code was not re-reviewed, as the brief says.

## Evidence

- `merge_train.py classify 1c42ca3fda183b63a6c3579071bef9a8e354acef --pr 3217`: `GREEN ... pending: none red: none`, exit 0 (ev/classify.txt).
- All 68 check-runs of the head, listed in one page: none pending. `codeql / Analyze (python)` was re-run and now concludes success; `gate`, `pr-contract`, `arch-score`, `budget-raise-gate`, `prelude`, `tests / fast`, `tests / mutation`, `tests / coverage`, `tests / closures`, `governance / policy-docs` and `hassfest` are success. The rest are skipped.
- The only failures are `tests / nightly-status` and `governance / delivery-status`. Both are status reporters that do not fail the gate.
- The PR body's `## Head` names `1c42ca3fda183b63a6c3579071bef9a8e354acef`. `## Red checks` says "none concluded", which was true at handoff, before this head ran in CI. The two reporter reds above came later and are not gate checks.
- `git merge-tree --write-tree origin/main <head>`: clean, no conflicts (ev/merge-tree.txt).
