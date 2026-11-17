# D10-s3 report: audit round 11, D10 platinum cells (steps M1 and M2)

Baseline is `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, measured in `<HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline`. Two low-severity findings: the `strict-typing: done` row is false at two places. Both steps cover all 114 cells, so `unfinished` is empty. The harness refuses report .md files from sub-seats, so this text is the REPORT.md. Its `report_path` is `dev/audit/rounds/round11/D10/s3/REPORT.md`.

## Method

- **Rules fetched (2026-11-16):** the current checklist (54 rules: 20 bronze, 10 silver, 21 gold, 3 platinum), plus the rule pages for `async-dependency`, `inject-websession`, `strict-typing` and `runtime-data`. Platinum has three rules: async-dependency, inject-websession and strict-typing.
- **Cells:** `check_scopes.py --seat D10-s3` prints 114 lines (`M1+M2 platinum <file>`), and the harness examines all 114:
  - **Python files:** an AST check per file for each rule:
    - session construction sites
    - blocking network-library imports
    - whether the entry points listed on the runtime-data page take the typed config entry
  - **Runtime check:** whether each in-package `DataUpdateCoordinator` subclass annotates `config_entry`.
  - **`manifest.json`:** is each requirement typed? It counts as typed if the installed distribution has `py.typed`, if a `types-`/`-stubs` package is installed or pinned in `tests/requirements-typing.txt`, or, with `--pinned`, if the pinned wheel has `py.typed`.
  - **`quality_scale.yaml`:** platinum rows present.
  - **Other files** (png, json, yaml, js): no platinum rule applies to them.
- **Harness:** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s3/platinum_rules.py [--perturb req|row|coord|session|entry] [--pinned]`
- **Redispatched C1** (gold docs-* and entity-* rules): the orchestrator says D10-s2, which holds the gold cells, examined it this round. It is recorded under M1's `redispatched` as `examined` by D10-s2; this seat did not re-measure it. Its "rule pages not fetched" half is done here for the platinum pages.

## Findings

**D10-s3-01 (low, bug, step D10.M1, class I5).** `strict-typing` reads `done`, but the manifest requirement `threadpoolctl` has no `py.typed` and no stub package.
- **Rule broken:** the rule allows no exceptions. Its page says "Its library must be typed as well, and ship a py.typed file", and hassfest checks that "every requirement in its manifest must ship a py.typed file, or have a separate types- stubs package".
- **Evidence:** threadpoolctl 3.7.0 (installed) and 3.8.0 (the version the typing lock pins, checked by downloading its wheel) have neither.
- **Why the row is wrong:** its comment counts the integration's own `py.typed` (`qs_py_typed_files=1`) as meeting this half of the rule. `optimizer.py:1447` already says threadpoolctl "publishes no py.typed and no stub distribution exists".
- **Consequence:** `tests/entities.py` derives the manifest's `quality_scale: platinum` from these rows. It fails D10-criteria Q2.
- **Metric:** `untyped_requirements_under_done_row` is 1 at baseline.
  - `--perturb req` (threadpoolctl dropped in memory) gives 0.
  - `--perturb row` (row read as `todo`) gives 0.
- **Not affected:** numpy ships `py.typed`, and scipy is covered by `scipy-stubs==1.18.1.1` in the typing lock.

**D10-s3-02 (low, hygiene, step D10.M1, class new).** `HeatPumpOptimizerCoordinator` has no `config_entry: HeatPumpOptimizerConfigEntry` annotation.
- **What happens:** the coordinator takes the typed entry (`coordinator.py:3514`) and passes `config_entry=entry` (`:3536`), but never annotates the attribute. So `config_entry` stays the base class's bare `ConfigEntry | None`, and `:7022` reads it through `getattr`.
- **Rule broken:** the strict-typing page says to use the typed entry everywhere, and the runtime-data page says "A coordinator that gets the config entry should use the typed entry too" (pylint check `home-assistant-coordinator-untyped-config-entry`).
- **Why the row is wrong:** the row's comment says every attribute annotation is typed. The census behind it, `qs_entry_param_bare`, counts parameters only.
- **Metric:** `coordinator_untyped_under_done_row` is 1 (1 of 1 subclasses). `--perturb coord` (annotation patched in) gives 0, and `--perturb row` gives 0.

Both findings report exact counts that do not depend on machine load. The box was at load1 147–260 and `thread_factor` was 1.000.

## M2: platinum tier table

| rule | tier | status | evidence command | result |
|---|---|---|---|---|
| async-dependency | platinum | exempt (row says done) | `platinum_rules.py \| grep BLOCKING` | `blocking_io_imports=0`; all HTTP is awaited aiohttp; the requirements do no I/O, which is the page's exception |
| inject-websession | platinum | done | `platinum_rules.py` (control `--perturb session` gives 1) | `unshared_http_sessions=0`; Tibber, Open-Meteo and the config flow all use `async_get_clientsession` |
| strict-typing | platinum | todo | `platinum_rules.py [--pinned]` | `untyped_requirements=1` (threadpoolctl); coordinator untyped 1; `entry_point_bare=0` |

- The draft register is `dev/audit/rounds/round11/D10/s3/quality_scale.draft.yaml`: 54 rows, bronze to gold unchanged, platinum as above.
- No `todo` rule needs a Home Assistant API newer than the `hacs.json` floor of 2025.2.0, so no minimum release applies.

## Non-findings (checks that passed)

- **Q1:** all 3 platinum rules have a row (`platinum_rows_missing=0`).
- **inject-websession:** 0 sites build their own session; the control perturbation gives 1.
- **async-dependency:** 0 blocking network imports. Executor jobs are CPU solves and local file I/O.
- **Typed entry points:** all 12 entry-point parameters use the typed entry (`entry_point_bare=0`; the control gives 1). These are the 4 in `__init__`, 6 platform `async_setup_entry`, diagnostics and the options flow.
- **Requirements:** scipy (through scipy-stubs) and numpy count as typed.

## Harnesses

`dev/audit/rounds/round11/D10/s3/platinum_rules.py`

## Leads

- **D10-s1, `coordinator.py:HeatPumpOptimizerCoordinator`:** the bronze `runtime-data` page names the same pylint check, so that row may also be affected.
- **D10-s1, mypy --strict (D10.M3):** the per-category mypy count was not measured here, because M3 is D10-s1's cell.

## Unfinished and exposure

Both are empty.

Files are in `<HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D10/s3/`:
- `REPORT.json`
- `findings/D10-s3-01.json`
- `findings/D10-s3-02.json`
- `platinum_rules.py`
- `quality_scale.draft.yaml`