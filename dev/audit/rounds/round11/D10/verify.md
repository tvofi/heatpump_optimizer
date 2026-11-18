# D10 verify, round 11

All twelve findings are scoped to planted seats (D10-s1..s3), so every number below comes from the private export copy `audit-r11-px-D10`, with `PYTHONPATH=tests/hastub` and the venv-ci Python 3.14. The box was under heavy contention (load1 122-137). thread_factor was 0.999-1.000 on every run. All the numbers are counts, so contention does not move them.

| id | V1 (finder harness) | perturbation | null | V2 (my measurement) | vote |
|---|---|---|---|---|---|
| D10-s1-01 | acknowledged_unparseable=6, cleared=3 | -> 0 / 0 (down) | control_accepted=1 | away._parse_return_time -> drift.stored_instant: "Anything that does not parse is None"; the set_away path stores None and raises nothing | verify |
| D10-s1-02 | silent_refusals=2 | -> 0 | controls_raised=2, sysid_enabled_armed=1 | button.py:155 and :216 hand the work to entity.off_the_action (a background task); a refusal never reaches the press | verify |
| D10-s1-03 | continue_settings_in_data=41 | -> 0, merged_equal=1 | finish_now=0 | config_flow.py:2898 `data=self._data` holds every step's keys | verify |
| D10-s1-04 | hidden_on_single_zone=2 | -> 0 | mode_off renders=1, zone_keys hides=1 | thermal from_config line 1122: `two_zone_mode in (ON, DEFAULT)`, where DEFAULT is auto, so the presence test never runs for auto | verify |
| D10-s1-05 | unrecovered 51/53, never_stepped_past 49 | -> 47 / 46 (down) | (none stated) | crude per-function count: 19 test functions mention errors, 8 of them reach a finish (a different unit; table-driven) | weaken |
| D10-s1-06 | see the coverage section below | | | | see below |
| D10-s2-01 | shadowed_options_saved=2 | -> 0 | shadowed_null=0 | _async_save_reconfigure writes entry.data only (config_flow.py ~2826-2840), and options override data | verify |
| D10-s2-02 | impossible_pairs=3 | --perturb-state -> 0 | | sensor.py:1791 _AccumulatingSensor has state_class MEASUREMENT; Space/DHW/TotalEnergySensor set device_class ENERGY and do not override it | verify |
| D10-s2-03 | bad=2 of 37 sites | -> 4 | | de.json reads `{entry_id}` and en.json `{entry_ids}`; button.py:119 and services.py:607 pass entry_ids | verify |
| D10-s2-04 | delta_bare=3 | --perturb-delta -> 2 | | sensor.py:1356/1378: degC + MEASUREMENT, no device_class | verify (low) |
| D10-s3-01 | untyped_requirements_under_done_row=1 | req -> 0, row -> 0 | | venv threadpoolctl 3.7.0 is a single module with no py.typed; manifest.json:26; quality_scale.yaml:199 says done | verify (low) |
| D10-s3-02 | coordinator_untyped_under_done_row=1 | coord -> 0, row -> 0 | | coordinator.py:3495 has no config_entry annotation | verify (low) |

## V3: reach and class

- **D10-s1-01:** reachable in real HA through the set_away service with any free text. The failure leaves away on with no return time, so the user's return is dropped silently (medium). Class N-silent-zero confirmed: a parse failure becomes None.
- **D10-s1-02:** reachable, since a button press in the UI is real. The user sees success, and the cost is that misleading feedback (low-medium). Class: new.
- **D10-s1-03:** reachable at setup. It is a quality-scale and maintainability defect (low). It is also the mechanism behind s2-01, which is what the s1-03 seam_rule enumerates.
- **D10-s1-04:** reachable. A single-zone user cannot edit the heat loss coefficient in options (medium).
- **D10-s2-01:** reachable. A reconfigure acknowledges success and changes nothing (medium). Class P2 is plausible (a shadowed write). The seam_rule names one demonstrated seam; the s1-03 split is the general seam.
- **D10-s2-02:** reachable. Real HA logs a state-class warning and the statistics/energy dashboard may reject the sensors (medium).
- **D10-s2-03:** reachable only for a German locale. The message renders the placeholder unformatted or fails formatting (low).
- **D10-s2-04, D10-s3-01, D10-s3-02:** quality-scale and typing correctness only, with no runtime effect (low).

## Coverage (D10-s1-06)

The cov_modules.sh all-stage re-run had not finished after more than 20 minutes at load1 about 130, so it produced no V1 number. Vote: unresolved. Attack: the finder's own mechanism says 15 of 25 scripts exit non-zero on the export tree. Coverage measured that way counts lines that crashed scripts never reached, which is an artefact of the export or stub tree rather than a measure of the suite.

## Test-gap mutation for D10-s1-05

I did not demonstrate a production mutation that survives the suite. Without one, step 4 is unmet, so the vote is weaken, not verify.
