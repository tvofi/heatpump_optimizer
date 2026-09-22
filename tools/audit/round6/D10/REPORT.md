# D10 — Home Assistant integration quality scale (audit round 6)

Baseline: export of `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), read only.
Interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, run from the
export root with `PYTHONPATH=tests/hastub`. Machine: Apple M1, 8 GB, macOS 25.6.0.
Standard: the public HA quality-scale checklist and per-rule pages under
`developers.home-assistant.io`, fetched over HTTPS on 2026-09-22. No GitHub record was read
and no earlier audit round in this export was consulted.

## Method

A custom integration cannot declare a tier officially, so adherence is decided rule by rule.
Three instruments, all under `tools/audit/round6/D10/`:

1. `qs_audit.py` — one executed check per rule: an AST walk over the package plus a
   stub-driven `async_setup_entry` for the six platforms (`FakeCoordinator(DATA)` with
   `tests/entities.py`'s own `DATA` literal, `FakeEntry().runtime_data`), so 74 entity
   instances are collected and interrogated rather than the source text. It never reads
   `quality_scale.yaml` for a verdict; it compares against the register afterwards.
2. `coverage_gap.py` — the `test-coverage` instrument (finding D10-01).
3. `quality_scale.draft.yaml` — the register as this audit would write it: byte-identical to
   the shipped one but for the `test-coverage` comment (see Finding D10-01).

```
cd <export root>
PYTHONPATH=tests/hastub python3 tools/audit/round6/D10/qs_audit.py      # 48 rule verdicts
PYTHONPATH=tests/hastub python3 tools/audit/round6/D10/coverage_gap.py  # D10-01
```

Cross-checked against the pre-existing in-tree instrument
`tools/audit/round4/D10/qs_rules.py` (executed by `tests/harness_headers.py` on every pull
request), which reports `rules_total=54`, `declared_mismatch=0`, and four rows it leaves
`unmeasured` because they need a toolchain or a remote listing (bronze 1, silver 1, gold 1,
platinum 1).

### Headline

| measure | value |
|---|---|
| rules in the register | 54 (20 bronze / 10 silver / 21 gold / 3 platinum) |
| register statuses | 50 `done`, 4 `exempt`, 0 `todo` |
| rules my executed walk decides | 48 |
| disagreements with the register | **0** |
| `qs_rules.py` `declared_mismatch` | 0 |
| findings | **1** (D10-01: the Silver `test-coverage` row is keyed to an aggregate, and one module measures below the rule's 95 % bar at the baseline while the per-pull-request check is green) |
| modules measured below the 95 % bar | **1** — `sysid.py` at 94.62 % (492/520 statements, 28 missed) |
| package coverage, measured | 97.55 % over 16873 statements, against the recorded 96.0 % floor |

The register is accurate. Every one of the 54 rows either agrees with an executed check or is
one of the four rows keyed elsewhere (below). The single finding is not a false status: it is
that the record a true status is keyed to measures a different predicate than the rule.

## The 54-rule tier table

`executed` is this audit's verdict from an executed check; `result` carries the number it
produced.

| rule | tier | register | executed | evidence | result |
|---|---|---|---|---|---|
| `action-setup` | Bronze | done | done | `qs_audit.py` `rule_action_setup` | value=12; async_register calls in services.py; services.yaml declares 12 |
| `appropriate-polling` | Bronze | done | done | `qs_audit.py` `rule_appropriate_polling` | value=1; iot_class=cloud_polling, update_interval from CONF_OPTIMIZATION_INTERVAL |
| `brands` | Bronze | done | done | brand-asset probe | icon.png + logo.png present, 256x256, sha256 8b92b5f14977036f (byte-identical) |
| `common-modules` | Bronze | done | done | `qs_audit.py` `rule_common_modules` | value=0; sensor imports the shared entity base; re-declared bases=[] |
| `config-flow` | Bronze | done | done | `qs_audit.py` `rule_config_flow` | value=3; ConfigFlow=True OptionsFlow=True async_step_user=True |
| `config-flow-test-coverage` | Bronze | done | done | `coverage_gap.py` | recorded config_flow_percent_floor=100.0 %, read per PR by read_module_percent |
| `dependency-transparency` | Bronze | done | done | `qs_audit.py` `rule_dependency_transparency` | value=0; non-PyPI requirements: []; all numpy/scipy/threadpoolctl |
| `docs-actions` | Bronze | done | done | `qs_audit.py` `rule_docs_actions` | value=0; README heading lookup, 0 missing |
| `docs-triggers` | Bronze | done | done | `qs_audit.py` `rule_docs_triggers` | value=0; trigger registrations; rule admits no exception, so 0 sites is a vacuous done |
| `docs-conditions` | Bronze | done | done | `qs_audit.py` `rule_docs_conditions` | value=0; condition registrations; vacuous done |
| `docs-high-level-description` | Bronze | done | done | `qs_audit.py` `rule_docs_high_level_description` | value=0; README heading lookup, 0 missing |
| `docs-installation-instructions` | Bronze | done | done | `qs_audit.py` `rule_docs_installation_instructions` | value=0; README heading lookup, 0 missing |
| `docs-removal-instructions` | Bronze | done | done | `qs_audit.py` `rule_docs_removal_instructions` | value=0; README heading lookup, 0 missing |
| `entity-event-setup` | Bronze | done | done | `qs_audit.py` `rule_entity_event_setup` | value=0; event subscriptions in an entity platform module; sites=[] |
| `entity-unique-id` | Bronze | done | done | `qs_audit.py` `rule_entity_unique_id` | value=0; entities with no _attr_unique_id; offenders=[] |
| `has-entity-name` | Bronze | done | done | `qs_audit.py` `rule_has_entity_name` | value=0; entities without _attr_has_entity_name; offenders=[] |
| `runtime-data` | Bronze | done | done | `qs_audit.py` `rule_runtime_data` | value=18; entry.runtime_data references across the package |
| `test-before-configure` | Bronze | done | done | `qs_audit.py` `rule_test_before_configure` | value=1; config flow surfaces validation errors |
| `test-before-setup` | Bronze | done | done | `qs_audit.py` `rule_test_before_setup` | value=1; async_config_entry_first_refresh raises ConfigEntryNotReady itself |
| `unique-config-entry` | Bronze | done | done | `qs_audit.py` `rule_unique_config_entry` | value=1; async_set_unique_id / _abort_if_unique_id_configured present |
| `action-exceptions` | Silver | done | done | `qs_audit.py` `rule_action_exceptions` | value=20; HomeAssistantError/ServiceValidationError raises in services.py |
| `config-entry-unloading` | Silver | done | done | `qs_audit.py` `rule_config_entry_unloading` | value=1; async_unload_entry present |
| `docs-configuration-parameters` | Silver | done | done | `qs_audit.py` `rule_docs_configuration_parameters` | value=0; README heading lookup, 0 missing |
| `docs-installation-parameters` | Silver | done | done | `qs_audit.py` `rule_docs_installation_parameters` | value=0; README heading lookup, 0 missing |
| `entity-unavailable` | Silver | done | done | `qs_audit.py` `rule_entity_unavailable` | value=0; entities still available after last_update_success=False; offenders=[] |
| `integration-owner` | Silver | done | done | `qs_audit.py` `rule_integration_owner` | value=1; manifest codeowners |
| `log-when-unavailable` | Silver | done | done | `qs_audit.py` `rule_log_when_unavailable` | value=4; failed-latch defs=2, recovered-latch defs=2 |
| `parallel-updates` | Silver | done | done | `qs_audit.py` `rule_parallel_updates` | value=0; platform modules with no PARALLEL_UPDATES: [] |
| `reauthentication-flow` | Silver | done | done | `qs_audit.py` `rule_reauthentication_flow` | value=1; async_step_reauth present |
| `test-coverage` | Silver | done | done, keyed to the wrong predicate | `coverage_gap.py` | 59 of 64 modules can fall to 0 % with the per-PR ratchet green — **finding D10-01** |
| `devices` | Gold | done | done | `qs_audit.py` `rule_devices` | value=0; entities with no DeviceInfo; distinct devices=1 |
| `diagnostics` | Gold | done | done | `qs_audit.py` `rule_diagnostics` | value=1; async_get_config_entry_diagnostics present |
| `discovery` | Gold | exempt | exempt | discovery-mechanism probe | 0 discovery sites, 0 discovery keys in manifest.json |
| `discovery-update-info` | Gold | exempt | exempt | discovery-mechanism probe | same basis as discovery |
| `docs-data-update` | Gold | done | done | `qs_audit.py` `rule_docs_data_update` | value=0; README heading lookup, 0 missing |
| `docs-examples` | Gold | done | done | `qs_audit.py` `rule_docs_examples` | value=3; three blueprints, set-equal in blueprints/automation/, README.md and docs/automations.md |
| `docs-known-limitations` | Gold | done | done | `qs_audit.py` `rule_docs_known_limitations` | value=0; README heading lookup, 0 missing |
| `docs-supported-devices` | Gold | done | done | `qs_audit.py` `rule_docs_supported_devices` | value=0; README heading lookup, 0 missing |
| `docs-supported-functions` | Gold | done | done | `qs_audit.py` `rule_docs_supported_functions` | value=0; README heading lookup, 0 missing |
| `docs-troubleshooting` | Gold | done | done | `qs_audit.py` `rule_docs_troubleshooting` | value=0; README heading lookup, 0 missing |
| `docs-use-cases` | Gold | done | done | `qs_audit.py` `rule_docs_use_cases` | value=0; README heading lookup, 0 missing |
| `dynamic-devices` | Gold | exempt | exempt | `qs_audit.py` `rule_dynamic_devices` | value=0; device-registry create sites |
| `entity-category` | Gold | done | done | `qs_audit.py` `rule_entity_category` | value=74; a judgement rule, no counterexample found |
| `entity-device-class` | Gold | done | done | device-class probe | 30 of 30 unit-bearing sensor classes carry a device_class |
| `entity-disabled-by-default` | Gold | done | done | `qs_audit.py` `rule_entity_disabled_by_default` | value=19; 19 of 74 entities disabled by default, each marked in README |
| `entity-translations` | Gold | done | done | `qs_audit.py` `rule_entity_translations` | value=0; entities whose translation_key has no strings.json['entity'] name |
| `exception-translations` | Gold | done | done | `qs_audit.py` `rule_exception_translations` + raise-site cross-check | value=21; 21 raised keys <-> 21 exceptions entries, bijection |
| `icon-translations` | Gold | done | done | `qs_audit.py` `rule_icon_translations` | value=0; no orphan entity icons; 102 icon entries |
| `reconfiguration-flow` | Gold | done | done | `qs_audit.py` `rule_reconfiguration_flow` | value=1; async_step_reconfigure present |
| `repair-issues` | Gold | done | done | `qs_audit.py` `rule_repair_issues` | value=1; async_create_fix_flow=True; async_create_issue sites=1 |
| `stale-devices` | Gold | exempt | exempt | `qs_audit.py` `rule_stale_devices` | value=0; device-registry removal/update sites |
| `async-dependency` | Platinum | done | done | `qs_audit.py` `rule_async_dependency` | value=3; sync CPU libs run via async_add_executor_job / process pool |
| `inject-websession` | Platinum | done | done | `qs_audit.py` `rule_inject_websession` | value=0; own aiohttp.ClientSession constructions: [] |
| `strict-typing` | Platinum | done | unmeasured (keyed) | `qs_audit.py` `rule_strict_typing` | value=0; source lane type_ignores=0; census errors=0 recorded at d8c47a7b02be |

### Minimum HA release for `todo` rules

**No rule is `todo` and no rule was found to belong there, so no rule needs an HA API newer
than the floor.** `hacs.json` pins `"homeassistant": "2025.2.0"`; nothing in this table is
gated on a release above it. The two rows whose HA surface is newest both clear it:
`async-dependency` uses `async_add_executor_job` / the import executor (long predates 2025.2)
and `inject-websession` uses `async_get_clientsession` (6 sites, 0 owned sessions). The 4
`exempt` rows depend on no HA API at all.

### The four rows no tree-local walk decides

| row | why the walk cannot see it | where its key lives | state at baseline |
|---|---|---|---|
| `config-flow-test-coverage` | needs a coverage run | tests/coverage_budgets.json:config_flow_percent_floor = 100.0, read by tests/coverage_ratchet.py:read_module_percent | holds; the module read is real (1 of 1 named module) |
| `test-coverage` | needs a coverage run | tests/coverage_budgets.json:package_percent_floor = 96.0, read by tests/coverage_ratchet.py:read_coverage | holds for the aggregate; **does not measure the rule** — D10-01 |
| `docs-examples` | the listing is a forum post, not a tree | the register's comment carries the resolving /t/<slug>/<id> URL; tests/entities.py pins it as a literal and checks the in-tree half | holds; the URL resolves (HTTP 200, checked this round) |
| `strict-typing` | needs mypy under a pinned toolchain | tests/typing_budgets.json:census (errors 0, by_code {}), recorded_at d8c47a7b02be; checked only by CI's typing job | holds as recorded; see Non-findings |

## Finding

### D10-01 — the Silver `test-coverage` row is keyed to a package aggregate: one module measures below the rule's 95 % bar and the per-pull-request check is green

- **Severity**: medium. No runtime behaviour is wrong; what is wrong is a `done` claim and the
  instrument that is supposed to defend it. A judge may prefer high on the ground that a
  value-bearing quality-scale row is factually false at the baseline — that is the stronger
  reading and it is not disputed here.
- **Stop-rule class**: hygiene
- **Claim**: the evidence chain the register's Silver `test-coverage` row is keyed to —
  `tests/coverage_budgets.json:package_percent_floor` (96.0) read by
  `tests/coverage_ratchet.py:read_coverage`, plus a per-module read applied to `config_flow.py`
  alone — cannot see a module fall below the rule's per-module 95 % bar. 59 of the package's 64
  modules are in that blind set, and `custom_components/heatpump_optimizer/sysid.py` is below the
  bar at the baseline: **94.62 %** (492/520 statements, 28 missed) against a green check.
- **Instrumented symbol**: `tests/coverage_ratchet.py:read_coverage` (the aggregate read) and
  `tests/coverage_ratchet.py:read_module_percent` (the one per-module read, applied to
  `config_flow.py` only). `tests/entities.py`'s check *"the register's test-coverage row agrees
  with the recorded coverage floor"* is the pin: it encodes `done iff package_percent_floor >=
  95.0`, so the pin cannot see the difference either.
- **Metric definition**: (a) the number of production modules whose complete loss (every
  statement uncovered) leaves `tests/coverage_ratchet.py` exiting 0; (b) the number of modules
  whose measured coverage is below 95 %.
- **Mechanism**: the instrument's only whole-package number is a ratio. A single module of `s`
  statements, zeroed, leaves the ratio at or above a floor `f` iff `s <= total * (1 - f/100)`. At
  the baseline `total = 16873` statements (the real payload; 16912 from `coverage.parser`) and
  `f = 96.0`, so the headroom is 674.9 statements and every module at or below that size is
  invisible to the aggregate — `sysid.py` at 520 statements among them. The rule's bar is per
  module, so `s/total` is irrelevant to it. The register's own comment on the row states the bar
  correctly ("The Silver rule asks that every module clear its bar") and then names the aggregate
  as the standing record.
- **Evidence**: `value=59`, unit `modules` (the blind set), with `1` module measured below the bar.
  - `RESULT modules=64 count`, `RESULT aggregate_headroom_statements=674.9 count`,
    `RESULT modules_blind_to_aggregate_floor=59 count` — **identical (59) from the synthetic
    payload built by `coverage.parser`, from the real `coverage_tree.sh fast` payload, and from
    the combined fast+e2e payload** (`combined 19 scripts, 5 coverage files`), which is the
    robustness check: the count does not depend on the instrument that produced the statement
    counts, nor on the stage set.
  - `RESULT modules_below_silver_bar=1 count`, emitting
    `below_bar: custom_components/heatpump_optimizer/sysid.py 94.62 % (492/520, 28 missed)` on the
    real payload — the rule broken, from the same command that counts the blind set. On the
    synthetic payload this reads `modules_below_silver_bar=0` (every module is 100 % there), so
    the below-bar number is a property of the payload, not of the harness.
  - The real payload: `custom_components/heatpump_optimizer/sysid.py` at
    `percent_covered=94.62`, `covered_lines=492`, `num_statements=520`, 28 lines missed, every one
    of them an error or refusal path (`except np.linalg.LinAlgError:` at 541-543 / 1090-1091 /
    1221, `return None` at 578 and 969, `SysIdResult(completed=False, ...)` at 593/595/600/1052,
    the not-armed early-out at 679-681, `continue` at 1032 and 1128). Package coverage over the
    same payload is 97.55 %.
  - **`strict-typing`-grade caveat, answered, and then taken**: is 94.62 % the honest number for
    the rule, or is it missing the e2e and stress stages? The combined fast+e2e payload was
    measured (`coverage_tree.sh` over `validate`, `edge`, `backtest`, `optimality`), and every
    number is unchanged — `package_statements=16873`, `modules=64`, `modules_blind=59`,
    `modules_below_silver_bar=1`, `sysid.py` still 94.62 % (492/520). The reason is structural, not
    luck: `custom_components/heatpump_optimizer/sysid.py` is imported by exactly one production
    module — `coordinator.py:361` (grep over every module) — and `tests/stress.py` imports only
    `optimizer`, `pv`, `dhw_schedule`, `presets` and `thermal_model`, while the four e2e scripts
    (`validate`, `edge`, `backtest`, `optimality`) import only `thermal_model`, `optimizer` and
    `dhw_schedule`. None of them can execute a statement of `sysid.py`, so the fast stage is the
    complete script set for that module and 94.62 % is final, not a partial reading.
  - The blind set includes `sysid.py` (520 statements, 3.082 % of the package), `const.py` (532,
    3.153 %), `price_model.py` (352, 2.086 %), `dhw_schedule.py` (308, 1.825 %), `tariff.py` (291,
    1.725 %), `wood_fuel.py` (280, 1.659 %), `inputs.py` (273, 1.618 %), `away.py` (278, 1.648 %),
    `services.py` (269, 1.594 %), `legionella.py` (260, 1.541 %) … down to `currency.py` (5, 0.030 %).
  - **Null control**: zeroing the largest module moves the check red —
    `RESULT ratchet_exit_zeroing_custom_components_heatpump_optimizer_coordinator_py=1 exit` (the
    same payload with `coordinator.py` zeroed fails at `package coverage 77.36 % >= 96.0 %`).
    Zeroing `currency.py` leaves it green:
    `RESULT ratchet_exit_zeroing_custom_components_heatpump_optimizer_currency_py=0 exit` with the
    instrument printing `ok package coverage 99.97 % >= 96.0 %` while that module is at 0 %.
- **Perturbation**: set the floor to 100.0 (`--floor 100`, the harness's knob, which is the same
  knob `package_percent_floor` is). Expected direction: `to_zero`. **Observed**:
  `RESULT modules_blind_to_aggregate_floor=0` (from 59), with
  `RESULT aggregate_headroom_statements=0.0`.
- **Reproduction**:
  ```
  cd /Users/timmalmstrom/audit-r6-baseline
  PYTHONPATH=tests/hastub python3 tools/audit/round6/D10/coverage_gap.py             # 59 blind
  PYTHONPATH=tests/hastub python3 tools/audit/round6/D10/coverage_gap.py --floor 100 # 0 blind
  W5P_WORK=$(mktemp -d) bash tools/audit/w5-partition/coverage_tree.sh fast          # ~15 min
  PYTHONPATH=tests/hastub python3 tools/audit/round6/D10/coverage_gap.py \
      --coverage $W5P_WORK/out/coverage.json   # 59 blind / 1 below bar; sysid.py 94.62 %
  # the combined fast+e2e payload gives the identical numbers (19 scripts, 5 files)
  ```
- **Files**: `tests/coverage_ratchet.py`, `tests/coverage_budgets.json`,
  `custom_components/heatpump_optimizer/quality_scale.yaml` (`test-coverage`),
  `tests/entities.py` (the `test-coverage` pin), `tools/audit/round4/D10/qs_rules.py` (reports the
  row `unmeasured`), `custom_components/heatpump_optimizer/sysid.py` (the module below the bar).
- **Proposed fix scope**: two halves, and they are separable. (1) The row. Either record a
  per-module floor and have `coverage_ratchet.py` read it for every module under
  `custom_components/heatpump_optimizer` — which is what the rule asks, and which turns
  `sysid.py`'s 94.62 % into a red check — or re-word the row so it names the aggregate as its
  record and states that the rule's per-module bar waits on a per-module measurement. (2) The
  28 missed statements in `sysid.py`, which are all reachable refusals and error paths; covering
  them, or recording deliberately that a defensive branch is unreachable and paying the pragma
  budget for it, is what makes the row's `done` true on the honest reading. Scope: one budget
  key, one reader in `coverage_ratchet.py`, the two sentences in `tests/entities.py`'s pin, and
  the `sysid.py` test additions.

#### Why this is a finding and not a note

The register's row is *honest* about the record it names — it names the floor, and
`tests/entities.py` pins the row to that floor. What fails is the predicate: the rule's bar is
per module and the record is a package ratio, so the row reads `done` while `sysid.py` violates
the rule, and no executed check in this tree distinguishes the two cases (`qs_rules.py` reports
the row `unmeasured`). The live demonstration is the real payload: `sysid.py` at 94.62 %,
`tests/coverage_ratchet.py` exiting 0, and `tests/entities.py`'s pin reading `96.0 >= 95.0` →
`done`. The synthetic arm shows the same defect without needing a coverage run at all: zero
`currency.py` and the check still exits 0.

## Non-findings (checked and held)

| # | suspected defect | command / instrument | executed value |
|---|---|---|---|
| 1 | an exception raised without a translation | AST: every Call whose callee ends in Error with a literal translation_key, vs strings.json['exceptions'] | 21 raised keys, 21 entries, raised_keys_without_exceptions_entry=0, exceptions_entries_never_raised=0 — an exact bijection |
| 2 | a repair issue whose text a user cannot read | AST: translation_key on repair/issue calls vs strings.json['issues'] | 15 call-site keys, all present in 19 entries; issue_keys_without_issues_entry=0 |
| 3 | an entity icon pinned in code instead of icons.json | grep -rho '_attr_icon' custom_components/heatpump_optimizer/*.py \| wc -l | 0; icons.json carries 102 entries under 'entity' |
| 4 | an entity with no translation_key name in strings.json | `qs_audit.py` `rule_entity_translations` | 0 offenders over 74 collected entities |
| 5 | an entity with no icon and no device class to fall back on | `qs_audit.py` `rule_icon_translations` | 0 offenders over 74 |
| 6 | a platform file that forgets PARALLEL_UPDATES | `qs_audit.py` `rule_parallel_updates` + per-file probe | 0 modules missing it; sensor 0, binary_sensor 0, button 1, climate 1, datetime 1, switch 1 |
| 7 | an entity that stays available after a failed poll | `qs_audit.py` `rule_entity_unavailable` | 0 offenders |
| 8 | the "log once, not per poll" rule drifting into log spam | `qs_audit.py` `rule_log_when_unavailable` | 4 latch definitions: _tibber_fetch_failed/_tibber_fetch_recovered and _weather_fetch_failed/_weather_fetch_recovered |
| 9 | a sensor with a unit but no device_class | AST over sensor.py | 30 of 30 unit-bearing classes carry one; 0 canonically-mapped units unset |
| 10 | the `discovery` exemption being wishful | grep for 12 discovery/async_step_* mechanisms + manifest keys | 0 sites, 0 keys — the exemption's stated basis holds |
| 11 | the `dynamic-devices` / `stale-devices` exemptions being wishful | `qs_audit.py` `rule_dynamic_devices`, `rule_stale_devices` | 0 device-registry create sites; 0 removal/update sites |
| 12 | entities shipping disabled by default and undocumented | 19 disabled-by-default classes vs README.md | each is marked inline ("Disabled by default; …") — README lines 490-549 |
| 13 | strings/en/sv drift | key-for-key comparison | identical, 1780 keys each, 21 exception keys |
| 14 | `docs-examples`' second half (the Exchange listing) being dead | HTTP GET on the pinned URL | 200 |
| 15 | the manifest's declared tier not matching the register | tests/entities.py's cumulative derivation + `qs_rules.py` | declared_mismatch=0; my walk disagrees on 0 of 48 |
| 16 | a py.typed marker owed by the Platinum `strict-typing` rule | find for the marker + the rule page | marker absent. The rule's requirement sentence is the runtime-data one and the py.typed sentence sits under "we recommend"; the enforcement mechanism it names (.strict-typing) is core-only. The register's "the marker-file half does not apply to a custom integration" is a judgement, and a defensible one — not filed |
| 17 | `strict-typing`'s census being measured at a commit other than the baseline | tests/typing_budgets.json:census.recorded_at | d8c47a7b02be… != e336cc2c…. That is what a ratchet record is; the source lane was re-measured this round: type_ignores=0 |
| 18 | `brands`' "adapted check for a custom integration" hiding missing assets | PNG header + sha256 of brand/*.png | both present; both 256x256 and byte-identical (8b92b5f1…). The rule asks for "a brand image" and both files exist, so it holds; the square logo is cosmetic (HA renders logo.png in a wide slot), not a quality-scale rule |

| 19 | coverage being measured against the wrong predicate only in principle, with every module actually clear of the bar | `coverage_tree.sh fast` + `coverage_gap.py --coverage` | **does not hold**: `sysid.py` 94.62 % (492/520, 28 missed), the only module below 95 %; package 97.55 % |

## Harnesses

- `tools/audit/round6/D10/qs_audit.py` — 48 executed rule verdicts, 0 disagreements with the
  register. `RESULT rules_checked=48`, `RESULT rules_disagreeing=0`.
- `tools/audit/round6/D10/coverage_gap.py` — the D10-01 instrument. Emits both numbers from one
  command: `RESULT modules_blind_to_aggregate_floor` (the blind spot) and
  `RESULT modules_below_silver_bar` (the rule already broken, with the offending module on the
  next line). `--floor` is the perturbation knob; `--coverage <path>` accepts a real payload and
  cross-checks its per-module statement counts against `coverage.parser`.
- Cross-checked against `tools/audit/round4/D10/qs_rules.py` (pre-existing, executed on every
  pull request by `tests/harness_headers.py`): `rules_total=54`, `declared_mismatch=0`.
- `tools/audit/round6/D10/quality_scale.draft.yaml` — the register as this audit would write
  it: 54 rows, statuses identical to the shipped register, differing in exactly one comment.

Wall-clock, CPU and load figures: **provisional** — the box is shared with other audit
dimensions. `load1` was 11.44 / 12.87 / 13.84 across the three runs. Every number above is a
count, a ratio or an exit code, so none of them moves with contention.

## Exposure

This dimension's sources are the integration, the test suite, the docs and the public HA
quality-scale pages. No earlier audit record in this export was read (none exists in it), no
`gh` invocation was made, and no GitHub issue, pull request or comment was consulted. The
`quality_scale.yaml` comments cite earlier rounds' issue numbers (#189, #195, #216, #217, #218,
#303, #951) — those were read as claims to test against execution, not as evidence for this
report. `docs/HANDOVER.md`, `docs/audit-2026-09.md` and the round-3/4/5 harness directories
were not opened except where named above (`tools/audit/round4/D10/qs_rules.py`, which is
executed by the tree's own gate).

## Unfinished / what this audit could not measure

1. **A full `stage=all` payload including stress.** The combined fast+e2e payload *was* taken
   before the audit closed (19 scripts, 5 coverage files) and every number is identical to the
   fast-only payload — `package_statements=16873`, `modules=64`, `modules_blind=59`,
   `modules_below_silver_bar=1`, `sysid.py` 94.62 % (492/520). `stage=all` still adds the stress
   stage, which this audit did not run. This does not weaken the finding: `sysid.py` is imported
   by `coordinator.py` alone, and `tests/stress.py` imports only `optimizer`, `pv`, `dhw_schedule`,
   `presets` and `thermal_model`, so no remaining stage can execute a statement of the module that
   is below the bar. A `stage=all` run is still worth taking before the finding is fixed, because
   the aggregate it reports is the number the register's row names.
2. **The 8-file statement-count drift** between the real payload's `num_statements` and
   `coverage.parser`'s (`__init__.py` 123 vs 126, `optimizer.py` 2001 vs 2017, `config_flow.py`
   950 vs 955, `coordinator.py` 3824 vs 3829, `inputs.py` 273 vs 279, `sensor.py` 1166 vs 1168,
   `away.py` 278 vs 279, `boost.py` 123 vs 124; totals 16873 vs 16912, 0.23 %). Not material —
   the blind-set count is 59 either way — but it means a flake8-style statement count is not a
   coverage statement count, and `coverage_gap.py --coverage` prints it rather than hiding it.
3. **`entity-category` is a judgement rule**; this audit only counted (74 entities reached).
   No executable counterexample was found and none is claimed.
4. **`entity-device-class` is measured on class attributes only.** If any sensor receives its
   unit from the descriptor table rather than a class attribute, that sensor is outside the
   probe. 30 unit-bearing classes were reached, all with a device_class.
5. **`strict-typing`'s census was not re-measured** — no mypy with the pinned toolchain on this
   box. The source-only lane was re-measured (type_ignores=0); the census is still the record
   from d8c47a7b02be.
