R11-OWNER-GENERIC-CONTROL-TEXT (owner item, tvofi 2026-11-15). Heat-curve control is now the subject of the user-facing text and the Danfoss ECL110 one of its three ways (MQTT topics, an offset `number` entity, a stored curve parameter); every vendor, model or integration name in the user-facing text is enumerated by one command and ruled an example (kept and marked), a real restriction (kept and said to be one) or a leftover (rewritten generic). Text only: no option key, entity id, translation key or behaviour changes.

- `docs/ecl110.md` is renamed `docs/heat-curve.md`, titled "Heat-curve control", opening on a three-way table; the MQTT section becomes "Over MQTT: topics and payloads" with the ECL110 as its example. The old address resolves both places: `docs/ecl110.md` stays as a pointer page, and `tools/site/build_docs.mjs`'s new `MOVED` map writes `ecl110.html` on the site as a redirect to `heat-curve.html` that keeps the fragment. `tests/doc_claims.py` pins both halves (`MOVED_PAGES`), including the fragment-keeping script line.
- README: the section is "Heat-curve control" (old anchor kept as `<a id="ecl110-heat-curve-control">`), the supported-controls rows are "Heat curve, over MQTT / offset entity / stored parameter", the Documentation row and the known limitation are generic. The limitation also said "an absolute or stored curve parameter is not supported in this version", false since the persistent kind shipped; it now states what is refused (an entity whose range excludes 0).
- Product page: the control-path chooser offers the three heat-curve ways (quoting the README rows), the doc link names `docs/heat-curve.md`.
- `docs/setup.md` now names the control paths, heat-curve control's three ways among them, under "Before you start"; `docs/configuration.md`, `how-it-works.md`, `automations.md`, `architecture.md` follow.
- Flow and services text, English with German and Swedish in the same diff: the heat-curve page description names all three ways (the German one named only the ECL110 and titled the page "Heizkurvensteuerung (ECL110)"); the two sensors' display names are "Heat-Curve Displace" / "Heat-Curve Effective Displace" (entity ids come from the translation key, `entity.py` `object_id`, so they do not move); the `set_thermal_parameters` field names drop ECL110. Luxtronik mentions in the set-point and power-feedback help are marked as examples beside their generic statement.
- Price source: the README feature lead, two interval diagrams, the product page's feature card and the DSO-fee text said "Tibber" where the price comes from Tibber or a price sensor.
- Carry built here (roster R11-OUTSIDE-DEARER-WORDING, folded into this group, owner 11-16): the English user-facing text says "more expensive" for "dearer" and "most expensive" for "dearest", except at two card sites that keep the short "pricier". Closes #3643. Thanks to @rasenschachmatt for raising the wording.

## Head

