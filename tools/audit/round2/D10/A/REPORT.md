# D10-A — Integration Quality-Scale Rules (round 2, auditor D10-A)

Baseline SHA `b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9`, export
`audit-r2-D10-export`, fresh eyes (no `.git`, no earlier audit records read,
no GitHub access). Assigned: 25 quality-scale rules + integration-owner
(26 rows). One finding returned.

## Method

One parametrized AST harness, `tools/audit/round2/D10/A/ast_checks.py`,
walks every `custom_components/heatpump_optimizer/*.py` (52 modules) with
`ast`, plus `manifest.json`, `strings.json`, `translations/en.json`,
`translations/sv.json`. It prints 97 `RESULT <rule>.<name>=<value>` lines
and a file:line evidence block. Run:

```
cd /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D10-export && \
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 \
/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
tools/audit/round2/D10/A/ast_checks.py
```

(full output of the recorded run is committed alongside as
`run_output_baseline.txt`). All numbers are counts —
contention-immune. `HPO_D10A_INT=<dir>` re-points the harness at a perturbed
copy of the integration for judge dry-runs; two perturbation dry-runs were
executed on `/tmp` copies (never in the export).

Key derivation technique (entity rules): the harness reads each platform's
`async_setup_entry` roster, then each entity class's
`super().__init__(coordinator, entry, <key>, <translation_key>)` literals
(or, for `climate`/`switch`, the direct `self._attr_unique_id =
f"{entry.entry_id}_<suffix>"` in `__init__`). All 65 entity unique_ids were
re-derived from scratch this way — nothing was carried over from round 1.

Instrument sanity (both executed on `/tmp` copies):
- collision detector: changing `DHWScheduleSensor`'s key `"dhw_schedule"` to
  `"schedule"` (colliding with `ScheduleSensor`) moves
  `entity-unique-id.collisions` 0 → 1.
- translation-kwargs counter: adding `translation_key=` to one raise site
  moves `exception-translations.raises_translatable` 0 → 1.

## Tier table

| rule | tier | status | number |
|---|---|---|---|
| action-setup | bronze | done (pass) | 11 register sites, 11 in `async_setup` chain, 0 elsewhere |
| appropriate-polling | bronze | done (pass) | default 30 min, UI bounds 10–120 min |
| common-modules | bronze | done (pass) | 1 DataUpdateCoordinator in coordinator.py; per-platform bases 2/1/1/0/0 |
| config-flow | bronze | done (pass) | 26 flow steps; options in `entry.options`; `data_description`=0 (noted) |
| entity-event-setup | bronze | done (pass) | 0 subscription sites in entity files; 3 in coordinator helpers w/ cleanup |
| entity-unique-id | bronze | done (pass) | 65/65 derived, 0 collisions |
| has-entity-name | bronze | done (pass) | 65/65 |
| runtime-data | bronze | done (pass) | 1 typed alias; 11 `.runtime_data` reads; 0 `hass.data[DOMAIN]` |
| test-before-setup | bronze | done (pass) | 1 first-refresh call; UpdateFailed on failure; 1 bounded except |
| action-exceptions | silver | done (pass) | 13 raises, 0 silent swallows in handlers |
| parallel-updates | silver | done (pass) | sensor=0, binary_sensor=0, button=1, climate=1, switch=1 |
| integration-owner | silver | done (pass) | codeowners = 1 (`@tvofi`) |
| devices | gold | done (pass) | 1 DeviceInfo, identifiers+manufacturer+model+sw_version |
| entity-category | gold | done (pass) | 17/65 categorized; internal signals all categorized |
| entity-device-class | gold | done (pass) | 29/55 sensors with device class; 0 with an applicable one missing |
| entity-disabled-by-default | gold | done (pass) | 6/65 disabled by default |
| entity-translations | gold | done (pass) | 0 uncovered (64 keyed + 1 device-named exempt) |
| exception-translations | gold | **fail** | 13 raise sites, 0 translatable, 0 `exceptions` sections |
| repair-issues | gold | done (pass) | 13 sites, 13 with severity + translation_key, 0 missing keys |
| discovery | gold | exempt | 0 discovery-mechanism imports |
| discovery-update-info | gold | exempt | same basis; no network addresses to update |
| dynamic-devices | gold | exempt | 0 device-registry create sites |
| stale-devices | gold | exempt | 0 `async_remove_config_entry_device`; static device lifetime |
| async-dependency | platinum | done (pass) | 0 blocking calls in async defs; 5 executor sites |
| inject-websession | platinum | done (pass) | 0 ad-hoc `aiohttp.ClientSession(`; 3 `async_get_clientsession` |

