# D0-s3 — round 10, price optimality: M4/M5/M6 on summer_typical, summer_negative, shoulder, flat; M7 on all profiles

Baseline 17f1c55fad1b. Machine: macOS arm64 (box B3, shared, load1 21-62 during the fan-out). Every harness runs from the export root with
`PYTHONPATH=tests/hastub` and the venv-ci python 3.14. No wall/CPU number is used as evidence; all evidence is objective values and counts.
Exposure: none (no docs/, no GitHub read).

## Findings

None. Nothing measured in my cells meets the finding bar (a price-sensitive gap that survives the flat-price null control **and** is material on the day's bill **and** is realised under receding-horizon re-planning).

## Method and non-findings

### M4 grid race (race.py) — 80 cells: 4 price profiles x 5 weather x single/two-zone x DHW on/off, 24 h horizon
Captures every `optimizer._multi_start_minimize` call, takes the call whose x matches the shipped `power_schedule`, and races, through the same production `_multi_start_minimize` (same objective, bounds, args, batched jac path): production candidates + 13 structured seeds (price-ranked bang-bang at 0.1-1.25x the plan's energy, zero/flat fractions of headroom, the production x), then a maxiter 3000 / ftol 1e-12 polish (arm B, via `_scoped_minimize`). All challenger points are inside the recorded bounds; comfort is priced inside the objective.
- Control `--seeds prod --tight 0`: 80/80 cells gap 0.0000 % (race_prod.out) — the harness reproduces production exactly.
- Full race (race_full.out): 21/80 cells > 0.1 %, 2/80 > 1 %; max 5.06 %, mean 0.218 %, mean with the most favourable cell dropped 0.157 %; max absolute gap 0.523 objective units (~SEK).
- The two > 1 % cells are `summer_negative/shoulder` (5.06 % and 4.85 %) on objectives of 0.29 and 0.22 SEK/day: absolute 0.015 SEK/day — not material (D0 trap: 1 % of a 2 SEK day is not a finding).
- Largest material priced cell: single-zone, DHW off, `shoulder`/`winter_cold`: 0.998 %, 0.487 SEK on 48.8; step-0 differs by 0.21 kW. Decomposed: seeds only 0.757 %, budget only (production seeds, ftol 1e-12) 0.887 %.

### M5 null control (flat price)
20 flat cells: max 0.521 % (two-zone, DHW off, winter_cold, 0.52 SEK, step-0 diff 2.1 kW), mean ~0.11 %. The gap survives flat prices, so what the race measures is mainly L-BFGS-B termination at ftol 1e-6 (convergence slack), not price optimality. The flat arm at the same weather/topology as the largest priced cell (single-zone, DHW off, winter_cold) is 0.0001 %, so that one cell is price-shaped, but see M6.

### M6 receding-horizon masking (rolling_mask.py), shoulder/winter_cold single-zone DHW off, hourly re-plan over 24 h, plant == model
- production: realised 39.499 SEK, end-state terminal 8.901, score 48.400, floor 0.
- `--tight` (the arm-B budget): realised 39.039, terminal 9.076, score 48.115 (−0.285 SEK, −0.59 %).
- Null control flat: production 86.423 vs tight 87.214 (+0.79 SEK, tight *worse*). The realised gain on the priced cell (0.29 SEK) is smaller than the flat-arm swing (0.79 SEK) of the same perturbation, and the score omits the comfort-pull/cycling terms the solver trades, so the realised gap is not separable from noise: not a finding.

### M7 decomposition
- decomp.py, 64 cells (8 prices x 4 weather x 1/2 zones, DHW on): iterating `HeatPumpOptimizer._co_optimize` up to 6 times changes the objective in 0/64 cells (max gap 0.0000 %); the first pass adopts a replan in 3/64 cells and a second pass never adopts. Single pass is sufficient, as its docstring claims.
- decomp.py --cold (replan pass also solves space cold, full multi-start): vs production, 3/64 cells improve, max 0.287 % (summer_negative/winter_cold, 0.044 objective units). Not material.
- terminal.py (on vs --off, which zeroes both `_terminal_cost` closures), 64 cells: mean last-2 h kWh 3.85 -> 0.20, mean end room 19.90 -> 18.60 C, cells with a tail floor breach 1 -> 12. The terminal credit changes the plan the way its docstring claims (prevents tail dumping and tail floor breaches).

## Harnesses
- dev/audit/rounds/round10/D0/s3/race.py — M4/M5 capture-and-race
- dev/audit/rounds/round10/D0/s3/rolling_mask.py — M6
- dev/audit/rounds/round10/D0/s3/decomp.py — M7 iteration and cold replan
- dev/audit/rounds/round10/D0/s3/terminal.py — M7 terminal credit
Outputs captured beside them (*.out).

## Leads (not measured further)
- D0-s2: terminal.py production arm, single-zone DHW `winter_typical/winter_cold`: shipped plan ends at room 16.895 C with 0.232 degree-steps below the 17 C floor in the last 2 h, at full power in the tail (feasibility, winter axis).
- D0-s1: `_solve_space` (DHW path) never receives the `_DEEP_LOW_ENERGY_START_FRACTION` (0.20) two-zone seed that `_optimize_space_only` gets; the race found seeds-only gains on DHW two-zone cells (e.g. summer_negative/shoulder).
- D0-s1: budget/termination slack (ftol 1e-6) leaves up to 0.52 % at flat prices and 0.89 % on shoulder/winter_cold single-zone; M2 budget challengers own it.

## Unfinished
- M4 grid not extended to valve storage, wood, 6/48 h horizons and coordinator captures (race.py has --horizon but was run at 24 h only).
- M6 rolling ran only the one material cell, plant == model.
