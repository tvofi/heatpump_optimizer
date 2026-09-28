# D6 — README and documentation claim verification (round 4)

Baseline `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`, measured in the read-only
export at `.claude/worktrees/audit-r4-baseline`. Machine: 8-core Apple M1,
8 GB, macOS 25.6.0, `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`
(3.11.5), `PYTHONPATH=tests/hastub`, thread pin applied in every harness.

**Root rule.** All three harnesses resolve the repository root from the
**working directory** — `ROOT = pathlib.Path(".")` — and never from `__file__`.
Each refuses to run correctly anywhere but the repository root, which is how
`tools/audit/README.md`'s root-resolution trap is avoided. Copy them into the
tree under test and run them from its root.

## Method

1. **Extraction.** Every sentence carrying a number, a default, an entity or
   service name, a field, a unit, a stated behaviour, a version or a link was
   pulled from `README.md`, `DISCLAIMER.md`, `docs/architecture.md`,
   `docs/automations.md`, `docs/configuration.md`, `docs/dashboard-card.md`,
   `docs/ecl110.md`, `docs/how-it-works.md`, `custom_components/heatpump_optimizer/`
   `services.yaml`, `strings.json`, `translations/{en,sv}.json`, `manifest.json`
   and `hacs.json`. Claims that are one rule over many rows (a whole table
   column) are numbered once and checked over every row, with the row count in
   the result — `C30` alone compares 76 documented defaults and `C31` 76
   documented ranges.
2. **One executed check per claim.** Entity names, counts, units, categories,
   enabled-by-default flags and entity ids come from driving the real
   `async_setup_entry` of all six platforms. Defaults and ranges come from
   *rendering* every one of the 21 options pages through
   `HeatPumpOptimizerOptionsFlow.async_step_*` and reading the marker defaults
   and `NumberSelector` configs — not from `const.py` literals, so a default
   that `const.py` declares but the page never offers would still be caught.
   Service fields come from the voluptuous schemas, with every `services.yaml`
   `example` payload fed through its own schema. `supports_response` is
   captured by spying on `hass.services.async_register` during the real
   `services.async_register_services`. Behaviours are driven against real
   coordinators. Links are resolved on disk and with `curl -I -L`.
3. **The claims table** is emitted by the harness to
   `tools/audit/round4/D6/claims.md` and `claims.json`, never hand-assembled.

## Numbers

    RESULT claims_extracted=125
    RESULT claims_checked=125
    RESULT claims_true=112
    RESULT claims_false=12
    RESULT claims_stale=0
    RESULT claims_unverifiable=1
    RESULT config_defaults_compared=76
    RESULT config_ranges_compared=76
    RESULT arch_modules_on_disk=56
    RESULT arch_map_listed=45
    RESULT arch_map_missing=11
    RESULT ha_module_level_importers=21

`claims_stale=0` is meant literally: nothing found was *out of date but once
true in a way that still reads as true*; the twelve false claims are false
now, against this tree, and ten of them share one cause.

Command: `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py --links`
(without `--links` the external-link claim is `unverifiable`, so
`claims_unverifiable=2` and `claims_true=111`).

## Findings

### D6-01 — `docs/architecture.md` is stale in ten separate claims, including the Home Assistant boundary it exists to state (`high`)

Ten of the twelve false claims are in one file, and they share one cause:
nothing pins `docs/architecture.md`. `tests/entities.py` pins the README's
entity counts, service list, options-page count and requirement line against
the code; `docs/` is `INERT` to `tests/closure.py`, so architecture.md has
drifted as the package grew and no check noticed.

The load-bearing one is the boundary. The document says:

