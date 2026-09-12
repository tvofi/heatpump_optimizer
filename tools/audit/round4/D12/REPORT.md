# D12 — Generalization (round 4, first round for this dimension)

Baseline `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`, VERSION 6.4.2, export at
`.claude/worktrees/audit-r4-baseline` (no `.git`).
Machine: MacBookAir10,1, 8-core Apple M1, 8 GB, macOS 25.6.0.
Interpreter `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
`PYTHONPATH=tests/hastub:tools/audit/round4/D12`, run from the export root.
Every number below is a **count** or a **published value**; none is a timing,
so none is contaminated by the shared box (`load1` 5.1–7.6 throughout, quoted
beside each RESULT block).

`exposure`: one incidental grep hit. `docs/audit-*.md`, `docs/backlog.md` and
`tools/audit/round3/` are absent from this tree; I ran no `gh` and read no
GitHub. While grepping the tree for prior Fahrenheit handling I got one
context line back from `docs/plan-v4.0.0-program.md:632` ("shows °F on a
metric install while every other HA surface converts"). I did not open that
file, and the finding below was already measured when the line appeared — but
a plan doc is inside `COMMON.md`'s wall, so it is recorded here rather than
left unsaid.

---

## 1. Method, and where the cell count comes from

The brief's bar, applied per cell: **setup finishes; a plan is published or a
named refusal explains why not; no path invents a tank, a zone, a sensor or a
compressor mode the config omitted; an omitted optional entity leaves its
dependents unavailable or unused, not crashed.**

A *cell* is one configuration. `tools/audit/round4/D12/cells.py` derives every
axis from the tree at import time — nothing is carried:

| axis | read from | size |
|---|---|---|
| the options pages | `config_flow.HeatPumpOptimizerOptionsFlow`, every `async_step_*` that returns a form, flattened through `golden.py:_presented_fields` | 168 distinct option keys over 15 form pages + 2 menus |
| optional entity slots | the `*_entity` keys among those 168 | **31** |
| coordinator topologies | `tests/golden.py:coordinator_scenarios()` | **5** |
| golden plant fixtures | `tests/golden.py:SCENARIOS` | 49 (read for the plant shapes they toggle: valve storage, wood two-tank, wood coil, two-tank, DHW on/off) |
| hydronic layouts | `topology.LAYOUTS`, `selectable` only | **4** |
| mixing-valve modes | the `mixing_valve_mode` selector on the options `building` page | **4** |
| control-surface selectors | `freq_control_mode`, `space_setpoint_unit`, `mixing_valve_write_target_kind` | 2 + 2 + 2 |

Crossed into seven groups:

| group | what it varies | cells |
|---|---|---|
| `T` | the five coordinator topologies verbatim | 5 |
| `P` | DHW × wood × PV × two-zone, 2⁴ | 16 |
| `L` | selectable layout × valve mode | 16 |
| `E_mapped` | each optional entity slot mapped **alone** on a minimal plant | 31 |
| `E_omitted` | each optional entity slot **omitted** from the fully mapped plant (leave-one-out) | 31 |
| `S` | the control surfaces the tree already has: freq observe/control, setpoint indoor/flow, valve-write indoor/flow, on/off switch, ECL110 MQTT displace | 8 |
| `NULL` | the fully mapped reference plant — every one of the 31 slots mapped, every feature on | 1 |
| | **cells_enumerated** | **108** |

Each cell is driven the way `tests/entities.py:collect` and
`tests/golden.py:_capture_coordinator` already do it, in
`tools/audit/round4/D12/d12lib.py:drive_cell`: construct
`HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))`, inject
the same 48 h of prices / weather / irradiance those two use, `await
coord._update_current_state()`, `await coord.async_run_optimization()`,
`coord._build_data_dict()`, then every one of the six platforms'
`async_setup_entry` and every entity's `available`, `native_value` /
`is_on` / `current_temperature` and `extra_state_attributes`. The clock is
frozen at `golden.START`.

---

## 2. Result on the crash / no-plan bar

```
RESULT cells_enumerated=108 count
RESULT cells_failing=0 count
RESULT null_control_fully_mapped_ok=1 count
RESULT null_control_plan_steps=96 count
```

**cells_failing = 0.** Every one of the 108 cells set up, solved and published
96 plan steps, and every one of the 74 entities on every cell answered
`available`, its state and its attributes without raising. That is a real
non-finding and it is the largest single result here: the crash axis of this
dimension is clean at this baseline.

The omission differential (`E_omitted` against `NULL`) is clean too. Dropping
any one of the 31 slots leaves the entities that read it **unavailable**, not
fabricating: `dhw_temperature` 52.0→unavailable, `buffer_tank_temp`
→unavailable, `indoor_temp` and `upper_floor_temp` →unavailable,
`HeatPumpOptimizerClimate` →unavailable, `lower_floor_temp` →unavailable,
`slab_temp` and `floor_return_temp` →unavailable, `measured_power` →None. The
`reading_ok` map (`coordinator.py:607 READING_SOURCES`, `sensor.py:118
_reading_ok`, `sensor.py:338 _MeasuredTemperatureMixin`, `sensor.py:161
_MeasuredStoreMixin`, `sensor.py:367 _DHWEntityMixin`, `climate.py:122/194`)
does what its docstrings say it does. `outdoor_temp` stays available and moves
−3.0 → −5.0, which is the documented and labelled forecast fallback
(`sensor.py:130 _effective_outdoor`), not a fabrication.

So the finding in this dimension is not a crash and not an omitted entity. It
is one axis of "a wide range of setups" that the matrix above cannot see
because every cell in it speaks the same units.

---

## 3. Finding D12-01 — the plant is read in whatever unit Home Assistant hands it, and only power is converted

**Claim.** On a Home Assistant instance that is not on the metric unit system,
every temperature the integration reads is adopted as °C without conversion,
so the solver plans against a plant that does not exist and publishes a
24-hour plan that commands **0.0 kWh** of heating — with no refusal, no
repair, and no unavailable entity.

`inputs.py:452 InputReader.read` is `float(state.state)` and nothing else.
`inputs.py:559 read_power_kw` is the one read that consults
`attributes["unit_of_measurement"]`, through `inputs.py:179
normalize_power_kw` / `const.py:122 POWER_UNIT_TO_KW` — whose own docstring
states the principle ("a wrongly scaled power value is worse than no power
value, because everything downstream trusts it") and applies it to W/kW/MW/mW
only. There is no Fahrenheit handling anywhere in production: the only
occurrence of the word is `sensor.py:2234`, a comment recording that **a
household on Fahrenheit** was already reported — the *output* side was fixed
for exactly this user by giving the sensor a `TEMPERATURE` device class, and
the *input* side was not.

Ten of the coordinator's guarded reads take a bare `read()` on an entity whose
unit Home Assistant varies: `indoor_temp_entity`, `outdoor_temp_entity`,
`floor_return_temp_entity`, `lower_floor_temp_entity`, `dhw_temp_entity`,
`buffer_tank_temp_entity`, `wood_tank_top_entity`, `wood_tank_bottom_entity`,
`valve_outlet_temp_entity`, `mixing_valve_target_entity`
(`coordinator.py:3246-3248, 4915-4973, 5008-5027`), plus
`heat_pump_energy_entity` at `coordinator.py:4988` where the varying unit is
Wh / kWh / MWh rather than °F — that one is unit-system-independent and hits a
metric user with a Wh-reporting meter.

**Evidence** — `tools/audit/round4/D12/units.py`. One physical plant, driven
twice: the fully mapped reference plant in °C/kWh, and the identical plant
expressed in °F/Wh with the matching `unit_of_measurement` attribute, which is
what Home Assistant puts in the state machine for a `device_class: temperature`
sensor on a US-customary instance. `InputReader.read` is wrapped so every
guarded read is recorded with the entity's own unit and the value the caller
received.

```
RESULT celsius_inputs_misread=0 count          <- NULL CONTROL
RESULT celsius_indoor_temperature_c=21.4 degC
RESULT celsius_dhw_temperature_c=52.0 degC
RESULT celsius_outdoor_temperature_c=-3.0 degC
RESULT celsius_plan_kwh=4.752 kWh
RESULT celsius_plan_steps=96 count

