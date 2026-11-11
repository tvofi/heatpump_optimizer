# Round 9, D10-s1: finder report (D10)

The box B1 thread rendered this file from the JSON report D10-s1 returned, which is stored verbatim in `tools/audit/round9/reports-B1.json`. The seat's own Write tool refused to create a report `.md` file. The JSON is the record, and this file adds nothing to it.

Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`

## Exposure

none. docs/ (README.md, docs/configuration.md, docs/setup*.md) was read only for the docs-* rules: headings, service names and option-topic keywords. No audit register, backlog or GitHub was read. The rule text was fetched from raw.githubusercontent.com/home-assistant/developers.home-assistant (rules/*.md and _includes/tiers.json) on 2026-09-26.

## Coverage

- **D10.M1** (deep): One executed check per Bronze (20) and Silver (10) rule. tools/audit/round9/D10/s1/rules_check.py drives async_setup, async_setup_entry, the six platform setups (75 entities), async_unload_entry and the Tibber fetch latch through tests/hastub, and uses AST or text for the structural rules. Three rules failed and each has its own harness with a perturbation and a null control: unique_id_drift.py (unique-config-entry), press_vs_service.py (action-exceptions), auth_failed.py (test-before-setup). config-flow-test-coverage and test-coverage are carried, not measured: the coverage measurement is D10.M3, seat D10-s2.
- **D10.M2** (deep): Tier table in the returned report text, and a draft tools/audit/round9/D10/s1/quality_scale.yaml for the Bronze and Silver rows. Status: 25 done, 2 exempt (docs-triggers, docs-conditions), 3 todo (unique-config-entry, test-before-setup, action-exceptions). No todo needs an HA API newer than hacs.json's floor 2025.2.0: ConfigEntryAuthFailed, HomeAssistantError and async_update_entry(unique_id=) predate it, and _abort_if_unique_id_mismatch shipped in 2024.11. The in-tree quality_scale.yaml marks all three todo rows done.

## Findings

### D10-s1-01: Entry unique id is not re-derived after reauth or an options edit, so the same plant can be set up twice

- step D10.M1, severity medium, class bug, class_guess P2, provisional None

**Claim.** A fresh setup that submits an entry's current identity answers is accepted as a new entry in 3 of 5 arms. The 3 arms are after reauth, after an options-page token change, and after an options-page indoor-sensor change. In the same 3 arms, a setup with the original answers (which no entry now holds) is refused as already_configured.

**Mechanism.** config_flow.entry_identity hashes the Tibber token and 13 entity slots into the unique id. _async_save_reconfigure re-stamps unique_id. async_step_reauth_confirm and the options 'entities' page (_save_or_menu/_save) write the same identity keys but never update entry.unique_id, so the duplicate guard compares against a stale id.

**Metric.** Arms out of 5 in which a fresh config flow submitting the entry's current effective identity answers is not aborted as already_configured.

**Instrumented symbol.** `heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow.async_step_user_sensors (duplicate guard), driven after config_flow:HeatPumpOptimizerConfigFlow.async_step_reauth_confirm and config_flow:HeatPumpOptimizerOptionsFlow.async_step_entities`

**Phenomenon property.** Every flow that writes an identity key (token, price entity or an _IDENTITY_ENTITY_KEYS slot) leaves entry.unique_id equal to the identity of the entry's effective config. Better: the id is keyed on an account or home identity that does not rotate with the credential (for example Tibber viewer.userId or home id), which would also let reauth refuse a different account (wrong_account).

**Seam rule.** `grep -n "async_update_entry\|_save(\|async_create_entry" custom_components/heatpump_optimizer/config_flow.py, keeping each write that can change CONF_TIBBER_TOKEN, CONF_PRICE_ENTITY or a key in _IDENTITY_ENTITY_KEYS`

**Proposed fix scope.** config_flow.py only: re-derive unique_id in async_step_reauth_confirm and in the options save path (or key the identity on a non-credential account id from validate_tibber_token), plus tests/config_flow_steps.py arms for reauth and options.

**Files.** custom_components/heatpump_optimizer/config_flow.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/unique_id_drift.py",
  "harness_path": "tools/audit/round9/D10/s1/unique_id_drift.py",
  "value": 3,
  "unit": "arms (dup_accepted; stale_refused also 3)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "audit box B1 (Linux container)",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; the metric is a count and immune to contention",
  "tolerance": "exact",
  "load1": 1.05,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--fix: wrap hass.config_entries.async_update_entry so every write re-stamps entry.unique_id = config_flow.entry_identity({**data, **options}). This is the one-line fix at each write seam.",
  "expected_direction": "to_zero",
  "observed_value": "dup_accepted 3 -> 0, stale_refused 3 -> 0; control_none and reconfigure arms 0 in both runs"
}
```

