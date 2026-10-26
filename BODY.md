R10-ARCH-SHAPES: one owner per duplicated shape, power readings bounded

R10-ARCH-SHAPES (round 10, D7/D8, wave 22), red-gate fixer pass after fix-review round 4. This pass merged origin/main into the PR head, cured the `tests / mutation` red, and re-took this body (three-round rule). Every figure below was taken in this pass at code head `864a96c02a6c58eed4a84d35d234fc9cd12d372b`. origin/main and the merge base were both `510787b769407ed25054177cfb0f6bd17e041e0e`, read at `Mon Oct 26 10:17:12 UTC 2026`. All runs were on Linux x86_64.

Closes #2236.

Closes #2239.

Part of #2238. Its D8-s1-01 plan-view, pump, sensor and wood-advisor arms and its D7-s2-01 `pump_offline` arm close here. The D8-s1-01 reason-classifier arm is split out (below). The remaining P2 sweep instances named under the `channel_active_kw` dispositions stay with #2238.

**The split (round 4, the orchestrator's ruling under mandate 6329234399).** The reason-classifier arm of D8-s1-01 moves golden `space_reasons`/`dhw_reasons`, and the set of scenarios it moves depends on the host, so no fixed claim set holds on every runner. This PR drops that arm: the `_heating_draws` lines in `optimizer.classify_space_steps` / `classify_dhw_steps`, their helpers `channel_heating_draw` and `_heating_draws`, the feature check "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)", and the two classifier dispositions in `tests/entities.py`, which name the parked group. The arm is parked as one commit at `park/r10-arch-shapes-classifier` (`996b54cf15ea3c7693383165ae2f080d2e04971b`), group R10-ARCH-SHAPES-CLASSIFIER, after R10-996-RUNNER-CLAIMS (Forward-carry). Both claim files are byte-identical to the merge base: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/` prints nothing.

What remains, one owner per concern:

- **Power state as kW** (D7-s2-61): `inputs.state_power_kw(state, sign=...)` is the one live-state parse outside `InputReader`. The reading must be finite and in a known unit, and still finite after conversion. Each caller states its sign policy (`signed`, `clamp` or `positive`). The range bound belongs to the caller: `quiet_windows._within_nameplate` admits only `(0, p_max]`, so an absurd finite reading (the 100 kW case of carry 1) falls through to the next source, and `silent_cap_kw` no longer clips it at `p_max`. `state_power_kw` reads no `last_updated` or `last_reported` and computes no age (carry 8): it parses a state object a caller already holds, and the P2 `state_age` registry passes at this head (Figures).
- **Finite-float coercion** (D7-s2-58, #2239): `const.finite_float(value, default=None)`, in the package's dependency-free module, replaces the coercers the census rule returns at the base. **Behaviour change** (carry 2): a `bool` is not a number, and neither are bytes; numeric text is read; NaN, the infinities and an int past a double are unreadable; so `pump_arbiter._step_kw` now refuses NaN, inf and `True` (`True` is not a number). `AccuracySample.from_dict.num` reads it too.
- **Hour clock** (D7-s2-57): `quiet_windows.wall_clock` folds 24:00 to 00:00, and `dhw_schedule.format_clock` keeps 24:00 in a window label. Every copy calls one of the two.
- **Cyclic range** (D7-s2-59, carry 4): `dhw_schedule.cyclic_span` owns the wrap. `grid_fee`'s range parsers and `dhw_schedule._parse_day_selector` read it, and `_format_day_selector` shares it for its run search; the `cyclic_range_wrap` P2 entry holds no `dhw_schedule` disposition.
- **Channel line** (D8-s1-01, carry 5, minus the parked arm): `optimizer.CHANNEL_ACTIVE_KW` is the one 0.05 kW line, and `optimizer.channel_heating_steps` the one reader of "does this channel heat at this step": its own draw above the line, on a step `planned_draws_run` runs. The plan view's `active_now`, `_plan_slots` (no `threshold` parameter any more), the space circulation pump (`pump_schedule.plan_commands_heat` takes the plan's space-heating flags), the wood advisor (`heat_pump_on_schedule`), the system-identification experiment's `heat_pump_on` (`planned_draw_runs`) and the DHW schedule sensor (its raw-draw fallback deleted, so it moves with `_plan_slots`) read it.
- **Pump freeze** (D7-s2-01 `pump_offline`, carry 6): `_freq_fold_blocked` refuses every `pump_signals` freeze reason, read as `freeze_reason is not None`, not as a copied flag.

This pass adds, on top of the reviewed code:
- `tests/guard_pins.py` `_r10_arch_shapes_pins()`: one check per mutation site the shared coercions re-spelled, each driven on its own bound; its closure in `tests/closures.json` is re-derived (`derive_closures.sh --single tests/guard_pins.py`, Linux) and now reaches `coordinator.py` and `sensor.py`.
- `tests/mutation_ledger/`: 14 `killed_by` rows recorded by `--pin-killed`, and 2 `survivor_triage` rows (Unpinned sites).
- `tests/deployment_shape.py`: the #1218 selection-cost note counts guard_pins.py's 9 new overlap pairs (122 -> 131), which `tests/entities.py` derives and refused until the note said so.

No production line changed in this pass, so the review delta is test-side only. Carry 3's mutation-ledger re-key is the ledger rows above; its quiet-window stress re-take is `tests/stress.py` in the gate run below. Carry 7: the group's approved design note stands; no design step is owed.

Alternatives considered:
- **Keep the classifier arm, claim the runner's latest pair.** A third runner reading would refute it, so it was rejected.
- **Keep the arm, add may-drift entries for the movers.** The census union is not closed (this host's susceptible set differs from the round-4 host's, Figures), so a named set leaks; rejected.
- **Make the classifier robust to the line.** The moved steps are mid-band, so there is nothing for robustness to fix; rejected.
- **For the two surviving mutants, a check driving `_async_drive_pumps` at `displace_value == 0.01`.** It would build a coordinator fixture to pin a boundary the line held unpinned on main before this PR re-keyed it; recorded as a triage gap instead.

## Head

`864a96c02a6c58eed4a84d35d234fc9cd12d372b`. It is the previous PR head `4b513acdd6529b3358e7cd7b29644ee65d415200` with:
- `6e084a3b2`, a merge of origin/main `ed1c9045e` (no rebase, no conflict; the merge drivers were installed);
- `aec11a772`, the guard pins and their 13 `killed_by` rows plus the closure re-derivation;
- `ea33506e0`, the `format_clock` pin, its row and the 2 triage rows;
- `632715d74`, the #1218 note;
- `864a96c02`, a merge of the PR branch's own new head `af7ec86f4` (the bot's `ci: merge main`, bringing origin/main `510787b76`: #2851 and #2832), no conflict; the ledger driver merged `tests/closures.json` and `tests/structure_budgets.json`, and `tests/structure.py` passes on the result.

Every figure in this body was re-taken after that last merge, except the `--pin-killed` record under Mutation proof (run against `ed1c9045e`), whose rows the re-taken mutation ratchet reads at this head.

**Delta review owed** against `4b513acdd`: the two merges of main and the three test-side commits.

## Mutation proof

**The fix predicates, re-run at this head.** A driver applied one replacement in a worktree at `864a96c02`, ran the script that pins it with `PYTHONPATH=tests/hastub`, restored the file, and reported the FAIL names beyond the unmutated head's own run. Each `old -> new`:

- `coordinator.py` `_run_system_identification`: `"heat_pump_on": planned_draw_runs(float(override))` -> `float(override) > 0.05`. `tests/features.py` rc=1, `1 of 4451`: "an experiment command under the running floor does not mark the pump on (D8-s1-01)".
- `accuracy.py` `AccuracySample.from_dict.num`: `value = finite_float(data.get(key))` -> a bare `float()` of the raw value. `tests/features.py` rc=1, `1 of 4451`: "a stored sample's numbers go through const.finite_float: a bool or a non-finite value loads as unknown (D7-s2-58 class)" (`True used to load as 1.0`).
- `coordinator.py` `_plan_slots`: `heating = channel_heating_steps(powers, other_powers)` -> `[p > 0.05 for p in powers]`. `tests/features.py` rc=1, `1 of 4451`: "a plan slot holds only steps the plan runs, each channel on its own share (D8-s1-01)".
- `coordinator.py` `_async_drive_pumps`: `schedule = channel_heating_steps(...)` -> `[p > 0.05 for p in result.power_schedule]`. `tests/features.py` rc=1, `1 of 4451`: "the space pump reads the plan's space-heating steps, not its raw draw (D8-s1-01)".
- `wood_fuel.py` `wood_fuel_from_parts`: `list(result.heat_pump_on_schedule or [])` -> `[p > 0.05 for p in result.power_schedule]`. `tests/features.py` rc=1, `1 of 4451`: "a step the plan calls off is no pump hour for the wood advisor (D8-s1-01)".
- `coordinator.py` `_build_plan_views`: `channel_heating_steps(raw_space[:1], raw_dhw[:1])[0]` -> `raw_space[0] > 0.05`. `tests/features.py` rc=1, `1 of 4451`: "a plan channel is heating now only on a step the plan runs (D8-s1-01)".
- `inputs.py` `state_power_kw`: `if kw is None or not math.isfinite(kw):` -> `if kw is None:`. `tests/features.py` rc=1, `1 of 4451`: "a power state parses to finite kW under the caller's sign policy, or to no reading".
- `coordinator.py` `_freq_fold_blocked`: `freeze_reason is not None` -> `== pump_signals.FREEZE_COOLING`. `tests/features.py` rc=1, `1 of 4451`: "an offline, faulted or cooling pump's interval never teaches the frequency map".
- `coordinator.py` `_pv_measured_production`: `sign="clamp"` -> `sign="signed"`. `tests/features.py` rc=1, `1 of 4451`: "a negative production reading is clamped to zero, not propagated".
- `quiet_windows.py` `_within_nameplate`: the range bound -> `return kw`. `tests/manual_plan.py` rc=1: "a non-finite or over-nameplate power reading is no measurement" (`'100': 100.0`) and "a frequency past its configured maximum measures nothing".
- `const.py` `finite_float`: the `bool` arm dropped. `tests/finite_boundary.py` rc=1, `1 of 108`: "const.finite_float reads a real number or numeric text, and nothing else -- not a bool, bytes, NaN, an infinity or an int past a double".
- `dhw_schedule.py` `_parse_day_selector`: `cyclic_span` -> an inline `(lo + k) % 7` wrap. `tests/entities.py` rc=1, `4 of 2455` against the head's `2 of 2455`; beyond the head's FAIL names: "P2 owners: cyclic_range_wrap is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" (`SEAM ['dhw_schedule.py:125 in _parse_day_selector', ...]`) and "and each P2 fact fails on a new sibling outside its owner, and each refusal fires on its planted skip (null controls)".
- `pump_arbiter.py` `_write_night_schedule`: `quiet_windows.wall_clock(nxt[0])` -> an inline `divmod(... % (24 * 60), 60)`. `tests/entities.py` `4 of 2455`; beyond the head: "P2 owners: hour_clock ..." (`SEAM ['pump_arbiter.py:975 in _write_night_schedule']`) and the null-controls check.
- `tests/entities.py` `_p2_match_channel_line`, Compare arm -> `len(n.ops) == 1 and ...` (the chained spelling unread). `4 of 2455`; beyond the head: "P2 owners: channel_active_kw ..." (`STALE-DISPOSITION ['coordinator.py::HeatPumpOptimizerCoordinator._record_accuracy']`) and the null-controls check.
- `tests/entities.py` `_p2_match_channel_line`, by-name arm -> `False and ...`. `4 of 2455`; beyond the head: the same `channel_active_kw` check (`STALE-DISPOSITION ['optimizer.py::classify_space_steps', 'optimizer.py::classify_dhw_steps']`) and the null-controls check.

The driver is a one-off kept in the seat's evidence, not landed (`fixer.md` step 18).

**The new pins.** `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/guard_pins.py` drove the real ledger mutants: `PIN KILLED: 11 pinned, 3 left unpinned` on the first run, then `PIN KILLED: 1 pinned, 0 left unpinned` after the `format_clock` check, each `killed by tests/guard_pins.py`. Its null control, a comment-only edit at `accuracy.py:50` (NULL_COMMENT), survived every driver, and guard_pins' unmutated baseline read `rc=0 failed=0`. The 2 survivors are triaged (Unpinned sites).

## Null control

- Unmutated head, gate run below: `tests/features.py` `ALL 4451 FEATURE CHECKS PASSED`, `tests/manual_plan.py` `ALL 132`, `tests/finite_boundary.py` `ALL 108`, `tests/guard_pins.py` `ALL 61`.
- `tests/entities.py` reads `2 of 2455` at this head and `2 of 2451` at the merge base `510787b76`, run one after the other on this box. The sets of FAIL-prefixed names (the line up to its `[`), sorted and compared with `diff`, printed `IDENTICAL-FAIL-NAME-SETS`; the two top-level failures at both ends are `hb:positive_control` heartbeat timing self-tests on try 3 of 3 (py-spy not naming the spin on a loaded box). This diff adds none.
- `env_drift.py --all 510787b76` at this head: "NO UNCLAIMED DRIFT: 56 scenario(s)" and "NO STALE FIXTURE: 56", with both claim files byte-identical to the base.
- Each finder harness's `--perturb` arm reads at both ends as listed in Figures; a harness that reads flat says so.

## Figures

Every command ran with `PYTHONPATH=tests/hastub` (plus `:custom_components` for the harnesses), on Linux x86_64, at head `864a96c02` unless the base `510787b76` is named. A harness at the base ran from the head's copy with the base worktree as its working directory, except `probe_coercion_reach.py`, which resolves its root from its own path and so ran from the base's own copy (the same sha1).

- **Gate**, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=510787b76 ./tests/run.sh` at `864a96c02`: `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` Every script passed except `tests/entities.py`, `2 of 2455`, the two heartbeat self-tests under Null control. That run includes `tests/stress.py` `ALL 113 STRESS CHECKS PASSED` (carry 3's quiet-window re-take), `tests/structure.py` `STRUCTURE RATCHET PASSED` and `tests/harness_headers.py` `ALL 112`. The same gate at `632715d74` against `ed1c9045e` had read `3 of 2455`: the heartbeat pair and "and the lane's docstring records those measured numbers as the selection-cost note (#1218)" (`missing markers -> ['131 of the 528']`), which `632715d74` answers.
- **Mutation ratchet**, `python3 tests/mutation_table.py --scope changed --base origin/main --max 0`: `3842 unpinned site(s) of 6383 candidate sites, 3907 at the ratchet base 510787b769407ed25054177cfb0f6bd17e041e0e; the ledger agrees with the deterministic inventory`, no refusal and no ADDED UNPINNED line. Before the pins, `python3 tools/pr/ci_predict.py --base origin/main` listed 12 added unpinned keys (14 mutants); at this head it prints "no closures, fast, wave-script or instrument red predicted against 510787b76940" and no `ADDED UNPINNED` line.
- **#1218 pairs**, a one-off over `tests/closures.json` with `tests/entities.py`'s `_d308_pairs` rule (Jaccard >= 0.80 of production closures): 9 pairs more at this head than at origin/main, every one of them with `tests/guard_pins.py` (block_duty, boost_drift_replay, card.mjs, card_drift.mjs, debug_collect, manual_plan, plan_view, solar_alignment, wood_advisor).
- **Band census**, `dev/audit/harnesses/r10_band_census.py` (sha1 `b2b3a938866e6923748552125afda64a0d9ce599`), no arguments: `RESULT scenarios=50 susceptible=15 failures=0`. The 15 on this Linux host: away_setback, direct_flow_carnot, everything_on, fuse_guard, shoulder_two_zone, tariff_plus_two_zone, valve_storage, valve_storage_low_target, valve_storage_small_tank, valve_storage_smart_write, valve_upper_direct_slab, winter_two_zone_dhw, wood_coil, wood_two_tank, wood_two_tank_smart_write. The round-4 run of the same harness on macOS arm64 also counted 15, but a different set (as the round-4 body recorded it: it had cool_rainy_summer, dhw_cold_tank, flat_prices, horizon_48h and valve_storage_flat_prices, and lacked away_setback, everything_on, fuse_guard, shoulder_two_zone and winter_two_zone_dhw): which scenarios carry a band step is a property of the host, the evidence for the split. Rule: a scenario is susceptible when, at any of the nudges {0, 1e-15, 1e-12, 1e-9} to price n//3, its solve has a channel draw above 0.05 kW on a step whose whole ask is at most 0.1 kW.
- D7-s2-61 / carry 1, `dev/audit/rounds/round10/catchup/arch-s2/probe_coercion_reach.py` (sha1 `c88a691c230d8c20a33e5f6f5831994d319df931`): at the base `silent_cap_kw=6.0` (p_max, no cap) for `1e6`, `1e400` and `inf`, with `inf_changes_decision=1`; at the head 4.2, the `unknown` arm, for all three, with `inf_changes_decision=0`. `unknown` reads 4.2 and `3` reads 3.6 at both ends (null control).
- D7-s2-01 `pump_offline` / carry 6, `dev/audit/rounds/round10/D7/s2/learner_gates.py` (sha1 `5b77f8743adbc990a2277046e9cdbb83c4d3a537`): `pump_offline.learners_ingesting` is 1 at the base and 0 at the head; `clean.learners_ingesting=8`, `freq_map_clean_folds=8` and `freq_map_defrost_folds=0` at both ends (null control).
- D7-s2-59 / carry 4, `dev/audit/harnesses/r10_weekday_range_twins.py` (sha1 `c409a33ef918234bdd3a8394583fb01d4ee35a7c`): `pairs=49 disagreements=0` at both ends, `--perturb` `disagreements=49` and `--identity` `disagreements=0` at both ends. It reads flat because this is a refactor; the class rule is the `cyclic_range_wrap` P2 entry, which passes at the head and fails on the inline-wrap mutant (Mutation proof).
- D7-s2-58, `python3 dev/audit/harnesses/r10_finite_float_census.py <head> <tree>`: `RESULT coercers=13` at the base and `RESULT coercers=1` at the head (`const.py::finite_float`).
- D7-s2-57, `grep -rnE '%=? *\(?24 \* 60\)?' custom_components/heatpump_optimizer/*.py | wc -l`: 5 at the base and 2 at the head, the two owners (`dhw_schedule.py` `format_clock`, `quiet_windows.py` `wall_clock`).
- D8-s1-01 / carry 5, finder harness `dev/audit/rounds/round10/D8/s1/f1_active_now.py` (sha1 `766cc95a3b886f3f70d122a167028d2313d78048`): at the base `heating_now_while_off=2`, `slot_steps_declared_off=5`, `snapshots=36`; at the head 0 and 0, `snapshots=36`. `--perturb`: `heating_now_while_off=0` at both ends, `slot_steps_declared_off` 5 at the base and 0 at the head.
- Companion `dev/audit/harnesses/r10_channel_running_rule.py` (sha1 `713436520d8f67bc9539ed962329ac1f0e8ff7c7`): at the base `slot_steps_declared_off=5`, `reason_steps_declared_off=5`, `sensor_periods_declared_off=2`; at the head 0, **5** and 0 (`sensor_state=None`). The reason arm reads 5 at both ends because it is the parked arm. `--perturb`: 0, 0 and 0 at both ends.
- Class enumeration, `python3 dev/audit/harnesses/r10_channel_line_reach.py <head> <tree>` (the `channel_active_kw` rule): `RESULT hits=26` at the base and `RESULT hits=19` at the head. Each head site with its disposition:
  - the owner, `optimizer.py::channel_heating_steps`;
  - `classify_space_steps` and `classify_dhw_steps`: distinct finding R10-ARCH-SHAPES-CLASSIFIER, the parked arm;
  - `accuracy.py::delivered_ratio` (2) and `AccuracyTracker.power_ratio`: a ratio's denominator floor;
  - `coordinator.py::_async_learn_buffer_cooling` and `_observe_frequency`: #2238 P2 sweep instances;
  - `freq_control.py::FrequencyMap.observe`, `recommend` and `evidence_exhausted`: the map's own metered floor;
  - the non-power sites, each dispositioned by its unit: `away.py::estimate_recovery_hours`, `_maybe_run_fuse_advisor`, `_record_accuracy`, `DhwProfileLearner.async_learn_usage`, `DhwPlanner._dhw_shortfall`, `ledger.py::freeze_month_report` (2) and `narrative.py::build`.
- Carry 8, `tests/entities.py` at both ends: "P2 owners: state_age is decided only by its owner or a dispositioned site, its owner exists, no disposition is stale, the rule is live" passes at the head. `git grep -n ATTR_MIN_TEMP custom_components | wc -l` prints 0 at this head.
- `python3 tools/audit/archscore/score.py --diff 510787b769407ed25054177cfb0f6bd17e041e0e HEAD`: `Architecture score: dS +1.8326 IMPROVES` (see `## Architecture score`).

## Architecture score

Architecture score: dS +1.8326 IMPROVES against the merge base `510787b76` (`python3 tools/audit/archscore/score.py --diff 510787b769407ed25054177cfb0f6bd17e041e0e HEAD`). No gate metric rises.

- duplication_copies 38 -> 35
- coord_footprint 2423 -> 2414
- params_over_10 7 -> 6
- layer_violations 17 -> 13
- private_cross_module 12 -> 10

No budget is raised; no `*_budgets.json` changes in this pass.

## Red checks

Every red the branch's commits carried, each read from its job log; main's comparison is main's own push CI over the same window (runs 40225415246, 40230380300, 40241491498, 40253407217, 40262054829, 40268792477).

- **`tests / mutation`** (this branch's): red at every head, last at `4b513acdd` (job 121388964907): "MUTATION TABLE REFUSED -- 3887 unpinned site(s) against 3938 at the ratchet base f6784210..., 13 of them added by this diff". The cause is the move itself: re-spelling a guarded line onto `finite_float` changes its content anchor, so each guard, bound and removable return on a re-spelled line is a new site, and `mutation-autofix` can pin only what an existing driver kills. Cured at `632715d74` (Figures, Mutation ratchet). Cheaper detector: `ci_predict.py` (prepr step 6d), which costs seconds and named every site before each push. It was not missing; earlier rounds deferred the sites to the bot, which kills nothing no driver checks. The countermeasure already in force is prepr step 7d, which asks `## Unpinned sites` for each site's disposition; this body gives each one a pin or a triage rather than "owed to the pin run".
- **`tests / mutation-autofix`** (this branch's): red at `734ad21fa` (job 121264338925) and `d710a5af5` (job 121302641404), "AUTOFIX: skip-measure-failed -- THE REPAIR DID NOT HAPPEN", the job's own report that it could not measure; it went green with `skip-nothing-killed` at `4b513acdd`. It reports on `tests / mutation`, so its detector is that one's, above; no separate detector is owed.
- **`tests / fast (3.14)`** (this branch's): red at `734ad21fa` (job 121260837344: `env_drift.py` 2 STALE CLAIMS, `dhw_cold_tank` and `horizon_48h`; `stress.py` `2 of 113`, heating steps with no reason code) and at `d710a5af5` (job 121296829654: `env_drift.py` 2 STALE CLAIMS, `away_setback` and `valve_storage_small_tank`). Both are the classifier arm's host-conditional drift, which round 4 split out; green at `6f91e6d05` and after, and this head's gate passes both scripts. Cheaper detector: none before the runner, since a dev box is a different numeric environment and the band census shows hosts move different subsets. Countermeasure: the claim-grammar group R10-996-RUNNER-CLAIMS, opened when #996's tally crossed its threshold (comment 6404201979).
- **`prelude`** (neither branch nor main code): red once, in the `edit` run 40255792086 at `e088bf833` (job 121357226591): `tools/ci/prelude.py` printed `RATE-LIMITED reset_epoch=1792984021 repos/tvofi/heatpump_optimizer/actions/runs/40255792457/jobs` and exited 3 after 79 minutes waiting on the API quota. Every `code`-run `prelude` on this branch passed, and so did main's push `prelude` in all six runs above. The cause is the repository-wide GitHub API rate limit, not this diff. Cheaper detector: none exists, since a quota is runtime state of the shared token that no static read of the branch can see. Its recurrence is already a group, R10-RCA-RATELIMIT-RECUR, in the round-10 fixer pool.
- **`governance / delivery-status`** (programme-wide, not this diff's): red at `734ad21fa`, `d710a5af5`, `6f91e6d05` and `e088bf833` on OVERDUE delivery rows of other pull requests (for example `#2821`, `#2812`, `#2798`, `#2762`), each pinned to that head's merge base. It is not a required context, its own log says a red blocks no merge, and main's push CI skips it. It passed at `4b513acdd`. It is itself the detector for an undrained batch, so no cheaper one is owed; this branch writes no delivery row.

## Forward-carry

- The D8-s1-01 reason-classifier arm: `optimizer.classify_space_steps` / `classify_dhw_steps` read each channel's draw only on its `channel_heating_steps`. The commit carries the helpers `channel_heating_draw` / `_heating_draws`, the feature check "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)", and the two `tests/entities.py` dispositions back to the owner-module reading. It is commit `996b54cf15ea3c7693383165ae2f080d2e04971b` on `park/r10-arch-shapes-classifier`, and claims nothing until the claim grammar lands; the band census is its evidence. Carry: R10-ARCH-SHAPES-CLASSIFIER
- The census `dev/audit/harnesses/r10_band_census.py` and its susceptible set are the input to the claim grammar for runner-conditional drift. The set is host-dependent: this Linux run and the round-4 macOS run each count 15 with different members (Figures), so the claim grammar needs their union at least. Carry: R10-996-RUNNER-CLAIMS

## Friction

none

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head lists no site the diff adds. Before this pass's pins it listed these 12 keys (14 mutants), and `--pin-killed` also drove `dhw_schedule.py:458 GUARD_OFF`; each one's disposition:

- `custom_components/heatpump_optimizer/accuracy.py:124 CMP_BOUND`: pinned, `killed_by` `tests/guard_pins.py` ("an accuracy sample's zero planned draw is kept").
- `custom_components/heatpump_optimizer/const.py:1335 GUARD_OFF`: pinned, `tests/guard_pins.py` ("an unreadable tank volume has no surface, not a raise").
- `custom_components/heatpump_optimizer/coordinator.py:417 CMP_BOUND`: pinned, `tests/guard_pins.py` ("a stored aperture sum at its floor is kept").
- `custom_components/heatpump_optimizer/coordinator.py:4065 CMP_BOUND`: `survivor_triage` verdict `gap`, `coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.CMP_BOUND.8c3893c0.json`. The mutant moves `> 0.01` to `>= 0.01` on the curve displacement; the line was unpinned on main as `_as_float(...)` and only re-keyed here.
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 CMP_BOUND`: pinned, `tests/guard_pins.py` ("three contiguous days render as a range, two as a list").
- `custom_components/heatpump_optimizer/dhw_schedule.py:151 GUARD_OFF`: pinned, the same check.
- `custom_components/heatpump_optimizer/dhw_schedule.py:458 GUARD_OFF`: pinned, `tests/guard_pins.py` ("a window ending at midnight keeps 24:00").
- `custom_components/heatpump_optimizer/inputs.py:391 GUARD_OFF`: `survivor_triage` verdict `equivalent`, `inputs.py/state_power_kw.GUARD_OFF.4cd28db0.json`: with the guard off, a None state reaches `finite_float(None)` and the next guard returns None, the same answer.
- `custom_components/heatpump_optimizer/optimizer.py:1358 CMP_BOUND`: pinned, `tests/guard_pins.py` ("a channel drawing exactly the active line is not heating").
- `custom_components/heatpump_optimizer/quiet_windows.py:343 CMP_BOUND*2`: both pinned, `tests/guard_pins.py` ("a measured ceiling of zero is no measurement", "... exactly at the nameplate is admitted").
- `custom_components/heatpump_optimizer/sensor.py:1381 RETURN_DEL`: pinned, `tests/guard_pins.py` ("the DHW minimum ceiling is the setpoint less the margin").
- `custom_components/heatpump_optimizer/wood_fuel.py:136 CMP_BOUND`: pinned, `tests/guard_pins.py` ("a pump hour costing exactly wood's price is not cheaper wood").
- `custom_components/heatpump_optimizer/wood_fuel.py:157 CMP_BOUND`: pinned, `tests/guard_pins.py` ("a COP series shorter than the horizon reads as no COP, not a raise").
