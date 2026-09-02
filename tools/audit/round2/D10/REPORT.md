# D10 — Home Assistant integration quality scale (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884` · export `audit-r2-baseline` · Apple M1, 8 GB, macOS Darwin 25.6.0, Python 3.13.1, numpy 2.5.2, scipy 1.18.1, mypy 2.3.1, coverage 7.16.0 · fan-out conditions (load1 6.9 at the checker run; all headline numbers are counts).

## Method

The current checklist (54 rules: Bronze 20, Silver 10, Gold 21, Platinum 3) and every per-rule page were fetched from developers.home-assistant.io on 2026-09-02. One check per rule was executed by `tools/audit/round2/D10/check_rules.py`: an AST or regex count over `custom_components/heatpump_optimizer`, a stub-driven drive of the production symbol (the coordinator's update cycle and Tibber fetch under fake sessions, the config flow's user step under each token verdict, the entry's setup/unload through `heatpump_optimizer.async_setup_entry`, and the 65-entity roster through each platform's real `async_setup_entry`), or a documentation lookup over README.md, docs/*.md and DISCLAIMER.md. Test coverage was measured once by `tools/audit/round2/D10/coverage_suite.sh` (coverage.py 7.16 installed into the private prefix `/tmp/d10-cov`; every process of every default-gate Python script traced through a `sitecustomize` hook, then combined). Strict typing is `mypy --strict` over the package with the stub on `MYPYPATH`. Custom integrations cannot declare a tier; adherence is recorded rule by rule in `quality_scale.yaml` (draft in this directory).

Status counts: **done 27 · todo 21 · exempt 6** of 54 (bronze: 12 done / 6 todo / 2 exempt of 20; silver: 4 done / 6 todo / 0 exempt of 10; gold: 9 done / 8 todo / 4 exempt of 21; platinum: 2 done / 1 todo / 0 exempt of 3).

Perturbations for D10-01 through D10-05 were executed in a scratch copy of the export (never in the export itself) and their observed values are recorded; the remaining perturbations are stated for the judge.

## Findings

### D10-01 — Nothing prevents a second config entry: no unique-id or entries-match guard in the config flow

**Severity** medium · **class** bug (provisional) · **rules** see the tier table

**Claim.** HeatPumpOptimizerConfigFlow.async_step_user never checks for an existing entry, so a user who adds the integration twice gets two coordinators driving the same heat pump switch.

**Mechanism.** config_flow.py contains none of async_set_unique_id/_abort_if_unique_id_configured/_async_abort_entries_match/_async_current_entries and manifest.json has no single_config_entry; strings.json already carries abort.already_configured, unused. Driven under the stub with one entry present, the user step returns the temperature form instead of an abort. Consequence: two entries pin the same suggested entity ids (the second gets _2 suffixes, breaking the card's id-suffix discovery), every service loops over both coordinators, and two MPC solves run per interval on Pi-class hardware.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT unique_entry_guards` → **0 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow.async_step_user`

**Metric.** Count of duplicate-entry guards in config_flow.py/manifest.json, and whether async_step_user aborts when hass.config_entries already holds an entry (0/1).

**Perturbation.** Insert at the top of async_step_user: `if self.hass.config_entries.async_entries(DOMAIN): return self.async_abort(reason="already_configured")` (production idiom: self._async_abort_entries_match()); RESULT unique_entry_guards and flow_aborts_with_existing_entry both go 0 -> 1 — expected direction **up**; observed: unique_entry_guards=1, flow_aborts_with_existing_entry=1 (scratch copy, same checker).

**Null control.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py (flow_user('ok', existing_entries=0))` → form/temperature (with no existing entry the flow proceeds identically; the guard's absence is the only difference)

**Files.** custom_components/heatpump_optimizer/config_flow.py, custom_components/heatpump_optimizer/manifest.json

**Proposed fix scope.** config_flow.py: two lines in async_step_user (_async_abort_entries_match() or async_set_unique_id(DOMAIN)+_abort_if_unique_id_configured()); alternatively manifest single_config_entry: true (HA >= 2024.3, above the 2024.1.0 floor).

### D10-02 — A rejected Tibber token is reported as a transient UpdateFailed: no ConfigEntryAuthFailed, no reauth flow

**Severity** medium · **class** bug (provisional) · **rules** see the tier table

**Claim.** _fetch_tibber_prices turns HTTP 401, 403 and an errors payload into UpdateFailed, so an invalid token is indistinguishable from an outage: setup retries forever and no reauthentication flow is offered.

**Mechanism.** coordinator.py has zero references to ConfigEntryAuthFailed and config_flow.py has no async_step_reauth; under a fake session returning 401, 403 or {'errors': [...]} the exception class raised is UpdateFailed in all three cases. Home Assistant therefore shows 'retrying setup' / unavailable entities and the ERROR-once log line, never the reauth repair. The user's only path is the options flow's 'entities' page. The trailing `except Exception` in _fetch_tibber_prices converts anything raised inside the request block into UpdateFailed, so the fix must re-raise ConfigEntryAuthFailed ahead of it (a first perturbation that only raised on 401/403 inside the block was swallowed: 0 -> 0).

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT auth_failures_raising_ConfigEntryAuthFailed` → **0 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fetch_tibber_prices`

**Metric.** Of three auth-failure responses (401, 403, 200+errors payload) driven through _fetch_tibber_prices, the number that raise ConfigEntryAuthFailed rather than UpdateFailed.

**Perturbation.** coordinator.py _fetch_tibber_prices: (a) before the generic status check `if resp.status in (401, 403): raise ConfigEntryAuthFailed(...)` and (b) `except ConfigEntryAuthFailed: raise` ahead of `except aiohttp.ClientError` (import from homeassistant.exceptions); RESULT auth_failures_raising_ConfigEntryAuthFailed goes 0 -> 2 of 3. The export's stub lacks the class, so add `class ConfigEntryAuthFailed(HomeAssistantError)` to tests/hastub/homeassistant/exceptions.py for the run. — expected direction **up**; observed: 2 (scratch copy with the stub class added; the same edit without (b) stayed at 0).

**Files.** custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/config_flow.py, custom_components/heatpump_optimizer/strings.json

**Proposed fix scope.** coordinator.py: raise ConfigEntryAuthFailed on 401/403 (and on an errors payload whose message says the token is invalid); config_flow.py: async_step_reauth + async_step_reauth_confirm reusing validate_tibber_token and async_update_reload_and_abort (~40 lines); strings.json: reauth_confirm step. All within the 2024.1.0 floor.

### D10-03 — Every failed refresh logs ERROR with a traceback: the outer handler in _async_update_data defeats the log-once latch

**Severity** low · **class** bug (provisional) · **rules** see the tier table

**Claim.** Three consecutive failed refreshes produce four ERROR records with tracebacks, where the log-when-unavailable rule (and the integration's own _tibber_fetch_failed latch) intends one.

**Mechanism.** _tibber_fetch_failed logs ERROR on the first failure and DEBUG afterwards, then raises UpdateFailed; _async_update_data's trailing `except Exception` catches that UpdateFailed, logs `_LOGGER.error(..., exc_info=True)` and re-raises. Null control: _fetch_tibber_prices alone three times gives exactly one ERROR, so the surplus is the outer handler. In real Home Assistant the DataUpdateCoordinator adds its own single ERROR on top. A day-long Tibber outage at the 30-minute interval is 49 tracebacks in the log.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT error_records_over_3_failed_refreshes` → **4 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data`

**Metric.** Number of logging records at level ERROR or above on logger heatpump_optimizer during three consecutive _async_update_data calls whose Tibber fetch fails.

**Perturbation.** coordinator.py, the `except Exception as err:` at the end of _async_update_data: change `_LOGGER.error(` to `_LOGGER.debug(` (the coordinator base already logs the outage once); RESULT error_records_over_3_failed_refreshes goes 4 -> 1 — expected direction **down**; observed: 1 (scratch copy, same checker).

**Null control.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT error_records_over_3_failed_fetches_direct` → 1 (the fetch alone, three times: the latch yields exactly one ERROR)

**Files.** custom_components/heatpump_optimizer/coordinator.py

**Proposed fix scope.** coordinator.py: demote the two outer `_LOGGER.error(..., exc_info=True)` calls (_async_update_data and _async_first_refresh_light) to debug, or gate them on the same latch.

### D10-04 — Service actions swallow operational failures: run_optimization no-ops, restore_learned_snapshot answers {restored: []}

**Severity** low · **class** bug (provisional) · **rules** see the tier table

**Claim.** With no price data, heatpump_optimizer.run_optimization returns None after a WARNING, and restore_learned_snapshot/simulate_plan report failure only inside their response dicts; no HomeAssistantError is raised anywhere in the integration.

**Mechanism.** async_run_optimization returns on `len(prices) < 4` after _LOGGER.warning; async_restore_learned_snapshot returns False; async_simulate returns {'error': 'no_plan'}. The handlers in __init__.py raise ServiceValidationError for bad input (14 sites) but never HomeAssistantError for a failed operation, so a user calling run_optimization from an automation sees success. simulate_plan's dict is consumed by the card and is arguably a response contract; the other two are silent. async_run_optimization additionally wraps its body in `except Exception` (coordinator.py:5536), so an exception raised inside it never reaches the service caller either: the raise has to happen in the handler.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT service_failure_paths_returning_silently` → **3 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer:async_setup_entry.handle_run_optimization -> coordinator:HeatPumpOptimizerCoordinator.async_run_optimization`

**Metric.** Of run_optimization, simulate_plan and restore_learned_snapshot called through the registered handlers on a coordinator with no prices/plan/snapshot, how many return instead of raising.

**Perturbation.** __init__.py handle_run_optimization: before `await coord.async_run_optimization()` add `if not coord._prices: raise HomeAssistantError("No electricity price data; nothing to optimize")`; RESULT service_failure_paths_returning_silently goes 3 -> 2 (a raise placed inside async_run_optimization is swallowed by its own except: 3 -> 3) — expected direction **down**; observed: 2 (scratch copy, same checker).

**Files.** custom_components/heatpump_optimizer/__init__.py, custom_components/heatpump_optimizer/coordinator.py

**Proposed fix scope.** coordinator.py/__init__.py: raise HomeAssistantError (translated) from run_optimization when the solve cannot run and from restore_learned_snapshot when no snapshot qualifies; keep simulate_plan's response contract but add the error to the response schema docs.

### D10-05 — Two buttons stay available after a failed refresh: available() overrides drop super().available

**Severity** low · **class** bug (provisional) · **rules** see the tier table

**Claim.** With coordinator.last_update_success False, 2 of 65 entities (optimize_now, run_system_identification) still report available.

**Mechanism.** ForceOptimizationButton.available and SystemIdentificationButton.available return their own flag without ANDing CoordinatorEntity.available; every sensor mixin in sensor.py does AND it. Pressing Optimize now during an outage triggers another failing refresh and looks like the button works.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT entities_available_after_failed_refresh` → **2 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.button:ForceOptimizationButton.available, SystemIdentificationButton.available`

**Metric.** Number of entities from the real platform setups whose .available is True while coordinator.last_update_success is False.

**Perturbation.** button.py: `return super().available and not self.coordinator.optimization_running` (and the same for system_identification_active); RESULT entities_available_after_failed_refresh goes 2 -> 0 — expected direction **to_zero**; observed: 0 (scratch copy, same checker).

**Files.** custom_components/heatpump_optimizer/button.py

**Proposed fix scope.** button.py: two one-line changes.

### D10-06 — All 11 services are registered in async_setup_entry, not async_setup (action-setup)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** __init__.py defines no async_setup; hass.services.async_register is called 11 times inside async_setup_entry and the services are removed after the last unload.

**Mechanism.** Service availability is tied to a loaded entry, so automation validation cannot see heatpump_optimizer.* while the entry is unloaded or failed setup, and a user gets 'service not found' instead of the rule's 'entry not loaded' ServiceValidationError.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT services_registered_in_setup_entry` → **11 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer:async_setup_entry (hass.services.async_register call sites)`

**Metric.** AST count of hass.services.async_register calls whose enclosing function is async_setup_entry in __init__.py.

**Perturbation.** Move the eleven async_register calls into a new `async def async_setup(hass, config)` with handlers resolving the loaded coordinator(s) from hass.data; RESULT services_registered_in_setup_entry goes 11 -> 0 and async_setup_defs 0 -> 1 — expected direction **to_zero**.

**Files.** custom_components/heatpump_optimizer/__init__.py

**Proposed fix scope.** __init__.py: add async_setup, move registration, drop the unload-time removal loop (handlers check for a loaded entry).

### D10-07 — No platform declares PARALLEL_UPDATES (parallel-updates)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** None of the five platform modules defines PARALLEL_UPDATES.

**Mechanism.** The rule wants an explicit value: 0 for the coordinator-fed read-only platforms (sensor, binary_sensor) and 1 where actions go out (button, switch, climate). Functionally harmless here (one coordinator, no outbound device protocol), so hygiene.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT platforms_declaring_parallel_updates` → **0 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.sensor/binary_sensor/button/switch/climate module globals`

**Metric.** Number of platform files whose module level assigns PARALLEL_UPDATES.

**Perturbation.** Add `PARALLEL_UPDATES = 0` at module level in sensor.py; RESULT platforms_declaring_parallel_updates goes 0 -> 1 — expected direction **up**.

**Files.** custom_components/heatpump_optimizer/sensor.py, custom_components/heatpump_optimizer/binary_sensor.py, custom_components/heatpump_optimizer/button.py, custom_components/heatpump_optimizer/switch.py, custom_components/heatpump_optimizer/climate.py

**Proposed fix scope.** five one-line additions.

### D10-08 — Runtime state in hass.data[DOMAIN], entity base classes outside entity.py (runtime-data, common-modules)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** There are 0 references to ConfigEntry.runtime_data against 24 hass.data[DOMAIN] references in seven files, and the five CoordinatorEntity base classes live in the platform files rather than entity.py.

**Mechanism.** Layout conventions only: no user-visible consequence. runtime_data needs HA >= 2024.4 (hacs.json floor is 2024.1.0), so adopting it moves the floor; entity.py is floor-neutral.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT hass_data_domain_refs` → **24 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer:async_setup_entry (hass.data[DOMAIN] writes) and the platform base classes`

**Metric.** Regex counts of `runtime_data` and of `hass.data[DOMAIN]`/`.get(DOMAIN`/`.setdefault(DOMAIN` across the integration; count of CoordinatorEntity base classes outside entity.py.

**Perturbation.** In async_setup_entry add `entry.runtime_data = coordinator`; RESULT runtime_data_refs goes 0 -> 1 (hass_data_domain_refs stays until the readers move) — expected direction **up**.

**Files.** custom_components/heatpump_optimizer/__init__.py, custom_components/heatpump_optimizer/sensor.py, custom_components/heatpump_optimizer/binary_sensor.py, custom_components/heatpump_optimizer/button.py, custom_components/heatpump_optimizer/switch.py, custom_components/heatpump_optimizer/climate.py, custom_components/heatpump_optimizer/frontend.py

**Proposed fix scope.** Typed HeatPumpOptimizerConfigEntry = ConfigEntry[HeatPumpOptimizerCoordinator] plus reader updates (24 sites) once the floor is 2024.4; move the five base classes into entity.py.

### D10-09 — All 14 service exceptions carry literal English messages; no exceptions block in strings.json (exception-translations)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** 0 of 14 raise ServiceValidationError(...) sites pass translation_domain/translation_key, and strings.json has no 'exceptions' section.

**Mechanism.** Swedish is the second shipped language (translations/sv.json) yet every service error reaches the UI in English. The API (translation_key on HomeAssistantError, 2023.11) is inside the floor.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT exception_raises_with_translation_key` → **0 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer:async_setup_entry handlers (raise ServiceValidationError sites)`

**Metric.** Regex count of raise ServiceValidationError/HomeAssistantError sites whose call carries translation_key, over all such raises.

**Perturbation.** Give one raise `translation_domain=DOMAIN, translation_key="no_entry_loaded"` and add the key under strings.json exceptions; RESULT exception_raises_with_translation_key goes 0 -> 1 — expected direction **up**.

**Files.** custom_components/heatpump_optimizer/__init__.py, custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/strings.json, custom_components/heatpump_optimizer/translations/en.json, custom_components/heatpump_optimizer/translations/sv.json

**Proposed fix scope.** __init__.py 13 sites + coordinator.py 1 site; strings.json exceptions block; sv.json.

### D10-10 — Icons are entity state: 64 _attr_icon assignments and no icons.json (icon-translations)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** icons.json is absent and the platform files assign _attr_icon 64 times.

**Mechanism.** Icon translations need HA >= 2024.2; the hacs.json floor is 2024.1.0, so this is a floor decision, not an oversight. Device-class icons should not be overridden where the class fits.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT icons_in_code` → **64 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.sensor/binary_sensor/button/switch class attributes _attr_icon`

**Metric.** Regex count of `_attr_icon =` assignments across the five platform files; existence of icons.json.

**Perturbation.** Delete one `_attr_icon = ...` line (e.g. OptimizationModeSensor) and move it to icons.json; RESULT icons_in_code goes 64 -> 63 — expected direction **down**.

**Files.** custom_components/heatpump_optimizer/sensor.py, custom_components/heatpump_optimizer/binary_sensor.py, custom_components/heatpump_optimizer/button.py, custom_components/heatpump_optimizer/switch.py, hacs.json

**Proposed fix scope.** icons.json with 64 entries; raise hacs.json to 2024.2.0.

### D10-11 — No diagnostics platform (diagnostics)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** diagnostics.py does not exist and no async_get_config_entry_diagnostics is defined, for an integration with 149 published keys, thirteen learners and a token that would need redaction.

**Mechanism.** Support requests must scrape entity attributes by hand; the sensor docstrings mention 'the diagnostics dump' that does not exist.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT diagnostics_defs` → **0 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `custom_components/heatpump_optimizer/diagnostics.py:async_get_config_entry_diagnostics (absent)`

**Metric.** Existence of diagnostics.py and count of async_get_config_entry_diagnostics definitions.

**Perturbation.** Add diagnostics.py with async_get_config_entry_diagnostics returning async_redact_data(entry.data, [CONF_TIBBER_TOKEN]) plus coordinator.data; the diagnostics row flips to done (defs 0 -> 1) — expected direction **up**.

**Files.** custom_components/heatpump_optimizer/diagnostics.py

**Proposed fix scope.** New diagnostics.py (~30 lines): entry data with the token redacted, coordinator.data, learner state, last exception.

### D10-12 — Docs gaps: no removal instructions (Bronze), known limitations, blueprints or supported-devices statement

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** README.md and docs/*.md contain 0 removal-instruction matches, 0 'Known limitations' sections, 0 blueprint mentions or automation examples and 0 supported/unsupported-devices sections.

**Mechanism.** The documentation is otherwise unusually complete (every service field, every options page, every entity, troubleshooting, data-update cadence), so these are four missing sections, of which docs-removal-instructions is a Bronze rule.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT docs_removal_instructions` → **0 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `README.md (docs-* rule lookups; no code symbol)`

**Metric.** Case-insensitive regex matches for removal/uninstall instructions, 'Known limitations' headings, 'blueprint', and '(Un)supported devices' headings over README.md, docs/*.md, DISCLAIMER.md.

**Perturbation.** Add a '## Removing the integration' section to README.md; RESULT docs_removal_instructions goes 0 -> 1 — expected direction **up**.

**Files.** README.md, docs/configuration.md

**Proposed fix scope.** README.md: 'Removing the integration' (also delete the stored learner files under .storage), 'Known limitations', 'Supported controls' (on/off switch, ECL110 via MQTT, frequency-writable pumps); one or two blueprints (e.g. away mode from a calendar).

### D10-13 — mypy --strict reports 722 errors in 37 of 45 modules (strict-typing)

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** With the test stub on MYPYPATH, mypy --strict finds 722 errors: no-untyped-call 227, type-arg 111, no-untyped-def 106, attr-defined 90, no-any-return 79, union-attr 25.

**Mechanism.** no-untyped-def (106: e.g. every sensor's `def __init__(self, coordinator, entry)`) and type-arg (111: bare dict/list) are integration-internal; no-untyped-call is partly the untyped stub, so the true count against real Home Assistant is lower but not near zero. Counted from 'error:' lines under custom_components/ only.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT mypy_strict_errors` → **722 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact for mypy 2.3.1; re-take with the pinned mypy if the release differs; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `custom_components/heatpump_optimizer (mypy --strict over the package, MYPYPATH=tests/hastub)`

**Metric.** Count of mypy --strict 'error:' lines whose path starts with custom_components/, python-version 3.13, stub on MYPYPATH.

**Perturbation.** Annotate OptimizationModeSensor.__init__(self, coordinator: HeatPumpOptimizerCoordinator, entry: ConfigEntry) -> None in sensor.py; RESULT mypy_strict_errors goes down by at least 1 — expected direction **down**.

**Files.** custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/sensor.py, custom_components/heatpump_optimizer/config_flow.py, custom_components/heatpump_optimizer/__init__.py

**Proposed fix scope.** Annotate the 106 untyped defs and the 111 bare generics first (mechanical); attr-defined/union-attr need Optional narrowing in coordinator.py and config_flow.py.

### D10-14 — Statement coverage 88.4 % overall, 20 of 45 modules at 95 %; config_flow.py at 86.4 % against a 100 % rule

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** The default gate's Python scripts, run once under coverage.py, cover 88.4 % of the integration's 12877 statements; 20 of 45 modules reach the 95 % test-coverage bar and config_flow.py reaches 86.4 % against config-flow-test-coverage's 100 %.

**Mechanism.** The suite renders the config flow's user form but never submits it (0 tests call async_step_user with input), so the invalid_tibber_token/cannot_connect branches are unexecuted. Lowest modules: climate.py 59 %, open_meteo.py 67 %, diagnosis.py 77 %, coordinator.py 78 %, frontend.py 80 %, curve_learning.py 85 %, config_flow.py 86 %, grid_fee.py 87 %. Caveats: measured once on a shared box (timing provisional); env_drift.py, closure.py (git) and the Node scripts are not in the measured set; tests/entities.py aborted at line 4360/4587 on the export's missing RELEASE_NOTES.md (517 checks passed; the remaining section checks release-notes claims, not integration code); golden.py ran in strict mode and its fixture mismatch on this box does not change which lines execute.

**Evidence.** `PYTHON=<venv python> D10_COV_PREFIX=/tmp/d10-cov tools/audit/round2/D10/coverage_suite.sh (then check_rules.py reads coverage/coverage.json)  # RESULT coverage_total_pct` → **88.4 pct** (harness `tools/audit/round2/D10/coverage_suite.sh`, count, tolerance ±1.0 pt (fixture-dependent branches); load1 6.92, thread_factor 1.0; single run during the fan-out; scripts wall 1818 s PROVISIONAL; load1 at the end 3.66; the percentage is a count ratio)

**Instrumented symbol.** `custom_components/heatpump_optimizer/*.py (coverage.py source filter; every process the gate scripts start)`

**Metric.** Executed statements / total statements over custom_components/heatpump_optimizer/*.py, combined across all processes of the gate's Python scripts (coverage.py 7.16, sysmon core).

**Perturbation.** SLOW=1 tools/audit/round2/D10/coverage_suite.sh adds tests/rolling.py to the measured set; RESULT coverage_total_pct rises (conversely, removing features.py from SCRIPTS drops it by tens of points) — expected direction **up**.

**Files.** tests/entities.py, custom_components/heatpump_optimizer/config_flow.py

**Proposed fix scope.** tests/entities.py: drive async_step_user with input for all three verdicts and complete one full initial flow; then the lowest modules listed above.

### D10-15 — Declarative metadata gaps: two kWh sensors without SensorDeviceClass.ENERGY; DeviceInfo without entry_type SERVICE

**Severity** low · **class** hygiene (provisional) · **rules** see the tier table

**Claim.** Of the 55 sensors, 29 carry a device class; solar_surplus_forecast and dhw_heavy_day_demand publish kWh without ENERGY, and the one device is declared without entry_type=DeviceEntryType.SERVICE and with manufacturer 'Custom'.

**Mechanism.** The other three flagged sensors (ecl110_displace, ecl110_effective_displace, prediction_accuracy) are degree-Celsius deltas where TEMPERATURE would convert wrongly and are correctly classless. entry_type SERVICE exists since 2021.12 and changes only how the device is presented.

**Evidence.** `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT sensors_with_unit_but_no_device_class` → **5 count** (harness `tools/audit/round2/D10/check_rules.py`, count, tolerance exact; load1 6.92, thread_factor 1.0; fan-out: ten other auditors plus this dimension's own coverage run on the box; load1 6.9 at the checker run. The metric is a count and does not depend on load.)

**Instrumented symbol.** `heatpump_optimizer.sensor (roster _attr_device_class/_attr_native_unit_of_measurement); heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.device_info`

**Metric.** Count of sensor entities whose native unit maps to a SensorDeviceClass (°C, W, kW, kWh, W/m², Hz, min, h, L) but whose _attr_device_class is None; count of DeviceInfo with entry_type.

**Perturbation.** Set `_attr_device_class = SensorDeviceClass.ENERGY` on DHWHeavyDayDemand's sensor class; RESULT sensors_with_unit_but_no_device_class goes 5 -> 4 — expected direction **down**.

**Files.** custom_components/heatpump_optimizer/sensor.py, custom_components/heatpump_optimizer/coordinator.py

**Proposed fix scope.** sensor.py: two class attributes; coordinator.py device_info: entry_type=DeviceEntryType.SERVICE, manufacturer=the project name.


## Non-findings (checked and held)

| claim | command | value |
|---|---|---|
| appropriate-polling: the coordinator polls at the configured optimization interval, 30 min by default, 15 min when configured so; iot_class cloud_polling | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT update_interval_default_s` | 1800 s |
| brands: brands.home-assistant.io serves a real icon for heatpump_optimizer (digest differs from the placeholder served for a nonexistent domain) | `curl https://brands.home-assistant.io/_/heatpump_optimizer/icon.png | shasum -a 256 vs .../_/zz_no_such_domain_d10/icon.png` | distinct=True (curl sha256, 2026-09-02) |
| config-flow: manifest config_flow true; every field of the 9 config and 15 options steps has a data_description | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT flow_fields_without_data_description` | 0 count |
| dependency-transparency: numpy, scipy, threadpoolctl are OSI-licensed (BSD), on PyPI, with GitHub sources and public CI | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 3 of 3 (importlib.metadata; PyPI JSON for threadpoolctl 3.6.0) |
| docs-actions: all 11 services in services.yaml are in the README table and have field-level detail in docs/configuration.md | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT services_documented_readme` | 11 count |
| docs-triggers / docs-conditions: no custom triggers or conditions registered (exempt) | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 0 registrations |
| docs-high-level-description, docs-installation-instructions, docs-troubleshooting, docs-use-cases, docs-data-update: sections present | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | What it does=1, Installation/HACS/Manual/Requirements=4/4, Troubleshooting=1 (4 bullets), use-case paragraphs=9, interval statements=5 |
| docs-configuration-parameters / docs-installation-parameters: all 12 options pages with fields are headings in docs/configuration.md; all 17 user-step labels documented | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 12/12 and 17/17 |
| docs-supported-functions: README entity totals 55+4+4 (+switch, climate) equal the 65-entity roster | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT entities` | 65 count |
| entity-event-setup: no entity-level subscriptions outside async_added_to_hass; the coordinator's four state/timer subscriptions are released in async_shutdown | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 0 entity subscriptions; 4 _unsub_*() calls |
| entity-unique-id / has-entity-name: 65 entities through the real platform setups, 65 unique ids, has_entity_name on all | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT entities` | 65 count |
| test-before-configure: async_step_user maps invalid_auth -> invalid_tibber_token, cannot_connect -> cannot_connect, ok -> temperature step | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 3/3 branches |
| test-before-setup: async_config_entry_first_refresh is awaited in async_setup_entry (temporary failures raise through it); auth failures are the D10-02 finding | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | first refresh in setup=1 |
| config-entry-unloading: setup registers 11 services, unload removes all 11, pops the coordinator and reaches DataUpdateCoordinator.async_shutdown | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 11 -> 0 services; coordinator_left=False; base_shutdown_called=True |
| integration-owner: codeowners @tvofi | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | ['@tvofi'] |
| devices: one service device per entry with identifiers (DOMAIN, entry_id) shared by all 65 entities | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 1 device |
| discovery / discovery-update-info / dynamic-devices / stale-devices: cloud API plus the user's own entities, one device per entry (exempt) | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | manifest discovery keys=[] |
| entity-category: DIAGNOSTIC on 12 entities; 4 uncategorised diagnostic-looking ones are judgement calls (optimization_status and three buttons) | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT entities_with_category` | 12 count |
| entity-disabled-by-default: 6 noisy/rare sensors disabled by default | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT entities_disabled_by_default` | 6 count |
| entity-translations: every entity's translation_key exists in strings.json (55/4/4/1) and sv.json ships | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT entities_missing_translation` | 0 count |
| repair-issues: 11 async_create_issue call sites, every translation_key present in strings.json issues | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT repair_issue_create_calls` | 11 count |
| async-dependency: requirements are compute libraries; no synchronous HTTP library; solve and diagnostics run through async_add_executor_job (5 sites) | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 0 sync HTTP imports; 5 executor offloads |
| inject-websession: the three HTTP call sites use async_get_clientsession; no private aiohttp.ClientSession | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py` | 3 shared, 0 private |
| log-when-unavailable null control: _fetch_tibber_prices alone three times logs exactly one ERROR (the latch works; the surplus in D10-03 is the outer handler) | `PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py  # RESULT error_records_over_3_failed_fetches_direct` | 1 count |

## Test coverage (rules test-coverage, config-flow-test-coverage)

total **88.4 %** of 12877 statements (1493 missed); config_flow.py **86.4 %**; modules ≥ 95 %: **20 of 45**; scripts run 13, non-zero exits 2 (count  # entities golden); wall 1818 s PROVISIONAL; load1 at the end 3.66, thread_factor 1.00

Not in the measured set: `tests/env_drift.py` and `tests/closure.py` (need git; the export has none), the Node scripts (card.mjs, card_drift.mjs, setup_qa_render.mjs), and `tests/rolling.py` (SLOW=1 only; `SLOW=1 coverage_suite.sh` adds it). `tests/entities.py` aborted at line 4360 of 4587 because the export deliberately has no `RELEASE_NOTES.md` (517 checks had passed; the remaining section verifies release-notes claims, not integration code). `tests/golden.py` ran in strict mode; its fixture comparison does not reproduce on this box (tests/README.md says so) but the traced lines are the same.

| script | exit | wall s (provisional) |
|---|---|---|
| tests/features.py | 0 | 191 |
| tests/entities.py | 1 | 33 |
| tests/manual_plan.py | 0 | 15 |
| tests/open_meteo.py | 0 | 1 |
| tests/solar_alignment.py | 0 | 1 |
| tests/golden.py | 1 | 422 |
| tests/validate.py | 0 | 92 |
| tests/edge.py | 0 | 138 |
| tests/backtest.py | 0 | 144 |
| tests/optimality.py | 0 | 393 |
| tests/plan_view.py | 0 | 2 |
| tests/frontend.py | 0 | 0 |
| tests/stress.py | 0 | 386 |

Per module (lowest first):

| module | statements | missed | % |
|---|---|---|---|
| climate.py | 144 | 59 | 59.0 |
| open_meteo.py | 201 | 66 | 67.2 |
| diagnosis.py | 43 | 10 | 76.7 |
| coordinator.py | 3797 | 843 | 77.8 |
| frontend.py | 94 | 19 | 79.8 |
| curve_learning.py | 82 | 12 | 85.4 |
| config_flow.py | 493 | 67 | 86.4 |
| grid_fee.py | 175 | 23 | 86.9 |
| dhw_schedule.py | 247 | 32 | 87.0 |
| switch.py | 43 | 5 | 88.4 |
| presets.py | 127 | 14 | 89.0 |
| comfort_learning.py | 115 | 12 | 89.6 |
| __init__.py | 280 | 28 | 90.0 |
| sysid.py | 209 | 20 | 90.4 |
| accuracy.py | 189 | 15 | 92.1 |
| wear.py | 63 | 5 | 92.1 |
| away.py | 116 | 9 | 92.2 |
| mixing_valve.py | 27 | 2 | 92.6 |
| tariff.py | 204 | 15 | 92.6 |
| drift.py | 70 | 5 | 92.9 |
| manual_plan.py | 115 | 8 | 93.0 |
| snapshots.py | 100 | 7 | 93.0 |
| freq_control.py | 117 | 8 | 93.2 |
| battery.py | 87 | 5 | 94.3 |
| button.py | 59 | 3 | 94.9 |
| inputs.py | 221 | 11 | 95.0 |
| price_model.py | 202 | 10 | 95.0 |
| dhw_draws.py | 81 | 4 | 95.1 |
| optimizer.py | 1690 | 78 | 95.4 |
| thermal_model.py | 890 | 39 | 95.6 |
| sensor.py | 1032 | 40 | 96.1 |
| ledger.py | 75 | 2 | 97.3 |
| defrost.py | 205 | 4 | 98.0 |
| external_heat.py | 227 | 4 | 98.2 |
| topology.py | 142 | 2 | 98.6 |
| binary_sensor.py | 78 | 1 | 98.7 |
| pump_signals.py | 85 | 1 | 98.8 |
| const.py | 460 | 5 | 98.9 |
| comfort_band.py | 40 | 0 | 100.0 |
| currency.py | 4 | 0 | 100.0 |
| narrative.py | 41 | 0 | 100.0 |
| power_guard.py | 65 | 0 | 100.0 |
| pump_mode.py | 62 | 0 | 100.0 |
| pump_schedule.py | 42 | 0 | 100.0 |
| pv.py | 38 | 0 | 100.0 |

## Tier table

| rule | tier | status | check | result |
|---|---|---|---|---|
| action-setup | bronze | todo | AST __init__.py: async_setup defs; hass.services.async_register calls inside async_setup_entry | async_setup defs=0; async_register inside async_setup_entry=11 |
| appropriate-polling | bronze | done | update_interval kwarg HeatPumpOptimizerCoordinator.__init__ passes to DataUpdateCoordinator.__init__; manifest iot_class | update_interval default=1800 s, optimization_interval=15 => 900 s; iot_class=cloud_polling |
| brands | bronze | done | sha256(brands.home-assistant.io/_/heatpump_optimizer/icon.png) != sha256(.../_/zz_no_such_domain_d10/icon.png) | served icon digest distinct from placeholder=True (cached 2026-09-02); in-tree brand/icon.png,logo.png present=[True, True] (not a location Home Assistant reads) |
| common-modules | bronze | todo | ls coordinator.py entity.py; grep '^class .*(CoordinatorEntity, ' platform files | coordinator.py=True; entity.py=False; CoordinatorEntity base classes in platform files=5 (binary_sensor.py, button.py, climate.py, sensor.py, switch.py) |
| config-flow | bronze | done | manifest config_flow; strings.json step.data vs step.data_description | manifest config_flow=True; steps=9 config + 15 options; fields without data_description=0/237 (none) |
| config-flow-test-coverage | bronze | todo | coverage_suite.sh -> coverage.json[config_flow.py]; grep tests for async_step_user(<input>) | config_flow.py 86.4% (67 of 493 statements missed); tests calling async_step_user with input=0 (error branches invalid_tibber_token/cannot_connect never driven) |
| dependency-transparency | bronze | done | importlib.metadata for manifest requirements (License, Project-URL); PyPI JSON with --network | numpy 2.5.2: BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 src=github; scipy 1.18.1: Copyright (c) 2001-2002 Enthought, Inc.  src=github; threadpoolctl 3.6.0: BSD-3-Clause src=github [local metadata] |
| docs-actions | bronze | done | services.yaml names vs README '## Services' table and docs/configuration.md field detail | services.yaml=11; README table rows=11; field-level in docs/configuration.md=11 |
| docs-triggers | bronze | exempt | grep async_attach_trigger|device_trigger | trigger registrations=0 |
| docs-conditions | bronze | exempt | grep async_condition_from_config|device_condition | condition registrations=0 |
| docs-high-level-description | bronze | done | grep '^## What it does' README.md | heading=1; first paragraph describes the service and links the upstream project |
| docs-installation-instructions | bronze | done | grep '^## Installation|^### HACS|^### Manual|^## Requirements' README.md | headings found=4/4 |
| docs-removal-instructions | bronze | todo | grep -i 'remov(e|ing|al) (the )?integration|uninstall' README.md docs/*.md | matches=0 [] |
| entity-event-setup | bronze | done | grep async_track_|async_listen|subscribe in platform files; _unsub_*() calls in coordinator.async_shutdown | entity-level subscriptions outside async_added_to_hass=0; coordinator unsubscribes on shutdown=4 |
| entity-unique-id | bronze | done | roster via each platform's async_setup_entry: _attr_unique_id present and unique | entities=65; missing unique_id=0; duplicates=0 |
| has-entity-name | bronze | done | roster: _attr_has_entity_name | has_entity_name True on 65/65 entities |
| runtime-data | bronze | todo | grep runtime_data; grep 'hass.data[DOMAIN]' custom_components/heatpump_optimizer | runtime_data references=0; hass.data[DOMAIN] references=24 in __init__.py, binary_sensor.py, button.py, climate.py, frontend.py, sensor.py, switch.py |
| test-before-configure | bronze | done | HeatPumpOptimizerConfigFlow.async_step_user with validate_tibber_token patched to each verdict | invalid_auth->invalid_tibber_token, cannot_connect->cannot_connect, ok->step temperature |
| test-before-setup | bronze | done | grep async_config_entry_first_refresh in async_setup_entry; _fetch_tibber_prices under a 401/403/errors-payload session | first refresh in setup=1; ConfigEntryAuthFailed in code=0; 401->UpdateFailed, 403->UpdateFailed, 200+errors->UpdateFailed (all UpdateFailed => ConfigEntryNotReady retry loop) |
| unique-config-entry | bronze | todo | grep unique-id/entries-match guards in config_flow.py; manifest single_config_entry; async_step_user with one entry already in hass.config_entries | guards=0; manifest single_config_entry=None; with an existing entry the user step returns type=form step=temperature (no abort); strings.json abort.already_configured exists unused |
| action-exceptions | silver | todo | grep raise ServiceValidationError|HomeAssistantError; call run_optimization/simulate_plan/restore_learned_snapshot through FakeServices on a coordinator with no prices | ServiceValidationError raises=14; HomeAssistantError raises=0; failure outcomes: run_optimization: returned None; simulate_plan: returned {'results': {'test_entry': {'error': 'no_plan', 'rate_limited': False}}}; restore_learned_snapshot: returned {'restored': []} |
| config-entry-unloading | silver | done | heatpump_optimizer.async_setup_entry then async_unload_entry on FakeHass | services after setup=11, after unload=0; coordinator left in hass.data=False; coordinator.async_shutdown reached base=True |
| docs-configuration-parameters | silver | done | strings.json options step titles (steps with fields) as headings in docs/configuration.md | options pages with fields=12; documented as headings=12 |
| docs-installation-parameters | silver | done | strings.json config.step.user.data labels found in docs/configuration.md '## Initial setup' | config steps with fields=8; user-step labels documented=17/17; 'Initial setup' section=14931 chars |
| entity-unavailable | silver | todo | roster with coordinator.last_update_success=False: count entity.available | available after a failed refresh=2/65 [('button', 'optimize_now'), ('button', 'run_system_identification')] |
| integration-owner | silver | done | manifest codeowners | codeowners=['@tvofi'] |
| log-when-unavailable | silver | todo | _async_update_data x3 with the Tibber fetch failing (stub: no HTTP session); count ERROR records on logger heatpump_optimizer | UpdateFailed raised=3/3; ERROR records=4 (rule: 1) with exc_info on 4: ['Unexpected error fetching prices: no HTTP session available ', 'Error updating Heat Pump Optimizer: Unexpected error fetchin', 'Error updating Heat Pump Optimizer: Unexpected error fetchin', 'Error updating Heat Pump Optimizer: Unexpected error fetchin']; null control _fetch_tibber_prices x3 alone => 1 ERROR |
| parallel-updates | silver | todo | grep '^PARALLEL_UPDATES' in the five platform files | declared in 0/5 platforms |
| reauthentication-flow | silver | todo | grep async_step_reauth config_flow.py; ConfigEntryAuthFailed count | async_step_reauth=0; ConfigEntryAuthFailed raises=0; the Tibber token is a credential (not exempt); re-entry only via the options 'entities' page |
| test-coverage | silver | todo | coverage_suite.sh (every gate script under coverage.py, combined) -> coverage.json | total 88.4% of 12877 statements; modules >= 95%: 20/45; lowest: climate 59%, open_meteo 67%, diagnosis 77%, coordinator 78%, frontend 80% |
| devices | gold | done | roster: device_info identifiers, entry_type | devices=1 (identifiers=frozenset({('heatpump_optimizer', 'test_entry')})); entry_type set on 0/65; manufacturer='Custom' model='MPC Optimizer' |
| diagnostics | gold | todo | ls diagnostics.py; grep async_get_config_entry_diagnostics | diagnostics.py=False; async_get_config_entry_diagnostics defs=0 |
| discovery | gold | exempt | manifest discovery keys | discovery keys=[] |
| discovery-update-info | gold | exempt | manifest discovery keys | discovery keys=[] |
| docs-data-update | gold | done | grep 'optimization interval (30 minutes by default)' README.md docs/*.md | matches=5 ['README.md:2', 'docs/architecture.md:1', 'docs/how-it-works.md:2'] |
| docs-examples | gold | todo | grep -i blueprint; grep '^ *(automation|trigger|alias):' README.md docs/*.md | blueprint mentions=0; automation examples=0; the YAML examples present are card configs (6 fences) |
| docs-known-limitations | gold | todo | grep '^#* Known limitations' README.md docs/*.md DISCLAIMER.md | sections=0; DISCLAIMER.md carries caveats (2 'not a ...' statements) but no limitations list |
| docs-supported-devices | gold | todo | grep '^#* (Un)supported devices' README.md docs/*.md | sections=0; the control paths (on/off switch, ECL110 over MQTT, frequency writer) are described separately (README lines 'Inverter frequency', 'ECL110 heat-curve control'; docs/ecl110.md) |
| docs-supported-functions | gold | done | README '## Entities' section: per-platform totals vs the roster | README totals=['55', '4', '4'] (+ switch and climate) vs roster=65 entities; table rows=63 |
| docs-troubleshooting | gold | done | grep '^## Troubleshooting' README.md | section=1; bullets=4 |
| docs-use-cases | gold | done | README '## What it does': bold-lead use-case paragraphs | use-case paragraphs=9 |
| dynamic-devices | gold | exempt | roster: one device per entry | devices per entry=1; entities=65 |
| entity-category | gold | done | roster: _attr_entity_category | categories={'None': 53, 'diagnostic': 12}; uncategorised entities with diagnostic-looking keys=4: ['optimization_status', 'run_system_identification', 'reset_learned_comfort_weight', 'diagnose_last_interval'] |
| entity-device-class | gold | todo | roster sensors: native unit maps to a SensorDeviceClass but _attr_device_class is None | sensors with device_class=29; unit-mappable without one=5: ['ecl110_displace[°C]', 'ecl110_effective_displace[°C]', 'prediction_accuracy[°C]', 'solar_surplus_forecast[kWh]', 'dhw_heavy_day_demand[kWh]'] |
| entity-disabled-by-default | gold | done | roster: _attr_entity_registry_enabled_default is False | disabled by default=6: ['ecl110_displace', 'ecl110_effective_displace', 'contract_comparison', 'dhw_heavy_day_demand', 'valve_target_recommendation', 'compressor_frequency_advisor'] |
| entity-translations | gold | done | roster: _attr_translation_key present in strings.json entity.<platform> | entities=65; missing translation=0 []; strings entity keys={'sensor': 55, 'binary_sensor': 4, 'button': 4, 'switch': 1}; translations/sv.json present=True |
| exception-translations | gold | todo | grep raise ServiceValidationError(...translation_key; strings.json 'exceptions' | raises=14; with translation_key=0; strings.json exceptions block=False |
| icon-translations | gold | todo | ls icons.json; grep '_attr_icon =' platform files | icons.json=False; _attr_icon assignments=64 |
| reconfiguration-flow | gold | todo | grep async_step_reconfigure config_flow.py | async_step_reconfigure=0; options flow pages=15 (the 'entities' page re-validates the token, so the function exists outside the reconfigure source) |
| repair-issues | gold | done | regex async_create_issue(...translation_key=) in coordinator.py vs strings.json issues | create calls=11 over 11 keys; strings issues=13; keys without strings=[]; is_fixable=False on 12 calls |
| stale-devices | gold | exempt | roster: one device per entry, identifiers=(DOMAIN, entry_id) | the device is the entry; removing the entry removes it |
| async-dependency | platinum | done | grep sync HTTP libraries; manifest requirements; grep async_add_executor_job | requirements=['numpy>=1.24.0', 'scipy>=1.10.0', 'threadpoolctl>=3.5.0'] (compute libraries, no I/O); sync HTTP imports=0; HTTP via aiohttp; executor offloads=5 |
| inject-websession | platinum | done | grep async_get_clientsession( vs aiohttp.ClientSession( | shared-session call sites=3 (config_flow.py, coordinator.py, open_meteo.py); private sessions=0 |
| strict-typing | platinum | todo | mypy --strict --python-version 3.13 custom_components/heatpump_optimizer with MYPYPATH=tests/hastub | errors=722 in 37/45 files (mypy run, 9 s, PROVISIONAL); by code: no-untyped-call=227, type-arg=111, no-untyped-def=106, attr-defined=90, no-any-return=79, union-attr=25; worst files: coordinator.py=172, sensor.py=144, config_flow.py=114, __init__.py=70; py.typed n/a (integration, not a library) |

## Harnesses

- `tools/audit/round2/D10/check_rules.py` — every rule's check; prints the tier table and the RESULT lines (`PYTHONPATH=tests/hastub python tools/audit/round2/D10/check_rules.py`; `--emit-yaml` prints the draft quality_scale.yaml; `--no-mypy`, `--network`, `--coverage-json` documented in the header).
- `tools/audit/round2/D10/coverage_suite.sh` — coverage of the gate's Python scripts, one run, combined; writes `coverage/` (RESULTS.txt, coverage_report.txt, coverage.json, per_module.tsv, scripts.tsv, logs/).
- `tools/audit/round2/D10/quality_scale.yaml` — the draft, generated by the checker.
- `tools/audit/round2/D10/check_rules.out` — the checker's output for the run this report cites.

## Minimum Home Assistant release for todo rules needing an API above the hacs.json floor (2024.1.0)

| rule | API | minimum release |
|---|---|---|
| icon-translations | icons.json | 2024.2 |
| unique-config-entry (manifest route) | `single_config_entry` | 2024.3 (`_async_abort_entries_match` works at the floor) |
| runtime-data | `ConfigEntry.runtime_data` | 2024.4 |
| reconfiguration-flow | `SOURCE_RECONFIGURE` / `async_update_reload_and_abort` | 2024.4 (helper `_get_reconfigure_entry` 2024.11) |
| exception-translations, reauthentication-flow, diagnostics, parallel-updates, action-setup, devices entry_type | within the floor | — |

## Not finished

- Coverage is a single fan-out run; the wall seconds are provisional and a quiet-window re-take is expected to change only the timing column.
- `tests/rolling.py` (SLOW=1) was not included in the coverage set (about fifteen minutes uncovered, much more under this load).
- The mypy count is exact for mypy 2.3.1; a different mypy release moves it.

## Exposure

README.md, docs/*.md and DISCLAIMER.md were read for the docs-* rules (no audit records exist in the export); code comments in coordinator.py cite D10-07, D10-09 and D1-02 ids from an earlier round as context only.
