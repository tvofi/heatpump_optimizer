Hotfix: prepr.sh's self-test arm "a body naming only repository-relative paths and ~/ text passes (null control)" failed on macOS (got 127, wanted 0), blocking every local open and update. Root cause, from the arm's own stderr: `python3: no pinned interpreter at /Users/exampleuser/.local/state/hpo/venv-ci/bin/python3 ... build the seat venv`. The seat's python3 is a shim that resolves its venv under $HOME; the arm plants a substitute HOME, so the shim exits 127 and body_privacy_line returns nonzero. The sibling "host home refused" arm only saw a nonzero rc and passed for the wrong reason. The fix puts the real interpreter's directory first on PATH for those two calls (ref_privacy.py's own self-test already does this). CI (Linux) never hit it: its python3 is a plain binary that reads no $HOME, so the arm was green there and this is a Darwin-only (shim hosts) defect.

## Head

89daf6c7398d91d567aa229efcd310d8e98cd790

## Mutation proof

Remove the PATH=$pfp prefix from the null-control call in tools/pr/prepr.sh: on this Mac the arm goes red (python3 -I tools/audit/seat/ref_privacy.py body-lines under HOME=/Users/exampleuser exits 127 for both the clean and the planted body).

## Null control

Unfixed (PATH unchanged): clean body rc=127, planted body rc=127. Fixed (real interpreter first): clean body rc=0, planted body rc=1. The unmodified tree on Linux gives 0 and 1 already.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
