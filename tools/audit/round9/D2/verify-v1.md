# Round 9 verify, lens V1 (reproduce), dimension D2

Tree: 6f51db2c (baseline 1936d5ca plus round-9 evidence). Box: G3-V1 cloud container, 4 cores, CPython 3.14.0rc2, numpy 2.4.6, OpenBLAS pinned to 1 thread. `/home/claude/venv314` is absent, so commands naming it ran on `/home/claude/venv/bin/python`, the same interpreter. thread_factor was 1.000–1.002 on every run. Every number below is a count or a deterministic value, so load does not affect it.

Votes: 9 verify, 0 weaken, 0 refute, 0 unresolved.

## D2-s1-01: Euler guard ignores coupling (medium): verify
- **Re-run** (`m1_stability.py`, load1 0.85): grid 69/3936 configs leave the envelope, 50 diverge past 100 K, 52 have radius > 1. Worst radius 1.3958 (2-zone, n_sub=1). Examples: 2/2 diverge, radius 1.5252, excess 2.843e35 K. Split: 1-zone 6/864, 2-zone 63/3072.
- **Perturbation** (`--perturb=ratio1`): every count goes to 0 and the worst grid radius falls to 1.0000.
- **Null control:** defaults 0 violations; presets.derive 0/3360 (worst radius 0.9995).
- **Reach:** the grid endpoints are `config_flow.py` `RANGE_*` (lines 558-579), the bounds of the options schema. No derived house reaches the region, so reaching it needs typed values.
- **Metric:** configs whose zero-input 24 h trajectory leaves [T_out, max T0] by more than 1e-6 K, plus the max |eig| of the per-substep Jacobian.

## D2-s1-02: DHW coil conservation (low): verify
- **Re-run** (`m1_coil.py`, load1 1.71): 28/28 cells below 40 C are non-zero. Max 0.405991 kWh per step, min 0.003407, drop-max 0.362492. At DHW 35 / wood 70: 0.054010.
- **Null control:** 3.275e-15 at 40 C or above.
- **Perturbation** (`--perturb=mixuse`): 0/28, max 0.000000.
- **Premise check:**
  - `thermal_model.py:1311` debits the wood tank the unscaled coil heat.
  - `thermal_model.py:1860-1863` scales only the reduced draw.
  - With the same tap outflow, the DHW tank should lose scale*draw − coil. The model books scale*draw − scale*coil, so (1 − scale)*coil vanishes. The finder's identity is correct.
- **Metric:** per 15-min step, wood heat out minus DHW heat spared, in kWh.

## D2-s2-01: settlement caps ignore house_heat_loss_scale (high): verify
- **Re-run, `slab_cap_scale.py`** (load1 2.13): max drift 1.4400 K/h, cap_gap max 13.500 K, unseen slab heat 67.500 kWh, gap with the worst cell dropped 9.750 K, hold_ratio 0.3043..5.0000. `--perturb` gives all 0. Null at s=1: drift 0, gap 1.34e-12.
- **Re-run, `slab_cap_plan.py 2.0`:** savings delta −0.393..−13.427 over 6 scenarios; end slab +0.015..+4.598 K. With the worst scenario dropped: 12.127. `slab_cap_plan.py 1.0`: all 0.000.
- **Reach:** the learned scale is clamped to [0.3, 3.0] (`const.py:1247-1248`, `coordinator.py:3990`), which is the swept range. `_settlement_caps` passes raw params (`optimizer.py:6326-6328`). `slab_settlement_cap` (`optimizer.py:1621-1633`) and `hold_demand_kw` (1522-1525) omit the scale. The dynamics apply it (`thermal_model.py:1616-1618`).
- **Flat-price arm:** flat_prices savings go from 18.300 to 6.172. This is a valuation error, not a price-shift gain, and the s=1 arm is the matching null.
- **Metric:** room drift per hour at slab = production cap, pump off, room at target.

## D2-s2-02: flow-bias clamp cannot reach real supply (medium): verify
- **Re-run** (`flow_bias_clamp.py`, load1 2.70): fixed50 0.3683; fixed45 0.2282 (mean 0.1056); fixed40 0.0836; curve max 27.921 C; clamp-bound cells 142/142 per arm; null (curve + 10 K) 0.0, with 0 clamp-bound cells.
- **Perturbation** (`--perturb`, clamp 40 K): max 0.0169, 0 clamp-bound cells. Direction is down.
- **Own reach harness** (`verify-v1/curve_reach.py`, load1 4.10): over 1440 presets.derive houses (flow_curve_cop on), the curve max ranges 21.55..49.85 C. 1232 houses have curve max + 15 K below 45 C; 336 are below 40 C. Emitter choice does not move the curve max. `--perturb` takes both counts to 0. "Tops out at 27.9 C" is true only for the default houses, but the defect reaches 86% of preset houses at 45 C.
- **Severity:** the flag defaults off, which is consistent with medium.
- **Metric:** max over outdoor −25..10 C of compute_cop / _cop_law at the real supply, minus 1.