## Finding

### D10-51 — Every service/config exception message is untranslated (gold rule exception-translations fails)

**Claim** (one sentence, falsifiable): all 13 raise sites of
`HomeAssistantError`/`ServiceValidationError` in the integration construct
their message as an English f-string with no `translation_key`/
`translation_domain`, and `strings.json`/`translations/en.json` carry no
`exceptions` section (0 keys), so a user running a Swedish UI gets
English-only service errors.

**Executed number**: `exception-translations.raises_translatable=0` of
`exception-translations.raise_sites_total=13`;
`exception-translations.exceptions_section_strings.json=0`;
`exception-translations.exceptions_section_en.json=0`.

Sites (from the harness evidence block): `__init__.py:413,417,427`
(`_loaded_entries`), `__init__.py:558,605,611,656,722,765,788,832,846`
(service handlers in `_async_register_services`),
`coordinator.py:1370` (`async_set_target_temperature`). All 13 are
`ServiceValidationError`; 0 carry translation kwargs.

**Instrumented symbol**: `__init__:_async_register_services` (raise sites
413–846; plus `coordinator:HeatPumpOptimizerCoordinator.async_set_target_temperature`).

**Perturbation** (executed on `/tmp/d10a-perturb/heatpump_optimizer`, a copy
of the integration): add `translation_key="no_entries",
translation_domain=DOMAIN` to the raise at `__init__.py:427` →
`exception-translations.raises_translatable` must move 0 → 1 (up). Observed
value on the perturbed copy: **1**.

**Metric definition**: count of raise sites of
`HomeAssistantError`/`ServiceValidationError` whose `Call` node carries a
`translation_key` or `translation_domain` keyword vs total such raise sites,
plus the key count of the `exceptions` section in `strings.json` and
`translations/en.json`.

**Severity**: low (hygiene). The messages are accurate and actionable; the
defect is language only. The integration ships `sv.json` for everything
else (entity names, issues, config flow), so the gap is visible only to
non-English users at error time.

**Stop-rule class**: hygiene.

**Files**: `custom_components/heatpump_optimizer/__init__.py`,
`custom_components/heatpump_optimizer/coordinator.py`,
`custom_components/heatpump_optimizer/strings.json`,
`custom_components/heatpump_optimizer/translations/en.json`,
`custom_components/heatpump_optimizer/translations/sv.json`.

**Proposed fix scope**: add an `exceptions` section to `strings.json` and
both translation files and convert the 13 raise sites to
`translation_domain=DOMAIN, translation_key=..., translation_placeholders=...`
(one key per distinct message; 13 keys, several shareable).

## Non-findings (each held, with the executed number)

Claim + command + value; command is the harness invocation above
(`ast_checks.py`), whose `RESULT` lines are quoted. Full output:
`tools/audit/round2/D10/A/run_output_baseline.txt`.

1. **action-setup** — All service registrations live in `async_setup`'s
   call chain. `action-setup.register_sites=11`,
   `sites_in_async_setup_chain=11`, `sites_elsewhere=0`; all 11 enclosing
   `_async_register_services` (`__init__.py:895–962`), called from
   `async_setup` (`__init__.py:393`).
2. **appropriate-polling** — Polling interval is user-bounded and sane for
   cloud polling. `default_interval_minutes=30`, `ui_bounds_minutes=10-120`
   (config_flow.py:1230–1234, `_number(10, 120, 5, "min")`), 1
   `update_interval` site (coordinator.py:652–660), `scan_interval_defs=0`.
3. **common-modules** — The DataUpdateCoordinator lives in `coordinator.py`
   (`coordinator_py_dataupdatecoordinator=1`); no `entity.py` exists
   (`entity_py_exists=0`) but each platform file holds its own base
   (`sensor=2`: `HeatPumpOptimizerSensorBase`, `_PlanSensorBase`;
   `binary_sensor=1`; `button=1`; climate and switch entities are
   standalone), `platform_files_importing_shared_entity_base=0`. Each base
   is platform-specific (different Entity ABC, different `entity_id`
   prefix); there is no cross-platform copy-paste of substance, so the
   rule's intent holds under the per-platform-base structure HA itself
   recommends.
