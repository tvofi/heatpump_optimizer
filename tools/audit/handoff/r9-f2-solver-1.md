<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Round-9 fix F2.1, the solver lane's first PR. Five findings at four solver seams, each driven through its production symbol:

- **D14-s4-01**, the optimizer seam only. `get_current_action` now measures the step length and the pre-horizon gap in epoch seconds, and finds the covering step by instant. Two datetimes sharing one ZoneInfo subtract and compare as wall clock. Across the spring transition a 15-min step read as 75 min. In the autumn fold, the repeated hour matched the wrong step. The coordinator, accuracy, dhw_learning and external_heat seams of this finding are F1.1's and stay open here.
- **D12-s2-03**. One helper, `optimizer._power_fraction`, now owns where a planned power sits in the modulation band, clipped to [0, 1]. The four sites that normalise power use it: `_zone_setpoints`, `_power_to_setpoints`, `_power_to_displace_schedule` and `get_current_action`.
  - A band narrower than `_MIN_MODULATION_BAND_KW` is a fixed-speed pump. Its steps are graded against its one running power, instead of flooring the band at 0.1 kW.
  - Behaviour change on a fixed-speed pump: a full-power step now maps to the top of the setpoint, zone-setpoint and ECL110 displace ranges, where it used to map to the bottom. A modulating pump's figures are unchanged inside its band.
- **D2-s2-81**. Each zone of a two-zone house now pays the single-zone `_COMFORT_FLOOR_L1` per kelvin under `min_temp`, in both twins. The quadratic undershoot and the overshoot stay averaged.
  - This is a design choice. I measured both forms on the 14 two-zone golden scenarios (`## Figures`), and pricing the quadratic in full as well left more degree-steps under the floor.
- **D2-s3-02**. `pv.import_margin` is signed. The piecewise identity export·min(P,s) + import·max(P−s,0) now holds at both PV pricing seams for any sign of import − export. The old `features.py` pin on the zero floor is rewritten to pin the signed margin.
- **D5-s2-51**. The warm-start docstring and the `buffer_temp_trajectory` comment now say what the code does.

Part of #1665 (P7); Part of #1654 (P3); Fixes #1666 (N-sign-floor); Part of #1645 (I5); Part of #201.
Leaves D14-s4-01 open: its seven coordinator, accuracy, dhw_learning and external_heat instance sites are F1.1's.
Class P3's RCA seat is the round-9 P3 RCA (`/mnt/project-files/audit-r9/rca/p3/RCA.md`). Its barrier lands in F1.10. P7, N-sign-floor and I5 have no RCA seat beside this PR.

## Head

6178adf5cd8747a8d59e3dc16706fa60ac96c94a, merge base 6169b74c5049a8ef8382ac8d31d3d174813371d7 (origin/main, v6.7.2).
The handoff transport commits that follow carry only this body and the resume note. They are stripped before the push.

## Mutation proof

Each mutant was applied to a copy of the head tree and run through the new `R9-F2.1` block of `tests/features.py`. Harness: the block sliced between its marker and `# -- #1524`, runner and log in `## Figures`. The restored tree passes 14 of 14.

- M1, `get_current_action` back on wall clock (`.replace(tzinfo=None).timestamp()` on both sides): FAIL `R9-F2.1 P7 (spring): a clock 30 min before a 15-min plan is beyond one step, so the action idles`, FAIL `R9-F2.1 P7 (autumn): the step covering now is the one whose instant precedes it, not the one whose wall clock does`.
- M2, `_power_fraction`'s narrow-band branch back to the 0.1 kW floor (`low, band = p_min, 0.1`): FAIL `R9-F2.1 P3: an on/off pump at full power publishes 'boost' at 1.0, and off publishes 0.0 -- never outside [0, 1]`, FAIL `R9-F2.1 P3: every site that normalises planned power puts an on/off pump's full-power step at the top of its range and off at the bottom`.
- M3, the clip removed from `_power_fraction`: FAIL `R9-F2.1 P3: a modulating pump's published fraction is clipped to [0, 1] outside its band`.
- M4 and M5, the linear floor price halved again in `_comfort_terms` or in `_comfort_terms_batch`: FAIL `R9-F2.1 P3: one zone-kelvin under min_temp is priced at the single-zone room's linear floor price (scalar)` and `(batch)` respectively. Each mutant fails only its own twin.
- M6, the zero floor restored in `pv.import_margin`: FAIL `R9-F2.1 N-sign-floor: the objective charges surplus-covered energy at the export price whatever the sign of import - export`, FAIL `R9-F2.1 N-sign-floor: a hot-water block's blended price is the same identity at every sign of the margin`.

