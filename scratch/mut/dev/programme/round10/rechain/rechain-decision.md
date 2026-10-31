# R10-FLOW-RECHAIN: decision on each coordinator.py `after` edge

Read-only decision seat, 2026-10-21. Nothing is applied here. The orchestrator applies the result in one burst.

## Bases and method

- **Roster:** `origin/handoff/audit-r10-roster` at `2c76c3128`. `origin/main` (`5d433771a`) has the same `after` list for every coordinator.py group. The two copies differ only in stage values, and in the newer groups that main does not carry yet (checked with `jq -S '[.groups[]|{group,after}]'`, then diff).
- **Code:** `custom_components/heatpump_optimizer/coordinator.py` at `origin/main` `5d433771a`, 11205 lines. Every line range below is a function span at that commit, taken from `ast`.
- **What a seam is.** Each group's owning seam comes from three sources:
  1. its architect note and brief in the roster;
  2. its prototype patch, where the brief names one (`arch-s1/ALL_P1_P2_P3`, `arch2-s1/P1` at 2c30ada11, `arch2-s2/P1,P2,P4,P6` at fabaf4664, `arch2-s4/P3` at b202335e2, `arch-s2/patches/05,06` and `arch2-s3/patches/03` at 1d1974df4);
  3. its pushed branch, where one exists: `handoff/r10-night-folds` at 79a542be2 and `handoff/r10-freq-defrost` at 25a94521b. `handoff/r10-advisor` has not been pushed.
- **Mapping hunks to functions.** Each patch or branch hunk was mapped to a function on main by its unique context lines, using a scratch script (`hunkmap.py`). Everything else was grepped (`git grep` and `grep -n`, with function spans from `ast`).
- **The rule (R6 and the brief).**
  - **DROP** needs two things: the two seams are disjoint (no shared function, and hunks far enough apart to merge cleanly), and neither group reads state the other writes.
  - An edge I could not show disjoint is **KEPT**.
  - Dropping an edge also removes any ordering that passed through it. Where that ordering joined two groups whose seams really overlap, a **replacement edge is required** (section 3).
- **Depth** is computed with `roster_lib.depth_of` and `critical_path` from origin/main, run on a scratch copy.

Scope: 15 edges between two not-done coordinator.py groups. Edges whose earlier group is already `done` (FEEDS, RATIO-SITES, VENT-DETECTOR, STORE, TARIFF, LEAF-IMPORTS, TRUST-RELATIVE, SAV-BASELINE, SAV-REASONS, SETPOINT-BOOST) already count as satisfied. They add no depth and were not examined. The UX-HEALTH and ARCH-DOCS rows of K7 are non-coordinator. They are **unchanged** and serve as the null control.

## 1. Decisions (15 edges: 8 DROP, 7 KEEP)

