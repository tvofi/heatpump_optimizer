<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: `nightly-status` and `delivery-status` run on every pull request and report `main`: its last scheduled run, and its merges that have no delivery row. Nothing in a pull request's diff can change either one. When one went red, `pr-contract` refused every open pull request's body until it named and answered that check. So one fact about `main` was re-explained in every body, and most "red and not named" refusals in the week to 2026-09-24 were these two. The census is in the project's `ci-autofix/ANALYSIS.md`.

After: `pr-contract` no longer asks a body to answer those two checks. Their tick still shows red on the pull request, and `defect-root-cause.md` now says clearing it is the orchestrator's job, on `main`.

This is a policy change: it changes what a seat must write in a body.

How:
- `policy_lint.mjs` gets a `MAIN_STATE_REPORTERS` set holding exactly those two names. The set is skipped both in the head's red list (`checkPrBody`) and in the red history (`failingCheckNames`).
- `pr-contract` restores `policy_lint.mjs` from the base commit, so a pull request cannot widen its own exemption. A change to the set takes effect only after it merges.
- `defect-root-cause.md` (and its generated `.mdc`) and `fix-review.md` are reworded to match.
- No check stops running, and no check that grades the pull request's own diff is exempted.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AJvUdyMZC5ztrV1UH5FmiH

## Approval

tvofi asked for this change in the project thread on 2026-09-24 ("do 1-4", item 3). Merging needs tvofi's approving code-owner review.

## Head

`ed488ddabe99c6311493296baea11ad1becbc6ba`

## Mutation proof

- **`checkPrBody` exemption:** removing it turned the acceptance red with `FIXTURE VACUOUS: red [nightly-status, delivery-status, typing] against a body naming none produced 3 error(s), not the one for \`typing\``.
- **`failingCheckNames` exemption:** removing it turned the acceptance red with `FIXTURE VACUOUS: the red history over a pull request's commits is ["delivery-status","fast (3.14)","typing"]`.
- **Mutant check:** `node .claude/workflows/policy_lint_mutants.mjs` printed `MUTANTS ok`.

## Null control

The new pin passes `typing` beside the two exempt names and requires exactly one refusal, for `typing`. So a gate that excused every red fails the pin. The existing red-history pin still requires `fast (3.14),typing` from the same fixture runs.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