## D2-s2-03: DHW-path settle-up omits the coil (low): verify
- **Re-run** (`objective_identities.py`, load1 4.94): end_mismatch 6, all in wood_coil; max 0.419558 K on the wood tank; room/slab/upper/lower/buffer 0.037..0.086 K. Savings overstated by 0.4816 (0.306% of baseline). cost_err and savings_err are 0 on all 50 scenarios.
- **Finder perturbation** (load1 5.10): 0. This perturbation copies the published trajectory end into the replay, so it moves by construction.
- **Own mechanism perturbation** (`verify-v1/coil_off_settle.py`, the finder's harness on wood_coil with `dhw_coil_draw_reduction` returning (draw, 0) in the thermal_model and optimizer namespaces): coil arm 6 mismatches, 0.4816 overstatement; no-coil arm 0 mismatches, 0.0000. The coil coupling is the mechanism.
- **Null control:** the 49 non-coil scenarios read 0.
- **Metric:** stores where the settled end state differs from the published trajectory end by more than 1e-6 K.

## D2-s3-01: _current_spot_price one-hour span (high): verify
- **Re-run** (`current_quarter_price.py`, load1 3.92): ramp arm 28..42/96 quarters mispriced, step arm 12..18/96. MAE 0.04187..0.58438 per kWh, mean 0.18494, leave-max-out 0.10505. Hourly-entry null 0; flat null 0.
- **Perturbation** (15-min span): quarter arms 0, hourly null 273, as the header predicts.
- **Reach:** `price_model.py:779-792` pulls QUARTER_HOURLY first and falls back to hourly only on a parse failure. `coordinator.py:6333` uses a fixed one-hour span. The seam is read by current_price (6318), spot_price (9332) and the relative price (10392).
- **Metric:** quarters where _current_spot_price differs from the price of the covering entry.

## D2-s3-02: import_margin zero floor (medium): verify
- **Re-run** (`pv_piecewise.py`, load1 4.16): summer_negative 16/96 breach steps at export 0.0 and 16/96 at 0.30; summer_typical at 0.30: 20/96; signed error at 3 kW, export 0.30: −5.04..0, mean −1.14, LOO −0.36; solve predicted_cost −0.608961 against identity 0.000; surplus drawn in negative-price steps 5.0747 kWh; blended_block breaches 16.
- **Perturbation** (floor removed): every cell 0, identity gap 0.000000, surplus 2.2733 kWh.
- **Null control:** non-negative-margin profiles 0; no-surplus arm 0.
- **Curtailment defence:** at import < 0 with export 0, the floored price equals "curtail PV and import", but the integration commands no curtailment, so a net meter bills export*min(P,s). In the export 0.30 cells with 0 < import < 0.30, no action achieves the floored price. The breach stands in both cases.
- **Metric:** steps where _energy_cost_fn differs by more than 1e-9 from the piecewise identity.

## D2-s4-01: sysid interval under-covers admitted fits (medium): verify
- **Re-run** (`coverage.py --seeds 40`, load1 6.89): admitted miss rate 0.636 (14/22), bias mean +7.26% (21/22 positive, max +18.64%). Adopted scale error mean +2.71%, max +8.95%. Per-cell 0.286..1.000, LOO 0.611.
- **Perturbations:** sigma0 gives 0/12 missed, bias +0.00%. Anchor gives 0.439 (18/41). Both move as stated.
- **Robustness** (`--seeds 80`, load1 4.17): 0.627 (42/67), bias +8.24% (66/67 positive), adopted error max +14.35%, per-cell min 0.421, LOO 0.708. 14/22 against nominal 0.05 is far outside binomial range.
- **Severity:** the error after blending is a bounded UA cost of a few percent, so medium holds.
- **Metric:** share of admitted fits with |log(UA_fit/UA_true)| above the combined half-width.

## D2-s4-02: step sized to the abort bound (medium): verify
- **Re-run** (`sizer_margin.py --seeds 16`, load1 4.03): 100/294 aborted. light_new 81/96 noisy runs; at 0.5 h cadence 47/48. Noisy-cell abort rate mean 0.344, LOO 0.305, range 0..1. With every light_new cell dropped, 19 aborts remain (typical_slab).
- **Perturbation** (step × 0.85): 3/294.
- **Null control:** sigma 0 at 0.25 h gives 0; the light_new 0.5 h sigma-0 cell gives 1 (integrator dt, as recorded).
- **Mechanism:** `sysid.py:1208-1217` sizes to peak <= max_excursion_c (headroom only on two-zone plants). `sysid.py:1258-1263` aborts at the same bound.
- **Metric:** aborted experiments by reason string.

## Environment note
No production or tests file was edited; all perturbations ran in memory.