### D10-s1-02: Optimize-now button press returns normally when the solve did not run; the run_optimization action raises

- step D10.M1, severity medium, class bug, class_guess P2, provisional None

**Claim.** On the same coordinator state, handle_run_optimization raises HomeAssistantError but ForceOptimizationButton.async_press returns normally, in 2 of 3 input arms (stale prices / no_prices, price feed down). The prices-OK control arm counts 0.

**Mechanism.** async_press awaits coordinator.async_force_optimization, which awaits async_request_refresh. _async_update_data ignores async_run_optimization's reason code, and the coordinator refresh swallows UpdateFailed. So the #294 refusal that the service implements never reaches a platform action, which the action-exceptions rule covers explicitly.

**Metric.** Input arms in which the run_optimization service raises HomeAssistantError on a coordinator state while the Optimize-now button press on the same state returns without an exception.

**Instrumented symbol.** `heatpump_optimizer.button:ForceOptimizationButton.async_press vs heatpump_optimizer.services:handle_run_optimization; solve outcome observed via coordinator:HeatPumpOptimizerCoordinator.async_run_optimization`

**Phenomenon property.** Every platform action whose purpose is to cause a solve (or an analysis) surfaces a not-run outcome as HomeAssistantError or ServiceValidationError, exactly as the equivalent service action does.

**Seam rule.** `grep -n "async_press\|async_turn_on\|async_turn_off\|async_set_" custom_components/heatpump_optimizer/{button,switch,climate,datetime}.py, keeping entries whose only effect is to request a solve or analysis (named candidate, not counted: DiagnoseIntervalButton.async_press)`

**Proposed fix scope.** button.py ForceOptimizationButton.async_press, and optionally coordinator.async_force_optimization returning the reason code; plus the strings.json exceptions key (already present: run_optimization_no_prices / run_optimization_solve_failed).

