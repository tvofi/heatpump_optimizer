# Round 9 · D6 (README and documentation claim verification) · seat D6-s2

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, export `/home/claude/audit-r9-baseline`,
interpreter `/home/claude/venv314/bin/python`, `PYTHONPATH=tests/hastub`, BLAS pinned to 1 thread.
Cells (`check_scopes.py --seat D6-s2`): D6.M1+M2+M3 over `docs/{architecture,automations,configuration,
dashboard-card,ecl110,how-it-works,setup}.md` and `docs/setup/*.png`. README.md is D6-s1's and was not measured.

## Method

Claims were extracted per document and each group checked by an executed harness that drives the
production symbol the claim is about (never a re-derived formula). Every harness is under
`tools/audit/round9/D6/s2/`, runs from the export root with the single command in its header, prints
`RESULT` lines, and carries a `--perturb*` arm that moves its count. All numbers are counts or
ratios (contention-immune); no wall/CPU/RSS number is claimed.

| harness | what it checks | symbol driven |
|---|---|---|
| `config_tables.py` | every settings-table row (Setting/Default/Range) in the seat's docs: default, min, max, step against the rendered schema | `config_flow` initial + options flows via `tests/golden.py:capture_config_flow` (seeded arm included) |
| `flow_census.py` | the initial-setup path, the weather page's submit, the entity census and every "N entities"/per-domain count, every `sensor.heat_pump_optimizer_*` id in the docs | `HeatPumpOptimizerConfigFlow` driven step by step; six platforms' real `async_setup_entry` over a real coordinator |
| `services_claims.py` | configuration.md `## Services`: count, entry_id roster, per-service fields, returns column, every documented range probed at its boundaries, `set_mode` values, 21 assignable keys, selectable layouts | `services.async_register_services` through the integration's `async_setup` into `FakeServices` (registration kwargs spied) |
| `behaviour_claims.py` | ecl110.md ON threshold, 8-h weather bias, lag fraction, curve-bias rate and sign; automations.md economy floor, headroom formula/fallbacks, entity ids independent of the entry name | `optimizer.HeatPumpOptimizer._power_to_heat_pump_schedule`/`_power_to_displace_schedule`, `curve_learning.CurveLearner.record_day`, `away.lower_floor`, `coordinator._power_headroom`, platform setup |
| `architecture_claims.py` | module count, HA-import roster (AST), in-function toucher, module-map completeness, binary_sensor/button/switch rosters, ring size, boost duration, hacs floor | AST of the package; platform setup; `boost.BoostState.set` |
| `setup_claims.py` | images, screen-2 groups, quick-setup defaults, 500 L / 35 L, hot-water-off, quick vs wizard physics, seven sliders, pre-fill offer default, 23 pages, menu position | `capture_config_flow`, `quick_setup.derive`, `config_flow._derive_preset` |
| `howitworks_claims.py` | sample: horizon/grid, interval, multi-start count, defaults, DHW activation rule, three learner bounds | `optimizer._multi_start_minimize` (wrapped) in a real solve via `tests/stress.py:build_case`; `ThermalParameters.from_config` |
| `card_config.mjs` | dashboard-card.md configuration options: defaults, the eight series keys, 1–168 hours bound, type refusals | the card's `setConfig`/`parseConfig` via `tests/card_rig.mjs` |
| `links.py` | 73 local links/anchors and 5 external links (HEAD, then GET) | the docs |

## Numbers (D6.M3)

