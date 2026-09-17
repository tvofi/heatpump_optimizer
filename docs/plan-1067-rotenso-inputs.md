# Wave 1067 — Rotenso Windmi inputs, disinfection lever, Modbus frequency and pre-fill

<!-- The wave plan for issue #1067, written before execution and kept as
written. It is the plan of record for this work, not a report: where it and
the branch disagree, the branch and the handover comment on the pull request
are what happened. The status block below, and the owner decision of
2026-09-17 with the two groups it added (W1067-G7b and the post-wave follow-on W1067-POST1), are the only
text added after the fact. -->

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

## Owner decision taken during execution (2026-09-17)

Given in chat with the orchestrator, verbatim: "I want A, and then B later in the plan".

7. **A is W1067-G7b**, split G7b-1 to G7b-3: the pre-fill page also takes a heat-pump device, reads that device's entities from Home Assistant's entity registry, and feeds them to G7's suggestion logic unchanged. It runs after G7 merges and before G8's close-out. The owner's same-day input widened it to any device source (tuya_heat_pump, Tuya Local, Local Tuya, brand-specific integrations), with a fuzzy fallback that matches by type, unit and name and says so on the page. **B is W1067-POST1**: offering the pre-fill when a heat-pump device is added. It is a follow-on after G8, outside wave 1067's close-out. G8 still closes #1067, and B does not hold it open. The owner confirmed that placement the same day, answering yes to the orchestrator's proposal. B gets its own issue or tracking entry when it is started, and none is filed before then.

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
| W1067-G7b-1 | A: device pre-fill (owner decision 7): resolver interface, tuya_heat_pump table, registry stubs, fixture script, flow | G7 | opus / opus | high | false (config_flow.json only) | ~180 |
| W1067-G7b-2 | A: tuya_local table and the localtuya decision, generated fixtures | G7b-1 | opus / opus | medium | false | ~80 |
| W1067-G7b-3 | A: fuzzy fallback resolver (type, unit, name; disclaimer), labelled corpus, measured thresholds | G7b-2 | opus / opus | high | false (config_flow.json only) | ~150 |
| W1067-G8 | close-out: Delivery-status, roster `resume`, HANDOVER, #201, close #1067 | G7b-3 | sonnet / sonnet | low | false | 0 |
| W1067-POST1 | post-wave follow-on, B: offer the pre-fill when a heat-pump device is added, with a global off switch (owner decision 7) | G8 | opus / opus | high | false (config_flow.json only) | ~220 |

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
- **Coverage 100 %** (`tests/coverage_budgets.json:7`, ratchet `tests/coverage_ratchet.py`): a three-phase walk in `tests/config_flow_steps.py` beside `registry_walk_recurses` (`:3545`, re-anchored at `c8eb0f6`) with `FakeHass` states populated in both spellings, blanks, a close-save, an empty snapshot; `infer()` unit tests in `tests/features.py` from a snapshot built out of the yaml's unique ids; `tests/entities.py` page pin, docs field names, menu strings. No pragma: the `pragmas` count is a ratchet too.
- **Mutation proof**: reduce the spelling list to one → both-spellings test red; write blanks → blank-not-written test red.
- **Forward carry from W1067-G7b (owner decision 7, 2026-09-17)**: `infer()` must take role → entity-id resolution as an input (a role map, or a resolver function), not hardcode the prefix lookup inside itself, so G7b feeds device-resolved ids without changing `infer()`. The prefix route becomes one resolver (the both-spellings candidates) and G7b's device route another. The resolution must also carry each role's scale, or the snapshot must hand `infer()` engineering units: the r404 row is raw × 0.1, while the Tuya device's DHW set-point number already reads °C (tvofi/tuya_heat_pump `fda9bed`, `custom_components/tuya_heat_pump/models/000004k4z6.py:369-378`), so a scale fixed inside `infer()` turns a 50 °C set-point into 5.0.

### W1067-G7b — A: pre-fill from a heat-pump device, any source (split G7b-1, G7b-2, G7b-3)

