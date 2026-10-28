# R10-UX-HEALTH design note (designer seat, `dev/governance/roles/designer.md`)

The group's architect note, extended (decision 0014). It lives on `design/R10-UX-HEALTH` only and is never merged. Size L, issues #2253, #2260, #2263, #2809 and #2815 (`fixes` empty: every one is named with Part of). Findings: owner items 1-5 and 7. Item 6 is a lead and is not owed (carry 1). **No finder harness: owner report** (screenshot of 2026-10-14) for items 1-5 and 7. #2809 and #2815 carry a D15 stub reproduction, which arm H turns into the failing test.

**Read at.** Round 2, answering `design-verdict/R10-UX-HEALTH` `7f4b360814d3c363a1be5f8f3d49113ba54c135e` (revise A-D). Code: `origin/main` `f844df1fe`; `git diff 6d86acc90 f844df1fe` is empty for the card, `custom_components/heatpump_optimizer/sensor.py`, `custom_components/heatpump_optimizer/services.py`, `custom_components/heatpump_optimizer/debugger.py`, strings.json and both translations, so round 1's line references stand. The roster brief was read at `handoff/audit-r10-roster` `8b434ef6246a0aa881a5f023f4b8c413896ebebe`. Of the `after` groups, R10-SCORES (`14405df59`), R10-HEAT-METER (#2854, `ea36188c3`) and R10-SAV-COMFORT (#2745, `34cd75bf1`) are merged. **R10-COP-GATE part 1** is read at its handoff `handoff/r10-cop-gate` `d3ce1d33f4475a5ec7479d878e11bb20e79c4fa7`: it publishes, in the learning view (`LearningView` in `custom_components/heatpump_optimizer/payload.py`), `cop_observability` (`accuracy.cop_observability`, five states), `cop_refusal` and `measured_cop_at`. **Part 2** (`r10-cop-gate-p2`, in flight) copies those three keys, under those names, into `ModelStatusSensor`'s `cop` attribute; that copy is part 2's, routed to its brief by the orchestrator, and this note only consumes it. Step 9's revalidation re-reads both parts' merged diffs before this fixer dispatches.

## Owning seam