| # | edge (later after earlier) | later seam (main) | earlier seam (main) | evidence | K7 | verdict |
|---|---|---|---|---|---|---|
| 1 | RATIO-ANCHOR after NIGHT-FOLDS | Options-save and reload re-anchor: `_async_load_thermal_learning` 3699-3833 (ratio load 3737-3746), `_house_heat_loss_anchor` 4817-4832, `_reanchor_house_heat_loss_scale` 4834-4917, snapshot restore `_apply_learner_payloads` 9171-9249, store.py thermal domain L320-321, config_flow.py, sysid.py | Branch 79a542be2: imports 183/316, new helpers after `_house_loss_terms` 1069-1081, `_async_learn_house_heat_loss` 5007-5176, `_async_learn_lower_floor_loss` 5177-5283, `_fold_solar_aperture` 8961-9008, `_fold_internal_gains` 9009-9048, `_record_accuracy` 9623-9784; accuracy.py, const.py ~L1028-1050, store.py `_ACCURACY` L286, thermal_model.py ~L1570 | No shared function. store.py hunks are 34 lines apart (286 against 320). NIGHT-FOLDS changes *which intervals* fold into `_lower_floor_loss_ratio` (write 5269), not what the ratio means or how it is stored. RATIO-ANCHOR rescales the ratio when its prior moves. | drop | **DROP** |
| 2 | INPUT-STALENESS after RATIO-ANCHOR | `HUMIDITY_MAX_AGE_MINUTES` L1207, `_indoor_humidity_value` 8747-8767; const.py `INPUT_MAX_AGE_MINUTES` L287 and L1475-1562; inputs.py `max_age_for` L247-253 and the `InputReader` age check | As in row 1 | No shared function or file region. Neither group reads the other's state. | drop | **DROP** |
| 3 | CURRENCY after INPUT-STALENESS | `_narrative_view` 10328-10359; currency.py, narrative.py | As in row 2 | Disjoint. The None-price callers in the CURRENCY carry (`_current_action["price"]`, diagnostics, relative price) are not in the freshness seam. | drop | **DROP** |
| 4 | LOOP-CPU after FREQ-DEFROST | Off-loop `away.estimate_recovery_hours` (away.py L212, called at L450 from `away.resolve`), reached from `_resolve_away` 9484-9517 (called at 5751 in `async_run_optimization`); the note's `_replay_interval` call sites are 5088 and 5240 | Branch 25a94521b: `_freq_fold_blocked` 1002-1017, `_observe_frequency` 10530-10599, `.freq_control` imports L290-294; freq_control.py | Disjoint functions and files. FREQ-DEFROST's predicate is not read on the replay or away path. | drop | **DROP** |
| 5 | SCORES after ADVISOR | `_scores_view` 10277-10327, `_close_score_day` 10243-10275, `_fold_score_sample` 10204-10241, score sensor (sensor.py L2655-2680), scores card section | Advisor what-if = the price tiles: `_price_tile_specs` 10416-10439 (`target_minus_1`/`target_plus_1`), `_maybe_refresh_price_tile` 10440-10477; card advisor section (card.js L8650-8654 reads "the score sensor's `price_tiles`") | **Shared surface.** The overall score sensor publishes `**scores` and `"price_tiles"` in one `extra_state_attributes` (sensor.py L2679). `_insight_view` 10479-10497 carries `"scores"` (10484) and `"price_tiles"` (10495). Item (3) of the SCORES brief requires a consistency test across the Advisor surface that ADVISOR is changing. The card chain is advisor 3 then scores 4 of 5. | drop | **KEEP** |
| 6 | LIVESTATE after SCORES | P1-P4 and P6 (arch-s1 ALL, arch2-s2): `_update_current_state` 6037-6326, `_async_drive_pumps` 3611-3674, `adopt_action` 3227-3235, `_async_handle_ecl110_state_message` 3293-3306, `async_set_mode` 5867-5885, `_async_update_data` 5364-5500, `_fetch_weather_forecast` 6507-6592, `_on_power_event` 8319-8401, `_resolve_away` 9484-9517, `async_set_away` 9518-9544, `_file_lead_predictions` 9854-9896, `_init_grid` 3000-3071 (L3048-3049), `_maybe_refresh_price_tile` 10440-10477, `_insight_view` 10479-10497 (L10495) | As in row 5 | `_insight_view`: the P6 hunk at 10495 is 11 lines from `"scores"` at 10484. `_init_grid`: the score day book (L3043-3046) sits next to the price-tile fields (L3048-3049) that P6 moves. These are adjacent hunks in shared functions. | keep | **KEEP** |
| 7 | CONFIG-NOTICES after LIVESTATE | arch2-s2 P1: `_init_grid` issue fields L3012-3026, `_audit_grid_fee` 7079-7151, `_audit_lower_floor_sensor` 7153-7198, `_audit_comfort_band` 7199-7238; setpoint_check.py | As in row 6 | The only shared function is `_init_grid`. CONFIG-NOTICES writes L3012-3026 and LIVESTATE writes L3048-3049, 22 lines apart (separate hunks, clean merge), on disjoint fields. The notice fields are written only by `_audit_*`. LIVESTATE neither reads nor writes them. **Needs replacement edges** (section 3): PARAMS-OWNER and ARCH-SHAPES reached LIVESTATE only through this edge. | drop | **DROP** |
| 8 | PARAMS-OWNER after CONFIG-NOTICES | arch2-s1 P1: module helper by `_with_quiet_keys` (~1901), `_hub` 1986-2003, `_init_model` 2814-2821, `_init_dhw_learning` 2891-2924, `_init_features` 3089-3202 (L3120), `_apply_cop_scale` 4377-4380, `_apply_*` 4806-4815, `async_update_thermal_params` 5909-5995, `_update_current_state` (~6050/6175/6272), `_refresh_model_corrections` 6328-6341, `_async_load_accuracy` 7923-7941, `_apply_learner_payloads` 9171-9249. arch2-s4 P3: both learner methods 5007-5283, `_update_current_state` ~6277 | As in row 7 | No shared function or file. `_audit_lower_floor_sensor` only *reads* `ctx._thermal_params.two_zone_enabled`, which a copy-on-write snapshot keeps valid. K7's reason ("config-notice fields moved behind the owner") names the setpoint_check `ConfigNotices` owner, which is not the thermal-params owner. | keep | **DROP** |
| 9 | ARCH-SHAPES after PARAMS-OWNER | Patches 06 and 03: `_as_float` 383-400, `_at_least` 417-427, `forecast_outdoor_now` 681-725, `_forecast_in_model_units` 2117-2147, `_async_drive_pumps` 3611-3674, `_current_weather` 4775-4783, `_fetch_weather_forecast` 6507-6592, `_weather_series` 6775-6868, `_mixing_valve_view` 7727-7762, `_on_power_event` 8319-8401, `_pv_measured_production` 9422-9438, `_accumulate_energy` 9938-10074, `_fold_score_sample`/`_close_score_day` 10204-10275, `record_setpoint_override` 10703-10737. Carries: `_freq_fold_blocked` 1002-1017 (pump_offline), `_plan_slots` 3975-4057 and `_build_plan_views` 4097-4235 | As in row 8 | No shared function with PARAMS-OWNER. Neither patch touches `_thermal_params` or `ThermalParameters` (grep on 05, 06 and 03). **Needs a replacement edge** (section 3): ARCH-SHAPES shares `_async_drive_pumps` (L3657 in both), `_fetch_weather_forecast` and `_on_power_event` with LIVESTATE, and reached LIVESTATE only through PARAMS-OWNER. | keep | **DROP** (with ARCH-SHAPES after LIVESTATE) |
| 10 | ARCH-SHAPES after FREQ-DEFROST | Carry: "`_freq_fold_blocked` still admits `pump_offline` ... lands here because this group owns `freq_control.py`" | Branch 25a94521b edits `_freq_fold_blocked` (hunks -1003,8 and -1012) and freq_control.py | **Same function and same file.** | drop | **KEEP** |
| 11 | LEARNER-ETA after ARCH-SHAPES | Learner status in the payload: `_learning_view` 7519-7616; payload.py | As in row 9 | Nearest ARCH-SHAPES hunk is `_mixing_valve_view` at 7743, outside 7519-7616. LEARNER-ETA is a read-only view of learner state, and ARCH-SHAPES changes input coercion, not learner state. **Needs a replacement edge**: HEAT-METER reached ARCH-SHAPES and PARAMS-OWNER only through this edge. | drop | **DROP** (with HEAT-METER after PARAMS-OWNER and ARCH-SHAPES) |
| 12 | HEAT-METER after LEARNER-ETA | New input key, options step, COP sample (`_learn_measured_cop` 4612-4614 / `_fold_measured_cop` 4615-4748), house-learner delivered heat (`_interval_measured_heat_kw` 891-922 into `_replay_interval` 925-964); new hot-water COP bin | As in row 11 | Code-disjoint, but **state is shared**. HEAT-METER writes new learner state (a heat-meter COP sample source and its own hot-water COP bin in `_cop_baseline`, read at 7582-7583 in `_learning_view`). LEARNER-ETA publishes progress and "waiting for" for those same learners. Cannot be shown disjoint. | drop | **KEEP** |
| 13 | HEAT-METER after INPUT-STALENESS | As in row 12, plus const.py | As in row 2 | Brief carry (3): "Add the new key's max age through R10-INPUT-STALENESS's freshness rule". const.py chain 1 then 2. | keep | **KEEP** |
| 14 | HEAT-METER after RATIO-ANCHOR | As in row 12, plus config_flow.py options step | As in row 1 | Brief carry (2): "Adding the meter re-anchors the learner scales through R10-RATIO-ANCHOR's mechanism". HEAT-METER *calls* RATIO-ANCHOR's code. config_flow.py chain 1 then 2. | drop | **KEEP** |
| 15 | COP-GATE after HEAT-METER | COP eligibility and its published state (`_observe_cop_health` 9049-9106, `COP_BASELINE_MIN_SAMPLES` reads) | COP sample sites, as in row 12 | Brief: "R10-COP-GATE runs after you and handles only installs without a heat meter". The eligibility depends on HEAT-METER's sample source. | keep | **KEEP** |

