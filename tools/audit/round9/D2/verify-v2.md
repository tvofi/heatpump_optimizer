# D2 — verifier V2 (independent), audit round 9, box G3-V2

Worktree at 6f51db2c (baseline 1936d5ca plus evidence), branch handoff/audit-r9-evidence. Machine: 4-core linux cloud container shared with the D14 and D9 sub-seats. Python 3.14.0rc2, numpy 2.4.6 OpenBLAS pinned to 1 thread, scipy 1.17.1. Every command ran from the repository root with PYTHONPATH=tests/hastub.

Finder re-runs are in `verify-v2/rerun/*.out`. My harnesses are `verify-v2/v2_*.py`, with outputs in `v2_*.out` and `v2_*.pert.out`. Every number is a count, an identity or a ratio, so none is contention-sensitive; load1 and thread_factor are still quoted. No production file was touched: every perturbation was in memory. None of these findings is a test-gap claim, so verifier.md step 4 applies to none. No D3 re-runs.

Votes: 7 verify, 2 weaken (D2-s1-01 to low, D2-s3-02 to low), 0 refute, 0 unresolved. The machine-readable votes, with the full value and attack strings, are in `tools/audit/round9/verify/votes-G3-v2.json`.

## D2-s1-01 — Euler sub-step guard vs coupled stores — **weaken, low**

- **Finder re-run** (`s1/m1_stability.py`, load1 1.77, tf 1.0000): grid 69/3936 envelope violations, 52 with radius > 1, 50 diverged > 100 K, worst radius 1.3958; the two named examples give radius 1.5252 and 2.843e35 K; defaults 0/2, presets 0/3360. `--perturb=ratio1` (load1 2.05): all 0, worst radius 1.0000. Exact match.
- **Own measure** (`v2_stability.py`, load1 2.39, tf 1.0000): config-flow ranges sampled log-uniformly (seed 9902) instead of on a grid; own continuous RC matrix A, production n_sub, radius of I + A·h/n_sub; escape keyed on the production `simulate_step` trajectory. Single-zone 11/1500 escape (3 diverge), two-zone 16/1500 (11 diverge). Worst analytic radius 1.4797 / 1.5852; radius and escape agree on 1492/1500 and 1495/1500. With every mass ≥ 2 kWh/K, 0 of 902 escape; every escape has a store mass below 1 kWh/K (largest 0.993 and 0.963). `--perturb=ratio1`: 0/3000.
- **Metric:** share of accepted configurations whose passive 24 h production trajectory leaves [0, 25] °C by more than 1e-6 K.
- **Attacks:** contention n/a (counts). Grid artefact: none, the mechanism survives a random sample and the analytic radius confirms it. Null: defaults, presets and the plausible-mass subset give 0. Reach: masses are never learned, so only a typed config reaches this, and it needs a store below 1 kWh/K (about 860 L of water) coupled strongly, physically implausible for a house.
- **Vote:** weaken to low. The divergence is real (1e35 K), but its reach is a typo region with an obvious workaround.

## D2-s1-02 — coil debit vs scaled DHW draw — **verify, low**

- **Finder re-run** (`s1/m1_coil.py`, load1 0.93, tf 1.0004): 28/28 cells below 40 °C non-zero, max 0.405991 kWh, 0.054010 kWh at DHW 35 °C / wood 70 °C, null 3.275e-15. `--perturb=mixuse` (load1 0.89): 0/28. Exact match. A bare `--perturb` does not switch the harness; it needs `=mixuse`.
- **Own measure** (`v2_coil.py`, load1 2.65, tf 1.0013): hooked `dhw_coil_draw_reduction` and `simulate_dhw_step`; vanished = q_coil·dt − (nominal·scale − production `_step_dhw_draw_kw`)·dt. Own two-zone sweep with a manual valve and the coil, at the production pattern's peak draw 0.847 kW: 12/21 cells lose heat, exactly the DHW < 40 °C cells, max 0.121176 kWh/step; closed form q_coil·(1 − scale)·dt matches to 1.73e-17. Golden `wood_coil` published plan: 32 coil steps, none with DHW below 40 °C (minimum 43.33 °C), 0.000 kWh vanished. mixuse: 0/21.
- **Attacks:** energy identity, contention n/a. Physics: under any consistent refill model the wood loss must equal the heat the DHW tank is spared. Reach and null: the shipped coil plan never enters the regime; it needs a DHW tank below the mixed-use temperature with the coil firing. Magnitude about 0.12 kWh/step at a realistic draw.
- **Vote:** verify, low.

