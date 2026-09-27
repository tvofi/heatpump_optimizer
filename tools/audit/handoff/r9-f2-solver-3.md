<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Round-9 fix F2.3, the solver lane's third PR. It repairs three places where the plant model disagreed with itself, and retires a second cold-water constant.

- **D2-s1-01**. The explicit-Euler guard judged each store on its own diagonal at a ratio of 1.5. Coupled stores share heat through their off-diagonals, so that rule let the coupled step's eigenvalue pass 1: a zero-input day on a light single-zone house with a stiff slab left the passive envelope by 2.8e35 K. `_stability_substeps` now bounds every row's whole conductance sum, `h * a_ii <= 1` (Gershgorin's row bound). That keeps the sub-step matrix non-negative and its spectral radius at or under 1, so a passive day can never overshoot its hottest store. The rows now include what the throttled mixing valve adds: `ua_rad` on the upper zone, `ua_floor` on the slab, and the regulating valve's buffer row. `EULER_STABILITY_MAX_RATIO` is gone, and `EULER_MONOTONE_MAX_RATIO` is 1.0.
- **D2-s1-02**. Below the mixed-use temperature the DHW draw is scaled by how hot the tank is, but the coil's wood debit was not, so the coil took more heat from the wood tank than it spared the DHW tank. One rule, `thermal_model.dhw_draw_scale`, is now read by the tank debit, the coil's wood debit (`ThermalModel.apply_dhw_coil`) and the planner's capacity clamp.
- **D2-s2-03**. The hot-water settle-up took its end state from a space-only replay that skipped the coil's wood debit, and the thermostat baseline had no coil at all. The plan's end is now its published trajectory's last state (`simulate_trajectory_with_dhw(..., end_state=)`). The baseline house owns the same coil and draws (`_compute_baseline_power(coil_draws=, coil_dhw_temp=)`). The coil's wood forecast, which prices the coil for the DHW planner, now runs the DHW plan in hand rather than zero DHW power, so the two agree.
- **D7-s1-71 / D5-s2-03**. `const.DHW_COLD_WATER_TEMP` duplicated `DEFAULT_DHW_INLET_TEMP` and was read at three sites, one of them a literal. It is retired. The bare `ThermalParameters()` default, `from_config` and the coil's inlet default all follow `DEFAULT_DHW_INLET_TEMP`, and the coil's cold end is `dhw_inlet_reference` at every call site.

Fixes #1671 (N-euler-coupled); Part of #1644 (P2); Part of #1645 (I5)
Part of #201.

The roster listed R9-F2.5 as an `after` edge. The orchestrator swapped that order: this PR merges on its own, and F2.5 branches from a main that already carries it. F2.5 edits `optimizer.py` in other methods. Against origin/main at 36d3c27a (v6.7.6), `git merge-tree` reports one conflict, in `tests/golden/claimed_drift.txt`: the `claims-for:` line and this branch's claim, which the `claimnotes` driver settles in a local merge. No production file overlaps.

## Head

Code head 00c41e21 on `handoff/r9-f2-solver-3-v2`, cut from 9c6b923f (origin/main after #1713, F2.2), which is also its merge base. The commits are:

- aa6779d2: the failing pins;
- 084e56e0: the fix;
- e564c64f: the coil's wood forecast runs the DHW plan in hand;
- 27c18bbd: a valved case per emitter row;
- dcf1eade: `max_method_loc` re-recorded 387 -> 386;
- 553dcb28: the carry to R9-F4.2;
- bdc688bf: the wood_coil claim;
- 157e6a23: the sysid frontier header re-recorded;
- 546aa968: checks that kill the mutation table's six survivors;
- ef071c1a: the mutation ledger's `killed_by` rows;
- 00c41e21: the wood_coil claim restated with its measured direction, down (the fix review found bdc688bf had it backwards).

The -v2 branch is the reviewed ef071c1a chain plus 00c41e21, which changes only `tests/golden/claimed_drift.txt`.

Production files are identical from e564c64f onward. The gate ran at dcf1eade. The scripts the later commits reach were re-run: harness_headers, env_drift, golden and entities at 157e6a23, and features and structure at 546aa968. The finder harnesses ran at base 9c6b923f and at 157e6a23. The mutation table ran at 546aa968; ef071c1a adds only its ledger rows. At 00c41e21, `env_drift.py --all 9c6b923f` and `entities.py` were re-run. The handoff commit stacked on the code head carries only this body, its evidence and the resume note.

## Mutation proof

Each mutant is one textual edit of a production line in a `git archive` copy of the tree. The runner, mutate.py in this handoff's evidence directory, runs the F2.3 block of `tests/features.py` in that copy through f23_run.py (the block verbatim, with the file's imports). Logs are in `ev/mut/` (at 27c18bbd) and `ev/mut3/` (at 546aa968). M4 alone was run through the whole of `tests/features.py`.

- M1, the ratio put back to 1.5 under the per-store rule: 7 of the block's 18 checks fail. Among them are `R9-F2.3 D2-s1-01 (single-zone C=0.5 k=5): a zero-input day stays inside the passive envelope [T_out, hottest store]` (left by 2.843e+35 K) and `... the sub-step matrix is monotone -- no negative entry -- with spectral radius at or under 1` (spectral radius 1.5252).
- M2, `ua_rad` dropped from the upper row: FAIL `R9-F2.3 D2-s1-01 (two-zone valved, radiator row): the sub-step matrix is monotone ...` (min entry -0.2667).
- M3, `ua_floor` dropped from the slab row: FAIL `R9-F2.3 D2-s1-01 (two-zone valved, floor row): the sub-step matrix is monotone ...` (min entry -1.0000, spectral radius 1.0004).
- M4, the buffer row dropped: the block passes, but two existing pins fail in the full file, beside the #363 archive artifact (see Null control): `more power never leaves the 35 L valved buffer cooler` (the buffer cooled 13.05 K) and `and its schedule is one the compared axes can see the divisor in` (`ev/mut/m4_features.txt`).
- M5, the coil's wood debit unscaled: FAIL `R9-F2.3 D2-s1-02: the coil takes from the wood tank exactly the heat it spares the DHW tank, below the mixed-use temperature as above it` (residual 0.405991 kWh).
- M6, the end taken from the space-only replay again: FAIL `R9-F2.3 D2-s2-03: the hot-water settle-up's plan end is the published trajectory's last state, store for store` (wood gap 0.3696 K).
- M7, the baseline without the coil: FAIL `R9-F2.3 D2-s2-03: the thermostat reference's wood tank ends lower than its no-coil twin -- it owns the coil the plan owns`.
- M8 and M9, the inlet default back to a literal 10.0 in `ThermalParameters` and in `dhw_coil_draw_reduction`: each FAILs `R9-F2.3 D7-s1-71: every site resolving the cold-water inlet default follows DEFAULT_DHW_INLET_TEMP when it moves`, naming its own site.
- M10 to M15, the six sites the mutation table's first run at 157e6a23 left alive (logs `ev/mut3/`, runner mutate.py with those names). Each is killed by a check 546aa968 adds:
  - M10, `_compute_baseline_power`'s coil-off guard deleted: FAIL `R9-F2.3 D2-s2-03: with the coil switched off, the reference's draws leave its wood tank as its no-coil twin's` (19.388882 vs 20.792082).
  - M11, `dhw_draw_scale`'s span unclamped: FAIL `R9-F2.3 D2-s1-02: an inlet at or above the mixed-use temperature scales the draw to 1 above it and 0 at it, never past [0, 1]` (ZeroDivisionError).
  - M12, the COP clamp dropped from the count: FAIL `R9-F2.3 D2-s1-01 (COP 0.5, delta-T 0.5 K): the count is the step's own stiffness -- monotone at n_sub, and one sub-step fewer is not` (n_sub 2 against the step's 3).
  - M13, the design delta-T clamp dropped: FAILs the same check on `(design delta-T 0.5 K)` (n_sub 15 against 8) and `(COP 0.5, delta-T 0.5 K)`.
  - M14, the empty-buffer fallback skipped: FAIL `R9-F2.3 D2-s1-01 (empty buffer): the count is the step's own stiffness -- monotone at n_sub` (ZeroDivisionError).
  - M15, `apply_dhw_coil`'s no-wood-tank guard skipped: FAIL `R9-F2.3 D2-s1-02: with no wood tank the coil passes the draw through untouched` (TypeError).
- The mutation ledger: `tests/mutation_table.py --scope changed --base 9c6b923f --max 10 --jobs 4 --pin-killed` at 546aa968 reads `PIN KILLED: 16 pinned, 0 left unpinned` (`ev/mt3.log`). At 157e6a23 the same run read 10 pinned and 6 alive (`ev/mt2.log`); the six are M10 to M15 above. At ef071c1a the ledger reads 3631 unpinned sites of 3995, against 3642 at the ratchet base 9c6b923f.

The block's first 18 checks at the merge base fail 14 (`ev/f23_tests_base.txt`); the six 546aa968 adds guard code this branch adds. The four that pass at base are:
- the two valved envelope checks (their matrix checks fail at base);
- the null arm;
- the coil control.

## Null control

- M0, the mutation runner with no edit: 0 of the block's checks fail, at 27c18bbd and at 546aa968. In the whole-file run (M4), `and the path that proceeds still stamps a resolvable recorded_at (#363)` also fails, because a `git archive` copy has no `.git`; the same check passes in the clone.
- The block's null arm: the shipped defaults keep `n_sub == 1` at base and head. That covers single-zone, two-zone, and valved with a 750 L tank, so the new rule does not sub-step a house the old rule left alone.
- The block's coil control: the coil draws on the wood tank in every grid cell at both ends, so the zero residual is not an empty zero.
- The finder harnesses' own null arms:
  - `m1_coil.py`: residual at or above 40 °C is 3.275e-15 kWh at both ends.
  - `m1_stability.py`: the default and preset configs read 0 violations at both ends (3360 preset configs, worst rho 0.9995).
  - `m1_stability.py --perturb=ratio1`: 0 at both ends.
  - `l3_cold_water_default.py --no-move`: 0 of 5 sites disagree at both ends.
- Goldens: at 00c41e21, `env_drift.py --all 9c6b923f` reads `CLAIMED wood_coil` and then `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. Every other scenario is byte-identical or a may-drift that did not move.

## Figures

All runs:
- CPython 3.14.0rc2, numpy and scipy from `requirements-ci.txt`;
- `OPENBLAS_CORETYPE=Haswell` with one thread (CI's kernel);
- a 4-core x86_64 Linux cloud container;
- `PYTHONPATH=tests/hastub`.

"base" is 9c6b923f and "head" is 157e6a23. The finder harnesses were run from an export of evidence commit 79aa98ec as `$EXPORT/<path>`. Logs are `ev/{base,head}_<harness>.txt`.

- D2-s1-01, `$EXPORT/tools/audit/round9/D2/s1/m1_stability.py` (sha1 8b1af906):
  - `grid_envelope_violations`: 69 -> 0 of 3936.
  - `grid_rho_gt_1`: 52 -> 0.
  - `grid_diverged_100K`: 50 -> 0.
  - `grid_worst_rho`: 1.3958 -> 1.0000.
  - `examples_envelope_violations`: 2 -> 0, with `examples_worst_rho` 1.5252 -> 0.9876.
- D2-s1-02, `$EXPORT/tools/audit/round9/D2/s1/m1_coil.py` (sha1 ea23c97a):
  - `coil_residual_cells_nonzero_below_40C`: 28 -> 0 of 28.
  - `coil_residual_max_one_step`: 0.405991 -> 0.000000 kWh.
  - `coil_residual_dhw35_wood70`: 0.054010 -> 0.000000 kWh.
- D2-s2-03, `$EXPORT/tools/audit/round9/D2/s2/objective_identities.py` (sha1 da5b9d32):
  - `savings_overstatement_max`: 0.4803 -> 0.0000.
  - `end_mismatch`: 11 in 2 scenarios -> 5 in 1 (`valve_storage_smart_write`, max 0.134859 K).
  - The remaining mismatch is the harness reading only the last `_deferred_energy_cost` call. That scenario makes two, both on the space path (`include_dhw=False`). The first call's end matches the published trajectory's last state exactly (gap 0.000000 K). The second, a candidate the plan does not publish, is 0.134859 K off. Instrument: smart_write_calls.py in the evidence directory, output `ev/smart_write_calls.txt`.
- D7-s1-71, `$EXPORT/tools/audit/round9/D7/leads/l3_cold_water_default.py` (sha1 8b318411): `sites_not_following`: 3 -> 0 of 5.
- D5-s2-03, `$EXPORT/tools/audit/round9/D5/s2/comment_numbers.py` (sha1 e058d3ba):
  - `draw_cold_end_off_constant` at base: 46 of 47.
  - At head the harness exits on `AttributeError`, because it reads the retired constant by name. `git grep DHW_COLD_WATER_TEMP custom_components` prints nothing at head.
  - The companion `comment_numbers_shim.py` (sha1 f36fad79, in the evidence directory; `ev/{base,head}_comment_numbers_shim.txt`) puts the name back in memory and runs the harness unchanged. It shows D5-s2-02's rows unchanged at base and head: `derate_floor`, `valve_write_cadence` and `stale_floor_interval` each read 1 row. Its `draw_cold_end` row reads the shim, not a claim.
- Gate at dcf1eade, scoped by `closure.py select` against 9c6b923f: `MODE: SCOPED -- 24 script(s) run, 2 scoped out`, with `GOLDEN_MODE=drift` against 9c6b923f. Log `ev/gate3.log`.
  - rc 0: backtest (25), card.mjs, card_drift.mjs (identical in all 40 states), config_flow_steps (454), deployment_shape, doc_claims (39), edge, entities (1973), features (3462), finite_boundary (51), frontend, golden, guard_pins (7), manual_plan (85), open_meteo, optimality (84), plan_view, solar_alignment, stress (87), structure, typing_ruler (`--mypy` under the pinned tools: 9 and 12 source checks), validate, wood_advisor (7).
  - Red at dcf1eade, both answered under Red checks: `harness_headers.py` and `env_drift.py --all`.
- At 157e6a23, re-run after the claim and header commits: `harness_headers.py` 91 of 91, `env_drift.py --all 9c6b923f` and `golden.py` clean, and `entities.py` 1973.
- At 546aa968: `tests/features.py` `ALL 3468 FEATURE CHECKS PASSED` (`ev/feat_546aa968.txt`), the F2.3 block 24 of 24, and `STRUCTURE RATCHET PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `max_method_loc` is re-recorded 387 -> 386 (dcf1eade), because `_optimize_with_dhw` shrank by one line. No budget was raised.

### Class sweep (fixer.md step 8)

These ran at e564c64f, whose production files equal the code head's. Logs `ev/enum_*`.

- **N-euler-coupled (S7)**, the grep of SWEEP.md at 1152a74346 for the Euler constants:
  - base: `EULER_STABILITY_MAX_RATIO` at thermal_model.py 144, 2471 and 2533;
  - head: only `EULER_MONOTONE_MAX_RATIO`, at 149, 2485 and 2547.
  - The one guard that judged stores per diagonal is closed here. No second site in the package computes a sub-step count. R9-F4.2's rollout is the carried one (see Forward-carry).
- **P2**, `$SWEEP_P2/tools/audit/round9/D14/sweep/P2/enumerator.py --seams`, where `$SWEEP_P2` is an export of c44e7bcd60 (sha1 d266a405):
  - Base and head are identical except for line shifts: the `from_config` wood seams moved from 1017/1009/1010 to 1016/1008/1009.
  - None of the listed seams are this PR's. The seam this PR closes, the coil's scale and debit, is not in the enumerator's list; the block's residual grid measures it.
- **I5**, `$SWEEP_I5/tools/audit/round9/D14/sweep/I5/enumerator.py`, where `$SWEEP_I5` is an export of 38f1230e92 (sha1 af15b9ca):
  - Base and head are identical except for the row `D5-s2-02/D5-s2-03 flagged 4.0 -> 0`.
  - That 0 is the head crash of `comment_numbers.py` described above, not a closure. Through the shim, D5-s2-02's three rows are unchanged, and they are not this PR's.
- **D7 sites**, a grep for `DEFAULT_DHW_INLET_TEMP`, `DHW_COLD_WATER_TEMP` and `dhw_inlet_temp: float`:
  - base: `DHW_COLD_WATER_TEMP` at const.py:351 and thermal_model.py:100, 1320 and 1335, plus the literal at thermal_model.py:469;
  - head: every site reads `DEFAULT_DHW_INLET_TEMP`.

## Red checks

- `tests/features.py`, two existing coil pins, red locally at 084e56e0:
  - `the wood temps the DHW planner prices the coil at are the published plan's`, with a gap of 0.0824 K against 0.05;
  - `the draws it credits ...`.
  - Cause: the coil's wood debit now scales with the DHW tank's temperature, but `_dhw_coil_wood_forecast` still simulated zero DHW power. Fixed in e564c64f: the forecast runs the DHW plan in hand, and the pins' spy passes the new argument.
  - Cheaper detector: none. `features.py` is the cheapest check that runs the planner against its own forecast, and it caught this before any push.
- `harness_headers.py`, red at dcf1eade:
  - `tools/audit/round4/D7/sysid_estimator_frontier.py` printed `interval_refused_typical_s005=15` against a header of 14, and `interval_refused_heavy_s005=7` against 4.
  - The move is expected. The frontier's x100 slab plants are stiff, and `simulate_step` now sub-steps them under the coupled row rule. It was measured at base and head in one environment (`ev/sysid_{base,head}.log`). Refusals only grew, and every fitted draw stays within the 10 % bar. The one typical draw the base fitted at sigma 0.05 was +11.9 %, past the bar, and it is now refused.
  - 157e6a23 re-records the header with that reason.
  - Cheaper detector: none needed. `run.sh` runs `harness_headers.py` unconditionally (`run_always`), and it caught this in the local gate before any push. The scope report still lists it as SKIP; see Friction.
- `env_drift.py --all 9c6b923f`, red at dcf1eade: `wood_coil.baseline_cost: 157.190147 vs 156.407745`, printed base first.
  - Expected: the thermostat reference now owns the plan's coil (D2-s2-03), and the coil drains its wood tank (20.79 °C at the end without the coil, 19.39 with it; the block's D2-s2-03 checks).
  - Direction, from `golden.capture('wood_coil')` at base and head (`ev/cap_wc.txt`, instrument cap_wc.py): `baseline_cost` falls 157.190147 -> 156.407745, `deferred_energy_cost` moves 26.368664 -> 27.234755 and `predicted_cost` 40.356399 -> 38.938116, so `predicted_savings` falls 90.465084 -> 90.234874 and `savings_percentage` rises 57.55137 -> 57.692075.
  - bdc688bf first claimed it as a rise, having read the diff line the wrong way round; the fix review caught it, and 00c41e21 restates the claim as down.
  - `baseline_cost` is a judged key that a may-drift entry cannot excuse, so the branch claims wood_coil with its direction. It suspends the may-drift entry, with the restore obligation beside it, as R8-P3 did (50a0d071, restored by dd53410b).
  - Cheaper detector: none. The golden drift gate is the cheapest check that sees a baseline cost.
- `prepr.sh` `closures`, refused at ef071c1a: `failed while being recorded: tests/card_drift.mjs (exit 1)`.
  - The recorder runs `card_drift.mjs` against `GOLDEN_REF=origin/main`, now 36d3c27a (v6.7.6). Main has since changed the card, so `layout_editing_dragged` renders differently and the card header reads v6.7.6 against this branch's v6.7.4 (`ev/card_drift_vs_main.txt`).
  - Against the merge base the same script reads `card_drift: identical in all 40 states`. The drift is main's, not this diff's; it clears when main is merged in before the merge. This branch touches no card file.
  - Cheaper detector: none; this is `prepr.sh` itself, and it caught it before any push.

## Forward-carry

`.claude/workflows/carry-1655.json`, to R9-F4.2, in the code head (553dcb28, linted clean by `brief_lint.mjs`).
- The rollout's sub-step count takes `ThermalModel._stability_substeps`, or reproduces its row rule.
- The refuted per-store 1.5 rule is not re-derived.

At the stamp that empties the claim list, wood_coil's may-drift entry in `tests/golden/claimed_drift.txt` is restored verbatim. The obligation is written beside the suspended entry.

## Friction

- gate-scoping.md: unclear: at dcf1eade the scoped gate's header printed `SKIP tests/harness_headers.py (no changed file is in its measured closure)` and its footer listed it under `NOT RUN`, yet `run.sh` ran it (`run_always`) and it went red. The closure also omits `thermal_model.py`, which `tools/audit/round4/D7/sysid_estimator_frontier.py` rolls through `ThermalModel.simulate_step`, the same shape as F2.2's h9 row.
- claim-files.md: cost: a may-drift fixture whose judged key moves cannot be claimed without suspending its may-drift entry, and restoring the entry is a manual step at the stamp. R8-P3 needed a follow-up commit (dd53410b) for exactly that.
- fixer.md#8: stale: `comment_numbers.py` (D5-s2) reads `const.DHW_COLD_WATER_TEMP` by name, so a fix that retires the constant makes the harness crash instead of reading 0. The I5 enumerator then reads the crash as `flagged 0`. A companion shim was needed to measure the neighbouring D5-s2-02 rows.
- fixer.md#2: cost: a `git archive` copy fails the #363 `recorded_at` check on every mutant. The M0 null run is what shows it is the runner's.
- prepr.sh#closures: unclear: the recorder grades against `origin/main` rather than the merge base, so a branch whose base main has moved the card reads as `failed while being recorded`, with a remedy ("fix the script first") that does not apply.
- env_drift.py: unclear: a judged-leaf diff prints `<fixture>.<key>: <base> vs <branch>` with no side named, and this seat read it backwards (bdc688bf claimed a rise that is a fall).