> Exactly ten modules import `homeassistant` at module level: `__init__`,
> `config_flow`, `coordinator`, `open_meteo`, `frontend`, and the five entity
> platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`.
> … Everything else is deliberately free of it, so each module can be driven
> directly by `tests/features.py` with no Home Assistant running.

Measured by *importing every module with `homeassistant` made unimportable*,
out of a scratch copy of the package whose `__init__.py` is emptied (so the
package's own import is not what fails every submodule):

    RESULT modules_total=56
    RESULT ha_free_import_failures=21
    RESULT undocumented_ha_dependents=11

Eleven modules — `away`, `boost`, `currency`, `datetime`, `dhw_learning`,
`diagnostics`, `entity`, `legionella`, `repairs`, `services`, `setpoint_check`
— import `homeassistant` at module level, are outside the ten the document
names, and cannot be imported without Home Assistant. `datetime.py` is a sixth
entity platform, absent from a list that calls itself "the five entity
platforms"; a static AST scan of module-level imports returns the same 21.

The other nine, each with the measured value:

| id | claim | measured |
|---|---|---|
| C32 | "45 modules" | 56 Python modules in the package |
| C33 | the module map is the package's module list | 11 absent: `boost.py`, `datetime.py`, `dhw_learning.py`, `diagnostics.py`, `entity.py`, `legionella.py`, `process_worker.py`, `repairs.py`, `services.py`, `setpoint_check.py`, `wood_fuel.py` |
| C29 | "config_flow.py … plus 13 option pages behind two menus" | `config_flow._OPTION_PAGES` holds **21**; README.md and configuration.md both say 21 |
| C37 | "__init__.py … the 11 services" | 12 |
| C38 | "services.yaml # The 11 service definitions" | 12 |
| C39 | "sensor.py # 59 sensors" | 59 — **true**, listed for contrast |
| C40 | "switch.py # Optimizer Active" | the platform constructs 4: Away, Boost Hot Water, Boost Space Heating, Optimizer Active |
| C41 | "binary_sensor.py # Input problem, open window, external heat, away mode" | the platform constructs 5; `Wood Cheaper Than Heat Pump` is unnamed |
| C34/C35/C36 | the boundary, above | 21 importers, 11 undocumented |

Severity `high`: this is the file a contributor reads before changing the code,
and the boundary claim is the one an author would rely on when deciding where
a new module may live. A wrong published value, per COMMON.md's scale.

### D6-02 — a monetary sensor the README documents in `CUR` publishes no unit at all (`medium`)

`README.md`'s sensor table states a unit for every sensor, with `CUR` meaning
the Home Assistant instance currency. Nine rows say `CUR`. Driving
`heatpump_optimizer.sensor:async_setup_entry` and reading each entity's
`native_unit_of_measurement`:

    RESULT sensors_constructed=59
    RESULT currency_rows_documented=9
    RESULT currency_rows_without_unit=1
    RESULT currency_sensors_with_unit=8

`SensorGapAdvisorSensor` ("Sensor-Gap Euro Advisor") is the one. It declares
`_attr_state_class = SensorStateClass.MEASUREMENT` and
`_attr_suggested_display_precision = 0`, publishes `native_value` in currency
per month (`topology.rank_sensor_gaps(...)["sek_per_month"]`), and never sets
`_attr_native_unit_of_measurement`. Every other monetary sensor in the file
sets `self._attr_native_unit_of_measurement = coordinator.currency` in its
`__init__` (lines 487, 510, 573, 589, 1247, 1790 of `sensor.py`). Measured with
`coordinator.currency == "SEK"`, the sensor still publishes
`unit=None, native_value=0.0`.

Consequence for a user: the figure renders as a bare number in the UI and in
its long-term statistics, with no currency and no conversion, while the README
and the entity's own English name ("Euro Advisor") both promise money.

Severity `medium`: a user-visible defect with an obvious workaround (read the
`gaps` attribute), and it is a published value that is wrong rather than
missing.

### D6-03 — `docs/automations.md` states a precondition for the Power Headroom sensor that the code does not enforce (`low`)

> The Power Headroom sensor … stays unavailable until you set a main fuse size
> in the options

Driving `HeatPumpOptimizerCoordinator._power_headroom` and the constructed
`power_headroom` sensor over the 2×2 grid (fuse set / not) × (capacity tariff
enabled / not):

    RESULT cells=4
    RESULT available_cells=3
    RESULT available_without_a_fuse=1
    RESULT predicted_by_the_doc=2

| cell | `available` | `limit_source` | value |
|---|---|---|---|
| no fuse, no tariff | False | — | None |
| **no fuse, capacity tariff** | **True** | `capacity tariff with no peak reference yet` | **0.0** |
| fuse, no tariff | True | `main fuse` | 13.8 |
| fuse, capacity tariff | True | `main fuse` | 13.8 |

The fuse is one of two sufficient conditions, not a necessary one. The
second cell is not a corner case: the main fuse defaults to `0`
(`const.DEFAULT_MAIN_FUSE_A`), so every install that enables the capacity
tariff and never fills in a fuse lands there, and the sensor is *available and
reads 0.0 kW* for the first metering window of every month — which an EV-charger
automation following the documented rule ("set a fuse and it appears") will
read as a real "no headroom" rather than as "not configured". The coordinator's
own comment at `coordinator.py:7528-7544` documents that branch deliberately;
the documentation was not updated with it.

Severity `low`: documentation-only, no wrong money and no wrong comfort, and the
sensor's own `limit_source` attribute says what happened.

## Non-findings — what was checked and held

The full table with a command and a result per row is
`tools/audit/round4/D6/claims.md`. The blocks worth naming:

- **The entity census (C1–C14).** README's `All 74 entities`, `Sensors (59
  total)`, `Binary Sensors (5 total)`, `Buttons (4 total)` and
  architecture.md's mermaid `74 / 59 / 5 / 4 / 4 / 1 / 1` all match the
  entities the six real `async_setup_entry` calls construct. The sensor table
  names **exactly** the 59 sensors the platform builds, the binary-sensor and
  button tables likewise. Every `Diagnostic` note is an
  `EntityCategory.DIAGNOSTIC`, every `disabled by default` note is an
  `entity_registry_enabled_default = False`, and the six named as disabled are
  the six that are.
- **Every documented default and every documented range (C30, C31).** 76
  defaults and 76 ranges in `docs/configuration.md`, matched to the fields by
  their `strings.json` label and compared against the options pages **as
  rendered**: zero mismatches. A perturbation that changes one documented
  default from `21.0 °C` to `22.0 °C` flips C30 to false, so the check is live.
- **Services (C15–C25).** 12 services in README, configuration.md and
  `services.yaml`; the README table is `services.yaml`'s key set; 28 fields on
  `set_thermal_parameters` and 16 on `simulate_plan`; seven schemas accept
  `entry_id`; `services.yaml` documents **exactly** the fields each voluptuous
  schema accepts (symmetric difference empty for all twelve); every
  `services.yaml` `example` payload passes its own schema; the README `Returns`
  column is each service's registered `SupportsResponse` (— = NONE, Always =
  ONLY, Optional = OPTIONAL); the 21 assignable keys listed in
  configuration.md are `topology.ASSIGNABLE_KEYS` exactly.
- **Options pages (C26–C28).** 21 pages in README and configuration.md, 6 on
  the first menu and 15 behind Advanced, all three derived from
  `config_flow._OPTION_PAGES` and `strings.json`'s menus.
- **Prose defaults (C49–C67).** target 21 °C, day 21 °C, night 19.5 °C,
  07:00–22:00, `06:00-08:30, 17:00-22:00`, legionella on at 60 °C / 7 days,
  3 %/m·s⁻¹ wind and 15 % rain, `comfort_weight` 5, 30-minute interval, 8
  weekly snapshots at 7-day spacing, 0.5 K/week curve creep, the 90th-percentile
  heavy day, 2-hour boost, 20-hour manual pins, 300 s minimum between frequency
  writes, 3 watchdog ticks, 2 agreeing peak-guard samples, economy 1.5 K / 15 °C
  floor, 40 °C mixed water, 10–95 % furnace efficiency.
- **`docs/ecl110.md` (C69–C81).** All eight option defaults; the eight settings
  are the eight non-navigation fields on the `heat_curve` page; the ON
  threshold really is `max(0.1, p.min_electrical_power * 0.5)`; the anticipation
  bias really covers `int(max(1, 8 / dt_hours))` steps; the published displace
  really is `int(round(...))`; comfort `min(4.0, max)`, boost `max`, off `min`;
  the peak guard's 2 °C nudge; both ECL110 sensors disabled-by-default and
  diagnostic.
- **`docs/how-it-works.md` "What the tests actually prove" (C90–C102).** All
  thirteen asserted properties — 25 % model error, the 5–35 °C runaway bound,
  3 degree-hours, the 0.5 K / 2 K settling pair, 1.6× daily cost, half rated
  power of first-step swing, the quartile comparison, 35 % learning error, >10
  samples, the 0.15 overshoot bound, 0.05 convergence spread, 0.12 drift over
  two days, 3 degree-hours of overshoot — are present verbatim in
  `tests/rolling.py`'s assertions. The document is careful to state that the
  breach comparison is a property, not a figure, and `rolling.py` asserts
  exactly that.
- **Links and ids (C107–C111).** 65 relative links resolve (bar the three
  export-removed ones, below); 9 embedded images exist; 10 external links
  answer `200` to `curl -I -L`; every one of the 9 entity ids quoted anywhere in
  the docs or in the card's `DEFAULTS` is an entity the platforms construct.
- **Translations (C112–C115, C125).** `translations/en.json` and
  `translations/sv.json` carry exactly `strings.json`'s key set, no key missing
  and none extra; every entity's display name resolves through the translations
  (the climate entity deliberately has none — it takes the device name); every
  `SelectSelector` option on every options page has a translated label.
- **Versions (C42–C48).** `manifest.json` version `6.4.2` equals `VERSION`;
  `hacs.json` floor `2025.2.0` equals the README badge and the README
  requirement line; `numpy` and `scipy` are in `requirements`.
- **The card (C85–C89).** The seven documented series keys are the card's
  `SERIES_DEFS` keys; `hours` defaults to 24 and is bounded `>0 … ≤168`;
  `what_if` and `show_stats` default true; the file carries no `import`,
  `require(` or CDN reference, so "no Chart.js, ApexCharts, npm or any CDN" holds.

### Disproved leads

- **`services.yaml` vs `set_thermal_parameters`'s 28 fields.** A first,
  regex-based read of `services.yaml` suggested three ECL110 fields were
  accepted by the schema but undocumented for the UI. Parsing the YAML properly
  shows all 28 documented. Harness gap, not a defect — recorded so the next
  auditor does not repeat it.
- **`Thermal Battery Charge`/`Energy` "unavailable when no store is sensed".**
  A sweep with an indoor thermometer configured showed both available and
  looked like a false note. `_MeasuredStoreMixin.available` gates on *at least
  one* store being sensed, and the house counts, so the note is right; with no
  thermometer at all both go unavailable (C104, measured). This is the shape my
  own notes call a predicate that over-fires: the check was written from the
  wording, not from the mechanism.
- **`services.yaml` number selectors vs the voluptuous `vol.Range`s.** 32
  fields have a narrower UI slider than the validator accepts. That is
  deliberate and documented — configuration.md says so in as many words ("the
  ranges below are the physics bounds rather than the UI's convenience
  sliders") — and the documented figures are the validator's, which is the
  honest half for an automation author. Not a finding.
- **Select-option lists in configuration.md.** Ten rows separate options with
  `/` instead of `·`, abbreviate a label, or order two options the other way
  round. Wording, and D5's dimension, not truth.

## Exposure

Audit-era documents opened, per the D6 brief's instruction to record them:

- `tools/audit/round4/BASELINE.md`, `tools/audit/briefs/COMMON.md`,
  `tools/audit/briefs/D6.md`, `tools/audit/README.md` — my own contract.
- `docs/` user documentation: `architecture.md`, `automations.md`,
  `configuration.md`, `dashboard-card.md`, `ecl110.md`, `how-it-works.md`.
  These are the dimension.
- **Not opened**: `docs/HANDOVER.md` and every `docs/plan-*.md`. They are
  present in the export (only `docs/audit-*.md` and `docs/backlog.md` were
  removed) and they carry issue numbers and judged verdicts, which COMMON.md's
  wall forbids. They are also development records rather than user
  documentation, so excluding them costs the dimension nothing. Their claims
  are therefore **unchecked**, and that is the largest hole in this report.
- No `gh`, no GitHub, no earlier round's findings. `tools/audit/round3/` is
  absent from the export. `tools/audit/round2/` is absent too; where
  `tests/entities.py` comments cite a `D6-nn` id, I read it as context and did
  not look it up.

## What I could not finish

1. **`docs/HANDOVER.md` and `docs/plan-*.md` are unchecked**, by the exposure
   decision above. ~3 800 lines of claims.
2. **`docs/backlog.md`, `docs/audit-2026-08.md` and `docs/audit-2026-09.md`
   are unchecked and unreachable.** Four links point at them from `README.md`
   and `docs/how-it-works.md`; the export removes exactly those files, so
   whether the links resolve on `main` is `unverifiable` here (C109). Do not
   read those four as broken links.
3. **`docs/dashboard-card.md` is checked only at its configuration surface.**
   Its 631 lines of interaction prose — the dashed-band rules, the pan/zoom
   window, the lane-editing limits, the keyboard map, the setup page — would
   need `tests/card_rig.mjs` and a Chromium run under `tests/card_browser.mjs`.
   D4 has the Chromium slot this round and COMMON.md says the Chromium finder
   does not sit beside the compute-heavy ones, so I did not take it. Roughly 40
   further claims live there.
4. **`tests/rolling.py` was not executed.** The thirteen "what the tests
   actually prove" claims are verified as *correspondences between the document
   and the assertions in the file*, by executed parse; whether those assertions
   pass on this box is a `SLOW=1` closed-loop run and is D3's dimension, not
   mine. A judge wanting the stronger form should run
   `SLOW=1 PYTHONPATH=tests/hastub python3 tests/rolling.py` in the quiet window.
5. **`RELEASE_NOTES.md` (379 KB) is unchecked.** Every release heading is a
   claim about what shipped; `tools/release/stamp.py` owns its rules and D11
   owns governance, so I left it.
6. **No timing claim was measured.** The documentation makes no performance
   statement I could find beyond "within one optimization interval", which is a
   configuration default (C57), not a measurement. Every number in this report
   is a count or a set comparison and is contention-immune; `load1` at the time
   of the final runs was 9.8–11.8 with the other finders on the box, and none of
   it touches these numbers.

## Harnesses

| path | what it measures | command |
|---|---|---|
| `tools/audit/round4/D6/claims.py` | the whole claims table, 125 claims | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py --links` |
| `tools/audit/round4/D6/ha_boundary.py` | modules that fail to import with `homeassistant` refused | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/ha_boundary.py` |
| `tools/audit/round4/D6/currency_unit.py` | `CUR`-documented sensors publishing no unit | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/currency_unit.py` |
| `tools/audit/round4/D6/headroom_availability.py` | Power Headroom availability over the 2×2 config grid | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/headroom_availability.py` |

Each carries `HPO_D6_PERTURB=1`, which applies its own perturbation **without
touching any file in the tree** (in-memory doc edits, a scratch copy of the
package, or a runtime monkeypatch), and each perturbation was run: the numbers
move in the stated direction.

Outputs: `tools/audit/round4/D6/claims.md` (the table) and `claims.json`.