RESULT imperial_inputs_misread=10 count
RESULT imperial_indoor_temperature_c=70.5 degC
RESULT imperial_dhw_temperature_c=125.6 degC
RESULT imperial_outdoor_temperature_c=26.6 degC
RESULT imperial_plan_kwh=0.0 kWh
RESULT imperial_plan_steps=96 count
  misread inputs (imperial):
    buffer_tank_temp_entity      unit='°F'  adopted=104.0
    dhw_temp_entity              unit='°F'  adopted=125.6
    floor_return_temp_entity     unit='°F'  adopted=82.4
    heat_pump_energy_entity      unit='Wh'  adopted=1234500.0
    indoor_temp_entity           unit='°F'  adopted=70.5
    lower_floor_temp_entity      unit='°F'  adopted=69.4
    mixing_valve_target_entity   unit='°F'  adopted=95.0
    outdoor_temp_entity          unit='°F'  adopted=26.6
    wood_tank_top_entity         unit='°F'  adopted=131.0
RESULT load1=5.73
```

The plan is not refused and not marked stale: 96 steps are published, every
one at zero power, because the model believes a 21.4 °C room is at 70.5 °C —
47 °C above the comfort band's 23 °C ceiling. Every measured-temperature
sensor stays **available** with a `TEMPERATURE` device class and a
`MEASUREMENT` state class, so Home Assistant writes long-term statistics for
70.5 °C indoors and 125.6 °C in the tank. This is precisely the hazard
`sensor.py:340` was written against, reached by a different door: the number
is not a constructor default, it is a real reading in the wrong unit, so every
`reading_ok` gate in the tree passes it through.

**Perturbation (production edit).** A one-line °F→°C conversion installed in
`InputReader.read`:

```
RESULT imperial_inputs_misread=1 count          (10 -> 1)
RESULT imperial_indoor_temperature_c=21.38888888888889 degC
RESULT imperial_dhw_temperature_c=52.0 degC
RESULT imperial_outdoor_temperature_c=-2.999999999999999 degC
RESULT imperial_plan_kwh=4.198 kWh              (0.0 -> 4.198)
```

The residual 1 is `heat_pump_energy_entity` at Wh, which a temperature-only
fix does not reach — the same mechanism, a second unit family.

**Perturbation (plant shrink, the brief's mandated one).** `--shrink` drops
DHW, wood, PV, one zone and four sensors from the same plant:

```
RESULT celsius_inputs_misread=0 count          <- null control holds
RESULT imperial_inputs_misread=4 count          (10 -> 4)
RESULT imperial_plan_kwh=0.0 kWh
```

The number moves with the plant, in the stated direction, and the null control
stays at zero in both plant sizes.

**Consequence.** A household whose Home Assistant is set to US customary units
installs this integration, completes the config flow, sees every entity
populate with plausible-looking numbers and a published plan — and the heat
pump is commanded off for the whole horizon, in winter. Nothing in the UI says
why: no repair, no unavailable entity, no named refusal. On the round-2
severity scale that is **wrong comfort silently**, which is `critical`. I have
scored it `high` rather than `critical` for one reason the panel should test:
the actual pump only follows the plan where a switch or ECL110 surface is
wired, and a user who has wired neither keeps the pump's own weather curve, so
the loss is the optimization rather than the heat. Where a switch *is* wired
(`coordinator.py:6305`), it is `critical`.

**Out of dimension, carried not filed.** The Wh/MWh half of this and the
°F-labelled published value are arguably D8's "wrong unit". The reason it is
filed here and not carried: the failure is not an entity's label, it is that
an entire install class — every non-metric Home Assistant instance — produces
no heating plan at all. That is this dimension's subject, and D8 measures the
reference plant's entities on the matrix I share with it, all of which speak
°C.

---

## 4. Non-findings (checked, held, with the number)

| claim | command | value |
|---|---|---|
| every enumerated plant cell sets up, solves and publishes a plan | `python3 tools/audit/round4/D12/matrix.py` | `cells_enumerated=108`, `cells_failing=0` |
| the fully mapped reference plant is not the only one that works — the 16 DHW×wood×PV×two-zone combinations all publish 96 plan steps | same, `--group=P` | `group_P_cells=16`, `group_P_failing=0` |
| every selectable hydronic layout × every mixing-valve mode sets up, including the combinations `const.topology_layout_valid` calls invalid | same, `--group=L` | `group_L_cells=16`, `group_L_failing=0` |
| each of the 31 optional entity slots, mapped alone on an otherwise minimal plant, sets up and solves | same, `--group=E_mapped` | `group_E_mapped_cells=31`, `group_E_mapped_failing=0` |
| omitting any one of the 31 slots from the fully mapped plant leaves its dependents unavailable, never crashed and never fabricating | same, `--group=E_omitted` | `group_E_omitted_cells=31`, `group_E_omitted_failing=0`; `dhw_temperature`, `buffer_tank_temp`, `indoor_temp`, `upper_floor_temp`, `lower_floor_temp`, `slab_temp`, `floor_return_temp`, `measured_power` and the climate entity all go unavailable |
| the eight control surfaces (freq observe/control, setpoint indoor/flow, valve-write indoor/flow, on/off switch, ECL110 MQTT) each set up and solve | same, `--group=S` | `group_S_cells=8`, `group_S_failing=0` |
| an install with no outdoor thermometer publishes the forecast step the plan was solved on, labelled, not the 5.0 constructor default | `units.py` / `matrix.py` differential | `outdoor_temp` −3.0 → −5.0, stays available with its source attribute |
| the wood tank is not simulated when it is not configured | read + drive: `coordinator.py:5026-5046` gates on `two_tank_modelled` and nulls `wood_tank_temperature` when reconfigured away | `P_*_wood0_*` cells publish no `two_tank_modelled` key at all |
| currency is not hard-coded to SEK | `currency.py:resolve_currency`, 8 `_attr_native_unit_of_measurement` sites in `sensor.py` | instance currency with an SEK fallback — correct generalization |
| power inputs ARE unit-normalised | `inputs.py:559` / `const.py:122` | W/kW/MW/mW, unknown unit → `unknown_unit`, never a guess |
| omitting `compressor_freq_entity`, `pv_production_entity`, `dhw_inlet_entity`, `indoor_humidity_entity` or `heat_pump_energy_entity` from the fully mapped plant changes nothing that is published | `units.py`-style differential | zero entity-availability or value deltas — the "correctly unused" case the brief calls a non-finding |

## 5. Harnesses

- `tools/audit/round4/D12/d12lib.py` — the cell driver (`drive_cell`), thread-pinned, count-only.
- `tools/audit/round4/D12/cells.py` — the matrix, every axis derived from the tree; run it alone to print the derivation.
- `tools/audit/round4/D12/matrix.py` — D12-H1, the crash / no-plan bar over all 108 cells.
- `tools/audit/round4/D12/units.py` — D12-H2, the finding, with `--convert` (production-edit perturbation) and `--shrink` (plant-shrink perturbation).
- `tools/audit/round4/D12/services_cells.py` — D12-H3, every registered service on every `T`/`P`/`L`/`NULL` cell.

## 6. What I could not finish

- **`services_cells.py` (D12-H3) did not return inside the budget** under the
  fan-out load. Its design is committed and it is runnable by the single
  command in its header; no finding rests on it and none of the numbers above
  came from it. It should be re-run in the quiet window.
- **The config and options flows were enumerated but not *walked* per cell.**
  I read all 15 option pages to derive the axes; I did not submit each page on
  each plant. `tests/config_flow_steps.py` already walks them on the reference
  plant; walking them on a DHW-less or valve-less plant is the obvious next
  probe, and it is the boundary where D4 (ergonomics) takes over from D12
  (does it work at all).
- **`heatpump_optimizer.__init__:async_setup_entry` was not driven.** I drove
  the coordinator and the six platforms directly, which is what
  `tests/entities.py` and `tests/golden.py` do. A crash confined to the entry
  setup wrapper — the frontend registration, the service registration, the
  store load — would not be visible in `cells_failing`.
- **Only the first coordinator cycle is driven per cell.** A defect that needs
  a restore-from-store, a reconfigure mid-session, or a second cycle is out of
  this matrix's reach.
- **The `price_source = entity` install class is not covered.** Every cell
  injects `coord._prices` directly, the way `golden.py` does, which bypasses
  `_fetch_tibber_prices` and therefore bypasses the entity price source
  entirely. That is a whole install class this matrix cannot speak to.
