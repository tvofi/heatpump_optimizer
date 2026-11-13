# BLOCKED: R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE carry round

Question: the only pending carry (#3530 body item 50b08d86, carries 1 and 2; carry 0 dismissed as its duplicate) already holds at main e23124ff6e with no code change, so the code head's tree equals main's and `tools/pr/prepr.sh` refuses it (`[pr-body] --paths-file ... is empty. A pull request changes at least one file`). Should the relay mark the carry answered by #3512 (merge 754a2b022d) on the roster, or does the owner want a diff from this seat, and if so which?

Evidence at main e23124ff6e (head a3fb580a81, tree = main's tree; it is a merge of the stale step ref 860f73e0, kept only so this ref fast-forwards):
- `coordinator._write_supply` runs `supply_hold.hold_supply(...)` and then `pump_arbiter.write_supply(self, switch_entity, value)` for a value that is not None.
- `python3 tools/audit/seat/features_block.py --prelude 'exec(open("pre.py").read())' "# #3420 part E (Bankaifan)" "# The pump_duty record's held slots are declared"` (pre.py from `--emit-prelude`) printed `ALL 20 FEATURES BLOCK PASSED`, including "with the minimum pause engaged too, a cycle switch-on an early cut-off holds writes no mode ahead of the switch it holds back".
- Mutants at this head, each restored afterwards. Removing `hold_supply` from `_write_supply` turns 2 of 20 checks red ("a cycle switch-on the minimum pause holds back writes no mode and no switch"; "a switch-on held on one tick and landing on a later one writes the mode immediately before the switch on that later tick"). Calling the bare `switch_supply` instead of `write_supply` turns 7 of 20 red.

Not pushed: handoff/r10-outside-supply-min-run-pause and handoff-body/r10-outside-supply-min-run-pause. Both are unchanged.
