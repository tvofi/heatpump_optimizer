# D6 round 4 — verifier seat 1 report (panel D6-0)

Worktree `../audit-r4-verify-D6-1`, detached at `0855277` (branch head of
`claude/13-dimension-audit-920935`). Finder's baseline was `7dd68dd`;
`git diff --stat 7dd68dd..HEAD -- custom_components/` shows only version
bumps (`manifest.json` 6.4.2 → 6.4.3, `www/heatpump-optimizer-card.js`
`CARD_VERSION` ditto). `docs/architecture.md`, `docs/automations.md`,
`README.md`, `sensor.py`, `coordinator.py`, `config_flow.py`, `switch.py`,
`binary_sensor.py` are byte-identical to baseline, so the baseline numbers
apply to this tree — and every number below was re-measured on this tree
regardless.

All harnesses, the finder's and mine, resolve the root from the working
directory and were run from this worktree's root with
`PYTHONPATH=tests/hastub`, so they measured this tree. No timing number
anywhere: every figure is a count or a set comparison, contention-immune.
`load1` ranged 3.86–12.17 across my runs (other agents on the box); quoted,
not gated, and immaterial to counts.

## D6-01 — architecture.md stale in ten claims, including the HA boundary (high, hygiene)

**Vote: verify (severity high).**

### Finder's harness re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/ha_boundary.py`

    RESULT modules_total=56 modules            (finder: 56)
    RESULT documented_ha_modules=11 modules    (finder: 11)
    RESULT ha_free_import_failures=21 modules  (finder: 21)
    RESULT undocumented_ha_dependents=11 modules (finder: 11)
    load1=11.60

Exact match, tolerance 0. Perturbation arm (`HPO_D6_PERTURB=1`):
`ha_free_import_failures` 21 → 22, `undocumented_ha_dependents` 11 → 12 —
moves in the stated direction.

`claims.py --links` also reproduced its header exactly (125/125/112/12/0/1,
arch 56/45/11, ha 21, 76/76; load1=9.73); the perturbation arm (no `--links`,
so 111 true / 12 false at rest) moved to 110 true / 13 false as stated.

### My own harness

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/d6_own_D6-01.py`
(written by me; static method, deliberately different from the finder's
dynamic import probe):

    RESULT arch_ha_importers_static=21 modules     (AST scan of DIRECT module-level imports)
    RESULT arch_ha_importers_dynamic=21 modules    (my own refusal-import, real tree)
    RESULT arch_doc_claim=10 modules
    RESULT undocumented_ha_dependents=11 modules
    RESULT arch_modules_on_disk=56 modules         (doc says 45)
    RESULT arch_map_listed=45 / arch_map_missing=11 (no phantoms)
    RESULT option_pages=21 pages                   (doc says 13)
    RESULT services_registered=12 services         (doc says 11; via the honest FakeServices registry)
    RESULT switch_entities=4 switches              (doc names 1)
    RESULT binary_sensor_entities=5 binary_sensors (doc names 4)
    RESULT entity_platforms=6 platforms            (datetime is a sixth)

Metric definition: *the number of .py files under
`custom_components/heatpump_optimizer/` with at least one module-scope
`import homeassistant`/`from homeassistant...` node in their AST* — exactly
the assertion architecture.md:140 makes. My 21 and the finder's 21 are the
same *set*, member for member:

    static == dynamic == {__init__, away, binary_sensor, boost, button,
    climate, config_flow, coordinator, currency, datetime, dhw_learning,
    diagnostics, entity, frontend, legionella, open_meteo, repairs, sensor,
    services, setpoint_check, switch}

The eleven outside the doc's ten are the same eleven the finder names.
Independently confirmed from `services.yaml` (12 top-level keys parsed with
yaml), from `_OPTION_PAGES` by import (21), and the doc sentences themselves
read verbatim (architecture.md lines 8, 61–135, 140–144).

### Attacks

1. **Method substitution (static vs dynamic).** The finder imports each
   module with `homeassistant` refused — a dynamic measure that would also
   fail on a module that merely imports an in-package HA-dependent module.
   My AST scan of *direct* module-level imports returns the identical 21-member
   set, so no transitivity inflation: every failing module itself imports
   HA at module level. The doc's "exactly ten ... at module level" is false
   under either instrument.
2. **The `documented_ha_modules=11` quirk.** The finder's regex counts
   `inputs` as documented (from the following sentence). Conservative — it
   can only shrink `undocumented_ha_dependents`, which is 11 anyway. I read
   the regex and the doc; agreed.
3. **The doc's second half** ("one module outside that set touches it at
   all: `inputs`, inside a function") is still true — `inputs.py:328` is a
   function-level lazy import. So the paragraph is not wholly wrong; the
   "exactly ten" and "everything else is free" halves are, which is what the
   finding claims.
4. **Reachability/stub.** None of these numbers touch the stub; they are
   tree facts.
5. **Severity.** COMMON.md: `high` = "a user-visible defect or a wrong
   published value". Ten wrong published values in one file, including the
   boundary claim the file exists to make. Counterargument noted for the
   judge: architecture.md addresses contributors, not users, so a
   consequence-only reading of the scale would say medium; the
   "wrong published value" arm is literal and I did not weaken on it.

## D6-02 — Sensor-Gap Euro Advisor documented as CUR, publishes no unit (medium, bug)

**Vote: verify (severity medium).**

### Finder's harness re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/currency_unit.py`

    RESULT sensors_constructed=59 sensors       (finder: 59)
    RESULT currency_rows_documented=9 rows      (finder: 9)
    RESULT currency_rows_without_unit=1 rows    (finder: 1)
    RESULT currency_sensors_with_unit=8 rows    (finder: 8)
    load1=11.00 — offender: 'Sensor-Gap Euro Advisor', unit=None, native_value=0.0