## D2-s2-01 — settlement caps ignore house_heat_loss_scale — **verify, high**

- **Finder re-run:** `s2/slab_cap_scale.py` (load1 0.93, tf 1.000): drift 1.4400 K/h, cap gap max 13.500 K (−4.725 min), 67.5 kWh unseen, hold ratio 0.3043..5.0000, null 1.34e-12; `--perturb` all 0. `s2/slab_cap_plan.py 2.0` (load1 1.71): savings overstated 0.393..13.427 over 6 cells (`winter_single_no_dhw` 60.175 → 49.376, `flat_prices` 18.300 → 6.172), end slab +0.015..+4.598 K. `slab_cap_plan.py 1.0` (load1 1.85): all 0.000. Exact match.
- **Own measure** (`v2_slab_cap.py`, load1 1.98, tf 1.0000): slab temperature that holds the room (two-zone: lower zone) at target with the pump off, by bisection on production `simulate_step`, against `slab_settlement_cap`; scale ∈ {0.3, 0.6, 1, 1.5, 2, 3} × outdoor {−10, 0, 8} × {1z, 2z}, shipped defaults, plant bound lifted. Gap up to −11.625 K (scale 3, 1z, −10 °C), −3.9375 K at scale 2/1z/0 °C, +4.07 K at scale 0.3. `hold_demand_kw` ratio 0.297..5.79. Null at scale 1: 2.2e-10 K. `--perturb`: 0.0000.
- **Attacks:** deterministic. Reach: the learner clamps the scale to [0.3, 3.0] (`coordinator.py:3990`, `const.py:1247-1248`), so every swept value is reachable; sign follows the scale. Null holds at scale 1. Flat prices: the overstatement survives (12.1 in `flat_prices`), a valuation error rather than arbitrage, as claimed. Leave-one-out: 12.127 with the largest cell dropped.
- **Severity:** published predicted_savings wrong and the objective's terminal cost distorted at any learned scale other than 1. High.

## D2-s2-02 — flow-bias clamp vs model curve — **verify, medium**

- **Finder re-run** (`s2/flow_bias_clamp.py`, load1 0.93, tf 1.000): fixed50 0.3683, fixed45 0.2282 (mean 0.1056), fixed40 0.0836; curve max 27.921 °C; 142/142 cells on the clamp; null (curve + 10) 0.0; `--perturb` (clamp 40) 0.0169. Exact match.
- **Own measure** (`v2_flow.py`, load1 2.03, tf 1.0000): 3 stress presets (`presets.derive`), sloped radiator plant supply = 21 + (21 − out), fed through `FlowCurveBias.observe` for 400 cycles. Curve max 24.32 °C, learned bias 14.63 K, up to 13.05 K of real lift unpriced. COP overstated 0.2157 with the flag on against 0.3057 with the flag off (shipped default). Null (plant at curve + 5): 0. Clamp at 60: still 0.1259 overstated, 8.35 K unpriced.
- **Metric:** max over outdoor −10..10 °C of compute_cop / _cop_law(out, None, real supply) − 1, bias learned from the plant; plus max K of real supply above curve_flow_temp.
- **Attacks:** null holds. Severity null: flag-off default overstates more, so this is an under-correction by an opt-in feature, not a regression; argues against high. Mechanism: on a sloped real curve the clamp is one of two causes, the other being the fixed `emitter_design_delta_t` 15 K setting the curve's slope; the finding's property and fix scope already name it, so it stands. The finder's REPORT "to_zero" under clamp removal holds only for flat-supply plants.
- **Vote:** verify, medium.

