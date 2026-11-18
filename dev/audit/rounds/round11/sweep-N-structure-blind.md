# Class sweep: N-structure-blind (round 11, D14 steps 3-4)

Class status in `dev/audit/config/bugclasses.json`: `barriered` (tests/structure.py on the PR gate). Findings judged in this class: D7-s1-01, D7-s1-02, D7-s1-03, D7-s1-04, D7-s3-05.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/n_structure_blind.py`

It takes every key of `tests/structure_budgets.json` less `recorded_at`, plus the class mechanism's properties that no row measures, and reads each one against an independent recount from the round's D7 harnesses (`D7/s1/m1_ratchet_census.py`, `D7/s3/m6_inner.py`). Each seam prints as `SEAM <row> proxy|recount-ok|no-recount|unmeasured <evidence>`. Worktree `handoff/audit-r11-register` @ 28b864af6d; about 90 s per run.

## Controls (all exit 0)

| control | command | result |
|---|---|---|
| positive | `--control positive` | all five findings re-found: const_unseen_modules=1, in_function_copies=6, unused_package_imports=14, coordinator_py_unpriced_loc=2981, unread_params=16 |
| null | `--control null` | a clean two-module fixture package gives unread state 0; m1's `use-import` arm (an import that is used) leaves unused_package_imports at 14 |
| perturbation | `--control perturb` | one unused `from .const import` line appended to ledger.py: unused_package_imports 14 -> 15, ratchet_rows_off_budget stays 0 |

## Dispositions (every seam returned)

| seam | disposition | evidence / reason |
|---|---|---|
| const_modules_over_50 | instance, the site of D7-s1-01 | any spelling 4, ratchet 3 (entry_config.py: 3 counted, 120 read) |
| duplication_copies | instance, the site of D7-s1-02 | 6 in-function copies the owner rule cannot read |
| no row: unused_package_imports | instance, the site of D7-s1-03 | 14; the perturbation adds a 15th and no row moves |
| class_excess_loc | instance, the site of D7-s1-04 | 2981 coordinator.py lines priced by no row |
| dead_methods, dead_top_level_symbols, name_kept_members | instance, the site of D7-s3-05 | liveness is measured per definition only; 40 pieces of unread production state (params, locals, fields, attributes) |
| coordinator_private_reach, functions_cc_over_15, functions_cc_over_25, import_cycle_modules, max_cc, max_class_loc, max_method_loc, methods_over_150, methods_over_200 | guarded | m1's independent AST recount gives the ratchet's value (RECOUNT ok), and structure.py's counting-rule self-check fails on a regressed rule |
| coordinator_attrs, coordinator_multiassigned_attrs | not applicable | the metric counts attribute stores on the coordinator, found by role. That is the property itself, not a proxy for it. The round has no independent recount of these two rows |
| seam_cut_total | not applicable | it is priced from the declared seam map, not from a name or regex proxy for liveness or coupling. Whether a label is wrong belongs to a separate mechanism (m1 `--perturb seam-relabel`). The round has no independent recount of this row |

Every instance is the site of a judged finding, so instances beyond the findings = 0. Per D14 step 4 the class stays at one finding per seam. The barrier proposal belongs to the class's fixer: add rows for unused_package_imports and unpriced module LOC, make the const fan-out count reads instead of import statements, use a place-keyed clone owner, and add an unread-state census. None of this is drafted here.
