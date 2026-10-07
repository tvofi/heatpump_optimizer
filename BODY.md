`prepr.sh --self-test` failed 7 rows on a seat (`186 passed, 7 failed`) and passes in CI. Cause: the step-7c fixture repository is built with `git config user.name st`, but the red-ancestry fixtures under `tools/policy/fixtures/red-ancestry/` are keyed by the two commit SHAs, and a seat exports `GIT_AUTHOR_NAME` (here `Tvofi2`), which outranks the config and changes both SHAs. The stub `gh` then finds no fixture and exits 1, so `ancestry_reds` returns 3 (skip) where 1 or 0 is wanted. Not detached HEAD (the fixture passes the remote ref explicitly) and not GitHub reach (the stub is offline). prepr's ancestry logic is correct; the fixture was environment-dependent. Fix: export `GIT_AUTHOR_NAME/EMAIL` and `GIT_COMMITTER_NAME/EMAIL` as `st`/`st@st` inside the fixture-building subshell. No other SHA-keyed construction exists in `tools/pr/prepr.sh` (`grep -n GIT_AUTHOR tools/pr/prepr.sh` shows only this one).

## Head

171ea64c8aa802d462d4230c94931d265e5ef9a3 (merge base 59b5ac6e, origin/main at the time; date -u 2026-10-07).

## Mutation proof

Mutant: the pre-fix tree (the added export line removed), run in a clean detached export of origin/main with `GIT_AUTHOR_NAME=Tvofi2` in the environment: `186 passed, 7 failed`, rows failing include "a red an earlier pushed commit carried and the body does not name is refused (got 3, wanted 1)", "the same ancestry with a body that names the red passes (null control) (got 3, wanted 0)" and "an ancestry whose only failure is pr-contract's own run passes (the exclusion key) (got 3, wanted 0)" and their four companion `ok line` rows. Restored: `193 passed, 0 failed`.

## Null control

Same pre-fix tree with the author variables unset, SHAs of the fixture repo built by the production construction: `12f5d877...` and `d01ba036...`, equal to the fixture file names, so the unmodified tree is green where the environment is clean (that is CI). Command: `env -u GIT_AUTHOR_NAME -u GIT_AUTHOR_EMAIL -u GIT_COMMITTER_NAME -u GIT_COMMITTER_EMAIL` around the same construction, `git rev-list main..fix`.

## Figures

- `PATH=$HOME/.local/state/hpo/venv-ci/bin:$PATH bash tools/pr/prepr.sh --self-test` at origin/main 59b5ac6e, `GIT_AUTHOR_NAME=Tvofi2` ambient: 186 passed, 7 failed (rc 2); at 171ea64c, same environment: 193 passed, 0 failed (rc 0).

## Red checks

delivery-status and nightly-status: both grade main, not this branch; main's record-autofix staged the old path and #2011 fixes it, so they are red on main independent of this diff, and no cheaper detector than those checks exists for that.

## Forward-carry

none

## Friction

none