4. **config-flow** — UI setup exists with stepped flows and an options flow
   that writes `options`, not `data`: `flow_step_functions=26`;
   `options_writes=1` (`config_flow.py:1620`, `async_update_entry(...,
   options={...})`; the OptionsFlow `async_create_entry(data={**options,
   **user_input})` at 1593 routes to options by HA contract);
   `create_entry_data_kwarg_sites=2`. `data_description_kwargs=0` across
   all 26 steps — recorded as a quality-scale observation, not a failure of
   the bronze rule (the integration ships per-field labels in
   `selector`/`strings.json` step descriptions instead).
5. **entity-event-setup** — No entity subscribes to anything outside the
   coordinator pattern: `subscription_sites_entity_platform_files=0`;
   `subscriptions_in_async_added_to_hass=0`,
   `subscriptions_in_init_or_other=0` for entities. The 3 state/event
   subscriptions in the integration live in coordinator setup helpers
   (`coordinator.py:7760` `_async_setup_defrost_watch`, `7807`
   `_async_setup_peak_guard`, `1278` `_async_setup_ecl110_state_subscription`)
   and are torn down via stored unsub callables at `coordinator.py:5019–5024`.
6. **entity-unique-id** — Every entity sets a unique_id and none collide:
   `entity_classes_total=65`, `derived_unique_ids=65`
   (`dynamic_underivable=0`), `collisions=0`,
   `suffix_shared_across_platforms=0`;
   `per_platform=sensor=55,binary_sensor=4,button=4,climate=1,switch=1`.
   Ids are dynamic (`f"{entry.entry_id}_{key}"`) — the harness derived the
   per-entity `key` statically (see Method) and scanned those. Collision
   detector proven non-vacuous by the executed perturbation (0 → 1).
7. **has-entity-name** — `entities_total=65`, `with_has_entity_name_true=65`
   (set once in each platform base: sensor.py:190, binary_sensor.py:57,
   button.py:53, climate.py:78, switch.py:43), `exceptions=0`.
8. **runtime-data** — `typed_alias_sites=1`
   (`HeatPumpOptimizerConfigEntry = ConfigEntry[HeatPumpOptimizerCoordinator]`,
   coordinator.py:11003), `runtime_data_reads=11`,
   `hass_data_DOMAIN_reads=0`, `alias_name_occurrences=16` (signatures
   across `__init__`/platforms). The one `hass.data` key that exists
   (`_PLAN_HANDOVER_KEY`, `__init__.py:106`) is the documented one-reload
   plan handover, not entry runtime data.
9. **test-before-setup** — Setup validates it can fetch before finishing:
   `first_refresh_calls=1` (`async_config_entry_first_refresh`,
   `__init__.py:476`); both refresh paths raise `UpdateFailed` on fetch
   failure (`coordinator.py:4463` full path, `coordinator.py:4506` light
   path — the light path still runs the Tibber/weather/solar fetches),
   which HA converts to `ConfigEntryNotReady`;
   `updatefailed_raises_in_coordinator=3`;
   `except_handlers_in_setup_entry=1` — the bounded, logged version lookup
   (`__init__.py:457`), documented as cosmetic.
10. **action-exceptions** — Handlers raise on invalid usage and never
    swallow silently: `raise_sites_total=13` (12 in the service path, all
    `ServiceValidationError` with actionable messages — unknown entry,
    entry not loaded, bad mode, bad windows, bad topology),
    `silent_swallow_except_in_handlers=0`.
11. **parallel-updates** — Present in all five platform modules:
    `sensor=0`, `binary_sensor=0` (coordinator-driven, read-only),
    `button=1`, `climate=1`, `switch=1` (actuating platforms serialize).
12. **integration-owner** — `manifest_codeowners_count=1`,
    `first_codeowner=@tvofi` (manifest.json:7–9). Non-empty; GitHub-account
    verification is out of scope by brief (no GitHub access).
13. **devices** — One DeviceInfo for the entry's virtual device:
    `deviceinfo_sites=1` (coordinator.py:1328) with
    `identifiers/manufacturer/model/sw_version` all present
    (`sites_with_identifiers=1`, `_manufacturer=1`, `_model=1`,
    `_sw_version=1`); serial/hw/connections are not applicable to a
    cloud-bound virtual device.
14. **entity-category** — `with_entity_category=17` of 65; the internal
    signals are all covered (OptimizationStatus, Next/LastOptimization,
    Schedule, PredictiveInsight, both ECL110 displace sensors, InputHealth,
    Ventilation are `DIAGNOSTIC`; two buttons explicitly set `None` as
    user-facing actions). The 48 uncategorized are primary values (temps,
    costs, energy, plan sensors, the switch, the climate entity) — none is
    an internal signal left exposed.
