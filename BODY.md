R10-DEEPLINK: one card helper builds every Home Assistant deep link, and one test enumerates every link-emitting button.

Closes #2253.

Part of #2238.

The owner's deep-link class (2026-10-14): Advisor "Open settings", Setup "Configure" and Health "Show" each built their own link and each landed on the integration's front page. This adds the shared builder and the enumeration test only. Per the group's architect note, the three call sites stay unconverted and go to R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH, which run `after` this group.

- `haLink(kind, entryId, entityId)` is pure. It builds the three routes that home-assistant-frontend 20260826.7 (the frontend HA 2026.9.3 pins) reads:
  - `options`: `/config/integrations/integration/heatpump_optimizer#config_entry=<entry>`. The integration page highlights and scrolls to this entry (`ha-config-integration-page._highlightEntry`), and its Configure button opens the options flow.
  - `entities`: `/config/entities?config_entry=<entry>`. `ha-config-entities._setFiltersFromUrl` sets `ha-filter-states: []`, and an empty state filter shows disabled entities (`showDisabled = !stateFilters?.length || ...`).
  - `entity`: the same table, plus `more-info-entity-id=<id>&more-info-view=settings`. On `location-changed`, `home-assistant._restoreMoreInfoFromUrl` opens that entity's settings dialog, which is where a disabled entity is enabled.

  An unknown kind, or an entity link with no entity, returns `null`. With no entry id, each kind falls back to the whole integration (`?domain=`), never to a guessed entry.
- `openHaLink(host, kind, entityId)` resolves the card's own entry through `config/entity_registry/get` on its plan sensor, then navigates with the existing `navigateTo`. `config/entity_registry/get` does not require admin. `hass.entities` carries no entry id, and this integration's entities have no device, so `hass.devices` cannot supply it either.
- ARCH2-s5 C2 is folded in as found at 3930b421a. `SetupPage.openPicker` is now the one writer of a picker visit's opening state, and `openSetupSlot` is the one in-card deep link into a Setup slot (advisor ranking and inbox Assign).
- The new test in `tests/card.mjs` works like this:
  - It renders each dialog page and presses every element there that has its own click listener, using a fresh card per press. It records every link it can see leave the card, and each must be a path `haLink` builds for this entry. The links it records are:
    - a `history.pushState` path;
    - an anchor's `href` in the rendered page;
    - a `hass-more-info` or `hass-action` event the card constructs. An event is never a `haLink` path, so an entity dialog goes through `haLink("entity")`'s URL instead.
  - Links not yet converted are listed in `PENDING` under the group that owns them, with the one path each row is known to emit. A row excuses that path and nothing else. A row whose path no press still produces is refused as stale.
  - The census asserts its own precondition. Every source line that calls `navigateTo` (outside `openHaLink`) or `openHaLink` must be reached by some press. A static guard covers rows the fixture does not render: `pushState` is the card's only history write, and the source holds no `window.open`, `location.href/assign/replace`, `hass-more-info`, `hass-action`, or `href=` built anywhere but from `haLink` on the same line.
  - `openHaLink` is driven directly, because no button calls it yet. With the fixture's `callWS` it asks the registry for its own plan sensor and links this entry (`entities`, `entity`). With a refusing registry it links the whole integration.

Alternatives not taken:
1. Opening the options flow at a step by firing the frontend's `show-dialog` for `dialog-data-entry-flow`. That would re-implement `showOptionsFlowDialog`'s about ten frontend-internal callbacks inside the card. It would be a parallel mechanism tied to frontend internals.
2. Filtering the entity table by `?domain=` only. That is wrong on an install with two entries, so it is kept as the fallback only.
3. A static grep for link buttons. That is keyed on spelling: it would miss a link built some other way and pass a button that never fires.

## Head

10a11f29e66e45f7787a2732791b1562d51baead. This is the PR head 0b4d46abd, with origin/main 694120d5a merged in (d2d4fc8cc) and two test commits on top (6a2decd2d, 10a11f29e). Merge base: 694120d5aa296b65c7d7be097f8684e7bc3b5f61. The merge changed neither the card nor `tests/card.mjs`.