**Where I differ from K7.** Of K7's 10 proposed drops I confirmed 6 (rows 1, 2, 3, 4, 7 and 11) and rejected 4:
- rows 5, 10 and 14 for code overlap;
- row 12 for shared state.

I added 2 drops K7 had kept: rows 8 and 9. That makes 8 drops in all.

## 2. Effect

| | critical depth | critical path |
|---|---|---|
| before (live roster) | **11** | ADVISOR, SCORES, LIVESTATE, CONFIG-NOTICES, PARAMS-OWNER, ARCH-SHAPES, LEARNER-ETA, HEAT-METER, COP-GATE, UX-HEALTH, ARCH-DOCS |
| K7 as proposed (10 drops) | 5 | not safe: it breaks rows 5, 10 and 14, and it unorders PARAMS-OWNER and ARCH-SHAPES from LIVESTATE |
| 8 drops alone, no replacements | 6 | not safe: it unorders PARAMS-OWNER and ARCH-SHAPES from LIVESTATE, where they share `_update_current_state` and `_async_drive_pumps` |
| **8 drops + 3 required replacements** | **8** | ADVISOR, SCORES, LIVESTATE, PARAMS-OWNER, HEAT-METER, COP-GATE, UX-HEALTH, ARCH-DOCS |
| plus the 4 recommended gap edges | **8** | unchanged |

