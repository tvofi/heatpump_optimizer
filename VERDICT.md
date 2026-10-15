Fix review: blocked 0b4d46abd10c6d4f95bc8a14aa1885f963c34ecf harness: surviving mutant in openHaLink's registry lookup, and the census misses href= and hass-more-info links

bus-nonce: cd8b0d9dbcbe1875d77d8b2be2d5139b

Round 1. Reviewed from a detached worktree at 0b4d46abd10c6d4f95bc8a14aa1885f963c34ecf. The card and `tests/card.mjs` blobs there are byte-identical to aea95a724 (cb4035b6 and 23a6221f), and the base card blob is the same at 5603ee319 and at the merge base 78324e4a1 (a80c4356). The roles diff against origin/main is empty.

## Blocking (the fixer repairs both in this PR)

1. **A mutant survives in openHaLink's registry lookup.** Replacing `entryId = (reg && reg.config_entry_id) || null;` with `entryId = null;` leaves every check green (`RESULT mutant=R4_entry_ignored rc=0 fails=0`). openHaLink has no caller, and no test calls it, so the claim that it resolves the entry through `config/entity_registry/get` is not pinned. The census would pin it only after a later group deletes its PENDING row. Adding that mutant to a conversion that keeps its row also passes. Fix: add a direct check that calls `openHaLink` with the fixture's `callWS`, and assert the pushed path for both the resolved entry and the failed-lookup fallback.
2. **The census misses two link mechanisms.** It sees only `history.pushState`, and its static guard refuses only `window.open` and `location.href/assign/replace`. Two planted bypasses pass:
   - `R5_anchor_href`: an `<a href="/config/integrations/integration/heatpump_optimizer">` added to the Health diagnostics row. Result: `rc=0 fails=0`.
   - `R6_more_info_event`: a pressed button dispatching `hass-more-info`. The only failures are the two older Assign checks, because the plant replaced the Assign branch. No census check fails.

   `hass-more-info` is Home Assistant's native way for a card to open an entity dialog, so it is the bypass a later group is most likely to write. Fix: extend the "only history write" check, or the census sink, so both are refused or recorded.

## Verified

- **Mutation proof.** I re-ran M1 to M6 with `node tests/card.mjs`, and all six are killed by exactly the checks the body names:
  - M1: two checks fail.
  - M2: two checks fail.
  - M3: `every link a button emits ...`
  - M4: `the census reached every line ...`
  - M5: the openSetupSlot focus check.
  - M6: the stale-row check.

  The tree was restored clean after each.
- **Finder harnesses**, run from exports with matching sha1s:
  - `card_shapes.mjs` (677b7542, from 3930b421a):
    - RESULT picker_open 3 -> 1
    - RESULT total 33 -> 31
    - RESULT dead 1 -> 2; the added dead symbol is `top:openHaLink`
  - `v2_card_lines.mjs` (b3a1890e):
    - RESULT picker_lines 5 -> 3
    - RESULT total 36 -> 34
    - every other column is equal

  All of these match the body.
- **Census attacks.**
  - `R1_bypass`: a non-pending button navigating to `?domain=`. Caught by `every link a button emits ...`.
  - `R1d`: the wrong entry. Caught by the same check.
  - `R2_stale`: a planted `setup:configure` PENDING row. Refused by the stale-row check.
  - `R1c`: `location.assign`. Caught by the static guard.
  - `R1b`: a hand-built string equal to haLink's output. It passes. This is by design, because the census checks the output, not the spelling (alternative 3), and I do not block on it.
- **Routes.** I checked each against home-assistant-frontend 20260826.7, which is HA 2026.9.3's `frontend/manifest.json` pin:
  - `options`: `ha-config-integration-page` reads `#config_entry` from `location.hash`. `updated()` then `_highlightEntry()` scrolls to and highlights the row.
  - `entities`: `_setFiltersFromUrl` sets `ha-filter-states: []`, and `showDisabled = !stateFilters?.length || ...`, so disabled entities are listed.
  - `entity`: on `location-changed`, `_restoreMoreInfoFromUrl` uses `decodeMoreInfoUrl`, and `settings` is in `MORE_INFO_VIEWS`.
  - `config/entity_registry/get` has no `require_admin` in core 2026.9.3.
- **Step 17 and the architect note.** The added lines are one pure helper, `openHaLink`, the test, and C2. C2 is byte-identical to `patches/C2_setup_slot_deep_link.patch` at 3930b421a. No call site is converted, and the settings/diagnostics branch still calls `navigateTo(SETTINGS_PATH)`. The inbox Assign `return` keeps the old `scroll = 0` and render through `openSetupSlot`.
- **Other checks.**
  - `card_drift: identical in all 40 states`.
  - STRUCTURE RATCHET PASSED.
  - VERSION, the manifest and the notes are untouched.
  - No budget, closure or golden file moved.
  - CI's `mutation` lane printed `MUTATION TABLE PASSED (empty scope)`, so it evaluated no mutant on the card JS. The targeted mutants above are the only mutation evidence.
- **Not pinned before this PR either.** Dropping the render from the advisor deep link is unpinned at base too (`base_R3.txt`), so I do not charge it to this PR.

## Carry (routed by the orchestrator, not the fixer's)

R10-UX-HEALTH item 4 ("land on exactly the disabled entities") cannot be done with a URL. The frontend's `_setFiltersFromUrl` always clears the state filter.

## Not done

- No local card_browser screenshots. Playwright 1.56.1 is not installed on this box. CI's `browser` lane is green at this head, and card_drift shows the markup unchanged.
- At posting, these checks were still running: `closures`, `lane-proofs`, and CodeQL `Analyze (python)`. Every completed check was success, skipped, or neutral (CodeQL).
