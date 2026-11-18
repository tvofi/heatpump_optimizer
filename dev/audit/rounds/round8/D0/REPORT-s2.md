# D0 seat s2: structure the solver cannot see (round 8)

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree: `/home/claude/audit-r8/seats/D0-s2` (a detached git worktree, production untouched). Machine: a shared 4-vCPU cloud container at load1 8-24. Every number below is a count, an objective value or a cost from deterministic solves, not a timing. Thread pin: thread_factor 1.000 on every run.

## Method

- **Decomposition** (`s2_decomp.py`, method step 7). Wraps `HeatPumpOptimizer._co_optimize` and lets production run unchanged, then iterates the DHW re-plan and space re-solve up to 4 more rounds.
  - Gated arm: production's own pass, called again.
  - Ungated arm: re-plan DHW every round with `space_demand`.
  - A round is accepted only if it lowers the same objective.
  - Grid: 8 prices x 5 weathers, single-zone and two-zone, plus a 3 kW contention arm.
- **Terminal credit** (`s2_terminal.py`). Solves each cell with and without `_terminal_cost` and compares tail power, tail floor breach and savings.
- **Terminal-seed race** (`s2_termrace.py`). Captures the exact `_multi_start_minimize` objective the shipped plan was solved against, matched by plan and by DHW args. Then runs production's own `_multi_start_minimize` from the terminal-free plan.
  - Grid: 32 cells, the DHW path, and the valve, wood and horizon golden specs.
  - Control: seeding from production's own plan must give 0.
- **Closed loop** (`s2_rolling.py`, method steps 4 and 6).
  - Receding horizon over 2 days against a plant equal to the optimizer's own model, replanning every 2 h.
  - Realised bill plus end-state settlement through production `_stored_thermal_energy` and `_settlement_caps`.
  - Also reports degree-hours below the floor and below the comfort target.
  - Arms: h24, h48, h6 and h24 without the terminal term.

## Findings

None. Every lead in this seat's focus either held, or its apparent gap had another explanation (comfort bought, harness artefact). Those are recorded below.

## Non-findings

1. Iterating the DHW <-> space decomposition beyond production's single _co_optimize pass (gated: re-calling _co_optimize up to 4 times; ungated: re-planning DHW against the current space plan every round) lowers the production objective by 0 in every cell: 35 priced + 5 flat cells, single-zone, 6 kW default. Leave-one-out is trivially 0. Production's own second pass ran in 6/40 cells and was adopted in 1.
   - value: sz_cells_with_gap_gt_0.1pct=0; sz_gap_max=0.0000 pct; sz_prod_second_pass_ran_cells=6; adopted=1; null flat 0.0000
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_decomp.py`

2. Same decomposition race, two-zone, 35 priced + 5 flat cells: 0 cells with any gap, and 0 extra rounds were accepted in either arm.
   - value: tz_cells_with_gap_gt_0.1pct=0; tz_gap_max=0.0000 pct
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_decomp.py --two-zone`

3. Contention arm: with the compressor cut to 3 kW so that DHW and space heating compete, iterating still gains nothing (14 cells: 7 prices x winter_cold/shoulder). The second pass ran in 4 cells, was adopted in 0, and further rounds were never accepted. In winter_typical/winter_cold the DHW plan re-planned with space_demand is byte-identical to the first plan (max abs diff 0.0 kW), so the coupling term changes nothing there.
   - value: sz_cells_with_gap_gt_0.1pct=0; sz_prod_second_pass_ran_cells=4
   - command: `D0S2_PMAX=3.0 PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_decomp.py --quick`

4. The terminal credit changes the plan in the direction its docstring states. Zeroing _terminal_cost drives the mean last-2h space power from 2.11 to 0.00 kW (single-zone, 28 priced cells; 22 of them lower) and from 2.12 to 0.18 kW (two-zone). This is a horizon effect, not an arbitrage: it survives flat prices (tail 0.27-1.20 kW -> 0). The docstring's 'breaches the comfort floor at the tail' holds only marginally: 0/28 single-zone cells, and 6/28 two-zone cells totalling 0.019 degree-steps. Production itself breaches 0 in both.
   - value: sz tail 2.1113->0.0000 kW, breach 0/28; sz_dhw 2.1315->0.0000, breach 0/28; tz 2.1206->0.1796 kW, breach 6/28 (0.0189 degree-steps)
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_terminal.py [--two-zone|--dhw 1]`

5. MPC masking of the terminal credit: over a 2-day closed loop (the plant is the optimizer's own model, replanning every 2 h) the h24 run without the terminal term realises +0.35% (winter_typical/winter_cold), +0.62% (shoulder/winter_cold) and -0.03% (winter_extreme/winter_cold) settled cost. The term earns a small realised gain; removing it would not make plans cheaper.
   - value: d_adj +0.354%, +0.62%, -0.03% (3 cells; provisional grid, see unfinished)
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_rolling.py --weather winter_cold --arms h24,h24_noterm`

