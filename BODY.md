The Health tab's labels were not missing. They were painted at 1.24:1. 906fee95e (PR #2841) put `.health-row` and `.adv-inbox-row` on `--hpo-surface-2`, a literal chosen by `hass.themes.darkMode`, while their text stayed `--hpo-text`, the theme's `--primary-text-color`. Under dark theme variables with darkMode false (any dark theme without `modes.dark`), the rows draw #e1e1e1 on #f7f9fb. Under the mirror arm (light variables, darkMode true) they draw 1.11:1. **The defect shipped in every release from v7.0.5 through v7.1.11 (13 releases), not only v7.1.11.** Root-cause analysis: the root-cause seat's document, `handoff-body/r10-rca-card-health-text` at f00f4a0233031ab3dd6d38450d36e29d09bf8abf, file `BODY.md`, cited and not restated. This seat reproduced its measurements before touching code (Figures).

Both carries the RCA routes to this group (the setup toggle, the header chip) are built in this diff. The issue's Root cause section and `bugclasses.json`'s P9 `rca` entry are the orchestrator's, as the RCA records.

No issue exists for the owner's report (tvofi, 2026-11-11, "Live bug on v7.1.11. All text in the "Health" Card tab is missing"). The orchestrator links it.

What changed:

- **The owning seam: the surface-2 pairing rule.** In the card stylesheet (`cardStyleBlock`), one rule now puts a text block on `--hpo-surface-2` and re-points `--hpo-text`/`--hpo-text-2` at `--hpo-ink`/`--hpo-ink-2`, for `.tile, .hl-stat, .hl-narrative, .health-row, .adv-inbox-row`. Before, the tiles had the pair and the two row rules carried only the surface. `.health-row` and `.adv-inbox-row` no longer declare a background of their own, so the surface cannot be given again without its ink. There are no per-row colour patches.
  - Alternatives considered: setting `color` on each row rule. It lost because it keeps two owners of one pair, which is the shape 906fee95e broke. Moving the rows back onto the theme's `--secondary-background-color` lost because it read 1.20:1 on themes that do not define that colour (H3a).
