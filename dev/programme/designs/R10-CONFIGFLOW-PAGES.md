# R10-CONFIGFLOW-PAGES design note (designer seat)

The group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/R10-CONFIGFLOW-PAGES` only and never merges. Issue #2238 (class P2, this group is the last open one listing it and the only one closing it). Findings D7-s2-55 (arch2-05), D7-s2-56 (arch2-06, re-classed bug by the catch-up judge), ARCH2-s5-F1.

**Round 2 of 3.** This adds Arm A3' (after Arm A), the B/C2 conflict resolution (Arm C2) and the #2238 disposition rule, answering the one revise point of `design-verdict/R10-CONFIGFLOW-PAGES` `d2d710ad8`. Nothing else changed. `git diff aaf8af512 6349205b6 -- custom_components/heatpump_optimizer/config_flow.py tests/config_flow_steps.py` is empty, so every line cited still holds at current main.

**Read at.** `origin/main` `aaf8af512c1fb9aeabdf58dbb5131928f432d4d1`. Both predecessors are merged, so there is no handoff head: R10-RATIO-ANCHOR (#2698, `2f88db054`, no `config_flow.py` hunk) and R10-HEAT-METER (#2854, `ea36188c3`, one `_F` row and one import). Prototypes at `01d9d0be2` (arch-s2 patches 04, 08) and `3930b421a` (branch `handoff/audit-r10-arch2-s5`: F1 and the patch-08 overlay). Patches 04, 08 and F1 each apply clean at `aaf8af512`, and together; the overlay is byte-identical to 08 less `index` lines.

## Premise, re-measured at `aaf8af512`

- **D7-s2-56, driven through the production steps** (`dev/programme/designs/R10-CONFIGFLOW-PAGES-probes/rejected_rerender.py`; the verifier's `dev/audit/rounds/round10/catchup/arch-s2/probe_rerender.py` evaluates the re-render expression, not the step, so it reads 9/0 at any tree). Store an entity in every `_STORED` row of the nine validating pages, clear them all, and add one field that makes the page reject: **27 of 30 cleared rows re-render as the stored entity** (entities 9, entities_metering 9, building 7, comfort 1, hot_water 1). Already right: hot_water_tank 2 (re-renders over `merged`) and grid_fees 1 (pops the slot by hand); grid and grid_connection hold no `_STORED` row. With patch 08: **0 of 30**. Null (`--null`, nothing cleared): 19 rows shown stored on both trees, unchanged.
- **D7-s2-55.** `_options_suggested_numeric` and `_suggested_entity` are still two copies of one rule, with the argument order swapped. Patch 04 alone: dS +0.3628 (duplication_copies 35 -> 34).
- **ARCH2-s5-F1.** The finder's harness `dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py` at `3930b421a` reads: wizard_fields 46, in_registry 44, spelled_twice 44, disagree 0, golden_equal 1. `--bump heat_pump_cop_nominal` gives disagree 2. Its `--all` arm adds a sibling the finding did not count: **other_spelled_twice 20** (user 4, user_sensors 14, quick_setup's wood probes 2), all with disagree 0.
- **Carried tripwires** (`tests/ci_budgets.json`): `archscore.unused_boundary_imports` 1 (`device_registry as dr` is imported and never read); `archscore.literal_clone_copies` 186 recorded, 185 measured.

## Owning seam

**`custom_components/heatpump_optimizer/config_flow.py`, one module, two symbols:**
- `HeatPumpOptimizerOptionsFlow._page`: the options page builder the roster names.
- `_OPTION_FIELDS`: the one place a setting's widget is declared, read through `_prefill_row(key).widget`.

Every other touched symbol only calls those two. `tests/seam_map.json` has no `config_flow` entry, so there is no second owner, and no state outside the flow is written.

## Shape (arms, in fixer order)

**Arm A, the bug first: one page template** (patch 08, which fixes D7-s2-56).
- `_page(step_id, user_input, *, clear=False, check=None, finish=None, placeholders=None)` runs one sequence:
  1. flatten the sections;
  2. `merged = {**current, **flat}`;
  3. `cleaned = _clear_absent(flat, step_id, merged)` if `clear`;
  4. `errors = await check(cleaned, current)`;
  5. no errors: `_save_or_menu(finish(cleaned, merged) if finish else cleaned)`;
  6. errors: re-render over `{**current, **cleaned}`, so a cleared slot shows empty.
- Types: `_PageCheck = Callable[[dict, dict], Awaitable[dict[str, str]]]` and `_PageFinish = Callable[[dict, dict], dict]`.
- Nine pages fold into it: entities, entities_metering, comfort, hot_water, hot_water_tank, building, grid, grid_connection, grid_fees. Their predicates move out unchanged as `_entities_errors`, `_metering_errors`, `_comfort_errors`, `_hot_water_errors`, `_disinfection_errors`, `_plumbing_errors`, `_peak_tariff_errors`, `_silent_window_errors` and `_grid_fee_errors`. Their save shaping moves out as `_warn_legionella_ceiling`, `_peak_window_as_int`, `_apply_dso_catalog` and `_building_wood_flag`, and the two duplicated placeholder dicts become `_fee_placeholders`.
- grid_fees' hand-written `current.pop(CONF_GRID_FEE_ENTITY)` goes: the template does that for every slot.
- Invariants:
  - an accepted submit saves byte-identical options;
  - every error key and placeholder is unchanged;
  - only a rejected form's cleared `_STORED` slots render differently.

**Arm A3', the price-entity clear** (in scope by the orchestrator's ruling; round 2 answers `design-verdict/R10-CONFIGFLOW-PAGES` `d2d710ad8`). It lands in arm A's pull request, after A's template, since it edits `_entities_errors`, the predicate A moves out.
- **Defect.** Today the entities page judges `price_entity_required` over `user_input.get(CONF_PRICE_ENTITY) or current.get(CONF_PRICE_ENTITY)` (config_flow.py:3405-3411). A cleared `_STORED` slot is absent from the submit, so the stored entity satisfies the check, and then `_clear_absent` saves `None`. `clear_required.py` reads `type=menu errors=None stored_price_entity=None` at `aaf8af512` and under patch 08. `config_flow.py` is unchanged from `aaf8af512` to `6349205b6`, so every line cited here holds.
- **Fix.** `_entities_errors(cleaned, current)` judges both the source and the entity over `view = {**current, **cleaned}`:
  - `source = view.get(CONF_PRICE_SOURCE, DEFAULT_PRICE_SOURCE)`;
  - when `source == PRICE_SOURCE_ENTITY` and `not view.get(CONF_PRICE_ENTITY)`, the result is `{CONF_PRICE_ENTITY: "price_entity_required"}`.

  The view reads the clear because `_clear_absent` writes a cleared `_STORED` slot back as `None` (2264-2267). It is the rule `async_step_hot_water_tank` already uses over `merged` (3540-3544). The tibber branch keeps `user_input.get(CONF_TIBBER_TOKEN) or current.get(...)` unchanged: the token row's default is `''`, not `_STORED` (row at 1563), so `_clear_absent` never nulls it, and the verdict's sibling grep found no other live site.
- **Failing test** (`tests/config_flow_steps.py`, beside the `price_entity_required` cases at 742 and 3335):
  - **Setup.** Stored `price_source: entity` and `price_entity: sensor.price`. Submit the entities page with `price_source: entity` and the price entity absent (cleared).
  - **Assert.** `type == "form"` and `errors == {CONF_PRICE_ENTITY: "price_entity_required"}`. The entry's options are unchanged, with `price_entity` still `sensor.price`.
  - At main it fails: `type=menu`, `None` saved.
  - **Null control.** The same submit with `price_entity: sensor.other` saves `sensor.other` with no error, at main and at head.
  - **Second control.** A switch to `price_source: tibber` with token `t` raises no error and saves the token. The absent price entity is still nulled by `_clear_absent`, as at main; that behaviour is unchanged.
- **Mutants**, both killed by the failing test:
  - judge over `{**current, **flat}`, the pre-clear view;
  - restore `user_input.get(CONF_PRICE_ENTITY) or current.get(CONF_PRICE_ENTITY)`.
- **Harness.** Port `dev/programme/designs/R10-CONFIGFLOW-PAGES-probes/clear_required.py` into `dev/audit/harnesses/r10_configflow_pages.py` (would be new) as a `--clear-required` arm beside the re-render arm. It prints `type=menu stored_price_entity=None` at base and `type=form errors=price_entity_required` at head. `--clear-required --null` submits `sensor.other` and reads `stored_price_entity='sensor.other'` on both trees.
- **Invariants, amended.** Arm A's "an accepted submit saves byte-identical options, and every error key is unchanged" keeps exactly one deliberate exception: on the entities page, a submit whose resolved source is `entity` and whose price entity is cleared changes from accepted to refused. A3's record-at-main comparison excludes that case and names it, as `A3-exception: price_entity_cleared_under_entity_source`. A3 also asserts that the exclusion predicate matches exactly one of its fixture cases, so the exception cannot grow silently. Every other A3 case must still compare equal.
- **Behaviour change, user-visible.** A submit that saved `price_entity: None` is now refused, with the existing `price_entity_required` error. The PR body's behaviour section names it. The translation key already exists in `strings.json` and the translations, so no string moves.

**Arm B: the suggested-optional helper** (patch 04, D7-s2-55). `_suggested_optional(current, key)` replaces both helpers. It has three call sites: `_field_marker` and the two wood probes in `_quick_setup_schema`. No behaviour moves.

**Arm C: wizard widgets from the registry** (F1, ARCH2-s5-F1).
- `_wizard_fields(marker, defaults)` returns `{marker(key, default=d): _prefill_row(key).widget}`, and `_NAMEPLATE_DEFAULTS` is shared by building_extras and thermal.
- The six wizard pages take all 44 widgets from their rows. Defaults and markers stay the wizard's own.

**Arm C2, the sibling sites:** the same move on the 20 first-screen widgets (`_user_credentials_fields`, `_user_sensors_fields`, `_quick_setup_schema`'s wood probes), as a value swap to `_prefill_row(KEY).widget`, with markers and defaults untouched. Spike `dev/programme/designs/R10-CONFIGFLOW-PAGES-probes/F1_plus_F1b_spike.patch`: other_spelled_twice 20 -> 0, golden_equal 1.
- **Conflict with arm B, resolved.** Patch 04 (arm B) and the spike conflict textually at `_quick_setup_schema`'s two wood probes (about config_flow.py:1221 on the 08+04 tree). Patch 04 rewrites the marker side (`_suggested_entity(K, current)` becomes `_suggested_optional(current, K)`), and the spike rewrites the value side (`_entity_of(["sensor"])` becomes `_registry_widget(K)`, the spike's lookup of `_OPTION_FIELDS`). So "apply clean together" holds for 04, 08 and F1, but not for F1b. The resolution keeps both sides on each probe: `_suggested_optional(current, CONF_WOOD_TANK_TOP_ENTITY): _registry_widget(CONF_WOOD_TANK_TOP_ENTITY)`, and the same for `CONF_WOOD_TANK_BOTTOM_ENTITY`. That combined A+B+C+C2 tree is the one the design reviewer measured at **dS +3.3700** (`score.py --diff aaf8af512`; duplication_copies 35 -> 28, literal_clone_copies 185 -> 123). Arm C2 lands after arm B, so the fixer applies this resolution and re-runs `wizard_widgets.py --all` (other_spelled_twice 0) and the `_field_marker` and quick-setup tests.

**Arm D: the carried tripwires.**
- Drop `dr` from the `homeassistant.helpers` import and lower `archscore.unused_boundary_imports` 1 -> 0.
- Re-record `archscore.literal_clone_copies` at the head's measured value. It is 123 with C2 and 133 without, at `aaf8af512`. State the merge-base figure, the head figure and the drop in the commit message, with `recorded_at`.

```
submit -> _page: flatten -> merged -> _clear_absent(over merged) -> check(cleaned, current)
            | errors: show_form(errors, placeholders, _page_schema(step, {**current, **cleaned}))
            | ok:     _save_or_menu(finish(cleaned, merged) | cleaned)
