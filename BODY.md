Root-cause seat (`R10-RCA-SAV-ESTIMATE`) beside `fix-savings-est`, for a savings defect that reached v7.0.4 and v7.1.1 on the owner's third savings report in three weeks. No production code changes here. The record is `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`: the cause reproduced, process state (c) with its evidence, the class search, the cost test, and the countermeasure. It registers class `N-unmetered-reference` in `dev/audit/config/bugclasses.json`, which also adds the id to `finding.schema.json` and `.claude/workflows/audit-find.js` through `fold_ledger.py sync`. Part of #2492.

The hypothesis was incomplete. On v7.1.x there are two independent causes of the zero booked step, the wood term and `valve_charge_demand`, and the second reaches every valved install with no wood tank.

## Head

`d8eeae8f8e51bee189ef133f8babdb91e5c3d916`. The harness arms ran at v7.0.4, v7.1.1 and main at `2a9cd3476`; this branch changes no file they import.

## Mutation proof

The census is the check. The defect is its mutation: `dev/audit/harnesses/r10_rca_sav_estimate.py census` exits 1 at v7.0.4, v7.1.1 and main, with 4 of 6 cells out of band, and exits 0 on main with a planted booking of the horizon mean. The planted pass is weak by construction. The pass at the fix's head is owed and carried below.

## Null control

The `single` and `unvalved` census cells stay in band on every defective tree (1.00 and 0.92). A missing `baseline_kw` raises and a cell that did not run exits 1, so the check does not go green by skipping.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py census`: the census table, at each tree named.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py blind`: #2411's metric on the installs it never ran.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py attrib BUNDLE` and `ledger BUNDLE`: ratios from the owner's export, which is not in the tree.
- `python3 tools/audit/fold_ledger.py check`: `0 violation(s)`.
- `node tools/policy/check-wave-script.mjs`: `224 passed, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Cost test: the commands and numbers are in the record's `## Cost test`.

## Red checks

`none`

## Forward-carry

- The second cause, the valved no-wood reach, the already-booked rows and wiring the census as a `tests/` script. Carry: #2492
- The meter band on the published row, including `notifier.py:90`, which needs its own fixer. Carry: #2492

## Friction

`none`
