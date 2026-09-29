# Round 9 · D5 · seat D5-s1 — docs structure, flow and content (README.md, docs/**)

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, export `/home/claude/audit-r9-baseline`,
box B1. Cells: D5.M1, D5.M2, D5.M3 over `README.md` and the resolved `docs/**` set
(architecture, automations, configuration, dashboard-card, ecl110, how-it-works, setup, and
`docs/setup/*.png`). Every number below is a count (contention-immune); none is provisional.

Node harnesses need markdown-it 14.1.0 in a temp prefix:
`T=$(mktemp -d); npm install --prefix "$T" markdown-it@14.1.0 >/dev/null 2>&1; NODE_PATH=$T/node_modules node <harness>`.
Python harnesses: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python <harness>`.
Each takes `--perturb` and states the expected move in its header.

## Method

- M1 reader paths: walked (1) a HACS install to a first plan (README → Installation → Quick
  start → setup.md / configuration.md), (2) configuring two-tank storage, ECL110 and the
  capacity tariff (README → configuration.md / setup.md / ecl110.md / how-it-works.md),
  (3) a developer running the tests (README / architecture.md → tests/README.md).
  Contradictions found by reading were then measured against the production seam that
  decides the fact (the real ConfigFlow, the platforms' async_setup_entry, quick_setup.derive
  → ThermalParameters, the registered service schemas, translations/en.json).
- M2 structure: heading depth/order/duplicates (md_headings.py), GFM rendering of every
  table (md_tables.mjs, markdown-it token stream), internal link + anchor check
  (md_links.mjs, GitHub slug rule), paragraph hashing README vs docs (md_dupes.mjs), orphaned
  docs/images (grep, below), stale version numbers (card_version_doc.py, grep).
- M3 content: every `code` identifier the docs name resolved against the package AST
  (doc_symbols.py); mechanism paragraphs spot-checked against their code path
  (setup flow, quick setup, stamp/CARD_VERSION, services, two-tank gating, module map).

## Findings

| id | step | sev | title | harness | value | perturbation → |
|---|---|---|---|---|---|---|
| D5-s1-01 | M1 | medium | configuration.md "Initial setup" documents the pre-v6.6.5 flow | setup_section.py (+ entity_counts.py) | stale_facts=4 (+ 1 wrong entity count) | finish_setup→temperature: 1 |
| D5-s1-02 | M3 | medium | setup.md Quick setup promises buffer storage and two-tank physics the answers cannot build | quick_setup_promise.py | unhonoured_promises=2 | derive + throttling valve: 0 |
| D5-s1-03 | M3 | low | dashboard-card.md upgrade troubleshooting describes a card version the stamp no longer keeps | card_version_doc.py | card_tracks_integration_share=1.00 | doc model: 0.00 |
| D5-s1-04 | M2 | low | configuration.md has 9 lines a GFM renderer puts in the wrong block | md_tables.mjs | misrendered_lines=9 | repair: 0 |
| D5-s1-05 | M1 | low | docs name 5 fields by names the options forms do not show | field_labels.py | unfindable_field_refs=5 | relabel: 4 |
| D5-s1-06 | M1 | low | simulate_plan's 5 wood fields are accepted but documented nowhere | service_fields.py | undocumented_fields=5 | strip wood keys: 0 |

### D5-s1-01 — configuration.md "Initial setup" documents the pre-v6.6.5 flow
The section's flowchart runs Basics → Temperatures with no finish menu; the real flow
(`HeatPumpOptimizerConfigFlow.async_step_user` → `async_step_user_sensors`) returns the
`finish_setup` menu with 3 entries (Quick setup (recommended) / Continue setup / Finish setup
now), none named in the section. The section says "Only two answers are genuinely required:
a Tibber API token and a weather entity" and marks the token "(**required**)"; the real first
screen accepts `price_source=entity` with no token. It closes "All 74 entities appear"; the
six platforms construct 75 (README and architecture.md say 75). README and setup.md describe
the current flow, so the reader meets a contradiction at the first step.
`setup_section.py`: stale_facts=4; `entity_counts.py`: constructed=75, disagreeing_claims=1.

### D5-s1-02 — Quick setup promises storage the answers cannot build
setup.md: Buffer tank "yes" … "On stores cheap heat and releases it during expensive hours";
the wood probes "are what actually switch the two-tank physics on". `quick_setup.derive`
never writes `mixing_valve_mode`, and both `ThermalParameters.buffer_is_store` and
`two_tank_modelled` (layout `two_tank_4way`) require a throttling valve. With every toggle
yes and both probes: buffer 500 L, two_zone True, wood_tank_configured True, layout
`no_valve`, buffer_is_store False, two_tank_modelled False. Null arm (same answers plus a
valve on Heating system and heat storage): 0 unhonoured. setup.md never names the valve.

### D5-s1-03 — stale card-version troubleshooting
dashboard-card.md "If an upgrade seems to change nothing": the banner version "moves only
when the card file changes, so it is often lower than the integration version … Compare it
against the card version named in the release notes … not against the integration version",
example banner `v6.6.8`. Since #265 `stamp.py:main` calls `rewrite_card_version(card, nxt)` on
every stamp; CARD_VERSION = VERSION = 6.7.1 at baseline and tracks it on 5/5 simulated stamps.
The advice sends the reader to look for a card version the notes no longer carry separately.

### D5-s1-04 — tables that render wrong
configuration.md:181-187: a paragraph inserted inside the setup "4 · Hot water" table leaves
its last three rows (anti-legionella on/temperature/interval) with no header, so they render
as a paragraph of raw pipes. configuration.md:633-638: prose directly under the Heating
system table with no blank line becomes six table rows (GFM spec: a table ends only at a
blank line or another block). All other tables in the 8 files render intact.

### D5-s1-05 — field names the UI does not show
Two-zone model page rows "Inter-zone transfer" (UI: "Inter-zone heat transfer (kW/°C)") and
"Radiator power fraction" (UI: "Share of heat going to radiators"); configuration.md:511 and
:514 "*Floor return temperature*" (UI: "Floor heating return temperature sensor");
how-it-works.md:673 "*Solar forecast source*" (UI: "Solar irradiance source"). All other
page/field references resolve (24 menu pages; every options field label appears in
configuration.md).

### D5-s1-06 — simulate_plan wood fields undocumented
The registered SERVICE_SCHEMA_SIMULATE_PLAN accepts 16 fields; configuration.md's table says
"16 optional comfort and wood fields" but its paragraph ("Fields, all optional:") names 11 and
no doc names `wood_slots`, `wood_type`, `wood_packing`, `wood_price_sek_m3`,
`wood_furnace_efficiency`. Every other service's fields (57 of 62) are named.

## Reader-path dead ends (M1 numbers)

- Reader 1, HACS → first plan: **3** — D5-s1-01's contradiction (menu, token) and its entity
  count; README "Add this repository to HACS as a custom repository" gives neither the URL
  nor the HACS category (Integration) — the fact is nowhere in README/setup.md (reading only,
  no harness; not returned as a finding).
- Reader 2, feature configuration: **4** — two-tank/buffer storage via Quick setup
  (D5-s1-02); field names not on the form (D5-s1-05, counted once); README Troubleshooting
  tells the reader to change `inter_zone_heat_transfer`, `window_area`,
  `solar_heat_gain_coefficient`, `dhw_min_temperature`, `dhw_setpoint`,
  `dhw_daily_consumption` by config key while the forms show labels only and no doc maps key
  to label outside the set_thermal_parameters list (reading only); ECL110 sensors are said to
  be enabled "on an install whose topics were configured at setup" although setup has not
  asked for topics since v4.1.0 (lead for D6). Capacity tariff path: 0.
- Reader 3, developer running tests: **0** inside these cells; README and architecture.md
  both hand off to tests/README.md, which is outside D5-s1's cells.

## Non-findings

- Broken internal links/anchors: 0 of 119 relative links (38 anchored); 4 targets stripped
  by the export not judged; 20 external links not fetched (`md_links.mjs`; perturb → 2).
- Duplicated paragraphs README vs docs: 0 exact duplicates of 677 blocks, 0 near-duplicate
  fences at line-Jaccard ≥ 0.6 (`md_dupes.mjs`; perturb → 1). A 4-gram shingle pass found
  one pair ≥ 0.3: README's mermaid flowchart vs architecture.md's (0.65), deliberate.
- Heading structure: 174 headings, 0 level skips, 0 duplicate texts, one H1 per file
  (`md_headings.py`; perturb → 1).
- Identifiers docs name in code spans: 282 checked, 1 unresolved — `direct_radiation`,
  named as what the code deliberately does not request (`doc_symbols.py`; perturb → 3).
- Orphans: every in-scope doc is linked from README or another doc (2–6 inbound each);
  every image under docs/img and docs/setup is referenced (grep loop in this report's method).
- architecture.md module map: lists all 66 modules; 23 import homeassistant at module level,
  as stated (grep).
- Options pages: all 23 page names in README/configuration.md equal the en.json menu labels;
  every options field label appears in configuration.md.
- Versions: VERSION, manifest and CARD_VERSION all 6.7.1; the only stale version literal in
  scope is dashboard-card.md's `v6.6.8` banner (inside D5-s1-03). Other version mentions are
  "since vX" history.

## Leads (not measured here)

- D4-s2 · translations/en.json config.step.quick_setup.data_description.buffer_tank /
  wood_buffer_tank: the same storage/two-tank promise as D5-s1-02, on the form itself.
- D6-s1 · README.md "Nineteen entities (eighteen sensors and the wood binary sensor) are
  disabled by default" while README:600 says DHW Boost is also disabled by default without
  hot water; the disabled list sits under Sensors but names a binary sensor.
- D6-s2 · docs/configuration.md simulate_plan table "16 … fields" vs the 11 in its prose
  (see D5-s1-06); docs/setup.md "original eleven-page wizard" and "Quick setup arrived in
  v6.6.5" unverified against RELEASE_NOTES.
- D6-s2 · docs/ecl110.md "Sensors": enabled "on an install whose topics were configured at
  setup" — setup has not offered the topics since v4.1.0.

## Unfinished

- M3: how-it-works.md lines 700–1317 (tariffs, wood, learning loops, tests section) were
  covered only by the identifier check and link/table/heading checks, not paragraph-by-
  paragraph spot-checks against their code paths.

## Exposure

Read in full: README.md and the seven in-scope docs. Incidental: a grep over docs/*.md printed
rows of docs/plan-2026-09-open-issues.md and one line of docs/HANDOVER.md (issue/PR numbers);
two passages of RELEASE_NOTES.md (#265 CARD_VERSION, the version-pinning note) — it is present
in this export, so release-history claims were checkable; production comments cite earlier
issue ids (#265, #1227, #1335, #942 in README). None was used as a list to re-find.
