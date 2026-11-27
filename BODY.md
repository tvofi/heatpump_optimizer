R11-SEAM-inputs-freshness: age and expiry of live inputs at the input boundary, with the reader arm of D7-s1-05 (ADR-001) and the reader's clock of ADR-002 part 2.

Refs #3744 (D1-s2-52), #3748 (D1-s2-02, D1-s2-03, D14-s2-02), #3757 (D1-s3-02), #3762 (D17-s2-02), #3774 (D14-s2-01), #3787 (D7-s1-05, reader arm), #3789 (D7-s1-06, ADR-002 part 2). Each issue stays open; the merge closes nothing.

- `inputs.entry_reader` is the one place the watchdog switch and age scale reach an `InputReader` (ADR-001 reader arm). The external-heat, state and humidity reads go through it, and so does the PV meter. The humidity read used `InputReader(hass, {})` with the watchdog defaults (D1-s2-52). The PV meter bypassed the reader and its 30 min limit (D1-s2-02).
- The reader takes its clock from the caller, which hands in `dt_util.utcnow`. Its fallback is `datetime.now(UTC)`, so `inputs.py` imports nothing from Home Assistant (ADR-002 part 2).
- `covering_forecast_row` is the one covering-row lookup for a forecast. `forecast_outdoor_now` delegates to it, and `_current_weather` reads the covering row instead of row 0 (D14-s2-02). A fetched reply with no row covering now is a failed fetch, not a recovery (D1-s2-03).
- D14-s2-01 takes the finding's second arm, not `inf`. Six tests pin the control direction: a flag latched on yesterday must excuse no COP sample today. The finite limit is kept, and `inputs.PUSHED_FLAG_KEYS` marks a quiet pushed flag `quiet`. `InputHealth.stale_keys` and `details()` then leave it out of `stale_inputs`, the problem list and the Input Problem sensor. A polled flag that went silent still lists.
- `plan_step.hold_current_hour` plans the current hour at a live outdoor reading (D17-s2-02). It uses absolute instants, because the DST census refused wall-clock hour arithmetic. `InputHealth.live` returns the reading.
- `_parse_ecl110_state` refuses a JSON bool at both arms (D1-s3-02).

Previous seat's BLOCKED.md: none exists for this group. No `handoff-wip/r11-seam-inputs-freshness` ref existed before this seat, and no commit's `BLOCKED.md` names the topic. Nothing to decide.

## Head

602cc4b2c78a512f63e690c08a48a9460246c715. It follows d5a59dcc9a, the merge of origin/main 8890fc2bad into the branch. That merge brought main's reworded HA-free check in tests/entities.py, which hard-coded "the one toucher", so 602cc4b2c7 makes it subtract the documented touchers, none since inputs takes its caller's clock. `git merge-tree` reported a conflict in docs/architecture.md: main reworded "The other N modules" to "Every other module", and main's line was taken. The figures and suites below were taken at f7959f39f8 (fork fd93aa3e9b) unless marked. At this merge, `tests/structure.py` rc 0, `tests/doc_claims.py` ALL 445 checks PASSED, `tools/audit/archscore/score.py --diff origin/main` reads the same dS +1.2196, and `m7_layer_edges.py` reads `layer_violations=2` with the same two carriers. At 602cc4b2c7, `tests/entities.py` ALL 2791 ENTITY CHECKS PASSED. `tests/features.py` ALL 6283 FEATURE CHECKS PASSED and `tests/deployment_shape.py` rc 0 at d5a59dcc9a. Stamped 2026-11-27 UTC against origin/main 8890fc2bad.

## Mutation proof

