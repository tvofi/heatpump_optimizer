Fix review: merge e560fd8215a8c60e769071044dfb5d73940a540c

bus-nonce: a1458e60fe54f82b7cb08a15adb72dce

## Verdict
Delta review of 1eadcbb3..e560fd8215a8c60e769071044dfb5d73940a540c ("ci: pin killed mutants"): pins only.

## Evidence
- Delta is 5 added files, all under tests/mutation_ledger/killed_by/coordinator.py/ (ev/delta.txt); zero production or test code changed (git diff outside the ledger is empty).
- Each pin's "old" line exists verbatim in coordinator.py at this head. Sites: _dhw_probe_temperature GUARD_OFF, _fold_measured_cop BOOLOP and GUARD_OFF, _learning_frozen BOOLOP and GUARD_OFF; each records tests/features.py going rc=0 to rc=1 (failed=4/4/6/31/13).
- Not re-run here: the mutants and the round-1 killed list. The pins' kill counts are the autofix's own, from mutation_table.py --pin-killed.
- git merge-tree against origin/main: clean.
- CI at this head (run 41125941628): typing, replay, browser, arch-instrument, briefs, closure-scope, hassfest, validate-hacs, env-matrix, budget-raise-gate green. tests / mutation, coverage, fast and closures were still in progress at review time; mutation is expected green because the pins record kills.