**The Health tab renderer in `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`**, as named by the architect note: `healthPageHtml` and its `health*Html` helpers, the `health.*` strings, and `attachAdvisorInbox`'s act branches that the Health page emits. Three neighbours are only called, never owned here:
- `haLink`/`openHaLink`/`navigateTo` (R10-DEEPLINK's shared helper, extended in arm G only);
- `scoreParts`/`envelopeDrivers` (R10-SCORES', generalised in arm F under this group's owner-spec carry);
- the census in `tests/card.mjs` (R10-DEEPLINK-HANDLERS'; extended by each row this group converts, as its carry requires).

No backend file changes. Every datum the card needs is already published, or is COP-GATE's to publish (arm E). `tests/seam_map.json` maps coordinator methods only, so it names none of these files.

## Shape, by arm

**A. One label source (item 1).** `healthInputLabel` falls back to the raw key with `_` turned into spaces. This produces "wood tank top" and "heat pump supply temp", because the card carries `health.input_<key>` for 11 keys against the 44 `*_entity` fields of the options flow in strings.json (enumerator: walk `options` for `data` keys ending `_entity`; at `6d86acc90` 33 have no card label and the card has none outside the set). Enumerator: `InputHealth.ages()`'s keys are the `key` argument of `InputReader.read*` (`custom_components/heatpump_optimizer/inputs.py`). Every such key that is an options-flow field has its label at `options.step.*.data` / `.sections.*.data` in `custom_components/heatpump_optimizer/strings.json`, and in `custom_components/heatpump_optimizer/translations/sv.json` for sv.
- The card keeps its synchronous `STRINGS` table: `health.input_<key>` exists for **every** `*_entity` field of the options flow, en and sv.
- **The label rule, per language.** A card label equals the options-flow label with the language's optional marker removed from its end, and nothing else: en strips " (optional)"; sv strips " (valfri)" or " (valfritt)" (both occur: `grep -oE ' \((valfri|valfritt)\)"' custom_components/heatpump_optimizer/translations/sv.json | sort | uniq -c`). Every other parenthesis stays ("(night mode)", "(nattläge)", "(Nord Pool or similar)").
- **One label per field per language.** A field asked on more than one page (`outdoor_temp_entity`, `dhw_temp_entity`, `heat_pump_supply_temp_entity`, `heat_pump_return_temp_entity`, `heat_pump_capacity_limited_entity` on `modbus_prefill`; `wood_tank_top_entity` and `wood_tank_bottom_entity` on `quick_setup`) must carry the same label on every page. The **field's owning page wins**: the page or section that configures that device (`entities`, `entities_pump`, `building/sections/wood`), never the shortcut pages `quick_setup` and `modbus_prefill`, which re-ask fields owned elsewhere and are not where a user goes to change one. For the wood pair this is `building/sections/wood`: "Vedtankens toppgivare (valfri)" and "Vedtankens bottengivare (valfri)", in the same device-noun form as the sv labels around them. sv.json's two `quick_setup` copies (under `config` and under `options`) are rewritten to those. en is already equal on both pages. `custom_components/heatpump_optimizer/translations/sv.json` is in `files` by orchestrator ruling under mandate 6329234399 (roster edit queued by the orchestrator).
- A new `tests/card.mjs` arm walks `options` (and `config` for the shortcut pages) in strings.json and sv.json and asserts both: every occurrence of a field has one label per language, and each card label equals it under the rule above. A second label for a field fails the arm by name, so the ambiguity cannot return.
- `healthInputLabel`'s raw fallback is removed. An unknown key renders a generic role line with the entity id as secondary text, and never a derived name.
- A backend arm in `tests/entities.py` runs one cycle on a fully configured stub. It asserts `health.ages()` keys are a subset of that strings.json field set. This pins both ends.
- `heat_pump_heat_energy_entity` and `heat_pump_thermal_power_entity` (HEAT-METER carry) fall out of the same rule.
- A card key outside the set fails the same arm (none at `6d86acc90`), so a removed option takes its label with it.

**B. Full-width input list (item 2).** `.health-cols` is already `repeat(auto-fit, minmax(16em, 1fr))`. The inputs are one column of it, so on a wide screen they fill half and the short plan/learning column leaves the other half empty. The plan and learning blocks move above the inputs. The input rows become their own grid with `grid-template-columns: repeat(auto-fill, minmax(18em, 1fr))`, spanning the page.

**C. First row under the header (item 3).** The card defines no `position: sticky` and no `scroll-margin`, so the cause is not yet measured. The fixer measures it first in `tests/card_browser.mjs` (`healthPageStates`). With the dialog scrolled to 0 and again after a page switch, the first `[data-health-input]` row's top must be at or below the header's bottom. The suspect is `host.dialog.scroll` restoration across page switches. The fix goes where the measurement points, inside the Health page or the dialog's scroll restore. If it points outside the Health renderer, it is raised as a new after-edge, not made.

**D. Learner state (item 5, LEARNER-ETA and SCORES carries).** `healthModelHtml` reads `learner_progress` from `HEALTH_MODEL_SUFFIX` for house, lower, solar and gains, and from nothing else:
- `waiting` renders `waiting_for` as words;
- `counting` renders progress, and `eta_days` labelled as the gate ("about N days until learned");
- `settling` renders progress and **never** a day figure;
- `off` renders no row.
A missing `learner_progress` keeps today's sample rows. The Health `score` row renders `scoreReasonText(reasons.overall)` in place of the static `health.learn_score_why`. The heat-loss row on an install with no power meter and no heat meter reads "not observable without a power meter" in place of "learned" (demand-overbook carry). That predicate is the checklist's `assigned(...)`, moved to one module function that both read.

**E. One COP reason, two rows (item 5; COP-GATE).** Two Health sites render the COP state today, and both are wrong on a `not_measurable` install. The model row (`healthModelHtml`) reads `Normal (COP scale 1.00)` whenever `cop.scale` is finite. The learning row (`HEALTH_WAITING`'s `cop` entry, rendered by `healthLearningHtml`) shows the fixed `health.learn_cop_why`, "Needs a power meter on the heat pump", which is false on an install that has one. Both rows read **one function, `copState(cop)`**, over **`ModelStatusSensor`'s `cop` attribute** (the entity `HEALTH_MODEL_SUFFIX` names): it stays available, it is unrecorded, and HA keeps its attributes. `ObservedCOPSensor` is unavailable whenever `_waiting_for` is set (`measured_power_entity`, `heat_meter`, `first_cop_sample`), so its own `observability`, `last_refusal` and `measured_at` are dropped in exactly the states the rows must explain; it stays only as the learning row's trigger.

The keys read, under part 1's own names: `alarm`, `scale`, `watched_buckets` (today), and `cop_observability`, `cop_refusal`, `measured_cop_at` (part 2's copy). `copState` returns `{value, reason, tone}` in this precedence:
1. `alarm` → "Below its own history", warn.
2. `cop_observability` is `not_measurable` or `no_electric_meter` → `—` and that state's words, **even when `watched_buckets > 0`**: folds taken before the gate ruled the ratio no COP do not vouch for it now.
3. `watched_buckets > 0` → "Normal (COP scale x)". On a counter install a `span_open` refusal beside a measured COP stays "Normal" (COP-GATE carry 11's control).
4. Otherwise `—` and the first of: `cop_refusal`'s words, `awaiting_draw_evidence`'s words, `cop_watch_learning` (R10-SCORES' dash code).

While `measured_cop_at` is set the model row's detail appends its age ("measured N h ago", `fmtMinutes`), the D15 seam-2 latch age. The learning row renders `copState(cop).reason` in place of `health.learn_cop_why`, which is deleted in en and sv; with no model status entity it renders `cop_watch_learning`'s words, never the meter sentence. Strings: `health.cop_reason_<code>` in en and sv for each of the five `cop_observability` states and each `COP_REFUSED_*`/`SPAN_REFUSED_*` code (`awaiting_draw_evidence` is both, so one string). `heat_metered` and `draw_follows_plan` name the evidence source in the detail line ("measured by the heat meter", "the draw follows the plan"). `span_open` reads "waiting for the meter span to close", not a fault. An unknown code renders the generic waiting text, never the raw code. Before part 2 merges the three keys are absent, so step 2 never fires and the row reads as step 3 or 4: green either way, and never "Normal" unwatched.

**F. Hover boxes (owner spec carries).** `envelopeDrivers` becomes `scoreDrivers(part, drivers)`, reading `envelope_drivers` and, once COP-GATE publishes it, `machine_drivers` with the same `{code, points}` shape. Each score hover and each Health model row's `title` carries `score.part_*`/`health.metric_*` plain-words text (what, unit, high/low, what "no data" means) plus its current reason or driver lines. The "driving scale" is **decision: orchestrator**: the only candidate in the card is the operation sub-score labelled "Driving" (`score.label_operation`). The carry already requires the fixer to confirm before building.

**G. Links and download (items 4 and 7, DEEPLINK carries).**
- **Item 4.** The checklist `insight` row's act becomes `show_entities`, which calls `openHaLink(host, "entities")`. Its copy narrows to "this integration's entities, disabled ones included", because no URL filters to disabled only (frontend 20260826.7). The `settings` act, its branch and its `ACTS` entry are deleted with the `health:settings` `PENDING` row. The PR #2572 note to reuse `open_options` loses to item 4: the options flow cannot enable an entity.
- **Item 7.** `diagnostics` calls `host.hass.fetchWithAuth` on HA's per-entry diagnostics endpoint (`/api/diagnostics/config_entry/<entry id>`, the entry id from `openHaLink`'s registry lookup, factored out). It saves the body as a Blob through **`navigateTo`'s single exit, extended with a download mode**, so `navigateTo` stays the one place the census allows `href`. A non-2xx response, a thrown fetch or a null entry id falls back to `openHaLink(host, "options")`, the entry page that holds HA's own menu. The `health:diagnostics` `PENDING` row is deleted.

**H. Debug collection (#2809, #2815).** The collection state is published on no entity, only in the diagnostics bundle and the `debug_collect` response (`SupportsResponse.OPTIONAL`, `custom_components/heatpump_optimizer/services.py`). The Health support block gains a collection row.
- On Health page entry and after a start, the card calls `hass.callService("heatpump_optimizer", "debug_collect", {action: "status", entry_id}, undefined, false, true)`. That resolves to `{context, response}`, and `handle_debug_collect` returns `{debug: {<entry_id>: status}}`, so the card reads `res.response.debug[entry_id]`: `{active, final, rows, bytes, started_at}` (`debugger._IDLE` and `status()`). Anything else, including a status keyed by another entry, is "off". It caches the answer on the host, keyed into `healthSignature`.
- The row renders active (rows, end = start + 7 days), finished, or off.
- A `debug_start` act calls `action: "start"`. On a finished collection with rows > 0, the first press only arms a confirm, which says the old collection is discarded and points at Download diagnostics. #2815's "never delete without saying so" requires this.
- `DebugFinalizeButton.extra_state_attributes` (`custom_components/heatpump_optimizer/button.py`) publishes `waiting_for` only while the button is unavailable, so HA drops it in both cases and the value is never observable. Whether to delete those lines (out of `files`) is **decision: orchestrator**. This note recommends leaving `button.py` untouched: the visible surface is this row.

## Alternatives rejected

- **Labels loaded at runtime via `hass.loadBackendTranslation("options", ...)`.** It adds a WS round trip and an async first render that shows the fallback. The card test stub has no translation loader, and the labels still need the " (optional)" rule. The sync table plus the equality arm gives one source, checked, with no new runtime dependency.
- **A Start button entity in `button.py` (#2815's own proposal).** It is a backend file outside `files`, and it would be a second owner of collection presentation beside the Health row. The service already restarts, and the card already calls services.
- **Signed-path download (`auth/sign_path`, HA's own `fileDownload`).** A refused download is not observable to the card, so the brief's fallback could never fire.
- **A boolean `observable` on `cop` (round 1).** It folds `no_electric_meter` and `awaiting_draw_evidence` into one bucket and needs a key part 1 does not publish; part 1's five-state enum, read verbatim, is one source the card cannot drift from.
- **A separate reason for the learning row.** Two functions over one state is the round-1 defect class (a second COP site saying something else); one `copState` keeps them equal by construction.
- **COP row from `ObservedCOPSensor`.** It is unavailable while waiting, so its attributes are dropped in exactly the state item 5 names.

## Sibling sites (enumerated by command, at `6d86acc90`)

- Raw-key labels: `grep -nE "replace\(/_/g, \" \"\)" custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` returns one hit at `6d86acc90`, `healthInputLabel` itself, closed by arm A.
- Null read as 0: `grep -nE "Number\((attrs|a|st\.attributes)\." <card>` returns 4 hits at `6d86acc90`, the Advisor-row sites (SCORES carry, R10-ADVISOR done). They move to `readNumber`.
- COP-state renderers: `grep -nE "learn_cop|model_cop|_learning_observed_cop" custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` (20 hits at `f844df1fe`): the `HEALTH_WAITING` entry, `healthLearningHtml`'s row, `healthModelHtml`'s row, and the en and sv strings. Every row site moves to `copState`; the string hits are the strings it renames or deletes.
- Multi-page option labels: the walk in arm A's equality arm is the enumerator; at `f844df1fe` it finds seven fields, of which only the wood pair differs (sv).
- Navigation exits: the census itself (`node tests/card.mjs`), with each converted row deleted from `PENDING`.

## Evidence plan

- **Failing tests first** (`tests/card.mjs`, each red at `6d86acc90`):
  - (A) a Health fixture with `wood_tank_top_entity` and `heat_pump_supply_temp_entity` in `input_ages_minutes` asserts the owning-page labels in en and sv ("Wood tank top sensor", "Vedtankens toppgivare"), and the one-label arm is red on sv.json's `quick_setup` copy;
  - (D) `learner_progress.house` `{phase: "settling", eta_days: 12}` asserts no day figure;
  - (E) `cop: {scale: 1.0, watched_buckets: 0}` asserts no "Normal";
  - (E) `cop: {scale: 1.0, watched_buckets: 3, cop_observability: "not_measurable"}` asserts no "Normal" and the `not_measurable` string; the same with `no_electric_meter`;
  - (E) `cop_refusal: "span_open"` with `watched_buckets: 0` asserts its string and not the raw code; `measured_cop_at` two hours old asserts the age on the row;
  - (B) the same `not_measurable` fixture with `_learning_observed_cop` unavailable asserts the learning row carries the `not_measurable` string and no "Needs a power meter";
  - (G) `diagnostics` press with a stub `fetchWithAuth` returning 200 asserts a download through `navigateTo`, and 403 asserts the options link;
  - (H) a stub `callService` resolving `{context: {id: "c"}, response: {debug: {[entry_id]: {active: false, final: true, rows: 40, bytes: 9000, started_at: <iso>}}}}` asserts the finished row, and a first `debug_start` press asserts no service call;
  - the P08/P41 pins: the `openSetupSlot` render, and a topology place outside `SETUP_CONFIGURE_PAGE` labelled by `placeLabel`.
- **Null controls.** A fully watched COP install (`watched_buckets > 0`, no refusal) still reads "Normal (COP scale x)". `{cop_observability: "heat_metered", cop_refusal: "span_open", watched_buckets: 3}` reads "Normal" (carry 11). (H) wrong-level arms render "off", never "finished": the status flat at the top level (`{final: true, rows: 40}`), the `debug` map without the `response` wrapper, and a `response.debug` keyed by a different entry id only. A `measured_heat` install never reads not-measurable. An `active` collection shows no Start. A metered install's heat-loss row still says learned. A `counting` learner still shows its day figure.
- **Browser** (`tests/card_browser.mjs`, carry 2): Health in light and dark, at 375 and 1280.
  - Item 2: input-grid width over page width at 1280 must be at least 0.9, with at least 2 rows per line.
  - Item 3: the header-clip measurement from arm C.
  - This group owns the P9 grid's localStorage reset after each `page.goto` (CARD-VOICE carry), and re-reads the 30 base-owned tile pairs.
- **Census.** New acts `show_entities` and `debug_start` are added to `ACTS`. Fixtures `health+debug_final` and `health+debug_off` are added to `FIXTURES`. `python3 tools/audit/seat/r10_deeplink_mutants.py RV1_history_bracket_back_in_undriven_keydown RD8_insert_adjacent_html_built_href_driven_residual` must still read RV1 red and RD8 green.
- **Mutation targets:**
  - the per-language marker strip (en, and each sv suffix);
  - the owning-page choice and the one-label assertion;
  - step 2 of `copState` (move it below step 3: the `not_measurable, watched_buckets: 3` test goes red);
  - the `response.debug[entry_id]` read level;
  - the `watched_buckets > 0` test;
  - the reason precedence order;
  - `settling` → no day figure;
  - the fetch fallback branch;
  - the confirm arm in `debug_start`;
  - the fallback in `placeLabel`.
- **Goldens.** Card captures move (Health rows, copy), claimed in `tests/golden/card_claimed_drift.txt` per `dev/governance/rules/claim-files.md`. No value-bearing coordinator golden moves.

## Hot files, serial position, archscore target

- Hot files: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` is at position 5 of 5 (after R10-ADVISOR and R10-SCORES; next none).
- `files`: the card, `custom_components/heatpump_optimizer/strings.json`, `custom_components/heatpump_optimizer/translations/en.json` and, added by orchestrator ruling under mandate 6329234399, `custom_components/heatpump_optimizer/translations/sv.json` (the two wood `quick_setup` labels, arm A). strings.json and en.json are touched only if the arm A equality finds a label wrong at the source. `en.json` already drifts from strings.json at `pump_duty_mode`, which is not this group's.
- `custom_components/heatpump_optimizer/sensor.py` is not in `files`: the copy of the three COP keys into `ModelStatusSensor.cop` is R10-COP-GATE part 2's.
- `tests/card.mjs`, `tests/card_browser.mjs` and `tests/entities.py` are test files.
- No coordinator hunk is needed, so no new after-edge.
- **Archscore target:** `python3 tools/audit/archscore/score.py --diff origin/main` must not read WORSENS and must stay admissible. Round 1 read `card_clone_copies` 108 and `card_dead_definitions` 0 at `6d86acc90`; the design review did not re-measure them, so the fixer re-takes both at its merge base (carry archscore-base) and neither may rise from that figure. The shared `assigned` predicate, `scoreDrivers`, the one `copState` behind two rows and the deleted `settings` branch are where a fall comes from.

## Notes for the fixer

- Carry: R10-COP-GATE (item ux-cop-contract). Part 2 (`r10-cop-gate-p2`) copies the learning view's `cop_observability`, `cop_refusal` and `measured_cop_at`, under those names, into `ModelStatusSensor`'s `cop` attribute in `sensor.py`: no new state, no boolean, no renamed key. `machine_drivers` beside `envelope_drivers` (arm F) mirrors part 2's own carries 6, 7 and 14; the name is agreed with part 2. Routed to part 2's brief by the orchestrator; this card reads only that interface. Control: a `measured_heat` install reads `heat_metered` while its fold moves `cop_scale`.
- Carry: R10-UX-HEALTH (item heat-loss-clause). Arm D widens the demand-overbook carry from "no power meter" to "no power meter and no heat meter". Before building, confirm with `dev/audit/harnesses/r10_demand_overbook.py` that a heat reading makes the scale observable (a heat-metered arm whose scale error falls against the `nometer_half` arm). If it does not, keep the carry's own predicate, "no power meter".
- Carry: R10-UX-HEALTH (item enum-strings). Each of the five `cop_observability` values (`heat_metered`, `draw_follows_plan`, `not_measurable`, `awaiting_draw_evidence`, `no_electric_meter`) gets its own `health.cop_reason_*` string in en and sv. `awaiting_draw_evidence` is also `COP_REFUSED_NO_EVIDENCE`, so one string covers both readings. A `tests/card.mjs` arm enumerates the codes by `grep -nE '^(COP_(HEAT|DRAW|NOT|NO_ELECTRIC)[A-Z_]*|COP_REFUSED_[A-Z_]+|SPAN_REFUSED_[A-Z_]+) = ' custom_components/heatpump_optimizer/accuracy.py custom_components/heatpump_optimizer/heat_energy.py` and asserts a string per code per language.
- Carry: R10-UX-HEALTH (item archscore-base). Re-take `card_clone_copies` and `card_dead_definitions` with `tools/audit/archscore/` at your merge base before the first edit; that figure, not round 1's, is the ceiling.
- Carry: R10-UX-HEALTH (item hacs-floor). `hass.callService`'s `returnResponse` argument and `hass.fetchWithAuth` must exist at the `hacs.json` floor (2025.2.0). Confirm both against that frontend release before building.
- Carry: R10-UX-HEALTH (item item6-lead). Internal gains peaking at 03:00 stays a lead to D2 and D15. Nothing here changes `healthGainsRow`.
- Carry: R10-UX-HEALTH (item disabled-count). No local HA frontend exists to count disabled rows, so item 4's control pins the link path to `haLink("entities", entryId)` and the narrowed copy. The frontend filter behaviour rests on the coordinator's reading of frontend 20260826.7.
