# D10 — Home Assistant integration quality scale, audit round 3

**Baseline** `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` (round-3 export, no
`.git`). **Box** 8-core Apple M1, 8 GB, python3 3.11.5, node v20.10.0, mypy
2.3.1, coverage 7.16.0. **Load** `load1` ran from 12.4 at dispatch to 197.5 across the
session, with eleven other agent sessions on the box; every number in this report is a count, a percentage or a ratio, so
none of them moves with the load. No wall-clock or RSS number is reported.

Custom integrations cannot declare a quality-scale tier officially — `hassfest`
returns early on `quality_scale.yaml` for a non-core repository — so this report
is rule by rule, not tier by tier.

## Verdict

| | count |
|---|---|
| rules in the published checklist | 54 |
| rules in the shipped `quality_scale.yaml` | 54 |
| measured `done` | 45 |
| measured `exempt` | 4 |
| measured `todo` | 3 — `config-flow`, `docs-examples`, `strict-typing` |
| unmeasured in this export | 2 — `test-coverage`, `config-flow-test-coverage` |
| statuses the shipped register gets wrong | 4 |

Four findings, all small: one stale register (`D10-01`), one missing
`data_description` on the reauthentication field (`D10-02`), the Platinum
`strict-typing` gap with its size (`D10-03`), and a coordinator built without
its config entry behind a stub that cannot see the difference (`D10-04`).
Nothing in this dimension costs a user money or comfort at this baseline.

## Method

The checklist and the per-rule pages were fetched from
developers.home-assistant.io on 2026-09-10 (listed under `exposure`) rather
than recalled: **54 rules — 20 Bronze, 10 Silver, 21 Gold, 3 Platinum.** One
check per rule was then executed against the tree and recorded with its command
and result. The integration ships its own
`custom_components/heatpump_optimizer/quality_scale.yaml`; that file was treated
throughout as a **claim to be verified**, and comparing it against the executed
checks is itself one of the measurements.

Five harnesses, all under `tools/audit/round3/D10/`, each runnable by the single
command in its own header:

| harness | what it measures |
|---|---|
| `qs_register.py` | one check per rule for all 54 rules; the divergence count against the shipped register; writes `rule_table.tsv` |
| `entity_rules.py` | the seven entity-shaped rules, by instantiating every entity through each platform's real `async_setup_entry` |
| `log_once_rule.py` | `log-when-unavailable`: log records by level over five failed polls and a recovery |
| `diagnostics_rule.py` | `diagnostics`: credential and coordinate leakage in the rendered payload |
| `coordinator_entry_rule.py` | whether `DataUpdateCoordinator.__init__` is given the config entry |
| `coverage_rule.sh` | `test-coverage` and `config-flow-test-coverage`: statement coverage per module |
| `strict_typing_rule.sh` | `strict-typing`: `mypy --strict` errors by code, with `tests/hastub` on `MYPYPATH` |

Two traps were live in this export and are recorded so a verifier does not
re-hit them:

- **`tests/hastub`'s `Entity` has none of Home Assistant's `_attr_*` → property
  machinery.** A sweep that reads `entity.unique_id` reports *74 of 74 entities
  have no unique id*, which is false. `entity_rules.py:_attr()` prefers a
  property the integration declares and falls back to the `_attr_` shadow. The
  first run of that harness produced the wrong answer for exactly this reason.
- **The export deliberately deletes `docs/audit-*.md`, `docs/backlog.md` and
  `RELEASE_NOTES.md`.** `README.md` links to all four. A documentation link
  check run in this export therefore reports broken links that are artefacts of
  the export, not defects; no link-check result is reported here for those four
  paths.
