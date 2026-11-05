`bus.sh train_add` posted every merge verdict to `merge_train.py add` without reading the orchestrator's `cloud-handoff-hold` file, so a held PR (#3198, #3222 on 2026-11-05) was queued for the train anyway. `train_add` now asks `cloud_relay.sh held <pr>`, the relay's one reader of that file, and skips a PR it lists. Nothing is copied: the hold grammar stays in `hold_list`/`held`. A malformed hold file (rc 2) also skips the add, matching the relay's rule of never hold-none; `merge_train.py sweep` remains the backstop for a head the event add missed. No new file, seat or lane; claim files, VERSION and release notes are untouched.

## Head

58d7d839e7c900479b07fa5df22195de1b732f30 (one commit on origin/main 2dc960f4a92b1ebf56ed5aa33f55400d8e269a10). main had not moved since the `tools/pr/prepr.sh` run, so no second run was made.

## Mutation proof

The predicate line (`[ $rc = 1 ] || { printf 'BUS train-add ... held ...'; return 0; }`, marked `# mut:trainhold`) was replaced by `true`, then `bash tools/audit/seat/bus.sh --self-test` run. Red: `a PR listed in the hold file is not added to the train` and `a malformed hold file adds nothing (never hold-none)`; `bus self-test: 132 checks, 2 failed`. Restored; the same command reads `132 checks, 0 failed`.

## Null control

The tests were written first and run against the unmodified `train_add`: the two skip checks failed there. The null controls pass both before and after: a PR the hold file does not list is added, and an empty hold file adds as before (`BUS train-add <pr> rc=0 ADDED ...`, stub argv recorded).

## Figures

- `bash tools/audit/seat/bus.sh --self-test` prints the check counts quoted above (instrument: the bus self-test; 4 checks added).
- `tools/pr/prepr.sh` at the head: `PRE-PR: 58d7d839e7c900479b07fa5df22195de1b732f30 ... rc=0`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` reports `MODE: SCOPED`, one changed file (`tools/audit/seat/bus.sh`); `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.
- Environment: numpy 2.5.4 and scipy 1.18.1, matching `tests/requirements-ci.txt`; no golden is touched.

## Red checks

none (no pull request exists yet, so no check run has concluded).

## Forward-carry

none

## Friction

none