Each fix was reverted alone in a detached worktree at the head, and the block `# --- R11-SEAM-inputs-freshness: age and expiry of live inputs ---` was run through `tools/audit/seat/features_block.py`. The head and restored trees are green. Each mutant fails its own check, and only that check:
- M1, humidity back on `InputReader(self.hass, {})`: `the humidity read obeys the entry's watchdog switch (D1-s2-52)` [(None, None)]
- M2, PV gate off: `a PV meter silent past its limit, or stamped ahead of now, is no measurement; a live one still is (D1-s2-02)`
- M3, stuck-reply branch off: `a forecast that stopped advancing marks the data stale; one reaching now does not (D1-s2-03)`
- M4, `_current_weather` on row 0: `a held forecast books the row covering now, and no wind past its last row (D14-s2-02)` [30 h held (0.0, 0.0)]
- M5, quiet mark off: `the six pushed pump flags quiet 255 min stay stale for control but publish no stale input or problem; polled and silent they still do (D14-s2-01)`
- M6, live outdoor value not handed on: `a live outdoor sensor plans the current hour, the next hour stays forecast (D17-s2-02)` [live (-5.0, -5.0, ...)]
- M7, bool admitted at both arms: `the ECL110 parser refuses a JSON bool and keeps a number (D1-s3-02)` [[1.0, 0.0, 1.0, 7.0, 3.0]]
- M8, `homeassistant.util.dt` import restored in `_utcnow`: `inputs.py imports nothing from Home Assistant; a reader with no clock reads the standard library's UTC now (ADR-002 part 2)`

The driver is `$SCRATCH/mutate.py` (sha1 8b1235c7), a one-off probe kept out of the tree.

