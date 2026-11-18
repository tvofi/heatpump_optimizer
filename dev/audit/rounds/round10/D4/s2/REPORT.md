# D4-s2 (D4.M2, config flow) — round 10, baseline 17f1c55fad1b

Limit: no Home Assistant frontend locally; rendering is inferred from the schema
async_show_form delivers through tests/hastub, and from strings.json / en.json / sv.json.

## Method
- `pages.py`: open each of the 23 options pages (top menu + advanced) with no input;
  recurse into sections; check label and data_description in all three string files.
- `config_labels.py`: untouched install walk (three menu choices) over 10 config forms; same check.
- `ranges.py`: every NumberSelector default/suggested_value against min/max/step on the
  options pages and install forms; counts install steps from `user` to create_entry.
- Error keys emitted by both flows (errors[...] literals, `_prefill_errors`) checked against
  config.error / options.error in the three files.

## Findings
None.

## Non-findings
- options: 23 pages, 223 fields, 0 missing labels / 0 missing help in strings, en, sv (pages.py).
- config: 10 forms, 0 missing labels / help in all three files (config_labels.py).
- 91 numeric fields: 0 defaults outside the selector range or off its step grid (ranges.py).
- Install to first entry: 8 steps untouched (user, user_sensors, temperature,
  building_describe, building_extras, dhw, weather_sensitivity, setup_overview).
- Largest options page: comfort, 20 fields grouped into 5 sections.
- Every config-flow error code is in config.error; options-only codes are in options.error.

## Unfinished
- quick_setup and device_prefill install branches, and the per-page written rubric score
  (adjacency, jargon), were not driven or scored.

exposure: none.