Exact match. Perturbation arm: without-unit 1 → 0, with-unit 8 → 9 — moves
as stated.

### My own harness

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/d6_own_D6-02.py`
(written by me):

    RESULT cur_rows=9 rows                      (independent row-oriented README parse)
    RESULT cur_rows_unitless=1 rows
    RESULT cur_rows_with_unit=8 rows
    RESULT advisor_unit=None
    RESULT advisor_native_value=0.0
    RESULT coordinator_currency='SEK'

Metric definition: *sensors whose README Unit column is exactly `CUR` whose
entity's `native_unit_of_measurement` PROPERTY (not the `_attr`) is None,
over the entities the real `sensor.async_setup_entry` constructs*. Reading
the property matters: a device class or subclass could still supply a unit
and rescue the sensor. It does not — `device_class=None`, the base
`HeatPumpOptimizerSensorBase.__init__` sets no unit, and
`SensorGapAdvisorSensor` (sensor.py:2563-2601) never assigns
`_attr_native_unit_of_measurement`, while the six other monetary sensors do
(`coordinator.currency` at sensor.py lines 487, 510, 573, 589, 1247, 1790).
The eight other CUR sensors all answered `'SEK'` through the property — the
contrast control holds and the finding's "the one" is right.

`topology.rank_sensor_gaps` (topology.py:650-709) returns
`sek_per_month` rows; the sensor's `native_value` is the top gap's value, so
it publishes money-per-month as a bare float. The entity is enabled by
default (no `entity_registry_enabled_default = False`; README says
"Diagnostic" only), name confirmed in `strings.json` ("Sensor-Gap Euro
Advisor").

### Attacks

1. **Property vs attribute** — run; the HA-level property is what I read.
2. **Stub artefact** — the missing unit is a class-level fact of production
   code, independent of the stub. In real HA
   `SensorEntity.native_unit_of_measurement` returns the `_attr`, i.e. None.
   One stub gap noted for the record: `tests/hastub` defines no
   `state_class` property at all, so my property read of `state_class` came
   back None; the finder's `_attr_state_class = MEASUREMENT` read is the
   correct one (real HA's property returns it). In real HA a MEASUREMENT
   sensor with no unit still gets long-term statistics recorded with a NULL
   unit, so "recorded unitless" holds.
3. **Workaround exists** (the `gaps` attribute carries the per-slot values),
   user-visible defect → medium per the scale. Not inflated, not deflated.

## D6-03 — automations.md Power Headroom precondition not enforced (low, hygiene)

**Vote: verify (severity low).**

### Finder's harness re-run

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/headroom_availability.py`

    RESULT cells=4 cells                    (finder: 4)
    RESULT available_cells=3 cells          (finder: 3)
    RESULT available_without_a_fuse=1 cells (finder: 1)
    RESULT predicted_by_the_doc=2 cells
    load1=11.00 — "no fuse, capacity tariff": available=True value=0.0,
    limit_source='capacity tariff with no peak reference yet'

