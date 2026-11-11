# D10 finder seat D10-s2 — audit round 9

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, export `/home/claude/audit-r9-baseline`,
4-CPU Linux cloud container shared with other seats (load1 4.2–5.0 during the fan-out),
Python 3.14.0rc2, `PYTHONPATH=tests/hastub`, BLAS pinned to 1 thread.

Cells: D10.M1 + D10.M2 on the Gold and Platinum axis (all files); D10.M3 (all tiers, all files).

## Method

* Rule texts fetched from `raw.githubusercontent.com/home-assistant/developers.home-assistant/master/docs/core/integration-quality-scale/rules/<rule>.md`
  (the developers.home-assistant.io host is refused by the proxy with 403). HA core's
  `homeassistant/components/climate/strings.json` fetched from `home-assistant/core@dev` for the
  standard preset set.
* M1: one executed check per Gold and Platinum rule, all in `gold_platinum_rules.py`, driving the
  real `async_setup_entry` of every platform in `const.PLATFORMS` (75 entities, coordinator built by
  `tests/golden.py:_capture_coordinator(coord_all_features)`), the real diagnostics handler with a
  secret token / free-text name / 6-decimal location, AST censuses of raise sites, issue sites and
  annotations, and documentation lookups over `README.md` + `docs/**/*.md`.
* M2: the tier table below and the draft `quality_scale.yaml` in this directory.
* M3: `coverage_modules.py` runs every fast-stage gate script (the list `tests/run.sh` yields,
  derived exactly as `tools/audit/w5-partition/coverage_tree.sh` does, which is what the CI coverage
  job runs) under coverage.py in its own process, combines, and reports per module (statement, and
  branch as a separately named number). `mypy_census.py` runs `mypy --strict` in two arms: the
  brief's literal "stub on the path" and the pinned real toolchain of `tests/typing_budgets.json`.

## Findings

### D10-s2-01 — climate presets `auto` and `economy` can be neither translated nor iconed (medium, bug)

`climate.py:HeatPumpOptimizerClimate` publishes `preset_modes = [auto, comfort, economy, boost]`.
Home Assistant's climate component translates and icons only its eight standard presets (`none, eco,
away, boost, comfort, home, sleep, activity` — `climate/const.py` PRESET_*, identical to the key set of
core `climate/strings.json` `entity_component._.state_attributes.preset_mode.state`). A non-standard
preset is translatable only under `entity.climate.<translation_key>.state_attributes.preset_mode.state`,
and the entity has no `translation_key` (it is the device's main feature, `_attr_name = None`), and
neither `strings.json`, `translations/{en,sv}.json` nor `icons.json` has an `entity.climate` section.
So every install's climate card shows the raw tokens `auto` and `economy` beside the translated
"Comfort"/"Boost" (Swedish: "Komfort"/"Boost"), with no icon, while the register's
`entity-translations` and `icon-translations` rows say `done`.

* Harness: `tools/audit/round9/D10/s2/climate_presets.py`
* Command: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s2/climate_presets.py`
* Result: `untranslated_presets_en=2`, `untranslated_presets_sv=2`, `uniconed_presets=2` (auto, economy);
  driving the coordinator to mode `economy` publishes `preset_mode='economy'`.
* Perturbation: `--perturb eco` (in-memory rename economy -> HA-standard `eco`) -> 1 (down);
  `--perturb translate` (translation_key + preset_mode state tables in memory) -> 0 (to_zero).
* Count key: the entity's own `preset_modes` as built by `climate.async_setup_entry`, checked against
  the translation tables the frontend would read; a fix that adds a translation_key and tables moves it.
* Property: every enumerated value the integration publishes into a climate state attribute that HA
  translates (preset_mode, and hvac/fan/swing modes if ever added) is either an HA-standard constant or
  translated in every shipped language and iconed under the entity's translation_key.
* Minimum HA release: none newer than the `hacs.json` floor (2025.2.0) is needed — entity
  translation keys with `state_attributes` tables and `icons.json` both predate it.

## Tier table (Gold, Platinum; plus the two M3 rows)

All numbers from `gold_platinum_rules.py` (exact counts) unless named otherwise.

