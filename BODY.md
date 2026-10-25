R10-ARCH-SHAPES: one owner per duplicated shape, power readings bounded

R10-ARCH-SHAPES (round 10, D7/D8, wave 22), fix-review round 4. This body is the round-4 re-cut (`fixer.md`, "Past three rounds, re-cut rather than repair"). Figures were taken in this pass at code head `94a4ea9044ed3b80d60f8c362f15f1067f861535`. origin/main was `c78df2b86b5ec51d631eb0ed18bbac8feecd166a` at `Sun Oct 25 23:04:40 UTC 2026`. The merge base is `f3ffb1c635327365841ad430ce8fad7488a02d61`.

Closes #2236.

Closes #2239.

Part of #2238. Its D8-s1-01 plan-view, pump, sensor and wood-advisor arms and its D7-s2-01 `pump_offline` arm close here. The D8-s1-01 reason-classifier arm is split out (below). The remaining P2 sweep instances named under the `channel_active_kw` dispositions stay with #2238.

**The split (round 4, the orchestrator's ruling under mandate 6329234399).** Round 3 was blocked on claim drift (comment 6403941902). The reason-classifier arm of D8-s1-01 moves golden `space_reasons`/`dhw_reasons`. It moves them on a set of scenarios that depends on the host, so no fixed claim set holds on every runner. This PR therefore drops that arm:
- the `_heating_draws` lines in `optimizer.classify_space_steps` / `classify_dhw_steps`;
- their helpers `channel_heating_draw` and `_heating_draws`;
- the feature check "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)";
- the two classifier dispositions in `tests/entities.py`, which now name the parked group.

Both claim files are byte-identical to the merge base: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/` is empty. The arm is parked, as one commit, at `park/r10-arch-shapes-classifier` (`996b54cf15ea3c7693383165ae2f080d2e04971b` on `a1d56b66f`). It is group R10-ARCH-SHAPES-CLASSIFIER, after R10-996-RUNNER-CLAIMS (Forward-carry).

Why the arm cannot land on every host identically (measured, Figures). The arm reclassifies a step only when the channel draws more than `CHANNEL_ACTIVE_KW` (0.05 kW) and the step's whole ask is at most `MIN_RUNNING_DRAW_KW` (0.1 kW). On this host the steps it moves sit mid-band, at least 2.5e-3 kW from either line, so this is not a float straddle. Whether a scenario has such a step at all is a property of the solve's basin, and a 1e-15 relative nudge to one price changes it. A more robust classifier cannot fix that. The two #996 instances are posted (comment 6404201979), and the count crossed `RUNNER_CONDITIONAL_REOPEN_AT`.

What remains, one owner per concern:

- **Power state as kW** (D7-s2-61): `inputs.state_power_kw(state, sign=...)` is the one live-state parse. The reading must be finite and in a known unit, and must still be finite after conversion. Each caller states its sign policy (`signed`, `clamp` or `positive`). The range bound belongs to the caller: `quiet_windows._within_nameplate` admits only `(0, p_max]`, so an absurd reading falls through to the next source, and `silent_cap_kw` no longer clips it at `p_max`.
- **Finite-float coercion** (D7-s2-58, #2239): `const.finite_float(value, default=None)`, in the package's dependency-free module, replaces the 13 coercers the census rule returns at the base. **Behaviour change:**
  - a `bool` is not a number, and neither are bytes;
  - numeric text is read;
  - NaN, the infinities and an int past a double are unreadable;
  - `pump_arbiter._step_kw` now refuses NaN, inf and `True`.
  `AccuracySample.from_dict.num` reads it too.
- **Hour clock** (D7-s2-57): `quiet_windows.wall_clock` folds 24:00 to 00:00, and `dhw_schedule.format_clock` keeps 24:00 in a window label. Every copy calls one of the two.
- **Cyclic range** (D7-s2-59 carry): `dhw_schedule.cyclic_span` owns the wrap. `grid_fee`'s range and day-selector parsers read it.
- **Channel line** (D8-s1-01 carry, minus the parked arm): `optimizer.CHANNEL_ACTIVE_KW` is the one 0.05 kW line. `optimizer.channel_heating_steps` is the one reader of "does this channel heat at this step": its own draw above the line, on a step `planned_draws_run` runs. These seats read it:
  - the plan view's `active_now`;
  - `_plan_slots`, which has no `threshold` parameter any more;
  - the space circulation pump (`pump_schedule.plan_commands_heat` takes the plan's space-heating flags);
  - the wood advisor, which takes `heat_pump_on_schedule`;
  - the system-identification experiment's `heat_pump_on` (`planned_draw_runs`);
  - the DHW schedule sensor, whose raw-draw fallback is deleted.
- **Pump freeze** (D7-s2-01 `pump_offline` carry): `_freq_fold_blocked` refuses every `pump_signals` freeze reason.

Alternatives considered:
- **Keep the classifier arm, claim the runner's latest pair.** The reviewer's table shows a third runner reading would refute it, so it was rejected.
- **Keep the arm, add may-drift entries for the movers.** The census union is not closed: away_setback moved in the cloud container and reads 0 at every nudge here. A named set leaks the way #1207 had to be widened, so this was rejected.
- **Make the classifier robust to the line.** The moved steps are mid-band, so there is nothing for robustness to fix. Rejected.

## Head

Code head `94a4ea9044ed3b80d60f8c362f15f1067f861535`, four commits on the round-3 PR head `d710a5af5bb2dd1263a5b72b77cdf8ecc011390b`, with no merge and no rebase:
- `a1d56b66f` is the split;
- `648f88d9e` adds the band census harness;
- `ec9687414` classifies it in `tests/closures.json` (`ci_predict.py --apply-inert`);
- `94a4ea904` gives the harness the canonical `repo_root`, for `harness_headers.py`'s depth-seam check.

`git merge-tree --write-tree origin/main HEAD` against `c78df2b86` exits 0 with no conflict, so no merge was made (`fixer.md` step 6). Every figure below is from this pass, on macOS arm64.

## Mutation proof

The round-4 delta deletes the classifier arm. Its "mutant" is the split commit itself, and the killing check travels with the arm on `park/r10-arch-shapes-classifier`.

For every fix predicate that remains, the driver did the following:
- applied one predicate replacement to a `git archive ec9687414` copy, or to a worktree at `ec9687414` for `tests/entities.py`, which needs a repository;
- ran the script that pins it, with `PYTHONPATH=tests/hastub`;
- reported the FAIL names beyond that copy's unmutated control.

The `features.py` archive control is `1 of 4410`, the archive-only #363 `recorded_at` check (`fixer.md` step 2). The `entities.py` worktree control is `4 of 2449`, the load-sensitive heartbeat self-tests. `ec9687414` and `94a4ea904` differ only in the harness's root lookup, which none of these scripts imports.

- `coordinator.py` `_run_system_identification`: `"heat_pump_on": planned_draw_runs(float(override))` -> `override > 0.05`. `tests/features.py` rc=1: "an experiment command under the running floor does not mark the pump on (D8-s1-01)".
- `accuracy.py` `AccuracySample.from_dict.num`: `value = finite_float(data.get(key))` -> a bare `float()`. `tests/features.py` rc=1: "a stored sample's numbers go through const.finite_float: a bool or a non-finite value loads as unknown (D7-s2-58 class)" (`True used to load as 1.0`).
- `coordinator.py` `_plan_slots`: `heating = channel_heating_steps(powers, other_powers)` -> `[p > 0.05 for p in powers]`. `tests/features.py` rc=1: "a plan slot holds only steps the plan runs, each channel on its own share (D8-s1-01)".
- `coordinator.py` `_async_drive_pumps`: `schedule = channel_heating_steps(...)` -> `[p > 0.05 for p in result.power_schedule]`. `tests/features.py` rc=1: "the space pump reads the plan's space-heating steps, not its raw draw (D8-s1-01)".
- `wood_fuel.py` `wood_fuel_from_parts`: `list(result.heat_pump_on_schedule or [])` -> `[p > 0.05 for p in result.power_schedule]`. `tests/features.py` rc=1: "a step the plan calls off is no pump hour for the wood advisor (D8-s1-01)".
- `coordinator.py` `_build_plan_views`: `channel_heating_steps(raw_space[:1], raw_dhw[:1])[0]` -> `raw_space[0] > 0.05`. `tests/features.py` rc=1: "a plan channel is heating now only on a step the plan runs (D8-s1-01)".
- `inputs.py` `state_power_kw`: `if kw is None or not math.isfinite(kw):` -> `if kw is None:`. `tests/features.py` rc=1: "a power state parses to finite kW under the caller's sign policy, or to no reading".
- `coordinator.py` `_freq_fold_blocked`: `freeze_reason is not None` -> `== pump_signals.FREEZE_COOLING`. `tests/features.py` rc=1: "an offline, faulted or cooling pump's interval never teaches the frequency map".
- `coordinator.py` `_pv_measured_production`: `sign="clamp"` -> `sign="signed"`. `tests/features.py` rc=1: "a negative production reading is clamped to zero, not propagated".
- `quiet_windows.py` `_within_nameplate`: the range bound -> `return kw`. `tests/manual_plan.py` rc=1: "a non-finite or over-nameplate power reading is no measurement" and "a frequency past its configured maximum measures nothing".
- `const.py` `finite_float`: the `bool` arm dropped. `tests/finite_boundary.py` rc=1: "const.finite_float reads a real number or numeric text, and nothing else -- not a bool, bytes, NaN, an infinity or an int past a double" (`{'True': 1.0, 'False': 0.0}`).
- `dhw_schedule.py` `_parse_day_selector`: `cyclic_span` -> an inline `(lo + k) % 7` wrap. `tests/entities.py` rc=1, beyond the control: "P2 owners: cyclic_range_wrap is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".
- `pump_arbiter.py` `_write_night_schedule`: `quiet_windows.wall_clock(nxt[0])` -> an inline `divmod`. `tests/entities.py` rc=1, beyond the control: "P2 owners: hour_clock is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" (`SEAM ['pump_arbiter.py:975 in _write_night_schedule']`), the same check for `slot_floor_rule`, and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".
- `tests/entities.py` `_p2_match_channel_line`, Compare arm -> `len(n.ops) == 1 and ...`, which leaves the chained spelling unread. `tests/entities.py` rc=1, beyond the control: "P2 owners: channel_active_kw is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" (`STALE-DISPOSITION ['coordinator.py::HeatPumpOptimizerCoordinator._record_accuracy']`, the chained `0.05 <= elapsed <= 2.0` unread) and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".
- `tests/entities.py` `_p2_match_channel_line`, by-name arm -> `False and ...`. `tests/entities.py` rc=1, beyond the control: the same `channel_active_kw` check (`STALE-DISPOSITION ['optimizer.py::classify_space_steps', 'optimizer.py::classify_dhw_steps']`, the classifier defaults unread) and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".

The driver is a one-off kept in the seat's evidence, not landed (`fixer.md` step 18). Each `old -> new` is above.

## Null control

- Unmutated head, in the worktree:
  - `tests/features.py` `ALL 4410 FEATURE CHECKS PASSED`. That is 4411 less the one classifier check that moved to the parked arm;
  - `tests/manual_plan.py` `ALL 132`;
  - `tests/finite_boundary.py` `ALL 108`.
- `tests/entities.py` reads `4 of 2449` at the head and `5 of 2445` at the merge base `f3ffb1c63`. Both were run in worktrees on this loaded box. I compared the sets of top-level FAIL names: the head's 4 are a subset of the base's 5, and all are heartbeat-timing self-tests. This diff adds none.
- `env_drift.py --all f3ffb1c63` at this head: "NO UNCLAIMED DRIFT: 56 scenario(s)", "NO STALE FIXTURE: 56", rc=0, with the claim list unchanged from the base. At `d710a5af5` (the arm in) this host moved `dhw_cold_tank` and `horizon_48h`. Those are exactly the two non-may-drift scenarios the band census finds band steps for at nudge 0, so the gate does read the arm on this host.
- Each harness's `--perturb` reads 0 at both ends (Figures).

## Figures

Every command was run with `PYTHONPATH=tests/hastub` (plus `:custom_components` for the harnesses) on macOS arm64, at the head unless an end is named.

- **Band census**, `dev/audit/harnesses/r10_band_census.py` (sha1 `b2b3a938866e6923748552125afda64a0d9ce599`, landed here), with no arguments:
  - `RESULT scenarios=50 susceptible=15 failures=0`;
  - the 9 already may-drift: flat_prices, direct_flow_carnot, tariff_plus_two_zone, valve_storage, valve_storage_smart_write, valve_upper_direct_slab, wood_coil, wood_two_tank, wood_two_tank_smart_write;
  - the 6 not may-drift: cool_rainy_summer, dhw_cold_tank, horizon_48h, valve_storage_flat_prices, valve_storage_low_target, valve_storage_small_tank.

  Rule: a scenario is susceptible when, at any of the nudges {0, 1e-15, 1e-12, 1e-9} to price n//3, its solve has a channel draw above 0.05 kW on a step whose whole ask is at most 0.1 kW. The same per-scenario lines came out at `d710a5af5` (arm in) and at this head, compared with `diff` and printing `IDENTICAL-PER-SCENARIO`, so the solve does not depend on the arm. Some single nudges change the band count: valve_storage_flat_prices goes 0 -> 7 at 1e-15, and valve_storage_small_tank 0 -> 1 at 1e-15. away_setback reads 0 at every nudge. It moved in the cloud container, so the union is a lower bound.
- **Band positions.** On this host the band steps of the two scenarios that move with the arm are:
  - `dhw_cold_tank` step 26: space 0.071929 kW, dhw 0;
  - `horizon_48h` step 153: space 0.097477 kW, dhw 0.

  The nearest line is 2.2e-2 and 2.5e-3 kW away respectively, so these are mid-band values, not float straddles. On the runner `valve_storage_flat_prices` moved at steps 28-31. On this host those steps read 0.296791-0.312815 kW, outside the band. These values were read with `golden.capture` from a one-off probe in the seat's evidence.
- **The runner's reading** (comment 6403941902, job 121296829654, at `d710a5af5`): STALE `away_setback` and `valve_storage_small_tank`, plus unclaimed `valve_storage_flat_prices` (4 leaves) and `valve_storage_low_target` (3). This head claims none of those and carries none of the arm, so CI `tests / fast` at this head judges whether the runner sees any drift.
- D7-s2-61, `dev/audit/rounds/round10/catchup/arch-s2/probe_coercion_reach.py`, run from each tree's own copy. The merge base gives `silent_cap_kw=6.0` (p_max, no cap) for `1e6`, `1e400` and `inf`, with `inf_changes_decision=1`. The head gives 4.2, the `unknown` arm, for all three, with `inf_changes_decision=0`. `unknown` reads 4.2 and `3` reads 3.6 at both ends.
- D7-s2-01 `pump_offline`, `dev/audit/rounds/round10/D7/s2/learner_gates.py`: `pump_offline.learners_ingesting` is 1 at the base and 0 at the head. `freq_map_clean_folds=8` and `freq_map_defrost_folds=0` at both ends.
- D7-s2-59, `dev/audit/harnesses/r10_weekday_range_twins.py`: `pairs=49 disagreements=0` at both ends. It reads flat because this is a refactor. The class rule is the `cyclic_range_wrap` P2 entry.
- D7-s2-58, `python3 dev/audit/harnesses/r10_finite_float_census.py <head> <tree>`: `RESULT coercers=13` at the base and `RESULT coercers=1` at the head (`const.py::finite_float`).
- D7-s2-57, `grep -rnE '%=? *\(?24 \* 60\)?' custom_components/heatpump_optimizer/*.py | wc -l`: 5 at the base and 2 at the head, the two owners.
- D8-s1-01 finder harness `dev/audit/rounds/round10/D8/s1/f1_active_now.py` (sha1 `766cc95a3b886f3f70d122a167028d2313d78048`):
  - at the base: `heating_now_while_off=1`, `slot_steps_declared_off=0`, `snapshots=36`;
  - at the head: 0 and 0;
  - `--perturb`: 0 and 0 at both ends, `perturbed=1`.

  The slot arm reads 0 at both ends on this host (per-BLAS, as its header says), hence the companion.
- Companion `dev/audit/harnesses/r10_channel_running_rule.py` (sha1 `713436520d8f67bc9539ed962329ac1f0e8ff7c7`):
  - at the base: `slot_steps_declared_off=5`, `reason_steps_declared_off=5`, `sensor_periods_declared_off=2`;
  - at the head: 0, **5** and 0 (`sensor_state=None`). The reason arm reads 5 at both ends because it is the parked arm;
  - `--perturb`: 0, 0 and 0 at both ends.
- Class enumeration, `python3 dev/audit/harnesses/r10_channel_line_reach.py <head> <tree>` (the `channel_active_kw` rule): `RESULT hits=26` at the base and `RESULT hits=19` at the head. Each of the 19 head sites, with its disposition:
  - the owner, `optimizer.py::channel_heating_steps`;
  - `classify_space_steps` and `classify_dhw_steps`: distinct finding R10-ARCH-SHAPES-CLASSIFIER, the parked arm;
  - `accuracy.py::delivered_ratio` (2) and `AccuracyTracker.power_ratio`: a ratio's denominator floor;
  - `coordinator.py::_async_learn_buffer_cooling` and `_observe_frequency`: #2238 P2 sweep instances;
  - `freq_control.py::FrequencyMap.observe`, `recommend` and `evidence_exhausted`: the map's own metered floor;
  - the non-power sites, each dispositioned by its unit: `away.py::estimate_recovery_hours`, `_maybe_run_fuse_advisor`, `_record_accuracy`, `DhwProfileLearner.async_learn_usage`, `DhwPlanner._dhw_shortfall`, `ledger.py::freeze_month_report` (2) and `narrative.py::build`.
- `python3 tests/closure.py select --diff f3ffb1c63`: `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` In the worktree at `ec9687414`, rc=0 for:
  - `features.py`, `finite_boundary.py`, `manual_plan.py`, `structure.py` (STRUCTURE RATCHET PASSED) and `plan_view.py`;
  - `wood_advisor.py`, `typing_ruler.py`, `guard_pins.py`, `deployment_shape.py`, `doc_claims.py`, `edge.py` and `config_flow_steps.py`;
  - `block_duty.py`, `debug_collect.py`, `validate.py`, `solar_alignment.py`, `open_meteo.py`, `boost_drift_replay.py` (46), `frontend.py` and `arch_score_head.py` (18).

  `harness_headers.py` reads `ALL 112 HARNESS HEADER CHECKS PASSED` at `94a4ea904`. At `ec9687414` it was `1 of 112`, the depth-seam check (Red checks). `tests/entities.py` is under Null control, and `env_drift.py --all` is under Null control. Left to CI: `card.mjs`, `card_drift.mjs`, `stress.py`, `backtest.py`, `optimality.py` and `golden.py`.
- `python3 tools/audit/archscore/score.py --diff f3ffb1c63 HEAD`: `Architecture score: dS +1.8325 IMPROVES` (see `## Architecture score`).
- `python3 tools/pr/ci_predict.py --base origin/main`: "no closures, fast, wave-script or instrument red predicted against f3ffb1c63532", and 71 unpinned sites, listed below. That is 74 at round 3 less the 3 sites of the parked helpers.

## Architecture score

Architecture score: dS +1.8325 IMPROVES against the merge base `f3ffb1c63` (`python3 tools/audit/archscore/score.py --diff f3ffb1c635327365841ad430ce8fad7488a02d61 HEAD`). No gate metric rises.

- duplication_copies 38 -> 35
- coord_footprint 2446 -> 2437
- params_over_10 7 -> 6
- layer_violations 17 -> 13
- private_cross_module 12 -> 10

## Red checks

- **`tests / fast (3.14)`** was red at `d710a5af5` on claim drift (comment 6403941902). The cause is the classifier arm's host-conditional drift. This head removes the arm and every claim, so there is nothing left to drift or go stale (Figures).
  - Cheaper detector: none exists before the runner. A dev box is a different numeric environment, and the census shows any host can move a different subset.
  - Countermeasure: the claim-grammar group R10-996-RUNNER-CLAIMS, opened when #996's tally crossed its threshold (comment 6404201979).
- **`tests/harness_headers.py`** "every inlined walk matches the canonical helper and no depth root remains" went red locally at `ec9687414`, before any push. The new harness used `parents[3]`. `94a4ea904` inlines the canonical `repo_root`. The cheaper detector is that check itself, run before the handoff, so none is owed.
- **`tests / mutation`** is red as predicted: the 71 unpinned sites below. `tests / mutation-autofix` reported skip-measure-failed at `d710a5af5`, the bot's own report that it did not repair. The pin run `python3 tests/mutation_table.py --pin-killed --base origin/main` is owed and carried to the orchestrator. `ci_predict.py` named every site before the push, so no new detector is owed.

## Forward-carry

- The D8-s1-01 reason-classifier arm: `optimizer.classify_space_steps` / `classify_dhw_steps` read each channel's draw only on its `channel_heating_steps`. The commit carries the helpers `channel_heating_draw` / `_heating_draws`, the feature check "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)", and the two `tests/entities.py` dispositions back to the owner-module reading. It is commit `996b54cf15ea3c7693383165ae2f080d2e04971b` on `park/r10-arch-shapes-classifier`. It claims nothing until the claim grammar lands, and the band census is its evidence. Carry: R10-ARCH-SHAPES-CLASSIFIER
- The census `dev/audit/harnesses/r10_band_census.py` and its 15-scenario susceptible set are the input to the claim grammar for runner-conditional drift. The set is a lower bound: away_setback is missing from it. Carry: R10-996-RUNNER-CLAIMS

## Friction

none

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head lists 71 sites the diff adds, all under `custom_components/`. Each one is owed to the pin run named under Red checks (`python3 tests/mutation_table.py --pin-killed --base origin/main`), because `mutation-autofix` reported skip-measure-failed at `d710a5af5` and pinned nothing. The fixer's own kills of the fix predicates are under Mutation proof.

- `custom_components/heatpump_optimizer/accuracy.py:124 BOOLOP: return value if value is not None and value >= lo else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/accuracy.py:124 CMP_BOUND: return value if value is not None and value >= lo else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/accuracy.py:124 RETURN_DEL: return value if value is not None and value >= lo else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/const.py:1313 GUARD_OFF: if isinstance(value, bool) or not isinstance(value, (Real, s`: owed to the pin run.
- `custom_components/heatpump_optimizer/const.py:1319 RETURN_DEL: return result if math.isfinite(result) else default`: owed to the pin run.
- `custom_components/heatpump_optimizer/const.py:1330 GUARD_OFF: if volume is None:`: owed to the pin run.
- `custom_components/heatpump_optimizer/const.py:1332 CLAMP_DROP: volume_m3 = max(volume, 1e-6) / 1000.0`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:415 BOOLOP: return value if value is not None and value >= lo else defau`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:415 CMP_BOUND: return value if value is not None and value >= lo else defau`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:415 RETURN_DEL: return value if value is not None and value >= lo else defau`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:713 RETURN_DEL: return None if temperature is None else finite_float(tempera`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:1049 GUARD_OFF: if coord._pump_signals.freeze_reason is not None:`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:3973 CMP_BOUND: abs(finite_float(action.get("displace_value"), 0.0)) > 0.01`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:4339 BOOLOP: other_powers[i] for i in span if i < len(other_heating) and `: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:4339 CMP_BOUND: other_powers[i] for i in span if i < len(other_heating) and `: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:4357 GUARD_OFF: if on:`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:4525 BOOLOP: raw_space and channel_heating_steps(raw_space[:1], raw_dhw[:`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:4544 BOOLOP: raw_dhw and channel_heating_steps(raw_dhw[:1], raw_space[:1]`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:5082 CLAMP_DROP: max(0.0, finite_float(first.get("wind_speed"), 0.0)),`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:5083 CLAMP_DROP: max(0.0, finite_float(first.get("precipitation"), 0.0)),`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:7049 CLAMP_DROP: gust = max(0.0, finite_float(entry.get("wind_speed"), 0.0))`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:7050 CLAMP_DROP: rain = max(0.0, finite_float(entry.get("precipitation"), 0.0`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:8498 GUARD_OFF: if kw is None:`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:9561 RETURN_DEL: return state_power_kw(self.hass.states.get(entity_id), sign=`: owed to the pin run.
- `custom_components/heatpump_optimizer/coordinator.py:10359 CLAMP_DROP: book["kwh"] = finite_float(book.get("kwh"), 0.0) + max(0.0, `: owed to the pin run.
- `custom_components/heatpump_optimizer/dhw_schedule.py:94 RETURN_DEL: return [first + (start - first + k) % size for k in range((e`: owed to the pin run.
- `custom_components/heatpump_optimizer/dhw_schedule.py:125 RETURN_DEL: return sorted(cyclic_span(lo, hi, len(_DAY_TOKENS)))`: owed to the pin run.
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 BOOLOP: if run is not None and len(ordered) >= 3:`: owed to the pin run.
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 CMP_BOUND: if run is not None and len(ordered) >= 3:`: owed to the pin run.
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 GUARD_OFF: if run is not None and len(ordered) >= 3:`: owed to the pin run.
- `custom_components/heatpump_optimizer/dhw_schedule.py:465 RETURN_DEL: return ", ".join(f"{format_clock(s)}-{format_clock(e)}" for `: owed to the pin run.
- `custom_components/heatpump_optimizer/entry_config.py:33 RETURN_DEL: return finite_float(value)`: owed to the pin run.
- `custom_components/heatpump_optimizer/freq_control.py:121 RETURN_DEL: return (finite_float(reading.state), hz_min, hz_max, source)`: owed to the pin run.
- `custom_components/heatpump_optimizer/grid_fee.py:132 RETURN_DEL: return frozenset(cyclic_span(start, end, size, first))`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:391 GUARD_OFF: if state is None:`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:394 GUARD_OFF: if value is None:`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:397 GUARD_OFF: if kw is None or not math.isfinite(kw):`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:399 GUARD_OFF: if sign == "clamp":`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:400 CLAMP_DROP: return max(0.0, kw)`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:401 GUARD_OFF: if sign == "positive":`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:402 CMP_BOUND: return kw if kw > 0.0 else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/inputs.py:403 RETURN_DEL: return kw`: owed to the pin run.
- `custom_components/heatpump_optimizer/modbus_prefill.py:182 RETURN_DEL: return None if row is None else finite_float(row[1])`: owed to the pin run.
- `custom_components/heatpump_optimizer/optimizer.py:1339 CONST: CHANNEL_ACTIVE_KW = 0.05`: owed to the pin run.
- `custom_components/heatpump_optimizer/optimizer.py:1354 GUARD_OFF: if other_kw is not None:`: owed to the pin run.
- `custom_components/heatpump_optimizer/optimizer.py:1358 BOOLOP: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: owed to the pin run.
- `custom_components/heatpump_optimizer/optimizer.py:1358 CMP_BOUND: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: owed to the pin run.
- `custom_components/heatpump_optimizer/optimizer.py:1358 RETURN_DEL: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: owed to the pin run.
- `custom_components/heatpump_optimizer/price_model.py:760 RETURN_DEL: return finite_float(raw)`: owed to the pin run.
- `custom_components/heatpump_optimizer/price_tiles.py:115 RETURN_DEL: return finite_float(answer.get(key))`: owed to the pin run.
- `custom_components/heatpump_optimizer/pump_arbiter.py:465 RETURN_DEL: return finite_float(_planned_room(result, now, "power_schedu`: owed to the pin run.
- `custom_components/heatpump_optimizer/pump_schedule.py:100 GUARD_OFF: if not space_heating:`: owed to the pin run.
- `custom_components/heatpump_optimizer/pump_schedule.py:105 RETURN_DEL: return bool(space_heating[idx]), bool(space_heating[nxt])`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:286 RETURN_DEL: return minutes // 60, minutes % 60`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:291 RETURN_DEL: return datetime.combine(day, time(*wall_clock(hour)), tzinfo`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:330 RETURN_DEL: return state_power_kw(get_state(power_id), sign="positive")`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:343 BOOLOP: return kw if kw is not None and 0.0 < kw <= p_max else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:343 CMP_BOUND*2: return kw if kw is not None and 0.0 < kw <= p_max else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:343 RETURN_DEL: return kw if kw is not None and 0.0 < kw <= p_max else None`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:401 CLAMP_DROP: return max(measured, CAPACITY_FLOOR_FRACTION * float(p_max))`: owed to the pin run.
- `custom_components/heatpump_optimizer/quiet_windows.py:654 RETURN_DEL: return f"{clock_h:02d}:{clock_m:02d}"`: owed to the pin run.
- `custom_components/heatpump_optimizer/sensor.py:1203 BOOLOP: if not (isinstance(plan, dict) and isinstance(plan.get("slot`: owed to the pin run.
- `custom_components/heatpump_optimizer/sensor.py:1203 GUARD_OFF: if not (isinstance(plan, dict) and isinstance(plan.get("slot`: owed to the pin run.
- `custom_components/heatpump_optimizer/sensor.py:1381 RETURN_DEL: return None if value is None else round(value - DHW_MIN_TEMP`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:131 GUARD_OFF: if not on:`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:136 CMP_BOUND: if wood_sek < finite_float(price, 0.0) / cop_f:`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:136 GUARD_OFF: if wood_sek < finite_float(price, 0.0) / cop_f:`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:157 CMP_BOUND: cop = finite_float(cops[i] if i < len(cops) else 0.0, 0.0)`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:215 CMP_BOUND: return cheaper_hour_count(wood_sek, prices, cops, runs) > 0`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:365 CMP_BOUND: if finite_float(forecast_kw[i], 0.0) > 0.0:`: owed to the pin run.
- `custom_components/heatpump_optimizer/wood_fuel.py:365 GUARD_OFF: if finite_float(forecast_kw[i], 0.0) > 0.0:`: owed to the pin run.