The same block at the merge base fails 9 of 14, the four null arms passing. D5-s2-51 is a comment fix with no production line to mutate. Its control is the seam grep in `## Figures`.

## Null control

- P7: the same plans on ordinary Sundays (2026-03-22, 2026-10-18) pass at base and head. The replay harness's plain day reads 0 wrong sites at both ends.
- D12: the modulating house's fraction inside its band is unchanged, and the check passes at base and head. The finder's modulating arm reads 0 mislabelled at both ends.
- D2-s2-81: the single-zone arm of the finder's harness reads 0.1471 at both ends. The block pins the quadratic undershoot and the overshoot still averaged, at half the single-zone curvature and price.
- D2-s3-02: an ordinary import > export step is priced identically at base and head. The finder's no-surplus and non-negative-profile arms read 0 at both ends.
- Goldens: every fixture outside the two-zone family is byte-identical to the merge base in the same environment (`env_drift.py --all`).

## Figures

All runs: CPython 3.14.0rc2, 4-core Linux cloud container, OMP/OpenBLAS pinned to 1 thread, PYTHONPATH=tests/hastub. "base" is 6169b74c (db878b29 for runs before the stamp merge; no file the harnesses read differs between the two). "head" is the fix tree. Finder harnesses were run from an export of evidence commit 79aa98ec as `$EXPORT/<path>`; sweep enumerators from exports of their sweep commits as `$SWEEP_Sn/<path>`.

- D12-s2-03, `$EXPORT/tools/audit/round9/D12/s2/onoff_label.py` (sha1 94575dbd):
  - `onoff_full_power_mislabelled`: 149 → 0.
  - `onoff_power_normalized_min`: -60.0 → 0.0.
  - `modulating_norm_out_of_range`: 585 → 0.
  - `modulating_full_power_mislabelled`: 0 → 0, the null arm.
- D2-s3-02, `$EXPORT/tools/audit/round9/D2/s3/pv_piecewise.py` (sha1 366ba01d):
  - `blended_block_breach_summer_negative_export0.00`: 16 → 0.
  - `solve_predicted_cost_minus_identity`: -0.608961 → 0.000000.
  - `solve_surplus_kwh_in_negative_steps`: 5.0747 → 2.2733.
  - `null_no_surplus_abs_err`: 0 → 0, the null arm.
- D2-s2-81, `$EXPORT/tools/audit/round9/D2/leads/l4_zone_floor.py` (sha1 2a9ddfdc):
  - `two_zone_floor_deg_steps_sum`: 2.4672 → 0.8562. That equals the value the finder's own `--perturb` printed (L1 doubled).
  - `single_zone_floor_deg_steps_sum`: 0.1471 → 0.1471, the null arm.
  - The rejected form, quadratic and linear both at full price, read 1.6225 on the same harness.
