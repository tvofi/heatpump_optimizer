# BLOCKED: merge repair of #3882 (R11-OWNER-FROST-HOLD) needs a 1-line max_class_loc raise

Question: may tests/structure_budgets.json record max_class_loc 7834 -> 7835 (+1, against main's table) for the merged head 7b4fc7209e486c04fccf7aff74927fe934b81d4c? CLAUDE.md rule 2 says this needs the owner's explicit confirmation before handoff/r11-owner-frost-hold moves. Until then that ref is untouched at d05081fb.

The merge head 7b4fc7209e486c04fccf7aff74927fe934b81d4c merges origin/main d3d66c40 into d05081fb. Both parents are in this commit's history.

- Conflicts: coordinator._write_supply and two skip-log blocks in tests/features.py. They are resolved as a union. Main's supply_hold.supply_write (cooling and blocked-mode gate, logging its own skip) sits under supply_hold.hold_supply, under frost_hold.gate (last). The frost-hold skip log moved into frost_hold.gate, where the hold is decided, so frost_hold.log_skip and the coordinator's elif are deleted. The features.py skip-log checks listen on supply_hold._LOGGER (main's side).
- python3 tests/features.py at the merged tree: ALL 6226 FEATURE CHECKS PASSED.
- Frost-hold block (features_block.py, prelude emitted at the merged tree): ALL 55 FEATURES BLOCK PASSED. All 18 of the body's mutants were re-run on the merged tree, plus a 19th (the gate's frost-hold skip log removed). Every one fails the block; there are 0 survivors.
- tests/structure.py at the merged tree: class_excess_loc 17287 (main 17290), module_excess_loc 21761 (main 21763), max_class_loc 7835 (main 7834). Both of those lower rows are recorded. max_class_loc is left at 7834, so the ratchet fails that row by 1.
- The ledger driver's sums (17281 / 7829 / 21755) are not a measurement: they count twice the 6-line coordinator skip log that both sides deleted.
- Payment already made: the frost-hold skip log moved from the coordinator into frost_hold.gate, which is -3 class lines (7838 -> 7835). The remaining +1 is the PR's `outdoor_c=frost_hold.outdoor_reading(...)` field in HeatPumpOptimizerCoordinator.arbiter_inputs. Its inputs (input health, weather forecast) are coordinator state, and the frost latch reads that field.
- No further payment found that is not a reformat. Reflowing the 4-line `disinfecting=` expression in the same method would be a reformat, which gaming the score cannot pay.
- Not run: the scoped gate, prepr.sh and archscore for a `## Raise justification`. All of these are pending the ruling.
