Fix review: merge 15e947e8d47fa45fb4446e400508879e0391a16f

bus-nonce: 79b9639bf65348e4bdbeeee40ea825be

Round: first review at this seat for this head (the body records earlier rounds 1-2 at other heads).

## Evidence
- Head measured: 15e947e8d47fa45fb4446e400508879e0391a16f (ev/HEAD.txt). Merge with main: `git merge-tree --write-tree origin/main 15e947e8d47fa45fb4446e400508879e0391a16f` rc=0, no conflict (ev/merge-tree.txt).
- VERSION 7.1.7 untouched; no manifest, RELEASE_NOTES, golden or claim file in the three-dot diff; `env_drift.py --claims-only` ok; `structure.py` PASSED; `policy_lint.mjs` 0 errors; `agreement_py.py --run` AGREEMENT ok unregistered=0 (ev/*.txt).
- Mutation proof re-run by me on brief_lint.mjs (ev/mutants.txt): M1, M7, R2, R5, M5b, M2 each rc=1 at the playbook acceptance; file restored. Live perturbations: renaming a cited instrument gives `playbook path` error rc=1; a stated cap figure gives `playbook cap` error. Null fixture and live README lint clean (`PLAYBOOK ok ... 7 moved instruments`).
- Figures re-derived: README row `320 321 6058 6059` and `corpus ~68610, cap 68618` match the body (ev/budgets.txt). Brief carry 14's 21-of-56 figure and the `tests/entities.py` 4-failure control I did not re-derive (container-dependent).
- CI at this head: merge_train classify printed RED (rc=1), not APPROVAL-OWED (rc=4). The only failing input to `gate` is `budget-raise-gate` (gate log: single line `FAIL budget-raise-gate`); I judge it as the approval-owed red, which the body answers (Red checks). `governance / delivery-status` red grades main and the diff adds only its own row; not this PR's. All other checks success or skipped at last render; `tests / mutation` success.
- Step 14: the raised caps (README lines/tokens, corpus_tokens) equal the measured values of an owner-ordered ~100-line playbook; dS +0.0000 NULL; payments listed. I found no unlisted payment that improves the code. Removing the playbook section removes the movement, so it is earned.
- Step 10: the finding-propagation carries go to R10-ROUND-PLAYBOOK-FINAL, resolved on origin/handoff/audit-r10-roster per carry_audit.

## Findings
- Residual: the budget raise in dev/governance/config/policy_budgets.json is owed tvofi's approving review at this head (or a mandate the gate reads in force); this verdict does not give it. Carry: dismissed: owed to the owner per the PR body Approval section, a merge-time condition, not a defect
- Note: the PR body's Red checks section says "This head has run no check yet" and "No other check has run on this branch"; checks have since run at this head (gate failed on budget-raise-gate only, tests/mutation/codeql success). A stale sentence, not a defect of the diff. Carry: dismissed: body staleness on a sentence the CI state supersedes, no downstream stage reads it
