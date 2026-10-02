Fix review: blocked 0077ab5aed0c4e406322fd3e648bfc69f31dc23b typing: sensor.py:2852 new mypy arg-type error (rank_sensor_gaps language param vs **_gap_probe_terms), CI typing red; that caller is also an unlocalised N-language seam

Round 1. PR #1806, code head f95051f4e5904df3c260745487b2d10e33fa4757, PR head measured 0077ab5aed0c4e406322fd3e648bfc69f31dc23b (main 787fe137 merged in). Live head at posting is 44a0ba7e9e2d59b50966dc849d3dc569ea12aad9, the CI autofix "pin killed mutants" commit: 4 mutation-ledger JSON files, no code, so every figure below holds there.

BLOCKING
1. typing (CI red at f95051f4, job 110296909321: errors 0 -> 1, by_code[arg-type] 0 -> 1, sensor.py 1). Reproduced locally at f95051f4 and 0077ab5a with the pinned mypy 2.3.1 + homeassistant-stubs 2026.9.3 (--no-deps install, Python 3.14):
   sensor.py:2852: error: Argument 7 to "rank_sensor_gaps" has incompatible type "**dict[str, float]"; expected "str"  [arg-type]
   Cause: the new `language: str = "en"` parameter on topology.rank_sensor_gaps is positional-or-keyword, so mypy matches the `**_gap_probe_terms(...)` dict[str, float] against it. Fix: make language keyword-only (`*, language: str = "en"`) or type the probe terms as a TypedDict. The body's "Red checks: none known" must then name typing and answer it (defect-root-cause.md second trigger): the cheaper detector is typing_ruler --mypy, which the fixer could not run on Python 3.11.
2. Same call site, class seam left open: SensorGapAdvisorSensor._gaps (sensor.py:2845-2858) calls rank_sensor_gaps with no language, so the sensor_gap_advisor entity's `gaps` attribute still publishes English labels on a Swedish install. The body's Figures line "every caller passes the language" is false for this caller. Pass language=self.hass.config.language here (fixes both items) and pin it.

OWED IN THE SAME ROUND (targeted mutants, run at f95051f4 in a CPython 3.13 venv with pinned requirements-ci, OPENBLAS_CORETYPE=Haswell)
3. The production wiring the finding is about is unpinned. Survived (every listed script rc 0):
   M1 coordinator.py describe_setup without hass.config.language (entities, features, config_flow_steps, env_drift --all)
   M2 config_flow.py _setup_overview_form describe_setup without flow.hass.config.language (config_flow_steps, entities, features)
   M3 coordinator.py _with_sensor_advisor without the language arg (entities, features, env_drift --all)
   M5a catalog description untranslated; M5b catalog requirement untranslated; M6 rank_sensor_advisor labels untranslated (features, entities)
   Killed: M4 _tr returns its input (3 features checks); M7 source_entity always None (1 entities check).
   Wanted: a config-flow/entity check driven with an sv hass (hass.config.language = "sv") that asserts the setup_overview text and setup_topology slot labels are Swedish, plus the gap advisor and sensor_advisor labels, and the catalog description/requirement. The fixer's own features checks only call topology with "sv" directly.

FINDER'S HARNESS (fixer.md step 3; the body does not cite it)
tools/audit/round9/D4/leads/l4_setup_labels.py at 79aa98ec, sha1 d3e719f46159fbe4471cc83b7193ca3cdaccd667.
- base cc00ed85: RESULT en_identical_total=41 (22 of 23 page lines, 16 of 16 slots, 3 of 3 advisor), null narrative 0 of 1. Matches the finding exactly. --perturb: 0.
- head 0077ab5a, unadapted: AttributeError: '_Flow' object has no attribute 'hass' (the harness's flow stub predates the new flow.hass read).
- head 0077ab5a, my adapter (disclosed: sha1 1a9192f8a2bbbd044420172a01c9b03752adca1b; adds hass.config.language to the flow stub and passes lang to describe_setup / rank_sensor_advisor, adapter.diff in this directory): en_identical_total=0 (0 page lines, 0 of 16 slots, 0 of 3 advisor), null 0 of 1. The fix moves the finding's metric 41 -> 0. The harness does not cover the sensor_gap_advisor seam in item 2.

VERIFIED CLEAN
- coordinator.py vs merge base cc00ed85 and vs main 787fe137 in the merge: exactly the two intended call changes (_with_sensor_advisor, describe_setup); no import churn from the lint hook.
- Golden: the five coord_* fixtures move by +5/-1 lines each, only setup_topology.language ("en", on both plan sensors) and indoor_temp.extra_state_attributes {source_entity: null}. No solver float moved. Both claim files claim exactly these (5 coord, 5 card history states); claims-for 6.7.12 = VERSION. env_drift.py --all origin/main at f95051f4: NO UNCLAIMED DRIFT (56), NO STALE FIXTURE (56).
- Merge 0077ab5a tree 7dd4fd1d equals git merge-tree 787fe137 f95051f4; no MERGE-CLAIM lines; no transport BODY.md or resume file in the code-head ancestry of the PR tree.
- VERSION, manifest version and notes heading untouched. No budget raise; structure.py passes.
- features 3631, entities 1998, config_flow_steps 495, card.mjs all pass at f95051f4.
- Real-HA ha_contract (Mac, HA 2026.9.3) at f95051f4: 61 contracts and 22 probe comparisons passed; the 2025.2.0 floor arm was not run.
- docs/img/card and docs/dashboard-card.md: required from UI-3 on; F6.4 precedes UI-3, so not owed here.
- Now-temp label: plan.now_temp "{temp} °C" in en and sv per tvofi's carry; key unchanged; no doc or test quoting the old text remains outside historical audit records. CI browser lane (overlap grid with the short string) was still running when I posted; cite it at the next head.

NITS (carry into the next push)
- topology.py _SV: "ingen (leveransen strypsas inte)" should read "ingen (leveransen stryps inte)".
- The sv summary still shows the raw valve mode value ("Blandningsventil: manual"); not a finding of this PR, mention it if not fixed.
- sensor.py: CONF_INDOOR_TEMP_ENTITY is inserted between the ECL110 imports, out of sorted order.

CI at 0077ab5a when posted: typing, fast, mutation, coverage, browser, closures, env-matrix still running; typing will repeat the sensor.py:2852 error (reproduced locally at 0077ab5a).