- D2-s2-81, the form choice, on 14 two-zone golden scenarios.
  - Instrument: a script calling `golden.capture` per scenario and summing max(0, min_temp − T) over both zone trajectories.
  - Summed degree-steps: 15.68 at base, 14.46 with the full-price form, 10.55 with the shipped linear-only form.
  - Per scenario, base → head, degree-steps then predicted_cost:
    - everything_on 0.276 → 0.896, 59.07 → 59.49 (the one clear regression: a different basin, see Friction).
    - tariff_plus_two_zone 0.497 → 0, 71.28 → 73.81.
    - valve_storage 2.108 → 1.251, 42.53 → 42.72.
    - valve_storage_smart_write 1.201 → 1.251, 41.67 → 42.72.
    - valve_upper_direct_slab 0.822 → 0.265, 41.41 → 42.68.
    - winter_two_zone_dhw 1.314 → 0, 67.50 → 70.52.
    - winter_two_zone_no_dhw 1.139 → 0.856, 57.98 → 58.85.
    - wood_coil 2.841 → 0.732, 38.44 → 40.36.
    - wood_two_tank 2.251 → 1.986, 32.33 → 31.73.
    - wood_two_tank_smart_write 1.916 → 2.022, 28.43 → 28.10.
    - shoulder_two_zone unchanged.
    - The three claimed fixtures are in `tests/golden/claimed_drift.txt`.
- D14-s4-01's optimizer seam, `$EXPORT/tools/audit/round9/D14/s4/p7_replay_clock.py --zone-clock` (sha1 b3186ee5), run from a tree with the evidence tools under it, since it reads `tests/replay/` relative to itself:
  - `replay_wrong_sites`: 10 → 9. The site that left is `optimizer.py:7003` (spring).
  - The nine sites left are F1.1's seven instances (accuracy.py:182, coordinator.py:4684, 6207, 9205, 9405, 9445, dhw_learning.py:347, external_heat.py:206) plus tariff.py:58, which is not applicable.
  - Without `--zone-clock`: 0 → 0, the null arm.
  - The tracer measures `-` and `+timedelta` only. The autumn-fold comparison is pinned by the block's P7 autumn check.
- D5-s2-51:
  - `$EXPORT/tools/audit/round9/D5/leads/dataflow_comments.py` (sha1 dd728b51) reads flat at both ends: `handed_offset_steps=0`, `elapsed_steps=2`, `model_sequence_writes=0`. It measures the data flow the fix rightly leaves alone.
  - Companion, the finding's own seam rule: `grep -c 'one step later\|stashes the series' custom_components/heatpump_optimizer/optimizer.py` reads 2 → 0.
- Evidence travels on the handoff branch under `tools/audit/handoff/r9-f2-solver-1/`, stripped before the push:
  - `run_block.py` execs `tests/features.py` from `# -- R9-F2.1:` to `# -- #1524`.
  - `mutate.py` applies M1–M6 to a copy of the head tree and runs it; its log is `ev/mutants.log`.
  - `dir.py` produces the golden degree-step and cost table: `ev/dir_base.json`, `ev/dir_fullprice.json`, `ev/dir_head.json`.
  - Every harness log above is `ev/<finding>_{base,base314,head,final}.log`.
- Gate, scope derived per `fixer.md` step 5 on the head less the handoff files: `MODE: SCOPED -- 22 script(s) run, 4 scoped out`. Every scope.run entry was run except `tests/stress.py`, which is left to CI. `GOLDEN_MODE=drift` against the merge base: results below.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget touched.

### Class sweeps (fixer.md step 8)

- **P7**, `$SWEEP_S7/tools/audit/round9/D14/sweep/P7/p7_static_sites.py` (sha1 99bc40b0): `candidates=74` at both ends.
  - It does not list `get_current_action`'s site at base either. Its regex keys on names like `*stamp`/`start`, and `result.timestamps` matches neither. The run-time tracer above is what reached it.
  - Seams by the sweep's list: the optimizer seam is closed here. Seven instances (coordinator.py `_forecast_arrays`, `_next_optimization`, `_record_accuracy`, `_file_dhw_lead_predictions`, `_file_lead_predictions`; accuracy.py `score_lead_predictions`; dhw_learning.py `async_learn_dynamics`; external_heat.py `_rate`) are D14-s4-01's, for F1.1. tariff.py `_window_slot` is not applicable. coordinator.py `close` is guarded.
  - The optimizer.py candidates it lists are dispositioned here:
    - `_dhw_step_weekdays` gives a weekday label, not applicable.
    - `_utc_step_starts` walks UTC, guarded.
    - The three `time.monotonic()` sites are not datetimes, not applicable.
    - The two hour/minute-of-day sites are wall-clock labels, not applicable.