## D2-s2-03 — DHW-path settlement replays space-only — **verify, low**

- **Finder re-run** (`s2/objective_identities.py`, load1 2.81, tf 1.000): 6 mismatches, all `wood_coil`, max 0.419558 K (wood tank); savings overstated 0.4816 (0.306 % of baseline); cost_err and savings_err 0. `--perturb` (load1 1.64): 0. Exact match.
- **Own measure** (`v2_replay.py`, load1 1.49, tf 1.0001): stored heat Σ C·(replay end − published end), kWh. 8/8 `wood_coil` variants mismatch (wood 40/55/70/85 °C × DHW 45/55 °C): space stores 0.69..0.90 kWh, wood 0.10..0.28 kWh. Coil-disabled null 0.00. `wood_two_tank` has no DHW-path settlement.
- **Disclosed correction:** an arm first labelled a null (wood tank starting at 12 °C) is not one — the loop reheats the wood tank to 24.6 °C and the coil fires. It was relabelled after the run; it reads 0.945 kWh, consistent with the mechanism. The coil-disabled arm is the null.
- **Severity:** niche option, error 0.3 % of baseline. Low.

## D2-s3-01 — _current_spot_price under 15-minute entries — **verify, high**

- **Finder re-run** (`s3/current_quarter_price.py`, load1 0.89, tf 1.000): ramp 28..42 of 96 quarters (winter_typical 41, winter_extreme 42, summer_typical 39, summer_negative 28, shoulder 42, winter_moderate 42); step 12..18; hourly null 0; flat 0. `--perturb`: quarter arms 0, hourly null 273. Exact match.
- **Own measure** (`v2_spot.py`, load1 1.59, tf 1.0000): clock frozen at every minute of a day (1440 points), entries built by production `prices_from_tibber_payload` from a QUARTER_HOURLY-shaped payload in +01:00. Distinct quarter prices: 1425/1440 minutes mispriced, mean |err| 0.1829 per kWh. Hourly-constant quarters: 1035/1440 (45 of every 60 minutes after a change). Hourly-entry null 0/1440. `--perturb`: 0 and 0, null 1035.
- **Attacks:** Reach: `pull_prices` queries `TIBBER_PRICE_QUERY_QUARTER` first (`price_model.py:780`), rows land in `_prices` (`coordinator.py:5695`), "today" includes past quarters — the default install reaches it. Scope: the plan uses `_known_prices_for`, which bisects correctly; the wrong price reaches the published current price, the settlement's spot price (`coordinator.py:9332`), sysid and the comfort learner (`:10392`). Null holds.
- **Severity:** wrong published value and wrong settlement accounting on the default path. High.

## D2-s3-02 — import_margin zero floor — **weaken, low**

- **Finder re-run** (`s3/pv_piecewise.py`, load1 2.05, tf 1.000): breaches 16/96 on summer_negative at export 0.0 and 0.30, 20 on summer_typical at 0.30; signed error −5.04..0, mean −1.14 (−0.36 with the most negative cell out); solve predicted_cost −0.608961 against the law, 5.0747 kWh from surplus in negative steps; blended block breaches 16. `--perturb`: all 0, solve gap 0.000, 2.2733 kWh. Exact match.
- **Own measure** (`v2_pv.py`, load1 1.69, tf 1.0000): seeded partly-cloudy 8 kWp surplus. Closure vs net-meter law on 200 random schedules: max |err| 1.2398 (summer_negative @0.0), 1.5322 (summer_typical @0.30), 0 (winter). Real solves, summer_negative @0.0: published minus true cost of the same schedule −0.086553 floored vs 0.000000 unfloored; true cost of the floored plan minus the unfloored plan −0.034513 (the floor costs no money). summer_typical @0.30 and winter: 0.
- **Metric:** published predicted_cost minus the true net-meter cost Σ(export·min(P,s) + import·max(P−s,0))·dt of the same schedule; and true cost floored minus unfloored plan.
- **Attacks:** identity confirms the breach against the closure's own docstring law. Null holds. Money null: no measured money loss; the consequence is predicted_cost misstated by 0.09..0.61 on negative-price days, plus DHW block ranking in those steps.
- **Vote:** weaken to low: a real but small, seasonal published-value misstatement with no measured money or comfort loss.

