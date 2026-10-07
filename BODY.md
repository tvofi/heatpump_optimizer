Main's Governance `record` and `record-autofix` stayed red after the delivery rows moved from `docs/delivery/` to `dev/programme/delivery/`. Two stale spellings: `record-autofix` in `.github/workflows/tests.yml` still ran `git add docs/delivery` (matches nothing, so each beat read "nothing-owed" and no row was ever pushed), and its pin in `tests/entities.py` hard-coded the same string, so the pin blessed the bug. Separately the `record` job's friction step spawned `.claude/workflows/policy_lint.mjs` (gone since the move), so `friction_issues.mjs` refused: "did not answer for all 20 existing friction-issue key(s) (exit 1)". The pin now derives the directory from `record_row.row_path` (one source); `friction_issues.mjs` spawns whichever policy_lint home exists. The `record` job's own error (rowless #1995, #2003) is real and clears once the autofix lands. No policy file, budget or claim file touched. #2002 untouched.

## Head

575990af6d319c4851aec6c802b786cf46bef4ec

## Mutation proof

- Old spelling restored in the pin (before the workflow fix): `tests.yml's record-autofix job: ... guarded write set` FAIL, adds=['git add docs/delivery', ...].
- `STATS_RUN = STATS_TOOL` in `friction_issues.mjs`: `FAIL the spawned stats tool exists on disk`, 100 passed, 1 failed.

## Null control

Unmodified main: run 37577849702 `record` job fails on #1995/#2003 and on the friction step (exit 1). With the fix: `tests/entities.py` 2188 of 2188 pass, `friction_issues.mjs --self-test` 101 passed, `record_row.py --self-test` all checks pass.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2188 ENTITY CHECKS PASSED`
- `node tools/policy/friction_issues.mjs --self-test` prints `101 passed, 0 failed`
- `python3 tools/audit/seat/record_row.py --self-test` prints `all checks passed`
- Scoped gate: `GATE_SCOPE=auto ./tests/run.sh` printed `MODE: FULL` (tests.yml is a gate file); not run to completion locally, CI is authoritative.

## Red checks

main `record` (rowless #1995, #2003): cause is the unlanded autofix; cheaper detector: the pin should have read the generator's path, now does. `record` friction step: cause is a path written for a moved file; a self-test arm now pins the spawned tool on disk.

## Forward-carry

none

## Friction

none
