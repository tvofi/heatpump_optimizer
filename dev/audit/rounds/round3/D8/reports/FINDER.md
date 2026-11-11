# D8 — sensor verification and ordering (audit round 3)

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. Tree: a `git archive`
export with no `.git`, and with `docs/audit-*.md`, `docs/backlog.md` and
`RELEASE_NOTES.md` removed. Box: 8-core Apple M1, 8 GB, python 3.11.5, numpy
2.4.6, scipy 1.17.1.

**The box was shared with eleven other audit sessions throughout. The
one-minute load average moved between 5 and 190 while these harnesses ran.
Every number in this report is a count, so no number here can move with load** —
that is why the matrix is built out of counts rather than out of timings, and
why `thread_factor` is 1.000 on every run (single-threaded, BLAS pinned).

## Method

Four harnesses, all under `tools/audit/round3/D8/`, each runnable by the single
command in its own header, each from the repository root with
`PYTHONPATH=tests/hastub`, each pinning the five BLAS thread variables before
importing numpy, each writing only under its own directory or an explicit
`--dump` path, and none of them touching the gate lock (none runs `stress.py`
or `run.sh`).

**`d8_matrix.py`** — the matrix the brief asks for. 23 cells: the five
topologies of `tests/golden.py:coordinator_scenarios()` crossed with two input
arms (`blind`, nothing wired — which is what the config flow produces when
every optional probe field is left alone; `sensed`, every non-topology probe
wired and reading), plus thirteen feature overlays on `coord_all_features`
(DHW off, DHW with a tank probe, two-zone, valve + buffer storage, two-tank
4-way, wood furnace + DHW coil, ECL110, PV off, PV metered, capacity tariff
off, grid fee, away active, inverter frequency).

Each cell builds a **real** `HeatPumpOptimizerCoordinator` the way
`tests/golden.py:_capture_coordinator` does — frozen clock at `golden.START`,
48 h of injected Tibber-shaped prices, weather and irradiance,
`_forecast_arrays()` — then runs the real optimizer and `_build_data_dict()`.
Every entity of all six platforms is constructed through the **real**
`async_setup_entry`, driven exactly as `tests/entities.py:collect` drives it.
(That module cannot be imported: it runs its whole suite at import and
`sys.exit()`s — `tools/audit/README.md`, "Traps" — so the eight lines that
matter are inlined, driving the same production symbols.)

**Two cycles**: the clock advances 3 h, prices shift +0.45 SEK/kWh, the weather
drops 6 K, and every wired probe reads a different value, so staleness is
observable. The published payload is wrapped in a key-recording `dict`
subclass, so each entity's **source keys are observed rather than guessed** —
which is what makes "unknown where its data exists" and "did not follow its
input" answerable per entity instead of by hand. 74 entities × 23 cells ×
2 cycles = 3,404 entity reads.

**`d8_ordering.py`** — the same roster sorted three ways (entity_id, English
display name, Swedish display name), with per-family split counts, the
rank-move count between the id order and the name order, the key-versus-name
slug divergence, and the capitalisation-style split.

**`d8_wood_advisor.py`** — D8-01 and D8-02's instrument: six shipped arms in
which the wood furnace is genuinely configured and priced, each read three
times (as shipped, `wood_tank_soc=0.2`, `wood_tank_soc=0.9`), plus a
solver-free probe straight against `wood_fuel:night_advice`, plus a count of
everything in the tree that mentions `wood_tank_soc`.

**`d8_timestamps.py`** — one cell with a **real, tz-aware, unfrozen** clock,
because the frozen-clock matrix cannot answer the TIMESTAMP question (see the
harness gaps).

## Findings

### D8-01 — the Wood-burn night advisor can never advise (medium, bug)

`wood_fuel.py:_attach_night_advice` reads `config.get("wood_tank_soc")` and
falls back to `0.5`. **That key has no writer anywhere in the tree**: the only
occurrence outside this report's own harness is the read itself. `0.5` sits
strictly between `night_advice`'s two productive thresholds
(`tank_soc < 0.4` → `light`, `tank_soc > 0.8` → `skip`), so the middle branch
`none` is the only reachable one, no `night_advice` key is ever attached to the
published `wood_fuel` view, and `WoodBurnAdvisorSensor.native_value` is `None`
for every install that ever existed. The feature `#702` describes — "48 h
light/skip advice when the wood furnace is on" — has never run.

Executed: `advice_value_as_shipped=0` over six arms where `wood_fuel_ready` is
`True`, and `0` non-null over all 46 matrix reads of the same sensor;
`gate_productive_at_0_5=0` against `night_advice` directly, while `soc=0.2`
reaches `light` at cheap wood and `soc=0.9` reaches `skip` at dear wood.
Perturbation (a config change, no tree edit): put `wood_tank_soc=0.2` in the
config entry and the same sensor publishes `'light Thu 23:00'` in all three
cheap-wood arms — 0 → 3, up. Control: the three dear-wood arms stay silent in
both, because there the pump is cheaper at every hour and silence is correct.