**Files.** custom_components/heatpump_optimizer/button.py, custom_components/heatpump_optimizer/coordinator.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/press_vs_service.py",
  "harness_path": "tools/audit/round9/D10/s1/press_vs_service.py",
  "value": 2,
  "unit": "arms (silent_presses)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "audit box B1 (Linux container)",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; the metric is a count and immune to contention",
  "tolerance": "exact",
  "load1": 1.16,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--fix: replace ForceOptimizationButton.async_press in memory with 'reason = await self.coordinator.async_run_optimization(); raise HomeAssistantError if reason is not None'.",
  "expected_direction": "to_zero",
  "observed_value": "silent_presses 2 -> 0; prices_ok control 0 in both runs"
}
```

### D10-s1-03: Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed, never ConfigEntryAuthFailed

- step D10.M1, severity low, class bug, class_guess P11, provisional None

**Claim.** In 3 of 3 auth-refusal arms (setup 401, setup 403, steady-cycle 401), the exception the integration delivers is transient-class (ConfigEntryNotReady or UpdateFailed), not ConfigEntryAuthFailed. The integration has 0 ConfigEntryAuthFailed raise sites. The HTTP 500 and connection-error controls are correctly transient (2/2).

**Mechanism.** _fetch_tibber_prices calls _tibber_start_reauth on a 'reauth' verdict, then _tibber_fetch_failed raises UpdateFailed. The first refresh converts that to ConfigEntryNotReady, so HA retries setup and keeps polling Tibber with a token it knows is revoked, instead of stopping and marking the entry for reauthentication as test-before-setup requires. The stub has no ConfigEntryAuthFailed class and no auth arm in DataUpdateCoordinator._async_refresh, so no test can express the correct behaviour (P11).

**Metric.** Auth-refusal arms (HTTP 401/403) in which the exception escaping async_setup_entry or _fetch_tibber_prices is not ConfigEntryAuthFailed.

**Instrumented symbol.** `heatpump_optimizer:async_setup_entry and heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fetch_tibber_prices`

**Phenomenon property.** An authentication refusal from any credentialed fetch reaches Home Assistant as ConfigEntryAuthFailed, at setup and on steady cycles, and the update wrappers never re-wrap it as UpdateFailed. The test stub models ConfigEntryAuthFailed and upstream's auth arm.

**Seam rule.** `grep -n '"reauth"\|_tibber_start_reauth\|except Exception' custom_components/heatpump_optimizer/coordinator.py (the fetch, _async_update_data and _async_first_refresh_light), plus grep -n 'ConfigEntryAuthFailed' tests/hastub/homeassistant/exceptions.py tests/hastub/homeassistant/helpers/update_coordinator.py`

**Proposed fix scope.** coordinator.py: raise ConfigEntryAuthFailed on the reauth verdict and pass it through the two update wrappers. tests/hastub: add the exception and the upstream auth arm in _async_refresh and the first refresh.

**Files.** custom_components/heatpump_optimizer/coordinator.py, tests/hastub/homeassistant/exceptions.py, tests/hastub/homeassistant/helpers/update_coordinator.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/auth_failed.py",
  "harness_path": "tools/audit/round9/D10/s1/auth_failed.py",
  "value": 3,
  "unit": "arms (auth_as_transient)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "audit box B1 (Linux container)",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; the metric is a count and immune to contention",
  "tolerance": "exact",
  "load1": 1.16,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--fix: wrap _fetch_tibber_prices to raise ConfigEntryAuthFailed (defined locally as an IntegrationError subclass, because the stub lacks it) when the fetch fails after _tibber_start_reauth fired, and let the first refresh pass it through the update wrappers as upstream's async_config_entry_first_refresh does.",
  "expected_direction": "to_zero",
  "observed_value": "auth_as_transient 3 -> 0; transient_ok stays 2"
}
```

## Non-findings

