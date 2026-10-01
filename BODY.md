<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

R9-UX-2, lane UX (#1795, design of record `handoff/round9/state/alt/design/ux/DESIGN-UX.md` at 1a90e4cb, section UX-2). Part of #1795 and #201; the lane issue stays open for UX-3..7.

Before: the Advisor tab drew only the sensor ranking (`sensor_advisor`), so the money the other advisors publish, a missing sensor's monthly cost and a cheaper hot-water setpoint, never reached the card.

After: the Advisor tab opens with a "Worth doing" inbox ranked by monthly value, read from the three advisor sensors that are on by default (sensor gap, hot-water setpoint, valve target). Each row has at most one action, through a lane the card already owns: "Assign sensor" opens the Setup picker for the gap's top slot; "Open schedule" goes to the Plan tab's schedule editor; "Apply" on the valve target calls `assign_entity` with `entity_id: ""` and a manual setpoint (only when the valve is in manual mode). A "More advice, once turned on" section offers wood-stove timing, fuse size and compressor frequency with "Open settings" and never reads them. The empty, waiting (the advisor's own `waiting_for`) and error ("This advice is unavailable right now", with the sensor's `reason`) states are drawn. Today's sensor ranking and its assign flow follow, unchanged.

How. Module-level functions beside `advisorPageHtml` (`advisorRows`, `advisorInboxHtml`, `attachAdvisorInbox`, `advisorSignature`), no new host member. The advisor sensors join the render signature through `ADVISOR_SUFFIXES`, not `HEADLINE_SUFFIXES`, and none of the three opt-in advisors is in it. The hot-water monthly value is `(cost_per_day at the running setpoint − cost_per_day at the recommendation) × 30` from the sensor's own `candidates`. The valve row carries no money figure, so it follows every priced row. Strings are in `en` and `sv`. Only the card, its tests, its docs and fixtures change: no Python, so no structure metric moves and no budget is touched.

Departures from the brief, each deliberate:
- **Price of a degree is not on the card.** Nothing on main publishes it (`grep -rniE 'of a degree|price_per_degree|degree_price'` over the `.js`, `.py`, `.md`, `.json` and `.yaml` outside the audit records prints only unrelated prose about tenths of a degree, no sensor, attribute or tile), so there is nothing to read and an "enable to see" row for an option that does not exist would be false advice. It joins the inbox when a producer lands; the Forward-carry below says so.
- **"Open schedule" opens the Plan tab**, where the schedule editor is; it does not seed a value, since the editor holds the hot-water minimum, not the setpoint. UX-5 makes it a persistent "Apply".
- **An opt-in row is offered even when that advisor is already on.** Telling the two apart needs a read of the sensor, which `tests/entities.py` refuses for a disabled-by-default one.

Documentation (U5): `docs/dashboard-card.md` "The advisor page" is rewritten around the inbox and embeds the regenerated `advisor-light.png` and `advisor-dark.png` (`HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs`), replacing the hand-drawn figure. The page fixture in `tests/card_browser.mjs` gains the three advisor sensors. The embed removal moves the D6 counts by one each (91 links, 21 images), regenerated in `tools/audit/round4/D6/`. The other pages re-rendered with raster noise only and are left as they were (`setup-*.png` reverted). The product page's gallery is not on main (no `docs` gallery slot exists), so no slot is owed.

`tests/card_browser.mjs` is code-owned: this merges on tvofi's approving review at the head.

## Head

98c0710e6ff1ad85866ee981522767797c5af099 (code head, `origin/main` 480a6911 merged in; main did not touch the card)

## Mutation proof

The card is not in `tests/mutation_table.py`'s production set, so no site is pinned. Hand mutants instead, each a one-line replace in the working tree at the code head, then `node tests/card.mjs`, failing names read from the output (`/tmp/ux2/mut.py`; rc is 0 on the unmutated head):

- M1 rank ascending: rc 1, failing 1: `rows rank by monthly value: gap 180 > hot water 45 > valve (no money)`
- M2 7 days a month: rc 1, failing 1: `a priced row shows its monthly value as an estimate`
- M3 valve threshold 0.5 → 5: rc 1, failing 2: the ranking check and `Apply on the valve target calls assign_entity with a manual setpoint`
- M4 Apply without the manual-mode guard: first run rc 0, failing 0, a survivor. Killed by `a valve not in manual mode shows the advice without an Apply button`, added in the last commit: with M4 applied rc 1, failing 1 on that name
- M5 signature drops the advisors: rc 1, failing 1: `the card's render signature includes the advisor sensors`
- M6 Apply payload `entity_id: "x"`: rc 1, failing 1: `Apply on the valve target calls assign_entity with a manual setpoint`
- M7 wood advisor added to `ADVISOR_SUFFIXES`: rc 1, failing 1: `the card never reads a disabled-by-default advisor`
- M8 waiting branch removed: rc 1, failing 1: `an advisor that is waiting shows its own reason`
- M9 opt-in rows removed: rc 1, failing 1: `off-by-default advisors are offered as enable-to-see rows`
- M10 assign opens the wrong key: rc 1, failing 1: `Assign sensor opens the setup picker for the gap's top slot`

Failing test first: commit 9bc74be9 (tests only) against main's card fails 13 of the 14 new checks then in the file (a 15th, the manual-mode guard, came with M4's kill); the 14th, `the card never reads a disabled-by-default advisor`, passes vacuously there and is pinned by M7 instead.

