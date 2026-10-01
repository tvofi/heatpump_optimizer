<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: the setup overview in the config flow, the card's setup page and diagram, and the sensor-gap advisor labelled every slot, layout and heading in English on a Swedish install, and the plan figure drew "now 21.1 °C" beside the axis "now" marker. After: `describe_setup`, `render_text_summary`, `rank_sensor_gaps` and `rank_sensor_advisor` take the install's language (`hass.config.language`) and publish Swedish text, the indoor sensor publishes `source_entity` (its thermometer's id, the D4 side of the L1 lead), and the corner reading is "{temp} °C" in both languages.

Fixes #1687 (N-language). Part of #201.

## Head

f95051f4e5904df3c260745487b2d10e33fa4757

## Mutation proof

- Language: `_tr` returning its input (the `_SV.get` line replaced) fails 3 of 3631 `tests/features.py` checks: "every slot label differs from English on a Swedish install", "the text summary carries no English heading on a Swedish install", "the layout catalog and sensor gaps follow the language too". Restored.
- Now label: restoring "now {temp} °C" in the en table fails 2 `tests/card.mjs` checks: "a live indoor reading shows the corner now temperature, without a second 'now'" and "the default live view draws exactly one 'now' for the current moment". Restored.

## Null control

English and an unknown language ("de") render byte-identically to the unlanguaged call (features check "null control: English and an unknown language read as before"). `origin/main` cc00ed85 renders English for every language.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py`: ALL 3631 FEATURE CHECKS PASSED at the head above.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 1998 ENTITY CHECKS PASSED (the #373 attribute roster gains IndoorTempSensor: source_entity).
- `node tests/card.mjs`: ALL CARD CHECKS PASSED.
- `python3 tests/structure.py`: no budget breached; no raise. The coordinator's one added line is paid by keeping `describe_setup` on one line.
- N-language seams (sweep S7 list; no enumerator script): topology.py `_SLOTS` labels, `describe_setup`, `render_text_summary` closed here via `_SV` and the `language` argument; card setup overview/diagram receives the translated `slots[].label`, `catalog[]` and `sensor_gaps[].label` (closed, same mechanism). `grep -n "describe_setup\|render_text_summary\|rank_sensor_advisor" custom_components/heatpump_optimizer/*.py` run at the head: every caller passes the language.
- Golden drift, deterministic leaves only: `coord_*` gain `setup_topology.language` and `indoor_temp.extra_state_attributes.source_entity`; claimed in tests/golden/claimed_drift.txt and the five committed coord fixtures patched by hand at those paths only (no `--record`, no float churn: `git diff --stat tests/golden`). Five card_drift history fixtures move by the now-temp text alone, claimed in card_claimed_drift.txt.

## Red checks

none known. Unrun in this container (Python 3.11, no 3.14.2): `tests/typing_ruler.py --mypy`, real-HA `tests/ha_contract.py`, `tests/card_browser.mjs` overlap grid (no browser run), `tests/stress.py`. `tools/audit/prepr.sh` result is in the hand-off message.

## Forward-carry

none: this PR publishes the attribute only; drawing the raw thermometer through a staleness gap in the card is not measured here and is reported to the coordinator, not carried as a finding.

## Friction

none
