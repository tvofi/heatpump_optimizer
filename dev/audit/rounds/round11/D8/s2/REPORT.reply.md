I covered all six files in my D8.M3 universe (ordering and naming) and found two problems, both low severity. Nothing is unfinished or not reached. I committed nothing and pushed nothing. I could not validate REPORT.json against `finding.schema.json` because the venv has no `jsonschema` module, so `check_report.mjs` on your side is the first real check. Load1 was 24 to 52 while I ran, but every number here is a count, so contention does not affect it.

**REPORT.json:** `/Users/timmalmstrom/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D8/s2/REPORT.json`

---

# D8-s2 REPORT (round 11, D8.M3 — ordering and naming)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Export tree `/Users/timmalmstrom/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline`. Exposure: none.

## Method
- **Cells:** `check_scopes.py --seat D8-s2` prints six files, all for step M3: `binary_sensor.py`, `button.py`, `climate.py`, `entity.py`, `sensor.py`, `switch.py`. I examined all six (6/6).
- **Building the entities:** `rig.py` builds each of the five `coordinator_scenarios()` coordinators the way `golden._capture_coordinator` does. It then calls every platform's real `async_setup_entry` and keeps the union of what they add. That gives 82 entities: sensor 62, binary_sensor 6, button 6, switch 6, climate 1, datetime 1.
- **What `m3_naming.py` measures:**
  - Family splits in the `entity_id` sort, per platform and across all platforms. A family is the `ENTITY_FAMILY_OVERRIDES` entry, otherwise the translation key's first token.
  - Family splits in the display-name sort for en, sv and de, using the same collations as `tests/entities.py`.
  - Missing and duplicate names.
  - `strings.json` against every translation file: missing keys, extra keys, placeholder sets, and that en matches value for value.
  - A state string for every ENUM option.
- **`m3_placeholder.py`** presses the real optimize-now button with a "no prices" result. It then formats the exception's message in every shipped language, using the placeholders the exception actually carries.

## Findings

**D8-s2-01 (low, bug, class `new`): the German "optimization did not run" message cannot be filled in.**
- `translations/de.json` `exceptions.run_optimization_no_prices.message` uses `{entry_id}`.
- `strings.json`, `sv.json` and both places that raise this error pass only `entry_ids`: `button.py` `ForceOptimizationButton.async_press`, and `services.py`.
- Measured: `unrenderable_langs=1` (de is missing `entry_id`).
- Perturbation `--perturb-de` (rename the placeholder to `{entry_ids}` in memory): 0.
- Null control: pressing with no failure raises nothing (`null_raised=0`), and en and sv format cleanly.
- Effect: Home Assistant drops a translation whose placeholders don't match English, so German users get the English text.
- To check every translation string the same way: `m3_naming.py` `tr_placeholder_<lang>` reads de=1, en=0, sv=0.
- Fix: change `de.json` to `{entry_ids}`. Also add a placeholder-equality check to `tests/entities.py`, whose current drift check compares keys only.

**D8-s2-02 (low, hygiene, class `N-name-sort`): the declared "lifetime" family sorts as three separate groups by sensor `entity_id`.**
- The four members are `cost_total_heating`, `space_heating_cost`, `space_heating_energy` and `total_energy`.
- #1668 renamed their display names to start with "Lifetime" but left their keys, and so their suggested ids, unchanged.
- Measured: `fam_runs_excess_entity_id_sensor=2`.
- Perturbation `--perturb-lifetime-ids` (give each id a `lifetime_` lead in memory): 0.
- Null control: every other platform reads 0, and the name sorts read 0 in en, sv and de.
- Fix: for new installs only, move the suggested ids the way #1227/#1333 did (unique ids stay the same, so existing installs keep their ids and history). Alternatively, the owner rules that a declared family only governs the name sort.

## Non-findings
- **Name sorts:** every family is one contiguous group in en, sv and de (`fam_runs_excess_name_*=0`).
- **Names:** no entity is missing a name and no two entities share one, in any language.
- **Translation keys:** no key is missing from or extra in de, en or sv, and `en.json` equals `strings.json`.
- **ENUM states:** every option has a state string in every language.
- **`entity_id` sorts:** binary_sensor, button, switch, climate and datetime each read 0. Across all platforms the count is 9 at baseline and 7 once the lifetime ids are moved; every remaining split falls where one platform's ids end and the next begin, which no key change can cross.
- **Unofficial groupings (suggested declaration changes, not splits):**
  - `dhw_cost` and `dhw_energy` are "(lifetime)" meters but sit in the dhw family.
  - The climate entity "Heat Pump Optimizer" and the sensor "Heat Pump Action" share the lead token "heat" by accident.
  - optimal, optimization, optimize and optimizer are separate families that happen to sort next to each other.

## Harnesses
In `dev/audit/rounds/round11/D8/s2/`: `rig.py`, `m3_naming.py`, `m3_placeholder.py`. Findings are in `findings/D8-s2-01.json` and `findings/D8-s2-02.json`.

## Leads
1. **Owner unknown, `dev/audit/config/scopes.json`:** the M3 universe leaves out `datetime.py`, which ships `away_return` in the "away" family. My rig measured it anyway, outside the enumerated cells.
2. **Owner unknown, `services.py` `run_optimization`:** this is the second place that raises the same exception as D8-s2-01. The de fix covers it, but no harness here drove that path.

## Unfinished
None.