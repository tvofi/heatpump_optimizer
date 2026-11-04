# R10-CLONE-2238: design note, P2 clone-class instances (F5_clone)

Base and code SHA: `c3a279e3252a8b57bb00b5a677318cd4fe20387f` (origin/main; this group has no predecessor handoff).
Round 2: answers revise point 1 of design-verdict `c49a584de` (a fourth P3 site) and folds its two fixer notes in as carries. The base is unchanged since round 1, so every other citation and figure stands as measured there.
Toolchain: `tools/audit/seat/cloud-setup.sh --check` returned OK. CI stays the authority for goldens, and none should move (see Evidence).

## 1. Re-measurement at the base

`git archive` of the base, then `python3 -I dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py --json`.
F5_clone lists 24 classes. Null control: `--fixture` reads 0 in every family.

| brief pair | at base |
|---|---|
| coordinator `_accumulate_energy` + `_maybe_run_fuse_advisor` (and `_settle_interval_diag`) | listed |
| coordinator `_async_learn_house_heat_loss` + `_async_learn_lower_floor_loss` | listed |
| coordinator `_file_lead_predictions` + `_predicted_next_room_temp` | listed |
| coordinator `_fold_internal_gains` + `_fold_solar_aperture` | **gone, dropped** |
| optimizer `_buffer_charge_ceiling` + `hold_demand_kw` | **gone, dropped** |
| optimizer `_grid_report` + tariff `_peak_excess` | listed |
| optimizer `_peak_day_kwargs` + `_peak_window_factors` | listed |
| sensor, the two `extra_state_attributes` (1913, 2394) | listed |
| tariff `_close_window` + `from_dict` | listed |
| tariff `_window_means_batch` + `metering_windows` | listed |
| tariff `plan_window_days` + `window_factors` | listed |

That leaves nine pairs. The other 15 classes are not in this brief, and none of them is touched.

## 2. Seams: one fact, one owner per pair

Each pair is its own fact with one owner module, so no fact needs two owners. Because the facts are independent, the group can land as one PR made of nine commits.

| # | the one fact | owner (new) | callers |
|---|---|---|---|
| P1 | an interval's planned (space, dhw) kW, with an absent channel read as 0 | `coordinator.py` module fn `_planned_split(pending) -> tuple[float, float]` | `_accumulate_energy`, `_settle_interval_diag` |
| P2 | a fabric-loss residual too large to be a heat-loss error is refused, and the refusal is logged | `coordinator.py` module fn `_loss_residual_rejected(residual, what) -> bool` | both loss learners |
| P3 | the trajectory the indoor sensor reads: upper floor in two-zone mode when present, else room | `optimizer.py` `OptimizationResult.sensor_trajectory(two_zone) -> list[float]` | `_file_lead_predictions`, `_predicted_next_room_temp`, and siblings `optimizer.py:3886` (`_publish_breach_reports`) and `optimizer.py:4261` (`_safety_release_steps`, the `space_pins` release loop) |
| P4 | window means at their billed-equivalent factor, with a window past the factors billed at 1 | `tariff.py` `billed_windows(windows, window_factors)`, which pads on `shape[-1]` | `_peak_excess`, `peak_cost_batch` (sibling, `tariff.py:1166`), optimizer `_grid_report` |
| P5 | how many metering windows a plan of `n_steps` spans | `optimizer.py` `HeatPumpOptimizer._n_peak_windows(n_steps, dt, offset_steps) -> int` | `_peak_window_factors`, `_peak_day_kwargs` |
| P6 | an evidence sensor's attributes: its payload block, `waiting_for`, and one insight report | `sensor.py` `_WaitsForEvidenceMixin._evidence_attributes(block, report_key)` | `PredictionAccuracySensor`, `ContractComparisonSensor` |
| P7 | the tracker stores a ranked (kW, day) record as the parallel `peaks`/`peak_days` lists | `tariff.py` `PeakTracker._keep_ranked(ranked)` | `_close_window`, `from_dict` |
| P8 | the metering-window partition: steps per window and steps in the leading partial window | `tariff.py` `_window_partition(n, window_minutes, dt_hours, offset_steps) -> (per_window, head_steps)` | `metering_windows`, `_window_means_batch` |
| P9 | each window's real local start, walked in UTC from the slot of `start_time` (#243, #777) | `tariff.py` `_window_starts(start_time, window, n_windows) -> list[datetime]` | `window_factors` (maps `sample_factor`), `plan_window_days` (maps `toordinal`) |

Interfaces: every owner is new and private except `billed_windows`. `optimizer.py` imports `billed_windows` beside `metering_windows`. No payload key, entity attribute or public signature changes. `_peak_window_factors` keeps `(n_steps, dt, start_time, offset_steps)` because two finder harnesses call it: `dev/audit/rounds/round3/D2/dst_window_factors.py:151` and `dev/audit/rounds/round4/D2/d2_own_D2-02.py:134`.

