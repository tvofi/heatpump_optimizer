# D10 — Home Assistant integration quality scale, round 7

**Dimension:** D10 — adherence to the Home Assistant integration platinum
quality-scale requirements (54 rules).
**Baseline:** `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave fully
merged), exported (no `.git`) at `~/audit-r7-baseline`.
**Machine:** darwin 25.6.0 arm64, 8-core Apple M1, 8 GB, Python 3.11.5, mypy
2.3.1. **No wall/CPU/RSS figure is reported by either harness** — every number
below is a count or a parse of deterministic output, so each is final under
fan-out contention.

## Method, and what it can and cannot decide

One executed check per rule, from `tools/audit/round7/D10/qs_rules_r7.py` — an
AST or text read over the integration for the code rules, a documentation
lookup for the docs rules, and the fetched rule pages under `/tmp/harules/`
(54 pages, zero 404, fetched 2026-09-23) as the deciding text. The
`strict-typing` rule is additionally checked by its named checker in
`tools/audit/round7/D10/mypy_strict.py` (`mypy --strict`, stub on the path,
counted by diagnostic code).

The register under test is the in-tree
`custom_components/heatpump_optimizer/quality_scale.yaml` (54 rows, header
"Totals: 50 done (2 vacuous) · 4 exempt · 0 todo"). `quality_scale.draft.yaml`
in this directory is the same register with the one row this audit overturns
flipped, and each overturned number carried in a comment.

### The network horizon (stated, not hidden)

The `brands` rule's requirement source is the external `home-assistant/brands`
repository's own README; the assignment forbids reading GitHub, so the rule's
*requirement text* could not be fetched. The check therefore reports the tree's
brand artefacts as measured facts and does not rule on them (see non-findings).
Every other rule's text was fetched to `/tmp/harules/*.md` and read.

## Tier table (all 54 rules; `register` = the in-tree claim)

| rule | tier | register | executed check | result |
|---|---|---|---|---|
| action-setup | bronze | done | ok | 12 registrations, services.yaml 12 keys, strings.json 12 keys, symmetric difference [] |
| appropriate-polling | bronze | done | ok | coordinator sets update_interval from the configured interval |
| brands | bronze | done | ok | brand/icon.png (256, 256), brand/logo.png present, logo byte-identical to icon: True |
| common-modules | bronze | done | ok | entity.py/coordinator.py/const.py: ['entity', 'coordinator', 'const'] |
| config-flow | bronze | done | ok | HeatPumpOptimizerConfigFlow with VERSION and async_step_user |
| config-flow-test-coverage | bronze | done | ok | config_flow.py 100.0 % (floor 100.0) |
| dependency-transparency | bronze | done | ok | 3 requirements, all version-constrained: ['numpy>=1.24.0', 'scipy>=1.10.0', 'threadpoolctl>=3.5.0'] |
| docs-actions | bronze | done | ok | 12/12 services named in both README.md and docs/configuration.md (undefined: []); README carries '## Services' |
| docs-triggers | bronze | done | ok | 0 triggers defined — vacuous |
| docs-conditions | bronze | done | ok | 0 conditions defined — vacuous |
| docs-high-level-description | bronze | done | ok | README.md carries '## What it does' |
| docs-installation-instructions | bronze | done | ok | README.md carries '### HACS (recommended)' |
| docs-removal-instructions | bronze | done | ok | README.md carries '### Removal' |
| entity-event-setup | bronze | done | ok | 0 async_track_* in the platform modules (the coordinator's two subscriptions are not entities) |
| entity-unique-id | bronze | done | ok | 0 entities without a unique id |
| has-entity-name | bronze | done | ok | 0 entities without has_entity_name |
| runtime-data | bronze | done | ok | entry.runtime_data assigned in async_setup_entry; 0 hass.data[DOMAIN]-shaped reads |
| test-before-configure | bronze | done | ok | config_flow calls async_get_clientsession and probes the price API before creating the entry |
| test-before-setup | bronze | done | ok | async_setup_entry awaits async_config_entry_first_refresh(); the rule's own note admits that as the implicit implementation (explicit raise sites: 0) |
| unique-config-entry | bronze | done | ok | the flow calls async_set_unique_id and aborts on _abort_if_unique_id_configured() |
| action-exceptions | silver | done | ok | 20 typed raises across 12 handlers |
| config-entry-unloading | silver | done | ok | async_unload_entry unloads the platforms and shuts the coordinator down |
| docs-configuration-parameters | silver | done | ok | README.md carries the post-setup settings section |
| docs-installation-parameters | silver | done | ok | README.md documents the setup wizard; docs/setup.md exists |
| entity-unavailable | silver | done | ok | 17 entity `available` overrides, 0 omit super().available ([]); the base is CoordinatorEntity |
| integration-owner | silver | done | ok | codeowners=['@tvofi'] |
| log-when-unavailable | silver | done | ok | coordinator latches the outage (first failure logged once, recovery logged once) via _tibber_fetch_failed/_tibber_fetch_recovered |
| parallel-updates | silver | done | ok | every platform declares PARALLEL_UPDATES ([]) |
| reauthentication-flow | silver | done | ok | async_step_reauth exists; strings.json declares ['reauth_confirm'] and ['reauth_successful'] |
| test-coverage | silver | done | ok | package 97.49 % (floor 96.0); per-module min 95.3 % ignoring the export artifact |
| devices | gold | done | ok | one DeviceInfo on the coordinator with identifiers/name/manufacturer/model |
| diagnostics | gold | done | ok | async_get_config_entry_diagnostics redacts via async_redact_data |
| discovery | gold | exempt | ok | exempt: 0 discovery-mechanism imports |
| discovery-update-info | gold | exempt | ok | exempt: same basis as discovery |
| docs-data-update | gold | done | ok | README.md 'How it works' documents the update/poll cycle |
| docs-examples | gold | done | ok | 3 blueprints in blueprints/automation, linked from README |
| docs-known-limitations | gold | done | ok | README.md carries '## Known limitations' |
| docs-supported-devices | gold | done | ok | README.md carries '## Supported heat pumps and controls' |
| docs-supported-functions | gold | done | ok | README.md carries '## What it does' |
| docs-troubleshooting | gold | done | ok | README.md carries '## Troubleshooting' |
| docs-use-cases | gold | done | ok | README.md carries '## What it does' |
| dynamic-devices | gold | exempt | ok | exempt: 0 device-registry mutation sites |
| entity-category | gold | done | ok | 20 entities carry EntityCategory.DIAGNOSTIC; the README entity tables mark 20 rows diagnostic; 0 carry EntityCategory.CONFIG |
| entity-device-class | gold | done | ok | sensor.py declares 11 distinct device classes |
| entity-disabled-by-default | gold | done | ok | the noisy/diagnostic entities are disabled by default |
| entity-translations | gold | done | ok | 74 entities, 1 device-named, 0 unnamed without a translation key, 0 keys absent from strings.json |
| exception-translations | gold | done | ok | 21/21 user-facing raises carry translation_domain+translation_key, 0 keys absent from strings.json |
| icon-translations | gold | done | ok | 0 _attr_icon pins, 0 entity keys absent from icons.json |
| reconfiguration-flow | gold | done | ok | async_step_reconfigure exists and writes back to the entry |
| repair-issues | gold | done | ok | 19 declared issue/translation keys named at 19 create sites, 0 named-but-undeclared; async_create_fix_flow implemented |
| stale-devices | gold | exempt | ok | exempt: device lifetime == entry lifetime |
| async-dependency | platinum | done | ok | the blocking numpy/scipy solve runs in a subprocess reached through async_add_executor_job; the network dependency is HA's aiohttp |
| inject-websession | platinum | done | ok | 3 async_get_clientsession calls, 0 direct ClientSession constructions |
| strict-typing | platinum | **done → todo** | **FAIL** | py.typed absent; 88/98 `entry` params typed bare `ConfigEntry` — **findings D10-01, D10-02** |

`strict-typing` is the only row this audit overturns. Everything else the
register claims is confirmed by execution.

## Coverage (`test-coverage`, `config-flow-test-coverage`)

Measured with the repo's own instrument,
`W5P_WORK=/tmp/d10r7/cov tools/audit/w5-partition/coverage_tree.sh fast` --
the exact invocation `tests/coverage_ratchet.py` documents in its header --
combined per module over the 15 default-gate `fast` scripts (65 package
modules, 16990 statements). Floors from `tests/coverage_budgets.json`.

| figure | measured | floor | verdict |
|---|---|---|---|
| package | **97.49 %** | 96.0 (at ceiling) | ok |
| config_flow.py | **100.0 %** | 100.0 | ok |
| per-module min, export | **70.27 %** (`diagnostics.py`) | 95.0 | **REFUTED — export artifact** |
| per-module min, excluding that | **95.3 %** (`sysid.py`) | 95.0 | ok |

`tests/coverage_ratchet.py --coverage .../coverage.json` prints
`COVERAGE RATCHET BREACHED` at this baseline, naming `diagnostics.py: 70.27 %`.
It is **not** a finding — it is the export. `tests/entities.py` dies at line
15312 (`FileNotFoundError: tools/audit/round4/D6/claims.json`, absent from an
export with no `.git`), and its D10-12 diagnostics block, which calls
`async_get_config_entry_diagnostics` over a nested-coordinate fixture, sits at
line 17620 -- after the crash. So in an export no script reaches the module's
coarsening branches and every one reads as missed.

`tools/audit/round7/D10/diag_export_control.py` runs the same entrypoint over
the same fixture shape in isolation, under the `coverage` library:

    RESULT diag_control_pct=100.00 percent
    RESULT diag_control_missing_lines=0 count
    RESULT diag_reported_in_export=70.27 percent

100.00 % isolated against 70.27 % in the export settles the cause: the module
is fully exercised when its test block runs, and the breach is the crash.
`test-coverage` (97.49 % package, every module >= 95 % once the artifact is
subtracted) and `config-flow-test-coverage` (100.0 %) are both **confirmed
done**, and the register's floors are correctly keyed to the tiers
(module_percent_floor 95.0 for the silver bar, config_flow_percent_floor 100.0
for the bronze bar).


## Findings

### D10-01 — `py.typed` is absent, and the register's stated basis is not in the rule

**severity: medium · stop_rule_class: hygiene**

The `strict-typing` rule text (fetched `/tmp/harules/strict-typing.md`) says,
in the Rule section, *"you need to add a `py.typed` file to your library"*, and
its Exceptions section says *"There are no exceptions to this rule."* The
integration ships no `py.typed` file anywhere in the package. The register
marks the row `done` with the comment *"py.typed is not owed — the Platinum
rule's marker-file half does not apply to a custom integration."* That carve-out
does not appear in the rule text, in the Exceptions section, or in the rule's
warning box — it is invented. The code half of the rule is separately violated
(D10-02).

Executed number: `qs_py_typed_files=0`. Perturbation `--perturb py-typed`
(creates the file in a scratch copy) moves it `0 -> 1`.

Corroboration from the rule's named checker: adding `py.typed` alone leaves
`mypy_total` at 441 (the marker does not silence anything by itself, which is
why both halves of the rule are separate findings).

**proposed_fix_scope:** ship an empty
`custom_components/heatpump_optimizer/py.typed`, and change the register row's
comment to the executed number rather than the unsupported exemption.

### D10-02 — the custom typed config entry is not "used throughout"

**severity: high · stop_rule_class: hygiene**

The rule's warning box says: *"If the integration implements `runtime-data`,
the use of a custom typed `MyIntegrationConfigEntry` is required and must be
used throughout."* The integration does implement `runtime-data`
(`entry.runtime_data` is assigned in `async_setup_entry`), and it does define
the custom alias (`HeatPumpOptimizerConfigEntry`), but of the 100 `entry`
parameters in the package only 10 use it; **88 are bare `ConfigEntry`**. That
is the opposite of "throughout".

Two independent instruments agree:

* `qs_entry_param_bare=88`, `qs_entry_param_custom=10`,
  `qs_entry_param_other=2`. Perturbation `--perturb entry-alias` rewrites every
  bare `entry: ConfigEntry` to the alias (all three spellings) and drives
  `qs_entry_param_bare 88 -> 0` / `qs_entry_param_custom 10 -> 98` — a clean
  positive control, so the predicate can go green and is not dead.
* `mypy --strict` counts 95 `[type-arg]` diagnostics ("Missing type arguments
  for generic type"). `--perturb entry-alias` drives that slice `95 -> 7`; the
  88 that vanish are exactly the 88 bare parameters. The non-strict null
  control drops it to 0, showing the diagnostic is strictly a strict-mode one.

The first is a shape count; the second is the rule's own named checker
reporting the same defect. Both move under the same perturbation.

**proposed_fix_scope:** type every `entry` parameter with the alias across the
six platform modules and `config_flow.py`; the alias already exists, so the
change is mechanical — 88 annotation sites. Re-run `mypy_strict.py` after, and
expect `mypy_type_arg` to fall to single digits.

## Non-findings (checked, held, with the executed number)

| claim ruled non-finding | command | value |
|---|---|---|
| every service is documented in README and docs/configuration.md | `qs_rules_r7.py` | `qs_services_undocumented=0`, `qs_services_registered=12` |
| every entity carries a translation key or is device-named | `qs_rules_r7.py` | `qs_entities_without_tk=0` |
| every user-facing exception is translatable | `qs_rules_r7.py` | `qs_user_facing_raises_keyed=21` of 21 |
| every repair issue is declared and used | `qs_rules_r7.py` | `qs_issue_keys_undeclared=0`, `qs_issue_keys_named=19` |
| the diagnostic-entity count matches the README tables | `qs_rules_r7.py` | `qs_entity_category_diagnostic=20` == `qs_readme_diagnostic_rows=20` |
| no entity pins a hard-coded icon instead of a translation | `qs_rules_r7.py` | `qs_attr_icon_pins=0` |
| no direct `ClientSession` construction | `qs_rules_r7.py` | `qs_direct_clientsession_sites=0` |
| `test-before-setup`'s basis is in the rule text, not a shortcut | `/tmp/harules/test-before-setup.md` | the rule's own info box admits `async_config_entry_first_refresh()` |
| coverage floors are correctly keyed to the tiers (95 / 100 / 96) | `tests/coverage_budgets.json` | module 95.0 / config_flow 100.0 / package 96.0 |

Also examined and found not to be defects:

* **`brands` — logo byte-identical to icon** (both 98834 B, 256x256). Unusual
  (HA's brands repo normally ships a wider logo), but the requirement source is
  the external brands README, which the assignment forbids reading. Recorded as
  an observation with its numbers, not ruled on. A stray root-level `icon.png`
  (512x512, 377596 B) also exists, outside `brand/`; HA loads only `brand/`, so
  it is inert.
* **`entity-device-class`** — 11 distinct classes; the SEK-denominated
  measurement sensors correctly carry no `MONETARY` class (that class requires
  `TOTAL` state class, which a current-value sensor must not have).
* **`entity-category`** — 0 entities carry `EntityCategory.CONFIG`; the 20
  diagnostic ones and 20 README rows agree.
* **`entity-disabled-by-default`** — 19 entities are disabled by default (8
  diagnostic + 11 ordinary measurements the README documents as "Disabled by
  default"). Documented, not silent.
* **`repair-issues`** — an earlier ruler reported `declared-never-created=4`;
  that was the ruler's blind spot (a conditional `translation_key` value, a
  per-entity f-string id, and two ids passed through `_set_issue`), not a
  register defect. The ruler was redefined to `named` / `undeclared` /
  `dynamic` and now reads `named=19, undeclared=0, dynamic=1`.

## Harnesses

* `tools/audit/round7/D10/qs_rules_r7.py` — one executed check per rule
  (54), the tier table, and 12 perturbations.
* `tools/audit/round7/D10/mypy_strict.py` — the `strict-typing` rule's named
  checker (`mypy --strict`) counted by diagnostic code, with a non-strict null
  control and two perturbations.
* `tools/audit/round7/D10/diag_export_control.py` — the export control that
  refutes the `diagnostics.py` coverage breach (`diag_control_pct=100.00`).

## Instrument limits, honestly

* The export crashes `tests/entities.py` (line 15312, stripped
  `tools/audit/round4/D6/claims.json`) and `tests/deployment_shape.py`
  (`git ls-files`, no `.git`). Neither is a D10 finding; both are artifacts of
  an export without its history and both still contribute their executed
  coverage lines.
* `tests/features.py` reports 1/3099 under coverage (the #525 heartbeat pair);
  the instrument's own header documents this as "the tracer removes the stall",
  so it is not read as a regression.
* mypy's raw 441 is dominated by the `tests/hastub` stub's incompleteness
  (51 `has no attribute "hass"`, 174 `no-untyped-call` mostly against HA's own
  selector/`dt` helpers). Only the `[type-arg]` slice is attributable to the
  integration, and it is the slice the rule's warning names.
* No min-HA-release note is owed: the register has 0 `todo` rules, and the two
  strict-typing defects need no API newer than the `hacs.json` floor.
