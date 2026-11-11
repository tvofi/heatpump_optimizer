# RCA r10-card-health-text: Health-tab labels blank on a dark theme

Seat: root-cause (dev/governance/roles/root-cause.md), beside R10-HOTFIX-CARD-HEALTH-TEXT, never inside it. Trigger: the defect reached a release (defect-root-cause.md, first trigger). Owner report, tvofi 2026-11-11 about 21:27Z: "Live bug on v7.1.11. All text in the "Health" Card tab is missing". Measured at main 61afd4f2d. The card JS, tests/card.mjs, tests/card_browser.mjs and tests/card_rig.mjs are byte-identical between main and v7.1.11 (`git diff --quiet v7.1.11 HEAD -- ...` exits 0).

## Verdict

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