MUTANT_CMD=`python3 tools/audit/seat/features_block.py "# --- R11-SEAM-inputs-freshness: age and expiry of live inputs ---"`
prepr ran with `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1` (scoped, the brief's), so its diff-mutant step skips. The run below is the brief's `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --report-only` at 4c0910fa3a, rc 0. Its survivors, verbatim:
`SURVIVED custom_components/heatpump_optimizer/coordinator.py:764 CMP_BOUND  index = 0 if now <= starts[0] else covering_index(starts, now, timedelta(hours=1))` (printed twice, one site)
The three earlier runs' other survivors are killed at this head by the block's `the covering row: ...`, `an unavailable pushed flag is still listed as an input problem` and `a cycle reads through the entry's reader ...` checks. The two `reader = entry_reader(...)` STMT_DELs were confirmed killed first by a real cycle (`NameError: name 'reader' is not defined`).

## Null control

Each harness's own null arm, at the base and at the head:
- weather_stuck.py `--advancing` (rows start at the current hour): the head's block check gives `-47 h` and `0 h` starts → not stale.
- pv_stale.py `--fresh`: the block check's 5 and 20 min cells still publish 5.0.
- staleness_flags.py `null_*` (changed 10 min ago) and `polled_*` (re-reported 1 min ago): 0 at both ends.
- current_weather `h0_match=1` and `outdoor_sibling_mismatch_hours=0` at both ends.
- outdoor companion `--unset` (option absent): `step0_outdoor_spread_K=0.000` at both ends.
- humidity_reader_settings.py `null_disagree=0`, `fresh_disagree=0` at both ends.
- parsers_fuzz.py `ecl110_numeric_null_control=2` at both ends.

The unmodified tree reads every defect (Figures, base column).

## Figures

Harnesses at `dev/audit/rounds/round11/` on main (sha1 of each file at fd93aa3e9b), run as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/<dimension>/<scope>/<harness>.py`, base fd93aa3e9b → head f7959f39f8 (production unchanged since 4c0910fa3a, where every figure below was taken; f7959f39f8 deletes 11 ledger pins):
- D1/s2/weather_stuck.py (8ad65a2f): `stuck_published_fresh` 5 → 0
- D1/s2/pv_stale.py (ab9bfb6d): `stale_cells_published` 6 → 0, `future_published` 1 → 0
- D14/s2/current_weather.py (e56efaae) does not run at main (`AttributeError: ... no attribute '_covering_index'`: #2229's rename). Its port changes only that name (`cmod._covering_index` → `cmod.covering_index`, two lines; `$SCRATCH/probes/current_weather_port.py` sha1 52feb315): `wind_mismatch_hours` 72 → 0, `booked_planned_wind_h30` 10.0 → 40.0
- D14/s2/staleness_flags.py (cf89801b): `quiet_stale_flags` 6 → 0, `quiet_input_problem_on` 1 → 0
- D17/s2/outdoor_sensor.py (575c1ee0) reads flat at both ends (`step0_outdoor_spread_K=0.000` base and head). Its own null `null_no_forecast_step0_spread_K` reads 0.000 at main where the record says 35.0, because its rig's `expert` walk no longer assigns the outdoor option (reading `problem='not_configured'`). Companion `$SCRATCH/probes/outdoor_companion.py` (sha1 594947b9) sets the option directly: `step0_outdoor_spread_K` 0.000 → 35.000, `step4_outdoor_spread_K` 0.000 → 0.000 (the next hour stays forecast)
- D1/leads/humidity_reader_settings.py (003f8950): `config_arms_disagree` 2 → 0
- D1/s3/parsers_fuzz.py `--arm ecl110` (75c288fe): `ecl110_bool_accepted` 3 → 0
- D7/s1/m7_layer_edges.py (2ef176cc): `layer_violations` 6 → 2; the two CARRIER lines left are `setpoint_check` and `snapshots`, the modules ADR-002 decision 3 keeps

Class sweeps, each finding's own seam rule, run at the head:
- D14-s2-02, `dev/audit/rounds/round11/D14/s2/covering_census.py` (a85bb128): 22 constant-index sites in 19 functions. `coordinator.py covering_forecast_row forecast[0]` is the untimestamped-rows arm (positional by design, the same assumption `_weather_series` makes); the `_current_weather` site is gone. The other 21 index sample, history, price-extension, timestamp-list and plan-result containers, not a forecast read as now: `_async_drive_pumps result.timestamps[0]`, `_forecast_arrays series[-1]` (pad), `debugger.cycle_row`, `dhw_learning.payload`, `disinfection.observe/view` (a (value, stamp) tuple), `plan_slots.close`, `price_model.extend_price_series`, `pump_arbiter._feedback` ×2, `room_history` ×2, `room_record.report_of`, `sysid.step` ×2, `wood_fuel` ×6 (the plan's step timestamps). Not widened: the barrier `_r10_covering_lookups` (the finding's proposed barrier). Carry below.
- D1-s2-02, `dev/audit/rounds/round11/D1/s2/consumers.py` (e3e11311): `CONF_PV_PRODUCTION_ENTITY` now lists `reader_keys=['pv_production_entity']`. Its getters run through `inputs:read` under `_pv_measured_production`, closed in this diff. The other age-limited slots' getters are all `inputs:read*`, already guarded.
- D1-s2-03, `dev/audit/rounds/round11/D1/s2/price_weather.py` (df02d488): `price_stuck_hidden` 0 at both ends; `weather_empty_hidden` 0 at both ends. `weather_stale_hidden` reads 1 at both ends, but the counted cell differs. At the base, `stuck+60h` published `stale_hours=None`. At the head it publishes `0.0`: the outage latched on that cycle, the forecast is flagged stale and the outdoor forecast is `None`. The harness's predicate `not sh` counts `0.0` as hidden, and the finding's own harness counts it stale.
- D14-s2-01, `dev/audit/rounds/round11/D14/s2/staleness_detector.py` (6e17dfd4): `quiet_stale_q255=13` and `quiet_stale_q480=19` count `InputReader`'s stale flag, which stays set for control by design. The publication is closed for the six `PUSHED_FLAG_KEYS`; the other keys keep their stale-and-published behaviour (the census `_r10st_same` names why for each).
- D1-s3-02, `python3 tools/audit/enumerate.py d1-parsers | grep -E '_parse_ecl110_state|parse_bool'`: `_parse_ecl110_state` (closed here); `inputs.parse_bool` already returns a bool as a bool (`if isinstance(raw, bool): return raw`).

Suites at the head: `tests/features.py` ALL 6283 FEATURE CHECKS PASSED; `tests/entities.py` ALL 2786 ENTITY CHECKS PASSED at c9e588afa5 (features ran at b4f58ff0b8; what followed touched tests/entities.py, a ledger file name and, at the head, only the `entry_reader` annotation); `tests/doc_claims.py` ALL 443 checks PASSED; `tests/structure.py` rc 0 after the re-record below. The rest of what `tests/closure.py select --diff fd93aa3e9b` names (`MODE: SCOPED -- 30 script(s) run, 4 scoped out` at the first commit) exits 0 under `GOLDEN_MODE=drift`: arch_score_head, backtest, block_duty, boost_drift_replay, card.mjs, card_drift.mjs, config_flow_steps, cycle_lane, debug_collect, deployment_shape, edge, env_drift, finite_boundary, frontend, golden, guard_pins, harness_headers, manual_plan, open_meteo, optimality, plan_view, solar_alignment, stress, validate, wood_advisor. typing_ruler refused `by_code[arg-type]` +1 at c9e588afa5 and passes at the head (ALL 9 and ALL 12 checks).

## Raise justification

The `tests/structure.py` rows `class_excess_loc` 17220 → 17228, `max_class_loc` 7762 → 7770, `module_excess_loc` 21646 → 21668 and `seam_cut_total` 413 → 415 are re-recorded under mandate 6893738184 (scope all, until 2026-12-15T12:00Z). The reason is in the commit message. The rise is the fixes' own logic: the PV age gate, the stuck-reply branch, the live-hour hand-off and the covering-row owner.
Payments tried: hold_current_hour moved to plan_step, the step grid's owner (paid `functions_cc_over_15` back to 26: `_weather_series` cc 20 → under 16); `InputHealth.live` owns a reading's usable value; the ECL110 bool refusal rewritten branch-free (`_parse_ecl110_state` cc 16 → 14); `forecast_outdoor_now` deduplicated onto `covering_forecast_row`; the locals the fix added in `_indoor_humidity_value` and `_pv_measured_production` dropped (`coord_footprint` 2539 → 2538, class +16 → +8). Tried and reverted: handing the live value to `_weather_series` as a parameter moved the branch into `_forecast_arrays` (`functions_cc_over_15` +1) and left `seam_cut_total` unchanged. Not taken: moving `covering_forecast_row` to `plan_step` needs `_comparable_ts`, whose naive-reference arm calls `dt_util.as_local`, so the leaf would import Home Assistant or duplicate the parse.
Architecture score: dS +1.2196 WORSENS

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` at the head: `dS +1.2196 WORSENS (inadmissible: coord_footprint 2533->2538)`, `layer_violations 6 -> 2 +1.2224`.
- `coord_footprint` 2533 -> 2538: five coordinator-class statements are the fixes' own logic. Two are the PV age gate, two the stuck-forecast branch and its failure call, and one the live-outdoor hand-off in `_weather_series`. `_current_weather`'s covering lookup replaced its row-0 read statement for statement.

## Unpinned sites

The 17 sites ci_predict lists as added with no ledger pin:
- `custom_components/heatpump_optimizer/coordinator.py:548 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `_parse_ecl110_state`'s bare-number arm; killed by the block's ECL110 check (`7` -> None).
- `custom_components/heatpump_optimizer/coordinator.py:749 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `covering_forecast_row`'s empty guard; the block's covering-row check drives `[]`.
- `custom_components/heatpump_optimizer/coordinator.py:759 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the untimestamped arm; the block's covering-row check drives untimestamped rows.
- `custom_components/heatpump_optimizer/coordinator.py:765 RETURN_DEL`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the covering row's return; every covering-row and `_current_weather` check reads it.
- `custom_components/heatpump_optimizer/coordinator.py:792 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `forecast_outdoor_now`'s past-the-end None; the block's covering-row check drives `_ifr_rows(-60)`.
- `custom_components/heatpump_optimizer/coordinator.py:5468 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `_current_weather` past the end; the D14-s2-02 check drives it.
- `custom_components/heatpump_optimizer/coordinator.py:5471 CLAMP_DROP`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the wind clamp at 0; no row carries a negative wind in the block, so it is left to mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:5472 CLAMP_DROP`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the precipitation clamp at 0; as above.
- `custom_components/heatpump_optimizer/coordinator.py:7018 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the stored-forecast branch; the D1-s2-03 check's -47 h and 0 h starts need it.
- `custom_components/heatpump_optimizer/inputs.py:171 BOOLOP`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `stale_keys`' quiet filter; the D14-s2-01 check reads `stale_keys`.
- `custom_components/heatpump_optimizer/inputs.py:176 BOOLOP`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `InputHealth.live`'s guard; the cycle check reads `live` for an unread key.
- `custom_components/heatpump_optimizer/inputs.py:176 RETURN_DEL`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `InputHealth.live`'s return; the cycle and D17-s2-02 checks read it.
- `custom_components/heatpump_optimizer/inputs.py:199 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `details()`' quiet skip; the D14-s2-01 and unavailable-flag checks read `details()`.
- `custom_components/heatpump_optimizer/inputs.py:1054 RETURN_DEL`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the stdlib clock fallback; the ADR-002 check calls `_utcnow()` with no clock.
- `custom_components/heatpump_optimizer/plan_step.py:102 GUARD_OFF`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: `hold_current_hour`'s no-value guard; the D17-s2-02 check's `none` arm.
- `custom_components/heatpump_optimizer/plan_step.py:106 BOOLOP`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the in-range guard of the hour comparison; the D17-s2-02 check.
- `custom_components/heatpump_optimizer/plan_step.py:106 CMP_BOUND*2`: mutation-autofix (its lane mutates custom_components/ and pins each kill). The local block: the hour bound; the D17-s2-02 check reads step 3 (inside) and step 4 (outside).

The diff-mutant survivors under `MUTANT_CMD`:
- `coordinator.py covering_forecast_row CMP_BOUND` (`now < starts[0]` → `<=`): equivalent, triaged in `tests/mutation_ledger/survivor_triage/coordinator.py/covering_forecast_row.CMP_BOUND.ad56f0aa.json`. The mark was re-keyed from `forecast_outdoor_now ... 08c8c646`, because the line moved unchanged and only its indentation changed.

## Red checks

- `budget-raise-gate`: red by design until an approving review lands at the head on the raise recorded in `tests/structure_budgets.json`. Under mandate 6893738184 that review may be an agent's, once `## Raise justification` holds. No cheaper detector exists: the gate is the review it waits for.
- `mutation` (tests / mutation): predicted red at the head for the 17 sites the diff adds with no ledger pin (listed under `## Unpinned sites`). `mutation-autofix` pins each kill in custom_components/. The cheaper detector already exists and ran: `tools/pr/ci_predict.py` inside prepr, under a minute. It also caught the 11 stale pins this diff left, which f7959f39f8 deletes by hand as its repair text prescribes. Nothing further to build.

## Forward-carry

- The N-no-expiry barrier `_r10_covering_lookups` in `tests/entities.py` still counts only the `bisect_right(...) - 1` shape. D14-s2-02 proposed widening it to constant-index reads of a timed series. This PR closes the one forecast-as-now site the census returns. Carry: dismissed: of the 22 constant-index sites the census lists, 21 are sample, history or step-timestamp containers and not a series read as now, so a constant-index barrier would need a 21-entry allow-list keyed on container names, which silences any new forecast read that reuses those names (fixer.md step 14)
- `dev/audit/rounds/round11/D14/s2/current_weather.py` calls `cmod._covering_index` and fails at main; `dev/audit/rounds/round11/D17/s2/rig.py`'s `expert` walk no longer assigns the outdoor option. Both are the round's harnesses, outside the tree's gate. A later rerun needs the ports named in Figures. Carry: dismissed: the round's harnesses are its frozen evidence, and the ports are cited by sha1 in Figures

## Friction

none