Added by owner decision 7. It runs after G7 merges (`git merge origin/main`) and before G8. Line numbers in this section are as of `origin/main` at `c8eb0f6`, and upstream sources are cited at the tag and commit named with each one; re-anchor both at the merge base. The owner's follow-up input on the same day: the device may come from tuya_heat_pump, Tuya Local (`tuya_local`), Local Tuya (`localtuya`) or a brand-specific integration, so G7b is source-agnostic. It is testable in this integration at stub level; see Tests. A second owner input the same day, verbatim: "Can there be some kind of fuzzy lookup as fallback that matches by type, unit and entity name (with a disclaimer)?" The answer is yes, and it is the fallback resolver below.

**Split, recommended.** Four sources, generated fixtures, a measured fuzzy matcher, both stub registries and a config-flow walk at 100 % make one pull request too large to review in one pass.
- **G7b-1** ships the resolver interface, the tuya_heat_pump table, the stubs, the fixture script and the flow. An unrecognised device resolves nothing.
- **G7b-2** adds the tuya_local table and the localtuya decision, with their fixtures. It changes no flow code, so its review concerns only mapping.
- **G7b-3** adds the fuzzy fallback and its labelled corpus. It gets its own group, not G7b-1, because its acceptance is a corpus measurement: the thresholds are derived from that corpus, and the zero-wrong-suggestion bar is a separate review question from whether the flow and stubs are right. It follows G7b-2 so its corpus includes the tuya_local definitions.