Round 2, after #2283's blocked verdict at 0b4d46abd (comment 6197381541). The verdict found two gaps:
- a surviving `entryId = null` mutant in `openHaLink`;
- a census blind to anchors and `hass-more-info`.

Both are repaired in `tests/card.mjs` only. The card source is byte-identical to 0b4d46abd (`git diff --quiet 0b4d46abd HEAD -- custom_components` exits 0), so the harness figures and the routes the review verified are unchanged.

## Mutation proof

All twelve were run at 10a11f29e with `node tests/card.mjs`, one plant at a time, and the tree was restored after each. The plants are scripted in the seat's scratch `round2_mutants.sh`; each is the exact one-line replacement named here.

- M1: `haLink("options")` drops `#config_entry=`. Red: `haLink builds the three deep links Home Assistant routes`.
- M2: `haLink("entity")` drops `more-info-view=settings`. Red: `haLink builds the three deep links ...` and `haLink without a resolved entry falls back to the domain, never a guessed entry`.
- M3: delete the `advisor:settings` row from `PENDING`. Red: `every link a button emits is one haLink builds for this entry`.
- M4: add `function unreachedLink(host) { openHaLink(host, "entities"); }`, a link site no press reaches. Red: `the census reached every line that emits a Home Assistant link` (`unreached 8998`).
- M5: `SetupPage.openPicker` sets `pickerFocus = false`. Red: `openSetupSlot opens the slot's picker, focused only from the keyboard` (`keys false/true`).
- M6: convert the advisor `settings` handler to `await openHaLink(host, "options")`. Red: `every LINK_PENDING row still names a button that emits an unconverted link`. This is the stale-row arm the later groups will trigger.
- R4 (review): `entryId = null;` in `openHaLink`. Red: `openHaLink asks the registry for its own plan sensor and links this entry`. It pushed `?domain=` for both kinds.
- R5 (review): an `<a href="/config/integrations/integration/heatpump_optimizer">` added to the Health diagnostics row. Red: `every link a button emits ...` (`health:a -> /config/integrations/integration/heatpump_optimizer`) and the static guard `navigateTo is the card's only way out: no other history write, navigation, entity-dialog event or href`.
- R6 (review): the advisor `settings` handler dispatches `hass-more-info` instead of navigating. Red: `every link a button emits ...` (`advisor:settings -> hass-more-info:{"entityId":"sensor.x"}`), the static guard, the reach check and the stale-row check.
- R6b: the pending `settings` handler keeps `navigateTo(SETTINGS_PATH)` and also dispatches `hass-more-info`, with the type assembled at run time. That hides it from the static regex, and the reach check still finds the `navigateTo` line. Red: `every link a button emits ...` (`advisor:settings -> hass-more-info:...`). This is the dynamic sink on its own, through a pending row.
- R6c: the reviewer's shape, the non-pending Assign branch dispatching `hass-more-info` with the type assembled at run time. Red: `every link a button emits ...` (`health:assign -> hass-more-info:...`), plus the two older Assign checks.

Disclosed self-corrections:
- At 79c5974e1 (round 1), M4 and M5 survived. The site filter skipped any line starting with `function `, and nothing pinned keyboard focus into the picker. Both were fixed at aea95a724.
- In this round, R6b first survived the event sink. A `PENDING` row excused every link its key emitted, so a pending button that also fired `hass-more-info` passed. Each row now names its one excused path (10a11f29e). The reviewer's R4, R5 and R6 shapes are listed above as R4, R5, R6 and R6c.

Failing test first: before the helper existed, `tests/card.mjs` stopped with `ReferenceError: haLink is not defined`.

## Null control