`4817b38ba6bf9029027b626f39074020cd992995`, branch `fix/r11-owner-generic-control-text-pr`, merge base `2d7161a4b70923da910f9997e18db632c0d4ec2d`. It is the merge-main bot's `ci: merge main` (origin/main `2d7161a4b7`) on `81ffccaa01`, the orchestrator's merge of the authored code head `e83eaff1977e3829fea8550fbfa72778eb3b5e11` with origin/main `b425502da8`. This repair adds no commit: both merges are automatic and resolved no conflict inside this PR's files, and `git merge-tree --write-tree origin/main 4817b38ba6` against origin/main `8f39313a44` (2026-11-17) reports none, so no further merge is made. The fix review returned `merge` at `81ffccaa01` (review/3663 `f08a6dc341`); no `blocked` verdict exists at this head. Figures below the figure block were taken at `e83eaff197`; the delta from it to this head is the two merges of main. Rule: `git diff --stat e83eaff197 4817b38ba6 -- $(git diff --name-only 2d7161a4b7...4817b38ba6)` lists the PR's files that those merges also changed: `dev/audit/config/scopes.json` (+124), `docs/dashboard-card.md` (+6 -2), `tests/closures.json` (+6), `tests/layout.json` (`product_reads.py` added to a `tools/audit/{...}` glob, main's line); CI re-measures that tree, and the train re-proves it on the current main.

prepr: passed rc=0 at 4817b38ba6bf9029027b626f39074020cd992995

## Block answered

Fix review `blocked` at `54fd5072b6`, `mutation-survivor`: deleting `tools/site/build_docs.mjs`'s `<script>location.replace(... + location.hash)</script>` line (mutant m4) left `tests/doc_claims.py` green. The `MOVED_PAGES` check in `check_docs_subpages` now also requires `location.replace(<json target> + location.hash)` in the built redirect page; its detail prints `fragment kept: <bool>`. The meta refresh beside it drops the fragment, so the script line is the only thing keeping a deep link (`ecl110.html#...`) on its anchor.

## Mutation proof

`PYTHONPATH=tests/hastub python3 tests/doc_claims.py`, at this head (the check change is b43f4c244f; `build_docs.mjs` is unchanged from `54fd5072b6`):

- head: `ALL 411 checks PASSED`, rc 0.
- m4, the reviewer's mutant (`ev/m4_mutant.diff`: the script line replaced by `</head>`): `FAIL docs/ecl110.md still resolves: a pointer to docs/heat-curve.md in the tree, a redirect to its page on the site  [site redirect to heat-curve.html, fragment kept: False; the in-tree file links docs/heat-curve.md: True]`, `1 of 411 checks FAILED`, rc 1.
- restored: `git diff --quiet -- tools/site/build_docs.mjs` true.
- The earlier mutants (`MOVED` emptied, the pointer link removed) are unchanged arms of the same conjunction.

Carry: `why.price_rank` reverted to "dearest" in the card → `node tests/card.mjs`: `FAIL UX-1 a dear idle step gives its price rank within the horizon`, `FAIL UX-1 both channels idle share one block and one price line`, `2 CARD CHECK(S) FAILED`, rc 1; restored, `ALL CARD CHECKS PASSED`. The three moved card states fail `tests/card_drift.mjs` unclaimed (`3 problem(s)`) and pass once claimed.

No `.py` line outside `tests/` and `dev/` is added or changed except `narrative.py`'s one string value, so `prepr.sh`'s mutant draw has no predicate to mutate.

## Null control

- Part 1: a change to the same redirect page that keeps the script line (`<title>Moved</title>` → `<title>Page moved</title>`) → `ALL 411 checks PASSED`, rc 0: the new conjunct keys on the fragment line, not on any edit to the page.
- Carry, the residual rule: `git grep -i -E '\b(dearer|dearest)\b' -- strings.json translations/en.json narrative.py docs blueprints README.md` prints 7 lines at the merge base `92d38ecb64` and 0 at the head. In the card, the diff from `54fd5072b6` removes 4 English lines carrying the words (`why.sub_dearer`, `why.price_rank`, `stats.dearer`, `whynow.explain_price_rank`); the words left in the card are i18n keys, reason codes, CSS classes and code comments, which the carry keeps.
- `git diff --quiet 54fd5072b6 HEAD -- translations/de.json translations/sv.json` is true; `cmp -s strings.json translations/en.json` is true.

## Figures

<!-- figure-block: scope-line mb=2d7161a4b70923da910f9997e18db632c0d4ec2d head=4817b38ba6bf9029027b626f39074020cd992995 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

Layout, `node dev/audit/harnesses/r11_why_hover_fit.mjs <ref> <plan.json>` (sha1 `3e3df85487f76bb25b38bd8c6450eca768b224e9`, Playwright Chromium, the `tests/plan_view.py` payload through `tests/card_rig.mjs`'s `planStates`; the fixture's dearest idle space step, 16:00, publishes `idle_dearer`). Rule: hover that step on the tile chart and the expanded dialog's chart at 375 and 500 px card width; print the fitWhy cap (chart height − 16), the tooltip height with fitWhy disabled (natural) and enabled (fitted), whether the `.tt-why` block survives, and each line's height in line-heights. Base `92d38ecb64` (dearer), head (pricier), and the control arm `WHY_SUB_DEARER="this hour is more expensive than the hours the plan uses"` on the head:

| surface, width | cap | natural height base / head / control | first line, lines | fitted: block shown base / head / control |
|---|---|---|---|---|
| dialog 375 | 173 | 197 / 197 / 197 | 1 / 1 / 1 | yes / yes / yes (the second line dropped) |
| dialog 500 | 224 | 197 / 197 / 197 | 1 / 1 / 1 | yes / yes / yes |
| tile 375 | 142 | 240 / 240 / 255 | 1 / 1 / 2 | no / no / no |
| tile 500 | 195 | 240 / 240 / 255 | 1 / 1 / 2 | no / no / no |

The brief's 375 px re-check holds: in the dialog the explanation block still shows at the head with the pricier line. On the tile chart "more expensive" wraps the line 1 → 2 (natural 240 → 255 px) where "pricier" keeps the base's 1 line and 240 px, which is the carry's reason for the short form. The tile's block is dropped by fitWhy at the base too (240 > 142 and > 195), so that drop is not this diff's. The `stats.dearer` row was not re-measured in a browser; its markup moves only in the text node (`card_drift.mjs`, below).

Checks run at the head for the repair's delta (`python3 tests/closure.py select --diff 54fd5072b6...` prints `MODE: SCOPED -- 23 script(s) run, 10 scoped out`; the whole branch is `MODE: FULL` because `tests/closure.py` is in the diff), `PYTHONPATH=tests/hastub`, `GOLDEN_MODE=drift GOLDEN_REF=92d38ecb64`, re-run at this head after the merge (`tests/plan_view.py` first): every script in that `scope.run` exited 0 — `arch_score_head.py`, `block_duty.py`, `boost_drift_replay.py`, `config_flow_steps.py`, `debug_collect.py`, `deployment_shape.py`, `doc_claims.py` (ALL 411 checks PASSED), `entities.py` (ALL 2723 ENTITY CHECKS PASSED), `env_drift.py`, `features.py`, `finite_boundary.py`, `golden.py`, `guard_pins.py`, `harness_headers.py`, `manual_plan.py`, `md_tables.mjs`, `plan_view.py`, `card.mjs` (ALL CARD CHECKS PASSED), `card_drift.mjs` (rc 0 with the three claims; rc 1, 3 unclaimed states, before them), `solar_alignment.py`, `structure.py`, `typing_ruler.py`, `wood_advisor.py`. After the harness landed: `harness_headers.py`, `structure.py`, `entities.py` re-run, and `python3 tools/pr/ci_predict.py` prints `no closures, fast, governance or instrument red predicted`.

Card drift claimed in `tests/golden/card_claimed_drift.txt`: `draft_dirty_menu_open`, `draft_mid_drag` (the what-if hint "pricier than the saved plan") and `tooltip_hover` (the Because line); text nodes only.

Census: `python3 dev/audit/harnesses/vendor_text_census.py --counts` (sha1 `269ed873594fde8f91389eb4de9c306d4c4e32ca`), the rule in its docstring: README, `docs/` less `docs/design/` and `docs/img/`, `strings.json` and `translations/*.json` values, the card's `www/*.js` and `services.yaml`; a brand in its `BRANDS` list (built from every capitalised token of that surface at the merge base, read by hand) matched as a whole word, an `_`-glued identifier excluded, plural `s` allowed. Base with `--root` on a checkout of `b3831ff64e` (the fix review re-derived 632 at the merge base `367c3b9cac` as well), head in this tree; re-run at this head, `total	560`, unchanged by the repair (no brand in its delta):

| brand | base | head |
|---|---|---|
| ECL110 | 115 | 33 |
| Danfoss | 16 | 20 |
| Luxtronik | 72 | 75 |
| SHI | 22 | 25 |
| Smart Home Interface | 11 | 11 |
| Tibber | 169 | 169 |
| Open-Meteo | 73 | 73 |
| Modbus | 44 | 44 |
| Nord Pool | 36 | 36 |
| GCHV | 13 | 13 |
| ESPHome | 9 | 9 |
| Daikin | 8 | 8 |
| Ellevio, Rotenso, Windmi | 5 each | 5 each |
| NIBE | 4 | 4 |
| Alpha Innotec, Met.no | 3 each | 3 each |
| ENTSO-E, Novelan, Tuya | 2 each | 2 each |
| ApexCharts, Bouni, EKMBDXA, GWF, Homey, LWDV, Mitsubishi, Panasonic, S1256PC, Stiebel, Vaillant, Vattenfall, Zigbee | 1 each | 1 each |
| **total** | **632** | **560** |

Rises are examples added beside a generic statement (the three-way tables and descriptions name the ECL110 and a Luxtronik as examples). Every head hit, ruled by group (`python3 dev/audit/harnesses/vendor_text_census.py`, grouped by brand and file):

- **Real restriction, kept and said to be one.** Tibber (169): a price source the integration builds, always named beside the price-sensor alternative. Open-Meteo (73): the built irradiance and snow source. Ellevio, Vattenfall (6): the built Swedish DSO tariff presets. GCHV, Rotenso, Windmi and Modbus in the pre-fill page, its error, its options rows and `architecture.md` (`modbus_prefill.py`): the pre-fill reads only what it has a mapping for; the page description now opens "Reads only what this page has a mapping for". GCHV in the duty-mode help ("as on the GCHV Modbus package") and "Tuya or Modbus, the same logic" in `configuration.md`'s duty section: the two packages the mode logic was built against, stated as such. ECL110 in the README acknowledgement (2) and `strutsfarm/ecl110` links: attribution. ECL110 in `heat-curve.md`'s rounding sentence: the integer rounding applies to every way because the ECL110 takes integers, said so. ECL110 in `architecture.md` (2): the payload's `ecl110_*` view, an identifier. The README `ecl110-heat-curve-control` anchor and `docs/ecl110.md` (2): the old address, kept so links resolve. `heat-curve.md`'s note that the `ecl110_` key prefix is historical (the ruled-out key rename).
- **Example, kept and marked.** Danfoss/ECL110 as the MQTT example (README, setup, configuration, how-it-works, product page, flow text). Luxtronik, SHI, Smart Home Interface, Alpha Innotec, Novelan, Bouni, LWDV: the offset-entity example, the return-temperature example, the limit-sensor and hysteresis examples, each now beside "for example"/"for one" or under `heat-curve.md`'s "Example:" heading. Nord Pool, ENTSO-E, Met.no: "or similar"/"such as". Modbus/ESPHome for the frequency entity: "typically". Tuya in "a Tuya pump reads 25 °C", Zigbee (a dropped room sensor), ApexCharts (a library the card does not depend on): examples.
- **Cited source of a default, kept.** Daikin, EKMBDXA, NIBE, S1256PC, Homey, GWF, Vaillant, Stiebel, Mitsubishi, Panasonic, and Luxtronik's ±5 K: `heat-curve.md`'s "Where the defaults come from" and the band and write-cap help, each a named source for an estimate.
- **Leftover, rewritten generic** (the base-to-head drop): every hit above that this diff changed — the page title and intro, the README section, row labels, limitation, Documentation row and diagram node, the product page's chooser, step 4, doc link and feature card, the flow's heat-curve description (en, de, sv), its MQTT-topic help, the German page title and menu entry, the two sensor names and three service-field names (en, de, sv), the grid-fee help, `configuration.md`'s heat-curve, finish-setup, reset and service-list text, `how-it-works.md`'s diagram, link and DSO-fee text, `automations.md`, two `architecture.md` module-map lines.

Instrument limit: the census reads a line or one JSON value at a time, so a brand split across a wrapped Markdown line is not seen; `configuration.md`'s "alpha innotec" was re-wrapped onto one line for that reason. The card's `www/*.js` has no heat-curve or Luxtronik text at either end (its hits are Nord Pool "or similar" labels and Open-Meteo).

## Red checks

Reds at `4817b38ba6`, from the PR's check runs (run `43986306110` attempt 3 and run `43986297330`); `python3 tools/audit/seat/merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`, all green here, so no red below is in the owed set.

- `pr-contract / pr-contract`: `figure-block scope-line names another head (81ffccaa0186, this is 4817b38ba6bf)` and the `## Head` naming `81ffcca`. A body finding: this body names `4817b38ba6`, and `body_push.sh` re-renders the scope-line block against the PR's recorded base.
- `governance / instrument-self-tests`, step "Show the self-tests outside tools/audit/seat/ refusing their own fixtures": inherited, not introduced. The failing command is `python3 -I tools/audit/product_reads.py --self-test`, which raises `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] are not the duty modes STATES names ['control', 'observe', 'off']`. Run locally: rc 1 at this head, rc 1 with the same Refuse at the merge base `2d7161a4b7` (a worktree of the base, no file of this PR), and rc 0 `SELF-TEST passed (86 arms)` at origin/main `8f39313a44`. `git diff --name-only 2d7161a4b7...4817b38ba6` names neither `const.py`, `tools/audit/enumerate.py` nor `tools/audit/product_reads.py`. The step's other 19 commands (`governance.yml`, id `self-tests-outside-seat`, run one by one at this head) exit 0; `product_reads.py --self-test` is the only rc 1. `merge_train.py classify 4817b38ba6 --pr 3663` refused (`selftests: ... concluded failure with no red step`) on the earlier run's job `133880150908`; the later attempt's job `133869556235` names step 48 as the red step.
- `gate`: red because the two above are.
- `tests / replay`: `owner-2026-10-30-away.json: cycle_cost [1 offender(s): cpu_ratio 453.8 over its budget 332.8]`, `1 of 198 replay checks FAILED`, at job `133880152350`; run `43986306110` skipped the lane. This PR changes no `custom_components/` `.py` line except `narrative.py`'s one string value; not in the owed set, not repaired here.
- `tests / nightly-status`: not in the owed set; grades `main`.

## Forward-carry

none

## Friction

none
