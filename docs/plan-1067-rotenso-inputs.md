# Wave 1067 — Rotenso Windmi inputs, disinfection lever, Modbus frequency and pre-fill

<!-- The wave plan for issue #1067, written before execution and kept as
written. It is the plan of record for this work, not a report: where it and
the branch disagree, the branch and the handover comment on the pull request
are what happened. The status block below is the only text added after the
fact. -->

## Status, written when the remote session handed over

Three of the nine groups below reached the branch, the third of them
incomplete. Read the handover comment on pull request #1068 for what is
done, what is owed and the traps the session hit; read
`.claude/workflows/carry-1067.json` before writing any solver code.

**One premise of this plan is refuted.** Group G2's brief below, and issue
#1067 itself, claim that judging the efficiency reference against a measured
supply temperature stops the learned scale absorbing the weather curve. It
cannot, and that was measured rather than argued: the scale's own expression
does not contain the reference curve. What the learner half ships is the
supply and return slots, the flow-bias learner and the bias itself; the
credited COP and the degradation baseline are unchanged from main.
Only pricing the lift, group G3, can stop the walk. Do not repeat the
original claim.

**The G2 brief's lift-aware reference was built, measured wrong, and reverted.**
Judging the efficiency reference at the measured supply double-counts the lift:
`_learn_measured_cop` credits `modelled_cop * commanded / measured`, so the
reference must be the COP the plan priced, and a harder lift already shows as a
larger measured power. Review round 1 of #1068 measured the credited COP 24 to
38 % low at a 55 °C supply; the owner chose to revert the reference (option 1).
What G2 ships is the two slots and the bias learner. It does not change the COP
learner, and it ships no lift arithmetic in `thermal_model.py`. The degradation
watch keeps its base behaviour on a supply change, and making it lift-aware is
carried to G3 in `.claude/workflows/carry-1067.json` with the measured traps.
The G2 brief below is kept as written; this block overrides its reference,
extraction, test and mutation bullets.

Two further deviations from the plan as written. The wave ran as sequential
commits on one branch with one pull request per repository, because the
executing session was pinned to a single branch, so the per-group branches
and merges never existed. And the roster file the plan asks for was
deliberately not committed, because the brief linter refuses a carry filed
at an issue a roster already covers.

---

Line numbers below are as of `origin/main` at `e602e65` (2026-09-16). Every brief re-anchors them at the wave's merge base; `brief_lint.mjs` refuses a `path:line` whose anchor phrase has moved.

## Context

