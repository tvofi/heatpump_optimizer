# Round 2 D10 — tier table (baseline b39fc6f, 2026-09-02)

Statuses: done / todo / exempt / tracked. Evidence commands live in A/REPORT.md, B/REPORT.md, C/REPORT.md and the harnesses beside them. "A:"/"B:"/"C:" prefix = finder lane.

## Bronze (20)

| rule | status | number |
|---|---|---|
| action-setup | done | A: 11 service sites, 11 in async_setup chain, 0 elsewhere |
| appropriate-polling | done | A+B: update_interval 1800 s default, UI bounds 10–120 min (900 s when configured 15) |
| brands | done | B: brand/icon.png + brand/logo.png 256×256 (98 834 B), repo icon.png 512×512, HACS Validate green at b39fc6f (adapted check: custom integration cannot join home-assistant/brands) |
| common-modules | done | A: 1 DataUpdateCoordinator in coordinator.py; per-platform base entities 2/1/1/0/0 |
| config-flow | done | A: 26 flow steps; options stored in entry.options; data_description helper text 237/238 fields via strings.json (sub-check candidate D10-19 refuted 3–0, judge-confirmed; residue nit: tibber_token on reauth_confirm, 1/238) |
| config-flow-test-coverage | tracked #194 | not re-measured this pass |
| dependency-transparency | done | C: 12/12 sub-checks (numpy BSD-3 24 workflows; scipy BSD 17; threadpoolctl BSD-3 2; PyPI↔tag mapped for floor+latest) |
| docs-actions | done | C: 11/11 service actions documented |
| docs-triggers | done (vacuous) | C: 0 triggers provided by the integration |
| docs-conditions | done (vacuous) | C: 0 conditions provided |
| docs-high-level-description | done | C: README.md:28 |
| docs-installation-instructions | done | C: 5 sections (README:150/152/160, dashboard-card.md:378/398) |
| docs-removal-instructions | done | C: README.md:167 incl. .storage leftovers + Lovelace resource |
| entity-event-setup | done | A: 0 entity-layer subscription sites; 3 coordinator sites with async_on_remove cleanup (coordinator.py:5019–5024) |
| entity-unique-id | done | A: 65/65 ids re-derived statically, 0 collisions (perturbation proven 0→1) |
| has-entity-name | done | A: 65/65 |
| runtime-data | done | A: 1 typed ConfigEntry alias; 11 runtime_data reads; 0 hass.data[DOMAIN] |
| test-before-configure | done | B: invalid_tibber_token=1, cannot_connect=1 (real probe driven through config_flow.py:988 via fake session) |
| test-before-setup | done | A: first-refresh path runs Tibber/weather fetch before setup completes; UpdateFailed→ConfigEntryNotReady both paths; 1 bounded except |
| unique-config-entry | done | B: duplicate submission aborted `already_configured` (1); null control: distinct entry proceeds (1) |

## Silver (10)

| rule | status | number |
|---|---|---|
| action-exceptions | done | A: 13 raise sites, 0 silent swallows in handlers |
| config-entry-unloading | done | B: unload_leak=0; super_shutdown=1; platforms_forwarded=5; handover popped on reload |
| docs-configuration-parameters | done | C: 139/139 persisted fields (95 by key + 44 by setting-table label alias) |
| docs-installation-parameters | done | C: 64/64 setup-flow fields |
| entity-unavailable | done | B: 55/55 sensors unavailable after failed update; 0 stale publishers after key removal |
| integration-owner | done | A+C: codeowners=1 (@tvofi), account HTTP 200 |
| **log-when-unavailable** | **todo** | B: **6 ERROR records over 5 failed polls (rule: 1 per transition); outage latch counts 2 cycles/poll → "recovered after 10 cycle(s)" after 5 polls** → D10-16 |
| parallel-updates | done | A: sensor=0, binary_sensor=0 (coordinator read-only), button=1, climate=1, switch=1 |
| reauthentication-flow | done | B: reauth started once after two 401s; confirm updates entry; 2 steps present (trigger via entry.async_start_reauth, contextvar-inferred entry on 2024.6.0) |
| test-coverage | tracked #195 | not re-measured this pass |

## Gold (21)

| rule | status | number |
|---|---|---|
| devices | done | A: 1 DeviceInfo with identifiers+manufacturer+model+sw_version |
| diagnostics | done | B: not a platform (0); payload keys=4; token_leak=0; redaction 1/1 |
| discovery | exempt | A: 0 discovery-mechanism imports; cloud API + user-picked entities |
| discovery-update-info | exempt | A: same basis; no network addresses to update |
| docs-data-update | done | C: 3 sections (30-minute cadence documented, how-it-works.md:47) |
| **docs-examples** | **todo** | C: **0 automation examples in README + 8 shipped docs; services tabled 11/11 but no worked YAML** → D10-18 |
| docs-known-limitations | done | C: 2 sections + 6 caveat statements |
| docs-supported-devices | done | C: interfaces (switch / ECL110 MQTT / frequency entity) documented across 6 files |
| docs-supported-functions | done | C: entity delta 0 (65 actual = 65 documented); PLATFORMS 5/5 |
| docs-troubleshooting | done | C: 1 section, 6 problem entries (README.md:601) |
| docs-use-cases | done | C: 9 narratives (README:76–134) + Quick start |
| dynamic-devices | exempt | A: 0 device-registry create sites; 1 static DeviceInfo |
| entity-category | done | A: 17/65 categorized; internal signals covered |
| entity-device-class | done | A: 29/55 with device class; 0 applicable-but-missing |
| entity-disabled-by-default | done | A: 6/65 disabled by default |
| entity-translations | done | A: 0 uncovered (64 keyed + 1 device-named); en/sv agree |
| **exception-translations** | **todo** | A: **13/13 raise sites untranslated; 0 `exceptions` sections in strings.json/en.json** → D10-17 |
| icon-translations | tracked #189 | not re-measured this pass |
| reconfiguration-flow | tracked #196 | not re-measured this pass |
| repair-issues | done | A: 13 issue sites, all severity+translation_key, 0 missing keys |
| stale-devices | exempt | A: 0 async_remove_config_entry_device; device lifetime = entry lifetime |

## Platinum (3)

| rule | status | number |
|---|---|---|
| async-dependency | done | A: 0 blocking calls in async defs; 5 executor sites; sync solve dispatched via executor |
| inject-websession | done | A: 0 ad-hoc aiohttp.ClientSession; 3 async_get_clientsession sites |
| strict-typing | tracked #197 | not re-measured this pass |

## Tally (post-panel, judge-confirmed)

44 done (incl. 2 vacuous) · 3 todo → verified findings D10-16/17/18 · 4 exempt · 5 tracked · 54 total
1 candidate refuted (D10-19, 3–0; kill re-measured by judge).