Flow for the one change that crosses modules (P4):
`optimizer._grid_report → tariff.metering_windows → tariff.billed_windows ← tariff._peak_excess / peak_cost_batch`.
Before the change, the optimizer and both tariff charges each padded the factors themselves. After it, all three call the tariff's owner, so the published `peak_kw` and the priced excess cannot disagree on a window past the factors.

Invariants: every output is bit-for-bit what it was. P2 keeps the two debug messages, which differ only in the noun. In the house learner, P2 keeps the finite check before the vent CUSUM, so the detector still sees large residuals. P1 keeps the module-level placement that `_settle_interval_diag` needs.

## 3. Alternatives that lost

- **P8:** have `metering_windows` call `_window_means_batch(house[None, :])[0]`. That would give one owner for the whole partition, but it routes every scalar call through the batch path, which costs an extra matrix allocation per call on the Pi target (D9). It also moves the scalar's `if not pieces` fallback. The partition is the duplicated fact, so the partition is what gets an owner.
- **P5:** compute `n_windows` once in `_peak_billing` and pass it down. This calls the counting rule once instead of twice, but it changes the `_peak_window_factors` signature, which breaks the two finder harnesses above. It would also leave a copy of the counting rule in `_peak_billing`'s callers whenever a harness drives `_peak_window_factors` directly.
- **P3:** a module function in `coordinator.py`. It loses because the optimizer's own copies (`optimizer.py:3886`, `:4261`) could not call it without an import cycle. `OptimizationResult` owns both trajectories, so the rule belongs on it.
- **P6:** a sensor base-class method. It loses because the fact includes `waiting_for`, which only `_WaitsForEvidenceMixin` defines. The three other `insight` readers (`sensor.py` 2649, 2691, 2740) carry no `waiting_for` and are not in F5, so they are out of scope.
- **P1, `_maybe_run_fuse_advisor`:** the two reads in its clone (`power_cap_breach_c`, `projected_peak_kw`) are different facts from the planned split. The class matched only on the shape `float(d.get(k) or 0.0)`. The real duplicate of the planned split is `_settle_interval_diag` (`coordinator.py:1217`). A generic `_num_or_zero` helper would name a coercion, not a fact, so it lost. Measured: the fuse advisor leaves F5 once P1 lands and enters no other class.

## 4. Sibling sites (commands)

- `rg -n 'upper_temp_trajectory' custom_components/` lists every reader (15 lines, 11 sites). The round-1 regex missed `optimizer.py:4259-4264`, which gates through a local `two_zone`. Each site:
  - `optimizer.py:3886`, `optimizer.py:4261`, `coordinator.py:10008`, `coordinator.py:10057`: the P3 rule, all four covered by P3.
  - `optimizer.py:1689`: the field definition. `optimizer.py:2875`: the producer that writes it. Neither reads the rule.
  - `coordinator.py:2325` (`_sim_coldest`): the minimum over every zone, a different fact.
  - `coordinator.py:2885`: the recorded upper column, upper when present with no two-zone gate, a different fact.
  - `coordinator.py:4589-4591`: needs both zones present, a different fact.
- `rg -n 'np.ones\(windows' custom_components/` finds `tariff.py:876`, `tariff.py:1169` and `optimizer.py:4713`, all covered by P4.
- `rg -n 'int\(round\(window_minutes / max\(dt_hours' custom_components/` finds `tariff.py:557` and `:1077`, covered by P8.
- `rg -n '_window_slot\(' custom_components/heatpump_optimizer/tariff.py` finds 261, 306, 609 and 670. Sites 609 and 670 are covered by P9. Sites 261 and 306 are the tracker keying a live window, a different fact (no UTC walk), and are out of scope.
- `rg -n 'HOUSE_LOSS_MAX_RESIDUAL' custom_components/` finds 5556 and 5679, covered by P2. Site 1329 passes the constant as an argument, which is a third fact and out of scope.
- `rg -n 'for kw, _ in ranked\]' custom_components/` finds 332 and 413, covered by P7.

## 5. Evidence plan, by file

**Spike measurement.** I applied all nine shapes to a scratch copy of the base; the spike is not committed.
- F5_clone went from 24 to 15. All nine pairs left, and **none entered**.
- `tools/audit/archscore/score.py --delta`: `IMPROVES`, dS +4.79 (duplication_copies), no rises.
- `tests/structure.py`: no violation. Three rows improved: `class_excess_loc` 17640→17617, `duplication_copies` 14→10, `max_class_loc` 7975→7954. **No budget raise is owed.** Re-record with `--record`, and name those rows in the commit message.
- Bit-identity: 618 outputs of `metering_windows`, `_window_means_batch`, `plan_window_days` and `window_factors` were identical between base and spike. That covers random series, offsets 0–11, windows of 15/60/90 minutes, both DST days in Europe/Stockholm, and one naive start. Expected golden movement: none, so no claim-file touch.

