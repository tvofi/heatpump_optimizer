# D5 round 9 — verifier V3 (reach and class)

Worktree /home/claude/wt (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 plus round-9 evidence). The box is a 4-core cloud container running CPython 3.14 and node v22. Every number below is a count or a ratio that contention cannot move. load1 ranged 0.31–3.08 and thread_factor was 1.000 on every run. My harnesses are in `tools/audit/round9/D5/verify-v3/`, and each carries the contract header and a `--perturb` arm.

## D5-s1-01 — configuration.md Initial setup: stale flow — **verify, medium**

- **Finder's harness, re-run:** `setup_section.py` gave stale_facts=4, and 1 under `--perturb`. `entity_counts.py` gave constructed=75, disagreeing=1, and 2 under `--perturb`.
- **My harness, `v3_s1_01_setup.py`:** the input is first validated through `_user_credentials_fields()`, as Home Assistant's FlowManager does on a real install. Results:
  - tokenless_schema_valid=1 and tokenless_reaches=1.
  - finish_menu_unnamed=3, and 0 under `--perturb`.
  - building_menu_unnamed=0 (control).
  - first_screen_fields_unnamed=2.
  - Entities: 75 at every one of the 5 golden coordinator configs.
- **Reach:** the finder's harness skips schema validation. Adding it still admits the tokenless screen, because token and price entity are `vol.Optional`. On the Tibber arm a missing token returns `tibber_token_required`, so the doc's "required" is true of that arm only.
  - `ConfigFlow` is FAITHFUL in `tests/ha_contract.py`.
  - The en.json finish_setup labels equal the fallback labels, so a real frontend shows the same three names.
- **Severity:** medium is earned. A user without Tibber reads the token as mandatory; the real form offers a price-source choice, which is the workaround.
- **Seam rule: partial.** It checks the finish menu and the token only. My first-screen rule finds 2 more unnamed labels: "Electricity price source" and "Price sensor".
- **Class:** I5 confirmed.
- **Metric:** en.json labels of the finish-menu entries on the tokenless path that the section never names, plus the entity count across 5 configs.

## D5-s1-02 — Quick setup promises storage it cannot produce — **verify, medium**

- **Finder's harness, re-run:** unhonoured_promises=2, and 0 under `--perturb`.
- **My harness, `v3_s1_02_quick.py`:** drives the production flow end to end: user → user_sensors → quick_setup (all toggles yes, both probes) → device_prefill declined → finish_setup → setup_overview → create_entry. It then reads the coordinator's own `_ctx._thermal_params`. Results:
  - buffer_is_store=0, two_tank_modelled=0, unhonoured_promises=2.
  - 0 under `--perturb` (a throttling valve added to the entry).
  - hold_two_zone_enabled=1 and control_no_probes_two_tank=0.
- **Reach:** no DIVERGENT stub symbol is on this path. The extra steps the real flow inserts write no valve key.
- **Severity:** medium. A buffer-tank owner who answers "yes" silently gets no store planning. The loss is bounded, and setting the valve on the Heating system page works around it.
- **Seam rule: partial.** It covers 2 of the 5 answers' promises. The wood-furnace promise ("stands the pump down while the fire is lit") is enumerated by neither rule.
- **Class:** I5.
- **Metric:** of the 2 promises, how many the coordinator built from the real flow's entry fails to honour.

## D5-s1-03 — card-version lag paragraph — **verify, low**

- **Finder's harness, re-run:** share=1.00, and 0.00 under `--perturb`.
- **My harness, `v3_s1_03_cardver.py`:** reads real release history with `git show`. 30 of the last 40 VERSION commits ship a CARD_VERSION equal to VERSION, and those 30 are the newest ones, consecutive (6.3.13 through 6.7.1). The most recent mismatch is 6.3.12, which shipped card 5.4.20. The in-memory stamp arm gives equal=1, and 0 under `--perturb`.
- **Consequence:** the doc's "often lower" was true up to 6.3.12 and has been false for 30 stamps. The banner prints in the real browser console. Low.
- **Seam rule: false.** It keys on one literal sentence. My grep of README plus the 7 user docs finds no second card-version statement, so no seam is missed today.
- **Class:** I5.
- **Metric:** consecutive newest stamps where CARD_VERSION equals VERSION.

## D5-s1-04 — 9 lines rendered in the wrong block — **verify, low**