- **Keys**: none new, if the device pick stays transient. The pick is a device selector on G7's pre-fill page, beside the prefix row. It adds no `_P` row, so the page count G7 sets does not move. Whether the pick is stored is the fixer's call, stated in the body. If stored, it is a new option key and carries every item of "Every new option key touches". If transient, the body shows that `registry_drives_every_page` (`tests/config_flow_steps.py:3438`) and the page fingerprint accept a field that is not a `_F` row. The selector is not filtered by integration, because the fallback serves any device. The prefix route stays for Modbus YAML entities: the generated package (tvofi/tuya_heat_pump `docs/modbus/rotenso_windmi_gchv.yaml`) gives them a `unique_id` and no device, so no device route reaches them.
- **Interface, new HA-free module** `device_prefill.py` (the name is the fixer's to choose). A resolver is a pure function from one device's registry records to G7's role map, where each role carries its entity id, its scale and the source that matched. A record is platform, unique_id, entity_id, original_name, translation_key, device_class, unit and state_class, as plain values. `config_flow.py` reads the registries and builds the records, so the module never imports `homeassistant`. Dispatch is by `platform`: a source table when one is registered for it, then (from G7b-3) the fallback for roles the table left empty. A source table resolves only what its own definitions prove.
- **Scale travels with the role** (the G7 forward carry above). Tuya DPs arrive in °C and the Modbus register rows are raw × 0.1, so a scale fixed inside `infer()` is wrong for every device source.
- **Source tables, each derived from that integration's own definitions at a pinned version, never typed from memory**:
  - **tuya_heat_pump** (G7b-1), tvofi/tuya_heat_pump `fda9bed`, platform `tuya_heat_pump` (`const.py:8`).
    - *unique_id*: the device-name slug, an underscore, then the model dict **key** (`binary_sensor.py:112`; the same shape at `sensor.py:103`, `switch.py:91`, `number.py:89`, `select.py:92`). It is the key, not the `code` field: `fault_description` carries `code: fault` (`models/000004k4z6.py:254-256`). The slug is built from the coordinator's `device_name`, which changes after the cloud lookup (`coordinator.py:105`, `:848`, `:868`). So the match is on (entity domain, unique_id ending in an underscore plus key), the longest key wins, and a rebuilt prefix or the entity_id is never used. `night_mode` (switch) also ends in the select key `mode`, and HA scopes unique_ids per domain (`models/enhs6o.py:58-61`).
    - *Where the meanings come from*: the device's entities come from `models/000004k4z6.py`. The generator's register rows (`tools/gen_gchv_package.py:118-134`, `:194-196`) and the yaml give the meaning each G7 role already has, and each mapping below pairs the two.
    - *Tests upstream*: that repo pins 3 of the package's 76 raw unique_ids (`tools/test_gen_gchv_package.py:164-188`, against `grep -c "unique_id: hp_gchv_r"` on the yaml) and nothing about register wiring, so no role below rests on an upstream test.
    - *Roles verified against the model file's code table (`models/000004k4z6.py:17-43`)*:
      - `outdoor_temp_entity` ← sensor `T4` (dp 105), register 1.
      - `dhw_temp_entity` ← sensor `temp_current_f` (dp 26, the tank in °C), register 206.
      - G2's supply slot ← sensor `temp_current` (dp 10, "total outlet, Midea T1"), register 4. `Tout` (dp 106, the plate outlet) is not T1 and is not mapped.
      - G2's return slot ← sensor `Tin` (dp 101, "Midea TW_in"), register 3.
      - G1's capacity-limited flag ← switch `night_mode` (dp 110). That is G1's own choice of dp, and `switch` is in `topology.FLAG_DOMAINS` (`topology.py:88`).
      - `dhw_setpoint` ← number `DHWSET` (dp 104) at scale 1.0, against register 404's 0.1 (generator `:194`).
    - *Unreachable from this device, so omitted by `infer()`'s absent rule*: registers 4102, 405, 406, 711-714, 518-519, 4109, 601 and 23. The Tuya schema has no installer parameters (`models/000004k4z6.py:51-55`). Keys `instant_heating`, `switch_microwave` and `disinfection` match G1's heater slots and G5's switch, but they are outside the role set `infer()` consumes, and widening it is a G7 change.
    - *Model scope*: other model files in that repo reuse keys such as `temp_current`, and the registry `model` is a cloud product name or a local placeholder (`coordinator.py:853-875`). So the table applies only when the device carries a key set the fixer shows is unique to `000004k4z6` among `custom_components/tuya_heat_pump/models/` at `fda9bed`, with the grep under Figures. Otherwise the fallback applies.
  - **tuya_local** (G7b-2), make-all/tuya-local tag `2026.9.1` (commit `4551357`), platform `tuya_local`.
    - *unique_id*: the device uid, a hyphen, then the slugified config id (`helpers/device_config.py:293-295`). The config id is the entity type plus the slugified entity `name`; failing that, the type plus the `translation_key`, where each `translation_placeholders` key found in that slug is replaced by the slugified value and any other placeholder value is appended with an underscore (`:328-335`); failing that, the type plus the device class; failing that, the bare type (`:323-338`). The entity property is at `entity.py:72-74`, and `has_entity_name` is true (`:49-50`).
    - *Candidate config*: `devices/fisher_water_heatpump.yaml`, a Fisher air-to-water config. tuya_heat_pump's model file says a Fisher unit shares this firmware (`models/000004k4z6.py:12-14`, tuya-local issue #1870). But this file's product id, `3gabjnrhtblg3ub6`, is not the modelId named there, so the fixer establishes which config the owner's unit matches rather than assuming it.
    - *What that file defines*: `sensor` entities "Outdoor temperature" (dp 105), "Inlet temperature" (dp 101) and "Outlet temperature" (dp 106). dp 10 and dp 26 are attributes of the `climate` entity. dp 104 and dp 107 are the `water_heater` target and current temperature.
    - *Only sensor entities can fill an entity slot*, so the verifiable roles are outdoor ← dp 105 and return ← dp 101.
    - **The two sources disagree**: tuya-local reads dp 107 as the tank's current temperature, and tuya_heat_pump reads it as the wired-controller temperature (T6), with dp 26 as the tank. Each table follows its own source. The disagreement is recorded in the pull-request body and in `docs/HANDOVER.md`, and not resolved in either direction without a reading from the owner's install.
  - **localtuya** (G7b-2), platform `localtuya`, at both maintained lines: xZetsubou/hass-localtuya tag `2026.7.0` (commit `3d0c0ec`), `entity.py:242-247`, and rospogrigio/localtuya tag `v5.2.5` (commit `59c95cd`), `common.py:469-471`.
    - *unique_id*: `local_`, the device id, an underscore, then the DP id, unless the xZetsubou entity sets its own. The DP id is recoverable from it.
    - *Why it does not map by default*: localtuya carries no model identity, and the user configures which DPs become entities and their names. A DP-keyed table would be the tuya_heat_pump meanings applied to a device of unknown firmware, so localtuya gets the fallback. A DP-keyed table ships only if the fixer finds a firmware signature in the records that proves the device, and says so.
  - **Brand-specific integrations**: fallback only.
- **Fuzzy fallback resolver** (G7b-3), by the owner's decision above. It matches by type, unit and entity name, and says so on the page.
  - **Hard filter first**: a candidate must pass the role's domain, device_class and unit before any name is read. Units are normalised by family (°C with K, W with kW), and nothing ever matches on name alone. So roles with no physical unit are out of the fallback's reach: the DHW and silent-mode windows, the legionella interval, control mode and the flag slots. A role whose unit is physical, such as a °C set-point, is in reach, because a Home Assistant state carrying a unit is already in engineering units.
  - **Name scoring**: entity_id, original_name and friendly name are normalised: lowercased, split on underscores, camelCase and digit boundaries, and stripped of the device-name prefix. They are then scored against a per-role synonym list: token overlap plus a `difflib` string-similarity ratio (standard library, no new requirement). The lists are English and Swedish, plus the vocabulary the pinned source definitions actually use, taken from the generated fixtures rather than typed. Examples of the shape: supply water — supply, flow, leaving, outlet, T1, framledning; return — return, entering, inlet, retur; outdoor — outdoor, ambient, outside, ute; tank — tank, DHW, hot water, varmvatten.
  - **Decision rule**: a role is suggested only when the best score clears a threshold AND beats the runner-up by a margin. A tie or near-tie gives nothing, one entity is suggested for at most one role, a filled slot is never overwritten (`infer()`'s only-when-empty rule), and nothing is written until the user submits the page. **The threshold and margin come from the corpus measurement and are cited in the pull-request body with the command that printed them, never chosen by feel.**
  - **Disclaimer**: the page description says which suggestions came from name matching, lists each as role → entity, and asks the user to check them before saving. Source-table suggestions are named by source. If the page is sectioned, those labels go under `sections.<s>.data` and `data_description`.
  - **Corpus**: a labelled set of realistic entity sets. The tuya_heat_pump and tuya_local sets are generated from the pinned definitions; localtuya-style sets with user-named DPs are hand-shaped and marked as such in the corpus. Real traps from the pinned sources belong in it. tuya_heat_pump carries both "Outlet Water Temperature (T1)" (dp 10) and "Heat Exchanger Outlet Water Temperature (Tout)" (dp 106), a near-tie for supply on the word "outlet". Its "T5" is the compressor discharge (`models/000004k4z6.py:168-178`), not the Midea tank probe the label suggests.
  - **Measured**: precision and recall per role over the corpus. **Acceptance is zero wrong suggestions**; recall is reported, not gated. The run also reports how many roles the fallback fills on each corpus device, because W1067-POST1 takes its qualifying minimum from that table.
- **Flow** (G7b-1): in phase 1 of `async_step_modbus_prefill`, a chosen device replaces the prefix resolver with the dispatched device resolver. G7b-3 adds only the disclaimer text to this path. Everything after that is G7's code path unchanged: `infer()`, the flat suggested-value form, and phase 3 through `_save_or_menu` (`config_flow.py:2520`). A device that resolves no role re-renders phase 1 with an error, not an empty form.
  - **#1107 binds**: the save path runs `_omit_unstored_defaults` over `_ABSENT_FALLBACKS` (`config_flow.py:1772`), which `tests/config_flow_steps.py:4860-4954` derives from coordinator snapshots. The pre-fill never writes a blank or an unchanged default, and no test hand-lists those keys.
  - **Section labels**: a device field inside a `section()` has its label and help under `options.step.<page>.sections.<s>.data` and `data_description` in `strings.json`, with the `en.json` byte-copy and a translated sv. A concurrent fix, branch fix/options-section-labels, adds a no-fallback lookup test that fails a label found only at the page level.
- **Stubs, measured at `c8eb0f6`, extended by G7b-1 to real HA's signatures at the `hacs.json` floor**:
  - `tests/hastub/homeassistant/helpers/device_registry.py` is 14 lines and defines only the `DeviceEntryType` str subclass. It has no registry, no `async_get`, and no device entry with `identifiers` or `config_entries`.
  - `tests/hastub/homeassistant/helpers/entity_registry.py` has a `RegistryEntry` of `entity_id`, `unique_id`, `domain` and `config_entry_id` (`:16-21`), plus `add`, `async_remove`, `async_get` and `async_entries_for_config_entry` (`:29-65`). It has no `device_id`, `platform`, `original_name`, `translation_key`, `device_class`, `unit_of_measurement` or `async_entries_for_device`.
  - `tests/hastub/homeassistant/helpers/selector.py` has `EntitySelector` (`:120`) and no device selector.
  - G7b-1 adds the device registry, the missing entry fields with defaults (so the retired-entity cleanup at `__init__.py:236` is untouched), the per-device lookup, and a device selector.
- **Fixtures, generated rather than typed**: a small script (a new tracked file, so it enters a closure or `tests/closure.py`'s `INERT` list) reads each source's definitions at the pinned commit and writes a registry fixture shaped like that source's entities. The fixture records the upstream repository, tag and commit, and the suite reads fixtures only, with no network. **Honest scope**: the fixtures prove the mapping against each source's definitions at the pinned version, not against a live device. Drift is noticed when the maintainer bumps a pin and re-runs the script: a changed fixture fails the per-source test until the table is re-derived. The script's `--check` mode, run against the recorded commit, must print no difference.
- **Tests** (`tests/features.py` for resolvers; `tests/config_flow_steps.py` beside `registry_walk_recurses`, `:3545`, for the walk):
  - **G7b-1**:
    - The tuya_heat_pump positive test runs from the generated fixture.
    - A device from an unknown integration resolves nothing: error, no write.
    - A device with no matching entities: error, no write.
    - **Both entity-id slug spellings**: the same records under the suffixed and the unsuffixed entity-id spelling, plus a user-renamed id, resolve identically, because resolution keys on unique_id.
    - **Domain in the match**: a device named "Heat Night" has the slug `heat_night`, so its select `mode` has the unique_id `heat_night_mode`, which also ends in `_night_mode`. With the `night_mode` switch absent, the capacity-limited flag must resolve to nothing. With the switch present, it must resolve to the switch.
    - A `DHWSET` of 50 suggests 50.0.
    - A filled slot is not overwritten.
    - Coverage stays 100 % with no pragma (`tests/coverage_budgets.json:7`; the `pragmas` ratchet at `:4`).
  - **G7b-2**: tuya_local and localtuya positive tests from their fixtures, and the recorded dp 107 disagreement pinned as each source's own reading.
  - **G7b-3**:
    - The corpus precision/recall table, with zero wrong suggestions asserted.
    - **Genuine tie**: two supply-water candidates that pass the hard filter with identical normalised names and metadata, so their scores are equal. The test asserts **no suggestion**; "the right one" is not an accepted outcome here.
    - Adversarial cases, each giving no suggestion or the right one: two temperature sensors with similar but unequal names (the T1/Tout pair above); an energy entity against a power entity; a sensor with a perfect name and the wrong unit.
    - Coverage: `config_flow` stays at its 100 % floor (`tests/coverage_budgets.json:7`) with no pragma (the `pragmas` ratchet at `:4`), including the disclaimer path.
    - A device from an unknown integration gets fallback suggestions only, each named in the disclaimer.
    - An entity that scores for two roles is suggested for at most one.
- **Mutation proof**:
  - G7b-1: drop the tuya_heat_pump table → its positive test red; resolve by entity_id → spelling test red; drop the domain from the match → the "Heat Night" switch-absent test red, because longest-key matching then maps `select.…` with unique_id `heat_night_mode` to the flag (a plain `mode` and `night_mode` fixture would survive this mutant, since longest-key matching alone gets it right); apply r404's 0.1 to `DHWSET` → set-point test red.
  - G7b-2: drop the tuya_local table → its positive test red.
  - G7b-3: remove the margin rule → genuine-tie test red, because an equal score then yields the first candidate; remove the unit filter → wrong-unit test red; drop the one-role-per-entity rule → two-role test red.
- **Null control**:
  - G7b-1: with no device picked, G7's prefix route over the same `FakeHass` states gives a phase-2 suggestion dict identical to the merge base's (`diff` of the dumped dicts). `env_drift.py --all` shows no drift beyond the re-recorded `config_flow` schema fixture.
  - G7b-2 and G7b-3: every earlier fixture's resolved role map is byte-identical before and after.
  - G7b-3 also reports its matcher run over the corpus with the name scores zeroed, which must suggest nothing: without the name evidence the hard filter alone does not pick.
- **Metrics**: `config_flow.py` grows, with no coordinator change. The new module enters `tests/closures.json` and `docs/architecture.md`'s map and counts. `python3 tests/structure.py` decides the re-record under owner decision 4.

### W1067-G8 — close-out (Sonnet)

Runs after G7b-3. Delivery-status rows verified against measured `origin/main`, roster `resume` flips, `docs/HANDOVER.md` decisions (C4 deferral: the two-zone model has one flow temperature at `thermal_model.py:1952` and no per-zone emitter law, so a zone-2 supply slot would feed nothing; card-slot deferral; one-sided lift semantics), one #201 comment via `gh_comment.py` with read-back, `Closes #1067`. No stamp.

### W1067-POST1 — B: offer the pre-fill when a heat-pump device is added (post-wave follow-on)

Added by owner decision 7. The owner confirmed its placement and the items marked (owner) below on 2026-09-17; items marked *added by the plan author* are not the owner's.

**Placement and tracking**
- **After G8, outside the wave.** G8 closes #1067, and this group does not hold it open.
- **Tracking.** It gets its own issue or Delivery-status tracking entry when it is started, cites that entry rather than #1067, and has nothing filed for it before then.
- **Why after G8.** The table's `after` column could express either order, so the format did not decide. #1067's evidence is the Rotenso inputs, which G7b completes, and an unsolicited Repairs prompt is a new surface whose review should not hold delivered work open.
- **Dependency.** It starts only when G7b's mappings are in use: G7b-1 to G7b-3 merged and released. The offer's qualification rule (below) reads their resolvers and G7b-3's corpus figures, so it cannot be written earlier.

**Design**
- **Keys**: one global option that turns offers off, default on, on the pre-fill's own page (the fixer names the page and says why). It carries every item of "Every new option key touches".
  - **#1107 binds**: an untouched page must not write this option at its default. `_ABSENT_FALLBACKS` is derived, never hand-listed, and the derivation in `tests/config_flow_steps.py:4860-4954` proves a key either through a coordinator snapshot or through a static read. This key is read by the listener's setup rather than by the coordinator, so the fixer shows which proof covers it, or why it belongs in `_ABSENT_IS_NOT_DEFAULT`.
  - **Section labels**: if the page is sectioned, the label and help go under `sections.<s>.data` and `data_description`.
- **New HA-free module** `prefill_offer.py` (the name is the fixer's to choose), holding pure functions over plain records.
  - **Qualification**: a device qualifies only when a source G7b can map resolves it. That means tuya_heat_pump, tuya_local with a supported model, or any integration where G7b-3's fuzzy fallback fills at least a minimum number of roles.
  - **The minimum is taken from G7b-3's corpus measurement and cited, never guessed.** Otherwise there is no prompt, because a prompt that opens an empty page is noise.
  - This integration's own service device (the `DeviceEntryType` the coordinator imports, `coordinator.py:40`) and a disabled device never qualify.
  - **Offer state**: a pure transition over the stored record says whether to offer, re-raise, withdraw or ignore.
- **Persistence**: a `Store`, keyed by device id, holding each device's state: seen, offered, or dismissed. The stub at `tests/hastub/homeassistant/helpers/storage.py:32-50` round-trips through its module-level disk; the pattern is at `away.py:330`.
  - Each device is offered once, and the store survives restarts.
  - A removed-then-re-added device has a new device id, so it counts as new.
  - On first load the store records every existing device as seen, and none is offered: those were not "added".
  - At a later load, a qualifying device that the store has not seen was added while the integration was not running. It is offered then.
- **Listener**: the device-registry update event, registered in `async_setup_entry` (`__init__.py:265`) only when offers are on, and released through `entry.async_on_unload` (the pattern at `:322`). The issue id is keyed by device id, so `ir.async_create_issue` stays idempotent across two config entries.
- **Prompt**: a repair issue through `setpoint_check.create_issue` (`setpoint_check.py:32-35`), naming the device.
  - **Nothing is written automatically.** The prompt only opens the pre-fill page for that device, and the user submits it. A fix flow in `repairs.py` (dispatch at `async_create_fix_flow`, `:78`) may render that page's step, or the issue text may point to it. The fixer chooses and says why. Either way, the write is the page's own submit through `_save_or_menu` and `_omit_unstored_defaults`, with no second copy of the suggestion logic.
  - **Dismissal**: closing the prompt without submitting, or an explicit "not this device", stores dismissed.
  - The fixer cites the Home Assistant source, at the `hacs.json` floor, for whether the issue registry keeps an Ignore across restarts. The integration's store is the record either way.
- **Withdrawal**: removing a device deletes its open issue and its store record.
- **Stubs, measured at `c8eb0f6`**:
  - `FakeBus` registers listeners only through `async_listen_once` (`tests/harness.py:104-123`; its `listeners_for` is a query helper, not a registration), so this group adds `async_listen` with the same honest remove callback (#525).
  - The device-registry event goes into the stub G7b-1 extended.
  - The issue-registry stub has create and delete only (`tests/hastub/homeassistant/helpers/issue_registry.py:21-35`).
- **Translations and docs**:
  - The `issues` block and the option label in `strings.json`, with `en.json` byte-identical and sv translated.
  - No issue-key roster exists under `tests/`: `tests/entities.py:8999` is the no-hardcoded-SEK check, which only iterates the `issues` block. Translated repair strings are pinned per issue in `tests/features.py`, for example `:28418-28440` for the set-point notices across `strings.json`, `en.json` and `sv.json`. This group adds the same per-issue assertion for its issue, including its `fix_flow` step if design (a) ships.
  - `docs/configuration.md`: the option, what qualifies, and how a dismissal is undone.

**Acceptance**

The owner's own items, confirmed 2026-09-17, are listed first; everything marked *added by the plan author* is not the owner's and may be argued with.
- **Tests (owner)**:
  - A device added before the integration loads against one added after it. A device present at first load is not offered; one added after load, or while the integration was not running, is offered once.
  - A restart between the offer and the response re-raises exactly one issue and no duplicate.
  - A dismissal is remembered across a restart.
  - A non-qualifying device gets no offer: another integration below the cited minimum, this integration's service device, or a device resolving nothing.
  - A device removed while its offer is open withdraws the offer.
  - Null control, below: offers off gives no listener side effects.
- **Tests (added by the plan author)**:
  - A removed-then-re-added device (new id) is offered; the rule is the owner's, the test is not.
  - The submit writes nothing unchanged (#1107), and dismissing writes no option.
  - Unloading leaves `FakeBus.listeners` empty.
- **Coverage**: `config_flow` stays at its 100 % floor (`tests/coverage_budgets.json:7`) with no pragma (the `pragmas` ratchet at `:4`), including the new option's page path.
- **Mutation proof (owner)**:
  - drop the dismissal persistence → restart test red;
  - drop the qualification threshold → non-qualifying test red.
- **Mutation proof (added by the plan author)**:
  - drop the withdrawal → removed-device test red;
  - drop `async_on_unload` → unload test red.
- **Null control**: an install with offers off registers no listener. Its store records zero saves (`SAVE_COUNTS`), and `hass.issues` is unchanged after a qualifying device is added. `env_drift.py --all` shows no drift beyond the re-recorded `config_flow` schema fixture.
- **Metrics**: `__init__.py`, `repairs.py` and the new module grow, with no coordinator change. The module enters `tests/closures.json` and `docs/architecture.md`. `python3 tests/structure.py` decides the re-record. Owner decision 4's pre-authorised raises cover this group too: the owner answered on #201 (comment 5717092455), "it also cover POST1, which comes after the wave".

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

