# D4-s2 report -- config and options flow (round 8)

Seat: D4-s2 of 2. Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree:
`/home/claude/audit-r8/seats/D4-s2` (a `copy` tree, no `.git`; production
files verified byte-identical to `/home/claude/audit-r8/export` at the end of
this seat's run via `diff -rq custom_components ...` -- only difference was a
stale `__pycache__/process_worker.cpython-311.pyc`, not a source file).

Focus (method step 2 of D4.md): field order/grouping, defaults, selector
ranges, validation error keys and their translations in every language, help
text, and steps from install to first plan, scored against a written rubric.
Seat s1 owns the card-in-Chromium work (method steps 1 and 3); nothing below
touches it.

## Limits to state

There is no Home Assistant frontend locally. Config-flow rendering is
inferred from the voluptuous schema each `async_step_*` returns and from
`strings.json`/`translations/*.json`, exactly as `tools/audit/briefs/D4.md`'s
"Limits to state" says to. `tests/config_flow_steps.py`'s `rendered_keys()`
was used to get the *actual* field set a page presents (section nesting and
toggle-hidden fields resolved), rather than reading the schema builder by eye.

## Method

1. Read `strings.json` (2283 lines, 1780 leaf keys) and both translation
   catalogs (`translations/en.json`, `translations/sv.json`, 1780 keys each)
   -- the only two languages shipped, matching D4.md's `sv`/`en` scope.
2. Confirmed exact key-set parity across all three files (non-finding below).
3. Built `s2_label_coverage.py`: walks every options-menu page via
   `config_flow_steps.py:fresh_options()` / `async_step_*`, reads the fields
   each page actually renders with `rendered_keys()`, and checks each has a
   label at the matching `strings.json` path. 23/25 menu pages render as a
   form with no extra seeding (the other two -- `entities_metering`,
   `entities_pump` -- need pre-seeded coordinator state to walk past their
   entity-count branch and were left unexplored to stay inside the
   90-minute budget). 0 mismatches found; the harness's own `--perturb`
   (deletes one label from `strings.json` in memory) moves the count 0 -> 1,
   so this is a working instrument, not a vacuous pass.
4. Sampled 8 validation error strings the config/options flow actually
   raises (`invalid_grid_fee_rules`, `grid_fee_rules_negative`,
   `grid_fee_rules_implausible`, `invalid_peak_months`, `invalid_peak_hours`,
   `freq_control_needs_number`, `flow_curve_needs_direct_plant`,
   `prefill_device_unreadable`) against the rubric's "errors that say what to
   change" criterion. All 8 name a concrete field, format or action; no
   counter-example found among the sample. Examples:
   - `grid_fee_rules_implausible`: "A fee rule has a rate above {fee_bound}
     {currency}/kWh. ... almost always ore or cents typed where whole
     {currency} were meant -- 25 instead of 0.25."
   - `invalid_peak_hours`: 'Those hours could not be read. Use 24-hour
     ranges like "07:00-19:00".'
   - `flow_curve_needs_direct_plant`: names the exact fix -- 'Set the valve
     to "No mixing valve" or turn this off.'
5. Counted rendered field count per options page (via the same walk) to
   check the "field count" / "one theme per page" rubric criterion:

   comfort 18, entities 15, hot_water_tank 14, quick_setup 13,
   building_preset 11, entities_metering 11, hot_water 11, building 10,
   tuning 10, entities_pump 9, learning_features 9, thermal_model_zones 9,
   grid 8, heat_curve 8, grid_connection 7, thermal_model 7, grid_fees 6,
   solar_pv 6, learning 5, away 4, modbus_prefill 3, hot_water_pumps 2,
   setup_overview 0.

   The three highest counts (comfort=18, entities=15, hot_water_tank=14) are
   not flat lists: `strings.json`'s `sections` map shows each split into
   named, themed HA sections (comfort: Comfort band / Day and night /
   Weekend / Holiday profile / Mold guard -- 5 sections; entities: Account
   and weather / Room temperatures / Heat pump and tanks -- 3; hot_water_tank:
   Tank / Inlet water / Heat recovery / Disinfection -- 4). Non-finding, not
   a rubric violation, recorded below so the next auditor does not re-open it.
6. Compared `translations/en.json` against `translations/sv.json`
   string-by-string (not just key-by-key) for pairs identical at the same
   path, which is how an untranslated field surfaces in the real UI. Found
   11 identical pairs; 3 are `/exceptions/*/message` bodies that are
   format-only placeholders (`"{violations}"`, `"{error}"`) and excluded
   structurally, leaving 8. Reviewed each of the 8 by hand: 7 are
   legitimately identical (brand names `Tibber`/`Open-Meteo`, bare numeric
   ranges `1960-1980`/`1980-2005`, the Swedish-identical loanwords
   `Legionella` and `Tank`, and one Swedish utility's own already-Swedish
   product name). The 8th, `/options/step/heat_curve/data/ecl110_mqtt_qos`
   ("MQTT quality of service"), is not: its sibling field on the same page,
   `ecl110_mqtt_retain`, *is* translated ("Retain MQTT messages" ->
   "Behall MQTT-meddelanden"), so this is a genuine miss, not a deliberate
   choice to leave technical vocabulary in English. Built into
   `s2_translation_gap.py` with the review captured as an inline
   `ALLOWLIST`, so the harness's `RESULT untranslated_residual=1` count and
   its perturbation (translating the string in memory drops the count to 0)
   are reproducible without re-doing the by-hand review. -> D4-s2-01.