15. **entity-device-class** — `sensors_with_device_class=29` of 55; of the
    26 without (full list in run_output_baseline.txt), each publishes
    money-rolling-prediction, percent, ratio, text or plan-payload values
    for which HA has no SensorDeviceClass, or values that HA's statistics
    rules would reject (MONETARY/ENERGY require `state_class TOTAL`; the
    horizon-money omission is documented at sensor.py:377–379, PVSurplus
    follows the same pattern to stay out of the Energy dashboard). 0
    sensors have an applicable-but-missing device class.
16. **entity-disabled-by-default** — `disabled_entities=6` of 65:
    ECL110Displace, ECL110EffectiveDisplace, ContractComparison,
    DHWHeavyDay, ValveTargetRecommendation, FrequencyAdvisor — exactly the
    niche/diagnostic tail.
17. **entity-translations** — `uncovered_entries=0` across `strings.json`,
    `en.json`, `sv.json`; `device_named_exempt=1` (the climate entity sets
    `_attr_name = None`, taking the device name — no key needed); sections
    carry `sensor=55`, `binary_sensor=4`, `button=4`, `switch=1` names.
18. **repair-issues** — `async_create_issue_sites=13`, all 13 with
    `severity` and `translation_key`, `issue_keys_missing_from_strings=0`
    (strings.json `issues` holds 14 keys: legionella family, pump mode,
    solve failures, grid fee, COP degradation, accuracy drift, freq
    watchdog). Every user-intervention condition found (unreachable
    disinfection setpoint, unreadable pump mode, solver failure streak,
    grid-fee sign/magnitude) raises a repair issue, not just a log line.
19. **async-dependency** — `blocking_calls_directly_in_async_defs=0`;
    `time_sleep_sites=1` sits in the sync `_optimize_with_dhw`
    (optimizer.py:4777, the documented GIL yield between L-BFGS-B starts),
    which runs via `hass.async_add_executor_job`
    (coordinator.py:4750); `executor_dispatch_sites=5`; `to_thread_sites=0`.
    All persistence goes through HA's async `Store.async_save`
    (e.g. coordinator.py:1495, 1516, and `_async_save_if_changed`'s
    `await store.async_save(payload)`), HTTP through aiohttp. Expected
    pattern met.
20. **inject-websession** — `adhoc_aiohttp_clientsession_constructions=0`;
    `async_get_clientsession_sites=3`: config_flow.py:347,
    coordinator.py:5409 (Tibber GQL), open_meteo.py:325. `sysid.py` performs
    no HTTP (it consumes coordinator snapshots).

### Exemption-basis records (not forced to pass/fail)

- **discovery** — exempt. `discovery_mechanism_imports=0`: no zeroconf,
  ssdp, dhcp, usb or bluetooth import anywhere in the integration; the
  integration binds to a cloud API (Tibber GraphQL + Open-Meteo) and to
  user-picked existing HA entities; nothing on the local network to
  discover. manifest `iot_class=cloud_polling`.
- **discovery-update-info** — exempt, same basis: no network addresses
  exist in device state to update.
- **dynamic-devices** — exempt. `device_registry_create_sites=0`; exactly
  one static `DeviceInfo` per config entry (coordinator.py:1328); the
  entity set is fixed at setup (rosters in each platform's
  `async_setup_entry`).
- **stale-devices** — exempt. `async_remove_config_entry_device_sites=0`;
  device lifetime equals config-entry lifetime (removed with the entry),
  so no stale-device handling is required. Note the integration *does*
  clean retired entity-registry entries on every setup
  (`_async_remove_retired_entities`, `__init__.py:360–379`).

## What I could not finish

- integration-owner's "matches a real GitHub account" half: GitHub access
  is forbidden by the brief; the check was reduced to codeowners non-empty
  (1, `@tvofi`).
- config-flow's data_description component: measured (0) and recorded; I
  did not promote it to a finding because the bronze rule's core (UI
  setup, options-in-options) holds and the gap is wording, not behaviour.

## Exposure

None. Read only `tools/audit/round2/D10/rules.json`, `tools/audit/README.md`,
`tools/audit/briefs/COMMON.md`, the integration source and its
manifest/strings/translations, and `tests/` file listings. No docs/audit
register, no GitHub, no earlier findings.