Issue [#1067](https://github.com/tvofi/heatpump_optimizer/issues/1067) evaluated the 25 Tuya data points `tuya_heat_pump` exposes for the Rotenso Windmi (model file `custom_components/tuya_heat_pump/models/000004k4z6.py`, tvofi/tuya_heat_pump) against the optimizer's optional entity slots. Ten map today with nothing to build. Three do not, and each is a learner blind spot on this unit: the pump's two electric heaters (no power meter on the Tuya surface, so `_detect_immersion` can never fire), the outlet and inlet water temperatures (the COP model's flow term is only ever fed from a buffer tank while a valve throttles), and night mode (capacity capped, plan unaware). The owner added two more: the DHW disinfection switch as an actuation lever for the legionella cycle, and the GCHV Modbus package's compressor-frequency sensor (that package has no writable frequency register, so observe mode must work from a sensor alone). Finally an options-flow entry that pre-fills option values from the Modbus package's entities.

Executed by an Opus 5 orchestrator with Opus/Sonnet/Haiku seats under the repository's own governance: `CLAUDE.md`, `.claude/rules/*.md`, `tools/audit/briefs/{orchestrator,fixer,fix-review}.md`, a roster `.claude/workflows/wave-1067-groups.json` linted by `brief_lint.mjs` and dispatched by `web-fix-wave.js`.

## Owner decisions taken during planning (2026-09-16)

1. **C1 scope: learner half AND the solver term** (gated option, default off; goldens byte-identical when off).
2. **Pre-fill UI: an options-flow menu entry**; inferred values are suggested values the user edits before saving.
3. **Disinfection switch: opt-in mode selector** (observe/control), mirroring `freq_control.py`.
4. **Ratchet: measured raises pre-authorised for this wave.** All 24 budgets in `tests/structure_budgets.json` sit at zero headroom (`PYTHONPATH=tests/hastub python3 tests/structure.py` prints `N <= N` on every row). New logic lives in new modules; the coordinator takes wiring only; each group re-records the counts it moves to the measured value, reason in the commit message, delta in the PR body, no padding. This is the "explicit confirmation before the branch is pushed" that `CLAUDE.md` rule 2 requires; each PR body cites this section.
5. **Stage 0 in tvofi/tuya_heat_pump**: verify and fix the Modbus generator's entity-id slug mismatch before the pre-fill group.
6. **Haiku 4.5: read-only seats only** (pre-dispatch in-flight check, comment read-back verify, label hygiene, post-merge gate watch); never a fixer, reviewer or translation seat. Recorded as a routing change in `docs/plan-2026-09-open-issues.md` "Model routing".

## Design decisions the orchestrator carries into every brief

- **Coordinator wiring only, in two cheap shapes.** Module-level `def _x(coord)` helpers outside the class on the `_freq_fold_blocked` precedent (`coordinator.py:595-600`) cost no `coordinator_loc`, `coordinator_methods` or seam edges; new fields ride on objects the coordinator already holds (`PumpSignals`, learners) so no new `self._attr` is born where avoidable. Never add a statement to `_learn_measured_cop` (`coordinator.py:3347-3490`, 140 lines against the 150 monster limit): new guards are an `or` on the existing `if self._immersion_active:` at `:3395`.
- **New modules are HA-free** (no `homeassistant` import at any level), so `docs/architecture.md`'s HA-boundary list does not move; each new module is added to that file's module map and opening counts (asserted by `tests/entities.py:909-925`) and enters `tests/closures.json` (orphan rule `tests/closure.py:507`, asserted at `tests/entities.py:10130-10134`). On a same-repo PR the `closures` job prints `UNDER-SCOPED` and `closures-autofix` pushes `ci: re-record closures`; per `.claude/rules/ci-autofix.md` the fixer waits for that commit and reads the summary line. `dead_top_level_symbols` is 0: every new symbol has a caller.
- **New keys are options-page slots, not card slots.** They stay out of `topology._SLOTS` (`topology.py:101-150`) on the `CONF_COMPRESSOR_FREQ_ENTITY` precedent (`config_flow.py:1388-1389`), so `ASSIGNABLE_KEYS` stays at 21 and the documented count at `docs/configuration.md:748-761`, its live harness `tools/audit/round4/D6/claims.py:434-442` (executed by `tests/harness_headers.py`) and `_IDENTITY_ENTITY_KEYS` (`config_flow.py:424-440`, first screen only) are untouched. Card assignment of the new slots is a recorded deferral in `docs/HANDOVER.md`.
- **Every new option key touches, always:** `const.py` (key, and for an entity slot an `INPUT_MAX_AGE_MINUTES[...]` row with its justification in the block at `const.py:1246-1312`); a `_F(...)` row in `config_flow.py` `_OPTION_FIELDS` (`:1364-1560`; `_OPTIONAL_ENTITY_KEYS` derives at `:2406-2413`); `strings.json` `options.step.<page>.data` and `data_description`; `translations/en.json` byte-identical; `translations/sv.json` genuinely translated; a `docs/configuration.md` table row (`tests/entities.py` asserts every shipped options field is named there); and a re-record of `tests/golden/config_flow.json` with `PYTHONPATH=tests/hastub python3 tests/golden.py --record --only config_flow` (a schema fixture; no scenario name contains that substring, so nothing value-bearing moves; the PR body says so).
- **Byte-identity when unset** is every group's acceptance bar: `env_drift.py --all` against the merge base reports no drift except a newly recorded fixture; both claim files stay byte-identical to `origin/main` (`.claude/rules/claim-files.md`).
- **Per group**: own worktree from `origin/main`; ≤ ~400 production lines; failing test first importing the production symbol; mutation proof on the predicate; null control per quantified claim; scoped gate via `tests/closure.py select` (lease only when `scope.run` names `tests/stress.py` or `MODE: FULL`; `thermal_model.py`'s closure does); `python3 tests/structure.py` before every push with the re-record reason in the commit; PR body per `.github/PULL_REQUEST_TEMPLATE.md` pushed through `tools/audit/push.sh`; `Part of #1067`, closes nothing until G8; a Delivery-status row written before handoff; adversarial `fix-review` from a detached worktree; merge commit never squash; `VERSION`, manifest and `RELEASE_NOTES.md` heading untouched.
- **Roster mechanics**: `serial: true` (the groups share `const.py`, `config_flow.py`, `strings.json`, `docs/configuration.md`); a group with `after` starts with `git merge origin/main`, never rebase; briefs name planned symbols in prose, never backticked (they exist at no tag); no literal metric values; reviewer never ranks below fixer (`web-fix-wave.js:224`). G0 lives in another repository, so the orchestrator dispatches it directly rather than through `web-fix-wave.js`.

## Groups

| group | scope | after | fixer / reviewer | effort | fixture | est. prod lines |
|---|---|---|---|---|---|---|
| W1067-G0 | tuya_heat_pump: Modbus generator slug fix | — | sonnet / sonnet | medium | n/a | ~15 |
| W1067-G1 | C2 + C3 flag slots, learner stand-downs, booster → immersion events | — | opus / opus | high | false | ~180 |
| W1067-G2 | C1(a) supply/return slots and the flow-lift bias learner; the COP reference stays the plan's curve (see status) | — | opus / opus | high | false | ~260 |
| W1067-G3 | C1(b) solver term, new golden | G2 | opus / opus | high | true (new fixture only) | ~120 |
| W1067-G4 | C3 plan half: silent-mode window + derate through `power_caps_extra` | G1 | opus / opus | medium | false | ~160 |
| W1067-G5 | D: disinfection switch, guard injection, mode selector | — | opus / opus | high | false | ~200 |
| W1067-G6 | E: sensor-only frequency observe, Hz bounds, control validation | — | opus / opus | medium | false | ~120 |
| W1067-G7 | F: Modbus pre-fill module and options page | G1, G2, G4, G6 | opus / opus | high | false (config_flow.json only) | ~350 |
| W1067-G8 | close-out: Delivery-status, roster `resume`, HANDOVER, #201, close #1067 | G7 | sonnet / sonnet | low | false | 0 |

### W1067-G0 — generator fix (tvofi/tuya_heat_pump, Sonnet)

- **Defect**: `raw_sensor()` at `tools/gen_gchv_package.py:333-335` names the entity `HP GCHV R404 (0194H)`, which Home Assistant slugs to `sensor.hp_gchv_r404_0194h`, while `raw_entity()` at `:62-63` emits `sensor.hp_gchv_r404` for every template reference, so every template entity resolves `unavailable`. Fix `raw_entity()` to slug the name actually emitted (a `{addr: hex}` map filled by `raw_sensor`/`ensure_raw` at `:358-363`); do **not** rename the sensors, because the owner's entity registry pins the existing ids by `unique_id`. Regenerate `docs/modbus/rotenso_windmi_gchv.yaml`.
- **Failing test first**: that repo has no `tests/`; add `tools/test_gen_gchv_package.py` importing `gen_gchv_package.build` and asserting every `states('sensor.…')` reference in the built templates names an emitted sensor's slug. Mutation: revert `raw_entity` → the check lists every raw reference.
- **Verification on the owner's install** (Haiku read-only seat): list `sensor.hp_gchv_r4*` ids from `hass.states`; that is the failing-before evidence.
- **Null control**: run the generator at the merge base and diff; only `states()` strings move.

### W1067-G1 — C2 + C3 flag slots (learner half)

- **Keys**: space backup heater (Tuya dp 15), DHW tank booster (dp 7), capacity-limited (dp 110); `INPUT_MAX_AGE_MINUTES = 30.0` each, beside `const.py:1312`, with the defrost horizon's rationale (`:1300-1306`). Config-flow rows on `entities_pump` after `config_flow.py:1394`, accepting the flag domains of `topology.py:83` through a public name (the fixer chooses and says why).
- **Mechanism, decided**: extend the immersion latch, not `freeze_reason`. The freeze (`pump_signals.py:106-108`, consumed by `_learning_frozen` at `coordinator.py:5152-5220`) is plant-wide and would stop the heat-loss learner during the cold snaps that carry the most information; resistive heat is real heat into the house, only the electrical attribution is wrong. So: a nested frozen aux-signals dataclass on `PumpSignals` (fields for the three flags, a derived `resistive_heat`, and a rising-edge `dhw_booster_started` computed from a new `previous=` kwarg on `read()` at `pump_signals.py:222`, resolved in a separate helper so `read()` stays under CC 25). Coordinator call site `:5052-5056` passes `previous=self._pump_signals`.
- **Consumers, one-token edits**: `coordinator.py:3395` gains `or resistive_heat or capacity_limited` (this covers the capacity-envelope fold and COP health, which hang off the learner's tail at `:3486-3489`); `:3056` gains `or resistive_heat` only (C3 must not enter here: measured power stays the replay input); `_freq_fold_blocked` `:595-600` gains both. `_detect_immersion` `:7727-7775` appends one ISO timestamp to `_immersion_events` on `dhw_booster_started` (rising edge, so a booster left on is one event, matching the detector's one-event-per-latch), which `_immersion_dhw_margin` `:7943` then counts under `CONF_IMMERSION_FEEDBACK_ENABLED` (default off, byte-inert). Settlement (`:9158`) and the start counter (`:9310`) stay meter-driven; the docstring says so.
- **Tests** (`tests/features.py`): `pump_signals.read` over the existing fake reader → aux flags true/false/None and the rising edge once; coordinator harness (pattern `:4283-4317`): booster on → `_cop_samples` and `_capacity_envelope` unchanged; capacity-limited on → COP/envelope/frequency folds skip while `_interval_space_power()` still returns the measured figure; `_detect_immersion` (pattern `:11617`) → exactly one event across three booster-on cycles. `tests/entities.py`: extend the `_SIGNAL_KEYS` loops (`:4269-4340`) for page, `vol.Optional`, `_ENTITIES_PUMP_KEYS` and round-trip clear, but split the `ASSIGNABLE_KEYS` assertion into a card-slot subset with the stated reason; the `INPUT_MAX_AGE_MINUTES` coverage rule (`:5610-5617` pattern).
- **Mutation proof**: delete the `or` at `:3395` → booster COP test red; delete the event lines → events test red; delete the `_freq_fold_blocked` clause → frequency test red.
- **Null control**: slots unset → aux fields all `None`, `resistive_heat` False; `env_drift.py --all` identical; the four v5.3.0 fixtures unchanged.
- **Metrics expected to move**: `coordinator_loc` (about +6), `cut_grid` (+1, `_interval_space_power` is a `power`-bucket method), possibly `cut_learning`.

### W1067-G2 — C1(a) supply and return slots, flow-lift learner

- **Keys**: supply water temperature (dp 10), return water temperature (dp 101); `INPUT_MAX_AGE_MINUTES = 30.0`; `_F("entities_pump", …, _entity_of('sensor', 'temperature'))`. Docs warn that the return slot is the pump-loop return, not `floor_return_temp_entity`'s floor-loop return behind a buffer or valve (`coordinator.py:4925` seeds the slab from that one).
- **New module** `flow_lift.py` (HA-free): a learner with `observe(supply, curve_flow)` → EWMA bias clamped ±15 K, `samples`, `as_dict`/`from_dict` on the `FrequencyMap` model (`freq_control.py:53`), `note(supply, ret)` holding the last readings, and one `curve_flow(model, outdoor, indoor_target)` = `flow_target_for_indoor` (`thermal_model.py:1525`), the single function G3 must reuse so the bias is learned against the curve the solver applies.
- **thermal_model.py**: extract the Carnot block `:1393-1424` into a private helper (pure move, identical arithmetic; the duplication ratchet refuses a copy) and add `compute_cop_at_flow(outdoor, flow_temp, humidity=None)` applying the lift unconditionally, then the 1.0 floor.
- **Coordinator wiring**: `self._flow_lift` (+1 attr, near `:1858`); read both slots after the buffer read `:5006-5008` and `note()` them (+4 lines, no new `if`); `_cop_reference_curve` `:3335` → `compute_cop_at_flow(outdoor, supply)` when a supply reading exists (one ternary); a module-level `_fold_flow_lift(coord, now)` called beside `_observe_frequency` (`:8753`), gated on the same duty floor, not frozen, not `resistive_heat`, space-dominant split (`_commanded_split` `:2974`, `_COP_CURVE_SHARE` `:3292`); persistence `"flow_lift"` in `_thermal_learning_payload` (`:2621-2697`), parsed in `_load_t4b_learners` (`:2575-2619`), reset to inert in `_apply_learner_payloads` (`:8283-8294`).
- **Tests** (`tests/features.py`): learner at both ends (zero evidence → bias 0.0; clamp end); the reference COP at a measured 55 °C supply is below the bare curve and `cop_scale` moves less per sample than at 35 °C, with the null (slot unset → `_cop_scale` trajectory identical to the merge base); snapshot restore resets to inert; scalar grid of `compute_cop` identical before and after the extraction (`diff … && echo IDENTICAL`).
- **Mutation proof**: remove the `compute_cop_at_flow` call → lift test red; remove the reset in `_apply_learner_payloads` → restore test red.
- **Metrics**: `coordinator_attrs` +1, `coordinator_multiassigned_attrs` +1, `coordinator_loc` about +12, `cut_learning` (+refs); `docs/architecture.md` map and counts.

### W1067-G3 — C1(b) solver term

- **Option**: a boolean, default off, on the `building` page beside the valve fields; `async_step_building` (`config_flow.py:2700-2735`) refuses it when the valve mode throttles (error `flow_curve_needs_direct_plant`, shape of `flow_target_needs_two_zone` at `:2721-2727`).
- **Where the flow temperature enters the horizon COP** (all call sites, not only the cited ones): scalar steps `thermal_model.py:1866` and `:1949-1953`; batch twin `_batch_cop` `:2439-2502` called at `:2655` and `:2814`; optimizer valuations `optimizer.py:1925`, `:1929` (→ `thermal_model.py:1445-1472`), `:6200`, `:6363`; coordinator `:8038`, `:10117`, `:10191`; the learner reference `:3335`. Gate today: `cop_flow_carnot` set once at `thermal_model.py:916` from `mixing_valve.is_throttling`; scalar applies above `cop_flow_reference_temp` (`:1393-1395`), batch mirrors with `np.where` (`:2474-2495`).
- **Design: substitute inside the law, not at call sites.** New `ThermalParameters` fields (near `:363-367`): `flow_curve_cop` (bool), `flow_curve_bias`, `flow_curve_indoor_target`; `from_config` (`:873-917`) sets `flow_curve_cop = option and not throttling` and `cop_flow_carnot = throttling or flow_curve_cop`. In `compute_cop` (`:1352`): when `flow_temp is None and flow_curve_cop`, `flow_temp = flow_target_for_indoor(indoor_target, outdoor) + bias`. Twin in `_batch_cop`: fill `T_buf` with the curve flow and set the eligibility flag; extend the scalar/batch parity test to the option-on case. `compute_cop_dhw` (`:1474-1490`) calls an unlifted base so DHW is not double-penalised. The bias is pushed per cycle from the G2 learner beside `params.dhw_ready_margin_c` at `coordinator.py:2184` (one line). One-sided lift semantics (above reference only) are kept for batch parity; the docstring records the trade-off.
- **Golden**: new scenario `direct_flow_carnot` in `SCENARIOS` (`tests/golden.py:365`) via `make(config_overrides=…)` (`:286-298`), name sharing no substring with any fixture, recorded with `--record --only direct_flow_carnot`; every existing fixture byte-identical; `fixture: true` in the roster for the new file only; claim files untouched (a new fixture is not drift).
- **Tests**: option-on parity grid (`np.array_equal`), option-off identity, DHW base unchanged with the option on; plan cost at −10 °C rises with the option on and a +5 K bias, with bias 0 as the null.
- **Mutation proof**: drop the batch twin → parity red; drop the `from_config` gate → throttled-plant test red.
- **Metrics**: coordinator +1 line; `compute_cop` CC 9→11, `_batch_cop` 8→10, both under 15. `stress.py` is in this closure: take the lease.

### W1067-G4 — C3 plan half (silent-mode window and derate)

- **Options**: a window string `HH:MM-HH:MM` (validated and parsed with the DHW window helpers `dhw_schedule.parse_windows` and the validator `config_flow.py:2205`/`:2633` use, which handle midnight wrap) and a derate fraction 0.3–1.0, default 1.0 (inert). Page: the fuse-and-peak-guards page.
- **New module** `silent_mode.py` (HA-free): `caps(start_time, n_steps, dt_hours, windows, fraction, p_max) -> ndarray | None`, `None` when fraction ≥ 1.0 or no window, floored at `CAPACITY_FLOOR_FRACTION` like `_capacity_caps` (`coordinator.py:8011-8043`) so the derate can never starve the house.
- **Wiring**: compose by `np.minimum` with the envelope caps at `coordinator.py:4540-4545` (+4) and in the what-if path `:10315-10319` (+3), both reaching `optimizer.optimize(power_caps_extra=…)` (`optimizer.py:2548`). The Tuya switch (G1's capacity-limited flag) covers the learner half; the window covers the forecast half because the schedule lives in the pump, not on Tuya.
- **Tests**: window across midnight; a DST day (`tests/dst_checks.py` pattern); fraction 1.0 → `None` (null); composition with envelope caps is a minimum, not a product; optional new golden `silent_mode_window`.
- **Mutation proof**: delete the `np.minimum` composition → the in-window plan-power test red.
- **Metrics**: `coordinator_loc` about +7 inside two methods already over 200 lines.

### W1067-G5 — D disinfection switch

- **Keys**: switch entity (`switch`, `input_boolean`; unbounded age on the external-heat flag rationale at `const.py:1287-1297`) and a mode selector reusing `FREQ_MODE_OBSERVE`/`FREQ_MODE_CONTROL` (`freq_control.py:34-35`), default observe, on `hot_water_tank`; validation: control without an entity → `disinfection_control_needs_entity`.
- **New module** `disinfection.py` (HA-free): a command object taking an injected service callable, `command(on, *, dhw_blocked) -> bool`; memo written only after a successful call (mirror `_async_set_pump` `coordinator.py:2407-2425`); refusals: mode not control → no-op; no entity → no-op; ON while DHW is mode-blocked → refuse (OFF always allowed); exception → warn, return False, memo untouched so the next tick retries.
- **Injection**: `LegionellaGuard.__init__` (`legionella.py:47-60`) gains a `disinfect` callable stored like `_action` (`coordinator.py:1631`); the coordinator passes it at `:1626-1632` (+1 attr, +2 lines). Edges: ON at the boost-start edge `legionella.py:254-256`, OFF at the close `:287-289` and on the disabled early return `:210-214` when a boost was active; `check_mode_block` (`:528`) stores `dhw_blocked` so the ON edge uses the same reading `coordinator.py:4578` delivers. A blocked ON is logged once; the existing `dhw_legionella_mode_blocked` notice (`:557-586`) already explains it. A failed write raises a new non-persistent repair `dhw_disinfection_write_failed` via `setpoint_check.create_issue` (imported at `legionella.py:38`), cleared on the next success; strings `issues` block and sv.
- **Observe mode**: the switch is read through `read_bool` and published in the legionella attributes (`coordinator.py:6420`); evidence before actuation, the frequency stage's shape.
- **Tests** (`tests/features.py`, on the existing legionella harness that injects `action=`): ON exactly once at the start edge; OFF once at close and once at the `DHW_LEGIONELLA_BOOST_MAX_HOURS` bound; no ON while blocked; memo not written on a raised error and the write retried; observe → zero calls (null). `tests/entities.py`: page round-trip and the issue-key translation roster.
- **Mutation proof**: remove the ON call → start-edge test red; remove memo-after-success → retry test red.
- **Metrics**: `coordinator_attrs` +1, `coordinator_loc` +3; `async_track_cycle` stays under 200 lines (165 today, keep additions under 35).

### W1067-G6 — E sensor-only frequency observe

- **Keys**: Hz min and max numeric options, defaults 20.0 and 120.0 (today's fallbacks at `coordinator.py:9761-9762`), two `_F` rows in the `compressor` group (`config_flow.py:1388-1390`).
- **Move the resolution into `freq_control.py`**: `resolve_reading(number_state, sensor_state, hz_min_opt, hz_max_opt) -> (reported, hz_min, hz_max, configured)`; `_freq_entity_reading` (`coordinator.py:9745-9784`) shrinks to two state lookups plus the helper (net coordinator decrease). Rules: number present → range from its attributes, sensor overrides the value (unchanged); number absent, sensor present → value from the sensor, range from the options; neither → unconfigured. `_freq_mode` (`:9785-9800`): unconfigured only when neither is set; control requires the number. `_freq_view` (`:9919-9955`) gains `"source": "number" | "sensor"`. `sensor.py:2542-2544`: keep the `compressor_frequency_entity` waiting key, relabel it to "a compressor frequency number or sensor".
- **Validation**: `async_step_entities_metering` (`config_flow.py:2575-2587`) refuses control without a number (`freq_control_needs_number`).
- **Tests**: `resolve_reading` table; `_freq_view()` sensor-only → observe with `range_hz` from the options and a learning map; control + sensor-only → the flow refuses; advisor `_waiting_for`. Null: number+sensor installs produce identical `_freq_view()` dicts before and after.
- **Mutation proof**: drop the sensor-only branch → observe test red; drop the validation → flow test red.

### W1067-G7 — F Modbus pre-fill

- **New module** `modbus_prefill.py` (HA-free): `candidates(prefix)` listing both slug spellings per register (`sensor.{p}_gchv_r404` and `sensor.{p}_gchv_r404_0194h`, first that resolves wins); `snapshot(get, prefix)` using only `.get` so `FakeStates` (`tests/harness.py:90-98`) drives it; `infer(snapshot, prefix, current_options) -> dict` (absent or non-numeric → key omitted; entity slots suggested only when empty); `notes(snapshot)` (backup-heater type register 601 ≠ 7 → "the auxiliary-heater slots are worth mapping"; "nothing about the house or plant is inferable").
- **Inference table** (register → key → formula; the fixer reads value tables from `tools/gen_gchv_package.py`, never guesses): `sensor.hp_unit_capacity` kW thermal ÷ `heat_pump_cop_nominal` → `heat_pump_max_power`; r404×0.1 → `dhw_setpoint`; r405×0.1 → `dhw_legionella_temperature`; r406×0.1 → `dhw_min_temperature`; r712/r713 (`hh*256+mm`) → `dhw_windows` only when r711 ≠ 0; r518/r519 → G4's window; `7 // popcount(r714)` when r714 ≠ 0 → `dhw_legionella_interval_days`; r4109 = water-temperature control → `mixing_valve_write_target_kind` and `space_setpoint_unit` = flow; entity slots when empty: `outdoor_temp_entity` ← `sensor.hp_outdoor_air_temperature`, `dhw_temp_entity` ← `sensor.hp_dhw_tank_temperature`, G2's supply/return ← `sensor.hp_leaving_water_temperature_t1` / `sensor.hp_entering_water_temperature_tw_in`, `compressor_freq_sensor` ← `sensor.hp_actual_compressor_frequency`, G1's capacity-limited flag ← the night-mode-active binary sensor when it resolves.
- **Flow**: one `_P("modbus_prefill", …, _ADVANCED)` row (`config_flow.py:1338-1359`) and one `async_step_modbus_prefill` handler (`registry_drives_every_page`, `tests/config_flow_steps.py:3328-3355`, requires handlers = pages). Phase 1: `_page_schema` with a single stored prefix row (default `hp`). Phase 2: compute `infer()`, keep it on the flow instance, render a FLAT `_options_schema` of `vol.Optional(key, description={"suggested_value": v})` fields with the notes in `description_placeholders` (flat because suggested values skip sectioned fields, `:1288`, `:1585`). Phase 3: drop `None`/`""`, then `_save_or_menu` (`:2455-2469`) returns to the advanced menu.
- **Page count 21 → 22**: README.md "menu of 21 pages" (pinned by `tests/entities.py:585-600`), `docs/configuration.md` "twenty-one" (`:9`, `:204`), `strings.json` advanced `menu_options` and the new step block, sv.
- **Coverage 100 %** (`tests/coverage_budgets.json:7`, ratchet `tests/coverage_ratchet.py`): a three-phase walk in `tests/config_flow_steps.py` beside `registry_walk_recurses` (`:3437`) with `FakeHass` states populated in both spellings, blanks, a close-save, an empty snapshot; `infer()` unit tests in `tests/features.py` from a snapshot built out of the yaml's unique ids; `tests/entities.py` page pin, docs field names, menu strings. No pragma: the `pragmas` count is a ratchet too.
- **Mutation proof**: reduce the spelling list to one → both-spellings test red; write blanks → blank-not-written test red.

### W1067-G8 — close-out (Sonnet)

Delivery-status rows verified against measured `origin/main`, roster `resume` flips, `docs/HANDOVER.md` decisions (C4 deferral: the two-zone model has one flow temperature at `thermal_model.py:1952` and no per-zone emitter law, so a zone-2 supply slot would feed nothing; card-slot deferral; one-sided lift semantics), one #201 comment via `gh_comment.py` with read-back, `Closes #1067`. No stamp.

## Verification

Per group:

```
D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt" "$D/scope.run"
PYTHONPATH=tests/hastub python3 <each script scope.run names>
PYTHONPATH=tests/hastub python3 tests/structure.py            # --record with the reason in the commit message; exit 2 = unrecorded improvement
python3 tests/coverage_ratchet.py                             # config_flow stays 100.00
PYTHONPATH=tests/hastub python3 tests/golden.py --record --only config_flow    # any group that changes a page
PYTHONPATH=tests/hastub python3 tests/golden.py --record --only direct_flow_carnot   # G3 only
PYTHONPATH=tests/hastub python3 tests/env_drift.py --all      # no unclaimed drift
git diff $(git merge-base origin/main HEAD)...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt   # empty
```

Wave: `node .claude/workflows/brief_lint.mjs` on the new roster (no args runs the acceptance fixtures too); `node .claude/workflows/check-wave-script.mjs` only if `web-fix-wave.js` is edited (not planned); after each merge, `main` green, the Delivery-status row present, the roster `resume` matched to the merge SHA.

## What refuses a PR (checklist for every brief)

- A new module absent from `tests/closures.json` (orphan) or from `docs/architecture.md`'s map and counts.
- Any top-level symbol without a caller (`dead_top_level_symbols` 0); a function-scope import (`local_imports` 7); a module importing more than 50 names from `.const` beyond the three that already do (`const_modules_over_50` 3).
- A `_F` row without a page render or a handler without a `_P` row; `_learn_measured_cop` crossing 150 lines; `pump_signals.read` crossing CC 25; `async_track_cycle` crossing 200 lines.
- An option absent from `docs/configuration.md`; `en.json` ≠ `strings.json`; an untranslated `sv.json` copy; an issue key missing from a translation.
- A roster brief that backticks a planned symbol, states a literal metric value, or cites a `path:line` whose anchor moved.
- A PR body missing Head, Mutation proof (check names), Null control, Figures (commands), Red checks, Forward-carry, Friction; a missing Delivery-status row; a head moved after handoff.

## Orchestrator's first actions

1. Owner decisions 1–6 above are recorded verbatim in `docs/plan-2026-09-open-issues.md` (a new wave section, Delivery-status rows for G0–G8, the Haiku routing line) and on #201 with read-back.
2. Write `.claude/workflows/wave-1067-groups.json` (header as `wave-5-groups.json`: `fork`, `session`, `serial: true`, `struck: []`, `groups`), briefs carrying the seams above re-anchored at the fork SHA; `node .claude/workflows/brief_lint.mjs` clean, exit code read.
3. Dispatch G0 directly in tvofi/tuya_heat_pump; then run the roster serially through `web-fix-wave.js`; Haiku seats for the pre-dispatch in-flight check and every comment read-back.
4. Each merge: Delivery-status row, roster `resume`, HANDOVER only in G8. Stamp at the orchestrator's discretion after G8, never in a branch.