Stage today and depth (before, then after drops, required and recommended edges):

| group | stage | depth before | depth after |
|---|---|---|---|
| R10-NIGHT-FOLDS | in-progress | 1 | 1 |
| R10-FREQ-DEFROST | in-progress | 1 | 1 |
| R10-ADVISOR | in-progress | 1 | 1 |
| R10-RATIO-ANCHOR | not-started | 2 | 1 |
| R10-INPUT-STALENESS | not-started | 3 | 1 |
| R10-CURRENCY | not-started | 4 | 1 |
| R10-LOOP-CPU | not-started | 2 | 2 (1 without the recommended LOOP-CPU after NIGHT-FOLDS) |
| R10-CONFIG-NOTICES | not-started | 4 | 1 |
| R10-LEARNER-ETA | not-started | 7 | 1 |
| R10-SCORES | not-started | 2 | 2 |
| R10-SENSOR-PAYLOAD (non-coordinator) | not-started | 3 | 3 |
| R10-LIVESTATE | not-started | 3 | 3 |
| R10-PARAMS-OWNER | not-started | 5 | 4 |
| R10-ARCH-SHAPES | not-started | 6 | 4 |
| R10-HEAT-METER | not-started | 8 | 5 |
| R10-COP-GATE | not-started | 9 | 6 |
| R10-UX-HEALTH (non-coordinator) | not-started | 10 | 7 |
| R10-ARCH-DOCS (non-coordinator) | not-started | 11 | 8 |
| R10-DEMAND-OVERBOOK | queued | 1 | 1 |
| R10-THERMAL-POWER-OPTION | not-started | 1 | 1 |
| R10-LEARNER-DEFAULT | not-started | 1 | 1 |

