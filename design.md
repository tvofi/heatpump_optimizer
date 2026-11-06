# R10-CLONE-2238: design note, P2 clone-class instances (F5_clone)

Base and code SHA: `b88684a218923f85de66f1e8fb1833e31a76a154` (origin/main). This group has no predecessor handoff and no `after` edges.
Revalidation of round 2 (`design/R10-CLONE-2238` at `51884d31f`, base `c3a279e3`, not yet reviewed). The base has moved 770 commits since then, so every line is re-cited here. The P1–P9 shape, the round-1 revise point (P3's fourth site) and both round-1 carries are unchanged. Two things moved: the line numbers, and probe 6 (see section 5).
Toolchain: `tools/audit/seat/cloud-setup.sh --check` returned OK. CI stays the authority for goldens.

## 1. Re-measurement at the base

I exported the base with `git archive origin/main`, then ran `python3 -I dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py --json`. F5_clone lists 24 classes. Null control: `--fixture` reads 0 in all seven families.

| brief pair | at base (enumerator entry) |
|---|---|
| coordinator `_accumulate_energy` + `_maybe_run_fuse_advisor` (and `_settle_interval_diag`) | listed, entry 4 |
| coordinator `_async_learn_house_heat_loss` + `_async_learn_lower_floor_loss` | listed, entry 5 |
| coordinator `_file_lead_predictions` + `_predicted_next_room_temp` | listed, entry 6 |
| coordinator `_fold_internal_gains` + `_fold_solar_aperture` | **gone, dropped** |
| optimizer `_buffer_charge_ceiling` + `hold_demand_kw` | **gone, dropped** |
| optimizer `_grid_report` + tariff `_peak_excess` | listed, entry 13 |
| optimizer `_peak_day_kwargs` + `_peak_window_factors` | listed, entry 14 |
| sensor, the two `extra_state_attributes` (1913, 2409) | listed, entry 18 |
| tariff `_close_window` + `from_dict` | listed, entry 20 |
| tariff `_window_means_batch` + `metering_windows` | listed, entry 21 |
| tariff `plan_window_days` + `window_factors` | listed, entry 22 |

That leaves nine pairs. The other 15 classes are outside this brief, and none of them is touched.

## 2. Seams: one fact, one owner per pair

Each pair is its own fact with one owner module, so no fact needs two owners. The facts are independent, so the group lands as one PR of nine commits.

| # | the one fact | owner (new) | callers |
|---|---|---|---|
| P1 | an interval's planned (space, dhw) kW, with an absent channel read as 0 | `coordinator.py` module fn `_planned_split(pending) -> tuple[float, float]` | `_accumulate_energy` (`coordinator.py:10153-10154`), `_settle_interval_diag` (`coordinator.py:1219`) |
| P2 | a fabric-loss residual too large to be a heat-loss error is refused, and the refusal is logged | `coordinator.py` module fn `_loss_residual_rejected(residual, what) -> bool` | both loss learners (`coordinator.py:5633`, `coordinator.py:5756`) |
| P3 | the trajectory the indoor sensor reads: the upper floor in two-zone mode when it is present, else the room | `optimizer.py` `OptimizationResult.sensor_trajectory(two_zone) -> list[float]` | `_file_lead_predictions` (`coordinator.py:10067`), `_predicted_next_room_temp` (`coordinator.py:10116`), `_publish_breach_reports` (`optimizer.py:4103`), `_safety_release_steps` (`optimizer.py:4477-4482`, the `space_pins` loop) |
| P4 | window means at their billed-equivalent factor, with any window past the factors billed at 1 | `tariff.py` `billed_windows(windows, window_factors)`, padding on `shape[-1]` | `_peak_excess` (`tariff.py:873-878`), `peak_cost_batch` (`tariff.py:1166-1170`), optimizer `_grid_report` (`optimizer.py:4932-4934`) |
| P5 | how many metering windows a plan of `n_steps` spans | `optimizer.py` `HeatPumpOptimizer._n_peak_windows(n_steps, dt, offset_steps) -> int` | `_peak_window_factors` (`optimizer.py:3377`), `_peak_day_kwargs` (`optimizer.py:3396`) |
| P6 | an evidence sensor's attributes: its payload block, `waiting_for`, and one insight report | `sensor.py` `_WaitsForEvidenceMixin._evidence_attributes(block, report_key)` (mixin at `sensor.py:376`) | `PredictionAccuracySensor` (`sensor.py:1872`), `ContractComparisonSensor` (`sensor.py:2369`) |
| P7 | the tracker stores a ranked (kW, day) record as the parallel `peaks`/`peak_days` lists | `tariff.py` `PeakTracker._keep_ranked(ranked)` | `_close_window` (`tariff.py:332`), `from_dict` (`tariff.py:413`) |
| P8 | the metering-window partition: steps per window, and steps in the leading partial window | `tariff.py` `_window_partition(n, window_minutes, dt_hours, offset_steps) -> (per_window, head_steps)` | `metering_windows` (`tariff.py:557`), `_window_means_batch` (`tariff.py:1077`) |
| P9 | each window's real local start, walked in UTC from the slot of `start_time` (#243, #777) | `tariff.py` `_window_starts(start_time, window, n_windows) -> list[datetime]` | `window_factors` (`tariff.py:609`, maps `sample_factor`), `plan_window_days` (`tariff.py:670`, maps `toordinal`) |

Interfaces: every owner is new and private except `billed_windows`. `optimizer.py` imports `billed_windows` beside `metering_windows`. No payload key, entity attribute or public signature changes. `_peak_window_factors` keeps `(n_steps, dt, start_time, offset_steps)`, because two finder harnesses call it: `dev/audit/rounds/round3/D2/dst_window_factors.py` and `dev/audit/rounds/round4/D2/d2_own_D2-02.py`.

Only P4 crosses modules:
`optimizer._grid_report → tariff.metering_windows → tariff.billed_windows ← tariff._peak_excess / peak_cost_batch`.
Today the optimizer and both tariff charges each pad the factors themselves; at base the optimizer slices with `f = factors[: windows.size]` before it pads. After the change all three call the tariff's owner. The owner both slices and pads, so the published `peak_kw` and the priced excess cannot disagree about a window past the factors.

Invariants: every output stays bit-for-bit what it was. P2 keeps the two debug messages, which differ only in the noun. In the house learner, P2 keeps the finite check before the vent CUSUM. P1 keeps the module-level placement that `_settle_interval_diag` needs.

## 3. Alternatives that lost

- **P8:** have `metering_windows` call `_window_means_batch(house[None, :])[0]`. This gives one owner for the whole partition, but it routes every scalar call through the batch path. That is an extra matrix allocation per call on the Pi target (D9), and it moves the scalar's `if not pieces` fallback. The duplicated fact is the partition, so the partition is what gets an owner.
- **P5:** compute `n_windows` once in `_peak_billing` and pass it down. This calls the rule once instead of twice, but it changes the signature of `_peak_window_factors` and breaks the two finder harnesses above. Any harness that drives `_peak_window_factors` directly would still need its own copy of the rule.
- **P3:** a module function in `coordinator.py`. This loses because the optimizer's own copies (`optimizer.py:4103`, `:4479`) could not call it without an import cycle. `OptimizationResult` owns both trajectories, so the rule belongs on it.
- **P6:** a method on the sensor base class. This loses because the fact includes `waiting_for`, which only `_WaitsForEvidenceMixin` defines. The other `insight` readers (`sensor.py:2649`, `:2666`, `:2707`) carry no `waiting_for` and are not in F5, so they are out of scope.
- **P1, `_maybe_run_fuse_advisor`:** the two reads in its clone (`power_cap_breach_c`, `projected_peak_kw`) are different facts from the planned split. The class matched only on the shape `float(d.get(k) or 0.0)`. The real duplicate is `_settle_interval_diag`. A generic `_num_or_zero` helper would name a coercion, not a fact. At `c3a279e3` the fuse advisor left F5 once P1 landed, and nothing new entered.

## 4. Sibling sites (commands, re-run at base)

- `rg -n 'upper_temp_trajectory' custom_components/` lists 15 lines at 11 sites:
  - `optimizer.py:4104`, `optimizer.py:4479`, `coordinator.py:10068`, `coordinator.py:10117`: the P3 rule. All four are covered by P3.
  - `optimizer.py:1902` is the field and `optimizer.py:3096` is its producer. Neither reads the rule.
  - `coordinator.py:2362` (`_sim_coldest`) takes the minimum over every zone, which is a different fact.
  - `coordinator.py:2922` is the recorded `ut` column: upper when present, with no two-zone gate, so a different fact.
  - `coordinator.py:4665-4667` requires both zones, so a different fact.
- `rg -n 'np.ones\(windows' custom_components/` finds `tariff.py:876`, `tariff.py:1169` and `optimizer.py:4934`. All three are covered by P4.
- `rg -n 'int\(round\(window_minutes / max\(dt_hours' custom_components/` finds `tariff.py:557` and `:1077`. Both are covered by P8.
- `rg -n '_window_slot\(' custom_components/heatpump_optimizer/tariff.py` finds 261, 306, 609 and 670. Sites 609 and 670 are covered by P9. Sites 261 and 306 key a live window with no UTC walk, a different fact, so they are out of scope.
- `rg -n 'HOUSE_LOSS_MAX_RESIDUAL' custom_components/` finds 5633 and 5756, covered by P2. The 1331 argument is a third fact and out of scope.
- `rg -n 'for kw, _ in ranked\]' custom_components/` finds 332 and 413. Both are covered by P7.
- `rg -n 'pending.get\("(space|dhw)_power"\)' custom_components/` finds 1219 and 10153-10154. All are covered by P1.

## 5. Evidence plan, by file

**Spike figures, measured at `c3a279e3` and not re-measured here.** I applied all nine shapes to a scratch copy; the spike is not committed. Results:
- F5 went from 24 to 15. All nine pairs left the list and none entered.
- archscore `--delta` read `IMPROVES`, dS +4.79.
- `tests/structure.py` rows: `class_excess_loc` −23, `duplication_copies` 14→10, `max_class_loc` −21.
- 618 tariff outputs stayed bit-identical.

**At this base**, `class_excess_loc` (17585), `duplication_copies` (14) and `max_class_loc` (7955) each sit at **zero headroom**. The fixer re-measures structure after every commit. A commit that grows any of the three rows is reshaped until it does not grow it (P3's method and P7's helper live inside classes). If a reshape is impossible, that commit stops for the owner under CLAUDE.md rule 2; it is never a quiet raise. The fixer re-records with `--record` and names the rows that moved in the commit message. Expected golden movement: none, so the claim files stay untouched.

**Failing test first, through the production path, one per pair, added to an existing script.** Each test patches the new owner to a sentinel answer and drives **both** production callers, asserting that both return the sentinel. At base each test fails, because the owner is absent. After the fix it passes. A mutant that restores the inline copy at any caller line in section 2 is killed. For P3 that means four mutation targets: `coordinator.py:10067`, `:10116`, `optimizer.py:4103`, `:4477`.

| pair | script | drive |
|---|---|---|
| P1 | `tests/features.py`, `tests/boost_drift_replay.py` | one pending dict → the ledger split and the diag attribution |
| P2 | `tests/dst_checks.py` | residual 1.2 K > 1.0 with the gate patched to accept → both learners fold |
| P3 | `tests/features.py`, `tests/boost_drift_replay.py`, `tests/stress.py` | two-zone result → lead buckets, next-room temp, the breach report, and `_safety_release_steps(result, temp_min_bounds, space_pins, None)` |
| P4 | `tests/features.py` | masked tariff with factors shorter than windows → `peak_kw`, `peak_cost`, `peak_cost_batch` |
| P5 | `tests/features.py` | patched count → factor length and `window_days` length agree |
| P6 | `tests/entities.py` | both sensors publish the owner's dict |
| P7 | `tests/features.py` | `from_dict` round-trip plus close |
| P8 | `tests/features.py` | patched partition → scalar and batch window counts |
| P9 | `tests/dst_checks.py` | autumn fold → factors and days |

**Controls:** `enumerate_p2.py --fixture` reads 0 in every family. After each commit, F5 drops exactly that pair and gains no entry. archscore is read before and after the change and must not read worse.

**Probes (`dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py`): this moved since round 2.** At base, all six F1 seams the probes evaluate now call the owner, `planned_draw_runs` (D8-s1-01). The script stops with `LookupError` at probe 4, because its needle `target_kw <=` is gone. Probes 5 and 6 would stop the same way. Re-extract, measured on a scratch copy of the base:
- In `_expr_in`, accept `ast.Call` alongside `Compare` and `BoolOp`.
- Use needles that survive either spelling: probe 4 `np.isfinite(target_kw)`, probe 5 unchanged, probe 6 `reported >= hz_min`.
- Bind `planned_draw_runs` (from `thermal_model`) in the eval globals of probes 4–6, and `defrost_interval` (from `freq_control`, its owner) in probe 6.
- Give `_Self` the attribute `_pump_signals = SimpleNamespace(defrosting=False)`.

With those changes the script reads **6/6 PASS** (`probes_failed=0`). Probe 6 now evaluates, and that is the reading to record. The null arm still moves: re-inserting the `> 0.05` / `<= 0.05` copies at probes 3–6 reads **4 FAIL**. `--perturb` is stale, because all of its `FIXES` have landed. The fixer turns `FIXES` around so that each entry re-inserts the copy, and the null arm then expects a failure for each probe.

## 6. Hot files, serial position, carries

- Hot files: `coordinator.py`, `optimizer.py`, `tariff.py`, `sensor.py`, and `tests/structure_budgets.json` (the re-record).
- No `after` edges. Rebase on main before re-recording, because any merge that moves the three zero-headroom rows changes the recorded values.

### Notes for the fixer

- P2: keep the finite check where it is in the house learner, between the replay and the CUSUM. Only the magnitude gate moves into the owner.
- P4: spell the owner on `windows.shape[-1]`, and slice before padding (`optimizer.py:4932`), so that the 1-D and 2-D paths share it.
- Carry: R10-CLONE-2238 (item golden-check). `tests/golden.py` in drift mode, through `tests/env_drift.py`, covers P1–P3 and P7 (the `coord_*` fixtures) and P3's optimizer sites plus P5 (`capacity_tariff`, `capacity_tariff_15min`, `peak_masked`, `shoulder_two_zone`, `tariff_plus_two_zone`). Say in the body that the scoped gate ran them with zero drift.
- Carry: R10-CLONE-2238 (item bugclasses-json). In `dev/audit/config/bugclasses.json`, the P2 entry lists the nine pairs as `sw:` instances (lines 280–290 at base). The file has no per-instance closed marker: the entry carries one `status` and records resolutions as prose. Leave the file untouched and say why in the body, unless the body's prose convention is extended in the same commit as the fix.
- Carry: R10-CLONE-2238 (item probe-reextract). Apply the section 5 probe re-extraction, and record both 6/6 PASS and the four-FAIL null.
- Carry: dismissed: round-2 probe-6 F1 reading already fixed on main by D8-s1-01 (item probe6-observe-frequency)
