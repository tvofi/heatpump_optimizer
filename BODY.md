Round-9 docs PR WEB-4 (tvofi's findings of 2026-10-03 on the published site): the first page's stray "..." between sentences, the setup-flow diagram that disagreed between README and the setup documents, and card pictures from an old design. README.md and docs/ are outside policy; `tests/doc_claims.py` is not.

1. The ellipses were literal text in `docs/index.html` (not a build or truncation artefact: the served page equals the source), written because the R9-WEB-1 pin quoted claims by fragments split on an ellipsis. Eleven claims now quote whole verbatim spans (or separate spans/lines where the README sentences are not adjacent); the pin no longer splits on an ellipsis and refuses one (`ellipsis` kind, with a planted-ellipsis null control). A sweep of README.md, DISCLAIMER.md and docs/*.md found one other, `docs/dashboard-card.md:661`, a deliberate bold lead-in continuing the previous heading, left alone.
2. Setup flow derived from `config_flow.py`: user -> user_sensors -> (device_prefill only when another entry turned the offer on) -> finish_setup menu; Quick setup -> device_prefill (always) -> back to the menu with Quick setup no longer offered; Finish setup now -> setup_overview; Continue -> temperature -> building menu -> (building_describe -> building_extras | thermal -> zones) -> dhw -> weather_sensitivity -> setup_overview -> create. README's diagram had Finish now, Quick setup and the last screen all skipping the review; configuration.md's lacked the pre-fill. One diagram text, with README's step numbers (the existing Quick start numbering check binds them), now in README, `docs/configuration.md` and `docs/setup.md` (which had none); configuration.md's section numbers follow it (new "2 · Optional sensors" split out of Basics, new "3 · The finish menu"). A check pins the three copies identical. Prose that said Finish setup now creates the entry immediately now says it goes through the review.
3. Pictures: `docs/img/card-plan-chart.png` (README, product page) and `docs/img/card-dhw-band-weekly.png` (dashboard-card.md, product page) were taken from earlier card designs; both re-rendered from the shipped card in real Chromium. The hero via the existing `HPO_HERO_OUT` mode of `tests/card_browser.mjs`; the weekly figure via new `docs/img/make_card_weekly_figure.mjs` (docs/ is INERT; no closure entry). `docs/img/card/*.png` were already current and are untouched. Old images are replaced in place, so no reference changed except the width/height attributes on the two `<img>` in `docs/index.html`.

## Head

6000dbf8d632985e6b35fbcc392e8c8674c6caea

## Mutation proof

Plant an ellipsis in a claim (`The heat-loss scale … the heat-loss scale` in docs/index.html): `python3 tests/doc_claims.py` goes red on "no claim is elided with an ellipsis" and the in-test null control asserts it. Restore the pre-fix `docs/index.html` and the same check is red (11 ellipses). Change one word in the setup.md diagram: "the three setup-flow diagrams are identical" goes red.

## Null control

The unmodified tree (origin/main ac255c200) passes `tests/doc_claims.py`, because the old pin quoted by ellipsis-split fragments; with the new pin applied to it, the ellipsis check reports the eleven claims.

## Figures

- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` -> MODE: SCOPED, 4 scripts run, 7 passed, rc 0 (FAIL lines in its log are the scripts' own null controls).
- `python3 tests/doc_claims.py` -> rc 0.
- `HPO_HERO_OUT=... HPO_PAGES_OUT=... node tests/card_browser.mjs` -> hero written; the run reports one failure, "P9 grid: no two text runs share ink", which is a raster-dependent grid check unrelated to these files (see Friction).
- Before/after contact sheet of the two replaced pictures: seat scratch `seat-web-4/contact-sheet-before-after.png`.

## Red checks

none

## Forward-carry

none

## Friction

README step 2 of the tests/layout.json reorganisation lists `docs/img/card-advisor-page.png` (an orphaned old-design picture nothing references) as a retired path; deleting it would make `tests/layout.py` report a dead entry in a code-owned file, so it is left for the layout owner.

_Requested by **tvofi**_