wizard/first screens: marker(key, default) -> _OPTION_FIELDS[key].widget (no second selector)
```

## Alternatives rejected

- **Fix the merge line in each of the 5 broken pages.** The bug is gone, but the 9 skeletons stay, and the next one drifts again: 2 of 9 had already done so differently (hot_water_tank and grid_fees). It moves 0 copies; arm A moves 6.
- **A `_PageSpec` table of (check, finish, placeholders) per step.** It moves the same lines into a second registry beside `_OPTION_PAGES`. Callables in a table are harder to test per page than bound methods, and nothing else would read it.
- **For F1, build the widget from row data (bounds) in the wizard.** That is still two constructions. Taking the row's object makes "two flows, one range" true by identity, which the finder's `is` test checks.

## Sibling sites

- Re-render merges: `grep -n 'current = {\*\*current, \*\*\|current = merged' custom_components/heatpump_optimizer/config_flow.py` returns 10 sites. Nine are arm A; the tenth is `_try_thermal_model_save`.
- Hand-written options steps: an AST walk over `HeatPumpOptimizerOptionsFlow` for `async_step_*` without `self._page(` returns 9 + init, advanced, setup_overview, quick_setup, building_preset, modbus_prefill and the thermal pair.
- **Out of scope:**
  - `_try_thermal_model_save` and the thermal pair: already one shared path, all `_SUGGESTED` with no `_STORED` row, so the defect cannot occur. Their placeholder depends on the re-render view, so folding them would widen the template for 0 copies.
  - building_preset: no check and no `_STORED` row.
  - quick_setup and modbus_prefill: multi-phase flows with their own state.
  - init, advanced, setup_overview: menus or read-only.
- Widget copies: `wizard_widgets.py --all`. Arms C and C2 cover all 64.

## Evidence plan, by file

- **Failing tests first**, in `tests/config_flow_steps.py`, which already has `suggested_value` and `options_over`:
  - **A1.** For each of the nine pages, store every `_STORED` row with its `when` gates open, submit with all of them cleared plus the page's rejecting field, and assert each cleared row's `suggested_value` is `None`. At main it fails with 27 of 30.
    - Null: the same rejection with nothing cleared re-renders every row as stored.
    - Positive control: hot_water_tank and grid_fees pass at main.
  - **A2.** On a rejected grid, grid_fees, hot_water and grid_connection form, `description_placeholders` is unchanged.
  - **A3.** An accepted submit on each of the nine pages saves the same options at main and at head: record them at main, then compare.
  - **C1.** Every wizard and first-screen field whose key has an `_OPTION_FIELDS` row delivers that row's widget object (`is`). It fails at main with 64. Null: `golden.capture_config_flow()` equals `tests/golden/config_flow.json` on both trees.
  - **B** is hygiene and has no failing test. Its evidence is score.py plus the existing `_field_marker` and quick-setup tests.
- **Finder's harnesses at both ends:**
  - `dev/audit/rounds/round10/D7/arch-s2/run_findings.sh 04_suggested 08_page` (patches on the finder's base `554e2ecfa`);
  - `wizard_widgets.py` from `3930b421a`, including `--all` and `--bump heat_pump_cop_nominal` (disagree 2 -> 0);
  - `python3 tools/audit/archscore/score.py --diff <merge-base>`.
  - Port `rejected_rerender.py` to `dev/audit/harnesses/r10_configflow_pages.py` (would be new) and run it at base and head: 27 -> 0, null 19 = 19.
- **Goldens:** none move (golden_equal 1 with all arms at `aaf8af512`), so `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` stay byte-identical.
- **Registry row:** `tests/entities.py` `_p2_registry`'s `wood_furnace_on` disposition moves from `async_step_building` to `_building_wood_flag` (patch `08t`, applies clean).
- **Mutation targets:**
  - the `_page` re-render merge (`**cleaned` -> `**flat`);
  - `_clear_absent`'s `merged` argument (-> `current`, killed by the existing wood-off clear test);
  - `if not errors`;
  - the `finish` application;
  - the placeholders pass-through;
  - each moved predicate's guard;
  - `_suggested_optional`'s `if key in current`;
  - `_wizard_fields`' widget lookup.
- **Mutation-ledger re-key, owed** (carry): `tests/mutation_ledger/killed_by/config_flow.py/` holds 15 entries keyed on symbols that move: options `_page`, `async_step_entities` x2, `async_step_entities_metering`, `async_step_comfort`, `async_step_hot_water` x2, `async_step_hot_water_tank`, `_options_suggested_numeric`, `_suggested_entity`, and the wizard's `async_step_temperature`, `async_step_building_extras`, `async_step_zones`, `async_step_dhw` and `async_step_weather_sensitivity`.
- Checked on the combined tree at `aaf8af512`: `tests/config_flow_steps.py` ALL 505 PASSED. `tests/entities.py` timed out at 590 s on a loaded machine (load1 65-97); the fixer runs it.

## Hot files, serial position, archscore

- `config_flow.py` is position 3 of 3. Both predecessors are merged, and no open `design/*` ref names it.
- `files` grows by `tests/config_flow_steps.py`, `tests/entities.py`, `tests/ci_budgets.json` and the mutation ledger.
- Churn of the combined spike: +351/-450 in one production file. That fits size L.
- **Archscore, per move** (`dev/programme/designs/R10-CONFIGFLOW-PAGES-probes/archscore.out`, admissible, counters on):

| move | dS | metric |
|---|---|---|
| A | +2.3483 | duplication_copies 35 -> 29 |
| B | +0.3628 | duplication_copies 35 -> 34 |
| C | +0.4731 | literal_clone_copies 185 -> 133 |
| C2 | +0.1119 more (C + C2 = +0.5850) | literal_clone_copies 133 -> 123 |
| D | 0, gate only | unused_boundary_imports 1 -> 0 |

- The combined spike without C2 reads **dS +3.2581**; with C2 and the B/C2 conflict resolution (arm C2) it reads **dS +3.3700**, measured by the design reviewer. A3' rewrites one predicate inside `_entities_errors` and is not expected to move a scored metric; the fixer's `score.py --diff` at head confirms it. The +3.3700 is about 15% of the programme's +22.7. Two metrics, with duplication_copies about 83% of this group's share; the 40% cap binds the plan, not the group (decision 0015).

## Decisions routed

- **Settled (orchestrator): A3' is in scope.** It is designed in Arm A3' above. The verdict's sibling grep closes the class with A3' alone.

## #2238 disposition rule, for the fix reviewer

This is the last group that lists #2238, and its `fixes` field holds it. The PR body therefore writes no closing keyword for #2238 until every other #2238 finding has a written disposition in that body: fixed by a named merged PR, fixed here, or carried to a named group or brief. The fix reviewer checks that list against the issue's findings at the head and returns `blocked` on a closing keyword that precedes a complete list. A keyword written inside a code span fires nowhere, so the body must not carry one there either.

## Notes for the fixer

- Carry: dismissed: overlay and patch identical (item overlay-08). The arch2-s5 overlay equals patch 08, and both apply clean at `aaf8af512`.
- Carry: R10-CONFIGFLOW-PAGES (item ledger-rekey). Re-key the 15 ledger entries listed above, in the same pull request.
- Carry: R10-CONFIGFLOW-PAGES (item c19-dr). Remove the `dr` import and lower `archscore.unused_boundary_imports` 1 -> 0, with the reason in the commit message.
- Carry: R10-CONFIGFLOW-PAGES (item literal-clones). Lower `archscore.literal_clone_copies` to the head's measured value, and give the merge-base figure, the head figure and the drop in the commit message.
- Carry: R10-CONFIGFLOW-PAGES (item grid-connection-flatten). grid_connection's `{CONF_SILENT_MODE_WINDOWS: "", **user_input}` default runs before the template flattens the sections. Pin it with a test that clears the window inside its section.
- Carry: R10-CONFIGFLOW-PAGES (item close-2238). This is the last group listing #2238, and `fixes` holds it. Before writing a closing keyword, check every other #2238 finding is dispositioned.
- Carry: R10-CONFIGFLOW-PAGES (item dr1-b-c2-conflict). Patch 04 and the C2 spike conflict at the two wood probes. Resolve as `_suggested_optional(current, K): _registry_widget(K)`, which is the tree measured at dS +3.3700 (arm C2).
- Carry: R10-CONFIGFLOW-PAGES (item dr1-close-2238-disposition). Every other #2238 finding is dispositioned in the PR body before any closing keyword, and the fix reviewer checks it (the rule above).
- Carry: R10-CONFIGFLOW-PAGES (item a3p-test). The A3' arm's failing test, its two controls, the two mutants, the `--clear-required` harness arm and the A3 exception, as designed above.
