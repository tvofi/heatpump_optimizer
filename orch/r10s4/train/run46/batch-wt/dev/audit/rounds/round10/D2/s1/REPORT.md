# D2-s1 — round 10, D2.M1 (thermal model), baseline 17f1c55fad1b

Harness: `dev/audit/rounds/round10/D2/s1/m1_thermal.py`
(`PYTHONPATH=tests/hastub <python> dev/audit/rounds/round10/D2/s1/m1_thermal.py [--perturb tank_ambient_shift]`).

Nine cells: single, single with forced sub-steps (n_sub 5), two-zone without a valve,
two-zone with a manual valve (200 L and 35 L, n_sub 2 and 9), wood two-tank (500 L),
valve_upper_direct_slab, Carnot flow COP, and a forced-substep valve cell (n_sub 5).

## Findings
None. Every M1 identity held.

## Non-findings (executed)
- Per-call energy conservation (sum C_i dT_i = net flux minus refused heat), 3600 random
  states with wind, rain, solar, external heat and humidity: max residual 1.563e-13 kWh (tolerance 1e-9).
  The harness is not blind: the `tank_ambient_shift` perturbation raises it to 3.65e-3 kWh.
- Bit parity between `simulate_trajectory_batch` and `simulate_trajectory` on 9 cells × 4 rows × 6 tracks, plus wood:
  0 mismatches out of 216.
- More power never cools a store: 0 violations out of 540 (+0.5 kW).
- No store crosses a bound over 24 h of charge and coast: 0 violations.
- A buffer read 15 K above its cap cools 4.26 K in 15 min with no power, so the cap clamps a rate and does not snap the state.
- dt invariance (4×15 min vs 1×60 min) is first order, as Euler predicts. The largest difference is 0.26 K on the
  two-zone lower floor with no valve, and every valve cell stays at or below 0.19 K.

## Unfinished
- D2.M1 golden sweep: the bounds were checked on random states, not on every `tests/golden.py:SCENARIOS` trajectory.
- D2.M1 has no `measured_heat_kw` parity, because the batch twin takes no measured heat and has no counterpart to compare.

## Exposure
None.
