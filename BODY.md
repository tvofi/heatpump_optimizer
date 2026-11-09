R10-BODY-CONTRACT part 3 bootstrap: registers `tools/pr/figure_block.py` as a pending DECLARED entry in `tools/policy/field_coverage.mjs`, so CI (which grades policy-docs with the base's copy) accepts part 3 pinning it in governance.yml. Same shape as ee2974270.

## Head

cdad1183b2309023682dad9a763552d508b2b4e3 (measured 2026-11-09, origin/main b8f67a775).

## Mutation proof

n/a: one declarative registry line in a policy data file; no production predicate. Deleting the entry makes `node tools/policy/field_coverage.mjs` fail once part 3 pins the script (not in this diff).

## Null control

The earlier seat stopped on prepr.sh refusing `closures failed while being recorded: tests/entities.py`: three checks (coverage cache key, release ZIP root, Pages deploy on tag) failed at that head and at unmodified main alike. Cause: cloud environment fault (dev/audit/rca/R10-RCA-CLOUD-ENTITIES-ENV.md), the setup script overwriting a caller's variables. Control: the same three fail at unmodified main without `env -u BASH_ENV`. Re-run here under `env -u BASH_ENV`: 0 failures.

## Figures

- `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` printed "ALL 2655 ENTITY CHECKS PASSED", rc=0.
- `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub env -u BASH_ENV bash tools/pr/prepr.sh` rc=0 (closures step skipped by design; closures-autofix owns it).

## Red checks

none

## Forward-carry

none

## Friction

none
