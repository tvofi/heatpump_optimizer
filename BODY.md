ci(#3885): the pages release step's tag pipeline reads its listing to the end
Refs #3885

This PR leaves #3885 open. It repairs one failing step, pages `Check out the release`, which exited 141 on both attempts of run 45663211757.

`git ls-remote --tags --refs --sort=-v:refname origin 'refs/tags/v*' | head -n 1` closes the pipe after one line. Once the v* tag listing outgrew the pipe buffer, `git ls-remote` took SIGPIPE and `set -o pipefail` failed the step. The line now ends `| awk 'NR == 1 { sub(/.*refs\/tags\//, ""); print }'`, which consumes the whole listing and prints the first tag, the same tag as before.

`tests/entities.py` runs the step's own `tag=` line, read from `pages.yml`, against a stand-in `git` that lists 20000 tags, under `set -euo pipefail`. It expects exit 0 and `v20000.0.0`, and a plant that restores the `head -n 1 | sed` form must fail.

## Head

`f8decf8b4f48d84c975e483ea958ddd33905f001` is the code head. It adds one commit to `bcf4ac059096da7ccd4b32ac6e9e1e98e2953308` (the fixer's commit), repairing `tests / fast (3.14)` at 455e9b09: `_pages_tag_run` ran its stand-in under a bare `bash -c`, which `tests/entities.py` countermeasure B refuses; it now runs under `_GHA_RUN`. Delta for review: `git diff bcf4ac0590 f8decf8b4f` (one line in `tests/entities.py`). origin/main is merged in at open. The change is two files: `.github/workflows/pages.yml` and `tests/entities.py`.

## Mutation proof

Restoring `| head -n 1 | sed 's#.*refs/tags/##'` in `pages.yml` makes the new `tests/entities.py` check, "pages.yml: the release step's tag pipeline reads its listing to the end under pipefail", go red: the stand-in exits 141. The check builds this plant itself and asserts it fails.

## Null control

The unmodified tree (the `head -n 1` form) run against the same 20000-tag stand-in exits non-zero under pipefail, which is the CI failure reproduced.

## Figures

none

## Red checks

`tests / fast (3.14)` at 455e9b09 (run 45719342344): `tests/entities.py` countermeasure B, "every `bash -c` / `sh -c` a check runs carries errexit", listed `tests/entities.py:_pages_tag_run`. Repaired at f8decf8b. Cheaper detector: none; that check is inside `tests/entities.py`, the script the PR's own test lives in,.

## Forward-carry

none

## Friction

none
