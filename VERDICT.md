Fix review: blocked ccdcb4d4039bc9e513f990fdd11d9f71d220811f harness: class-open setAttribute("href") link passes the census and the static guard

bus-nonce: 7c02753caf67ca0a26da038a58f7d1d1

This is round 2. It judges the delta from 0b4d46abd: `tests/card.mjs` only, through 6a2decd2d and 10a11f29e, plus a merge of main. I reviewed from a detached worktree at ccdcb4d4039bc9e513f990fdd11d9f71d220811f. The card blob there is cb4035b6, identical to round 1, and the merge base card is a80c4356, unchanged. The roles diff against origin/main is empty.

## Blocking

**A literal `setAttribute("href", ...)` link is still invisible (R7b).** The plant adds an empty `<a class="zz"></a>` to the Health diagnostics row. In `attachAdvisorInbox`, it then runs `a.setAttribute("href", "/config/integrations/integration/heatpump_optimizer")` on it. Result: `RESULT mutant=R7b_setattr_href_literal rc=0 fails=0`. Two things miss it:
- The static guard `/\bhref\s*=/` misses `"href",`.
- The dynamic `anchors()` walk reads only `n.href`, which the stub DOM does not fill from `setAttribute`.

This is the class (b) asked to close, written the ordinary way, so I am not treating it as an obfuscation. Fix either half, or both:
- make `anchors()` also read `getAttribute("href")`;
- add `setAttribute\(\s*["']href` to the static guard.

Then re-run R7b.

## Verified (the delta's claims)

- **(c) is closed.** R4 (`entryId = null;`) is now red on `openHaLink asks the registry for its own plan sensor and links this entry`. The direct drive checks two things:
  - the registry request is for `DEFAULT_SPACE`, and the resolved-entry links are `haLink("entities"|"entity", ENTRY)`;
  - the refused-lookup fallback is `haLink("options", null)`.
- **(b) is closed for the shapes I planted in round 1:**
  - R5 (an anchor `href` in the template) is red on the dynamic sink (`health:a`) and on the static guard.
  - R6 (`hass-more-info` CustomEvent) is red on the sink and on the static guard.
  - R6x (`new Event("hass-more-info")` with the literal type) is red on the static guard.
  - R6z (CustomEvent with the type assembled at run time) is red on the sink.
- **PENDING rows are one path each.** R8, a pending `settings` button switched to a different wrong path, is red on `every link a button emits ...` and on the stale-row check. R2 (a planted stale `setup:configure` row) is still refused.
- **M1 to M6 are all killed again.** M1 now reddens only `haLink builds the three deep links ...`, because the stale-row arm keys on the row's own path. The body says the same.
- **Earlier attacks still behave as in round 1.** R1 and R1d are red on the sink, R1c on the static guard. R1b (an identical hand-built string) passes, by design.
- **Finder harnesses carry from round 1** because the card blob is unchanged:
  - `card_shapes.mjs`: RESULT picker_open 3 -> 1, total 33 -> 31, dead 1 -> 2 (`openHaLink`).
  - `v2_card_lines.mjs`: RESULT picker_lines 5 -> 3, total 36 -> 34.
- **The card test passes at this head:** `node tests/card.mjs` prints ALL CARD CHECKS PASSED.
- **Forward-carry is on main.** #2287 (9b1320d37 is an ancestor of origin/main) carries every item into the brief text of R10-ADVISOR, R10-UX-SETUP and R10-UX-HEALTH, including the disabled-only filter limit.

CI: all 45 check-runs at this head concluded success or skipped.

## Residual, not blocking

- R6y and R7 split the event type or attribute name into string pieces (`"hass-" + "more-info"` on a plain `Event`, and `"hr" + "ef"`). Both survive. A static check cannot be expected to defeat deliberate obfuscation.
- R3, dropping the render from `openSetupSlot`, is unpinned. It was unpinned at base too.
- The body's twelve plants are scripted in an out-of-tree `round2_mutants.sh`, though each plant is spelled out in the body. Mine are in the evidence `mut.py`.