Exact match, cell for cell. Perturbation arm (tariff off in the fuse-less
cell): available_cells 3 → 2, available_without_a_fuse 1 → 0 — moves as
stated.

### My own harness

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/d6_own_D6-03.py`
(written by me; the entity is constructed on the SAME real coordinator with
`coordinator.data` populated by a real `_build_data_dict()`, no
FakeCoordinator in between):

    RESULT doc_sentence_found=1 bool  ("It stays unavailable until you set a main fuse size in the options")
    RESULT cells=4 cells
    RESULT available_cells=3 cells
    RESULT available_without_a_fuse=1 cells
    RESULT default_main_fuse_a=0 A
    RESULT default_peak_tariff_enabled=False bool

Metric definition: *cells of (main fuse 0/20 A) × (capacity tariff off/on)
in which the constructed power_headroom entity's `available` is True; the
doc's sentence predicts only the two fuse cells*.

### Attacks

1. **Real-HA reachability.** The tariff toggle lives on the `grid` options
   page, the fuse on `grid_connection` (config_flow.py:1511 vs 1520); no
   cross-field validation forces a fuse when the tariff is on; the fuse
   defaults to 0 (`const.py:391`). The falsifying cell is one toggle away
   from defaults. The coordinator's own comment (coordinator.py, the
   `elif tariff.enabled ...` branch of `_power_headroom`) documents exactly
   this install population and calls the 0.0 answer deliberate — the doc was
   not updated with it.
2. **Metering-window accident?** No: `tariff.py:122-138` — with no masks
   (the default tariff config) `sample_factor` is 1.0 at all times, so the
   fuse-less tariff cell is continuously available at 0.0 kW, not
   window-bound. The finder's "first metering window of every month"
   phrasing actually understates the exposure.
3. **Grid artefact / drop-cell.** Each cell is individually reported; the
   single fuse-less tariff cell alone falsifies the sentence. No aggregate
   to artefact.
4. **Honest near-refute.** My first run returned available=False in all four
   cells — because I had not populated `coordinator.data` (the entity reads
   the publish payload, and a coordinator that has never completed a
   refresh has none). The finder's harness feeds the entity a
   `_build_data_dict()` payload too, produced by the real coordinator. With
   the payload produced, the numbers reproduce. Recorded so the next seat
   does not mistake that failure for a refute.
5. **Severity.** Documentation-only; no wrong money, no wrong comfort; the
   `limit_source` attribute discloses the branch. Low per the scale.

## Summary

| id | vote | severity | my number vs finder's |
|---|---|---|---|
| D6-01 | verify | high | 21 HA importers (static AST, own) = 21 (finder, dynamic); 11 undocumented; 56/45/11 module map; 21 vs 13 option pages; 12 vs 11 services; 4 switches; 5 binary sensors; 6 platforms |
| D6-02 | verify | medium | 1 of 9 CUR rows unitless (own, via the HA property) = finder's 1; other 8 publish SEK |
| D6-03 | verify | low | 3 of 4 cells available, 1 without a fuse (own, entity on the real coordinator) = finder's 3/1 |

No timing-based evidence anywhere; nothing provisional. All three findings
survived a method substitution (static vs dynamic import; property vs
attribute; same-coordinator vs FakeCoordinator construction).
