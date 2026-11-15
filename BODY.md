R11-OWNER-GENERIC-CONTROL-TEXT (owner item, tvofi 2026-11-15). Heat-curve control is now the subject of the user-facing text and the Danfoss ECL110 one of its three ways (MQTT topics, an offset `number` entity, a stored curve parameter); every vendor, model or integration name in the user-facing text is enumerated by one command and ruled an example (kept and marked), a real restriction (kept and said to be one) or a leftover (rewritten generic). Text only: no option key, entity id, translation key or behaviour changes.

- `docs/ecl110.md` is renamed `docs/heat-curve.md`, titled "Heat-curve control", opening on a three-way table; the MQTT section becomes "Over MQTT: topics and payloads" with the ECL110 as its example. The old address resolves both places: `docs/ecl110.md` stays as a pointer page, and `tools/site/build_docs.mjs`'s new `MOVED` map writes `ecl110.html` on the site as a redirect to `heat-curve.html` that keeps the fragment. `tests/doc_claims.py` pins both halves (`MOVED_PAGES`).
- README: the section is "Heat-curve control" (old anchor kept as `<a id="ecl110-heat-curve-control">`), the supported-controls rows are "Heat curve, over MQTT / offset entity / stored parameter", the Documentation row and the known limitation are generic. The limitation also said "an absolute or stored curve parameter is not supported in this version", false since the persistent kind shipped; it now states what is refused (an entity whose range excludes 0).
- Product page: the control-path chooser offers the three heat-curve ways (quoting the README rows), the doc link names `docs/heat-curve.md`.
- `docs/setup.md` now names the control paths, heat-curve control's three ways among them, under "Before you start"; `docs/configuration.md`, `how-it-works.md`, `automations.md`, `architecture.md` follow.
- Flow and services text, English with German and Swedish in the same diff: the heat-curve page description names all three ways (the German one named only the ECL110 and titled the page "Heizkurvensteuerung (ECL110)"); the two sensors' display names are "Heat-Curve Displace" / "Heat-Curve Effective Displace" (entity ids come from the translation key, `entity.py` `object_id`, so they do not move); the `set_thermal_parameters` field names drop ECL110. Luxtronik mentions in the set-point and power-feedback help are marked as examples beside their generic statement.
- Price source: the README feature lead, two interval diagrams, the product page's feature card and the DSO-fee text said "Tibber" where the price comes from Tibber or a price sensor.

## Head

064e7eb6d587face9a4ea19eaa9665165d2e07f5, branch `fix/r11-owner-generic-control-text`, merge base `b3831ff64eca1936f0b618193ee86c3e337b51a9` (`origin/main` at 2026-11-15T15:28Z).

## Mutation proof

The one production predicate is the redirect; the check is `tests/doc_claims.py` "docs/ecl110.md still resolves: a pointer to docs/heat-curve.md in the tree, a redirect to its page on the site", run at 55b537cf5f (`PYTHONPATH=tests/hastub python3 tests/doc_claims.py`):

- `MOVED` emptied in `tools/site/build_docs.mjs` → `FAIL docs/ecl110.md still resolves ... [site redirect to nothing; the in-tree file links docs/heat-curve.md: True]`, `1 of 411 checks FAILED`.
- the pointer page's link to `heat-curve.md` removed (`docs/ecl110.md` rewritten without it) → the same check `FAIL ... [site redirect to heat-curve.html; the in-tree file links docs/heat-curve.md: False]`, `1 of 411 checks FAILED`.
- restored: `ALL 411 checks PASSED`.

No `.py` line outside `tests/` and `dev/` is added (`git diff --stat` names no `custom_components/**.py`), so `prepr.sh`'s mutant draw has nothing to mutate.

## Null control

- Census perturbation: one ` Thermia` appended to README line 64 → `--counts` prints `Thermia	1` and `total	561`; restored, no Thermia line and `total	560`.
- The brief's null control: a vendor named as a stated example of a generic shape is not a finding, so every example below is kept, with "for example", "for one", "typically" or "or similar" beside it where the sentence did not already say so.
- Merge base: `ecl110.html` is a built page there (the README row), so no redirect is owed; the new check does not exist there.

## Figures

<!-- figure-block: scope-line mb=b3831ff64eca1936f0b618193ee86c3e337b51a9 head=064e7eb6d587face9a4ea19eaa9665165d2e07f5 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

Census: `python3 dev/audit/harnesses/vendor_text_census.py --counts` (sha1 `269ed873594fde8f91389eb4de9c306d4c4e32ca`), the rule in its docstring: README, `docs/` less `docs/design/` and `docs/img/`, `strings.json` and `translations/*.json` values, the card's `www/*.js` and `services.yaml`; a brand in its `BRANDS` list (built from every capitalised token of that surface at the merge base, read by hand) matched as a whole word, an `_`-glued identifier excluded, plural `s` allowed. Base with `--root` on a checkout of `b3831ff64e`, head in this tree:

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

Checks run at the head (the gate is `MODE: FULL` because `tests/closure.py` is in the diff; these are the scripts whose `tests/closures.json` closure the diff reaches, `PYTHONPATH=tests/hastub`, `GOLDEN_MODE=drift GOLDEN_REF=b3831ff64e`): `tests/doc_claims.py` (ALL 411 checks PASSED), `tests/entities.py` rc 0, `tests/features.py` rc 0, `tests/golden.py` rc 0, `tests/config_flow_steps.py` rc 0, `tests/deployment_shape.py` rc 0, `tests/arch_score_head.py` (ALL 18 PASSED), `node tests/md_tables.mjs` rc 0, `node tests/card.mjs` (ALL CARD CHECKS PASSED), `node tests/card_drift.mjs` (identical in all 45 states, after `tests/plan_view.py`), `tests/env_drift.py --claims-only b3831ff64e` rc 0, `tests/closure.py selftest` rc 0, `tests/structure.py` (STRUCTURE RATCHET PASSED), `tools/audit/text_ledger.py --self-test` rc 0. entities.py was first red on two names: the German pair lost its shared lead token (#1334) and `docs/heat-curve.md` had no recorded closure; fixed in aaf3de7899. `tools/pr/prepr.sh` then refused the layout placement of `docs/heat-curve.md`, the census's INERT READS entry and the round-4 D6 claims register (re-written by `dev/audit/rounds/round4/D6/claims.py` for the renamed sensors and new links); all three repaired at the head.

## Red checks

none

## Forward-carry

none

## Friction

none
