All 21 gold rules for D10-s2 (D10.M1 and D10.M2) are measured, and 3 of them fail. My count for gold is now 14 done, 4 exempt and 3 todo; the register says 17 done and 4 exempt. REPORT.json, four finding files, eight harnesses, a shared builder and the draft register are in `dev/audit/rounds/round11/D10/s2/`. Nothing was committed or pushed.

**REPORT.md does not exist.** The tool refused that write because sub-seats may not write report `.md` files. Its content (method, tier table, findings, exposure) is below and in REPORT.json, whose `report_path` I pointed at itself so it doesn't name a missing file. `jsonschema` isn't installed here, so I checked the report against the schema by hand: required fields, field lengths and coverage rows.

**Findings** (all counts, so contention doesn't affect them; each harness's number moves under its perturbation):

| id | severity | rule | measured | perturbation |
|---|---|---|---|---|
| D10-s2-01 | high | reconfiguration-flow | 2 of 2 changed keys have no effect; 0 on an entry with no saved options | patch the save to also clear those keys from options: 0 |
| D10-s2-02 | high | entity-device-class | 3 sensors pair device class energy with state class measurement | set the state class to total_increasing: 0 |
| D10-s2-03 | low | exception-translations | 2 raise sites with mismatched German placeholders | delete one English entry: 4 |
| D10-s2-04 | low (hygiene) | entity-device-class | 3 temperature-difference sensors have no device class | give one the new class: 2 |

- **D10-s2-01:** Reconfigure saves only to `entry.data`, but the coordinator reads `{**entry.data, **entry.options}`. Once a user has saved the Options "Entities" page, which stores the same keys, a reconfigure reports success and the old indoor sensor and weather entity stay in force. The form is also prefilled with the old value, not the one running. Driven through the real options flow and the real reconfigure steps (`reconfig_shadow.py`).
- **D10-s2-02:** Lifetime Space Heating Energy, DHW Energy (lifetime) and Lifetime Total Energy inherit `MEASUREMENT` from `sensor._AccumulatingSensor`. HA's `DEVICE_CLASS_STATE_CLASSES` forbids that pair, logs a warning, and the recorder builds no sum statistics, so they stay out of the Energy dashboard (`entity_census.py`).
- **D10-s2-03:** In `translations/de.json`, `run_optimization_no_prices` uses `{entry_id}`, while `button.py` and `services.py` pass `entry_ids`. HA drops the German text and shows English. Checked over 37 raise sites, including 3 that pass the key through helpers, in 4 catalogues (`exc_translations.py`).
- **D10-s2-04:** ECL110 Displace, ECL110 Effective Displace and Prediction Accuracy are °C differences with no device class. `TEMPERATURE_DELTA` first appears in HA 2025.11.0; it is absent at 2025.10.0. This is the only todo that needs an API newer than the `hacs.json` floor (2025.2.0), which M2 asks for.

**Tier table** (rule: status, measured value)
- **devices:** done. 82 of 82 entities sit on one device marked as a service.
- **diagnostics:** done. 0 coordinate leaks across 4 arms (solar location in options, solar location in data, HA home fallback, device_tracker presence), with the debug bundle and recorder replay included; the perturbation gives 31.
- **discovery, discovery-update-info, dynamic-devices, stale-devices:** exempt, and every reason is still true: 0 discovery keys or steps, 0 device-registry writes, no remove hook, 1 device.
- **docs-data-update:** done. The docs state 30 min, matching the code default of 30.
- **docs-examples:** done. 5 blueprints, all 5 linked.
- **docs-known-limitations, docs-supported-devices, docs-troubleshooting, docs-use-cases:** done. Each README section exists, with 10, 6, 43 and 9 entries.
- **docs-supported-functions:** done. All 82 entities are named; the 62/6/6 headings match; the disabled list matches the 20 the code disables.
- **entity-category:** done. 24 diagnostic, 58 primary.
- **entity-device-class:** todo (02, 04).
- **entity-disabled-by-default:** done. 20 disabled by default.
- **entity-translations:** done. 0 missing names or states in 4 catalogues.
- **exception-translations:** todo (03).
- **icon-translations:** done. 0 missing, 0 icons pinned in code.
- **reconfiguration-flow:** todo (01).
- **repair-issues:** done. 29 raise sites, 0 bad, 0 unused catalogue keys.

**Coverage**
- **Universe:** both steps range over the 21 gold rows printed by `python3 dev/audit/rounds/round11/D10/s2/enum_gold.py`. All 21 examined, nothing unreached.
- **Q1:** the 21 rows equal the fetched checklist's gold list (`enum_gold.py --checklist`).
- **C1 (from last round):** examined. I fetched the rule pages and counted the seven docs rules, entity-category, entity-device-class and entity-disabled-by-default separately.
- **Unfinished:** nothing.

**Leads**
- **D10-s1, reauthentication-flow:** the same shadowing probably affects reauth. It writes the new Tibber token only to `entry.data`, and the saved Entities page also stores `tibber_token` in options.
- **README.md:** it says the three energy sensors feed the Energy dashboard; that is false while D10-s2-02 stands.
- **Other failures in `tests/entities.py`, not measured by me:** two-zone flips on an untouched options save, thermal-battery store naming, sensor-gap advisor ordering, and a `KeyError` on `house_heat_loss_coefficient`.

**Exposure:** I read `README.md` and `docs/how-it-works.md`, and fetched HA's developer docs and core source from upstream. I ran `tests/entities.py` once at the baseline. That run independently showed the energy state-class failure, but no finding rests on it. Two scratch diff files went to `/tmp`.

Files are in `<HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D10/s2/`:
- REPORT.json
- findings/D10-s2-01.json … D10-s2-04.json
- quality_scale.draft.yaml
- entity_census.py
- exc_translations.py
- reconfig_shadow.py
- diag_locations.py
- repair_issues.py
- exempt_rows.py
- docs_gold.py
- enum_gold.py
- _census.py
- rules/