## 3. Edges to add

**Required.** Apply these in the same burst as the drops. Each restores an ordering the drops would otherwise remove between groups whose seams overlap.

| add | overlap it protects | lost by dropping |
|---|---|---|
| PARAMS-OWNER after LIVESTATE | `_update_current_state`: P1 hunks ~6175 and ~6272 against LIVESTATE hunks 6175 and 6267; P3 ~6277 | rows 7 and 8 |
| ARCH-SHAPES after LIVESTATE | `_async_drive_pumps` (both at L3657), `_fetch_weather_forecast` (6557/6560), `_on_power_event` (8349 against 8400) | row 9 |
| HEAT-METER after PARAMS-OWNER and ARCH-SHAPES | P3 "one fabric interval" rewrites the learner call signature (both learners and the `_update_current_state` call site), which is where HEAT-METER feeds delivered heat. ARCH-SHAPES' `_accumulate_energy`/power reader is the electric delta HEAT-METER divides by. Not shown disjoint. | row 11 |

**Recommended.** These pairs are already unordered today, because their old path ran through groups now `done`. Each adds 0 to depth.

| add | overlap |
|---|---|
| LIVESTATE after LOOP-CPU | Both edit `_resolve_away` and away.py. LOOP-CPU's own carry reads "R10-LIVESTATE edits the away override path after you". The old path ran through SAV-BASELINE and SAV-REASONS, both done. |
| LOOP-CPU after NIGHT-FOLDS | LOOP-CPU's seam (`_replay_interval` calls at 5088 and 5240) sits inside the learner methods NIGHT-FOLDS edits (hunks at 5078, 5107 and 5239). |
| PARAMS-OWNER after NIGHT-FOLDS and RATIO-ANCHOR | P3 rewrites both learner methods. P1 rewrites `_apply_house_heat_loss_scale` and `_apply_lower_floor_loss_ratio` (4806-4815) and `_apply_learner_payloads`, which are RATIO-ANCHOR's re-anchor writers. |
| ARCH-SHAPES after INPUT-STALENESS | Both edit inputs.py: patch 03 at `InputReader` L796-810, against the freshness check, plus the `_RANGE_KEYS` comment L357-360 carried to INPUT-STALENESS. |