- **P3**, `$SWEEP_S5/tools/audit/round9/D14/sweep/P3/enumerate.py` (sha1 8b9fd95e): `p3_seam_groups=22` at both ends. Its keys reach neither the power band nor the zone weight, as the RCA measured.
  - The RCA's arm (a), from prototype `2ca057ae`'s `tests/features.py` (sha1 e953061d), run by `/mnt/project-files/audit-r9/rca/p3/run_p3_block.py`, reads groups 9 → 8. The group that left is `max_electrical_power - min_electrical_power`, D12-s2-03, closed here.
  - Arm (b) reads 4 FAIL → 4 PASS, D2-s2-81, closed here.
  - Remaining: `dhw_tank_thermal_mass` is D14-s3-01, F1.10. `slab_heat_transfer` is the RCA's open seam, F1.10. Six latent floor groups go to F1.10's arm (a). The 22 schema-floor pairs are guarded, per the sweep.
- **N-sign-floor**, `$SWEEP_S6/.../sign-floor-price-margin/enumerate.sh` (sha1 75a6694a). Its grep was run at each tree root, because the script `cd`s to its own export.
  - `pv.py import_margin`, closed here.
  - `pv.py blended_block_prices`, closed here, consuming the signed margin.
  - `optimizer.py _energy_cost_fn`'s call, closed here.
  - The 8 remaining `np.clip(..., 0.0, None)` rows (pv.py irradiance; optimizer.py surplus, external heat, price sigma, min-temp margins, the planned-vs-required gap, demand, headroom) are physical or deficit quantities, not signed price margins: not applicable, as the sweep said.
- **I5**, `$SWEEP_S2/tools/audit/round9/D14/sweep/I5/enumerator.py` (sha1 af15b9ca), run at the base and at 0861362e. No comment it reads changed after 0861362e.
  - Output is byte-identical at both ends (`diff` exit 0). D5-s2-51's shape reads `flagged=0` at both ends, blind to comments, hence the grep companion above.
  - Its other 14 shape rows are other PRs' instances, per the sweep's list: D4-s2-09, D5-s1-01/02/03/05, D5-s1-06/D6-s2-01, D5-s2-01, D5-s2-02/03, D6-s1-01/02/03, D6-s2-02/03/04/05 and D8-s3-02. Its four widening siblings are not applicable.

## Red checks

none: the branch has not run CI.

## Forward-carry

To F1.10 (the P3 barrier), handed to the round-9 orchestrator for the F1.10 roster entry and `handoff/round9/fix/F1.md`, since the plan is generated from `handoff/round9/fix/src/data.py`.

The modulation band's normalisation now lives in the power-fraction helper this PR adds to optimizer.py. The helper branches on a band narrower than 0.1 kW instead of flooring it, so arm (a) sees no group for the band (9 → 8 at this head).

Do not move it into a floored ThermalParameters property. A `max(band, 0.1)` floor is D12-s2-03 itself. Control: mutant M2 above fails the on/off checks.

## Friction

- fixer.md step 5: cost: the handoff branch's resume note is a tracked file no closure mentions, so `closure.py select` on the handoff head prints `MODE: FULL`. The scope was derived on a scratch commit without the handoff files.
- D2-s2-81: unclear: the finder's metric is non-monotone in the floor price. Raising the quadratic price as well moved several two-zone fixtures to basins with more breach, and everything_on breaches more under either form. That is the solver's multi-start basin sensitivity, class P4 (F2.4's D0-s2-02), not something this PR can price away.
