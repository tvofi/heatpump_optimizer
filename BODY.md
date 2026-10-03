_Requested by **tvofi**_

Round 2 (head merges origin/main; changes since the first review: items 2, 3 and the dashed-lines figure below). Round-9 docs PR WEB-4 (tvofi's findings of 2026-10-03 on the published site): the first page's stray "..." between sentences, the setup-flow diagram that disagreed between README and the setup documents, and card pictures from an old design. README.md and docs/ are outside policy; `tests/doc_claims.py`, `tests/card_browser.mjs` and `tests/layout.json` are not, and the owner approves those under the mandate.

1. The ellipses were literal text in `docs/index.html` (the served page equals the source; not a build or truncation artefact). They were written because the R9-WEB-1 pin quoted claims as fragments split on an ellipsis. Eleven claims now quote whole verbatim spans (separate spans or lines where the README sentences are not adjacent); the pin no longer splits on an ellipsis and refuses one (`ellipsis` kind, with a planted-ellipsis null control). A sweep of README.md, DISCLAIMER.md and docs/*.md found one other, `docs/dashboard-card.md:661`, a deliberate lead-in continuing the previous heading, left alone.
2. Setup flow derived from `config_flow.py`: user -> user_sensors -> (device_prefill only when another entry turned the offer on and a device qualifies, `config_flow.py` `async_step_user_sensors` / `prefill_offer.qualifies`) -> finish_setup menu; Quick setup -> device_prefill (always) -> back to the menu without Quick setup (#1685); Finish setup now -> setup_overview; Continue -> temperature -> building menu -> (building_describe -> building_extras | thermal -> zones) -> dhw -> weather_sensitivity -> setup_overview -> create. README's diagram let Finish setup now, Quick setup and the last screen skip the review; configuration.md's lacked the pre-fill. One diagram text, with README's step numbers (the Quick start numbering check binds them), now in README, `docs/configuration.md` and `docs/setup.md`; configuration.md's section numbers follow it ("2 · Optional sensors" split out of Basics, new "3 · The finish menu"). A check pins the three copies identical. The diagram draws the two routes into the pre-fill as two nodes: the dashed one conditioned on a qualifying device, the Quick setup one returning to the menu without the Quick setup option. Prose saying Finish setup now creates the entry immediately now says it goes through the review. README step 2 said the flow offers the pre-fill whenever the pump publishes a device; it now says what the code does (only when another entry switched the offer on, off by default, and a device qualifies; Quick setup reads the entities in any case). A sweep of README, docs/*.md and the product page found no other prose saying the old thing.
3. Pictures, all re-rendered from the shipped card in Chromium and replaced in place:
   - `docs/img/card-plan-chart.png` (README first picture, product page): the existing `HPO_HERO_OUT` mode of `tests/card_browser.mjs`, now fed the page fixture (`pageStates`) so all six tiles, the savings sub-line and the headline lines are populated; 1864x1700, no orphan tile.
   - `docs/img/card-dhw-band-weekly.png` (dashboard-card.md, product page): new `docs/img/make_card_weekly_figure.mjs` (docs/ is INERT, no closure entry). `HPO_WEEKLY_MEASURE=1` prints the card's own plotted-against-published lower edge per window: Friday 07:30-08:30 plotted 45.00-46.47 against published 43.77-46.47 (pinned to 45 where it dipped); Friday evening plotted = published 42.23-42.53 (free); Saturday 19:00-21:00 all eight steps plotted 45.00 against published 44.00. The dashboard-card.md caption states exactly these, so it is unchanged. (A first render of mine had the tank itself under 45, which the card draws unfloored; the fixture now keeps the tank at or above 45 with the edge 2.5 under it, as the script says.)
   - `docs/img/card-advisor-page.png`, an orphaned old-design picture nothing referenced, is deleted. Its `tests/layout.json` entry becomes `"new": null` (a deletion; `tests/layout.py` runs in report mode and refuses re-introduction only under `--enforce`); `python3 tests/layout.py` is green.
   - `docs/img/chart-dashed-lines.svg` (and its generator `docs/img/make_card_figures.mjs`, plus the alt text in `docs/dashboard-card.md`) called the hot-water band "one symmetric band"; the card floors its lower edge at the window minimum inside a demand window, so the title, the aria-label, the note and the alt text now say so. The two text edits are made directly in the SVG and the generator alike; the picture itself was not re-rendered.
   - `docs/img/card/*.png` were already current and are untouched; `options-hot-water-by-day.png` is an options page, not the card.
   - The only reference edits are the width/height attributes on two `<img>` in `docs/index.html`.

## Head

75af6b9592a66f26767bbfc4da747be599dc89cf

## Mutation proof

Plant an ellipsis in a claim (`The heat-loss scale … the heat-loss scale`): `python3 tests/doc_claims.py` goes red on "no claim is elided with an ellipsis"; the in-test null control does exactly this on every run. Change one word in the setup.md diagram: "the three setup-flow diagrams are identical" goes red. The reviewer ran the ellipsis refusal on the pre-fix `docs/index.html` and it refused 12.

## Null control

`python3 tests/layout.py --self-test` still fires its own dead-entry and reintroduction controls (green). For the picture checks, the unmodified tree's hero was 1864x1402 with an orphan tile, the empty-tile fixture this body replaces.

## Figures

- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`: MODE: SCOPED, 5 scripts run, 7 passed, rc 0 at the head above (after merging origin/main).
- `python3 tests/doc_claims.py`: rc 0. `python3 tests/layout.py`: rc 0.
- `HPO_PLANDATA=... node tests/card_browser.mjs` on origin/main ac255c200 (a detached checkout) and on this head: both report exactly one failure, "P9 grid: no two text runs share ink". It fails identically on main on this machine, so it is not caused by this change; it is raster-dependent on a Mac and CI's Linux run is the authority.
- Before/after contact sheet of the two replaced pictures: seat scratch `seat-web-4/contact-sheet-before-after.png`.

## Red checks

none

## Forward-carry

none

## Friction

none
