# BLOCKED: merge repair of #3882 (R11-OWNER-FROST-HOLD) needs a structure budget raise, now on two rows

Question: may tests/structure_budgets.json record max_class_loc 7832 -> 7833 (+1) and module_excess_loc 21763 -> 21773 (+10), both against main 91773476's table, for the merged head below? CLAUDE.md rule 2 and the merge scope say a raise needs the owner's explicit confirmation before handoff/r11-owner-frost-hold moves. That ref is untouched at d05081fb.

This commit merges origin/main 91773476 into the previous BLOCKED head 76d5d1e3 (which merged main d3d66c40 into d05081fb). The previous fire's question (max_class_loc +1) is still open and is carried here.

- Conflicts at this merge: config_flow.py _OPTION_FIELDS (union: main's CONF_FLOW_HEAT_C row on _WATER_LIMIT_C plus the PR's two frost-hold rows); pump_arbiter.py step_duty and _arm_space docstrings (both sides shortened the same prose; main's wording taken); docs/architecture.md and D6 claims.py/claims.md, tests/deployment_shape.py #1218 note (both sides added a module: frost_hold.py and main's flow_limit.py). coordinator.py and tests/features.py merged cleanly onto the previous fire's resolution.
- Counts: D6 claims.py at the merged tree reports claims_false=0, arch_modules_on_disk=104, arch_map_listed=104, missing=0. The deployment_shape note's "all 122 files" total is not yet re-derived from tests/entities.py.
- tests/structure.py at the merged tree: class_excess_loc 17285 (ok), max_class_loc 7833 (main 7832), module_excess_loc 21773 (main 21763). The ledger driver's sums are not a measurement.
- Where the +10 sits, per module past MODULE_LOC_LIMIT, merged vs main: pump_arbiter.py +13, config_flow.py +1, coordinator.py -1, thermal_model.py -3. On its own branch the PR paid pump_arbiter's frost-hold lines (ArbiterState and ArbiterInputs fields, desired(frost=), _hold_floor_c, the _arbitrate/_lead_mode/_observe frost paths) by shortening docstring history prose. Main has since shortened the same prose (step_duty, _arm_space and others), so that payment is counted only once and the PR's lines show again.
- The +1 class line is the previous fire's: the arbiter_inputs `outdoor_c=frost_hold.outdoor_reading(...)` field.
- No further payment found in a merge-repair scope. pump_arbiter.py has no remaining history prose of size; a 10-line payment would be a refactor beyond the reviewed diff.
- Not run: the scoped gate, prepr.sh, a re-run of the frost-hold block and its mutants on this tree, and archscore for a `## Raise justification`. All of these are pending the ruling.