- `v2_card_lines.mjs` run twice on the base card prints identical counts.
- The census is not vacuous at the head. It presses `plan=12 setup=0 savings=0 advisor=4 health=3` elements and reaches both link-emitting source lines.
- The three `PENDING` rows are each still observed emitting the bare integration path, which is the defect: removing one turns the test red (M3), and converting one does too (M6).
- `setup=0` and `savings=0` mean those pages have no own-listener element in this fixture. Their links would be caught by the reach precondition, as M4 shows.

## Figures

These are the finder's harnesses, run from exports, on the card at the base (`git show 5603ee319:<card>`) and at the head. The card blob is unchanged since 79c5974e1, so these were not re-run in round 2; the reviewer re-ran them at 0b4d46abd and got the same values. Each count's rule is the pattern named in the harness header.

- `node $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs <card>` (sha1 677b75421ca84ac0f404dc90fa0b6a0b72edea0e, from 3930b421a):
  - `picker_open` 3 -> 1
  - `total` 33 -> 31
  - `dead` 1 -> 2. The added dead symbol is `openHaLink`. It has no caller until R10-ADVISOR / R10-UX-HEALTH convert their sites, per the architect note ("one pure helper; the three call sites stay for their groups").
- `node $EXPORT/dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs <card>` (sha1 b3a1890e77115f9dbe0e2b64954bb21419890366, from handoff/audit-r10-catchup-verify):
  - `picker_lines` 5 -> 3, `total` 36 -> 34. The other columns are equal.
- Scoped gate: `GATE_SCOPE=auto bash tests/run.sh` gives MODE: SCOPED. The selection is `tests/closure.py select --diff 694120d5a`. The result is `12 TEST SCRIPT(S) PASSED; 23 SCOPED OUT AND NOT RUN`, rc 0, at 10a11f29e. card_drift.mjs ran in that set against origin/main and printed `card_drift: identical in all 40 states`, so the markup is unchanged.
- `python3 tests/structure.py` at 10a11f29e: STRUCTURE RATCHET PASSED. No budget moved, and no host member was added (`HOST_MEMBER_CEILING` check green).
- Step 8 seam enumeration: the rule is the census itself, meaning every source line calling `navigateTo` or `openHaLink`, reached by a press. It also counts every anchor `href` and every `hass-more-info`/`hass-action` event the presses produce, and the static guard covers rows the fixture does not render. It returns 2 sites, and no anchor or event at this head:
  - the advisor/health `.adv-act` handler: pending, owned by R10-ADVISOR (`settings`) and R10-UX-HEALTH (`settings`, `diagnostics`)
  - `openHaLink`'s own navigation: closed in this diff
  - Setup "Configure" does not exist yet. R10-UX-SETUP adds it, and the census refuses it unless it goes through `haLink`.

## Red checks

none

## Forward-carry

1. `tests/card.mjs` carries two of the constraints for the later groups in its own code. Its pending list names R10-ADVISOR and R10-UX-HEALTH as owners and refuses a stale row, so each group must delete its rows when it converts its button. Its reach precondition refuses a link line that no press reaches, so R10-UX-SETUP's Configure must be pressable in the census fixture.
2. Home Assistant (frontend 20260826.7) has no URL into an options-flow step, so `haLink("options")` lands on the entry highlighted. R10-ADVISOR item 7 must name the step in its copy, or link the option's entity. The destination is the R10-ADVISOR entry in `dev/programme/rosters/wave-r10-groups.json`, which is now on main. The orchestrator writes it there; at origin/main 694120d5a the entry does not yet carry it. Until it does, the carry is stated here and beside `haLink` in `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`.
3. The reviewer's carry for R10-UX-HEALTH item 4 is that "exactly the disabled entities" cannot be reached by a URL. The frontend's `_setFiltersFromUrl` always clears the state filter. The orchestrator routes it to the R10-UX-HEALTH entry in the same roster file.

## Friction

- fixer-step-6: contradiction: the shared seat brief told the seat to open the PR with app_push.sh and post on #201, while fixer.md step 6 and the group brief say seats push refs only; the orchestrator corrected it mid-task and only refs were pushed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

