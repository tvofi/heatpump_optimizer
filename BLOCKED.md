Question: two fixer seats hold R11-OUTSIDE-HONEST-DHW-RUNS (#3709) again. This seat was fired as the single owner by a FRESH RESUME brief (dispatch/fixer-r11-outside-honest-dhw-runs f82ff94a46, PROMPT.md: "Two earlier seats went idle ... you are now the single owner", start state ddc4090264). The r3 seat is not idle: it pushed 4bb2f9869c (pin shard 2/8) and 4d8293da92 to this ref at 08:18Z, after that brief was rendered. Which seat continues to the handoff? This seat has stopped and pushed nothing to handoff/ or handoff-body/.

What this seat leaves on this ref, on top of the r3 seat's 4d8293da92 (nothing of it dropped):
- 2c0f244bba: the six shard-1 survivors the inbox ruling 13deb4b14d names, each with a disposition, each mutant run against tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block with tools/audit/seat/features_block.py (block-mode baseline: 1 failed of 50, the check "combi: the exchange leaves its rounds when a round's plan repeats the one before", 4 of 4 rounds; whether that check fails in a full features.py run here was not measured).
  - dhw_planner.py:615 `t >=` -> `t >`: killed by the new check "the store program keeps a store that coasts exactly onto its floor bound ..." (2 failed with the mutant).
  - dhw_planner.py:615 `j < width` -> `j <= width`: killed by "the store program's grid ends at its top knot ..." (2 failed).
  - dhw_planner.py:615 `j >= 0` -> `j > 0`: equivalent (lo <= min floor - 1 K puts j >= 4 wherever the first conjunct holds); 1 failed (no added failure). The line's anchor 8e6c71cd is therefore under survivor_triage, its reason naming the two kills.
  - dhw_planner.py:684 CLAMP_DROP: killed by "a space plan under zero commits as no space plan ..." (2 failed); killed_by row 92461313.
  - optimizer.py:2106 `<=` -> `<`: killed by "combi: the committed build ships where its store falls exactly the slack further ..." (2 failed); killed_by row a94c3e31.
  - dhw_planner.py:590 `<` -> `<=`: equivalent: bisecting the step's ceiling to adjacent floats steps the level from 0.9999999989999981 to 0.9999999990000011, over the bound 0.999999999; triage row f5054d73.
- This seat's pin shard 2/4 run was stopped unfinished on finding the r3 seat; the r3 seat's shards run with N=8, so the two seats' shard numbers do not compose.

Not done by this seat: the remaining pin shards, the origin/main merge (tests/features.py, tests/structure_budgets.json), prepr, body, handoff.
