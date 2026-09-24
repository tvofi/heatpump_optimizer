<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: `nightly-status` and `delivery-status` run on every pull request and report `main`: its last scheduled run, and its merges that have no delivery row. When one went red, `pr-contract` refused every open pull request's body until it named and answered that check. So one fact about `main` was re-explained in every body, and most "red and not named" refusals in the week to 2026-09-24 were these two. The census is in the project's `ci-autofix/ANALYSIS.md`.

After: `pr-contract` no longer asks a body to answer those two checks, **unless the diff touches what they read**. Their tick still shows red on the pull request, and `defect-root-cause.md` now says clearing it is the orchestrator's job, on `main`.

Both reporters run the pull request's own checkout, so a diff can redden them itself. Deleting a merged pull request's row turns `delivery-status` OVERDUE, and nothing else refuses that before the merge. So the exemption is void when the diff touches a reporter's script, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md`, or a delivery row the base already had. Adding the pull request's own row does not count.

This is a policy change: it changes what a seat must write in a body.

How:
- `policy_lint.mjs` gets a `MAIN_STATE_REPORTERS` set holding exactly those two names. `checkPrBody` is the one place it is applied, to the head's reds and the history's alike, and only when `reporterInputsTouched` finds nothing.
- `pr-contract` derives a second list, the diff less its additions (`--diff-filter=a`), and passes it as `--existing-file`. That is how an edited or deleted row is told apart from the pull request's own new row.
- Both gaps fail closed. Without `--existing-file`, every row counts as touched. Without a path list, the exemption never applies.
- The mechanical void (the review's remedy b) was chosen over a condition in the prose (remedy a), because the body check can enforce it and a reviewer's reading cannot be forgotten.
- `pr-contract` restores `policy_lint.mjs` from the base commit, so a pull request cannot widen its own exemption. A change to the set takes effect only after it merges.
- `defect-root-cause.md` (and its generated `.mdc`) and `fix-review.md` are reworded to match.
- No check stops running.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Approval

tvofi asked for this change in the project thread on 2026-09-24 ("do 1-4", item 3). Under tvofi's mandate to 2026-09-25T08:40Z, the fix thread may approve it as tvofi after a merge verdict and green CI.

## Head

`126a3f668b284ee9826af439fe6c2908289e44df`

The review fix is commit `126a3f66`. The handoff commit after it only carries this body.

## Mutation proof

Each mutant was run against `node .claude/workflows/policy_lint.mjs`. Every one turned the acceptance red with `FIXTURE VACUOUS: MAIN_STATE_REPORTERS (<case>)`:
- the prefix match and the case-fold (the review's M8 and M9) failed `exempt, own row added`;
- reading `paths` instead of `existing` failed `exempt, own row added`;
- treating a missing `existing` list as empty failed `no existing list`;
- no void on an empty path list failed `no paths`;
- dropping `REPORTER_INPUTS` failed `the reporter's own script`;
- never voiding failed `a merged row deleted`;
- removing the exemption failed `exempt, own row added`.

Restored, it printed `FIXTURE ok: 91 error(s) hold 192 pins`, and `policy_lint_mutants.mjs` printed `MUTANTS ok`.

## Null control

The first case passes `typing`, `delivery-status-publish` and `Nightly-Status` beside the two exempt names, and all three must still be answered. A gate that excused every red, or matched loosely, fails it. The four voiding cases each require the reporter's own red to be owed again. The existing red-history pin still requires `fast (3.14),typing` from its fixture runs.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