- Two gate scripts exit non-zero in this export for want of `.git`
  (`tests/features.py`: 1 of 2136 checks, an unresolvable `recorded_at`;
  `tests/entities.py`: the handover's `updated-for` ancestry check). Both are
  export artefacts. Coverage data from a script is unaffected by its exit status
  and was kept.

## The rule table

54 rules. `claimed` is the status in the shipped `custom_components/heatpump_optimizer/quality_scale.yaml`; `measured` is what the executed check returned. Every row is produced by `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py`, which also writes `tools/audit/round3/D10/rule_table.tsv`; the rows that need another harness name it in the evidence column.

| rule | tier | claimed | measured | evidence command | result |
|---|---|---|---|---|---|
| `action-setup` | bronze | done | done | `… qs_register.py` | AST: _async_register_services is called from async_setup and from no other top-level entry point; hass.services.async_register lives in services.py |
| `appropriate-polling` | bronze | done | done | `… qs_register.py` | DataUpdateCoordinator constructed with an explicit update_interval |
| `brands` | bronze | done | done | `… qs_register.py` | brand/icon.png (256, 256), brand/logo.png present |
| `common-modules` | bronze | done | done | `… qs_register.py` | entity.py + coordinator.py, HeatPumpOptimizerEntity shared base |
| `config-flow` | bronze | done | **todo** | `… qs_register.py` | config_flow=true; 1 field(s) with no data_description: ['config.reauth_confirm.tibber_token'] |
| `config-flow-test-coverage` | bronze | done | **unmeasured** | `bash tools/audit/round3/D10/coverage_rule.sh` | config_flow.py statement coverage = None% |
| `dependency-transparency` | bronze | done | done | `… qs_register.py` | requirements all version-constrained PyPI packages: ['numpy>=1.24.0', 'scipy>=1.10.0', 'threadpoolctl>=3.5.0'] |
| `docs-actions` | bronze | done | done | `… qs_register.py` | 12/12 services named in README/docs |
| `docs-triggers` | bronze | done | done | `… qs_register.py` | vacuous: 0 trigger platforms (no trigger.py, no async_get_triggers) |
| `docs-conditions` | bronze | done | done | `… qs_register.py` | vacuous: 0 condition platforms (no condition.py, no async_get_conditions) |
| `docs-high-level-description` | bronze | done | done | `… qs_register.py` | README '## What it does' |
| `docs-installation-instructions` | bronze | done | done | `… qs_register.py` | README '## Installation' with a HACS subsection |
| `docs-removal-instructions` | bronze | done | done | `… qs_register.py` | README '### Removal' |
| `entity-event-setup` | bronze | done | done | `… qs_register.py` | 0 event subscriptions in the six platform modules; every entity is a CoordinatorEntity, so the base class owns the subscription lifecycle |
| `entity-unique-id` | bronze | done | done | `… entity_rules.py` | 74 entities, 0 without a unique_id, 0 duplicates |
| `has-entity-name` | bronze | done | done | `… entity_rules.py` | 0 entities without has_entity_name |
| `runtime-data` | bronze | done | done | `… qs_register.py` | entry.runtime_data written in __init__, read by all 6 platforms, typed alias present |
| `test-before-configure` | bronze | done | done | `… qs_register.py` | config flow calls validate_tibber_token before creating the entry |
| `test-before-setup` | bronze | done | done | `… qs_register.py` | AST: async_setup_entry awaits coordinator.async_config_entry_first_refresh(), which is what raises ConfigEntryNotReady; the literal name appears in the package only in 2 comments |
| `unique-config-entry` | bronze | done | done | `… qs_register.py` | async_set_unique_id + _abort_if_unique_id_configured in config_flow.py |
| `action-exceptions` | silver | done | done | `… qs_register.py` | 21 HomeAssistantError/ServiceValidationError raise sites |
| `config-entry-unloading` | silver | done | done | `… qs_register.py` | async_unload_entry unloads every platform |
| `docs-configuration-parameters` | silver | done | done | `… qs_register.py` | docs/configuration.md, 55962 bytes |
| `docs-installation-parameters` | silver | done | done | `… qs_register.py` | README installation section plus docs/configuration.md field reference |
| `entity-unavailable` | silver | done | done | `… qs_register.py` | 17 `available` overrides in the entity modules, 17 of them conjoined with super().available; the CoordinatorEntity base supplies the rest |
| `integration-owner` | silver | done | done | `… qs_register.py` | codeowners=['@tvofi'] |
| `log-when-unavailable` | silver | todo | **done** | `… python3 tools/audit/round3/D10/log_once_rule.py` | outage latch: first failure ERROR, subsequent DEBUG, recovery INFO (measured by log_once_rule.py) |
| `parallel-updates` | silver | done | done | `… entity_rules.py` | 0 of 6 platforms without a PARALLEL_UPDATES declaration |
| `reauthentication-flow` | silver | done | done | `… qs_register.py` | async_step_reauth + async_step_reauth_confirm in config_flow.py |
| `test-coverage` | silver | todo | **unmeasured** | `bash tools/audit/round3/D10/coverage_rule.sh` | statement coverage of the integration = None% (rule bar: >95%) |
| `devices` | gold | done | done | `… qs_register.py` | one DeviceInfo, every entity attached through entity.py |
| `diagnostics` | gold | done | done | `… python3 tools/audit/round3/D10/diagnostics_rule.py` | async_get_config_entry_diagnostics with async_redact_data (token redaction measured by diagnostics_rule.py) |
| `discovery` | gold | exempt | exempt | `… qs_register.py` | 0 discovery keys in manifest.json; the service is a cloud API and the hardware is user-picked HA entities |
| `discovery-update-info` | gold | exempt | exempt | `… qs_register.py` | no network address is stored, so there is nothing to update |
| `docs-data-update` | gold | done | done | `… qs_register.py` | README '## How it works' |
| `docs-examples` | gold | todo | todo | `… qs_register.py` | 3 yaml automation examples in docs/automations.md, 0 blueprint mentions |
| `docs-known-limitations` | gold | done | done | `… qs_register.py` | README 'Boundaries worth knowing before you pick a path' + 0 occurrences of the word 'limitation' |
| `docs-supported-devices` | gold | done | done | `… qs_register.py` | README '## Supported heat pumps and controls' |
| `docs-supported-functions` | gold | done | done | `… qs_register.py` | README '## Entities' and '## Services' |
| `docs-troubleshooting` | gold | done | done | `… qs_register.py` | README '## Troubleshooting' |
| `docs-use-cases` | gold | done | done | `… qs_register.py` | README '## What it does' + '## Quick start' describe real-world use; 0 literal 'use case' occurrences |
| `dynamic-devices` | gold | exempt | exempt | `… qs_register.py` | 0 device-registry create sites; one static device per entry |
| `entity-category` | gold | done | done | `… entity_rules.py` | 20 of 74 entities carry an entity_category |
| `entity-device-class` | gold | done | done | `… entity_rules.py` | 35 of 74 entities carry a device_class |
| `entity-disabled-by-default` | gold | done | done | `… entity_rules.py` | 6 entities disabled by default |
| `entity-translations` | gold | done | done | `… entity_rules.py` | 0 entities without a translation_key; 0 keys absent from strings.json |
| `exception-translations` | gold | todo | **done** | `… qs_register.py` | 21/21 raise sites carry translation_domain+translation_key; strings.json has 21 exceptions entries |
| `icon-translations` | gold | done | done | `… entity_rules.py` | 69 entity icons in icons.json, 4 without one (all four carry a device_class, whose default icon the rule prefers), 0 _attr_icon pins |
| `reconfiguration-flow` | gold | todo | **done** | `… qs_register.py` | async_step_reconfigure in config_flow.py |
| `repair-issues` | gold | done | done | `… qs_register.py` | 15 create-issue call sites, 17 translated issues, repairs.py fix flow |
| `stale-devices` | gold | exempt | exempt | `… qs_register.py` | device lifetime equals config-entry lifetime; 0 removal sites |
| `async-dependency` | platinum | done | done | `… qs_register.py` | aiohttp only; 0 synchronous HTTP clients imported |
| `inject-websession` | platinum | done | done | `… qs_register.py` | 3 async_get_clientsession call sites, 0 privately constructed ClientSession |
| `strict-typing` | platinum | todo | todo | `MYPY=… bash tools/audit/round3/D10/strict_typing_rule.sh` | mypy --strict over the integration: 578 errors, 67 unannotated defs, py.typed absent |

## Findings

Grouped by phenomenon. Severity is by consequence for a user on
Raspberry-Pi-class hardware, and this dimension does not produce much of it:
the executed verdict over 54 rules is **45 done, 4 exempt, 3 todo, 2
unmeasured**, so most of what follows is small. That is the finding.

### D10-01 — the shipped register calls three rules `todo` that the tree satisfies

`custom_components/heatpump_optimizer/quality_scale.yaml` marks
`log-when-unavailable`, `exception-translations` and `reconfiguration-flow` as
`todo`, each with a comment describing a specific defect. All three defects are
absent from this baseline:

| rule | the register's claim | what the executed check returned |
|---|---|---|
| `log-when-unavailable` | "6 ERRORs per 5 failed polls, latch double-counts" | `errors_over_5_failures=1`, `debugs_over_5_failures=4`, `info_on_recovery=1` (`log_once_rule.py`) |
| `exception-translations` | "13/13 raise sites untranslated, 0 exceptions sections" | 21/21 raise sites carry `translation_domain` **and** `translation_key`; `strings.json` has 21 `exceptions` entries; all 21 keys resolve in `en.json` and `sv.json` |
| `reconfiguration-flow` | "tracked in issue #196" | `config_flow.py:1673` defines `async_step_reconfigure` |

The file's own totals line ("44 done · 4 exempt · 6 todo") is wrong in the same
direction: the measured split is 45 done / 4 exempt / 3 todo, with the two
coverage rules unmeasured in this export (see *What I could not finish*).

- **Severity** `low` — a stale register costs a user nothing directly; it costs
  the next reader, who plans work that is already done and trusts a `done` that
  is not (D10-02).
- **Metric** rules whose `quality_scale.yaml` status differs from the status
  `qs_register.py`'s own check of the tree returns, out of 54.
- **Executed** `register_divergences=4`, `rules_todo_but_satisfied=3`,
  `rules_done_but_unsatisfied=1`.
- **Perturbation** rename `async_step_reconfigure` to
  `async_step_reconfigure_disabled` in `config_flow.py`;
  `rules_todo_but_satisfied` falls 3 → 2 and the `reconfiguration-flow` row
  stops diverging.
- **Fix scope** re-derive the file from `qs_register.py` (a draft is at
  `tools/audit/round3/D10/quality_scale.draft.yaml`), and wire `qs_register.py`
  — or an equivalent — into the gate so the register cannot go stale again.
  Today nothing in `tests/` reads `quality_scale.yaml`.

### D10-02 — `config-flow`: the reauthentication step's only field has no `data_description`

The `config-flow` rule requires `data_description` in `strings.json` "to give
context about the input field". Across the whole flow surface — 13 config steps
and 23 options steps, 270 fields — exactly one field has none, and it is
`config.reauth_confirm.tibber_token`: the single field of the single screen a
user only ever reaches because their Tibber token has stopped working. Every
other token field in the flow (`config.user.tibber_token`) does carry one.

- **Severity** `low` — one field, and the field's label still renders; what is
  lost is the line that would say where a replacement token comes from, at the
  moment the user needs it.
- **Metric** fields under `strings.json`'s `config`/`options` `step.*.data` with
  no matching key under the same step's `data_description`.
- **Executed** `1` of `270` (`qs_register.py`, `config-flow` row).
- **Perturbation** add the key to `strings.json` (and `translations/en.json`,
  `translations/sv.json`); the count goes 1 → 0 and the `config-flow` row stops
  diverging.
- The shipped register calls this rule `done`; it is the one `done` the tree
  contradicts.

### D10-03 — `strict-typing` is the one Platinum rule that is unmet, and by how much

Under the D10 brief's ruler — `mypy --strict` with `tests/hastub` on `MYPYPATH`
— the integration produces **578 error lines located inside
`custom_components/heatpump_optimizer/`** (648 in total; the other 70 are
`tests/hastub`'s own, and are excluded by path). The largest codes are
`no-untyped-call` 174, `type-arg` 119, `attr-defined` 102, `no-untyped-def` 67,
`no-any-return` 35. Errors land in 29 modules, led by `coordinator.py` (203),
`config_flow.py` (103) and `sensor.py` (64). `py.typed` is absent.

Part of that total is an artefact of the stub rather than of the integration:
`attr-defined` is dominated by `"HomeAssistant" has no attribute "data"` and
`no-untyped-call` by calls into stub functions that carry no annotations. The
number that is **ruler-independent** is `no-untyped-def = 67` — identical under
this harness and under the repository's own pinned census in
`tests/typing_budgets.json` (`mypy 2.3.1` + `homeassistant-stubs 2026.2.3` on
Python 3.13, total 191). Both rulers agree the rule is unmet; they disagree only
about the size of the gap, and the repository's own instrument is the one to
plan against.

- **Severity** `low` — no user-visible consequence was executed here; 67
  unannotated definitions in a 43 000-line numerical integration is where a
  type defect hides rather than a defect itself.
- **Metric** `mypy --strict` error lines whose path is under
  `custom_components/heatpump_optimizer/`, split by error code.
- **Executed** `integration_errors=578`, `code_no_untyped_def=67`,
  `py_typed_present=0`.
- **Perturbation** annotate any one unannotated `def`; `code_no_untyped_def`
  falls 67 → 66.
- **Fix scope** the repository already has the instrument (`tests/typing_ruler.py`,
  a per-code ratchet at 191); this rule closes by paying that ratchet down, not
  by adding a new mechanism. No Home Assistant API is involved, so the
  `hacs.json` floor of `2025.2.0` does not bind it.

### D10-04 — the coordinator is built without its config entry, and no test can see it

`HeatPumpOptimizerCoordinator.__init__` calls
`super().__init__(hass, _LOGGER, name=..., update_interval=...)`. Home
Assistant's own current example on
`developers.home-assistant.io/docs/integration_fetching_data` (fetched
2026-09-10) passes `config_entry=config_entry` as well. Instrumenting the base
`__init__` and building the coordinator the way `async_setup_entry` builds one:
one call, `kwargs_actually_passed=['name', 'update_interval']`,
`calls_passing_config_entry=0`, and `coordinator.config_entry` is unset —
the integration keeps its own `self.entry` instead.

The reason this survived a 2136-check feature suite and a 74-entity sweep is
the second half of the finding: `tests/hastub`'s stub is
`def __init__(self, *args, **kwargs)`. It names no parameter, so **no gate test
can distinguish the documented call from this one**, and
`tests/ha_contract.py:535` — the file whose job is to say what the stub owes
Home Assistant — carries an `S()` simplification entry for
`DataUpdateCoordinator` that records two absent *members*
(`_debounced_refresh`, `async_add_listener`) and says nothing about the
constructor's parameters, so `config_entry` is neither supplied by the stub nor
declared missing from it.

- **Severity** `medium` — bounded and one line to fix, but it is a real
  divergence from the documented construction, and the instrument that should
  have caught it is structurally unable to.
- **Metric** `DataUpdateCoordinator.__init__` invocations made by the
  integration that pass a `config_entry` argument.
- **Executed** `super_init_calls=1`, `calls_passing_config_entry=0`,
  `coordinator_config_entry_is_set=0`, `stub_names_config_entry=0`.
- **Perturbation** add `config_entry=entry` to the `super().__init__` call;
  `calls_passing_config_entry` goes 0 → 1 and `coordinator_config_entry_is_set`
  0 → 1.
- **What was not executed** the consequence on a real Home Assistant. No Home
  Assistant package is installed on this box, so this report does not claim a
  deprecation warning or a version at which it becomes an error; the claim is
  the divergence and the gate's blindness to it, both of which are executed.
- **Fix scope** one keyword in `coordinator.py`, plus a named parameter in the
  stub and an extension of the `tests/ha_contract.py:535` entry to the
  constructor's parameter set, so the gate can see the difference.

## Non-findings — what was checked and held

Every row of the rule table below is one of these; the ones worth naming
separately, because a later round should not re-do them:

| what was checked | command | result |
|---|---|---|
| Every entity the six platforms add has a unique id, and no two share one | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/entity_rules.py` | 74 entities (59 sensor, 5 binary_sensor, 4 switch, 4 button, 1 climate, 1 datetime); `missing_unique_id=0`, `duplicate_unique_ids=0` |
| `has-entity-name` on every entity | same | `missing_has_entity_name=0` — one `_attr_has_entity_name = True` on the shared base in `entity.py` reaches all 74 |
| Every entity name comes from a translation key that resolves | same | `missing_translation_key=0`, `translation_key_absent_from_strings=0` |
| `icon-translations` | same | 69 of 73 keyed icons present in `icons.json`, `attr_icon_pins=0`; the 4 without an icon are `optimal_setpoint`, `outdoor_temperature_optimizer` (device class `temperature`), `measured_power` (`power`) and `compressor_frequency_advisor` (`frequency`) — the rule prefers the device-class default there, so this is 4 correct absences, not 4 gaps |
| `parallel-updates` on every platform | same | `platforms_without_parallel_updates=0` (sensor 0, binary_sensor 0, switch 1, button 1, climate 1, datetime 1) |
| `log-when-unavailable` really logs once | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/log_once_rule.py` | 1 ERROR, 4 DEBUG over five failed polls; 1 INFO naming the outage length on recovery; the latch re-arms, so a second outage logs 1 more ERROR and not 0 |
| `diagnostics` leaks no credential and no precise home location | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/diagnostics_rule.py` | `token_leaks=0`, `precise_coordinate_leaks=0`, `entry_name_leaks=0`; coordinates coarsened to 1 decimal place; the entity ids a support case needs are kept |
| `exception-translations` end to end | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py` | 21/21 raise sites translated, 21 `exceptions` keys in `strings.json`, 0 unresolved in `en.json` or `sv.json` |
| `action-setup` binds actions in `async_setup`, not per entry | same (AST check) | `_async_register_services` is called from `async_setup` and from no other top-level entry point; 12 `hass.services.async_register` calls all live in `services.py` |
| `runtime-data` used throughout | same | `entry.runtime_data` written once in `__init__.py`, read by all 6 platforms, and the typed `HeatPumpOptimizerConfigEntry = ConfigEntry[HeatPumpOptimizerCoordinator]` alias exists |
| `discovery`, `discovery-update-info`, `dynamic-devices`, `stale-devices` are genuinely exempt | same | 0 discovery keys in `manifest.json`; 0 `async_get_or_create` device-registry sites; 0 `async_remove_device` sites |
| `dependency-transparency` | same | `numpy>=1.24.0`, `scipy>=1.10.0`, `threadpoolctl>=3.5.0` — all version-constrained, all PyPI, all OSI-licensed |
| `docs-actions` | same | 12 of 12 services named in `README.md`/`docs/` |
| `brands` (adapted for a custom integration) | same | `brand/icon.png` 256×256, `brand/logo.png` present |
| `inject-websession` | same | 3 `async_get_clientsession(` call sites, 0 privately constructed `aiohttp.ClientSession` |
| `repair-issues` | same | 15 `async_create_issue(` sites, 17 translated `issues` entries, `repairs.py` provides `async_create_fix_flow` and a `RepairsFlow` |

### Disproved leads

- **`docs-examples` looked like a fourth stale `todo`.** `docs/automations.md`
  carries 3 YAML automation examples, which is what the register's comment says
  is missing ("0 automation examples"). Fetching the rule page showed it asks
  for **blueprints**, hosted in the blueprint repository or the community
  exchange and *linked* from the documentation — not for YAML in the docs.
  `blueprint` appears 0 times in `README.md` or `docs/`, so the rule is `todo`,
  the register is right, and the first version of `qs_register.py`'s check was
  wrong. Recorded here because the corrected check is in the committed harness
  and a verifier will see the count change if they read the rule page too.
- **`action-setup` looked unmet** on a first, text-based check that split
  `__init__.py` at `async def async_setup_entry` — the helper
  `_async_register_services` is *defined* below that point, so the naive check
  saw a registration "after" setup-entry. The AST check in the committed
  harness asks the right question (which top-level function calls it) and the
  rule is `done`.
- **`docs-known-limitations` and `docs-use-cases` carry no heading containing
  those words** (0 occurrences of "limitation", 0 of "use case" across
  `README.md` and `docs/`). Both are nevertheless satisfied in substance —
  `## Supported heat pumps and controls` ends with "Boundaries worth knowing
  before you pick a path" and four explicit boundary bullets including
  "Heating, not cooling"; `## What it does` and `## Quick start — the first 30
  minutes` are use cases in everything but name. Marked `done` rather than
  manufacturing two findings out of vocabulary.

## The Home Assistant version floor

`hacs.json` declares `"homeassistant": "2025.2.0"`. The brief asks, for every
`todo` rule needing an API newer than that floor, the minimum release that
carries it. **No `todo` rule needs one.**

| todo rule | what closing it needs | minimum HA release |
|---|---|---|
| `config-flow` (D10-02) | one `data_description` key in `strings.json` | none — `data_description` predates the floor by years |
| `docs-examples` | blueprints published and linked from the docs | none — a documentation and repository change, no API |
| `test-coverage` | test scripts | none |
| `strict-typing` | annotations, and paying down `tests/typing_budgets.json` | none |

Checked from the other side as well: every Home Assistant API the integration
already calls sits at or below the floor — `ConfigFlowResult` (2024.4),
`ConfigEntry.runtime_data` and the subscripted `ConfigEntry[...]` (2024.6),
`async_step_reconfigure` (2024.4, with `_get_reauth_entry` guarded by
`getattr` for the 2024.11 helper), `SupportsResponse` (2023.7),
`async_forward_entry_setups` (2022.8), `RepairsFlow`/`async_create_issue`
(2022.9). The one construction that has moved on since — the coordinator's
`config_entry` argument — is D10-04, and it is backward compatible.

## What I could not finish

- **No real Home Assistant.** Every dynamic check ran against `tests/hastub`.
  That is enough to measure the integration's own shape, and it is why D10-04
  reports the divergence and the gate's blindness rather than a claim about
  what a real Home Assistant logs. `tests/nightly_ha.py` is the file that runs
  against the real package; it was not run here.
- **`test-coverage` and `config-flow-test-coverage` are UNMEASURED, and the
  reason is the export, not the tree.** `tests/entities.py:11299` reads
  `RELEASE_NOTES.md`, which the round-3 export deletes, so the script dies there
  with `FileNotFoundError` — 11 299 of 14 996 lines in, before its
  `Diagnostics (D10-12)` section at `:13020` and everything after it. A coverage
  run in this export therefore under-counts by roughly a quarter of the largest
  test script, and reports `diagnostics.py` at 0.00 % even though
  `tests/entities.py:13068` calls `async_get_config_entry_diagnostics`
  outright. What the 12 scripts that did complete produced —
  **90.81 % total (15 113 statements, 1 389 missed), `config_flow.py` 98.17 %
  (13 missed at 451, 1110, 1115, 1609, 2224, 2417-2421), 28 of 55 modules below
  95 %** — is a loose lower bound and is recorded in
  `coverage_report_12scripts.txt` and in `coverage_rule.sh`'s header. **It does
  not refute the >95 % bar and it does not refute the register's `config_flow.py
  is at 100 %` claim**, and no finding is built on it. The remaining five
  scripts (`backtest`, `optimality`, `plan_view`, `frontend`, `golden`) were
  still running when the box reached a 1-minute load average of 197 and the run
  was stopped. Re-take: run `coverage_rule.sh` in a checkout that still has
  `RELEASE_NOTES.md`, on a quiet box.
- **`tests/deployment_shape.py` is excluded from the coverage number** because
  it spawns its own interpreters, so this process's tracer sees nothing of it.
  `tests/stress.py` and `tests/rolling.py` are excluded by the round-3 seat
  block and by their `SLOW` gate respectively.
- **`tests/dst_checks.py` fails 1 of 27 checks in this export**
  ("dt_util carries the configured zone"). It is deliberately outside
  `run.sh`'s wiring accounting (`tests/run.sh:280`), so this is not a gate
  regression; it is noted because the coverage run executed it.
- **The `mypy` census disagrees with the repository's own.** Both were reported
  rather than reconciled: reconciling them needs Python ≥ 3.13.2 and
  `homeassistant-stubs 2026.2.3`, which `tests/typing_budgets.json` pins and
  this box (3.11.5) cannot satisfy.

## exposure

- Fetched from `developers.home-assistant.io` on 2026-09-10, and nothing else
  from the network except the `pip install mypy` that the brief's
  `strict-typing` measurement requires:
  - `/docs/core/integration-quality-scale/checklist`
  - `/docs/core/integration-quality-scale/rules/strict-typing`
  - `/docs/core/integration-quality-scale/rules/dependency-transparency`
  - `/docs/core/integration-quality-scale/rules/test-coverage`
  - `/docs/core/integration-quality-scale/rules/config-flow`
  - `/docs/core/integration-quality-scale/rules/docs-examples`
  - `/docs/integration_fetching_data`
- Read in the tree: `custom_components/heatpump_optimizer/quality_scale.yaml`,
  which is the round-2 D10 register and names issues #189, #194–#197 and
  #216–#218 and their round-2 finding ids. The brief requires that file to be
  read as a claim, so this exposure is by instruction. Its statuses were **not**
  used as input to any check — `qs_register.py` computes every verdict from the
  tree first and compares afterwards — and its issue numbers were not looked up.
- `README.md` and `docs/*.md` were read for the eleven documentation rules.
  `docs/audit-*.md`, `docs/backlog.md` and `RELEASE_NOTES.md` are absent from
  this export and were not sought. No `gh`, no GitHub, no git history (the
  export has no `.git`).
- `D10-<nn>` ids appearing in production comments (`diagnostics.py` "audit
  D10-12", `config_flow.py` "D10-14", `coordinator.py` "D10-07/-09") were read
  as context; no earlier finding text was opened.

## Harnesses

All under `tools/audit/round3/D10/`, each runnable by the single command in its
own header comment, each printing `RESULT <name>=<value> <unit>` lines plus
`thread_factor`, `load1` and `swapins`. All numbers are counts, percentages or
ratios; none is a wall-clock or RSS number, so none needs a quiet-window re-take
except the coverage run, which needs a checkout rather than a quiet box.

| harness | command | headline result |
|---|---|---|
| `qs_register.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py` | `register_divergences=4`, `rules_measured_done=45`, `rules_measured_todo=3` |
| `entity_rules.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/entity_rules.py` | `entities_total=74`, `missing_unique_id=0`, `missing_has_entity_name=0`, `platforms_without_parallel_updates=0` |
| `log_once_rule.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/log_once_rule.py` | `errors_over_5_failures=1` |
| `diagnostics_rule.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/diagnostics_rule.py` | `token_leaks=0`, `precise_coordinate_leaks=0` |
| `coordinator_entry_rule.py` | `PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/coordinator_entry_rule.py` | `calls_passing_config_entry=0`, `stub_names_config_entry=0` |
| `strict_typing_rule.sh` | `MYPY=<mypy 2.3.1> bash tools/audit/round3/D10/strict_typing_rule.sh` | `integration_errors=578`, `code_no_untyped_def=67` |
| `coverage_rule.sh` | `bash tools/audit/round3/D10/coverage_rule.sh` | did not complete — see *What I could not finish* |
| `make_draft_yaml.py` | `python3 tools/audit/round3/D10/make_draft_yaml.py` | writes `quality_scale.draft.yaml` from `rule_table.tsv` |

Artefacts beside them: `rule_table.tsv` (the machine-readable rule table),
`quality_scale.draft.yaml` (the brief's draft register, every comment being the
evidence string of the check that produced the status), `mypy_strict.txt` and
`mypy_by_code.json`, `coverage_report_12scripts.txt` and `coverage_scripts.txt`.

`mypy` is not installed on this box; it was installed into a throwaway venv
outside the tree (`python3 -m venv …; pip install mypy` → 2.3.1, which is the
version `tests/typing_budgets.json` pins). Nothing was installed into the
export, and no production or test file in the export was modified.

`tools/audit/` is already on `tests/closure.py`'s `INERT` tuple
(`tests/closure.py:166` ff.), so these files are classified and do not force a
full suite when a fixer lands them.