- Claims checked by an executed harness: **497** (263 table rows + 17 flow/census + 59 services + 14 behaviour + 12 architecture + 22 setup + 11 how-it-works + 21 card + 78 links).
- False: **1** (curve bias rate). Stale: **4** (74-entity count; "saving this page creates the entry"; two starting points; simulate_plan field list). Unverifiable: **2** external links (sandbox egress refused) plus the measurement-only figures listed under non-findings.
- Table rows: 247 matched to a rendered field, 233 agree on every parsed column, 0 disagree, 14 matched rows carry no parseable number (read off the harness output: all agree), 16 unmatched (10 are the card's YAML table, checked by `card_config.mjs`; 6 are composite/paraphrased rows).

## Findings

**D6-s2-01 (low, I5) — configuration.md:196 says "All 74 entities"; the platforms create 75.**
`flow_census.py`: `entities_total=75`, `configuration_md_count_delta=1`; architecture.md:37's 75 and its per-domain split (59/6/4/4/1/1) all agree. Perturbation `--perturb-count` (skip the datetime platform) → delta 0. `tests/entities.py` pins the README's counts only, which is how this copy drifted.

**D6-s2-02 (low, I5) — configuration.md "Saving this page creates the entry" (weather sensitivity, :196) and the setup flowchart are stale.**
`flow_census.py`: submitting the weather page returns `form:setup_overview` (`weather_submit_creates_entry=0`); the real path is user → user_sensors → finish_setup menu → temperature → building menu → building_describe → building_extras → dhw → weather_sensitivity → setup_overview → entry (`wizard_steps=11`). The flowchart (:24–38) has neither the finish-setup menu nor the overview. `--perturb` (weather submit creates the entry) → 1 and 10.

**D6-s2-03 (low, I5) — "at most 0.5 K per week" for the learned heat-curve bias is false: 0.6 K in a 7-day window.**
`behaviour_claims.py` drives `CurveLearner.record_day` over 70 comfortable days: steps of 0.2 K every 3 days, `curve_bias_max_7day_drop_k=0.600`. The cap in `_step_down` limits each step against the last step only (0.5·days/7), so three steps fit in any 7-day window. Seams: ecl110.md:31, configuration.md:767, how-it-works.md:1152 (and README.md:44 → D6-s1; strings.json:1333 → D4-s2). `--perturb-curve` (MAX_DOWN_PER_WEEK=0.3) → 0.457. Fix is either the docs (≈0.47 K/week on average, up to 0.6 K in 7 days) or a sliding-window cap in code.

**D6-s2-04 (low, I5) — how-it-works.md:108–113 says the space solve runs from two starting points and a third was not worth the runtime; it runs from four, each refined and polished.**
`howitworks_claims.py` wraps `_multi_start_minimize` in a real solve: `space_solve_start_candidates=4`, `space_solve_minimize_calls=8` (SolverWork). In production a fifth candidate (the previous plan, `_warm_start_starts`) joins after the first cycle (read, not measured). `--perturb-starts` (truncate to two) → 2 and 4.

**D6-s2-05 (low, I5) — configuration.md:951 lists simulate_plan's fields and omits the five wood fields.**
`services_claims.py`: the prose list after "Fields, all optional:" names 11; the registered schema has 16 (`wood_slots`, `wood_type`, `wood_packing`, `wood_price_sek_m3`, `wood_furnace_efficiency` missing). The table row's "16" is right. Perturbation (generic) raises the false count 1 → 5.

## Non-findings (held)

- Every settings table in configuration.md and ecl110.md: 233/233 parsed rows agree on default, range and step (`config_tables.py`).
- 23 option pages, 8 on the first menu, 15 behind Advanced; Quick setup last on the first menu.
- 12 services; 7 take `entry_id`; the five that do not are the five named; all 12 field lists and Returns cells; 28 `set_thermal_parameters` fields; 25 documented ranges probed at both ends; `set_mode` values; 21 assignable keys; 4 selectable layouts (`services_claims.py`).
- ECL110: ON threshold `max(0.1, ½·min power)` at three minimum powers; weather bias over exactly 32 steps = 8 h; lag fraction 0.165 vs dt/τ 0.167; curve bias range [−4, 0]. Economy floor 17.5 from 19 and 15.0 from 16. Headroom: fuse-only, tariff-only-no-peak (0.0 kW, named source), nothing → unavailable, clamp at 0. Entity ids identical under two entry names (75 of 75).
- architecture.md: 66 modules, 23 module-level HA importers (roster exact), `inputs` the only in-function toucher, 42 free, module map complete, platform rosters, 8 snapshots, 2-hour boost, floor 2025.2.0.
- setup.md: 22/22 (images present, three groups, five defaults, 500/35 L, identical quick/wizard physics, seven sliders, pre-fill offer off).
- dashboard-card.md configuration options: 21/21.
- how-it-works.md sample: 24 h × 15 min, 30-min interval, zone/single-zone defaults, DHW activates on any one of the three inputs and not on none; COP [0.5, 1.6], capacity ≥ 60 %, aperture [0.3, 2.0] (constant reads, spot depth).
- Six entity ids named in the docs all exist.
- Links: 73 local links resolve except `how-it-works.md:1317 → backlog.md`, which is an export artefact (the export omits `docs/backlog.md` by design; the file exists at the baseline, checked by existence only). Blueprint URLs return < 400; github.com/tvofi/tuya_heat_pump and developer.tibber.com were unreachable from the sandbox (unverifiable).
- Unverifiable by design: measurement-only figures (how-it-works.md "2.2 %", "0.2 %", "2.6–4.7 kWh", the comfort-weight table), setup.md "the original eleven-page wizard" (historical), the content of the eight PNG renders.

## Could not finish

- D6.M1/M2 on how-it-works.md: 11 claims sampled out of ~92 numeric lines; the thermal-model, hot-water, tariff, wood, away and learning sections' behaviour sentences are unchecked.
- D6.M1/M2 on dashboard-card.md: only the configuration section; chart, headline, savings, advisor, setup page, keyboard and installation prose unchecked.
- ecl110.md fixed-mode displaces (+4/max/min), the peak-guard −2 °C nudge and the sensors' enabled/disabled defaults were read in code, not executed.

## Leads (not measured)

- D5-s1 · docs/configuration.md:181–187: a paragraph splits the setup hot-water table, so the three anti-legionella rows (185–187) follow a paragraph with no header row and render as literal pipe text, not table rows. (Their values were checked and hold: on, 60 °C 55–70, 7 days 1–30.)
- D6-s1 · README.md:44: the same "at most 0.5 K per week" claim as D6-s2-03.
- D4-s2 · strings.json:1333 (`curve_learning_enabled` description): "at most half a degree per week", same as D6-s2-03.
- unknown · tests/entities.py: the doc-count pins cover README.md only; configuration.md:196's count has no pin.

## Exposure

Opened `docs/` files within the cells only. Did not open `docs/HANDOVER.md`, plans, `docs/audit-*`, or any `tools/audit/round*` evidence. `tools/audit/bugclasses.json` (read for `class_guess`) lists earlier-round instance ids; none were followed. `RELEASE_NOTES.md` was read at v6.6.5 to check setup.md's version claim. `docs/backlog.md` was checked for existence at the baseline via `git cat-file -e`, not read.