- action-setup: services are registered in async_setup, with none registered or removed per entry: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/rules_check.py` gave 12 async_register in services.py; 12 registered by async_setup with no entry; 0 in setup_entry/unload; services.yaml 12
- appropriate-polling: coordinator interval: `rules_check.py (same command)` gave update_interval 30.0 min, captured at the DataUpdateCoordinator constructor
- brands: brand assets shipped: `rules_check.py` gave brand/icon.png 256x256; brand/logo.png present
- common-modules: `rules_check.py` gave coordinator.py DataUpdateCoordinator subclass 1; entity.py CoordinatorEntity base 1
- config-flow: UI setup with data_description on every field: `rules_check.py` gave manifest config_flow true; fields without data_description 0/91 (config), 0/117 (options)
- dependency-transparency: `rules_check.py` gave 3 requirements (numpy, scipy, threadpoolctl), 0 not a plain PyPI spec
- docs-actions: every service documented: `rules_check.py` gave 0 of 12 services.yaml actions absent from README + user docs
- docs-triggers / docs-conditions: vacuous, so exempt: `rules_check.py` gave device_trigger.py 0, device_condition.py 0
- docs-high-level-description, docs-installation-instructions, docs-removal-instructions: `rules_check.py` gave README headings 'What it does' 1, 'Installation' 1, 'Removal' 1
- entity-event-setup: `rules_check.py` gave 0 async_track_*/async_listen calls in platform or entity modules outside async_added_to_hass
- entity-unique-id and has-entity-name over every entity the real platform setups add: `rules_check.py (and --perturb as control)` gave 75 entities: unique_id missing 0, duplicates 0; has_entity_name False 0 (perturb -> 1)
- runtime-data: `rules_check.py` gave entry.runtime_data is HeatPumpOptimizerCoordinator; hass.data[DOMAIN] keys 0
- test-before-configure: the token is validated in every flow that accepts one: `rules_check.py` gave 3 'await validate_tibber_token(' sites (user, reauth_confirm, options entities)
- test-before-setup, offline arm: an unreachable service is ConfigEntryNotReady: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/auth_failed.py` gave transient_ok 2/2 (HTTP 500, connection error)
- unique-config-entry, control: the same answers twice abort already_configured: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/unique_id_drift.py` gave control_none and reconfigure arms: 0 duplicates accepted
- config-entry-unloading: `rules_check.py` gave async_unload_entry returns True; coordinator base async_shutdown called 1
- docs-configuration-parameters / docs-installation-parameters: `python3 label/keyword grep of strings.json config/options data labels against README.md + docs/*.md (non-plan) + docs/setup/*.md` gave options: 110/117 labels verbatim, the other 7 (min power, export compensation, away indicator, holiday calendar, circulation pump, DSO tariff, live fee sensor) found by topic keyword in docs/configuration.md; config: 87/91 verbatim, the other 4 (min power, floor heat loss) found by keyword
- entity-unavailable: entities follow coordinator failure: `rules_check.py` gave 53 entities available while last_update_success True, 0 while False
- integration-owner: `rules_check.py` gave codeowners 1 (@tvofi)
- log-when-unavailable: log once when unavailable, once on recovery: `rules_check.py` gave 3 failed Tibber fetches + 1 success: 1 ERROR line, 1 INFO recovery line
- parallel-updates: `rules_check.py (and --perturb as control)` gave 6/6 platforms declare it (sensor=0, binary_sensor=0, button/switch/climate/datetime=1); perturb -> 5
- reauthentication-flow: exists and is started on a refused token: `rules_check.py; auth_failed.py` gave async_step_reauth defined 1; a 401 starts 1 reauth flow (reauth_flows_started=1). The new token's account is not checked; the cause is in D10-s1-01.
- action-exceptions, services side: service handlers raise on refusal: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/press_vs_service.py` gave run_optimization raises HomeAssistantError in 2/2 not-run arms and returns normally in the prices_ok control

## Harnesses

- `tools/audit/round9/D10/s1/rules_check.py`
- `tools/audit/round9/D10/s1/unique_id_drift.py`
- `tools/audit/round9/D10/s1/press_vs_service.py`
- `tools/audit/round9/D10/s1/auth_failed.py`
- `tools/audit/round9/D10/s1/quality_scale.yaml`

## Unfinished

- **D10.M1**: The REPORT.md file could not be written: the harness tool refused a report .md write from this subagent. Its full content (method, tier table, findings, non-findings) is carried in this JSON. The orchestrator should write it at tools/audit/round9/D10/s1/REPORT.md if the file is required. Also left: the DiagnoseIntervalButton.async_press seam of D10-s1-02 is named but not counted. On a coordinator with no settled interval it logs INFO and returns normally.
- **D10.M2**: The rows for config-flow-test-coverage and test-coverage are carried from the in-tree register without measurement. They wait on D10-s2's M3 per-module coverage number.

## Leads

- owner D10-s2, `custom_components/heatpump_optimizer/config_flow.py` `config-flow-test-coverage / test-coverage rows`: s1 carried both coverage-bearing Bronze/Silver rows as done without measuring them. The per-module coverage number is D10.M3 and decides both rows.
- owner D10-s2, `custom_components/heatpump_optimizer/strings.json` `exceptions section`: exception-translations (gold): the fixes for D10-s1-02 (button raise) and D10-s1-03 (ConfigEntryAuthFailed) add raise sites, and each needs a translation_key in strings.json/en/sv.
- owner D10-s2, `custom_components/heatpump_optimizer/quality_scale.yaml` `manifest quality_scale: platinum`: The manifest tier is derived from the in-tree register, which marks unique-config-entry, test-before-setup and action-exceptions done. The s1 draft marks them todo, so the declared tier depends on the gold/platinum rows only through s1's Bronze/Silver outcome.