| rule | tier | status | evidence check | result |
|---|---|---|---|---|
| devices | gold | done | distinct device identifier sets over 75 entities; DeviceInfo fields; entry_type | 1 device, 0 missing fields, entry_type service |
| diagnostics | gold | done | real handler with secret token, name, 59.334591/18.063240 | 0 leaks (coords published at 1 dp); `--perturb diag` -> 1 |
| discovery | gold | exempt | manifest discovery keys + async_step_<discovery> | 0; iot_class cloud_polling |
| discovery-update-info | gold | exempt | same | 0 |
| docs-data-update | gold | done | README states "30 minutes by default" == DEFAULT_OPTIMIZATION_INTERVAL | match |
| docs-examples | gold | done (partial verify) | 3 blueprints, README link, service + default entity refs resolve | 0 dangling; exchange listing unreachable (403) |
| docs-known-limitations | gold | done | README heading | present |
| docs-supported-devices | gold | done | README "Supported heat pumps and controls" | present |
| docs-supported-functions | gold | done | 74 entity names + 12 services looked up in README/docs | 0 undocumented |
| docs-troubleshooting | gold | done | README heading | present |
| docs-use-cases | gold | done | README "What it does" | present |
| dynamic-devices | gold | exempt | device-registry create/update/remove sites | 0 |
| entity-category | gold | done | census | 21 diagnostic, 54 none (primary controls/readings) |
| entity-device-class | gold | done | sensors with a unit but no device class | 14, each carrying a recorded reason (MONETARY/ENERGY state-class table, unit price, temperature deltas) |
| entity-disabled-by-default | gold | done | census | 11 disabled by default |
| entity-translations | gold | **todo** | translation_key + name in strings/en/sv; ENUM state tables; climate presets | 0 entity gaps; **2 climate presets untranslatable (D10-s2-01)** |
| exception-translations | gold | done | AST census of HA-exception raise sites | 0 without key, 0 key missing in a language, 0 placeholder mismatches |
| icon-translations | gold | **todo** | icons.json per translated entity; `_attr_icon` pins; climate presets | 0 / 0 / **2 presets uniconed (D10-s2-01)**; `--perturb icon` -> 1 |
| reconfiguration-flow | gold | done | config flow class has async_step_reconfigure | 0 missing |
| repair-issues | gold | done | literal issue keys present in strings/en/sv | 0 missing |
| stale-devices | gold | exempt | removal sites | 0 |
| async-dependency | platinum | done | sync HTTP imports; requirements are numpy/scipy/threadpoolctl | 0 |
| inject-websession | platinum | done | own ClientSession constructions vs async_get_clientsession sites | 0 own, 3 shared |
| strict-typing | platinum | done | py.typed; type ignores; bare ConfigEntry; mypy --strict (real stubs) | present / 0 / 0 / 0 errors |
| test-coverage | silver (M3) | done | coverage_modules.py | min module 95.12 % (diagnostics.py), 0 modules <= 95 % |

## M3 numbers

`coverage_modules.py --branch` (17 scripts; 4 exited non-zero in this export for reasons outside
coverage: `features` (the documented tracer-vs-timing pair), `entities` (git/lease/handover checks in a
tree with no `.git`), `deployment_shape` (needs `git ls-files`), `golden` (strict fixture comparison on
this BLAS). Their lines up to the exit still count, so the percentages are a lower bound on CI's):

* package statement coverage 97.98 %, min module 95.12 % (`diagnostics.py`, 2 of 41 missed),
  next `accuracy.py` 95.85, `button.py` 95.92, `sysid.py` 95.98; 0 modules at or below 95 %.
* branch coverage (informational: the rule text asks for "test coverage" and names no branch measure):
  package 93.87 %, 25 modules at or below 95 %.

`mypy_census.py`:

* real arm (homeassistant-stubs 2026.9.3 + homeassistant 2026.9.3 `--no-deps`, scipy-stubs, mypy 2.3.1):
  0 errors under the package; `--inject` (one untyped function + one bad assignment in a temp copy) -> 2.
* stub arm (the brief's literal "stub on the path"): 355 package errors — no-untyped-call 181,
  attr-defined 129, assignment 11, no-any-return 8, untyped-decorator 8, operator 6, return-value 4,
  arg-type 3, type-arg 2, import-not-found 1, import-untyped 1, name-defined 1 — plus 85 in
  `tests/hastub` itself. These are the stub's own missing annotations and missing symbols, not the
  integration's: the same package is clean against the real stubs. The ruler (`tests/typing_ruler.py`)
  strips `PYTHONPATH`/`MYPYPATH` for exactly this reason. Recorded as a non-finding; the brief's M3
  wording ("with the stub on the path") yields an instrument number, which is worth correcting in the
  D10 brief (propagation note, not an issue).

## Non-findings

See `report.json` `non_findings`; each carries its command and value.

## Leads (outside the rule cells, no harness)

* `sensor.py:SolarIrradianceSensor.extra_state_attributes` merges
  `open_meteo.py:OpenMeteoSolar.diagnostics()` which publishes `latitude`/`longitude` rounded to 5
  decimals (~1 m) as recorded state attributes, while `diagnostics.py` coarsens the same coordinates to
  1 decimal as a privacy control. Owner unknown (privacy of published attributes is not a
  quality-scale rule).
* `icons.json` has no `services` section for the 12 services in `services.yaml`; hassfest requires
  service icons for core integrations only, so this is not a quality-scale rule for a custom one.

## Unfinished

* D10.M1 docs-examples: the Blueprints Exchange half (the forum listing) could not be fetched — the
  proxy refuses community.home-assistant.io (403); only the in-tree half was verified.
* D10.M3: the coverage perturbation (`--drop config_flow_steps`) was not executed; the M3 result is a
  non-finding, so no finding rests on it.

## Exposure

No file under `tools/audit/round3..round8` was read. Earlier-round finding ids were seen incidentally
in: `custom_components/heatpump_optimizer/quality_scale.yaml` comments (read for the rule register),
`tests/coverage_budgets.json` `reason`, `tools/audit/bugclasses.json` `instances` (read for
class_guess), and code comments (`diagnostics.py`, `coordinator.py`). None is cited as evidence.
`README.md` and `docs/**/*.md` were read for the docs-* rules.

## Harnesses

* `tools/audit/round9/D10/s2/gold_platinum_rules.py` — M1/M2, one check per Gold/Platinum rule.
* `tools/audit/round9/D10/s2/climate_presets.py` — D10-s2-01.
* `tools/audit/round9/D10/s2/coverage_modules.py` — M3 test-coverage (about 11 min wall on this box).
* `tools/audit/round9/D10/s2/mypy_census.py` — M3 strict-typing (installs the pinned stubs into a temp
  target unless `--target` names an existing one).
