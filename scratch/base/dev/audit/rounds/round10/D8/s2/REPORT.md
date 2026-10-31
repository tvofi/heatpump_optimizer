# D8-s2 — D8.M3 ordering and naming (baseline 17f1c55fad1b)

## Method
`order.py` builds a real `HeatPumpOptimizerCoordinator` per `tests/golden.py:coordinator_scenarios()`
cell (5 cells), injects prices/forecasts as `_capture_coordinator` does, runs `_build_data_dict`,
constructs every platform's entities via its real `async_setup_entry`, and sorts the constructed
set by display name (en/sv translations, sv collation å<ä<ö after z) and by entity_id per platform.
Families: `const.ENTITY_FAMILY_OVERRIDES`, else the translation key's lead token. Run over all
entities and over the enabled-by-default subset. Catalogue check: strings.json vs en.json vs sv.json.

## Findings
None.

## Non-findings
- Name-sort family splits, all entities, 5 cells: en 0, sv 0 (`order.py`). Enabled-only: en 0, sv 0 (`order.py --enabled`).
- Positive control `--control` (homes optimal_setpoint in `cost`): en 5, sv 5 — instrument moves.
- Constructed entities without a translation: 0; duplicate en display names: 0.
- strings.json == en.json names (81 keys), sv has all 81 keys, none extra, none identical to en.
- entity_id split: `lifetime` family in sensor, 5/5 cells — declared and intended: const.py's override
  comment states ids/translation keys are untouched for the four lifetime meters (the family is a
  name-sort declaration only). Not a defect.
- Undeclared groupings (proposed declaration changes, not splits): `Lower Floor Temperature` /
  `Upper Floor Temperature` (two-zone pair) sort apart; `Indoor Temperature (Predicted)` vs `Prediction Accuracy`.

## Harnesses
`dev/audit/rounds/round10/D8/s2/order.py`

## Unfinished
None for M3. Exposure: none.
