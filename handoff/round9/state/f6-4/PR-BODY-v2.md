<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: the setup overview in the config flow, the card's setup page and diagram, and the sensor-gap advisor labelled every slot, layout and heading in English on a Swedish install, and the plan figure drew "now 21.1 °C" beside the axis "now" marker. After: `describe_setup`, `render_text_summary`, `rank_sensor_gaps` and `rank_sensor_advisor` take the install's language (`hass.config.language`) and publish Swedish text, the indoor sensor publishes `source_entity` (its thermometer's id, the D4 side of the L1 lead), and the corner reading is "{temp} °C" in both languages.

Fixes #1687 (N-language). Part of #201.

Not changed: the Swedish summary still prints the raw valve mode value ("Blandningsventil: manual"); the mode is a config value, not text this finding owns.

## Head

ed1c0af5494145912480b713643b6e234a9c353f

## Mutation proof

- Wiring (round 2): each of coordinator `describe_setup`, `_with_sensor_advisor`, config-flow `_setup_overview_form`, `SensorGapAdvisorSensor._gaps` (reads `coordinator.hass`: an entity has no `hass` until Home Assistant adds it, and the golden capture reads `native_value` before that) without the language, and the catalog `description`, `requirement` and `rank_sensor_advisor` labels left untranslated, fails a check in `tests/entities.py` or `tests/config_flow_steps.py` driven by a Swedish `hass` (one mutant at a time, restored).
- Language: `_tr` returning its input (the `_SV.get` line replaced) fails 3 of 3631 `tests/features.py` checks: "every slot label differs from English on a Swedish install", "the text summary carries no English heading on a Swedish install", "the layout catalog and sensor gaps follow the language too". Restored.
- Now label: restoring "now {temp} °C" in the en table fails 2 `tests/card.mjs` checks: "a live indoor reading shows the corner now temperature, without a second 'now'" and "the default live view draws exactly one 'now' for the current moment". Restored.

## Null control

English and an unknown language ("de") render byte-identically to the unlanguaged call (features check "null control: English and an unknown language read as before"). `origin/main` cc00ed85 renders English for every language.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py`: ALL 3631 FEATURE CHECKS PASSED at the head above.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 1998 ENTITY CHECKS PASSED (the #373 attribute roster gains IndoorTempSensor: source_entity).
- `node tests/card.mjs`: ALL CARD CHECKS PASSED.
- `python3 tests/structure.py`: no budget breached; no raise. The coordinator's one added line is paid by keeping `describe_setup` on one line.
- Finder's harness `tools/audit/round9/D4/leads/l4_setup_labels.py` at 79aa98ec (sha1 d3e719f46159fbe4471cc83b7193ca3cdaccd667), run from an export: `en_identical_total=41` at the merge base cc00ed85. At this head through the reviewer's adapter (sha1 1a9192f8a2bbbd044420172a01c9b03752adca1b, adds `hass.config.language` to the flow stub and passes the language): `en_identical_total=0`. The unadapted harness raises at the head (its flow stub has no `hass`).
- N-language seams (sweep S7 list; no enumerator script): topology.py `_SLOTS` labels, `describe_setup`, `render_text_summary` closed here via `_SV` and the `language` argument; card setup overview/diagram receives the translated `slots[].label`, `catalog[]` and `sensor_gaps[].label` (closed, same mechanism). `grep -n "describe_setup\|render_text_summary\|rank_sensor_advisor" custom_components/heatpump_optimizer/*.py` run at the head: every caller passes the language, including `SensorGapAdvisorSensor._gaps`.
- Golden drift, deterministic leaves only: `coord_*` gain `setup_topology.language` and `indoor_temp.extra_state_attributes.source_entity`; claimed in tests/golden/claimed_drift.txt and the five committed coord fixtures patched by hand at those paths only (no `--record`, no float churn: `git diff --stat tests/golden`). Five card_drift history fixtures move by the now-temp text alone, claimed in card_claimed_drift.txt.

## Red checks

typing (round 1, CI at f95051f4): `sensor.py:2852: Argument 7 to "rank_sensor_gaps" has incompatible type "**dict[str, float]"; expected "str" [arg-type]`. Cause: `_gap_probe_terms` returned `dict[str, float]`, which unpacked with `**` could also supply the new `language` str. Fixed by a `_GapTerms` TypedDict. Cheaper detector: `tests/typing_ruler.py --mypy` (a seat with the pins runs it before hand-off); standing cost: needs Python 3.14 and the pinned stubs, which this cloud seat lacks, so I reproduced and cleared the error with plain `python3 -m mypy custom_components/heatpump_optimizer/sensor.py` (error present at f95051f4, absent at the head) and the real run is CI's `typing` job. Also unrun here: real-HA `ha_contract`, `card_browser.mjs` overlap grid, `stress.py`.

mutation (CI at f95051f4): wiring mutants survived (coordinator `describe_setup` and `_with_sensor_advisor`, config-flow `_setup_overview_form`, the untranslated catalog description, requirement and advisor labels), because the first round's checks called topology with "sv" directly and never drove the production call sites. Cheaper detector: the new checks in `tests/entities.py` and `tests/config_flow_steps.py`, which run with a Swedish `hass` in seconds and fail on each of those mutants; standing cost: a few seconds in the scoped gate.

## Forward-carry

none: this PR publishes the attribute only; drawing the raw thermometer through a staleness gap in the card is not measured here and is reported to the coordinator, not carried as a finding.

## Friction

none