## D2-s4-01 — sysid adoption interval coverage — **verify, medium**

- **Finder re-run** (`s4/coverage.py --seeds 40`, load1 2.12, tf 1.000): 22 admitted, 14 missed (0.636); finite-interval miss 0.583; bias +7.26 %, 21/22 positive, max +18.64 %; adopted scale error +2.71 % mean, +8.95 % max; cell miss 0.286..1.000, 0.611 worst dropped. `--perturb sigma0`: 0/12. Exact match.
- **Own measure** (`v2_coverage.py`): own driver, seeds from 777000 (disjoint), plant integrated with 6 sub-steps per reading on `simulate_step`, typical_slab and heavy_old, step capped at 3.5 kW. Outdoor 0 °C, sigma {0.01, 0.02, 0.05} (load1 2.42): 33 admitted, 24 missed (0.727), median z 1.445, bias +10.33 %, 32/33 positive, 0.947 worst cell dropped. Sigma-0 null (load1 3.00): 0/6 missed, median z 0.333 (the finer integrator adds a noise-free +1.4 % bias the interval covers). Outdoor 2 °C: 4 admitted, 4 missed, bias +18.9 %.
- **Metric:** among admitted fits, share with z = |log(UA_fit/UA_true)| / slab_ua_adoption_halfwidth > 1 (calibrated 95 %: ~0.05).
- **Attacks:** seeded counts. Independence: disjoint seeds, different integrator, different outdoor; miss share reproduces. Null holds. Caveat: admissions are rare (33 of 480 runs).
- **Severity:** admitted fits biased high and move the learned scale. Medium.

## D2-s4-02 — sysid step sized to the abort bound — **verify, medium**

- **Finder re-run** (`s4/sizer_margin.py --seeds 16`, load1 1.37, tf 1.000): 100/294 aborted, noisy-cell rate 0.000..1.000, mean 0.344 (0.305 max dropped). `--perturb margin` (load1 1.77): 3/294. Exact match.
- **Own measure** (`v2_sizer.py`, load1 0.83, tf 1.0000): production step from `_size_step_power`, production sizer plant path (`_held_state` / `_valve_drive`) sampled at the reading cadence, 4000 Monte-Carlo draws through production `_over_excursion` with a noisy baseline. Noiseless headroom 0.0015 K (light_new), 0.0139 K (typical_slab, at plant max), 0.5102 K (heavy_old). Abort probability, mean over 6 cells: sigma 0 → 0; 0.01 → 0.0181; 0.02 → 0.1288 (max 0.2182); 0.05 → 0.3162 (max 0.5657). A 0.1 °C-quantised sensor: 1.0000 on light_new and typical_slab, 0 on heavy_old (21.8 − 21.0 = 0.8000000000000007 > 0.8). `--perturb margin`: headroom ≥ 0.174 K, abort ≤ 0.0095, quantised 0.
- **Attacks:** null (sigma 0) gives 0. Reach: default interval 30 min; baseline is one noisy reading (`sysid.py:1364`); a quantised HA sensor makes the abort deterministic on 2 of 3 presets, so the finding understates the realistic case. Regime-specific: a plant with headroom does not abort.
- **Severity:** experiments never complete, nothing silently wrong. Medium.