## Null control

- The unmutated head: `node tests/card.mjs` rc 0, `ALL CARD CHECKS PASSED`, which is what the M-list is read against.
- `tests/card_drift.mjs` at the merge base: 39 states moved and claimed, 1 identical (`editor_schema`). Every moved state moves through the one stylesheet; `advisor_page` also moves in markup. A scan of the diff lines of the other 38 for anything that is not an `adv-` rule found none; the claims in `tests/golden/card_claimed_drift.txt` say which is which.
- Ranking null: the three-row fixture has a 180, a 45 and an unpriced row; M1 reverses it and the check goes red, so the ranking check is not satisfied by any order.

## Figures

- `node tests/card.mjs`: ALL CARD CHECKS PASSED at 98c0710e.
- `node tests/card_drift.mjs` (merge base 480a6911 is main's tip): "39 state(s) moved and claimed, 1 identical".
- `node tests/card_browser.mjs` (`HPO_PAGES_OUT=docs/img/card`): ALL BROWSER CHECKS PASSED at the commit before the merge, P9 grid MODE: FULL; main's merge touched no card or browser file, so it is not re-run.
- Scoped gate selection, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: "MODE: SCOPED -- 11 script(s) run, 17 scoped out". Run at 98c0710e with `GOLDEN_MODE=drift`: `deployment_shape`, `doc_claims`, `entities` (2034 checks), `env_drift`, `features`, `golden`, `harness_headers` (94 checks), `md_tables`, `plan_view`, `card`, `card_drift`: all passed. `tests/stress.py` is not in the selection.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node .claude/workflows/brief_lint.mjs`: TOTAL: 0 error(s) across 45 file(s).
- The monthly figure in the screenshot is the fixture's own: `(12.00 − 10.50) × 30 = 45`, and 180 is the fixture's gap, both labelled "≈" on the page.
- Contrast: the inbox button first used the accent colour on the surface-2 row and measured 2.09:1; it now inherits the text colour. The P9 contrast check is the instrument, and it reads green at the head.

## Red checks

Two local reds, neither on a pushed commit's CI:
- `card_browser.mjs` "P9 grid: every visible text run clears WCAG AA": the new button's accent colour, 2.09:1 against 4.5. Cheaper detector: none; the rendered pixel contrast is only measurable in the browser, which is the gate that found it. Fixed before the push that carried the stylesheet.
- `harness_headers.py` "the executed harnesses leave their committed output byte-identical": the D6 link and image counts moved with the embed. The detector is already seconds-cheap; the fix is the regenerated `tools/audit/round4/D6/` in the same commit.

## Forward-carry

`.claude/workflows/carry-1795.json`, stage R9-UX-5 (hot-water "Apply" through a persistent schedule field): `advisorRows` in the card gives the hot-water row `act: "open_schedule"`; UX-5 changes that to an apply action and the Plan-page fallback goes. The roster's R9-UX-5 brief on handoff/audit-r9-fixplan should carry the same text; sent to the coordinator.

`.claude/workflows/carry-1795.json`, a later UX stage: a producer for "price of a degree" does not exist on main. When one lands, its read belongs in `advisorRows` and its suffix in `ADVISOR_SUFFIXES` only if the sensor is enabled by default.

## Friction

- fixer.md-2: unclear: `mutation_table.py --scope changed` has no JavaScript sites, so a card-only PR's mutation proof is hand-run and nothing pins it; the M-list above is that proof.
- fixer.md-5: cost: this cloud seat has no Python 3.14 or Home Assistant, so typing and real-HA `ha_contract` are unrun; no Python changed and CI is their authority.
