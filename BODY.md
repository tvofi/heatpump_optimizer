# RCA r10-card-health-text: Health-tab labels blank on a dark theme

Seat: root-cause (dev/governance/roles/root-cause.md), beside R10-HOTFIX-CARD-HEALTH-TEXT, never inside it. Trigger: the defect reached a release (defect-root-cause.md, first trigger). Owner report, tvofi 2026-11-11 about 21:27Z: "Live bug on v7.1.11. All text in the "Health" Card tab is missing". Measured at main 61afd4f2d. The card JS, tests/card.mjs, tests/card_browser.mjs and tests/card_rig.mjs are byte-identical between main and v7.1.11 (`git diff --quiet v7.1.11 HEAD -- ...` exits 0).

## Verdict

**Second pass (below) supersedes this verdict as the explanation of the owner's screenshot.** The first-pass cause stays a real, separate defect, but it does not produce the owner's state.

- **Cause:** the text is not missing; it is painted at **1.24:1**. Commit 906fee95e (PR #2841, R10-CARD-VOICE, 2026-10-25) moved `.health-row` and `.adv-inbox-row` onto `--hpo-surface-2`. That token is a literal chosen by `hass.themes.darkMode`. The rows' text was left on `--hpo-text`, which is the theme's `--primary-text-color`. Under a dark theme that Home Assistant reports as `darkMode: false`, the rows draw #e1e1e1 on #f7f9fb.
- **Not a v7.1.11 regression:** the defect was first shipped in **v7.0.5** (2026-10-27) and is present in all 13 releases from v7.0.5 to v7.1.11. The suggested lead does not hold: `SHIPPED_LANGS` does not exist at v7.1.11. The v7.1.10 → v7.1.11 card diff adds one catalogue key (`setup.dhw_combi_caption`) and the combi pipe, and nothing on the Health path.
- **Process state: (c).** The barrier for mismatched themes (`themeMismatch`, R9-UI-3 review) existed and ran green on v7.1.11. Its unit does not reach dialog pages: a fixed list of four selectors on the dashboard tile view only.
- **Cost test:** build it. The standing cost is about 1 s per browser-lane run, against a 309 s lane. The defect is also an instance of the barriered class P9, which owes a barrier whatever the cost test says.
- **Countermeasure:** change `themeMismatch`'s unit from a selector list to every own-text run on every dialog page, in both mismatch arms. It is demonstrated below: it fails on v7.1.11 and v7.1.10, and passes on a stand-in fix and on 906fee95e^.

## 1. Cause, reproduced

Probe (scratch, not in the tree): a Playwright/Chromium page built like `healthLayout`, using `tests/card_rig.mjs` fixtures and the `healthPageStates` payload (one stale input plus model rows). It mounts the card, opens each dialog page, and measures every element that owns a text node: computed `color` against the first opaque background up the tree, with the WCAG ratio. It runs four arms: light vars with darkMode false, dark vars with darkMode true, **dark vars with darkMode false** (a community dark theme), and light vars with darkMode true.

Health page, v7.1.11, dark vars with darkMode false:

| element | runs | min ratio | painted |
|---|---|---|---|
| `.adv-text` (input names, model labels, checklist texts, support/debug titles) | 16 | 1.24:1 | rgb(225,225,225) on rgb(247,249,251) |
| `.adv-sub` (ages, details) | 10 | 1.24:1 | same |
| `.model-value` | 4 | 1.24:1 | same |
| `.adv-act` (Show, Download diagnostics) | 4 | 1.24:1 | same |
| `.health-h` headings | 4 | 13.03:1 | on the card surface #1c1c1c |
| `.status-pill` Fresh / Stale | 3 / 1 | 5.04 / 5.29:1 | own `--hpo-ok`/`--hpo-warn` pair |
| `.health-mark` ✓ | 3 | 5.04:1 | own pair |

This matches the report: headings, status chips and check marks are visible; every row label is not. The mirror arm (light vars with darkMode true) gives 1.11:1 (#212121 on #242a30) on the same elements. The two matched arms are clean (15.26:1 and 11.08:1), which is why every tree the gates render looks right.

Mechanism, in card source: `CARD_TOKENS` declares `--hpo-text` as `var(--primary-text-color, …)` (theme-driven) and `--hpo-surface-2` as a bare literal picked by `tokenDeclarations(darkMode)`. The token comment calls out exactly this hazard: "text taken from that theme's --primary-text-color would then be light on the light surface (1.24:1, R9-UI-3 review)". `.tile`, `.hl-stat`, `.hl-narrative` and `.setup-svg > g` re-point `--hpo-text` to `--hpo-ink` for that reason. `.health-row` and `.adv-inbox-row` do not. 906fee95e replaced `background: var(--secondary-background-color, #f5f5f5)` with `var(--hpo-surface-2, #f7f9fb)`. Its comment says "the text is the card's --hpo-text, so the surface is the card's --hpo-surface-2". `--hpo-ink` is the token paired with surface-2; `--hpo-text` is not.

Bisection: the same probe on `906fee95e^` gives 11.27:1 on Health `.adv-text` in the dark/false arm (pass), and on `906fee95e` 1.24:1 (fail). v7.1.10 is identical to v7.1.11: 16 runs under 4.5:1, and 1.24:1 on Health.

**How far the class reaches.** The all-pages sweep in the mismatch arms found the same mechanism on the **Advisor** inbox rows (`.adv-inbox-row`): `.adv-text`, `.adv-sub` and `.adv-act` at 1.24:1 and 1.11:1. 906fee95e changed that rule too. No other page has text under 2:1. `--hpo-surface-2` has 12 uses in the v7.1.11 card. The rest either set their own ink (tiles, pills, `.setup-svg > g`) or carry no text. The sweep covers one fixture state, so states outside `pageStates`/`healthPageStates` were not reached.

A separate, older finding of the same theme-mismatch family, which 906fee95e did not cause: the Setup page's `.layout-edit-toggle.on` reads 2.95:1 (rgb(2,106,168) on #1c1c1c) under dark vars with darkMode false, and 2.32:1 under the mirror arm. It is already present at `906fee95e^`. Carry: R10-HOTFIX-CARD-HEALTH-TEXT

Not explained by this cause, and recorded as open:
- The owner sees the header chip say one input is stale while every visible tile reads Fresh. In every arm the stale row renders first with a visible warn pill (5.29:1). This cause does not produce that symptom. Note that `health.pill_one` says "stale" for every problem kind (`n = problems.length`). Carry: R10-HOTFIX-CARD-HEALTH-TEXT
- The owner says values and the Download diagnostics button render. Under HA's default dark tokens the probe puts `.model-value` and the button label at 1.24:1 as well; only the button's border stays visible. The owner's theme colours are unknown. The fixer's owner question (BLOCKED.md on handoff-wip at e83de0f05) asks for the computed colour, which settles it. The darkMode-false precondition is inferred from the symptom pattern, not observed on the install.

The fixer's null result (BLOCKED.md: 0 empty labels across en/sv/de, light and dark, three widths) is consistent with this. Its "dark" arm set darkMode true with dark vars, the matched arm. It also tested emptiness (`textContent`, width), not ink.

## 2. Process state: (c), with evidence

Gates run on v7.1.11's card tree, measured in this seat:

| gate | result on v7.1.11 | why green |
|---|---|---|
| `tests/card_browser.mjs` (CI `tests / browser`, required) | `ALL BROWSER CHECKS PASSED`, rc 0, 5m09s | see the next three rows |
| ↳ `themeMismatch` (R9-UI-3 review, the mismatch barrier) | 2 `ok` lines: "tile, headline-stat and pill text clears 4.5:1 with dark theme variables, darkMode false", and the mirror | Its unit is `root.querySelectorAll(".tile, .hl-stat, .hl-narrative, .status-pill")` on the dashboard tile. It never opens the dialog, so no Health or Advisor row is in it. |
| ↳ P9 grid (class P9 barrier) | `MODE: FULL`, 360 cells, 22,776 text runs, "every visible text run clears WCAG AA" ok, 277 s | Every cell "sets [darkMode] in lockstep with its theme variables". The off-lockstep cells vary the OS scheme, not darkMode (p9Grid cells). Mismatched pairings are deferred to themeMismatch ("the mismatched pairings are themeMismatch's"). The arm that blanks the rows is never a grid cell. |
| ↳ `healthLayout` (UX-HEALTH B/C) | 10 `ok` lines | Geometry only (hit-test, grid share). It renders dark with `darkMode: theme === "dark"`, the matched arm. |
| ↳ P40 page figures | ok | Compares figure size and structure hash (`pages.json`), not pixels. `cardPages` renders light/false and dark/true only. |
| `tests/card.mjs` | `ALL CARD CHECKS PASSED`, rc 0, 2m12s | "UI-3 tokens: pill, tile and text pairs clear 4.5:1 on the literals" measures `PAIRS`, including `[--hpo-ink, --hpo-surface-2]`. The rows draw `--hpo-text`, a pair not in `PAIRS`, and the static check cannot follow inheritance. 906fee95e itself added "the health and advisor rows take the surface their ink is drawn for", which asserts the background token and never the ink. It pins the defect's own surface as correct. |
| `tests/card_drift.mjs` | not run here | Differential against a ref, and it sets no darkMode or dark vars (scout: no `darkMode`/theme in `card_drift.mjs` or `card_rig.mjs`). It cannot see ink. |
| per-language catalogue (STRINGS parity, `health.input_*` equality) | ok | Not involved. All labels exist, and `L()` falls back to English and then to the key, never to "". |
| a11y / visible-text check | none exists outside the contrast checks above | n/a |

**State (c):** a process for exactly this hazard existed and was followed. The card's own token comment names the 1.24:1 pairing, and `themeMismatch` was built for it in the R9-UI-3 review. CI ran it green on PR #2841 and at every stamp since v7.0.5. It did not produce the intended result because its unit is a selector list frozen to the four elements that drew on a darkMode literal when it was written. 906fee95e put two more element families on such a surface, and no barrier enumerates "what draws on a darkMode-literal surface". This is not (a): the check exists. It is not (b): it ran. It is not (d) either: the card's darkMode/theme split is the same precondition the check was written for. Here the barrier's unit did not reach the instance, which is the case `root-cause.md` §2 names. The countermeasure changes the unit.

Class: an instance of barriered class **P9** ("card UI: … missing colour token …", `dev/audit/config/bugclasses.json`, barrier = the P9 grid, 37 recorded instances R1–R9, rca `R9-P9`). Text contrast under a theme/darkMode pairing is P9's (D4-s1-01, R9-UI-3). Any instance of a barriered class owes a class-eliminating barrier (defect-root-cause.md, tvofi 2026-09-25).

## 3. Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, in wall-clock per occurrence.

- **cost(countermeasure, recurring):** the scratch detector runs all 7 dialog views × 4 arms in **2.0 s** wall, browser launch included (2.01 s on v7.1.11, 1.96 s on the stand-in). Only the 2 mismatch arms are new, so about **1 s** per browser-lane run against the lane's measured **309 s**, under 0.4 %. The alternative, adding the two mismatch arms as P9 grid cells, costs 2/7 × 277 s ≈ **79 s** per run. It is rejected on cost.
- **cost(defect):** shipped for **15 days** (v7.0.5 2026-10-27 to the 2026-11-11 report), across **13 releases**. It blanked the Health and Advisor pages for every install on a theme without `modes.dark`. Repair cost in this round: one fixer seat (blocked on reproduction for want of the arm), this seat, a fix review and a stamp.
- **P(recurrence):** class P9's measured frequency is 37 instances over rounds R1–R9 (~4 per round). Escapes to a release: `RELEASE_NOTES.md` v7.0.0–v7.1.11 holds 0 contrast fixes, so this is the first released one in that window. The recurrence route is open: any new rule that puts text on `--hpo-surface-2` (12 uses today) without re-pointing ink repeats it, and no check enumerates those rules.
- **Verdict:** 1 s per run against a 15-day release-wide escape at a class rate of ~4 per round: **build**. It is also owed regardless, as a P9 instance.

## 4. Countermeasure (proposal; tests are policy-adjacent, so the owner decides)

Addresses state (c) by changing the unit. In `tests/card_browser.mjs` `themeMismatch`, replace the selector list with a sweep of **every element owning a visible text node on every dialog page** (`.dlg-tab[data-page]`) plus the tile. Run it in both mismatch arms at the existing 4.5:1 floor. A selector-free unit cannot be outrun by a new class name. The existing P9 reach rule ("every card rule that sets a colour is rendered in some cell") does not cover a rule that sets only `background`, which is how `.health-row` escaped it.

Demonstration with the scratch detector (`FLOOR` = minimum ratio; rc 1 = fails):

| tree | floor 4.5 | floor 4.5, toggle excluded | floor 2 |
|---|---|---|---|
| v7.1.11 (defect) | rc 1, 16 runs | rc 1, 14 | rc 1, 14 |
| v7.1.10 (also affected; not a null control) | rc 1, 16 | rc 1, 14 | rc 1, 14 |
| stand-in fix (scratch copy of the v7.1.11 card: `.health-row` and `.adv-inbox-row` re-point `--hpo-text`/`--hpo-text-2` to `--hpo-ink`/`--hpo-ink-2` and set `color`, as `.tile` does; never pushed) | rc 1, 2 (the toggle) | **rc 0, 0** | **rc 0, 0** |
| 906fee95e^ (null control, healthy tree) | rc 1, 2 (the toggle) | **rc 0, 0** | **rc 0, 0** |

Non-skip control: on the stand-in, the sweep reports Health `.adv-text` n=16 and Advisor `.adv-text` n=4 in all four arms (15.26:1 and 11.08:1), so it passes by measuring, not by skipping. On a tree that is also correct, the 4.5 floor stays red on `.layout-edit-toggle.on` (2.95 / 2.32:1). The countermeasure therefore lands with that toggle fixed, or the lane goes red on main. That is a real second finding, not an allow-list case (the P9 barrier is a zero rule with no allow-list).

A cheaper static companion, not demonstrated and so not proposed as the barrier: a `tests/card.mjs` rule that every stylesheet rule whose `background` is a darkMode-literal token (`--hpo-surface-2`, `--hpo-ok-bg`, …) must also set `color` or `--hpo-text` from the same switch.

## Forward carries

- The setup `.layout-edit-toggle.on` contrast at 2.95 / 2.32:1 under the mismatch arms. It predates 906fee95e and blocks the countermeasure at the AA floor. Carry: R10-HOTFIX-CARD-HEALTH-TEXT
- The fix must cover `.adv-inbox-row` (Advisor) as well as `.health-row`: same commit, same mechanism, same 1.24:1. Its failing-first test needs the dark vars with darkMode false arm; the arm the fixer probed (dark/true) cannot fail. Carry: R10-HOTFIX-CARD-HEALTH-TEXT
- The header chip "1 input stale" against all-Fresh tiles is not explained by this cause. Carry: R10-HOTFIX-CARD-HEALTH-TEXT
- The issue's **Root cause** section and the `rca` entry on P9 in `bugclasses.json` pointing at `dev/audit/rca/r10-card-health-text.md` are the orchestrator's to write when it commits this document. Carry: dismissed: the orchestrator's commit of this file carries it

## Figures

Every figure above was measured in this seat on main 61afd4f2d. Instruments: the scratch probe (Playwright Chromium, WCAG relative luminance), `node tests/card_browser.mjs`, `node tests/card.mjs`, `git merge-base --is-ancestor 906fee95e <tag>` over `git tag -l 'v7.*'`, and `git log -1 --format=%ad`.

# Second pass: the owner's steady-state screenshot

Owner facts (OWNER-FACTS-2): default Home Assistant theme in auto mode, OS dark, no recent switch, a reload does not cure it. That is the matched arm: dark variables with darkMode true. The first pass measured that arm at 11.08:1, so its darkMode-false precondition does not hold on this install.

## Verdict (second pass)

- **Not a colour defect.** Home Assistant's real default dark variable set renders every Health label at **11.08:1** in Chromium, on v7.1.11 and on every v7.x tag. No token falls back to a card literal.
- **The screenshot's state is a missing label box, not a dim label.** In the owner's rows the value and bar sit at the row's left edge and nothing is drawn to their right. In this card that geometry occurs only when `.adv-text` produces **no layout box**. A label painted in any colour, including the row surface colour (1.00:1), or an empty label keeps its box. `.adv-text` is the only item in the row that grows (`flex: 1 1 14em`), so a label with a box pushes the value to the right edge (x = 758 of a 906 px row). Removing the box is the only perturbation of the four tried that puts the value at x = 11, the bar right after it, and the input pill, the tick and the button at the left.
- **Nothing in the tree removes that box.** The card has no rule that hides, collapses or reorders `.adv-text`: the only `display: none` is `.setup-svg.editing .setup-flow`, and there is no `@container` rule, no `order` and no `visibility`. Every Health row builder emits `<span class="adv-text">` unconditionally. Bisection over all 18 v7.x tags found no tree that reproduces the state under HA's dark set.
- **Cause: not established in this seat.** The state needs a factor outside what the tree and Chromium reproduce: the owner's rendering engine (macOS, so possibly Safari or the HA companion app on WebKit, which this container cannot run; only Chromium is installed and `playwright install` is not allowed), or a card build other than v7.1.11 reaching the browser. One owner reading settles which (see Owner question).
- **Why the gates read clean:** they render this state correctly. In Chromium the matched-dark cells draw the labels with a box at 11.08:1, as Home Assistant's own variables do. A failure that removes the box is also outside what the P9 grid's unit can report: the grid measures visible text runs, and a run with no box is not a low-contrast run. It is not counted at all.

## 5. Home Assistant's default dark variables, pinned

Source: home-assistant/frontend tag **20261028.5** (commit e32bc0696ebe, 2026-11-06), `src/resources/theme/color/`. The light blocks (`colorStyles`, `semanticColorStyles`, `coreColorStyles`, `waColorStyles`) are a stylesheet on `html`. The dark blocks (`darkColorStyles`, 52 declarations, and `darkSemanticColorStyles`, 88) are written by `applyThemesOnElement` as inline style when `darkMode` is true, so they override the light values. The frontend sets no `color-scheme` anywhere. Assumption: the target element is `html` (the `main` flag). This sparse checkout has no call site that shows it.

The six Home Assistant variables the card's tokens read, under that set:

| card token | HA variable | in the dark block? | value | card literal (dark) |
|---|---|---|---|---|
| `--hpo-text` | `--primary-text-color` | yes | #e1e1e1 | #e1e1e1 |
| `--hpo-text-2` | `--secondary-text-color` | yes | #9b9b9b | #9b9b9b |
| `--hpo-surface` | `--card-background-color` | yes | #1c1c1c | #1c1c1c |
| `--hpo-divider` | `--divider-color` | yes | rgba(225, 225, 225, 0.12) | #3a3a3a |
| `--hpo-primary` | `--primary-color` | **no**, falls to the light block's `var(--ha-color-primary-40)` = **#009ac7** | #009ac7 | #03a9f4 |
| `--hpo-on-primary` | `--text-primary-color` | **no**, falls to the light block's #ffffff | #ffffff | #ffffff |

`--ha-card-background` is defined in neither block; `ha-card` falls back to `--card-background-color`. The tokens without an HA variable (`--hpo-surface-2` #242a30, `--hpo-ink` #e1e1e1, the status pairs) are card literals chosen by darkMode: true. Every token resolves to a theme value or to its own literal, never to an unintended one. The rig's `THEMES.dark` (tests/card_browser.mjs:97) matches HA on every text and surface variable. It differs on `--primary-color` (#03a9f4 against HA's #009ac7), which colours no Health text.

## 6. Reproduction, per element

Probe (scratch, not in the tree): Playwright Chromium, 1000 px viewport, scale 2, OS scheme dark, `hass.themes.darkMode: true`. The fixture is `healthPageStates(pageStates(plan))`, taken verbatim from tests/card_browser.mjs. HA's light blocks are loaded as the `html` stylesheet and its dark blocks as inline style on `html`. The card is v7.1.11 (= main 61afd4f2d). Ratios are WCAG, against the first opaque ancestor background.

| element | n | colour | background | ratio |
|---|---|---|---|---|
| `.health-h` heading | 5 | #e1e1e1 | #1c1c1c | 13.03 |
| `.health-row .adv-text` (labels) | 19 | #e1e1e1 | #242a30 | **11.08** |
| `.adv-sub` (details, opacity 0.8) | 13 | #e1e1e1 | #242a30 | 11.08 |
| `.model-value` | 4 | #e1e1e1 | #242a30 | 11.08 |
| `.adv-act` (Download diagnostics) | 4 | #e1e1e1 | #242a30 | 11.08 |
| `.status-pill` Fresh | 4 | #1fad6b | #1c3027 | 4.83 |
| `.health-mark` ✓ | 6 | #1fad6b | #1c3027 | 4.83 |

The rig's `THEMES.dark` gives identical figures. The background and surface match the screenshot (#1c1c1c; #242a30 against #242a31 in lossy WebP). The value text #e1e1e1 matches the screenshot's brightest pixel, #e2e8ed. **Why the value is light and the label is not, in the same row:** in v7.1.11 they cannot differ in colour. `.adv-text` and `.model-value` set no `color` and both inherit the row's. So the screenshot's difference has to be a box, not an ink.

Geometry discriminator, learned-model row "heat_loss" (offsets in CSS px from the row's left; row 906 px wide):

| arm | label box | value x | bar x | row height | matches screenshot |
|---|---|---|---|---|---|
| HA dark, as shipped | 11..746 | 758 | 825 | 47 | no: label drawn, value at the right |
| label ink = row surface (#242a30, 1.00:1) | 11..746 | 758 | 825 | 47 | no: value still at the right |
| label text emptied | 11..746, 0 tall | 758 | 825 | 33 | no: value still at the right |
| **label `display: none`** | **none** | **11** | **78** | **33** | **yes**: value and bar at the left, nothing to their right; the pill, tick and button also move to the left |

In the last arm the bar ends 148 CSS px into the row, about 300 px at the screenshot's scale. That fits the orchestrator's 1700 px single-colour region to the right of the bar in a 2000 px image. The first pass's arms, which only change ink, are all of the first two kinds. That is why neither of them reproduces the screenshot.

Bisection: `haDark` arm over every v7.x tag (v7.0.0–v7.0.5, v7.1.0–v7.1.11). Every tag draws the label with a box: 11.27:1 up to v7.0.4 and 11.08:1 from v7.0.5. The value sits at x = 779 (v7.0.0–v7.0.4) or x = 758 (v7.0.5 onward). **No v7.x tag reproduces the state under HA's dark set in Chromium**, so there is no in-tree commit to bisect to.

## 7. Why the matched-dark gate cells read it as clean

- **P9 grid (dark cells, darkMode in lockstep):** the cells use `THEMES.dark`, which equals HA's set on every variable the Health text reads (section 5). In Chromium they render the same 11.08:1 labels this probe measured with HA's own variables. They are not wrong about this state; they never contain it. Their unit is also blind to it. The grid asserts that "every visible text run clears WCAG AA". A label with no box is not a visible run, so it is neither measured nor counted as missing. No cell asserts that a text node which exists in the DOM has a box.
- **healthLayout (dark, 375 / 1280 px):** it checks the first row's hit-test, the input grid's share of the page and the number of tiles per line. A row whose label has no box still passes all three: the row is still hit at its top edge, and the grid is unchanged.
- **The fixer's null result** (0 empty labels, en/sv/de, three widths) measured `textContent` and width in Chromium, where the box exists. That is the same reason.
- **Engine.** The browser lanes run Playwright Chromium. This seat's container holds Chromium alone (`/opt/pw-browsers`); CI's image was not inspected. If the owner's client is WebKit, a Chromium-only lane cannot reach this state, whatever its unit.

## 8. Process state (second pass): provisional

Until the owner's reading names the factor, this is provisional between **(a)** and **(d)**:
- If the client is WebKit and v7.1.11 itself drops the label box there: **(a)** for engine coverage. No process known to this seat renders the card in a non-Chromium engine. The barrier's form would be a WebKit arm of a box-presence check: every text node in the DOM of a dialog page has a non-empty client rect. That check is cheap (same 2 s probe shape) but needs the WebKit browser in the CI image.
- If a build other than v7.1.11 reaches the browser: not a card defect. It is a delivery or caching question, outside this tree.

A box-presence assertion added to the P9 sweep closes the unit blindness of section 7 in any engine. It is proposed only once a failing case for it is demonstrated, and none is here: the defect is not reproduced in this seat, so the countermeasure cannot be shown failing on it (defect-root-cause.md, "A detector must be shown to detect").

## Owner question (the one reading that settles it)

On the Health page as it appears now: (1) the browser, e.g. Safari, Chrome or the HA macOS app; (2) in its inspector, for one model-row label (`span.adv-text` inside `.health-row.model-row`), the computed `display`, `width` and `color`; (3) the card version the browser loaded (the console banner, or the resource URL's version). If `display` is not `none` and the width is about 700 px, the cause is ink, and sections 6–7 are wrong. If the box is missing, the cause is the engine or the build.

## Forward carries (second pass)

- The fix's failing-first test cannot be a matched-dark contrast cell: that arm is clean on every tag. It must reproduce the box-less label, which this seat could not do in Chromium. Blocked on the owner reading above. Carry: R10-HOTFIX-CARD-HEALTH-TEXT
- The first-pass fix (`.health-row`/`.adv-inbox-row` ink re-pointed, branch d76f4d056) remains correct for the darkMode-false arm. It is not expected to change the owner's screenshot. Carry: R10-HOTFIX-CARD-HEALTH-TEXT
- The rig's `THEMES.dark` `--primary-color` (#03a9f4) differs from HA 20261028.5's #009ac7 (`--ha-color-primary-40`). It affects no text measured here. Carry: dismissed: no text pair reads --primary-color on the Health or Advisor pages

## Figures (second pass)

Every figure in sections 5–7 was measured in this seat at main 61afd4f2d. Instruments: a scratch Playwright Chromium probe (WCAG relative luminance, `getBoundingClientRect` offsets), the HA frontend tag 20261028.5 blocks parsed from `src/resources/theme/color/*.ts`, `tests/plan_view.py` for the plan payload, and `git show <tag>:custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` for the bisection over 18 tags.