- **Finder's harness, re-run** (markdown-it 14.1.0): 9, and 0 under `--perturb`.
- **My harness, `v3_s1_04_tables.mjs`:** uses a second, independent GFM parser (micromark 4 plus micromark-extension-gfm-table 2). It finds 3 orphaned rows (configuration.md:185–187) and 6 swallowed prose lines (:633–638), 9 in total. Under the finder's repair applied in memory it finds 0.
- **Reach:** GitHub renders these docs; there is no Home Assistant path.
- **Severity:** low hygiene.
- **Class: null.** No bugclasses.json class fits: I5 is drift against code, and this is markup against the renderer. This agrees with the finder's "new".
- **Seam rule: true.** It covers every pipe row and every prose line in all 8 user docs, and docs/ holds no other user doc.
- **Metric:** lines the reference GFM parser places in the wrong block.

## D5-s1-05 — 5 field names not on the form — **verify, low**

- **Finder's harness, re-run:** 5, and 4 under `--perturb`.
- **My harness, `v3_s1_05_labels.py`** (468 en.json labels): finder_sites_unfound=5, and 0 under `--perturb`. None of the five is a substring of any label.
- **Broader rule:** italic or bold spans near a form noun give 12 unfound. 8 of those are entity names or selector options, and 4 remain; none of the 4 is a new form-label miss.
- **Reach:** the real frontend renders these labels from en.json; the stub's empty translation loader is not on this path.
- **Seam rule: partial.** It covers table rows and italics but not bold. My bold probe found 0 further misses.
- **Class:** I5.
- **Metric:** of the finder's 5 names, how many are a substring of no en.json label.

## D5-s1-06 — five simulate_plan wood fields undocumented — **verify, low**

- **Finder's harness, re-run:** 5, and 0 under `--perturb`.
- **My harness, `v3_s1_06_services.py`:**
  - 12 services registered, with 67 schema keys; schema_not_in_yaml=0.
  - yaml_fields_undocumented=5, and 0 under `--perturb`.
  - en_labels_for_all=1.
- **Reach:** HA's Actions UI lists all 16 fields with en.json names, so the gap is in configuration.md only. That bounds the consequence, and low holds.
- **Seam rule: true.** It walks every key of every registered schema.
- **Class:** I5.
- **Metric:** services.yaml fields that the Services section never names in backticks.

## D5-s2-01 — 12 stale `_name` references in card comments — **verify, low**

- **Finder's harness, re-run:** 12/17, and 5/6 under `--perturb`.
- **My harness, `v3_s2_01_cardnames.py`:** lexes the card file line by line and keeps string literals as code, which can only hide a stale name. It finds the same 12 names with 17 mentions, and 5/6 under `--perturb`.
- **Reach:** these are comments; there is no runtime behaviour.
- **Seam rule: partial.** It covers underscore-prefixed names only. Of the 60 backticked camelCase names without an underscore, 2 are unresolved, and both are external APIs (Lovelace `editMode`, DOM `getComputedTextLength`). So 0 defects are missed.
- **Class:** I5.
- **Metric:** comment `_name` identifiers that match no code token in the card or in production .py.

## D5-s2-02 — three comment numbers — **verify, low, value 2 (finder: 3)**

- **Finder's harness, re-run:** mismatches=3, hold failures 0 of 5, and 0 under `--perturb`.
- **My harness, `v3_s2_02_03_numbers.py`:**
  - The defrost derate floor reads 0.550 at the bucket centre after 2000 observations at 10 % delivered; the comment says 0.5.
  - The default update interval is 30 minutes; the selector admits 10 to 120 minutes in steps of 5.
  - comment_numbers_unreachable=2, and 0 under `--perturb`.
- **Why my number differs:** the valve-write comment's "every 15 minutes" is a cadence a user can select. Under my reachable-set definition that row holds; under the finder's default-value definition it does not. Both definitions are stated for the judge.
- **Stub:** `tests/hastub`'s `DataUpdateCoordinator` drops `update_interval` (SIMPLIFIED in ha_contract), so I captured the value at the production call, as real HA would schedule it.
- **Seam rule: false.** The rows are hand-listed; comment numbers across the tree are not enumerated.
- **Class:** I5.
- **Metric:** comment numbers outside the value set the production symbol can deliver.

## D5-s2-03 — DHW_COLD_WATER_TEMP coupling comment — **verify, low**

- **Finder's harness, re-run:** 46 of 47, and 0 of 47 under `--perturb`.
- **My harness** (same file as s2-02) runs `ThermalModel.simulate_trajectory_with_dhw` with the coil forced active and the inlet configured at 15 °C:
  - coil_calls=8, of which 0 use the constant; every call received `inlet_temp=15.0`.
  - The draw's cold end is 15.000 °C.
- **Default attack:** at the shipped inlet of 10.0 the comment's "~10 °C" holds. The drift shows only on a configured inlet, which the options selector admits across 2–25. The coupling the comment claims is absent at every call site either way.
- **Seam rule: false.** One coupling was hand-picked.
- **Class:** I5.
- **Metric:** coil calls on the default constant at a 15 °C inlet.
