# D8 — verifier seat 2 (consequence and reachability)

- worktree: `/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D8-2`
  at `c398fc84eec25fc44b60d74aae05b9a2da205884` (tree clean; every production
  edit below was made from a backup copy and restored, `git status` shows only
  the untracked `tools/audit/` copy of the finder's harness).
- scratch: `/private/tmp/claude-501/audit-scratch/D8-2`
- my harnesses: `seat2_reach.py` (D8-01 reachability and timing),
  `seat2_consequence.py` (D8-03 delivery and D8-04 regrouping),
  `flow_probe.py` (the real config flow).
- box: MacBookAir10,1 (M1, 8 GB), thread-pinned, `load1` 8.4–12.6 throughout.
  Every number below is a **count**, so contention-immune; the only timing
  numbers are `thread_factor` (0.943–1.000) reported for the record.

## Re-run of the finder's harness

`PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py` (full matrix,
85 cells) reproduces the header **exactly**, every RESULT line:

```
RESULT cells=85  entities=65  snapshots=11050  exceptions=0
RESULT default_temperature_leaks=1132   outdoor_default_published=10
RESULT numpy_attribute_sites=3  unserialisable_attributes=3630  numpy_state=30
RESULT schedule_truncated=170
RESULT family_splits_entity_id=15  name_en=15  name_sv=16
RESULT disabled_by_default=6  first_hour_disabled=0
RESULT thread_factor=1.000  load1=12.55
```

Single-cell baseline used for the perturbations below
(`--cells coord_minimal+none`): `default_temperature_leaks=10`,
`unserialisable_attributes=42`, `numpy_attribute_sites=1`,
`schedule_truncated=2`, `family_splits_entity_id=15`, `thread_factor=1.000`.

No discrepancy anywhere. Nothing in this panel rests on a timing number.

---

## D8-01 — ThermalState constructor defaults published as temperatures

**Vote: `verify` (severity `high` stands; the consequence is if anything
understated).**

### My own number, my own metric

Metric, one line: *the number of distinct **enabled-by-default entity STATES**
(never an attribute) that are `available` and whose published value **moves**
when the `ThermalState` constructor defaults move by +7.0 K, on the config
entry the **real config flow** produces when the user changes nothing, counted
at the first publication (Home Assistant's own setup order) and at steady
state.*

The definition is deliberately perturbation-decided, not `reading_ok`-decided:
it does not use the finder's `SOURCES` map or the payload's own bookkeeping. If
a state moves when a dataclass constructor default moves, the number on the
user's dashboard **is** that constructor default.

```
RESULT flow_thermometers=0                              (real config flow)
RESULT flow_dhw_tank_volume=200.0 L                     (so DHW is ON)
RESULT null_determinism_diffs=0                         (null control)
RESULT default_derived_states_first_publication=7
RESULT default_derived_states_steady=16
RESULT default_derived_recorded=11
RESULT cycles_to_correction=-1
RESULT per_cycle_counts=[7, 16, 16, 16, 16]
RESULT default_derived_states_probed=1                  (to_zero control)
RESULT thread_factor=0.943  load1=9.48
```

### Reachability — the sharp question, answered by driving the real flow

`flow_probe.py` walks the **actual** `HeatPumpOptimizerConfigFlow`, submitting
each form exactly as an untouched browser would (`suggested_value` or
`default`, nothing else) and supplying only the three fields the first screen
marks `vol.Required`: name, Tibber token, weather entity. It reaches
`create_entry` with a **39-key** config entry:

```
RESULT flow_temperature_entities_configured=0
```

All six thermometer keys are `vol.Optional` on `config_flow.py:975–992`
(indoor, outdoor, floor-return, lower-floor, DHW tank, buffer tank), and the
DHW page's `dhw_tank_volume` default is **200.0 L**, which is what turns
`dhw_enabled` on. So the configuration D8-01's leaks live in is not a corner of
the finder's matrix — **it is the default install**, produced by the shortest
legal path through the shipping config flow.

This kills the strongest artefact hypothesis (the harness assembling configs by
hand that a user could not reach).

### Timing — measured, not reasoned

`__init__.py:405–425` is unambiguous and my harness reproduces it:

```
coordinator._skip_solve_once = True
await coordinator.async_config_entry_first_refresh()     # line 412
...
await hass.config_entries.async_forward_entry_setups(...) # line 425
```

Entities are created **after** the first refresh, and that refresh runs
`_async_first_refresh_light`, which calls `_update_current_state()` and
`_build_data_dict()` with no solve. So the premise behind "if entities are
unavailable until the first refresh completes, the severity is wrong" does not
hold: there is **no unavailable window at all**. The first value a user ever
sees is already the default.

`per_cycle_counts=[7, 16, 16, 16, 16]`, `cycles_to_correction=-1`. The seven
temperature-derived states are default-derived at the instant of entity
creation and at every one of the four subsequent solved cycles; the window
length is **unbounded**, not transient. (The extra nine at steady state are
solve-dependent — savings, costs, plan and narrative sensors — because the same
defaults are the MPC's initial conditions; see "beyond the claim" below.)

Confirmed at source: `coordinator.py:5142` writes
`_current_state.dhw_temperature` **only** inside `if dhw.ok:`, and
`coordinator.py:5057` writes `outdoor_temperature` only inside `if outdoor.ok:`.
With no thermometer nothing ever advances either field. There is no forecast
fallback for outdoor anywhere in `coordinator.py`.

### What the user actually sees

| entity | state on the default install | device / state class |
|---|---|---|
| `sensor…outdoor_temperature_optimizer` | **5.0 °C** while the plan is solved on a −5 °C forecast | temperature / measurement |
| `sensor…indoor_temperature_optimizer` | **21.0 °C** | temperature / measurement |
| `sensor…mixed_hot_water` | **300.0 L**, 37.5 shower minutes | volume_storage / measurement |
| `sensor…thermal_battery_charge` | **86.8 %** | **battery** / measurement |
| `sensor…thermal_battery_energy` | **50.77 kWh** | energy_storage / measurement |
| `sensor…estimated_cop` | **3.32** (README: "Modelled COP at the current outdoor temperature") | — / measurement |
| `climate.heat_pump_optimizer` | `current_temperature` **21.0** | — |

Eleven of the sixteen steady-state entities carry a `state_class`, so Home
Assistant writes **long-term statistics** for them. The stub has no recorder;
in a real install these become permanent statistics rows that survive the
recorder purge. The stub also has no unit conversion — an imperial user reads
`41 °F`, still the default. **Both stub gaps hide consequence rather than
manufacture it.**

Three independent corroborations that are not the finder's harness:

1. The production code states the consequence itself.
   `sensor.py:_MeasuredTemperatureMixin` docstring: *"the history chart breaks
   the line rather than drawing a flat one, the recorder stops writing, and a
   template that checks `is_state('unknown')` or `has_value` sees the truth."*
   That reasoning was applied to five sensors and not to these.
2. The committed golden fixtures record the leak as expected output.
   `tests/golden/coord_dhw.json` and `coord_all_features.json` both carry
   `"dhw_mixed": {"litres_40c": 300.0, "shower_minutes": 37.5,
   "tank_temperature": 55.0}` and `"dhw_temperature": 55.0`.
3. The README contradicts it. `README.md:317` — "Mixed Hot Water | L | Litres
   of 40 °C water **the tank holds now** … | **Unavailable without mixed-water
   data**". It is available, and it does not describe the tank.

### Attacks run

- **Stub artefact — synchronous `FakeHass.async_add_executor_job`.** Ruled out.
  My first-publication number (7 of the 16, including every temperature-derived
  one) is taken with **no solve at all**, so the executor boundary is never
  crossed; and `_build_data_dict` is event-loop code in real HA too.
- **Stub artefact — the entity registry.** Ruled out. I counted only entities
  whose `_attr_entity_registry_enabled_default` is true, a plain class
  attribute the real registry reads identically. A registry difference could
  only add entities to the count, never remove them.
- **Stub artefact — the state machine / recorder / frontend.** Ruled out as a
  source; see above, all three make it worse.
- **Null control.** Baseline vs baseline, same seed, same clock:
  `null_determinism_diffs=0`. The metric is not solver noise.
- **Perturbation (config, `to_zero`).** Same run with all six thermometers
  wired: `default_derived_states_probed=1` — 16 → 1. Reported honestly: it is
  not exactly zero. The residual is
  `thermal_battery_energy 136.24 → 136.48 kWh` (0.18 %), so one path still
  touches a default even with every probe present.
- **Perturbation (production, one line).** `thermal_model.py:988`
  `dhw_temperature: float = 55.0 → 50.0`, in the tree: the matrix's numbers and
  my own both move as the finder states. But **`tests/entities.py` (538 checks)
  and `tests/features.py` (1557 checks) both PASS unchanged with the mutated
  default.** Only the `coord_*` golden fixtures pin it, and only as drift to be
  blessed — nothing states it as a property. A load-bearing constant with no
  behavioural guard.
- **The proposed fix against the repo's own gate.** Two results the judge
  should have:
  - the *entity-side* gate the finding proposes for Mixed Hot Water
    (`available` also requiring `_reading_ok(coordinator, "dhw_temperature")`)
    applies cleanly and `tests/entities.py` still passes 538/538 — i.e. the
    suite does not notice either direction of this gate;
  - the *coordinator-side* variant would **fail** `tests/features.py:7732`,
    which calls `_c28._dhw_mixed_water()` on a coordinator that sets
    `_current_state.dhw_temperature = 55.0` by hand with **no tank thermometer
    configured**, and asserts 450 L / 56.3 min;
  - and the finding's claim that "entity-side gating alone drifts nothing" is
    **wrong for the Outdoor sensor**: the `reading_ok` map published by
    `coordinator.py:6636` has no outdoor key (and no indoor key — indoor is
    `upper_floor_temperature`). Gating `OutdoorTempSensor` requires a
    coordinator payload change, which drifts all five `coord_*` fixtures.

### Beyond the claim (for the judge, not part of my vote)

The finding's own reason for stopping at `high` — *"no money or comfort is
decided on these publications (the solve uses the forecast and the plan, not
the published outdoor state)"* — is not what I measure. `_solve_snapshot()`
deep-copies `self._current_state` as the MPC's **initial condition**, so the
same never-updated defaults are solve inputs. Under the +7 K perturbation on
the default install: Predicted Cost 15.43 → 2.09 SEK, Baseline Cost
21.51 → 3.90, `dhw_heating_schedule` "3 heating periods" → "0 heating periods",
`space_heating_plan` "3 slots planned" → "1 slots planned". That is a separate
finding (the optimizer plans hot water against a tank temperature it has never
measured), outside D8-01's stated claim. I raise it only so the judge does not
adopt the "no money or comfort" sentence as settled.

**Decisive number:** `default_derived_states_steady=16` (11 with long-term
statistics) on a config entry with `flow_thermometers=0`, with
`cycles_to_correction=-1` and `null_determinism_diffs=0`.

---

## D8-02 — numpy scalars reach entity attributes and one state

**Vote: `verify` (severity `low` stands).**

### Re-run and perturbation

Full matrix reproduces `numpy_attribute_sites=3`,
`unserialisable_attributes=3630`, `numpy_state=30`.

I ran the stated perturbation as a **one-token production edit**, not a
harness change — `optimizer.py:1535`,
`self.model.compute_solar_gain(sr)` → `float(self.model.compute_solar_gain(sr))`:

```
coord_minimal+none  before: numpy_attribute_sites=1  unserialisable_attributes=42
coord_minimal+none  after:  numpy_attribute_sites=0  unserialisable_attributes=0
```

Not a constant, and the mechanism the finder named is exactly the one that
moves the number: the whole 42 in that cell trace to that single line.

Cross-check from an unrelated perturbation: widening D8-03's `[:24]` slices to
the full horizon took `unserialisable_attributes` 42 → **184** in the same cell
(24 → 96 schedule rows), confirming the count really is one per `solar_gain`
entry and scales with the list length.

### Consequence — cannot be settled on this box, and I say so

```
orjson installed:            no
homeassistant core installed: no  (tests/hastub only)
isinstance(np.float64(1.5), float) -> True
isinstance(np.float32(1.5), float) -> False
```

Whether an `np.float64` in an attribute is harmless (converted by the core's
`json_encoder_default`, at one callback per value) or fatal (a `TypeError` on
the state write, taking the entity's whole attribute dict with it) depends on
the installed core's hook, which does not exist on this machine. The finder
scoped this correctly and flagged it for the judge; I confirm the flag is
necessary and that no measurement on this box can retire it. The **presence**
of the numpy scalars is established and perturbation-confirmed.

One consequence I can bound: `ScheduleSensor._unrecorded_attributes` excludes
`schedule`, so the 24-value site never reaches the recorder — only the live
websocket path.

**Decisive number:** `numpy_attribute_sites` 1 → 0 in `coord_minimal+none`
under a one-token edit at `optimizer.py:1535`.

---

## D8-03 — the legacy schedule sensors describe 6 of 24 hours

**Vote: `verify` (severity `low`, class `hygiene`, stands).**

### My own number, my own metric

Metric, one line: *the wall-clock span, in hours, actually covered by the
`schedule` attribute of `sensor…optimization_schedule` on the config entry the
real config flow produces, against the 24 h the README's entity table
promises — plus how many of the two legacy sensors a user sees without
touching the registry, and how many the bundled card reads.*

```
RESULT schedule_rows=24                       RESULT schedule_hours_delivered=6.0 h
RESULT plan_rows=96                           RESULT schedule_state='24 steps'
RESULT schedule_sensors_enabled_by_default=2  RESULT card_reads_legacy_schedule=0
RESULT card_entity_ids=['heat_pump_optimizer_dhw_heating_plan',
                        'heat_pump_optimizer_solar_irradiance',
                        'heat_pump_optimizer_space_heating_plan']
```

### The two questions I was asked

**Is anything a user could reasonably build reading them?**

- The **bundled card reads neither**. `DEFAULTS` in
  `www/heatpump-optimizer-card.js:835–837` names exactly three entities —
  `space_heating_plan`, `dhw_heating_plan`, `solar_irradiance` — and a grep of
  the whole shipped asset for `heat_pump_optimizer_*` returns those three and
  nothing else. `card_reads_legacy_schedule=0`.
- Neither key appears anywhere outside `sensor.py` and the three translation
  files. No automation, blueprint or template in the tree reads them.
- The one reader a user could reasonably build is a **template off the
  documented attribute**, and the README invites exactly that:
  `README.md:286` — "Optimization Schedule | — | **The whole 24 h schedule**, in
  attributes | Not recorded". Such a template silently receives 6.0 h.
- `_unrecorded_attributes = {"schedule"}` / `{"dhw_schedule"}` means the
  attribute never reaches history, so there is no historical consequence — only
  a live one.

**Are they disabled by default?** **No.** `schedule_sensors_enabled_by_default=2`.
The six disabled-by-default sensors are `ECL110DisplaceSensor`,
`ECL110EffectiveDisplaceSensor`, `ValveTargetRecommendationSensor`,
`ContractComparisonSensor`, `DHWHeavyDaySensor`, `FrequencyAdvisorSensor`
(`sensor.py:1125, 1146, 1824, 1896, 2076, 2262`) — neither schedule sensor is
among them. So this is **not** "a sensor nobody sees": every install shows both
in its entity list, with a state that reads "24 steps" for six hours of plan.

### Attacks run

- **Perturbation (production).** Widening the `[:24]`/`[1:25]` slices in
  `coordinator.py:7023–7086` to the horizon: `schedule_truncated` **2 → 0** in
  `coord_minimal+none`. Not a constant. It also drifts every `coord_*` golden
  fixture's `schedule`/`dhw_schedule` length, as the finder says.
- **"N heating periods" counts steps, not periods.** On the flow-default
  install the two coincide (`dhw_periods_claimed=1`,
  `dhw_periods_contiguous=1`), so this cell does not settle it; the claim is
  nonetheless plain in `sensor.py:998`,
  `sum(1 for s in schedule if s.get("dhw_power", 0) > 0.1)`, which is a step
  count by construction. I record this as *asserted from source, not measured*.
- **Reachability.** No stub dependence: the slice is a literal, and 24 vs 96 is
  the same in any host.
- **Severity.** Zero wrong values — every row in the truncated list is correct;
  there are simply 18 fewer hours than the README promises, in an attribute the
  recorder never keeps, that no shipped consumer reads. The plan sensors the
  card and README both point at carry the full 96 steps. `low`/`hygiene` is
  right, and the one-line README correction is the cheaper of the two fixes the
  finder offers.

**Decisive number:** `schedule_hours_delivered=6.0 h` against a documented
24 h, on two sensors that are enabled by default (2/2) and that the bundled
card reads zero of (0/2).

---

## D8-04 — alphabetical order splits the hot-water family

**Vote: `verify` (severity `low`, class `hygiene`, stands) — with a consequence
caveat the judge should weigh before commissioning the fix.**

### Re-run and perturbation

`family_splits_entity_id=15`, `name_en=15`, `name_sv=16`, identical in the full
matrix and in every single-cell run (roster-only, so cell-independent).

I ran the stated perturbation as real edits to `sensor.py`, `strings.json`,
`translations/en.json` and `translations/sv.json` — renaming the three keys
`hot_water_energy`, `hot_water_cost`, `mixed_hot_water` into the `dhw_*`
family:

```
before: family_splits_entity_id=15  name_en=15  name_sv=16
after:  family_splits_entity_id=13  name_en=12  name_sv=15
        translation_key_mismatch=0  en_differs_from_strings=0  bad_entity_ids=0
```

The number moves, so the harness is not measuring a constant, and the rename is
internally consistent (no translation or entity-id violation follows).

### Attacks run

- **Grid / grouping artefact.** I recomputed the split count under a mechanical
  grouping (first entity-id token, groups of ≥ 2) instead of the hand-listed
  `FAMILIES` and got `family_splits_regrouped=0` over 10 groups. **I do not
  offer this as a refutation**: a group defined by the sorted-order prefix is
  contiguous by construction, so that metric can only ever return 0. It is
  degenerate and I discard it. The honest statement is the one the finder
  already makes — the count measures the hand list.
- **Leave-one-out on the hand list.** Per-family (id order): dhw 2, tariff 2,
  learning 2, accuracy 1, card_headline 3, lifetime 2, two_zone 3; ecl110, pv,
  thermal_battery 0. Dropping the largest single family leaves 12; no cell
  dominates, so the aggregate is not carried by one judgement call.
- **Severity by consequence.** Zero wrong values; zero entities made
  unreachable (all 55 sensors carry distinct translated names in both
  languages, `sv_untranslated=0`); the card's id-suffix contract touches only
  the three plan/solar entities and is unaffected (`card_entity_ids` above).
- **The fix's yield, measured.** The finder's own perturbation removes **2 of
  15** splits in id order (13 %) and **1 of 16** in Swedish, at the cost of
  **three breaking entity-id renames** — the suggested object id follows the
  translation key, so every dashboard card, automation and long-term-statistics
  series pointing at `sensor.heat_pump_optimizer_mixed_hot_water`,
  `…hot_water_cost` and `…hot_water_energy` is orphaned. `low` is right; the
  finding belongs in a naming release that can announce the break, exactly as
  the finder suggests, and should not be picked up as a patch.

**Decisive number:** the stated perturbation moves 15 → 13 (id) / 15 → 12 (en)
/ 16 → 15 (sv) — real, not a constant — against 0 wrong values and 3 breaking
renames.

---

## Summary

| id | vote | decisive number |
|---|---|---|
| D8-01 | `verify` (high) | 16 default-derived enabled-by-default **states** (11 with long-term statistics) on a config entry the real flow produces with `flow_thermometers=0`; `per_cycle_counts=[7,16,16,16,16]`, `cycles_to_correction=-1`, `null_determinism_diffs=0`, probes control 16 → 1 |
| D8-02 | `verify` (low) | `numpy_attribute_sites` 1 → 0 under a one-token edit at `optimizer.py:1535`; consequence unresolvable here (no orjson, no HA core) |
| D8-03 | `verify` (low) | `schedule_hours_delivered=6.0 h` vs a documented 24 h, on 2/2 enabled-by-default sensors the card reads 0/2 of; perturbation 2 → 0 |
| D8-04 | `verify` (low) | perturbation 15 → 13 / 12 / 15 (not a constant) against 0 wrong values and 3 breaking entity-id renames |

Nothing voided. No finding in this panel rests on a timing number, so nothing
is `unresolved` for the quiet box.
