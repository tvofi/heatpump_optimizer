# D0-s1 — round 11, price optimality, steps D0.M1–M3

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B1 (4 vCPU, shared). Exposure: none.

## Method

- **Universe** (`python3 dev/audit/rounds/round11/D0/s1/cells.py`, 144 lines): each scope file
  (coordinator.py, optimizer.py, thermal_model.py) × each of the 8 price profiles × the solve arms that
  file owns. optimizer.py: space-only and DHW at 6/24/48 h, two-zone DHW, and a manual-pin arm (space
  forced on 02–04 and off 17–19, hot water forced on 03–04 and off 06–07). thermal_model.py: two-zone,
  mixing valve over a 750 L buffer (manual and smart_write), the two-tank wood plumbing, the wood DHW
  coil. coordinator.py: the five `golden.coordinator_scenarios()` configs solved through
  `HeatPumpOptimizerCoordinator.async_run_optimization`, with profile prices and weather injected and
  `_await_optimize` run inline.
  The weather is winter_cold for winter_* and flat, summer_cool for summer_*, and shoulder for shoulder.
- **M1 capture** (`race.py`): `mock.patch.object(optimizer, "_multi_start_minimize", …)` records every
  call's objective, candidates, bounds, args, maxiter, batch jac and move_starts. It also hooks
  `_solve_objectives` (trajectory and horizon), `_dhw_build` (the DHW plan) and `_scoped_minimize`
  (status and nit of every L-BFGS-B run). Every challenger runs against the exact recorded callable and
  uses the same batched-jac path.
- **M2 challengers**, per call: `seeds` (production's candidates plus 13 structured seeds: bang-bang at
  0.1–1.5× the plan's energy and flat fractions of the headroom), `budget` (maxiter ×10, maxfun 150000),
  `eps-1e-6` and `eps-1e-3`, `global` (scipy differential_evolution over hourly blocks on the batched
  objective, then the production L-BFGS-B run and restart on the full grid) and `warm` (production
  run and restart from the best challenger at maxiter ×10).
- **M3 parity**: a challenger counts only if all of these hold:
  - bounds hold;
  - no extra manual-pin violation;
  - comfort degree-steps below floor and above ceiling, summed over the room and both zones on
    two-zone, are each no worse than production's plus 1e-3;
  - DHW degree-steps under the planner's `floor_temps` are no worse, re-simulated through
    `simulate_trajectory_with_dhw` with the call's fixed DHW plan.

## Coverage (all three steps: 144/144 cells, 183 multi-start calls, 1556 production L-BFGS-B runs)

- Redispatched work:
  - C1 (M3 had no denominator): examined over all 144 cells.
  - C2 (no global bound; DHW, 6/48 h and valve/wood arms not raced; harness crash): examined. The
    differential_evolution challenger ran on every call. The DHW, 6/48 h, valve and wood arms all ran.
    The harness never builds `ThermalState(dhw_tank_temperature=…)`.
  - C3 (no DHW or pin parity): examined. DHW-floor parity ran on 92 calls and pin parity on 18 calls.
- Aggregate (`race.py --aggregate`):
  - 43/144 cells have a gap over 0.1 % and 6/144 over 1 %.
  - The mean relative gap is 0.225 %, with a range of 0–6.67 %.
  - Dropping the most favourable cell gives 0.180 %.
  - All 1 %+ cells except the two-zone DHW cell are days on which the gap is ≤0.17 SEK: summer_negative
    and summer_typical coord_all_features, shoulder coord_minimal, summer_negative space-24h and
    shoulder space-24h.

## Findings

**D0-s1-01** (medium, P4): the DHW path's space multi-start (`_solve_space`) anchors its bang-bang seeds
on the smooth guess's energy. It has no thermostat seed and no two-zone deep anchor.

- Two-zone DHW gap: winter_typical 1.043 (1.18 %, on a 60.6 SEK energy day), winter_moderate 1.066,
  winter_extreme 0.483, winter_narrow 0.392, shoulder and summer ~0.
- Null control: at flat the seeds-closable gap is 0.041.
- Perturbation (the space-only path's thermostat anchors) brings winter_typical from 1.043 to 0.285;
  flat stays unmoved.
- Leave-one-out over the 7 non-flat cells: mean 0.426, which falls to 0.320 when the most favourable
  cell is dropped.
- The effect on energy money is mixed (see the finding file).

## Non-findings

- Budget does not bind: `budget` tied production on 183/183 calls, and 0 of 1556 production runs hit maxiter.
- eps has no consistent direction: `eps-1e-3` beat production on 47 calls and lost on 36; `eps-1e-6` won 20 and lost 42.
- Feasibility parity held: of 183 calls, one had a cheaper challenger that failed parity
  (thermal_model.py/summer_negative/wood-two-tank call 1: 5.07 against 6.73, comfort ceiling exceeded by 0.122
  degree-steps). It was rejected. Pin violations by production or by challengers: 0.
- The 6 h horizon: 0 gap on all 16 space-6h and dhw-6h cells.
- Two-zone space-only gaps survive flat prices (thermal_model twozone-24h flat 0.485; winter_narrow
  0.841; winter_typical 0.462). By D0.M5 this is not price optimality: it is the two-zone objective's
  basin non-convexity, which the `warm` polish or seeds reach. It is passed on as a lead to D0.M5.
- 135 of 1556 production L-BFGS-B runs end in a line-search abnormal termination (status 2). Production
  still matches its own challengers in most of those cells; this is an observation, not a finding.
- The `warm` challenger wins many small gaps (83 calls), but it duplicates the winner-only polish that
  #2612 refused, so no finding is drawn from it.

## Harnesses

- `cells.py`: the enumerator.
- `race.py`: capture, challengers, parity and the aggregate; per-cell JSON goes to `out/`.
- `anchor.py`: D0-s1-01's perturbation arm.

## Unfinished

None of the step universes. Limits:

- differential_evolution on hourly blocks is a global *challenger*, not a certified lower bound.
- The "previous cell's plan" seed was not used: the cells are independent solves, not an MPC sequence.
