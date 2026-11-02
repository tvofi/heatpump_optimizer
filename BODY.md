Re-centres the replay cost budgets on the second CI runner class (issue 3129) and pins two sites the 3078 review mutated. Measured only what ran.

## Head

46a4a63c8afb9d0a4bd01433601afae2908faa32 on origin/main 8fcaf47e1d6989b6c5f2a053aaa0f2b79c24067a (main unmoved since the base, so one prepr run).

## Red checks

- #3167's replay job: `synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.81 over its budget 2.173]`. Cheaper detector: the lane's own `record:` line, which already prints it; the cause is a one-class budget, the process state is "recorded on one class". Countermeasure: this re-centring on both classes. Inherited: #3167 changes only tests/replay.py (no cycle code), and the unmodified base on a 4-core box reads 2.0 to 2.14, the CI class reads 2.6 to 2.81, so the budget, not the branch, moved.
- Open, not fixed (outside the four items): the same base on this box reads synthetic `loop_cpu_ratio` 0.158 to 0.162 against 0.143, red at base on the faster-ruler class (loop_ref_ms 83 to 88). The CI class reads 0.0903. Carry: R10-REPLAY-COST-BUDGET.

## Mutation proof

- AWAY_COVERED literal misspelt (`...-awya.json`): `FAIL AWAY_COVERED names committed fixtures [owner-2026-10-30-awya.json: declares away coverage but is not a committed fixture]`.
- open_recorder's refusal as an f-string with the URL: `FAIL recorder:unsupported_scheme_refusal_prints_none_of_the_url`.
Both run with `PYTHONPATH=tests/hastub python3 tests/replay.py --fixture tests/replay/synthetic-dhw-only.json`, restored after.

## Null control

Correct literal: `ok control:away:covered_names_are_committed` pair and the real check pass. Non-credentialed URL (`ftp://core-mariadb/x`): same refusal text as the credentialed one, asserted equal. Synthetic budget null: base tree on this box, two flat runs cpu_ratio 2.0 and 2.1409. Owner fixture null: base tree, one run 264.1 against 409.7.

## Figures

- Owner cpu_ratio readings: 217.8 to 290.5 (earlier boxes, in the budget comment), 240.7 (#3167 replay job, ref_ms 30.4), 264.1 (this box, 808.6 s, ref_ms 31.9, loop_ref_ms 85), 385.3 (second CI class, as quoted in the brief; its log was not reachable here, so first-hand only for the others). Rule: sqrt(2) x geometric midpoint of the extremes, 217.8 and 385.3 = 409.7; the lowest is 53 % of it. M1 177 to 394 stays excluded. Command: `PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/owner-2026-10-30-away.json`.
- Synthetic cpu_ratio: 2.0, 2.1409, 2.105 (this box), 2.615 (#3167, as quoted), 2.81 (#3167 log). Same rule gives 3.353; lowest doubled 4.0 over it; this box's cpu doubled arm read 3.97, over it.
- peak_kib 3740 and owner loop_cpu_ratio 0.249 unchanged: new readings 2687 to 2709 and 0.134 to 0.196 sit inside both bands.
- No second-class record line for the owner fixture was reachable (the actions listing stopped at 2026-10-23); the 385.3 is the brief's figure, not mine.
- Instruments: `python3 tests/structure.py` PASSED; scoped gate MODE: SCOPED, 3 scripts (debug_collect, entities, features); prepr.sh clean.

## Unpinned sites

The two new checks are value checks in tests/replay.py, not custom_components/; no mutation-autofix site added. The tools/replay/export.py line is pinned by the in-tree mutant above.

## Carries

- Carry 1: the owner fixture's budget entry re-recorded; cpu_ratio 409.7 from the readings under Figures, null control the synthetic budget read flat on the base tree. The second-runner-class record line itself was not reachable here: 385.3 is the brief's figure.
- Carry 2: AWAY_COVERED names pinned against the committed fixtures, and the unsupported-scheme refusal pinned to print none of the URL; both with a null and a mutant under Mutation proof.
- Carry 3: the cost budget re-centred on the second class (cpu_ratio only; peak_kib and loop_cpu_ratio kept, with the reason under Figures). The synthetic cpu_ratio (the added fourth item) is re-centred the same way, from the two data points named under Figures.

## Forward-carry

Synthetic loop_cpu_ratio red on the faster-ruler class at base; the loop re-centring needs the same two-class readings. Lands in dev/programme/rosters/wave-r10-groups.json (group R10-REPLAY-COST-BUDGET). Carry: R10-REPLAY-COST-BUDGET

## Friction

none