**Failing test first, through the production path, one per pair.** Each test is added to an existing script, so no new closure is needed. Each test patches the new owner to a sentinel answer and drives **both** production callers. It asserts that both callers return the sentinel answer.
- At the base, each test fails because the owner does not exist and the second copy ignores it.
- After the fix, each test passes.
- A mutant that restores the inline copy at any caller is killed. Those caller lines are the mutation targets. For P3 there are four: `coordinator.py:10008`, `coordinator.py:10057`, `optimizer.py:3886` and `optimizer.py:4261`.

| pair | script (existing coverage) | drive |
|---|---|---|
| P1 | `tests/features.py` (`_accumulate_energy` 20001), `tests/boost_drift_replay.py` (`_settle_interval_diag` 673) | one pending dict; patched split → both the ledger split and the diag attribution see it |
| P2 | `tests/dst_checks.py` (both learners, 2128–2129) | residual 1.2 K > 1.0; patched gate accepts → both learners fold |
| P3 | `tests/features.py` (22475), `tests/boost_drift_replay.py` (599), `tests/stress.py` (1143, the `space_pins` run) | two-zone result; patched `sensor_trajectory` → lead buckets, next-room temp, the breach report (`_publish_breach_reports`) and the release steps (`_safety_release_steps(result, temp_min_bounds, space_pins, None)`) all read it |
| P4 | `tests/features.py` (`_grid_report` 16993) | masked tariff, factors shorter than windows; patched owner → `peak_kw`, `peak_cost` and `peak_cost_batch` all move |
| P5 | `tests/features.py` (17069) | patched count → factor length and `window_days` length agree |
| P6 | `tests/entities.py` (2475, 2484) | both sensors publish the patched owner's dict |
| P7 | `tests/features.py` (`_close_window` 3871) | `from_dict` round-trip plus close; patched owner observed on both paths |
| P8 | `tests/features.py` (16106) | patched partition → scalar and batch window counts both follow |
| P9 | `tests/dst_checks.py` (`window_factors` 59) | autumn fold; patched starts → factors and days both follow |

**Controls.**
- `enumerate_p2.py --fixture` should read 0 in every family.
- After each commit, F5 should drop exactly that pair and gain no entry.
- archscore should be read before and after, and must not read worse.

**Probe 6 (bind `defrost_interval`).** In `dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py`:
- add `"defrost_interval"` to the probe-6 eval locals, imported from the package's own `freq_control` (its owner);
- give `_Self` a `_pump_signals = SimpleNamespace(defrosting=False)` attribute.

Measured on a scratch copy, probe 6 then evaluates and reads **FAIL**: `'self._commanded_power() > 0.05 and reported >= hz_min and (not defrost_interval(...))' -> watch_active=True owner_runs=False`. That is a live F1_run_threshold copy at `coordinator._observe_frequency`, where 0.05 sits against `MIN_RUNNING_DRAW_KW`. Overall the probes read 6/6 FAIL. The fixer records this reading and does not fix it here: F1 is not this group's family.

## 6. Hot files, serial position, carries

- **Hot files:** `coordinator.py`, `optimizer.py`, `tariff.py`, `sensor.py`, and `tests/structure_budgets.json` (the re-record).
- **Order:** this group has no after edges. Rebase on main before re-recording the structure budgets, because any merge that moves `class_excess_loc` changes the recorded value.

### Notes for the fixer

- Keep P2's finite check where it is in the house learner, between the replay and the CUSUM. Only the magnitude gate moves into the owner. Merging the two checks would starve the vent detector.
- Spell P4's owner on `windows.shape[-1]` so that the 1-D scalar path and the 2-D batch path share it.
- Carry: R10-CLONE-2238 (item golden-check). Golden coverage for P1-P3, P5 and P7 is `tests/golden.py` in drift mode, through `tests/env_drift.py`: the `coord_*` fixtures run the coordinator (P1-P3, P7), and the optimizer scenarios run P3's optimizer sites and P5 (`capacity_tariff`, `capacity_tariff_15min`, `peak_masked`, `shoulder_two_zone`, `tariff_plus_two_zone`). The spike's 618-output check covered only the tariff partition and starts. Say in the body that the scoped gate ran these scripts with zero drift.
- Carry: R10-CLONE-2238 (item bugclasses-json). `dev/audit/config/bugclasses.json` changes: the P2 entry's instance rows for the nine pairs (lines 280-290 at base) are marked closed by this group, in the convention that file already uses for a closed instance. Where it has none, leave the file untouched and say why in the body.
- Carry: dismissed: probe-6 F1 reading belongs to the F1_run_threshold family, not this clone group (item probe6-observe-frequency)
- Carry: dismissed: `probes_p2.py --perturb` is stale at base because its first FIXES text is no longer in `optimizer.py`, which is outside the clone fix (item probes-perturb-stale)
