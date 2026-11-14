## Forward-carry

- Once this merges (the grader then reads `files_tokens` as `CAPFILE` from the base), drop from `dev/governance/config/policy_budgets.json` the `files_tokens` cap this diff kept for the retired orchestrator turn (keyed on that file's pre-move path; its value is 3814) (routine under the fixed grader), and extend `tools/policy/policy_lint.mjs`'s orphan-cap check to `files_tokens`: measured at this head, a `files` cap on a path no glob matches is refused and a `files_tokens` cap on the same path passes with `TOTAL: 0 error(s)`. Control: the two `policy_lint.mjs` runs in `## Figures`. Re-measure at that group's merge base. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
