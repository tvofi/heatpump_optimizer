Main is red on policy_lint: `dev/governance/roles/fixer.md` (budget key `tools/audit/briefs/fixer.md`) measures about 4867 tokens against a 4866 cap. #2027 and #2030 each fit the cap alone and merged together, so neither PR could have seen the break. This cuts "that is safe" from the `tests/README.md` pointer on line 55 of fixer.md; the meaning is kept because `tests/README.md` ("The scoped gate") says why.

## Head

1101a2fb057677b0d64371c7b1dcc4a0a1d90a7f

## Mutation proof

Restoring `dev/governance/roles/fixer.md` to origin/main (143e2d0a) turns `node tools/policy/policy_lint.mjs` red: `TOTAL: 1 error(s) across 40 policy file(s)`. At this head it prints `TOTAL: 0 error(s) across 40 policy file(s)` and `FIXTURE ok: 92 error(s) hold 243 pins across 12 check classes`.

## Null control

The unmodified tree (origin/main 143e2d0a) fails policy_lint with 1 error, the fixer.md token cap, as above. Nothing else in the diff: one line of one file.

## Figures

- `node tools/policy/policy_lint.mjs` -- before 1 error, after 0 errors (instrument prints both).

## Red checks

Fixed by this PR: main's `policy-docs` and `env-matrix` checks, which run policy_lint. Cause: a combined break of two PRs (#2027, #2030), each green alone; no cheaper detector exists short of a merge-queue run of policy_lint on the merge result, and the cap itself is the detector that caught it within one merge. Main's state checks `delivery-status` and `nightly-status` also read red on main and are not touched by this diff.

## Forward-carry

none

## Friction

none

## Approval

Policy file (`dev/governance/roles/fixer.md`). Approved under tvofi's round-9 programme mandate 5951564627.
