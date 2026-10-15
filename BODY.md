R10-DEEPLINK: one card helper builds every Home Assistant deep link, and one test enumerates every link-emitting button.

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
  - It renders each dialog page and presses every element there that has its own click listener, using a fresh card per press. It records everything that reaches `history.pushState`, and every recorded path must be one that `haLink` builds for this entry.
  - Links not yet converted are listed in `PENDING` under the group that owns them. A row that no press still produces is refused as stale.
  - The census asserts its own precondition: every source line that calls `navigateTo` (outside `openHaLink`) or `openHaLink` must be reached by some press, and `pushState` must be the card's only history write.

Alternatives not taken:
1. Opening the options flow at a step by firing the frontend's `show-dialog` for `dialog-data-entry-flow`. That would re-implement `showOptionsFlowDialog`'s about ten frontend-internal callbacks inside the card. It would be a parallel mechanism tied to frontend internals.
2. Filtering the entity table by `?domain=` only. That is wrong on an install with two entries, so it is kept as the fallback only.
3. A static grep for link buttons. That is keyed on spelling: it would miss a link built some other way and pass a button that never fires.

## Head

aea95a72457da8c7f954ad2d521e26cde2844d52, merge base 5603ee319d73cd464d38a3cbbad90d83d4cf4cdf (origin/main at branch time).

## Mutation proof

Each mutant was run with `node tests/card.mjs` and the tree was restored after each one:

- M1: `haLink("options")` drops `#config_entry=`. Red: `haLink builds the three deep links Home Assistant routes` and `every LINK_PENDING row still names a button that emits an unconverted link`.
- M2: `haLink("entity")` drops `more-info-view=settings`. Red: `haLink builds the three deep links ...` and `haLink without a resolved entry falls back to the domain, never a guessed entry`.
- M3: delete the `advisor:settings` row from `PENDING`. Red: `every link a button emits is one haLink builds for this entry`.
- M4: add `function unreachedLink(host) { openHaLink(host, "entities"); }`, a link site no press reaches. Red: `the census reached every line that emits a Home Assistant link` (`unreached 8998`).
- M5: `SetupPage.openPicker` sets `pickerFocus = false`. Red: `openSetupSlot opens the slot's picker, focused only from the keyboard` (`keys false/true`).
- M6: convert the advisor `settings` handler to `await openHaLink(host, "options")`. Red: `every LINK_PENDING row still names a button that emits an unconverted link`. This is the stale-row arm the three later groups will trigger.

Disclosed self-correction: at 79c5974e1, M4 and M5 survived. The site filter skipped any line starting with `function `, and no Node check pinned keyboard focus into the picker (that line was already unpinned before C2 moved it). aea95a724 fixes the filter and adds the focus check. Both mutants were re-run at that head and are listed red above.

Failing test first: before the helper existed, `tests/card.mjs` stopped with `ReferenceError: haLink is not defined`.

## Null control

- `v2_card_lines.mjs` run twice on the base card prints identical counts.
- The census is not vacuous at the head. It presses `plan=12 setup=0 savings=0 advisor=4 health=3` elements and reaches both link-emitting source lines.
- The three `PENDING` rows are each still observed emitting the bare integration path, which is the defect: removing one turns the test red (M3), and converting one does too (M6).
- `setup=0` and `savings=0` mean those pages have no own-listener element in this fixture. Their links would be caught by the reach precondition, as M4 shows.

## Figures

These are the finder's harnesses, run from exports, on the card at the base (`git show 5603ee319:<card>`) and at the head (unchanged since 79c5974e1). Each count's rule is the pattern named in the harness header.

- `node $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs <card>` (sha1 677b75421ca84ac0f404dc90fa0b6a0b72edea0e, from 3930b421a):
  - `picker_open` 3 -> 1
  - `total` 33 -> 31
  - `dead` 1 -> 2. The added dead symbol is `openHaLink`. It has no caller until R10-ADVISOR / R10-UX-HEALTH convert their sites, per the architect note ("one pure helper; the three call sites stay for their groups").
- `node $EXPORT/dev/audit/rounds/round10/catchup/arch-b/v2_card_lines.mjs <card>` (sha1 b3a1890e77115f9dbe0e2b64954bb21419890366, from handoff/audit-r10-catchup-verify):
  - `picker_lines` 5 -> 3, `total` 36 -> 34. The other columns are equal.
- Scoped gate: `GATE_SCOPE=auto bash tests/run.sh` gives MODE: SCOPED. The selection is `tests/closure.py select --diff 5603ee319`. The result is `12 TEST SCRIPT(S) PASSED; 23 SCOPED OUT AND NOT RUN`, rc 0, at aea95a724. card_drift.mjs ran in that set and printed `card_drift: identical in all 40 states`, so the markup is unchanged.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No budget moved, and no host member was added (`HOST_MEMBER_CEILING` check green).
- Step 8 seam enumeration: the rule is the census itself, meaning every source line calling `navigateTo` or `openHaLink`, reached by a press. It returns 2 sites:
  - the advisor/health `.adv-act` handler: pending, owned by R10-ADVISOR (`settings`) and R10-UX-HEALTH (`settings`, `diagnostics`)
  - `openHaLink`'s own navigation: closed in this diff
  - Setup "Configure" does not exist yet. R10-UX-SETUP adds it, and the census refuses it unless it goes through `haLink`.

## Red checks

none

## Forward-carry

These go to the orchestrator for the roster entries of the three groups (dev/programme/rosters/wave-r10-groups.json, R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH):

1. Home Assistant (frontend 20260826.7) has no URL into an options-flow step. `haLink("options")` lands on this entry highlighted, and its Configure button opens the flow. R10-ADVISOR item 7 ("deep-link to the specific config-flow step or option") must say which step to open next in the row's copy, or find an option that is an entity (`haLink("entity")`).
2. Each group deletes its own `PENDING` rows in `tests/card.mjs` when it converts its handler. The test refuses a stale row.
3. A new link button must be reachable by a press in the census fixture. A delegated listener or an unrendered row fails the reach precondition, and the fix is to extend the fixture.

## Friction

- fixer.md step 6 / FIXER-BRIEF: contradiction. The shared seat brief said to open the PR with app_push.sh and post on #201, while fixer.md step 6 and the group brief say seats push refs only. The orchestrator corrected the brief mid-task, and refs only were pushed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
