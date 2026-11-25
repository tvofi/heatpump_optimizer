ci(#3885): the pages release step's tag pipeline reads its listing to the end
Refs #3885

This PR leaves #3885 open. It repairs one failing step, pages `Check out the release`, which exited 141 on both attempts of run 45663211757.

`git ls-remote --tags --refs --sort=-v:refname origin 'refs/tags/v*' | head -n 1` closes the pipe after one line. Once the v* tag listing outgrew the pipe buffer, `git ls-remote` took SIGPIPE and `set -o pipefail` failed the step. The line now ends `| awk 'NR == 1 { sub(/.*refs\/tags\//, ""); print }'`, which consumes the whole listing and prints the first tag, the same tag as before.

`tests/entities.py` runs the step's own `tag=` line, read from `pages.yml`, against a stand-in `git` that lists 20000 tags, under `set -euo pipefail`. It expects exit 0 and `v20000.0.0`, and a plant that restores the `head -n 1 | sed` form must fail.

## Head

`bcf4ac059096da7ccd4b32ac6e9e1e98e2953308` is the code head: the fixer's single commit, with origin/main merged in at open. The change is two files: `.github/workflows/pages.yml` and `tests/entities.py`.

## Mutation proof

Restoring `| head -n 1 | sed 's#.*refs/tags/##'` in `pages.yml` makes the new `tests/entities.py` check, "pages.yml: the release step's tag pipeline reads its listing to the end under pipefail", go red: the stand-in exits 141. The check builds this plant itself and asserts it fails.

## Null control

The unmodified tree (the `head -n 1` form) run against the same 20000-tag stand-in exits non-zero under pipefail, which is the CI failure reproduced.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
