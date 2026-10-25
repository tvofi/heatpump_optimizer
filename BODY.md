R10-ARCH-SHAPES (round 10, D7/D8, wave 22). The bug comes first. D7-s2-61: a heat-pump power entity reading `inf`, `1e400` or a finite absurd figure (100 kW) made the quiet-window ceiling the nameplate itself, so there was no silent cap. `silent_cap_kw` clipped any reading past `p_max` down to `p_max`, and the frequency and fraction fallbacks never ran. Then come the duplicated-shape owners from ARCH-s2: hour-clock (D7-s2-57), finite-float (D7-s2-58), the weekday cyclic range (D7-s2-59, carried from R10-TARIFF) and the plan's channel line (D8-s1-01, carried from R10-SENSOR-PAYLOAD). Last is the `pump_offline` arm of D7-s2-01, carried from R10-FREQ-DEFROST.

Closes #2236.

Closes #2239.

Part of #2238 (its D8-s1-01 and D7-s2-01 `pump_offline` arms close here; the remaining P2 sweep instances named under the `channel_active_kw` dispositions stay with #2238).

What changes, one owner per concern:

- **Power state as kW** (D7-s2-61): `inputs.state_power_kw(state, sign=...)` is now the one live-state parse. The state must be finite and its unit known, and the converted figure must be finite too: `1e306 MW` overflows on conversion. The caller states its sign policy: `signed` for the peak listener, `clamp` for PV production, `positive` for the quiet-window ceiling. It replaces three hand parses: `quiet_windows._power_entity_kw`, `coordinator._on_power_event` and `_pv_measured_production`. **The range bound is the caller's.** `quiet_windows._within_nameplate` admits only `(0, p_max]`, and it bounds both the power reading and the frequency-scaled figure, so an absurd reading falls through to the next source. `silent_cap_kw` no longer clips at `p_max`.
- **Finite-float coercion** (D7-s2-58, #2239): `const.finite_float(value, default=None)` lives in the package's dependency-free module, so no model or learner module climbs to the glue layer for it. It replaces `coordinator._as_float` and every other coercer the census rule returns at the base (list under Figures). **Behaviour change, stated as the carry asks:** a `bool` is not a number (`True` used to read as 1.0 in `pump_arbiter._finite_or_none`, `float()` and others), and neither are bytes. Numeric text is read. NaN, the infinities and an int past a double are all unreadable. `pump_arbiter._step_kw` now refuses NaN and inf, where `_finite_or_none` passed them (`isinstance(value, (int, float))`). It also refuses `True`, and it reads numeric text.
- **Hour clock** (D7-s2-57): `quiet_windows.wall_clock`, where a clock folds 24:00 to 00:00, and `dhw_schedule.format_clock`, where a window label keeps 24:00. The two owners name the one real difference. `pump_arbiter._night_clock`, the GCHV `_gchv_at`/`_fmt` copies and the `format_windows`/`dhw_draws` copies now call them.
- **Cyclic range** (D7-s2-59 carry): `dhw_schedule.cyclic_span` owns the wrap. `grid_fee._parse_cyclic_range`, `_parse_day_selector` and `_format_day_selector` read it, and the two `cyclic_range_wrap` dispositions are removed from `tests/entities.py`.
- **Channel line** (D8-s1-01 carry): the 0.05 kW line has one owner, `optimizer.CHANNEL_ACTIVE_KW`, and one reader of "does this channel heat at this step", `optimizer.channel_heating_steps` (its own draw above the line, on a step `planned_draws_run` runs). Every seat that answered that question from a raw draw now reads the plan's running rule:
  - the plan view's `active_now` (both channels);
  - `_plan_slots`, which merges slots on `channel_heating_steps` and has lost its `threshold` parameter; its shared-energy figure reads the other channel's heating steps. The simulator's two slot counts now pass the other channel too;
  - the reason classifiers `classify_space_steps` / `classify_dhw_steps`, which read `channel_heating_draw` (the draw on heating steps, 0 elsewhere), so a step the plan calls off gets an idle code;
  - the DHW schedule sensor, whose raw-draw fallback is deleted. Its period count is the plan's own slot count, and a payload without `dhw_plan` reads unknown (`None`). The coordinator publishes `dhw_plan` beside every non-empty `dhw_schedule`, so production never reaches that branch;
  - the space circulation pump: `pump_schedule.plan_commands_heat` takes the plan's space-heating flags, which the coordinator computes with `channel_heating_steps`. Its own `_PLAN_ACTIVE_KW = 0.05` is deleted;
  - the wood advisor: `wood_fuel.cheaper_hour_count` / `wood_cheaper` / `build_wood_fuel_view` take the plan's `heat_pump_on_schedule` (`runs`) in place of two power series and `PUMP_HOUR_KW = 0.05`, which is deleted. `max(space, dhw) > 0.05` was a third spelling of the pump's running rule.

  The `channel_active_kw` P2 rule in `tests/entities.py` (`_p2_match_channel_line`) now reads every spelling of the line: a power comparison against the literal (the operand pattern now includes `space`), a threshold or `_kw` parameter defaulting to 0.05, any read of `CHANNEL_ACTIVE_KW` by name, and a new module-level kW constant bound to 0.05. A rename therefore no longer hides a site.
- **Pump freeze** (D7-s2-01 `pump_offline` carry): `_freq_fold_blocked` refuses any `pump_signals` freeze reason (offline, fault, cooling), not cooling alone.

Alternatives considered:

- A finiteness check alone (the verifier's patch 03) was rejected: the carry measured that 100 kW still gave 6.0 after it.
- For the channel line, a class rule that matched only the literal (round 1) was rejected by review: renaming the literal hid the sites. Keeping the DHW sensor's fallback with a running-rule read was rejected because its payload, `dhw_schedule`, carries no space draw, so the rule cannot be applied there. Adding a per-step flag to `dhw_schedule` would duplicate the plan's slot list and move every coordinator golden. The wood advisor and the space pump take the plan's flags from the coordinator, not from an import. `thermal_model` imports `wood_fuel`, so `wood_fuel` cannot import the running-rule owner without a cycle, and `pump_schedule` stays free of the optimizer.
- A new `finite.py` (2c0bc14d7) was folded into `const.py` (0ef69bfcf): `const.py` is already the dependency-free module every layer imports, and a new module was one more import edge for nothing.
- The range bound was put in the caller, not in `state_power_kw`, because only the caller owns the envelope. A PV meter or grid meter has no nameplate.

The architect note's seam: every `coordinator.py` hunk is a float-coercion call site moving to the owner, plus the three power parses, `_freq_fold_blocked` and the `active_now`/`_plan_slots` lines the carries assigned here.

**Architect note amendment.** Round 2 adds two `coordinator.py` hunks outside the note's seam (float coercion only). The first is `_async_drive_pumps`, the space pump's plan lookup, which now passes `channel_heating_steps` over both schedules. The second is the simulator's two `_plan_slots` calls, which now pass `other_powers=`. The class closure for D8-s1-01 requires both: the class rule returns the pump's `_PLAN_ACTIVE_KW` seat, and the simulator's slot counts read the same merge. The orchestrator accepted both hunks under mandate 6329234399 (ruling 1 to this seat, 2026-10-25). `git merge-tree --write-tree` against R10-PARAMS-OWNER's local head `c8a234897` reports no conflict.

## Head

Round 2: `9c9d12c827fd53aa2e6cb6dadb13bf5423a340ce`. This is fix-review round 2. Round 1's verdict (blocked, comment 6400399252) was measured at `6feac7eceeff979bfe3692555179565bde565d9b`. This head adds ten commits to it, `41c7f46d2..9c9d12c82`, with no merge or rebase, so the merge base stays `da12aa37dee15b9e9567bd6c848493436f2592dd`. `git merge-tree --write-tree origin/main HEAD` reports no conflict. Every round-2 figure below was taken at this head or at the commit it names, on macOS arm64 on 2026-10-25. Round-1 figures are kept where the round-2 delta does not reach them, and each names its SHA.

`6feac7ece` merges main `da12aa3` into `21d646821`, the handed-off round-1 code head, automatically and with no resolution. `21d646821` is the merge of origin/main `bc52ad2af` into `c2dc1e39b`.

The failing test came first: `26be3410d` adds `tests/manual_plan.py`'s two D7-s2-61 checks before any fix. With `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` in a `git archive 26be3410d` copy, `2 of 132 manual plan checks FAILED`. At this head, `ALL 132 manual plan checks PASSED`.

## Mutation proof

**Round 2 (head `e43fcdcd6`).** Each mutant was applied to a `git archive e43fcdcd6` copy and run against the script that pins it. The exception is the two `tests/entities.py` sensor mutants: an archive copy of `tests/entities.py` exits before its sensor section (it needs a git repository), so those ran in a detached worktree at `e43fcdcd6`. The FAIL names below are those beyond the unmutated control's own (#363 in an archive copy of features; the heartbeat self-tests in entities).

- `coordinator.py` `_plan_slots`: `heating = channel_heating_steps(powers, other_powers)` -> `heating = [p > 0.05 for p in powers]`. `tests/features.py` rc=1: "a plan slot holds only steps the plan runs, each channel on its own share (D8-s1-01)".
- `optimizer.py` `classify_space_steps`: the line `power, other = _heating_draws(power, other)` deleted. `tests/features.py` rc=1: "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)".
- `optimizer.py` `classify_dhw_steps`: `power, other = _heating_draws(power, ctx.other)` -> `other = ctx.other`. `tests/features.py` rc=1: the same check.
- `coordinator.py` `_async_drive_pumps`: `schedule = channel_heating_steps(result.power_schedule, result.dhw_power_schedule)` -> `schedule = [p > 0.05 for p in result.power_schedule]`. `tests/features.py` rc=1: "the space pump reads the plan's space-heating steps, not its raw draw (D8-s1-01)".
- `wood_fuel.py` `wood_fuel_from_parts`: `list(result.heat_pump_on_schedule or [])` -> `[p > 0.05 for p in result.power_schedule]`. `tests/features.py` rc=1: "a step the plan calls off is no pump hour for the wood advisor (D8-s1-01)".
- `sensor.py` `DHWScheduleSensor.native_value`: the no-plan branch's `return None` -> `return "1 heating period"`. `tests/entities.py` rc=1 (worktree, FAIL set = control + 1): "and a schedule with no plan dict has no period count: unknown, not a count from raw draws (#1644, D8-s1-01)".
- `tests/entities.py` `_p2_match_channel_line`: the by-name arm -> `False and ...` (the instrument mutant, named in the review). `tests/entities.py` rc=1: "P2 owners: channel_active_kw is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)". The by-name arm alone is what reaches the classifier defaults and `channel_heating_steps`.

The round-2 checks were written with the fix, not run first at `6feac7ece`. The evidence that each one reads the defect is the mutant above that restores its base predicate. The companion harness's `6feac7ece` column reads the same defect in the same readers.

**Round 1 (code head `c2dc1e39b`).**

Each mutant is one fix predicate, replaced in a `git archive c2dc1e39b` copy (the pre-merge code head; the merge added no line to any mutated function, and every mutated predicate text is unchanged at this head) by the driver below. It is then run with `PYTHONPATH=tests/hastub python3 tests/<script>.py` against the script that pins it, and the copy is discarded. The worktree is never edited. A `git archive` copy fails `tests/features.py`'s "and the path that proceeds still stamps a resolvable recorded_at (#363)" on every run, baseline included (`fixer.md` step 2). It is the runner's failure, not the mutant's, and it is left out of the lists below.

- `quiet_windows.py` `_within_nameplate`: `return kw if kw is not None and 0.0 < kw <= p_max else None` -> `return kw` (the range bound, D7-s2-61). `tests/manual_plan.py` rc=1: "a non-finite or over-nameplate power reading is no measurement", "a frequency past its configured maximum measures nothing".
- `inputs.py` `state_power_kw`: `if kw is None or not math.isfinite(kw):` -> `if kw is None:` (finiteness after conversion). `tests/features.py` rc=1: "a power state parses to finite kW under the caller's sign policy, or to no reading" (the `1e306 MW` row reads `inf`).
- `const.py` `finite_float`: `if isinstance(value, bool) or not isinstance(value, (Real, str)):` -> `if not isinstance(value, (Real, str)):` (the bool policy). `tests/finite_boundary.py` rc=1, `1 of 108`: "const.finite_float reads a real number or numeric text, and nothing else -- not a bool, bytes, NaN, an infinity or an int past a double".
- `coordinator.py` `_freq_fold_blocked`: `if coord._pump_signals.freeze_reason is not None:` -> `== pump_signals.FREEZE_COOLING` (the D7-s2-01 `pump_offline` arm). `tests/features.py` rc=1: "an offline, faulted or cooling pump's interval never teaches the frequency map".
- `coordinator.py` `_build_plan_views`: `raw_space and channel_heating_steps(raw_space[:1], raw_dhw[:1])[0]` -> `raw_space and raw_space[0] > 0.05` (D8-s1-01). `tests/features.py` rc=1: "a plan channel is heating now only on a step the plan runs (D8-s1-01)".
- `coordinator.py` `_pv_measured_production`: `sign="clamp"` -> `sign="signed"`. `tests/features.py` rc=1: "a negative production reading is clamped to zero, not propagated".
- `dhw_schedule.py` `_parse_day_selector`: `return sorted(cyclic_span(lo, hi, len(_DAY_TOKENS)))` -> the base's inline `(lo + k) % 7` wrap (D7-s2-59). `tests/entities.py` rc=1: "P2 owners: cyclic_range_wrap is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".
- `pump_arbiter.py` `_write_night_schedule`: `quiet_windows.wall_clock(nxt[0])` -> an inline `% (24 * 60)` divmod (D7-s2-57). `tests/entities.py` rc=1: "P2 owners: hour_clock is decided only by its owner or a dispositioned site, ..." and the same null-controls check.

The two `tests/entities.py` mutants are measured against `tests/entities.py` on a `git archive` copy at this head, whose FAIL names are otherwise the copy's own. Those are the git-repository checks (#2119, the handover reachability) and the load-sensitive heartbeat and a3-a13 harness self-tests, all of which also fail in the base archive copy. The two P2 checks named above fail in neither the base copy nor this head's worktree run.

The driver was a one-off kept in the seat's scratch space and not landed (`fixer.md` step 18). Each mutant's `old -> new` is printed above.

## Null control

- The unmutated head is the mutants' control: `tests/features.py` `ALL 4391 FEATURE CHECKS PASSED`, `tests/manual_plan.py` `ALL 132 manual plan checks PASSED`, `tests/finite_boundary.py` `ALL 108 FINITE BOUNDARY CHECKS PASSED` (in the worktree at this head).
- `probe_coercion_reach.py`: the `unknown` state (every parser refuses) reads 4.2 at both ends, and the legitimate `3` kW reading reads 3.6 at both ends, so the fix moves only the out-of-range rows. Its `--perturb`-style in-memory refusal arm reads `perturbed_1e400_equals_unknown=1` at both ends.
- Round 2 mutants: each was run against an unmutated copy of the same tree as its control. That copy's `tests/features.py` fails only the archive's #363 check, and its `tests/entities.py` FAIL set equals the worktree's.
- `r10_channel_running_rule.py --perturb` reads 0 at both ends (Figures), and so does the same tree's unperturbed head.
- `f1_active_now.py --perturb` (the finder's in-memory perturbation) reads `heating_now_while_off=0` at base and head. The harness moves under its own perturbation, and the head reaches the perturbed value without it.
- `r10_weekday_range_twins.py --identity` reads 0 of 49 at both ends, and `--perturb` reads 49 of 49 at both ends.
- Finite-float census: the rule (`tests/finite_boundary.py::_finite_float_coercers`) must return a planted coercer. The census asserts this itself ("the census reaches the owner and a planted sibling").
- P2 registries `hour_clock`, `power_state_kw` and `channel_active_kw` each carry a `_P2_PLANTS` entry that the registry must refuse.
- P8 state-float census: a planted probe of three reads must return three sites (below).
- Round 2, `tests/entities.py` in worktrees: `4 of 2448 ENTITY CHECKS FAILED` at `6feac7ece` and `4 of 2449` at `e43fcdcd6`. The FAIL-name sets are identical (`diff <(grep '^  FAIL' base | sed 's/  \[.*//' | sort -u) <(... head ...) && echo IDENTICAL-FAIL-SETS` printed `IDENTICAL-FAIL-SETS`). They are the heartbeat-timing self-tests on this loaded box. This diff adds none.
- Round 1, `tests/entities.py` in detached worktrees: `4 of 2440 ENTITY CHECKS FAILED` at the pre-merge base `de794b537`, `4 of 2443` at the pre-merge head `c2dc1e39b`, and `4 of 2448` at this merged head (run in the worktree). The set of FAIL names is identical across all three, compared with `diff` over `grep '^  FAIL' | sed 's/  \[.*//' | sort -u` and printing nothing. They are the heartbeat-timing self-tests, which are load-sensitive on this box (load average above 100). This diff adds none.

## Figures

All harnesses were run from a `git archive` export of each end, with `PYTHONPATH=tests/hastub python3 <path>` from the export root.

- D7-s2-61, `dev/audit/rounds/round10/catchup/arch-s2/probe_coercion_reach.py`. Base `bc52ad2af`: `1e6`, `1e400` and `inf` give `silent_cap_kw=6.0` (p_max, no cap), `inf_changes_decision=1`, `inf_equals_finite_absurd=1`. Head: all three give 4.2 (the `unknown` arm), `inf_changes_decision=0`. The carry's finite out-of-range figure is checked by `tests/manual_plan.py` at this head: `100` and `5.001` kW against a 5.0 kW nameplate give 3.5, the configured fraction, not 5.0. `pump_arbiter._step_kw(nan|inf)` is `nan`/`inf` at base and `None` at head, and `nan_reaches_flow=0` at both ends, because the flow set-point already refused it downstream.
- D7-s2-01 `pump_offline` arm, `dev/audit/rounds/round10/D7/s2/learner_gates.py`: the `pump_offline` row's `freq_map` column reads `INGEST` at base and `frozen` at head (`pump_offline.learners_ingesting` 1 -> 0). `freq_map_defrost_folds=0` and `freq_map_clean_folds=8` at both ends.
- D7-s2-59 carry, `dev/audit/harnesses/r10_weekday_range_twins.py`: `pairs=49 disagreements=0` at both ends. This is a refactor, so the behaviour harness reads flat. The class rule is the `cyclic_range_wrap` P2 registry entry in `tests/entities.py`, owner `dhw_schedule.py::cyclic_span`, with zero dispositions at head (two at base).
- D7-s2-58, finite-float coercers: head's seam rule `tests/finite_boundary.py::_finite_float_coercers`, applied to each tree by `python3 dev/audit/harnesses/r10_finite_float_census.py <rule tree> <tree>` (landed in this round; round 1's figures were taken with a scratch copy of the same driver), returns 13 at base and 1 at head (`const.py::finite_float`). The 13 at base: `away._as_num`, `const.buffer_tank_surface_area`, `coordinator._as_float`, `entry_config._number`, `inputs._finite`, `modbus_prefill._number`, `price_model._raw_value`, `price_tiles.monthly_figure`, `pump_arbiter._finite_or_none`, `quiet_windows._power_entity_kw`, `sensor._dhw_min_ceiling`, `thermal_model._optional_float`, `wood_fuel._optional_float`. Every one is closed in this diff, and the census's disposition table is empty.
- D7-s2-57, hour-clock sites: `grep -rnE '%=? *\(?24 \* 60\)?' custom_components/heatpump_optimizer/*.py` returns 5 at base and 2 at head. The base five are `dhw_draws.py` `_fmt`, `dhw_schedule.py` `format_windows.fmt`, `pump_arbiter.py` `_night_clock`, and `quiet_windows.py` `_gchv_at` and `_fmt`. The head two are the owners `dhw_schedule.format_clock` and `quiet_windows.wall_clock`. The class rule is the `hour_clock` P2 registry entry.
- D7-s2-61 class rule: the `power_state_kw` P2 registry entry, where every `normalize_power_kw(` call is an owner (`inputs.state_power_kw` or `InputReader.read_power_kw`) with zero dispositions. P8 state-float census (#1513): 2 sites at base (`coordinator._on_power_event` and `_pv_measured_production`) and 0 at head. This was measured by the census's own `_p8_float_sites`, applied to each tree's package.
- `c2dc1e39b`: that P8 check required at least one production site, so it refused this closed tree (`[0 site(s); ]` in the head's first `tests/entities.py` run). Its precondition is now the rule's reach: a planted probe of three reads (a local, a direct read, and `finite_float` on a state outside `inputs.py`) must return three sites. `finite_float` joined `float` and `_as_float` as a call it follows, so the new owner is no bypass.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at `9c9d12c82`. `tests/structure_budgets.json` moves only down: round 1 (`67e3092b0`) has class_excess_loc 18103 -> 18092, max_class_loc 8343 -> 8330 and functions_cc_over_15 30 -> 29. Round 2 (`984a35dbb`, reason in the commit) has class_excess_loc 18091 -> 18090, max_class_loc 8298 -> 8297 and duplication_copies 16 -> 15. No raise.
- `python3 tools/audit/archscore/score.py --diff da12aa37dee15b9e9567bd6c848493436f2592dd HEAD` (taken at `abc9dfa7e`; the later commits touch only `tests/`): `Architecture score: dS +1.8325 IMPROVES`. duplication_copies 38 -> 35, coord_footprint 2446 -> 2437, params_over_10 7 -> 6, layer_violations 17 -> 13, private_cross_module 12 -> 10. The round-2 delta alone (`--diff 6feac7ece HEAD`) is `dS +0.5449`, with coord_footprint 2436 -> 2437. That is one more coordinator statement: `_plan_slots` now holds the two heating masks in place of the threshold compares. See `## Architecture score`.
- `python3 tests/arch_score_head.py`: ALL 18 PASSED at `9c9d12c82`. At `e43fcdcd6` the stale-row check failed because `wood_fuel.build_wood_fuel_view` went under the parameter line (params_over_10 7 -> 6); `9c9d12c82` drops its disposition row.
- `tests/coverage_budgets.json`: the pragma cap goes 12 -> 10 (`9ad5f78a9`). The two `# pragma: no cover` unit lookups went to `inputs.state_unit`.
- Scoped gate: `python3 tests/closure.py select --diff da12aa37dee15b9e9567bd6c848493436f2592dd` prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` These ran with `PYTHONPATH=tests/hastub` (2026-10-25, macOS arm64). In a `git archive e43fcdcd6` copy, `tests/features.py` reported `1 of 4409 FEATURE CHECKS FAILED`, and the one failure is the archive's #363 `recorded_at` check (`fixer.md` step 2). In the worktree at `e43fcdcd6`/`9c9d12c82`, each of these printed its ALL-PASSED line with rc=0: `guard_pins.py` (50), `finite_boundary.py` (108), `manual_plan.py` (132), `typing_ruler.py` (12), `edge.py`, `validate.py`, `doc_claims.py` (203), `debug_collect.py` (122), `config_flow_steps.py` (499), `deployment_shape.py`, `solar_alignment.py`, `open_meteo.py`, `frontend.py`, `wood_advisor.py` (7), `plan_view.py`, `arch_score_head.py` (18), `harness_headers.py` (112, with `PYTHONPATH=tests/hastub:custom_components:tests`), `node tests/card_drift.mjs` and `tests/env_drift.py --claims-only`. `GOLDEN_MODE=drift tests/golden.py` at `06eccb1a5` reported "NO UNCLAIMED DRIFT: 56 scenario(s)" and "NO STALE FIXTURE". For `tests/entities.py`, see Null control. Left to CI: `card.mjs`, `stress.py`, `backtest.py`, `optimality.py`, `block_duty.py` and `boost_drift_replay.py`.
- Golden drift claimed (`tests/golden/claimed_drift.txt`, `06eccb1a5`): `dhw_cold_tank` step 26 and `horizon_48h` step 153, 2 leaves each. `space_reasons` goes `cheap_price -> idle_coasting` and `dhw_reasons` goes `idle_other_channel -> idle_coasting`. On those steps the space share is above 0.05 kW, but the plan runs no pump, so the classifier fix rightly reads them as idle. Before the claim, `GOLDEN_MODE=drift tests/golden.py` printed exactly these two scenarios as `2 UNCLAIMED DRIFT(S)`. That was the run before the claim was written, and it is this claim's null control.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: "no closures, fast, wave-script or instrument red predicted against da12aa37dee1"; 71 unpinned sites, listed below.

### D8-s1-01, the class (round 2)

- Finder harness `dev/audit/rounds/round10/D8/s1/f1_active_now.py` (sha1 `766cc95a3b886f3f70d122a167028d2313d78048`), run with `PYTHONPATH=tests/hastub:custom_components` on this machine (macOS arm64). At the merge base `da12aa37d`: `heating_now_while_off=1`, `slot_steps_declared_off=0`, `snapshots=36`. At `6feac7ece`: 0 and 0. At this head: 0 and 0. With `--perturb`: 0 and 0 at `da12aa37d` and at this head. **Round 1's "`slot_steps_declared_off` 0 at both" was this machine's reading; I restate it with the machine named.** The harness header says the count is exact per machine/BLAS. The reviewer reads 5 at every end on Linux and the finder 4. On arm64 the solve emits no step that the slot arm catches, so on this machine that arm reads flat at both ends. It measures nothing here, and per `fixer.md` step 3 I add a companion.
- Companion `dev/audit/harnesses/r10_channel_running_rule.py` (landed here), run with `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_channel_running_rule.py [--perturb]` from each tree. It drives the production readers with one 10-step plan whose steps straddle both lines (7 steps the plan calls off), so it does not depend on what the solve happens to emit. The three ends:
  - `da12aa37d`: `slot_steps_declared_off=5`, `reason_steps_declared_off=5`, `sensor_periods_declared_off=2` (`'2 heating periods'`);
  - `6feac7ece`: 5, 5 and 2;
  - this head: 0, 0 and 0 (`sensor_state=None`).
  `--perturb` lifts every off step to 0.2 kW and reads 0, 0 and 0 at `da12aa37d` and at this head. The counts are of declared-off steps, not of the readers' existence. The slot arm is the reviewer's secondary metric, re-derived without the BLAS dependence.
- Class enumeration: the rule is `tests/entities.py::_p2_match_channel_line`, the `channel_active_kw` P2 registry entry. `python3 dev/audit/harnesses/r10_channel_line_reach.py <rule tree> <tree>` lists every site it returns in a tree. With this head's rule it returns 16 sites at `da12aa37d`, 15 at `6feac7ece` and 10 at this head. Each site and its disposition:
  - `coordinator.py::_build_plan_views` `raw_space[0] > 0.05` and `raw_dhw[0] > 0.05` (2 sites at `da12aa37d`): closed in round 1 (`channel_heating_steps`).
  - `coordinator.py::_plan_slots` (`threshold` default 0.05, then `CHANNEL_ACTIVE_KW`): closed in this round. The parameter is gone and the merge reads `channel_heating_steps`.
  - `sensor.py::DHWScheduleSensor.native_value` (2 compares, literal then `CHANNEL_ACTIVE_KW`): closed in this round. The fallback is deleted.
  - `pump_schedule.py` `_PLAN_ACTIVE_KW = 0.05` (read by `plan_commands_heat`): closed in this round. It was not named by the finder; the widened rule found it.
  - `wood_fuel.py` `PUMP_HOUR_KW = 0.05` (read by `cheaper_hour_count` / `wood_cheaper`): closed in this round. It was not named by the finder; the widened rule found it.
  - `optimizer.py::channel_heating_steps`: the owner.
  - `optimizer.py::classify_space_steps` and `classify_dhw_steps` (the `threshold` default): closed in this round, and dispositioned in the registry as the owner module's idle line. Both now compare against `channel_heating_draw`, which is 0 on every step the plan does not run (the companion's `reason_steps_declared_off` 5 -> 0).
  - `accuracy.py::delivered_ratio` (2), `coordinator.py::_async_learn_buffer_cooling`, `coordinator.py::_observe_frequency` and `freq_control.py::FrequencyMap.observe` / `recommend` / `evidence_exhausted`: unchanged dispositions from round 1. These are a ratio's noise floor, distinct findings (#2238 P2 sweep instances), and the frequency map's own floor on a metered draw.
- Rule reach versus round 1's literal-only rule: run against `6feac7ece`, that rule returned none of the renamed sites (the reviewer's `ev/p2_rule_reach.txt`). This head's rule returns 7 sites there that the literal-only rule missed: `_plan_slots`, two sensor compares, the two classifier defaults, `_PLAN_ACTIVE_KW` and `PUMP_HOUR_KW`. These are the 15 at `6feac7ece` less the 7 round-1 dispositions and the owner. A plant of each spelling into `topology.py` must fail the rule ("and D8-s1-01's rule fails on each spelling of the channel line: the literal, a second module constant, and a default naming either"). The four spellings are a literal compare, a module alias, a `CHANNEL_ACTIVE_KW` default and a literal default. `_P2_PLANTS["channel_active_kw"]` is now the renamed spelling `dhw_power > CHANNEL_ACTIVE_KW`.

## Architecture score

Architecture score: dS +1.8325 IMPROVES against the merge base `da12aa37d` (duplication_copies, coord_footprint, params_over_10, layer_violations and private_cross_module fall; no gate metric rises).

- `coord_footprint` against the merge base `da12aa37d`, which is what this PR is judged on: 2446 -> 2437, with dS +1.8325. On the round-2 delta alone (`--diff 6feac7ece HEAD`) it is 2436 -> 2437, because `_plan_slots` holds two heating masks from `channel_heating_steps` where it held one threshold parameter. The orchestrator ruled under mandate 6329234399 (ruling 2, 2026-10-25) that this +1 is not a payment owed inside this PR, since the PR is judged against its merge base, where the metric falls. Folding both masks into one tuple assignment was rejected: it would buy the statement and improve nothing. Moving `_plan_slots` out of the coordinator is the sound payment. It is filed as proposal V62, for an existing group.

## Red checks

- `tests/entities.py` "every mark still names a mutant this tree generates, pin and all (#1217)" was red locally at `984a35dbb`, before any push. Three pins sat on lines this round rewrites (`pump_schedule.plan_commands_heat RETURN_DEL 85430f16`, and `DHWScheduleSensor.native_value` `BOOLOP` / `GUARD_OFF f17fef3f`). `tools/pr/ci_predict.py` had named all three as STALE PIN before any push. It is the cheaper detector, it already exists and it costs seconds. `0a087ad4e` deletes the three, and `mutation-autofix` re-pins the edited lines. No new detector is owed.
- `tests/arch_score_head.py` "every dispositioned row is still over the line" was red locally at `e43fcdcd6`, before any push. This is an improvement the stale-row check exists to catch. The cheaper detector is that check itself, run at the head before the handoff (`fixer.md` step 5). Repaired in `9c9d12c82`, and no new detector is owed.
- `mutation` (`tests / mutation`) is predicted red. `tools/pr/ci_predict.py` lists the 71 unpinned sites this diff adds (`## Unpinned sites`), all `custom_components/` sites, which `mutation-autofix` pins on the PR (`ci-autofix.md`). The cheaper detector already exists and ran here: `ci_predict.py`, at a standing cost of seconds per handoff. No new detector is owed.
- Round 1's `tests/entities.py` P8 precondition red (`9ad5f78a9`, repaired in `c2dc1e39b`) stands as written then.

## Forward-carry

none

## Friction

none

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head lists 71 sites the diff adds. All are under `custom_components/`, so each is mutation-autofix's to pin (`ci-autofix.md`). The fixer's own kills of the fix predicates are under Mutation proof.

- `custom_components/heatpump_optimizer/const.py:1313 GUARD_OFF: if isinstance(value, bool) or not isinstance(value, (Real, s`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/const.py:1319 RETURN_DEL: return result if math.isfinite(result) else default`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/const.py:1330 GUARD_OFF: if volume is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/const.py:1332 CLAMP_DROP: volume_m3 = max(volume, 1e-6) / 1000.0`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:415 BOOLOP: return value if value is not None and value >= lo else defau`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:415 CMP_BOUND: return value if value is not None and value >= lo else defau`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:415 RETURN_DEL: return value if value is not None and value >= lo else defau`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:713 RETURN_DEL: return None if temperature is None else finite_float(tempera`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:1049 GUARD_OFF: if coord._pump_signals.freeze_reason is not None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:3973 CMP_BOUND: abs(finite_float(action.get("displace_value"), 0.0)) > 0.01`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4339 BOOLOP: other_powers[i] for i in span if i < len(other_heating) and `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4339 CMP_BOUND: other_powers[i] for i in span if i < len(other_heating) and `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4357 GUARD_OFF: if on:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4525 BOOLOP: raw_space and channel_heating_steps(raw_space[:1], raw_dhw[:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4544 BOOLOP: raw_dhw and channel_heating_steps(raw_dhw[:1], raw_space[:1]`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:5082 CLAMP_DROP: max(0.0, finite_float(first.get("wind_speed"), 0.0)),`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:5083 CLAMP_DROP: max(0.0, finite_float(first.get("precipitation"), 0.0)),`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:7049 CLAMP_DROP: gust = max(0.0, finite_float(entry.get("wind_speed"), 0.0))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:7050 CLAMP_DROP: rain = max(0.0, finite_float(entry.get("precipitation"), 0.0`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:8498 GUARD_OFF: if kw is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:9561 RETURN_DEL: return state_power_kw(self.hass.states.get(entity_id), sign=`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:10359 CLAMP_DROP: book["kwh"] = finite_float(book.get("kwh"), 0.0) + max(0.0, `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/dhw_schedule.py:94 RETURN_DEL: return [first + (start - first + k) % size for k in range((e`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/dhw_schedule.py:125 RETURN_DEL: return sorted(cyclic_span(lo, hi, len(_DAY_TOKENS)))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 BOOLOP: if run is not None and len(ordered) >= 3:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 CMP_BOUND: if run is not None and len(ordered) >= 3:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 GUARD_OFF: if run is not None and len(ordered) >= 3:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/dhw_schedule.py:465 RETURN_DEL: return ", ".join(f"{format_clock(s)}-{format_clock(e)}" for `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/entry_config.py:33 RETURN_DEL: return finite_float(value)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/freq_control.py:121 RETURN_DEL: return (finite_float(reading.state), hz_min, hz_max, source)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/grid_fee.py:132 RETURN_DEL: return frozenset(cyclic_span(start, end, size, first))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:391 GUARD_OFF: if state is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:394 GUARD_OFF: if value is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:397 GUARD_OFF: if kw is None or not math.isfinite(kw):`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:399 GUARD_OFF: if sign == "clamp":`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:400 CLAMP_DROP: return max(0.0, kw)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:401 GUARD_OFF: if sign == "positive":`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:402 CMP_BOUND: return kw if kw > 0.0 else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/inputs.py:403 RETURN_DEL: return kw`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/modbus_prefill.py:182 RETURN_DEL: return None if row is None else finite_float(row[1])`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1339 CONST: CHANNEL_ACTIVE_KW = 0.05`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1354 GUARD_OFF: if other_kw is not None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1358 BOOLOP: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1358 CMP_BOUND: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1358 RETURN_DEL: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1369 RETURN_DEL: return np.where(channel_heating_steps(channel, other_kw), ch`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1376 GUARD_OFF: if other is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1378 RETURN_DEL: return channel_heating_draw(power, other), channel_heating_d`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/price_model.py:760 RETURN_DEL: return finite_float(raw)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/price_tiles.py:115 RETURN_DEL: return finite_float(answer.get(key))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/pump_arbiter.py:465 RETURN_DEL: return finite_float(_planned_room(result, now, "power_schedu`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/pump_schedule.py:100 GUARD_OFF: if not space_heating:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/pump_schedule.py:105 RETURN_DEL: return bool(space_heating[idx]), bool(space_heating[nxt])`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:286 RETURN_DEL: return minutes // 60, minutes % 60`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:291 RETURN_DEL: return datetime.combine(day, time(*wall_clock(hour)), tzinfo`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:330 RETURN_DEL: return state_power_kw(get_state(power_id), sign="positive")`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:343 BOOLOP: return kw if kw is not None and 0.0 < kw <= p_max else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:343 CMP_BOUND*2: return kw if kw is not None and 0.0 < kw <= p_max else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:343 RETURN_DEL: return kw if kw is not None and 0.0 < kw <= p_max else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:401 CLAMP_DROP: return max(measured, CAPACITY_FLOOR_FRACTION * float(p_max))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:654 RETURN_DEL: return f"{clock_h:02d}:{clock_m:02d}"`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/sensor.py:1203 BOOLOP: if not (isinstance(plan, dict) and isinstance(plan.get("slot`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/sensor.py:1203 GUARD_OFF: if not (isinstance(plan, dict) and isinstance(plan.get("slot`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/sensor.py:1381 RETURN_DEL: return None if value is None else round(value - DHW_MIN_TEMP`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:131 GUARD_OFF: if not on:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:136 CMP_BOUND: if wood_sek < finite_float(price, 0.0) / cop_f:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:136 GUARD_OFF: if wood_sek < finite_float(price, 0.0) / cop_f:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:157 CMP_BOUND: cop = finite_float(cops[i] if i < len(cops) else 0.0, 0.0)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:215 CMP_BOUND: return cheaper_hour_count(wood_sek, prices, cops, runs) > 0`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:365 CMP_BOUND: if finite_float(forecast_kw[i], 0.0) > 0.0:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:365 GUARD_OFF: if finite_float(forecast_kw[i], 0.0) > 0.0:`: pinned by mutation-autofix (custom_components/ site).