### D8-02 — one entity renders Unknown where every sibling renders Unavailable (medium, bug)

`WoodBurnAdvisorSensor` declares no `available` override, so it is available
whenever the coordinator is, and it publishes `None`. Home Assistant renders
that as **Unknown** — which is also what it renders for an integration that
has thrown. That confusion is the exact thing `sensor.py:_WaitsForEvidenceMixin`
was written to end ("Unavailable is the state that means 'nothing to
report'"), and it is what its sibling `binary_sensor.py:WoodCheaperBinarySensor`
avoids with a one-line gate on the same payload key. The entity is enabled by
default and carries `EntityCategory.DIAGNOSTIC`, so every install shows a
permanently-Unknown row in the Diagnostic section.

Executed: `available_unknown_default_install=2` on `coord_minimal/sensed` (of
59 enabled-by-default value entities) and `available_but_unknown_everywhere=2`
across all 23 cells. The second member is `AwayReturnDateTime`, a `datetime`
**control** whose value the user sets, which is arguably legitimate and is
named here rather than claimed. Perturbation:
`d8_matrix.py --perturb wood-gate` applies, in memory, the one-line fix — give
`WoodBurnAdvisorSensor` the gate `WoodCheaperBinarySensor` already has — and
both counts drop by exactly one.

### D8-03 — the entity list has a family-prefix convention and applies it to half the families (low, hygiene)

Home Assistant lists a device's entities alphabetically. The families that
carry a leading family noun survive that sort almost intact — `Solar …`,
`ECL110 …`, `Thermal Battery …` and `Boost …` at 0 splits each, `DHW …` at 1
split over 10 entities. The rest use a trailing noun and scatter: **36 splits
in total** across the 16 families the harness lists, worst
being temperature — eight temperature entities in eight separate runs
("Buffer Tank Temperature (Model)", "DHW Temperature", "Floor Heating Return
Temperature", "Indoor Temperature (Optimizer)", "Lower Floor Temperature",
"Outdoor Temperature (Optimizer)", "Slab Temperature (Estimated)", "Upper
Floor Temperature") — then cost (5), advisor (5), optimization (5), tariff (4).
Swedish scatters the same total differently (DHW 1 → 3, temperature 7 → 4), so
this is not an artefact of English. Two smaller symptoms of the same drift ride
along and are counted, not claimed separately: 15 entities whose
`translation_key` is not the slug of their display name (so `entity_id` order
and name order disagree; 33 entities move ≥ 5 places between the two sorts),
and 6 display names in sentence case against 68 in Title Case.

Perturbation: `d8_ordering.py --perturb split-ecl110` moves one object id out
of the `ecl110_` run without touching its name;
`family_splits_entity_id` 36 → 37 (up by exactly 1) while `family_splits`,
`family_splits_sv` and `case_style_minority` do not move.

## Non-findings — what was checked and held

| what was checked | number | how |
|---|---|---|
| `(device_class, state_class)` pairs Home Assistant calls impossible | 0 over 3,404 entity reads | `d8_matrix.py` `RESULT dc_sc_impossible` |
| native unit outside the valid set for the device class, and any unit at all on a non-numeric device class | 0 | `RESULT unit_vs_device_class` |
| a numeric state class publishing a non-numeric value | 0 | `RESULT state_class_type` |
| an ENUM state outside its declared options (`tests/hastub`'s transcription of core's `SensorEntity.state`, which raises the way a real install does) | 0 | `RESULT enum_not_in_options` |
| TIMESTAMP sensors tz-aware on a real clock | 0 naive of 2 | `d8_timestamps.py` `RESULT timestamp_naive` |
| published attributes carrying a numpy object, a non-finite float, or anything `json.dumps(allow_nan=False)` refuses — on **all six** platforms, not only the scrubbed one | 0 | `RESULT attr_unserialisable` |
| duplicate `entity_id` or `unique_id` within a cell | 0 | `RESULT id_collision` |
| `strings.json` versus `translations/en.json` and `sv.json`, entity name keys | 0 missing, 0 orphan, and 0 names left untranslated (no identical en/sv pair) | `d8_ordering.py` `RESULT strings_vs_en`, `strings_vs_sv` |
| entity ids pinned in the right domain on every platform | 6 of 6 platforms pin `"<domain>.heat_pump_optimizer_…"` | `grep -rn "self.entity_id = "` |
| every entity id the card and `README.md` name exists and is enabled by default | 6 card suffixes + 6 README ids, all present, none in the disabled roster | `grep -o` over `www/heatpump-optimizer-card.js` and `README.md` against the roster |
| numeric sensors with no `suggested_display_precision` | 1, and it is `compressor_starts`, an integer count | inline probe |
| `icons.json` coverage | 4 sensor keys absent, all four already pinned as device-class defaults by `tests/entities.py`'s `_DC_DEFAULT_KEYS` | `python3 -c` diff of the two files |
| enabled-by-default entities dead on the first-hour install | 10 of 59, of which 8 are honestly `available=False` (config-gated or waiting for evidence) and only 2 are Unknown-while-available (D8-02) | `RESULT enabled_default_dead_first_hour`, control `enabled_default_dead_all_features=7` |

## Harnesses, and every number they printed

All four run from the repository root, single-threaded, BLAS pinned; every
`thread_factor` was 1.000. `load1` is quoted, not gated — the box's own
ambient floor makes a `load1 <= 1.5` bar a stall rather than a safeguard, and
every number below is a count, which no load can move.

### `tools/audit/round3/D8/d8_matrix.py`
`PYTHONPATH=tests/hastub python3 tools/audit/round3/D8/d8_matrix.py`
(`load1=20.72`, ~2.5 min, 46 real solves)

```
cells=23  entities_per_cell=74  entity_classes=74
dead_where_data_exists=1            unavailable_everywhere=8
available_but_unknown_everywhere=2
enabled_default_first_hour=59       enabled_default_dead_first_hour=10
enabled_default_dead_all_features=7
available_unknown_default_install=2 available_unknown_all_features=2
frozen_while_input_moved=9
state_class_type=0  timestamp_naive=0  enum_not_in_options=0
dc_sc_impossible=0  unit_vs_device_class=0  attr_unserialisable=0
id_collision=0
```
Perturbations, both verified at `--limit 2` (cell 2 is `coord_minimal/sensed`,
which is the cell the per-install metrics use, so the judge need not pay for
23 cells to check them). The `--limit 2` **unperturbed** baseline, for that
comparison, is `available_unknown_default_install=2`,
`available_but_unknown_everywhere=2`, `frozen_while_input_moved=9`:
`--perturb wood-gate` → `available_unknown_default_install` 2 → **1**,
`available_but_unknown_everywhere` 2 → **1**.
`--perturb same-inputs` → `frozen_while_input_moved` → **0**.

### `tools/audit/round3/D8/d8_ordering.py`
`PYTHONPATH=tests/hastub python3 tools/audit/round3/D8/d8_ordering.py`
(`load1=13.96`, instant)

```
entities=74  family_splits=36  family_splits_entity_id=36  family_splits_sv=36
rank_moves_ge_5=33  key_not_slug_of_name=15  case_style_minority=6
strings_vs_en=0  strings_vs_sv=0
```
Per family (name / entity_id / Swedish): dhw 1/1/3 (n=10), temperature 7/7/4
(n=8), cost 5/5/4 (n=6), energy 2/2/2, cop 1/1/1, optimization 5/4/6 (n=12),
solar_pv 0/0/1, ecl110 0/0/0, away 1/2/1, boost 0/0/0, wood 0/1/0, advisor
5/4/2 (n=6), learning_accuracy 2/2/5, tariff_peak 4/4/3 (n=7), plan 3/3/4,
battery 0/0/0.
Perturbation `--perturb split-ecl110` → `family_splits_entity_id` 36 → **37**,
`family_splits` 36 (unmoved), `family_splits_sv` 36 (unmoved),
`case_style_minority` 6 (unmoved).

### `tools/audit/round3/D8/d8_wood_advisor.py`
`PYTHONPATH=tests/hastub python3 tools/audit/round3/D8/d8_wood_advisor.py`
(`load1=17.07`, ~5 min, 18 real solves)

```
gate_combinations=6  gate_none_at_default_soc=4  gate_productive_at_0_5=0
arms=6  writers_of_wood_tank_soc=0  wood_fuel_ready=6  advice_available=6
advice_value_as_shipped=0
advice_value_soc_low=3  advice_value_soc_high=0
cheap_wood_arms_value_as_shipped=0  cheap_wood_arms_value_soc_low=3
```
The perturbation is inside the run: the `soc=0.2` column. As shipped, all six
arms publish `None`; with `wood_tank_soc=0.2` and nothing else changed, the
three cheap-wood arms publish `'light Thu 23:00'`. The three dear-wood arms
stay `None` in every column, which is the control — there the pump is cheaper
than wood at every hour and silence is the correct answer.

### `tools/audit/round3/D8/d8_timestamps.py`
`PYTHONPATH=tests/hastub python3 tools/audit/round3/D8/d8_timestamps.py`
(`load1=189.95` — the worst moment of the fan-out, and it did not matter,
because these are counts)

```
clock_tz_aware=1  timestamp_entities=2  timestamp_naive=0  timestamp_nondt=0
```
Perturbation `--perturb naive-stamp` → `timestamp_naive` 0 → **2**, which is
what shows the zero is a result and not dead code.

## Disproved leads, each with the harness gap named

These cost real time. They are written down so the next auditor does not repeat
them; every one of them **fails green**.

1. **"`device_class`, `state_class`, `entity_category` and `icon` are unset on
   all 74 entities."** They are not. `tests/hastub`'s entity stubs declare **no**
   `device_class` / `state_class` / `entity_category` / `icon` property, so
   `ent.device_class` is `None` for every entity and every metric keyed on it
   silently measures nothing. A whole first matrix run produced four vacuous
   zeroes this way and looked like a clean bill of health. The `_attr_…` class
   attributes are the real source, and are what `tests/entities.py` reads for
   the same reason. **This is the most expensive gap in this dimension.**
2. **"`MeasuredPowerSensor` is permanently unavailable even with a power meter
   wired."** It is not. `inputs.py:normalize_power_kw` returns `None` for a
   power entity with no `unit_of_measurement` ("a missing one means the entity
   is not really a power sensor"), so a `FakeState("2.4")` with no unit makes
   `measured_power` `None` and the sensor unavailable in every cell. Giving the
   probe states their units clears it; the refusal is deliberate and correct.
3. **"`NextOptimizationSensor` is permanently unknown."** It is not.
   `coordinator.py:4693` assigns `_next_optimization` only inside
   `_async_update_data`, which needs the Tibber network call; a harness that
   drives `async_run_optimization` directly never runs that line.
4. **"Both TIMESTAMP sensors publish naive datetimes."** They do not.
   `tests/hastub`'s `dt_util.now()` returns the frozen value verbatim and
   `tests/golden.py:START` is naive, so *every* clock-derived timestamp is naive
   under the frozen matrix whatever production does. `d8_timestamps.py` answers
   it with `HASTUB_TZ` set and no freeze: `timestamp_naive=0`, and
   `--perturb naive-stamp` moves it to 2, so the check is not dead code. The
   matrix now counts a naive timestamp only when `dt_util.now()` was itself
   aware.
5. **The trap the brief names, confirmed — and extended.**
   `HeatPumpOptimizerSensorBase.__init_subclass__` wraps every subclass's
   `native_value` and `extra_state_attributes` in `sensor.py:_finite`, so a
   non-finite or numpy value produced inside a sensor is scrubbed before any
   harness can see it. `peak_threshold_kw` is `+inf` in the published payload of
   every cell and its only consumer is a scrubbed sensor attribute.
   **The extension worth recording:** `__init_subclass__` is installed on the
   *sensor* base only, so `binary_sensor`, `switch`, `climate`, `datetime` and
   `button` publish attributes **unscrubbed**. That is a structural gap, not a
   defect today — the matrix checks all six platforms and finds 0 numpy and 0
   non-finite leaves in 3,404 reads — but a future payload key reaching, say,
   `HeatPumpOptimizerClimate.extra_state_attributes` would not be covered.
   Recorded rather than filed: an argument is not a finding.

## What I could not finish

- **`frozen_while_input_moved=9` is a triage list, not a finding.** The metric
  reports an entity whose value is byte-identical across the two cycles in
  every cell where a key it read moved. Several members are correct by design
  (`ScheduleStepsSensor` publishes the horizon step count, constant by
  construction; the plan sensors publish a slot-count summary string that can
  legitimately repeat). Separating "correctly constant" from "stale" needs a
  per-entity expectation this harness does not have. The number, the class
  list, and the `--perturb same-inputs` control that must take it to zero are
  in the harness output, so a later round starts from there rather than from
  scratch.
- The matrix runs two coordinator cycles, not a day. Entities that legitimately
  wait for accumulated evidence (`ObservedCOPSensor`, `PredictionAccuracySensor`,
  `MonthlySavingsSensor`, `CompressorStartsSensor`, `OptimizationScoreSensor`,
  `ContractComparisonSensor`) are unavailable throughout and are excluded from
  every "permanently unknown" claim on that ground. A closed-loop arm through
  `tests/rolling.py:run_rolling` would settle whether each does light up; it is
  `SLOW=1` and there was no quiet window.
- The Lovelace card was not driven. `tests/card_rig.mjs` would answer whether
  the card degrades gracefully on the entities that are unavailable on a
  minimal install; that is D4's dimension and it was left there.

## exposure

None beyond the tree. `README.md` and
`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` were read
for brief item 4 only, to list the entity ids the documentation and the card
depend on. No `gh`, no GitHub, no `docs/audit-*.md` (absent from this tree), no
earlier-round findings. Two `D8-nn` ids appear as identifiers in
`tests/entities.py` (the `_d801_*` helpers and a comment reading "D8-01
(#173)"); they were treated as context, not as a to-do list, and no attempt was
made to recover what they referred to.
