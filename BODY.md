R10-HOTFIX-CARD-HEALTH-TEXT, carries 0 and 1, cut from main after #3485. This PR changes only `tests/card_browser.mjs`, and no production line.

**Carry 1 (P662).** `themeMismatch`'s cases now include the two matched arms: light variables with darkMode false, and dark variables with darkMode true. One unit therefore measures every own-text run on the tile and on every dialog page, Health and Advisor rows included, in all four theme/darkMode pairings. Before this PR, the matched arms were measured only by the P9 grid's lockstep cells. The own-text sweep moves out of `themeMismatch`'s page script into `hpoContrastKit`, which `themeLiveSwitch` also reads. That keeps one copy of the WCAG unit.

**Carry 0 (owner fact: default theme, auto, following macOS).** `themeLiveSwitch` mounts the card on HA's default theme tokens (`THEMES.light`/`THEMES.dark`) and opens the Health dialog. It then switches the OS colour scheme live, light to dark and back, with `page.emulateMedia`. In the page, a `prefers-color-scheme` change listener does what HA's themes mixin does, in the same order. It writes the theme's variables onto the document. One microtask later, it gives the card a hass whose `themes.darkMode` is the new scheme. The Health dialog is measured twice per direction: between the variable write and the hass update, and on the frame after the card's re-render. Reach requires each of these:
- at the first point, the card still holds the old darkMode and the old row surface, so that measurement is the mismatched pairing;
- after the re-render, the dialog is still open on Health;
- the row surface flipped;
- at least 10 `span.fact-text` labels are measured at both points.

**Which state the owner's install was in.** Steady state is the matched arm: dark variables with darkMode true (or light with false). HA writes the variables and darkMode together on every OS switch. The card reads no OS scheme itself: the card has 0 `@media (prefers-color-scheme` rules, and its 2 `matchMedia(` calls are `pointer: coarse` and `prefers-reduced-motion`. So the P9 grid's off-lockstep cells (OS scheme varied, darkMode fixed) do not change the card's paint, and they are not the live state.

On the released pairing, the steady arms are green, so this contrast check cannot be red in the owner's steady state. The released pairing is red only in the window between HA's variable write and its hass update, at 1.24:1 (light to dark) and 1.11:1 (dark to light). In this model the hass update lands one microtask after the write, so no frame is painted inside that window. Whether HA's frontend paints one is not measured here. The orchestrator's hypothesis is therefore refuted as an explanation of the screenshot: the owner's install was in the matched arm, where the released rows read 11.08:1 (RCA second pass). The screenshot's box-less labels are #3485's blocker cause, and `blockerHide` is red on the released card in that matched dark arm (#3485 body). The new check still pins the transient. A fix that moved the rows back onto a darkMode literal under theme text would go red there, as the mutation below shows.

## Head

e5e6c81b8ee7fe91a2599ae6d021bb6a471a4890, merged with origin/main 19baca76181cb019d9b1cfd93ee6bc0a08e20047 (merge base 19baca76181cb019d9b1cfd93ee6bc0a08e20047) at 2026-11-12T13:38:51Z. The two merges of main (at cbe8d93bd8 and 19baca7618) brought in no card or browser-lane file (`git diff --name-only e1361b108c HEAD`: gate, stamp, merge-train, plan-tooling and delivery files only). The browser-lane run below was taken at the pre-merge commit e1361b108c, on the same card and test tree.

## Mutation proof

Planted the released defect as Carry 1 specifies: `.health-row, .fact-inbox-row` back on `--hpo-surface-2` with `--hpo-text`, as at 906fee95e. In the card's surface-2 rule, the two row selectors leave the ink re-point and get a background-only rule. I ran a scratch driver that calls only `themeLiveSwitch` and `themeMismatch` from `tests/card_browser.mjs`. Four checks go red:
- `R10 live light to dark: every Health text run clears 4.5:1 between HA's theme write and its hass update`: 40 of 59 runs under 4.5:1, `span.fact-text` / `span.fact-sub` at 1.24:1
- `R10 live dark to light: every Health text run clears 4.5:1 between HA's theme write and its hass update`: 40 of 59 runs, 1.11:1
- `R10 every own-text run on every dialog page clears 4.5:1 with dark theme variables, darkMode false`: 65 runs, Advisor `span.fact-text`, `span.fact-sub`, `span.fact-value` and `button.fact-act` at 1.24:1
- `R10 every own-text run on every dialog page clears 4.5:1 with light theme variables, darkMode true`: 65 runs, the same elements at 1.11:1

Card restored with `git checkout custom_components/`.

## Null control

Under the same planted defect, these stay ok:
- both matched arms of `themeMismatch`, with their tile and chart checks;
- both `after the card's re-render` checks;
- both reach checks;
- the start check.

The matched arms and the post-render frames are the steady states the RCA found clean, so the red comes from the mismatched pairing and not from the sweep. On the unmutated tree, all 7 `themeLiveSwitch` checks and all 12 `themeMismatch` checks are ok.

## Figures

- 59 runs measured on the Health dialog per live switch, and 40 under 4.5:1 on the planted defect. Instrument: `themeLiveSwitch` in `node tests/card_browser.mjs`. Measured through a scratch driver that patches the file's driver to call only that function after `chromium.launch()`; it is not in the tree.
- 65 runs under 4.5:1 per mismatched arm on the planted defect, and 0 in the matched arms. Instrument: `themeMismatch` in `node tests/card_browser.mjs`, same driver.
- Full browser lane: `node tests/card_browser.mjs` printed `P9 grid MODE: FULL (HPO_BROWSER_SCOPE=full)` and `ALL BROWSER CHECKS PASSED`, rc 0, at e1361b108c. Payload from `PYTHONPATH=tests/hastub python3 tests/plan_view.py`.
- The card has 0 OS-scheme rules and 2 `matchMedia(` calls, neither of them the colour scheme. Instrument: `python3 -c` with `re.findall(r'@media[^{]*prefers-color-scheme', s)` and `s.count('matchMedia(')` over `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

<!-- figure-block: scope-line mb=19baca76181cb019d9b1cfd93ee6bc0a08e20047 head=e5e6c81b8ee7fe91a2599ae6d021bb6a471a4890 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
