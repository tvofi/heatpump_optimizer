R10-ARCH-SHAPES (round 10, D7/D8, wave 22). The bug comes first. D7-s2-61: a heat-pump power entity reading `inf`, `1e400` or a finite absurd figure (100 kW) made the quiet-window ceiling the nameplate itself, so there was no silent cap. `silent_cap_kw` clipped any reading past `p_max` down to `p_max`, and the frequency and fraction fallbacks never ran. Then come the duplicated-shape owners from ARCH-s2: hour-clock (D7-s2-57), finite-float (D7-s2-58), the weekday cyclic range (D7-s2-59, carried from R10-TARIFF) and the plan's channel line (D8-s1-01, carried from R10-SENSOR-PAYLOAD). Last is the `pump_offline` arm of D7-s2-01, carried from R10-FREQ-DEFROST.

Closes #2236.

Closes #2239.

Part of #2238 (its D8-s1-01 and D7-s2-01 `pump_offline` arms close here; the remaining P2 sweep instances named under the `channel_active_kw` dispositions stay with #2238).

What changes, one owner per concern:

- **Power state as kW** (D7-s2-61): `inputs.state_power_kw(state, sign=...)` is now the one live-state parse. The state must be finite and its unit known, and the converted figure must be finite too: `1e306 MW` overflows on conversion. The caller states its sign policy: `signed` for the peak listener, `clamp` for PV production, `positive` for the quiet-window ceiling. It replaces three hand parses: `quiet_windows._power_entity_kw`, `coordinator._on_power_event` and `_pv_measured_production`. **The range bound is the caller's.** `quiet_windows._within_nameplate` admits only `(0, p_max]`, and it bounds both the power reading and the frequency-scaled figure, so an absurd reading falls through to the next source. `silent_cap_kw` no longer clips at `p_max`.
- **Finite-float coercion** (D7-s2-58, #2239): `const.finite_float(value, default=None)` lives in the package's dependency-free module, so no model or learner module climbs to the glue layer for it. It replaces `coordinator._as_float` and every other coercer the census rule returns at the base (list under Figures). **Behaviour change, stated as the carry asks:** a `bool` is not a number (`True` used to read as 1.0 in `pump_arbiter._finite_or_none`, `float()` and others), and neither are bytes. Numeric text is read. NaN, the infinities and an int past a double are all unreadable. `pump_arbiter._step_kw` now refuses NaN and inf, where `_finite_or_none` passed them (`isinstance(value, (int, float))`). It also refuses `True`, and it reads numeric text.
- **Hour clock** (D7-s2-57): `quiet_windows.wall_clock`, where a clock folds 24:00 to 00:00, and `dhw_schedule.format_clock`, where a window label keeps 24:00. The two owners name the one real difference. `pump_arbiter._night_clock`, the GCHV `_gchv_at`/`_fmt` copies and the `format_windows`/`dhw_draws` copies now call them.
- **Cyclic range** (D7-s2-59 carry): `dhw_schedule.cyclic_span` owns the wrap. `grid_fee._parse_cyclic_range`, `_parse_day_selector` and `_format_day_selector` read it, and the two `cyclic_range_wrap` dispositions are removed from `tests/entities.py`.
- **Channel line** (D8-s1-01 carry): `optimizer.CHANNEL_ACTIVE_KW` and `channel_heating_steps` (a channel's own draw above the line, on a step `planned_draws_run` runs). The plan view's `active_now`, the `_plan_slots` threshold and the DHW schedule sensor's fallback all read them, so the threshold and the fallback moved together as the carry asked.
- **Pump freeze** (D7-s2-01 `pump_offline` carry): `_freq_fold_blocked` refuses any `pump_signals` freeze reason (offline, fault, cooling), not cooling alone.

Alternatives considered:

- A finiteness check alone (the verifier's patch 03) was rejected: the carry measured that 100 kW still gave 6.0 after it.
- A new `finite.py` (2c0bc14d7) was folded into `const.py` (0ef69bfcf): `const.py` is already the dependency-free module every layer imports, and a new module was one more import edge for nothing.
- The range bound was put in the caller, not in `state_power_kw`, because only the caller owns the envelope. A PV meter or grid meter has no nameplate.

The architect note's seam: every `coordinator.py` hunk is a float-coercion call site moving to the owner, plus the three power parses, `_freq_fold_blocked` and the two `active_now`/threshold lines the carries assigned here. `git merge-tree --write-tree` against R10-PARAMS-OWNER's local head `c8a234897` reports no conflict.

## Head

`c2dc1e39b7af5de0aadda4652957d7f6a146e60b`, on base `de794b53765388da42b2b5f22da455ccfe3fe912` (the merge base; origin/main `b89fea13e99f23cc75f01bb1604030cabea4ca66`, committed 2026-10-25T10:04:53Z, differs from it only in `dev/programme/rosters/wave-r10-groups.json` and `dev/programme/delivery/2797.md`, and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the branch was not merged). The fixer seat was resumed after a crash. `c2dc1e39b` (the P8 census repair, below) is the resumed seat's commit. Every figure in this body was taken by the resumed seat from 2026-10-25T12:45Z, at `9ad5f78a9` or at `c2dc1e39b7af5de0aadda4652957d7f6a146e60b`. The two differ only in `tests/entities.py`, and every figure that reads `tests/entities.py` was taken at `c2dc1e39b7af5de0aadda4652957d7f6a146e60b`.

The failing test came first: `26be3410d` adds `tests/manual_plan.py`'s two D7-s2-61 checks before any fix. With `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` in a `git archive 26be3410d` copy, `2 of 132 manual plan checks FAILED`: "a non-finite or over-nameplate power reading is no measurement" `[got {'inf': 5.0, '1e400': 5.0, '100': 5.0, '5.001': 5.0}]` and "a frequency past its configured maximum measures nothing" `[got 7.5]`. At this head, `ALL 132 manual plan checks PASSED`.

## Mutation proof

Each mutant is one fix predicate, replaced in a `git archive HEAD` copy by the driver below. It is then run with `PYTHONPATH=tests/hastub python3 tests/<script>.py` against the script that pins it, and the copy is discarded. The worktree is never edited. A `git archive` copy fails `tests/features.py`'s "and the path that proceeds still stamps a resolvable recorded_at (#363)" on every run, baseline included (`fixer.md` step 2). It is the runner's failure, not the mutant's, and it is left out of the lists below.

- `quiet_windows.py` `_within_nameplate`: `return kw if kw is not None and 0.0 < kw <= p_max else None` -> `return kw` (the range bound, D7-s2-61). `tests/manual_plan.py` rc=1: "a non-finite or over-nameplate power reading is no measurement", "a frequency past its configured maximum measures nothing".
- `inputs.py` `state_power_kw`: `if kw is None or not math.isfinite(kw):` -> `if kw is None:` (finiteness after conversion). `tests/features.py` rc=1: "a power state parses to finite kW under the caller's sign policy, or to no reading" (the `1e306 MW` row reads `inf`).
- `const.py` `finite_float`: `if isinstance(value, bool) or not isinstance(value, (Real, str)):` -> `if not isinstance(value, (Real, str)):` (the bool policy). `tests/finite_boundary.py` rc=1, `1 of 108`: "const.finite_float reads a real number or numeric text, and nothing else -- not a bool, bytes, NaN, an infinity or an int past a double".
- `coordinator.py` `_freq_fold_blocked`: `if coord._pump_signals.freeze_reason is not None:` -> `== pump_signals.FREEZE_COOLING` (the D7-s2-01 `pump_offline` arm). `tests/features.py` rc=1: "an offline, faulted or cooling pump's interval never teaches the frequency map".
- `coordinator.py` `_build_plan_views`: `raw_space and channel_heating_steps(raw_space[:1], raw_dhw[:1])[0]` -> `raw_space and raw_space[0] > 0.05` (D8-s1-01). `tests/features.py` rc=1: "a plan channel is heating now only on a step the plan runs (D8-s1-01)".
- `coordinator.py` `_pv_measured_production`: `sign="clamp"` -> `sign="signed"`. `tests/features.py` rc=1: "a negative production reading is clamped to zero, not propagated".
- `dhw_schedule.py` `_parse_day_selector`: `return sorted(cyclic_span(lo, hi, len(_DAY_TOKENS)))` -> the base's inline `(lo + k) % 7` wrap (D7-s2-59). `tests/entities.py` rc=1: "P2 owners: cyclic_range_wrap is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".
- `pump_arbiter.py` `_write_night_schedule`: `quiet_windows.wall_clock(nxt[0])` -> an inline `% (24 * 60)` divmod (D7-s2-57). `tests/entities.py` rc=1: "P2 owners: hour_clock is decided only by its owner or a dispositioned site, ..." and the same null-controls check.

The two `tests/entities.py` mutants are measured against `tests/entities.py` on a `git archive` copy at this head, whose FAIL names are otherwise the copy's own. Those are the git-repository checks (#2119, the handover reachability) and the load-sensitive heartbeat and a3-a13 harness self-tests, all of which also fail in the base archive copy. The two P2 checks named above fail in neither the base copy nor this head's worktree run.

Driver: `/Users/timmalmstrom/hpo-seats/r10s6/arch-shapes-scratch/mutants.py` (scratch, a one-off; each mutant's `old -> new` is printed above).

## Null control

- The unmutated head is the mutants' control: `tests/features.py` `ALL 4378 FEATURE CHECKS PASSED`, `tests/manual_plan.py` `ALL 132 manual plan checks PASSED`, `tests/finite_boundary.py` `ALL 108 FINITE BOUNDARY CHECKS PASSED` (in the worktree at this head).
- `probe_coercion_reach.py`: the `unknown` state (every parser refuses) reads 4.2 at both ends, and the legitimate `3` kW reading reads 3.6 at both ends, so the fix moves only the out-of-range rows. Its `--perturb`-style in-memory refusal arm reads `perturbed_1e400_equals_unknown=1` at both ends.
- `f1_active_now.py --perturb` (the finder's in-memory perturbation) reads `heating_now_while_off=0` at base and head. The harness moves under its own perturbation, and the head reaches the perturbed value without it.
- `r10_weekday_range_twins.py --identity` reads 0 of 49 at both ends, and `--perturb` reads 49 of 49 at both ends.
- Finite-float census: the rule (`tests/finite_boundary.py::_finite_float_coercers`) must return a planted coercer. The census asserts this itself ("the census reaches the owner and a planted sibling").
- P2 registries `hour_clock`, `power_state_kw` and `channel_active_kw` each carry a `_P2_PLANTS` entry that the registry must refuse.
- P8 state-float census: a planted probe of three reads must return three sites (below).
- `tests/entities.py` in detached worktrees: `4 of 2440 ENTITY CHECKS FAILED` at base `de794b537`, `4 of 2443 ENTITY CHECKS FAILED` at this head. The set of FAIL names is identical at the two ends, compared with `diff` over `grep '^  FAIL' | sed 's/  \[.*//' | sort -u` and printing nothing. They are the heartbeat-timing self-tests, which are load-sensitive on this box (load average above 100). This diff adds none.

## Figures

All harnesses were run from a `git archive` export of each end, with `PYTHONPATH=tests/hastub python3 <path>` from the export root.

- D7-s2-61, `dev/audit/rounds/round10/catchup/arch-s2/probe_coercion_reach.py`. Base `de794b537`: `1e6`, `1e400` and `inf` give `silent_cap_kw=6.0` (p_max, no cap), `inf_changes_decision=1`, `inf_equals_finite_absurd=1`. Head: all three give 4.2 (the `unknown` arm), `inf_changes_decision=0`. The carry's finite out-of-range figure is checked by `tests/manual_plan.py` at this head: `100` and `5.001` kW against a 5.0 kW nameplate give 3.5, the configured fraction, not 5.0. `pump_arbiter._step_kw(nan|inf)` is `nan`/`inf` at base and `None` at head, and `nan_reaches_flow=0` at both ends, because the flow set-point already refused it downstream.
- D8-s1-01, `dev/audit/rounds/round10/D8/s1/f1_active_now.py`: `heating_now_while_off` 1 at base, 0 at head; `slot_steps_declared_off` 0 at both; `snapshots=36` at both.
- D7-s2-01 `pump_offline` arm, `dev/audit/rounds/round10/D7/s2/learner_gates.py`: the `pump_offline` row's `freq_map` column reads `INGEST` at base and `frozen` at head (`pump_offline.learners_ingesting` 1 -> 0). `freq_map_defrost_folds=0` and `freq_map_clean_folds=8` at both ends.
- D7-s2-59 carry, `dev/audit/harnesses/r10_weekday_range_twins.py`: `pairs=49 disagreements=0` at both ends. This is a refactor, so the behaviour harness reads flat. The class rule is the `cyclic_range_wrap` P2 registry entry in `tests/entities.py`, owner `dhw_schedule.py::cyclic_span`, with zero dispositions at head (two at base).
- D7-s2-58, finite-float coercers: head's seam rule `tests/finite_boundary.py::_finite_float_coercers`, applied to each tree by `/Users/timmalmstrom/hpo-seats/r10s6/arch-shapes-scratch/ff_census.py <head> <tree>`, returns 13 at base and 1 at head (`const.py::finite_float`). The 13 at base: `away._as_num`, `const.buffer_tank_surface_area`, `coordinator._as_float`, `entry_config._number`, `inputs._finite`, `modbus_prefill._number`, `price_model._raw_value`, `price_tiles.monthly_figure`, `pump_arbiter._finite_or_none`, `quiet_windows._power_entity_kw`, `sensor._dhw_min_ceiling`, `thermal_model._optional_float`, `wood_fuel._optional_float`. Every one is closed in this diff, and the census's disposition table is empty.
- D7-s2-57, hour-clock sites: `grep -rnE '%=? *\(?24 \* 60\)?' custom_components/heatpump_optimizer/*.py` returns 5 at base and 2 at head. The base five are `dhw_draws.py` `_fmt`, `dhw_schedule.py` `format_windows.fmt`, `pump_arbiter.py` `_night_clock`, and `quiet_windows.py` `_gchv_at` and `_fmt`. The head two are the owners `dhw_schedule.format_clock` and `quiet_windows.wall_clock`. The class rule is the `hour_clock` P2 registry entry.
- D7-s2-61 class rule: the `power_state_kw` P2 registry entry, where every `normalize_power_kw(` call is an owner (`inputs.state_power_kw` or `InputReader.read_power_kw`) with zero dispositions. P8 state-float census (#1513): 2 sites at base (`coordinator._on_power_event` and `_pv_measured_production`) and 0 at head. This was measured by the census's own `_p8_float_sites`, applied to each tree's package.
- `c2dc1e39b`: that P8 check required at least one production site, so it refused this closed tree (`[0 site(s); ]` in the head's first `tests/entities.py` run). Its precondition is now the rule's reach: a planted probe of three reads (a local, a direct read, and `finite_float` on a state outside `inputs.py`) must return three sites. `finite_float` joined `float` and `_as_float` as a call it follows, so the new owner is no bypass.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at this head. Against the base, `tests/structure_budgets.json` moves only down (`67e3092b0`: class_excess_loc 18103 -> 18092, max_class_loc 8343 -> 8330, functions_cc_over_15 30 -> 29); no raise.
- `python3 tools/audit/archscore/score.py --diff de794b53765388da42b2b5f22da455ccfe3fe912 HEAD`: `Architecture score: dS +1.2702 IMPROVES` (duplication_copies 39 -> 37, coord_footprint 2446 -> 2436, layer_violations 17 -> 13, private_cross_module 12 -> 10).
- `tests/coverage_budgets.json`: the pragma cap goes 12 -> 10 (`9ad5f78a9`). The two `# pragma: no cover` unit lookups went to `inputs.state_unit`.
- Scoped gate: `python3 tests/closure.py select --diff de794b53765388da42b2b5f22da455ccfe3fe912` prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` Run locally at this head with `PYTHONPATH=tests/hastub`: `tests/features.py` ALL 4378 FEATURE CHECKS PASSED, `tests/manual_plan.py` ALL 132, `tests/finite_boundary.py` ALL 108, `tests/guard_pins.py` ALL 50, `tests/plan_view.py` OK, and `tests/entities.py` as under Null control. With rc=0, as is every other script `scope.run` names that ran locally: `harness_headers.py`, `typing_ruler.py`, `validate.py`, `edge.py`, `deployment_shape.py`, `doc_claims.py`, `debug_collect.py`, `config_flow_steps.py`, `wood_advisor.py`, `solar_alignment.py`, `open_meteo.py`, `frontend.py`, `arch_score_head.py`, `card_drift.mjs`, `GOLDEN_MODE=drift GOLDEN_REF=de794b537 tests/golden.py` ("NO UNCLAIMED DRIFT: 56 scenario(s)") and `env_drift.py --claims-only`. `tests/card.mjs` ran out of node heap at its 2 GB default under this load and passed (`ALL CARD CHECKS PASSED`) with `NODE_OPTIONS=--max-old-space-size=6144`. The heavy scripts (`stress.py`, `backtest.py`, `optimality.py`, `block_duty.py`, `boost_drift_replay.py`) are left to CI, because the shared box sat at load 100-180 through this session.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: "no closures, fast, wave-script or instrument red predicted against de794b537653"; 63 unpinned sites, listed below.

## Architecture score

Architecture score: dS +1.2702 IMPROVES (duplication_copies, coord_footprint, layer_violations and private_cross_module fall; no gate metric rises).

## Red checks

- `tests/entities.py` "every float() of an entity's state outside inputs.py is normalised or dispositioned (#1513)" was red locally at `9ad5f78a9`, before any push to a PR. Its precondition required a production site, and this diff removes the last one. The detector that would have caught it cheaply is `tests/entities.py` run at the head before the handoff, which `fixer.md` step 5 already requires. The predecessor seat crashed before running it. No new detector is owed. Repaired in `c2dc1e39b`.
- `mutation` (`tests / mutation`) is predicted red: `tools/pr/ci_predict.py` lists the 63 unpinned sites this diff adds (`## Unpinned sites`). All of them are `custom_components/` sites, which `mutation-autofix` pins on the PR (`ci-autofix.md`), so the fixer does not duplicate that work. The cheaper detector already exists and ran here: `ci_predict.py`, at a standing cost of seconds per handoff. It predicted this red before any push, and no new detector is owed. No PR exists yet, so there is no other CI red to name.

## Forward-carry

none

## Friction

none

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head lists 63 sites the diff adds. All are under `custom_components/`, so each is mutation-autofix's to pin (`ci-autofix.md`). The fixer's own kills of the fix predicates are under Mutation proof.

- `custom_components/heatpump_optimizer/const.py:1313 GUARD_OFF: if isinstance(value, bool) or not isinstance(value, (Real, s`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/const.py:1319 RETURN_DEL: return result if math.isfinite(result) else default`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/const.py:1330 GUARD_OFF: if volume is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/const.py:1332 CLAMP_DROP: volume_m3 = max(volume, 1e-6) / 1000.0`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:414 BOOLOP: return value if value is not None and value >= lo else defau`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:414 CMP_BOUND: return value if value is not None and value >= lo else defau`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:414 RETURN_DEL: return value if value is not None and value >= lo else defau`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:712 RETURN_DEL: return None if temperature is None else finite_float(tempera`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:1023 GUARD_OFF: if coord._pump_signals.freeze_reason is not None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:3876 CMP_BOUND: abs(finite_float(action.get("displace_value"), 0.0)) > 0.01`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4431 BOOLOP: raw_space and channel_heating_steps(raw_space[:1], raw_dhw[:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4450 BOOLOP: raw_dhw and channel_heating_steps(raw_dhw[:1], raw_space[:1]`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4998 CLAMP_DROP: max(0.0, finite_float(first.get("wind_speed"), 0.0)),`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:4999 CLAMP_DROP: max(0.0, finite_float(first.get("precipitation"), 0.0)),`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:6987 CLAMP_DROP: gust = max(0.0, finite_float(entry.get("wind_speed"), 0.0))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:6988 CLAMP_DROP: rain = max(0.0, finite_float(entry.get("precipitation"), 0.0`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:8434 GUARD_OFF: if kw is None:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:9499 RETURN_DEL: return state_power_kw(self.hass.states.get(entity_id), sign=`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/coordinator.py:10297 CLAMP_DROP: book["kwh"] = finite_float(book.get("kwh"), 0.0) + max(0.0, `: pinned by mutation-autofix (custom_components/ site).
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
- `custom_components/heatpump_optimizer/optimizer.py:1352 BOOLOP: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1352 CMP_BOUND: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/optimizer.py:1352 RETURN_DEL: return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zi`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/price_model.py:760 RETURN_DEL: return finite_float(raw)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/price_tiles.py:115 RETURN_DEL: return finite_float(answer.get(key))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/pump_arbiter.py:465 RETURN_DEL: return finite_float(_planned_room(result, now, "power_schedu`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:286 RETURN_DEL: return minutes // 60, minutes % 60`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:291 RETURN_DEL: return datetime.combine(day, time(*wall_clock(hour)), tzinfo`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:330 RETURN_DEL: return state_power_kw(get_state(power_id), sign="positive")`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:343 BOOLOP: return kw if kw is not None and 0.0 < kw <= p_max else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:343 CMP_BOUND*2: return kw if kw is not None and 0.0 < kw <= p_max else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:343 RETURN_DEL: return kw if kw is not None and 0.0 < kw <= p_max else None`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:401 CLAMP_DROP: return max(measured, CAPACITY_FLOOR_FRACTION * float(p_max))`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/quiet_windows.py:654 RETURN_DEL: return f"{clock_h:02d}:{clock_m:02d}"`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/sensor.py:1211 CMP_BOUND: if s.get("dhw_power", 0) > CHANNEL_ACTIVE_KW`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/sensor.py:1214 CMP_BOUND: or schedule[i - 1].get("dhw_power", 0) <= CHANNEL_ACTIVE_KW`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/sensor.py:1392 RETURN_DEL: return None if value is None else round(value - DHW_MIN_TEMP`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:129 CLAMP_DROP: if max(finite_float(space, 0.0), finite_float(dhw, 0.0)) <= `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:129 CMP_BOUND: if max(finite_float(space, 0.0), finite_float(dhw, 0.0)) <= `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:129 GUARD_OFF: if max(finite_float(space, 0.0), finite_float(dhw, 0.0)) <= `: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:134 CMP_BOUND: if wood_sek < finite_float(price, 0.0) / cop_f:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:134 GUARD_OFF: if wood_sek < finite_float(price, 0.0) / cop_f:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:155 CMP_BOUND: cop = finite_float(cops[i] if i < len(cops) else 0.0, 0.0)`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:367 CMP_BOUND: if finite_float(forecast_kw[i], 0.0) > 0.0:`: pinned by mutation-autofix (custom_components/ site).
- `custom_components/heatpump_optimizer/wood_fuel.py:367 GUARD_OFF: if finite_float(forecast_kw[i], 0.0) > 0.0:`: pinned by mutation-autofix (custom_components/ site).