7. Counted config-flow steps from install to first plan along the
   quick-setup and questionnaire paths by reading `async_step_*` chains
   (`user -> user_sensors -> finish_setup(menu) -> quick_setup ->
   device_prefill -> finish_setup -> finish_now -> setup_overview ->
   create_entry`, i.e. as few as 4-5 submitted screens; the questionnaire
   path adds `temperature -> building -> building_describe ->
   building_extras -> thermal -> zones -> dhw -> weather_sensitivity`
   before the same `setup_overview -> create_entry`, ~12 screens). Did not
   find a defect in this count within budget; recorded as description, not
   scored against a rubric threshold since D4.md asks only to count it.

## Findings

**D4-s2-01** (low, hygiene) -- one options-flow field label,
`ecl110_mqtt_qos` on the Heat curve control page, is left in English in
`translations/sv.json` while every sibling field on the same page and the
same section is translated. Full evidence in `report-s2.json`; harness at
`tools/audit/round8/D4/s2_translation_gap.py`.

Note on finding-id format: the task brief for this seat specifies IDs of the
form `D4-s2-01`; `tools/audit/finding.schema.json`'s `id` pattern
(`^D(1[0-3]|[0-9])-[0-9]{2}$`) does not admit the `-s2-` seat infix and
rejects it (checked directly: substituting a schema-legal id validates the
rest of `report-s2.json` clean). `report-s2.json` keeps the task-specified
`D4-s2-01` per the task's explicit instruction rather than renaming to
`D4-01`, since a same-numbered `D4-01` from seat s1 would then collide.
Flagged here as a harness gap, not filed as an issue.

## Non-findings

1. **Translation key-set parity.** `strings.json`, `translations/en.json`
   and `translations/sv.json` all have exactly 1780 leaf keys, 0 missing in
   either direction, 0 orphans in either direction. No field or error string
   can fall back to a raw key for lack of an entry. (Ad hoc key-flattening
   comparison script, run inline during the audit.)
2. **Label coverage for rendered options fields.** 0 fields across 23
   walkable options pages render with no matching `strings.json` label.
   `tools/audit/round8/D4/s2_label_coverage.py`; `RESULT
   unlabeled_fields=0`, moves to 1 under `--perturb`.
3. **Sampled validation error text.** 8/8 sampled error strings name a
   concrete corrective action (field, format example, or setting to change),
   meeting the rubric's "errors that say what to change" criterion. Manual
   review, see Method step 4.
4. **High per-page field counts are sectioned, not flat.** comfort (18),
   entities (15) and hot_water_tank (14) -- the three highest field counts
   among options pages -- each split into 3-5 named, themed HA sections
   rather than one undifferentiated list, so the raw count does not indicate
   a "one theme per page" rubric violation. Method step 5.
5. **Undocumented import-time trap in `tests/config_flow_steps.py`.**
   Importing this module (the natural harness for walking the flow) runs
   its entire 454-check self-test at import time and ends with
   `sys.exit(asyncio.run(main()))` at module scope. This is not on
   `tools/audit/README.md`'s named trap list (which names `entities.py,
   features.py, rolling.py, backtest.py, optimality.py` for this behaviour
   and omits `config_flow_steps.py`). Both harnesses in this report
   neutralise `sys.exit` and swallow the import-time stdout before
   importing it, and both are proven not to depend on any state that
   self-test run would have mutated (they only build a *fresh*
   flow/options object per `fresh_flow()`/`fresh_options()` afterwards).
   Recording as a harness gap, not a product defect, per `CLAUDE.md`'s
   "fix it, or verify independently, or file" chain: independently verified
   and worked around here, so nothing to file.

## Harnesses

- `tools/audit/round8/D4/s2_label_coverage.py`
- `tools/audit/round8/D4/s2_translation_gap.py`

Both run from the tree root, no arguments for baseline, `--perturb` for the
stated perturbation; both print `RESULT` lines including `load1` and
`thread_factor` per the harness contract even though neither number is a
timing/CPU measurement (both are exact, deterministic counts over static
JSON/schema data, so no contention or BLAS-thread caveat applies to their
correctness).

## What could not be finished

- Method step 1 (the card in a real browser) is seat s1's, not attempted
  here.
- Two options pages (`entities_metering`, `entities_pump`) were not walked
  by `s2_label_coverage.py` because they need pre-seeded coordinator/entity
  state to render past an early branch; left unexplored inside the time
  budget rather than hand-building that state. Coverage claim is 23/25, not
  25/25.
- Did not build a full rubric-scoring rig (one score per page against the
  6-criterion written rubric in D4.md) across all 25 options pages plus the
  ~17 initial-flow pages; sampled instead (error text: 8 keys; field
  count/grouping: the 3 highest-count pages) to stay inside budget, per
  COMMON.md's preference for a few solid findings over exhaustive but
  unreviewed coverage.

## Exposure

None. No `docs/` or GitHub material was read; this seat's tree has neither
(`COMMON.md`'s stripped-baseline setup).
