# R10-UX-HEALTH design note (designer seat, `dev/governance/roles/designer.md`)

The group's architect note, extended (decision 0014). It lives on `design/R10-UX-HEALTH` only and is never merged. Size L, issues #2253, #2260, #2263, #2809 and #2815 (`fixes` empty: every one is named with Part of). Findings: owner items 1-5 and 7. Item 6 is a lead and is not owed (carry 1). **No finder harness: owner report** (screenshot of 2026-10-14) for items 1-5 and 7. #2809 and #2815 carry a D15 stub reproduction, which arm H turns into the failing test.

**Read at.** Code: `origin/main` `6d86acc909f7fc465e5736771daf8fa45c1373a4`. The roster brief was read at `handoff/audit-r10-roster` `8b434ef6246a0aa881a5f023f4b8c413896ebebe`. Of the `after` groups, R10-SCORES (`14405df59`), R10-HEAT-METER (#2854, `ea36188c3`) and R10-SAV-COMFORT (#2745, `34cd75bf1`) are merged. **R10-COP-GATE is not started**: there is no `handoff/r10-cop-gate` ref, and its roster stage is `not-started`. Its owning seam (the COP eligibility and its published state, in `custom_components/heatpump_optimizer/coordinator.py` and `custom_components/heatpump_optimizer/sensor.py`) is fixed by its architect note. Its payload key names are not. This note designs against the contract in arm E and states that dependency. Step 9's revalidation re-reads COP-GATE's merged diff before this fixer dispatches.

## Owning seam

**The Health tab renderer in `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`**, as named by the architect note: `healthPageHtml` and its `health*Html` helpers, the `health.*` strings, and `attachAdvisorInbox`'s act branches that the Health page emits. Three neighbours are only called, never owned here:
- `haLink`/`openHaLink`/`navigateTo` (R10-DEEPLINK's shared helper, extended in arm G only);
- `scoreParts`/`envelopeDrivers` (R10-SCORES', generalised in arm F under this group's owner-spec carry);
- the census in `tests/card.mjs` (R10-DEEPLINK-HANDLERS'; extended by each row this group converts, as its carry requires).

No backend file changes. Every datum the card needs is already published, or is COP-GATE's to publish (arm E). `tests/seam_map.json` maps coordinator methods only, so it names none of these files.

## Shape, by arm

**A. One label source (item 1).** `healthInputLabel` falls back to the raw key with `_` turned into spaces. This produces "wood tank top" and "heat pump supply temp", because the card carries `health.input_<key>` for 11 keys against the 44 `*_entity` fields of the options flow in strings.json (enumerator: walk `options` for `data` keys ending `_entity`; at `6d86acc90` 33 have no card label and the card has none outside the set). Enumerator: `InputHealth.ages()`'s keys are the `key` argument of `InputReader.read*` (`custom_components/heatpump_optimizer/inputs.py`). Every such key that is an options-flow field has its label at `options.step.*.data` / `.sections.*.data` in `custom_components/heatpump_optimizer/strings.json`, and in `custom_components/heatpump_optimizer/translations/sv.json` for sv.
- The card keeps its synchronous `STRINGS` table: `health.input_<key>` exists for **every** `*_entity` field of the options flow.
- A new `tests/card.mjs` arm asserts each value equals the strings.json label (and sv.json for sv) under one stated rule: strip the trailing " (optional)" and nothing else.
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

**E. The COP row (item 5, COP-GATE dependency).** Today the value reads `Normal (COP scale 1.00)` whenever `cop.scale` is finite, even with `watched_buckets` 0. The row takes its state from one place, `ModelStatusSensor`'s `cop` attribute: it stays available, it is unrecorded, and HA keeps its attributes. `ObservedCOPSensor` goes unavailable while waiting, which drops its attributes. The value is:
- the alarm when `alarm`;
- `Normal (scale)` only when `watched_buckets > 0`;
- otherwise `—` plus the reason in words.
The reason's precedence is COP-GATE's not-measurable state, then its refusal code, then `cop_watch_learning` (R10-SCORES' dash code, from the same `_watched_cop_buckets` predicate as `watched_buckets`). The contract this note designs against, owed by COP-GATE: `cop` gains `observable` (false only for the honest "COP not measurable here" state, and never on a `measured_heat` install) and `last_refusal` (one `COP_REFUSED_*` value from `custom_components/heatpump_optimizer/accuracy.py`, or one `SPAN_REFUSED_*` from `custom_components/heatpump_optimizer/heat_energy.py`, or null). Every code gets a `health.cop_reason_<code>` string in en and sv. `span_open` reads "waiting for the meter span to close", not a fault. An unknown code renders the generic waiting text, never the raw code. While COP-GATE has not published the keys, the row falls back to `cop_watch_learning`, so the arm is green either way and never shows "Normal" unwatched.

**F. Hover boxes (owner spec carries).** `envelopeDrivers` becomes `scoreDrivers(part, drivers)`, reading `envelope_drivers` and, once COP-GATE publishes it, `machine_drivers` with the same `{code, points}` shape. Each score hover and each Health model row's `title` carries `score.part_*`/`health.metric_*` plain-words text (what, unit, high/low, what "no data" means) plus its current reason or driver lines. The "driving scale" is **decision: orchestrator**: the only candidate in the card is the operation sub-score labelled "Driving" (`score.label_operation`). The carry already requires the fixer to confirm before building.

**G. Links and download (items 4 and 7, DEEPLINK carries).**
- **Item 4.** The checklist `insight` row's act becomes `show_entities`, which calls `openHaLink(host, "entities")`. Its copy narrows to "this integration's entities, disabled ones included", because no URL filters to disabled only (frontend 20260826.7). The `settings` act, its branch and its `ACTS` entry are deleted with the `health:settings` `PENDING` row. The PR #2572 note to reuse `open_options` loses to item 4: the options flow cannot enable an entity.
- **Item 7.** `diagnostics` calls `host.hass.fetchWithAuth` on HA's per-entry diagnostics endpoint (`/api/diagnostics/config_entry/<entry id>`, the entry id from `openHaLink`'s registry lookup, factored out). It saves the body as a Blob through **`navigateTo`'s single exit, extended with a download mode**, so `navigateTo` stays the one place the census allows `href`. A non-2xx response, a thrown fetch or a null entry id falls back to `openHaLink(host, "options")`, the entry page that holds HA's own menu. The `health:diagnostics` `PENDING` row is deleted.

**H. Debug collection (#2809, #2815).** The collection state is published on no entity, only in the diagnostics bundle and the `debug_collect` response (`SupportsResponse.OPTIONAL`, `custom_components/heatpump_optimizer/services.py`). The Health support block gains a collection row.
- On Health page entry and after a start, the card calls `hass.callService("heatpump_optimizer", "debug_collect", {action: "status", entry_id}, undefined, false, true)`. It caches the answer on the host, keyed into `healthSignature`.
- The row renders active (rows, end = start + 7 days), finished, or off.
- A `debug_start` act calls `action: "start"`. On a finished collection with rows > 0, the first press only arms a confirm, which says the old collection is discarded and points at Download diagnostics. #2815's "never delete without saying so" requires this.
- `DebugFinalizeButton.extra_state_attributes` (`custom_components/heatpump_optimizer/button.py`) publishes `waiting_for` only while the button is unavailable, so HA drops it in both cases and the value is never observable. Whether to delete those lines (out of `files`) is **decision: orchestrator**. This note recommends leaving `button.py` untouched: the visible surface is this row.

## Alternatives rejected

- **Labels loaded at runtime via `hass.loadBackendTranslation("options", ...)`.** It adds a WS round trip and an async first render that shows the fallback. The card test stub has no translation loader, and the labels still need the " (optional)" rule. The sync table plus the equality arm gives one source, checked, with no new runtime dependency.
- **A Start button entity in `button.py` (#2815's own proposal).** It is a backend file outside `files`, and it would be a second owner of collection presentation beside the Health row. The service already restarts, and the card already calls services.
- **Signed-path download (`auth/sign_path`, HA's own `fileDownload`).** A refused download is not observable to the card, so the brief's fallback could never fire.
- **COP row from `ObservedCOPSensor`.** It is unavailable while waiting, so its attributes are dropped in exactly the state item 5 names.

## Sibling sites (enumerated by command, at `6d86acc90`)

- Raw-key labels: `grep -nE "replace\(/_/g, \" \"\)" custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` returns one hit at `6d86acc90`, `healthInputLabel` itself, closed by arm A.
- Null read as 0: `grep -nE "Number\((attrs|a|st\.attributes)\." <card>` returns 4 hits at `6d86acc90`, the Advisor-row sites (SCORES carry, R10-ADVISOR done). They move to `readNumber`.
- Navigation exits: the census itself (`node tests/card.mjs`), with each converted row deleted from `PENDING`.

## Evidence plan

- **Failing tests first** (`tests/card.mjs`, each red at `6d86acc90`):
  - (A) a Health fixture with `wood_tank_top_entity` and `heat_pump_supply_temp_entity` in `input_ages_minutes` asserts the strings.json labels;
  - (D) `learner_progress.house` `{phase: "settling", eta_days: 12}` asserts no day figure;
  - (E) `cop: {scale: 1.0, watched_buckets: 0}` asserts no "Normal", and `last_refusal: "span_open"` asserts its string and not the raw code;
  - (G) `diagnostics` press with a stub `fetchWithAuth` returning 200 asserts a download through `navigateTo`, and 403 asserts the options link;
  - (H) a stub `callService` returning `{final: true, rows: 40}` asserts the finished row, and a first `debug_start` press asserts no service call;
  - the P08/P41 pins: the `openSetupSlot` render, and a topology place outside `SETUP_CONFIGURE_PAGE` labelled by `placeLabel`.
- **Null controls.** A fully watched COP install (`watched_buckets > 0`, no refusal) still reads "Normal (COP scale x)". A `measured_heat` install never reads not-measurable. An `active` collection shows no Start. A metered install's heat-loss row still says learned. A `counting` learner still shows its day figure.
- **Browser** (`tests/card_browser.mjs`, carry 2): Health in light and dark, at 375 and 1280.
  - Item 2: input-grid width over page width at 1280 must be at least 0.9, with at least 2 rows per line.
  - Item 3: the header-clip measurement from arm C.
  - This group owns the P9 grid's localStorage reset after each `page.goto` (CARD-VOICE carry), and re-reads the 30 base-owned tile pairs.
- **Census.** New acts `show_entities` and `debug_start` are added to `ACTS`. Fixtures `health+debug_final` and `health+debug_off` are added to `FIXTURES`. `python3 tools/audit/seat/r10_deeplink_mutants.py RV1_history_bracket_back_in_undriven_keydown RD8_insert_adjacent_html_built_href_driven_residual` must still read RV1 red and RD8 green.
- **Mutation targets:**
  - the " (optional)" strip;
  - the `watched_buckets > 0` test;
  - the reason precedence order;
  - `settling` → no day figure;
  - the fetch fallback branch;
  - the confirm arm in `debug_start`;
  - the fallback in `placeLabel`.
- **Goldens.** Card captures move (Health rows, copy), claimed in `tests/golden/card_claimed_drift.txt` per `dev/governance/rules/claim-files.md`. No value-bearing coordinator golden moves.

## Hot files, serial position, archscore target

- Hot files: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` is at position 5 of 5 (after R10-ADVISOR and R10-SCORES; next none).
- `files` stays the card, `custom_components/heatpump_optimizer/strings.json` and `custom_components/heatpump_optimizer/translations/en.json`. The last two are touched only if the arm A equality finds a label wrong at the source. `en.json` already drifts from strings.json at `pump_duty_mode`, which is not this group's.
- `tests/card.mjs`, `tests/card_browser.mjs` and `tests/entities.py` are test files.
- No coordinator hunk is needed, so no new after-edge.
- **Archscore target:** `python3 tools/audit/archscore/score.py --diff origin/main` must not read WORSENS and must stay admissible. At `6d86acc90`, `card_clone_copies` is 108 and `card_dead_definitions` is 0. Both must not rise. The shared `assigned` predicate, `scoreDrivers` and the deleted `settings` branch are where a fall comes from.

## Notes for the fixer

- Carry: R10-COP-GATE (item ux-cop-contract). Publish `observable` and `last_refusal` on `ModelStatusSensor`'s `cop` attribute (arm E), and `machine_drivers` beside `envelope_drivers` (arm F). Control: a `measured_heat` install reads `observable` true while its fold moves `cop_scale`.
- Carry: R10-UX-HEALTH (item hacs-floor). `hass.callService`'s `returnResponse` argument and `hass.fetchWithAuth` must exist at the `hacs.json` floor (2025.2.0). Confirm both against that frontend release before building.
- Carry: R10-UX-HEALTH (item item6-lead). Internal gains peaking at 03:00 stays a lead to D2 and D15. Nothing here changes `healthGainsRow`.
- Carry: R10-UX-HEALTH (item disabled-count). No local HA frontend exists to count disabled rows, so item 4's control pins the link path to `haLink("entities", entryId)` and the narrowed copy. The frontend filter behaviour rests on the coordinator's reading of frontend 20260826.7.