- **Carry 1, the Setup page's pressed layout toggle** (`.layout-edit-toggle.on`, also the tank bar's): its darkMode-literal `--hpo-accent` ink was drawn on the theme's card surface, at 2.95:1 and 2.32:1. It is older than 906fee95e. It now draws on `--hpo-surface-2` from the same switch: 5.48:1 light, 6.24:1 dark (literals). The wash also marks the pressed state beyond its 1 px border.
- **The barrier** (the RCA's countermeasure, state (c)). `themeMismatch` in `tests/card_browser.mjs` changes its unit. It no longer reads the selector list `.tile, .hl-stat, .hl-narrative, .status-pill` on the tile. It now reads every element that owns a visible text node, on the tile and on every dialog page that the rendered `.dlg-tab[data-page]` list offers, in both mismatch arms, at 4.5:1.
  - The check controls itself: at least 5 pages, every page has at least 5 runs, and at least 10 Health `.adv-text` and 3 Advisor `.adv-text` runs are measured. A sweep that found nothing to measure cannot pass.
  - It mounts on a standards-mode document. On `about:blank` (quirks mode) a table does not inherit `color`, so the Savings table read black-on-dark at 1.23:1, which no install renders.
  - SVG text is outside its unit, because its paint is `fill` and its surface is a sibling shape. The chart check in the same function and the P9 grid own SVG text.
- **The static companion in `tests/card.mjs`.** 906fee95e's check "the health and advisor rows take the surface their ink is drawn for" asserted only the background token, so it pinned the defect as correct. It now asserts that a rule listing each row sets `--hpo-surface-2` and re-points both text tokens at the ink literals. This encodes a design choice: surface and ink belong to one rule.
- **Carry 2, the header chip.** `healthPillHtml` counts `problems.length`, which is every Input Problem entry of any kind (unavailable, missing_entity, not_numeric, implausible, unknown_unit, stale). It said "N input(s) stale" for all of them. Each entry gets its own Health row whose pill names the kind, so the chip and the rows agree on the count but not on the word. The chip now reads "1 input problem" / "{n} input problems" (sv "1 indataproblem", de "1 Eingangsproblem"), and `docs/dashboard-card.md` says what it counts. A first wording, "needs attention", overlapped the dialog title in Swedish in a P9 grid cell (`P9 grid: no two text runs share ink`, local run). The shipped wording is no longer than v7.1.11's Swedish string.
  - The owner's "1 input stale while every visible tile reads Fresh" is explained if their one problem was a non-stale kind. Its row's label was then one of the 1.24:1 runs, and its pill read the kind ("Unavailable", "Out of range"), not "Stale". This is an inference: the owner's bundle is not in hand. The owner's theme is unknown, and this fix does not depend on it.

## Head

75839015cff572055184d30a69322781906a1a99, on origin/main 61afd4f2db10341ab9b86583944402b206eb4c78 (merge base); measured 2026-11-11 UTC.

## Mutation proof

Each mutant was applied to the card at the head and run through `themeMismatch` (`node tests/card_browser.mjs`). The static mutant ran through `node tests/card.mjs`. Then restored (`cmp` against the head's card).

- **M1**: the rows keep `--hpo-surface-2` but leave the ink rule (`.health-row, .adv-inbox-row { background: var(--hpo-surface-2, #f7f9fb); }`, with the shared rule cut back to `.tile, .hl-stat, .hl-narrative`). This is 906fee95e's shape. Red:
  - `R10 every own-text run on every dialog page clears 4.5:1 with dark theme variables, darkMode false` (Advisor and Health `.adv-text`, `.adv-sub`, `.adv-value`, `.model-value`, `.adv-act` at 1.24:1)
  - `... with light theme variables, darkMode true` (1.11:1)
  - `the health and advisor rows take their surface and its ink from one rule`
- **M2**: delete `background: var(--hpo-surface-2, #f7f9fb);` from `.layout-edit-toggle.on`. Red: both `R10 every own-text run ...` checks, each failing only on `setup button.layout-edit-toggle.on` (2.95:1 / 2.32:1).
- **M3**: the chip strings back at "1 input stale" / "{n} inputs stale" (and sv/de), on a card with the CSS fix applied. Red:
  - `the header pill reads 1 input problem (warn)`
  - `two failing inputs read 2 input problems`
  - `one unavailable input: the pill counts it and does not call it stale (en, sv, de)`
- **A vacuous mutant, disclosed.** Removing `.health-row, .adv-inbox-row` from the shared rule entirely (losing surface and ink together) stays green. That is 906fee95e^'s healthy pairing, not the defect, so M1 is the proof.

## Null control

- **Bisection of the barrier.** It fails at the merge base and at 906fee95e on the rows, and fails at 906fee95e^ only on the older toggle. With the toggle fixed it passes, so the barrier separates the defect from the healthy tree.
- **Matched arms.** The same sweep in the matched arms (dark variables with darkMode true, light with false) passes on the merge-base card and on the head's card. Both ends are green, which is why the earlier null result (BLOCKED.md at e83de0f05, emptiness tested in the matched arms) found nothing.
- **Non-skip.** On the head, the sweep measures plan 81, setup 10, savings 22, advisor 46 and health 59 runs, including 19 Health `.adv-text` and 7 Advisor `.adv-text` runs, so it passes by measuring.

## Figures

Every row below ran `node tests/card_browser.mjs` (`themeMismatch`), after `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, unless it names another command. The card under test is swapped with `git show <rev>:custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`. A ratio is the minimum WCAG ratio of a run's computed `color` against the first opaque background up its tree. "Runs" counts elements owning a visible text node.

| tree | dark vars, darkMode false | light vars, darkMode true |
|---|---|---|
| merge base 61afd4f2d (= v7.1.11 card) | FAIL, 67 runs under 4.5: rows 1.24:1, toggle 2.95:1 | FAIL, 67: rows 1.11:1, toggle 2.32:1 |
| 906fee95e | FAIL, 64: rows 1.24:1, toggle 2.95:1 | FAIL, 64: rows 1.11:1, toggle 2.32:1 |
| 906fee95e^ | FAIL, 2: toggle 2.95:1 only | FAIL, 2: toggle 2.32:1 only |
| head 75839015c | ok, 0 | ok, 0 |

- Tile checks (`R9-UI-3 every tile text run clears 4.5:1`, now selector-free on the tile) and `R9-UI-4 chart series`: ok in all four trees.
- Toggle literal pairs: `--hpo-accent` on `--hpo-surface-2` is 5.48:1 (#026aa8 on #f7f9fb) and 6.24:1 (#4fb3f0 on #242a30). These are the WCAG formula on the `CARD_TOKENS` literals, the same pair `tests/card.mjs`'s `PAIRS` already measures (`UI-3 tokens: pill, tile and text pairs clear 4.5:1 on the literals`).
- Seam enumeration (`fixer.md` step 8). Rule: every stylesheet rule whose `background` or `fill` is a darkMode-literal surface (`--hpo-surface-2`, `--hpo-ok-bg`, `--hpo-warn-bg`, `--hpo-crit-bg`, `--hpo-plot`). Enumerated by a regex over `cardStyleBlock`'s rules, plus a grep of the card outside it. Dispositions:
  - `.status-pill.tone-ok`, `tone-idle`, `tone-warn`, `tone-crit`, `tone-accent`: own `color` from the same switch. Already guarded.
  - `.tile, .hl-stat, .hl-narrative, .health-row, .adv-inbox-row`: closed in this diff.
  - `.layout-edit-toggle.on`: closed in this diff.
  - `.setup-box` (SVG `fill`): its text is re-pointed by `.setup-svg > g` (R10-UX-SETUP). Already guarded.
  - `.health-row[data-done="true"] .health-mark`: ink `--hpo-ok` from `.health-mark`, measured by this sweep. Already guarded.
  - Outside the stylesheet, one hit: `rect.panel` `fill="var(--hpo-plot, …)"` in `renderChart`, no text. Guarded by `R9-UI-4`.
- Gate scope: `python3 tests/closure.py select --diff 61afd4f2db10341ab9b86583944402b206eb4c78`, MODE: SCOPED, 12 scripts. `GATE_SCOPE=auto bash tests/run.sh`: every selected script ok except `tests/golden.py` (strict against the committed fixtures: "55 of 56 GOLDEN SCENARIOS CHANGED", and `GOLDEN_MODE=strict python3 tests/golden.py` at the merge base 61afd4f2d in the same container prints the same "55 of 56", so it is this container's solver build, CLAUDE.md rule 3; `GOLDEN_MODE=drift python3 tests/golden.py` at the head: "NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main", "NO STALE FIXTURE"). `node tests/card_browser.mjs` (no scope selects it): ALL BROWSER CHECKS PASSED, P9 grid MODE: FULL.
- `node tests/card_drift.mjs origin/main`: 44 of 45 states move and are claimed in `tests/golden/card_claimed_drift.txt` (the whole shadow root carries the stylesheet); `editor_schema` is identical.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

none

## Friction

none
