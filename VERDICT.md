Fix review: merge 2b8677d3dbbe0b39322affd0c25f40afa972c33c

bus-nonce: 0a4e21a5ef6c61e991f86ec7dac8ac9d

Round 1 (first review of this PR).

## Scope

Dependabot pip-group bump of 13 packages, in three hash-pinned test requirement files only: `tests/requirements-ci.txt`, `tests/requirements-coverage.txt` and `tests/requirements-typing.txt`. Nothing under `custom_components/` changes, and no fixture, claim file, budget or version file changes.

## Evidence

- RESULT head: the reviewed head is 2b8677d3dbbe0b39322affd0c25f40afa972c33c. I re-read `refs/pull/3853/head` before writing this verdict and it had not moved (`ev/head-reread.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main 2b8677d3` exits rc=0, so there is no conflict (`ev/merge-tree.txt`).
- RESULT figures: the body says "13 updates". The three-dot diff changes 13 distinct package pins; numpy appears twice, in ci and in typing, so there are 14 file-level pin changes. Each version pair matches the body's table.
- RESULT hashes: for each of the 14 changed pins, the pinned sha256 set equals PyPI's published digest set for that exact version: 0 hashes missing from PyPI and 0 PyPI files left unpinned. No unchanged pin's hashes moved, and no package was added or removed (`ev/hash-check.txt`, script `$HOME/hc/check.py`, which is my own instrument).
- RESULT mutation: no mutation proof applies. The diff writes no production line, so there is nothing to delete; per `changed_lines`, `tests / mutation` draws no mutant here.
- RESULT harness: no finder's harness applies. This is a dependency bump with no audit finding. The behavioural signal is CI's lanes that install the bumped files with `--require-hashes` (tests.yml: fast, coverage, typing, closures; governance env-matrix). Those ran at this head and are green.
- RESULT claims: `env_drift.py --claims-only <merge-base>` printed `claims hygiene: ... ok`, exit 0 (`ev/env-drift-claims-only.txt`).
- `env_drift.py --all` was not run locally. It compares two captures made in the same environment, so it cannot see a numpy version change; the CI lanes that install numpy 2.5.5 are the drift signal for the goldens, and they are green.
- RESULT untouched: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff (`ev/untouched.txt`).
- RESULT CI: the final `merge_train.py classify 2b8677d3... --pr 3853` printed `GREEN ... pending: none red: none`, exit 0 (`ev/classify-17.txt`). Earlier polls were WAIT on `gate`.
- Red checks: there are none at this head, so no owed-red answer is due.
