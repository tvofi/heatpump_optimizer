# R10-HOTFIX-CARD-HEALTH-TEXT: blocked on reproduction

Question: The shipped v7.1.11 card renders every Health-tab label in Chromium. Which client showed the blank labels, and what does one blank row hold? Needed from the owner's install: (1) the client: browser and version, or Companion app with OS and version; (2) Home Assistant core and frontend version, and the profile language; (3) whether a hard refresh or a cleared frontend cache changes it; (4) whether the Advisor tab's inbox rows are blank too, since they use the same `.adv-text` span; (5) from devtools on the Health tab, the outerHTML of one blank checklist row (`.health-row[data-check="price"]` in the card's shadow root) and the computed `color`, `font-size`, `width` and `visibility` of its `.adv-text`.

## What was measured, at origin/main 61afd4f2db10341ab9b86583944402b206eb4c78 (card CARD_VERSION 7.1.11)

- Release range: `git diff v7.1.10 v7.1.11 -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
  changes only CARD_VERSION, one new catalogue key `setup.dhw_combi_caption` in en/sv/de, and the combi
  box caption and pipe in `setupSvgHtml`. Nothing on the Health render path (`healthPageHtml`, `healthRow`,
  `healthModelRow`, `healthChecklistHtml`, `healthDebugHtml`) or in the CSS changed. The card is served
  untransformed (`frontend.py` static path, `release.yml` git-archive zip).
- Content: every blank element in the report is the `<span class="adv-text">` of a `.health-row`; the
  elements that render (`.model-value`, `.status-pill`, `.adv-act`, `h3.health-h`) are its siblings or
  ancestors. Each label is `esc(L(key))`, and L falls back to English and then to the key, so it cannot
  return "" unless a catalogue holds "". Control: a node vm load of `STRINGS` lists 643 keys in each of
  en, sv and de, with zero empty or non-string values.
- Style: in Chromium, walking every CSSOM rule in the card's shadow root (including rules inside @media
  and @container) and testing it with `Element.matches` against a model row's `.adv-text` and `.adv-sub`
  matches exactly two rules: `.adv-text { flex: 1 1 14em; min-width: 0 }` and
  `.adv-text .adv-sub { display: block; font-size: max(12px, 0.85em); opacity: 0.8 }`. Neither can hide
  text. `color` is inherited by `.adv-text`, `.model-value` and `.adv-act` (`color: inherit`) from the
  same `.health-row`, so a colour clash would blank the values and the button too. The owner reports
  that those render.
- Rig: a Playwright probe (Chromium, from the healthLayout recipe in tests/card_browser.mjs and the
  card_rig.mjs fixtures) renders the Health tab with hass languages en, sv, de, sv-SE, de-DE, en-GB and fr,
  in light and dark themes, at viewport widths 375, 800 and 1280 px, with reduced motion. The state
  holds 8 inputs (one stale), the model rows (heat loss, lower floor, window aperture, tank, COP) and
  learner_progress in all four phases. Result: 132 rows per width, and 0 with an empty `.adv-text`
  textContent, an empty innerText or zero width. The stale input renders first, as "Stale", above the
  fresh ones. Control: the probe prints any row whose label is empty, as it does for rows of a page
  that is not the Health page.

## Why no fix is pushed

The brief requires a failing test first, and a fix at the seam that produces the labels. No input
tried makes a label blank, so no test can fail yet. A guessed change to the CSS or the strings would
have no mutation proof. The only browser installed in this container is Chromium, so a WebKit or
Firefox-only rendering defect cannot be ruled out or reproduced here. Item (1) decides whether the
reproduction needs another engine.