Not resolved here (out of scope; listed for the orchestrator):
- R10-THERMAL-POWER-OPTION (hot_files: flow_meter.py, config_flow.py, const.py, coordinator.py, sensor.py) has no `after` edge but shares files with HEAT-METER.
- R10-LEARNER-DEFAULT (coordinator.py, thermal_model.py) has no `after` edge either.
- CURRENCY may touch `self.currency` in `_update_current_state` L6053 (LIVESTATE's seam) if it moves currency resolution there.

## 4. Architect-note and brief amendments

The note text appears twice for every group: in `architect_note`, and again as an older copy inside `brief` ("position N of 24"). Amend both.

**Every group whose own `after` changes** (RATIO-ANCHOR, INPUT-STALENESS, CURRENCY, LOOP-CPU, CONFIG-NOTICES, PARAMS-OWNER, ARCH-SHAPES, LEARNER-ETA, HEAT-METER, LIVESTATE if the recommended edge is applied):
- Replace `Start from the previous group's merge, and re-run fixer.md steps 2-8 after any rebase.` with `Start from main; your merge follows <predecessors> if both are in one pitch. Re-run fixer.md steps 2-8 after any rebase.`
- Groups left with no coordinator predecessor use `Start from main.` instead.
- Replace the coordinator.py clause `coordinator.py (position N of 25; before you: ...; next: ...)` with `coordinator.py (seam-ordered; before you: <new after list>; after you: <groups now after this one>)`.

| group | coordinator.py clause, new text |
|---|---|
| R10-RATIO-ANCHOR | `before you: none; after you: R10-HEAT-METER` (+ `R10-PARAMS-OWNER` if recommended). Start from main. config_flow.py clause unchanged. |
| R10-INPUT-STALENESS | `before you: none; after you: R10-HEAT-METER` (+ `R10-ARCH-SHAPES` if recommended). Start from main. |
| R10-CURRENCY | `before you: none; after you: none`. Start from main. |
| R10-LOOP-CPU | `before you: none` (or `R10-NIGHT-FOLDS` if recommended); `after you: R10-LIVESTATE` if recommended. |
| R10-CONFIG-NOTICES | `before you: none; after you: none`. Start from main. |
| R10-PARAMS-OWNER | `before you: R10-LIVESTATE` (+ `R10-NIGHT-FOLDS, R10-RATIO-ANCHOR` if recommended); `after you: R10-HEAT-METER`. |
| R10-ARCH-SHAPES | `before you: R10-LIVESTATE, R10-FREQ-DEFROST` (+ `R10-INPUT-STALENESS`); `after you: R10-HEAT-METER`. |
| R10-LEARNER-ETA | `before you: none; after you: R10-HEAT-METER`. Start from main. |
| R10-HEAT-METER | `before you: R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-LEARNER-ETA, R10-INPUT-STALENESS, R10-RATIO-ANCHOR; after you: R10-COP-GATE`. |
| R10-LIVESTATE | `before you: R10-SCORES` (+ `R10-LOOP-CPU`); `after you: R10-PARAMS-OWNER, R10-ARCH-SHAPES`. The old `next: R10-CONFIG-NOTICES` goes. |

**Earlier side.** Only the `next:` list changes:
- R10-NIGHT-FOLDS: `next: R10-RATIO-ANCHOR, R10-INPUT-STALENESS` becomes `next: none` (or `R10-LOOP-CPU, R10-PARAMS-OWNER` if recommended).
- R10-FREQ-DEFROST: `next: R10-LOOP-CPU, R10-SAV-BASELINE` becomes `next: R10-ARCH-SHAPES`.
- R10-SCORES: unchanged (`next: R10-LIVESTATE`).
- R10-ADVISOR: unchanged.
- R10-LEARNER-ETA's old predecessor ARCH-SHAPES: `next: R10-LEARNER-ETA, R10-HEAT-METER` becomes `next: R10-HEAT-METER`.

NIGHT-FOLDS, FREQ-DEFROST and ADVISOR are in flight. For them the edit is cosmetic and does not change their seats' work.

**One more brief, besides the notes:** R10-LOOP-CPU's carry "(2) R10-LIVESTATE edits the away override path after you" is true only if the recommended LIVESTATE after LOOP-CPU is applied. Otherwise strike it.

## 5. Uncertainties

- The seams of RATIO-ANCHOR, INPUT-STALENESS, CURRENCY, LOOP-CPU, ADVISOR, SCORES, LEARNER-ETA, HEAT-METER and COP-GATE are inferred from the brief, the note and grep. They have no patch or branch. The others are prototype patches, which a fix may not follow exactly.
- A drop can therefore turn out wrong. The train stops at the first refusal and returns that PR to its fixer: one rework, not a silent merge (K7 Change, last bullet). Semantic (non-textual) coupling is not caught that way; those are the edges I kept.
- RATIO-ANCHOR's snapshot-restore path may touch `_async_save_restored` (L1084-1090). NIGHT-FOLDS inserts helpers immediately above it, an adjacent-hunk risk for a textual conflict only.
