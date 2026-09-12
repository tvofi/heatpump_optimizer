# D8 — sensor verification and ordering (round 4)

- baseline: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- tree: the read-only export at
  `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline`
  (no `.git`); nothing under `custom_components/` or `tests/` was modified.
- interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub` (plus `/tmp/d8pkgs` for `orjson`), always
  from the export root.
- machine: 8-core Apple M1, 8 GB, shared with the D9 and D4 finders for the
  whole session. **Every number in this report is a count.** No timing, wall,
  CPU or RSS number is reported, so nothing here is contention-sensitive.
  `load1` is printed by each harness anyway and ran 2.9–8.1.

## Method

### The matrix

`tools/audit/round4/D8/entity_matrix.py` builds
**75 cells = 5 topologies × 15 feature overlays**:

- topologies: `tests/golden.py:coordinator_scenarios()` — `coord_minimal`,
  `coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`;
- overlays: `none`, `dhw`, `two_zone`, `valve_storage`, `two_tank`, `coil`,
  `wood`, `ecl110`, `pv`, `capacity_tariff`, `grid_fee`, `tuya`, `probes`,
  `away`, `all` (every overlay merged).

Each cell is a real `HeatPumpOptimizerCoordinator` over a `FakeHass` seeded
with 23 live input states (18 of them carrying the `unit_of_measurement` their
reader demands; the other 5 are read by paths that do not), 48 h of
Tibber-shaped prices, 48 h of weather and an irradiance series — the injection `tests/golden.py:_capture_coordinator` performs — then
`_update_current_state()`, **a real `async_run_optimization()` solve**, and
`_build_data_dict()` (164 published keys). The solve is the part
`_capture_coordinator` does not do, and it is not optional here: with
`--no-solve` the same matrix reports `never_alive_enabled_default = 20` and
`unknown_with_data = 75`, and with the solve 12 and 0 — eight enabled
entities publish nothing at all until a plan exists, so without the solve the
whole "is this entity permanently unknown where its data exists" question
is unanswerable.

**Every entity of every platform** is then constructed through the real
`async_setup_entry` for all six platforms in `const.PLATFORMS` — the same
mechanism as `tests/entities.py:collect` — giving **74 entities per cell** and
**5550 entity-cells**: 59 sensor, 5 binary_sensor, 4 button, 1 climate,
4 switch, 1 datetime.

Each cell runs **two cycles**: cycle 2 changes every input state, moves the
price offset 0.6→1.9 and the spread 0.5→2.4, the outdoor base −5 °C→+8 °C and
the irradiance peak 200→40, and advances the frozen clock by three hours.

### Mapping each entity to its source keys

Not by a hand table. `coordinator.data` is replaced with a `TrackingDict` that
records every key read while a property is evaluated, so an entity's source
keys are whatever it actually touched inside `native_value` on that cell.

### Per entity, per cell

`state` (through the stub's `SensorEntity.state`, which mirrors upstream's
three refusals), `available`, `device_class`, `state_class`, unit,
`entity_category`, `entity_id`, `options`, `translation_key`,
`_attr_entity_registry_enabled_default`, `extra_state_attributes`, and the
entity's recorded attribute bytes after `_unrecorded_attributes` is removed.

**A harness trap that made three checks vacuous before it was found, and which
the next auditor will hit too:** `tests/hastub`'s `SensorEntity` declares **no**
`device_class`, `state_class` or `entity_category` property. `getattr(ent,
"device_class")` therefore returns `None` for every entity in the tree, and the
first run of this harness reported `enum_state_not_in_options=0`,
`measurement_non_numeric=0`, `timestamp_naive=0` and
`unit_device_class_mismatch=0` for a reason that had nothing to do with the
code under test. The harness now reads `_attr_device_class` /
`_attr_state_class` / `_attr_entity_category` and falls back to the property
only where one exists. `entity_category_declared=1500` (20 of 74 entities × 75
cells) is the tell that the corrected read is live.

## Findings

Two, both `hygiene`, both `low`. The matrix's ten typed publication contracts
all came back clean — see Non-findings, which is the substance of this report.

### D8-01 — alphabetical order clusters two of seven entity families, and splits five

`name_order_intruders = 159` over 7 families and 74 entities
(`tools/audit/round4/D8/naming_order.py`). Per family, "intruders" is the count
of entities **not** in the family whose position in the globally sorted English
display-name list lies strictly between the family's first and last member:

| family | n | name intruders | name breaks | sensor-id intruders |
|---|---|---|---|---|
| `ecl110` | 2 | **0** | 0 | 0 |
| `pv` | 3 | **0** | 0 | 0 |
| `dhw` | 10 | 7 | 1 | 10 |
| `card_headline` | 5 | 18 | 4 | 13 |
| `accuracy` | 3 | 29 | 2 | 44 |
| `learning` | 5 | 45 | 3 | 28 |
| `tariff` | 7 | **60** | 4 | 49 |

The two families that score zero are exactly the two whose display names share
a literal prefix (`ECL110 …`, `Solar …`). `dhw` nearly scores zero — its one
break is `Boost Hot Water`, the only DHW entity not named `DHW …`. The five
that are split have no shared prefix, and the worst is the money family: the
seven entities a user compares against each other (`Baseline Cost`,
`Contract Comparison`, `Current Electricity Price`, `Monthly Peak Power`,
`Power Headroom`, `Predicted Cost`, `Total Heating Cost (lifetime)`) have 60 of
the other 67 entities interleaved between them, in four runs.

`card_headline` is the sharpest case because the card itself treats the five as
one row: `HEADLINE_SUFFIXES` in `www/heatpump-optimizer-card.js` resolves
`_predicted_savings`, `_savings_percentage`, `_optimization_score` and
`_plan_narrative` together, and `statEntity("_monthly_savings")` joins them.
On the device page those five are 18 names apart in four separate runs.

Leave-one-out over the seven families: dropping the single most favourable
family changes nothing (`ecl110` and `pv` are both 0, so the total stays 159);
dropping the worst (`tariff`) leaves 99. Range across families 0–60.

**The metric moves under its own perturbation, measured, not asserted.**
`naming_order.py --perturb tariff-prefix` renames the seven money entities in
memory to share the literal prefix `"Cost "` — the one change this finding
says would cluster them, and nothing else; the export is never written to.
`name_order_intruders` falls **159 → 101** and the `tariff` family goes
`60 → 0` intruders and `4 → 0` breaks. (The extra 2 beyond tariff's own 60 are
the `learning` family's span shrinking as the renamed names leave it.)

- **Severity** `low`, **stop-rule** `hygiene`. Nothing is wrong with any
  published value; this is the brief's "grouping and naming such that
  alphabetical sort clusters related entities", measured. The fix is display
  names only (`strings.json` + both translations); `unique_id` and `entity_id`
  must not move, or every install's history and the card's suffix contract
  break.

### D8-02 — four entities are the only ones with no `icons.json` entry

`entity_without_icon_entry = 4` of the 73 translation-keyed entities
(`naming_order.py`): `sensor.optimal_setpoint`,
`sensor.outdoor_temperature_optimizer`, `sensor.measured_power`,
`sensor.compressor_frequency_advisor`. `orphan_icon_keys = 0`.

The reading that would make this a non-finding is "a device class supplies
Home Assistant's default icon, so those four do not need one". The measurement
refutes it: **31 entities carry both a device class and an explicit
`icons.json` entry**, and **0 entities without a device class lack one**
(`/tmp/d8_icons.py`, folded into `naming_order.py`'s output). The convention
this integration actually follows is "every entity gets a chosen icon"; these
four are the exceptions, and they render with Home Assistant's generic
device-class glyph beside siblings that do not — `Optimal Setpoint` and
`Outdoor Temperature (Optimizer)` with the stock thermometer next to
`Indoor Temperature (Optimizer)`'s `mdi:home-thermometer`, `Upper Floor
Temperature`'s `mdi:home-floor-1`, `DHW Temperature`'s `mdi:water-thermometer`;
`Measured Power` beside `Recommended Power`'s `mdi:lightning-bolt`.

`naming_order.py --perturb drop-icon` removes one existing entry
(`sensor.indoor_temperature_optimizer`) and the count rises **4 → 5**, so the
number is a measurement over the constructed entity set and not a constant.

- **Severity** `low`, **stop-rule** `hygiene`.

## Non-findings

Each is a class the matrix could have failed and did not, with the command and
the number. These are what make the dimension callable dry.

Run `PYTHONPATH=tests/hastub:/tmp/d8pkgs python3 tools/audit/round4/D8/entity_matrix.py`
(75 cells, 74 entities, 5550 entity-cells, two cycles each, a real solve per
cycle):

| class | count | what it would have caught |
|---|---|---|
| `state_write_raises` | 0 | the stub's `SensorEntity.state` mirrors upstream's three refusals (a unit on a non-numeric device class; enum options without the enum device class; a state outside the declared options). Upstream raises on **every** state write, so one of these takes an entity down on a real install and nowhere else. |
| `enum_state_not_in_options` | 0 | an ENUM sensor publishing a code its `options` list misses |
| `enum_missing_options_attr` | 0 | ENUM device class with no option list |
| `measurement_non_numeric` | 0 | a `MEASUREMENT` state class over a non-number |
| `unit_device_class_mismatch` | 0 | a unit outside upstream's `DEVICE_CLASS_UNITS` for the declared class, or any unit on `timestamp`/`enum`/a binary sensor |
| `unit_without_device_class_unlisted` | 0 | a device class this harness has no unit table for (would silently pass) |
| `device_state_class_impossible` | 0 | a device-class/state-class pair outside upstream's `DEVICE_CLASS_STATE_CLASSES` |
| `attrs_numpy` | 0 | a numpy scalar or array in published attributes |
| `attrs_nan` | 0 | a non-finite float in published attributes |
| `attrs_unserialisable` | 0 | attributes real `orjson` refuses (`orjson_mode=real`, 3.12.0) |
| `state_string_over_255` | 0 | a state longer than `MAX_LENGTH_STATE_STATE` |
| `attrs_recorded_over_16k` | 0 | attributes the recorder drops whole above `MAX_STATE_ATTRS_BYTES` |
| `unknown_with_data` | 0 | an entity `available` and `None` while every payload key it read exists and is non-empty |
| `stale_between_cycles` | 0 | a value that did not follow the payload across two cycles (every scalar source key moved, the value did not) |
| `never_available_enabled_default` | 6 | an enabled-by-default entity unavailable in all 75 cells |
| `never_alive_enabled_default` | 12 | an enabled-by-default entity that never published a value in any cell |

**The 16 KB recorder limit, checked properly.** Three sensors publish
attribute payloads far above it — `space_heating_plan` 26 477 B,
`dhw_heating_plan` 25 085 B, `optimization_schedule` 23 961 B (real `orjson`,
all-features solved cell). That is not the number that matters: Home
Assistant's recorder drops a state's attributes whole only above
`MAX_STATE_ATTRS_BYTES = 16384` **after** `_unrecorded_attributes` is removed,
and the union over the MRO removes exactly the bulk (`forecast`, `slots`,
`setup_topology`, `manual_override`, `dhw_windows`, `dhw_windows_spec`,
`wood_fuel` on `_PlanSensorBase`; `schedule` on `ScheduleSensor`;
`dhw_schedule` on `DHWScheduleSensor`). Recorded, the same three are 499 B,
494 B and under 400 B; the largest recorded payload on the device is
`thermal_battery_charge` at 1 242 B and the whole device records 13 028 B per
cycle. The harness measures the recorded figure, which is why the count is 0.

**Every entity against a degraded payload.**
`tools/audit/round4/D8/payload_degradation.py` drives all 74 entities against
330 perturbations of a solved all-features payload — `data = None`, `data =
{}`, and for each of the 164 published keys both "key deleted" and "key set to
`None`" — reading everything Home Assistant reads on a state write
(`available`, `state`, `native_value` / `is_on` / `current_temperature` /
`target_temperature` / `hvac_mode` / `hvac_action`, `extra_state_attributes`).
**24 420 probes, 4 raises**, and all four are on payload states that cannot
occur:

- `current_action = None` → `TypeError` in `CurrentSetpointSensor`,
  `AttributeError` in `RecommendedPowerSensor` and in the climate entity.
  `HeatPumpOptimizerCoordinator._current_action` is initialised `{}` and is
  only ever assigned a dict literal (four sites) or
  `optimizer.get_current_action()`, which returns `_idle_action()`'s dict on
  both of its early exits. It is never `None`.
- `outdoor_temperature = None` → `TypeError` in `ObservedCOPSensor`, whose
  `_modelled_cop` guards with `data.get("outdoor_temperature", 5.0)` — a
  default that applies to an **absent** key and not to a present `None`. The
  key is `ThermalState.outdoor_temperature`, a `float` field with a 5.0
  constructor default, written only under `if outdoor.ok`, and `ok` requires
  `value is not None`.

The general form of that second one was measured rather than argued: across
all 75 cells, **24 of the 164 published keys are `None` in at least one cell**,
and **0 of the 79 `.get(key, non-None default)` call sites in the six platform
modules name one of them**. The `dict.get` default idiom never meets a `None`
in this tree.

**The `__init_subclass__` scrub has no mixin hole.** The trap named in the
brief and the README is that
`HeatPumpOptimizerSensorBase.__init_subclass__` wraps only properties in
`cls.__dict__`, so a published property defined on a **mixin** (which derives
from `object` at runtime, never from the base) would never be wrapped. An AST
sweep of `sensor.py` finds **0** classes that define `native_value` or
`extra_state_attributes` and are not a direct subclass of
`HeatPumpOptimizerSensorBase`; the four mixins (`_MeasuredStoreMixin`,
`_MeasuredTemperatureMixin`, `_DHWEntityMixin`, `_WaitsForEvidenceMixin`)
define only `available` and `_waiting_for`. The hole is not open.

**Translations.** `strings_vs_en_mismatch = 0`, `strings_vs_sv_missing = 0`,
`sv_untranslated = 0`, `entity_without_strings_entry = 0`,
`strings_entry_without_entity = 0` — every one of the 73 translation-keyed
entities has a name in `strings.json`, an identical one in `translations/en.json`,
and a Swedish one that is not a copy of the English. The climate entity is the
one entity with no translation entry, correctly: it sets `_attr_name = None`
under `has_entity_name`, which is Home Assistant's device-named-entity idiom.

**`narrative` reason codes vs the ENUM option list.** `PlanNarrativeSensor`
declares `_attr_options = sorted(narrative.TEMPLATES["en"])` (14 codes) and
publishes the raw reason code, so a producer emitting an untemplated code
takes the entity down on every state write. All 13 codes any producer writes
are literals in `optimizer.py`, the 14th (`untagged`) is written by
`narrative.group_by_reason` itself, and `TEMPLATES["sv"]` has the identical
key set. Same for `HEAT_PUMP_ACTION_STATES` and `OPTIMIZATION_MODE_STATES`,
both already re-derived from their producers by `tests/entities.py`.

**`_reading_key` coverage.** `_MeasuredTemperatureMixin` defaults
`_reading_key = ""`, and `_reading_ok` treats a missing key as `False`, so a
subclass that forgot to set it would be **permanently unavailable and
silent**. All 8 subclasses set it, and all 6 distinct values
(`upper_floor_temperature` ×2, `lower_floor_temperature`,
`floor_return_temperature`, `slab_temperature`, `buffer_tank_temperature`,
`dhw_temperature` ×2) are keys of the coordinator's `READING_SOURCES` map.

**Enabled by default.** 68 of 74 entities are enabled; the 6 that are not are
`ecl110_displace`, `ecl110_effective_displace`, `valve_target_recommendation`,
`contract_comparison`, `dhw_heavy_day_demand`, `compressor_frequency_advisor`.
The README documents exactly those six as disabled by default, each with the
opt-in it waits for (`README.md:359`, `:410`, `:441`, `:459`, `:467`, `:468`,
`:469`, `:473`). The card needs 12 entities — 6 by id suffix
(`statEntity`/`statNumber`) and 3 pinned ids plus their `unique_id`
fallbacks — and **`card_needs_disabled = 0`**: nothing the card resolves is off
by default. The README names 72 of the 74 entities by display name and 0 by
entity id (the two it does not name are the device-named climate entity and
`datetime.away_return`).

**Entity-id and unique-id integrity.** No duplicate `(platform, _key)`, no
duplicate `unique_id`, and **0 entity-id object-id suffix collisions** — which
matters because the card resolves headline sensors with `id.endsWith(suffix)`
and the away strip with `unique_id.endsWith(suffix)`; an id that is a suffix of
another would make that resolution ambiguous.

**Entity categories.** 20 of 74 declare `DIAGNOSTIC`, 54 are primary, none
declare `CONFIG`. All five card-headline sensors plus `dhw_temperature` are
primary and enabled — the "half the family buried on the Diagnostic side"
shape the `PlanNarrativeSensor` comment records as #175 is not present.

### Disproved leads (harness gaps, not tree defects)

**`timestamp_naive = 75` is a stub gap, not a defect.** (Control arm executed:
`--tz` gives `timestamp_naive = 0` with every other one of the 20 `RESULT`
counts byte-identical to the default arm, including `unknown_with_data = 0`,
which is the tell that the solve really ran in the control arm.) In the default arm one
entity per cell — `sensor.heat_pump_optimizer_last_optimization` — publishes a
naive `datetime` under `SensorDeviceClass.TIMESTAMP`, which on a real install
is a `ValueError` on every state write. The value is `dt_util.now()`, and
`tests/hastub/homeassistant/util/dt.py:now()` returns whatever `freeze()` was
handed; `tests/golden.py:START` is naive. Real Home Assistant's `dt_util.now()`
is always aware. The harness carries the control arm: `--tz` freezes an aware
clock **and anchors every injected price and forecast timestamp to it**, and
`timestamp_naive` goes to 0. (The first attempt at this control anchored the
prices naively, so the coordinator discarded the whole series — "No published
prices cover the planning horizon" — and skipped the solve; a control arm that
proves nothing looks exactly like one that passes, and that is why the arm
prints `RESULT arm=` and the plan-fed counts move with it.)

**`stale_between_cycles` is 0 only once dict-valued sources are excluded.** The
first formulation — "every payload key the entity read moved, and its value did
not" — fired on 542 entity-cells, over 13 distinct entities. Every one of them
reads a single **dict**-valued key and publishes a summary of it:
`optimization_schedule` = `"96 steps"` and `optimization_schedule_steps` = `96`
over a changed `schedule` (75 cells each); `predictive_optimization_insight` =
`"normal"` and `compressor_starts` over changed `predictive_info` / `insight`
(75 each); `dhw_setpoint_advisor` = `60` over a changed `dhw_advisor` whose
recommended whole-degree setpoint did not move (42); `heat_pump_action` =
`"off"` (37). Each is honest. The check now requires every source key to be a
**scalar** that moved; that count is **0**, and the dict-sourced cases are
reported separately as `stale_dict_source_undecided = 542` and are not a defect
class.

**The eight enabled-by-default entities that were never available** in an early
sweep shrank to six once the injected input states carried a
`unit_of_measurement`: `InputReader.read_power_kw` refuses a unitless state
with `problem: unknown_unit`, so `measured_power` (and with it `compressor_starts`
and part of `observed_cop`) was unavailable for the harness's reason, not the
tree's — the state table now carries a unit per entity id and `measured_power`
reads 2.2 kW. The six that remain — `wood_cheaper`, `monthly_savings`,
`observed_cop`, `optimization_score`, `prediction_accuracy`,
`wood_burn_advisor` — all wait on accumulated evidence (a month of billing, a
first COP sample, a wood-fuel readiness flag), which is what
`_WaitsForEvidenceMixin` exists to express; four of the six use it
(`monthly_savings`, `observed_cop`, `prediction_accuracy`,
`wood_burn_advisor`), and the other two carry an equivalent hand-written
`available` gate (`OptimizationScoreSensor` on `scores["overall"] is not
None`, `WoodCheaperBinarySensor` on `wood_fuel["ready"]`). Not a defect.

`never_alive_enabled_default = 12` adds six more that are available but publish
no state: the four buttons (a `ButtonEntity` has no state by design),
`datetime.away_return` (no return time set in any cell) and
`sensor.next_optimization` — the last of which is a harness artefact, because
`_next_optimization` is written by `_async_update_data`, and this harness calls
`async_run_optimization()` directly rather than driving the whole cycle.

## Harnesses

All under `tools/audit/round4/D8/`, each runnable by the single command in its
header, each thread-pinned before the numpy import, each writing only inside
its own directory.

| file | what it measures |
|---|---|
| `entity_matrix.py` | the 75-cell × 74-entity matrix, two cycles, one `RESULT` line per violation class; `--no-solve` for a fast structural pass, `--tz` for the aware-clock control arm |
| `naming_order.py` | family clustering under both orderings, translation parity across `strings.json`/`en`/`sv`, `icons.json` coverage, the enabled-by-default set against the card and the README |
| `payload_degradation.py` | all 74 entities against 330 payload perturbations, counting properties that raise |
| `matrix_run.txt`, `matrix_run_tz.txt`, `matrix_detail_naive.json`, `matrix_detail_tz.json`, `naming_detail.json`, `degradation_detail.json` | the recorded output of the runs the findings cite |

**It graduates.** `entity_matrix.py` is deterministic, needs no network, takes
no lock, prints one `RESULT` line per violation class, and its only
non-standard dependency (`orjson`) has a documented pure-Python fallback that
agrees with it on this baseline. Two things must change before it becomes a
`tests/` script: it must live directly under `tests/` (`tests/closure.py` globs
`tests/*.py` non-recursively, so a subdirectory is invisible to the gate and to
`no-copies`), and the default arm must use the aware clock, or
`timestamp_naive` will be a permanent false positive. Its wall cost is a real
solve per cycle × 150 cycles, so it belongs behind `SLOW`.

## What I could not finish

- **`stale_dict_source_undecided` (542 entity-cells) is unresolved, not
  cleared.** Each is an entity summarising a changed dict into an unchanged
  scalar. I hand-checked four (`optimization_schedule`, `dhw_setpoint_advisor`,
  `predictive_optimization_insight`, `heat_pump_action`) and all four are
  honest, but the class was not exhaustively vetted. Deciding it needs a
  per-entity map from the entity's value to the sub-field of the dict it
  summarises, which is the hand table the `TrackingDict` was built to avoid.
- **One solve per cell, not a closed loop.** Learners, accumulators and the
  accuracy history are empty everywhere, so `monthly_savings`,
  `prediction_accuracy`, `observed_cop`, `optimization_score`,
  `compressor_starts`, `wood_cheaper` and `wood_burn_advisor` were never
  observed publishing a value. `tests/rolling.py:run_rolling(learn=True)` would
  drive them; it is `SLOW`-gated and needs the quiet box.
- **Feature overlays are 15 named combinations, not the 2^12 cross product.**
  Each toggle appears alone and all of them appear together, so a defect that
  needs exactly two specific toggles and not all of them is out of reach.
- **No real Home Assistant.** Everything runs against `tests/hastub`. The
  `state` property mirrors upstream's three refusals and the unit and
  state-class tables are transcribed from upstream, but the stub has no
  entity registry, so `_attr_entity_registry_enabled_default`,
  `entity_category` and the suggested-object-id mechanism are read from the
  class rather than observed. `tests/nightly_ha.py` is the lane that would
  close this.

## Exposure

`README.md` (read: the enabled-by-default derivation and the six
disabled-by-default rows), `custom_components/heatpump_optimizer/**` and
`tests/**` (read only). No `docs/audit-*.md`, no `docs/backlog.md`, no
`docs/plan-*.md`, no `tools/audit/round3/`, no GitHub, no `gh`. A `D<k>-nn` id
appearing in a production comment was read as context and not followed. `orjson`
3.12.0 was installed into `/tmp/d8pkgs` with
`pip install --target /tmp/d8pkgs orjson`; nothing was installed into the
interpreter or into the export.
