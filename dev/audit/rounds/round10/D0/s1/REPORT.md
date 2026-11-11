# D0-s1 report (round 10, baseline 17f1c55fad1b)

Method: `race.py` patches `optimizer:_multi_start_minimize` (D0.M1), captures objective,
candidates, bounds, args, maxiter, batch objective and result of every call inside
`HeatPumpOptimizer.optimize`, then races challengers on the captured objective (D0.M2):
C1 = production's own multi-start over production candidates + structured seeds
(price-ranked bang-bang at 0.3-1.3x energy, constant levels, prod.x); C2 = warm L-BFGS-B,
maxiter 5000, ftol 1e-12, same batched jac; C3 = C2 at fd eps 1e-6. Challengers count only
if their simulated room band violation is no worse than production's (D0.M3).
Grid: 8 price x 5 weather x single/two-zone, DHW off, 24 h (80 cells): `grid_dhw0.out`.

## Finding D0-s1-01 (low/medium, provisional class new)
Production returns plans above what its own minimizer reaches from a wider seed set on the
same objective: 26/80 cells gap > 1e-3, 2 > 1e-2, max 5.06e-2 (summer_negative, bill < 2 SEK),
mean 2.00e-3, mean with worst cell dropped 1.39e-3. Consequential cells: tz0 shoulder/winter_cold
8.8e-3 of objective (40 SEK bill), tz1 winter_narrow/winter_cold 5.1e-3 (1.93 SEK/day energy cheaper).
Null control: flat price max gap 4.98e-3 -- the gap survives flat prices, so it is a
basin/seeding gap of the solver, not a price-arbitrage miss.
Perturbation: `--perturb-maxiter 20` on tz1 winter_typical/winter_cold moves 3.99e-3 -> 5.80e-3 (up);
`--perturb-maxiter 2000` leaves it 3.99e-3 (production converges before budget).
`--perturb-fd-eps 1e-6` did not shrink it (8.24e-3): not an FD-step artefact.

## Non-findings
- Budget: maxiter 200 -> 2000 does not change any measured gap on the two-zone cells.
- Feasibility: 0 challengers discarded as comfort-infeasible across 80 cells.

## Unfinished
DHW-on arm crashed in the harness (`ThermalState` has no `dhw_tank_temperature`); horizons 6/48,
valve/wood topologies not run. No global outer bound (DE/DP) run.
Exposure: none.