6. Using the no-terminal plan as one extra L-BFGS-B start on production's own objective (captured _multi_start_minimize closure, same bounds, maxiter and batch jac) finds no material basin. Single-zone no-DHW: gap mean +0.014%, max 3.76% on a 0.31-objective summer_negative cell (0.01 SEK), with 13 of 28 cells worse than production. DHW: max 0.96% (0.015 SEK), mean -0.15%. Topology specs (valve_storage x3, wood_two_tank, wood_coil, horizon_48h, horizon_6h): max +0.037%, mean -0.29%. Flat null in the same band. Control: seeding with production's own plan gives exactly 0 in 14/14 cells.
   - value: sz gap_mean 0.0143%, drop-best -0.1246%; sz_dhw max 0.9645%; spec max 0.0374%; seedprod 0.0000%
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_termrace.py [--dhw 1 | --specs valve_storage,valve_storage_low_target,valve_storage_smart_write,wood_two_tank,wood_coil,horizon_48h,horizon_6h,valve_storage_flat_prices]; D0S2_SEED=prod ...`

7. Horizon 48 h against 24 h in closed loop: h48 realises +1.31% (winter_typical) and +1.62% (winter_extreme) settled cost, but buys 13-10% less comfort shortfall (pull 68.8->59.7 and 83.9->75.7 degree-hours below target). It is -0.40% on shoulder and -0.76% on flat, where it has more pull. So the extra spend buys comfort the objective prices; it is not a planning loss. h6 realises +0.75% to +9.64% (winter_extreme), the expected cost of a short lookahead, and is not a defect.
   - value: h48 d_adj +1.307/+1.617/-0.40/-0.76 %; pull h24/h48 68.8/59.7, 83.9/75.7, 83.5/89.7
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_rolling.py --prices <p> --weather winter_cold --arms h24,h48[,h6]`

8. valve_storage_low_target: the terminal-free-seeded challenger reaches the same objective (+0.037%) on a bill of 43.14 SEK against production's 59.02 SEK, with 0 floor violations in both. The objective is flat along an energy-for-comfort direction (production runs 6 kW 20:00-24:00 to recover the house after the 16-20 peak), not a cheaper plan. Whether that exchange rate is right is D2's question.
   - value: Jprod 103.5395 vs Jch 103.5007; bill 59.02 -> 43.14
   - command: `PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D0/s2_termrace.py --specs valve_storage_low_target`

## Leads carried to other dimensions

D9: _co_optimize's second full space solve ran in 6/40 single-zone default cells and was adopted in 1 (0/4 at 3 kW), so it is mostly discarded compute. D5: _terminal_cost docstring says removing it breaches the floor at the tail; measured 0/28 single-zone, 6/28 two-zone at 0.019 degree-steps total.

## Harness artefacts caught during the run (not findings)

- The first `s2_termrace.py --dhw 1` run showed a 19.06% gap on summer_negative/winter_mild. The cause was scoring the shipped plan against the *last* captured `_multi_start_minimize` call, whose args are the un-adopted second-pass DHW plan. It is fixed: the harness now matches the call by DHW args and by plan, and the gap is now at most 0.96%.
- `viol()` in `s2_termrace.py` simulates without per-step valve targets, so its comfort-parity column is unreliable for `valve_storage_smart_write`.

## Harnesses

- `tools/audit/round8/D0/s2_decomp.py`
- `tools/audit/round8/D0/s2_terminal.py`
- `tools/audit/round8/D0/s2_termrace.py`
- `tools/audit/round8/D0/s2_rolling.py`

## Unfinished

The closed-loop horizon/terminal grid (s2_rolling.py) covered 4 cells for h24/h48 and 3 for h6/noterm, not the planned 7 prices x 3 weathers: at load1 12-24, one 4-arm cell took about 30 min. Two-zone rolling and the valve/wood topologies in closed loop were not run. The race's viol() ignores per-step valve targets, so its comfort-parity column for valve_storage_smart_write (0.829 vs 0.140) is a harness gap, not evidence. Bang-bang challengers were left to seat s1, whose area they are (seeding).

## Exposure

None.
