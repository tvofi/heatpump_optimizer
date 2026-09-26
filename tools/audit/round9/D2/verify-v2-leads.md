# D2 leads unit — verifier V2 (independent), box G3-V2

Run from a worktree of `handoff/audit-r9-evidence` at 96b89163 (baseline 1936d5ca production code), PYTHONPATH=tests/hastub, CPython 3.14.0rc2, numpy 2.4.6. Own harnesses: `tools/audit/round9/D2/verify-v2-leads/`. Votes with full strings: `tools/audit/round9/verify/votes-G3-v2.json`, key `leads`.

Tally: 3 verify, 0 weaken, 0 refute, 0 unresolved.

## D2-s1-51 — DHW advisor prices at the 5.0 °C default without an outdoor thermometer — **verify, low**
- **Finder re-run** (`leads/dhw_sweep_outdoor.py`, load1 0.96–1.05, tf 1.000): off_total_cold=14 of 14; worst rel err 0.527 (F = −15), 0.265 (F = −5), 0 (F = +5, control). `--forecast` zeroes every cell. Exact match.
- **Own** (`v2_dhw_cop_sensitivity.py`, load1 1.02, tf 1.001): `ThermalModel.compute_cop_dhw` at the 5.0 °C default vs the forecast outdoor, DHW flow 45–65 °C: COP overstated by 1.111 at −15 °C and 0.357 at −5 °C, constant across flow. Metric: |cop(5.0, flow) − cop(f, flow)| / cop(f, flow).
- **Attacks:** identity, not an aggregate; null (forecast equals default) 0; no executor path. The recommended setpoint is unchanged in every run; only the published cost_per_day is wrong.
- **Vote:** verify, low.

## D2-s2-81 — two-zone comfort floor halved; plans breach min_temp — **verify, medium**
- **Finder re-run** (`leads/l4_zone_floor.py`, load1 1.62/1.87, tf 1.000): two_zone_floor_deg_steps_sum 2.4672 (max 1.3144, two|dhw|winter_typical), single-zone 0.1471, flat 0.0000; `--perturb` 0.8574. Exact match.
- **Own** (`v2_zone_floor_check.py`, load1 1.16/1.23, tf 1.001): independently chosen subgrid (winter_typical, winter_narrow; DHW on) reproduces the worst cell at 1.3144 degree-steps; 0.0016 under the same in-memory perturbation. Source: exactly one `0.5 * weight * (` block (two-zone) against two unhalved `weight * (` blocks (single-zone scalar and batch) in `_comfort_terms` / `_comfort_terms_batch`.
- **Attacks:** grid artefact ruled out (identical worst cell on an independent subgrid); nulls (single-zone, flat) reproduced; the `_COMFORT_FLOOR_L1` comment ("tuned to the smallest value that removes the residual violations") corroborates tuning at the unhalved weight.
- **Severity:** bounded (max ~0.46 K below min_temp, cold/DHW cells); the shipped cost is correct for the plan it returns. Medium.

## D2-s4-81 — sysid refuses its own exact fit — **verify, medium**
- **Finder re-run** (`leads/l4_sysid_null_refusal.py`, load1 1.32–1.87, tf 1.000): null_refused 19, null_admitted 37, null_aborted 24 of 80 (timber_crawlspace 8, timber_slab 4, concrete_slab 5, masonry 2); `--perturb` null_refused 2. Exact match. The title's 43 is 19 refused + 24 aborted.
- **Own** (`v2_sysid_refusal_subgrid.py`, load1 0.72): 8-cell subgrid (timber_slab/masonry × 1960_1980/low_energy × floor/radiators at 4.0 kW, a pump size the finder did not use): refused 0, admitted 4, aborted 4, unchanged under `--perturb`.
- **Attacks:** the own subgrid's 0 refusals do not refute — it excludes timber_crawlspace (8 of the 19) and the pre_1960/post_2005 eras, and the finder's leave-one-out already shows the refusal is structure/era-concentrated. **Limit of this vote:** the independent arm did not itself reproduce a refusal; the verify rests on the exact finder re-run and the admit control (37).
- **Severity:** auto-adoption blocked on a real slice of housing stock; falls back to priors; nothing silently wrong. Medium.
