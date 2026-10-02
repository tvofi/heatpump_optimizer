Hotfix for main's red Governance workflow since 87d780c7, the F11.3 merge (#1715), stamped in v6.7.6.

Before: `policy-docs`, `env-matrix` and `pr-contract` fail on main and on every open pull request. The Actions `GITHUB_TOKEN` reads ruleset 23698884 without `bypass_actors`, a field GitHub returns only to an admin token. The leaf compare in `counts.mjs` `requiredContextsDrift` reported each recorded bypass leaf as removed, giving 3 errors of the form `ruleset 23698884 field bypass_actors[0].actor_id is (absent) live, null recorded`.

After: a field in `RULESET_TOKEN_HIDDEN` (today only `bypass_actors`) that the live object omits entirely is UNCHECKED, printed as one `skip required-contexts` line, and gives no finding. `[]`, `null`, any other recorded field missing live, and an absence inside a field the read carried all still fire. env-matrix's `pr / nothing skipped in a full clone` row accepts exactly that line (`TOKEN_HIDDEN_SKIP_RE`) and refuses every other skip. The recording is unchanged, since an admin read matches it.

How:
- `counts.mjs`: `RULESET_TOKEN_HIDDEN` and `TOKEN_HIDDEN_SKIP_RE`; a token-hidden key the live object lacks is skipped, loudly.
- `policy_lint_envmatrix.mjs`: the `nothing skipped` row filters out lines matching `TOKEN_HIDDEN_SKIP_RE` and no others.
- `policy_lint.mjs`: five acceptance pins. An omitted `bypass_actors` gives the skip line and 0 findings. `bypass_actors` carried as `[]` or `null` fires. A missing `enforcement` fires and is not skipped. The printed line matches `TOKEN_HIDDEN_SKIP_RE`.
- `field_coverage.mjs`: the ruleset probe parses the JSON on its last line, because the skip line now prints ahead of it.

## Head

Code head `39bc45fe` on `handoff/r9-f11-hotfix-ruleset-absent-v2`, two commits above `origin/main` `36d3c27a`: `ea22db6c`, then the review round's `39bc45fe`. No merge. Everything below was measured at `39bc45fe`.

## Mutation proof

Each mutant was applied, run, and restored. The first five run `node .claude/workflows/policy_lint.mjs`, which exits 1 each time:
- The skip removed from the compare (`|| under(k)` deleted): `FIXTURE VACUOUS: a recorded field the live read omits produced 3 finding(s) and 1 skip line(s)`.
- Every recorded array treated as unreadable: `FIXTURE VACUOUS: a ruleset parameter that moved with the context names and ids unchanged produced 0 finding(s)`.
- Any missing recorded field skipped, not only a token-hidden one: `FIXTURE VACUOUS: a recorded enforcement field missing from the live read produced 0 finding(s)`.
- `null` treated as absent: `FIXTURE VACUOUS: a bypass list the live read carried as null produced 0 finding(s)`.
- The skip line's wording drifted from the row's pattern: `FIXTURE VACUOUS: the token-hidden skip line no longer matches TOKEN_HIDDEN_SKIP_RE`.
- The env-matrix row accepting every skip (`&& false`): with no `gh`, the API-unreachable skip line passes the row (`16 declared outcome(s) held, 0 did not`), where the head fails it (`15 held, 1 did not`). No CI pin holds this one; the run was by hand.

## Null control

At `origin/main` `36d3c27a`, the Actions view reproduces the red. That view is the recorded ruleset object with its volatile keys restored and `bypass_actors` deleted, served by `field_coverage.mjs`'s own `gh` stub. `policy_lint.mjs` gives `TOTAL: 3 error(s)`, the three `bypass_actors[0].*` leaves. `field_coverage.mjs --only ruleset` gives `REFUSED` with `refused=1`.

At `ea22db6c`, the first code commit, `policy_lint_envmatrix.mjs` under the Actions view reports `15 declared outcome(s) held, 1 did not`: the `nothing skipped` row refusing the new skip line.

At the head, the same Actions view gives `TOTAL: 0 error(s)` plus the skip line, field coverage reports `read=37 blind=0`, and env-matrix reports `16 declared outcome(s) held, 0 did not`. The admin view, with `bypass_actors` present, gives `TOTAL: 0 error(s)` and `read=40 blind=0` at both ends.

## Figures

none

## Red checks

`policy-docs`, `env-matrix` and `pr-contract` on main at 87d780c7. This was a red CI check on main, so the root-cause rule applies.

- **Cause:** every run of the comparator, in the acceptance, in field coverage and in review, fed it an admin-shaped ruleset object. None ever used the read an Actions token actually gets.
- **Cheaper detector:** field coverage's ruleset arm could also load the object as the Actions token sees it. That is owed to a root-cause seat and is not built here.

This pull request's own `policy-docs` and `env-matrix` runs will still be red. Both jobs restore `.claude/workflows/*.mjs` from the base commit, and the base carries the defect. `pr-contract` is green on this pull request. Both reds go green on the first push to main after the merge, and `env-matrix` does so only because of the row change above.

## Forward-carry

none

## Friction

pinned-graders: cost: a fix to a pinned grader cannot go green on its own pull request, because the red comes from the base's copy of the file being fixed.

_Requested by **tvofi**_
