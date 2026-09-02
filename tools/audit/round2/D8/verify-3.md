# D8 verifier seat 3 — perturbation and scope

- baseline: `c398fc84eec25fc44b60d74aae05b9a2da205884` (worktree `v-D8-3`, tracked
  files clean at the end of every experiment; `git status` shows only my
  untracked copy of `tools/audit/`)
- interpreter: `tvofi-claude/.venv/bin/python` 3.13.1, numpy 2.5.2, scipy 1.18.1
  (the pyenv shim has no numpy; the venv has no `orjson` and **no real
  `homeassistant`** — see D8-02)
- machine: MacBookAir10,1 (Apple M1, 8 GB), OpenBLAS, five BLAS variables pinned
  before every numpy import
- my harnesses: `/private/tmp/claude-501/audit-scratch/D8-3/{causal,numpy_probe,numpy_scope,ordering}.py`
- every number below is a **count**; contention-immune. `thread_factor` 1.000
  throughout. The one timing line the finder's harness prints (`cpu_s`) is
  marked provisional by the harness itself and no finding rests on it.

## Re-run of the finder's harness

`PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py` (full matrix,
85 cells), thread-pinned:

```
RESULT cells=85  entities=65  snapshots=11050
RESULT default_temperature_leaks=1132   outdoor_default_published=10
RESULT numpy_attribute_sites=3  unserialisable_attributes=3630  numpy_state=30
RESULT schedule_truncated=170
RESULT family_splits_entity_id=15  name_en=15  name_sv=16
RESULT exceptions=0 unknown_where_data_exists=0 type_violations=0
RESULT metadata_violations=0 nonfinite_attributes=0 stale_entities=0
RESULT follows_payload_mismatch=0
RESULT thread_factor=1.000  load1=10.79
```

**Every headline number reproduces exactly.** `load1` 10.79 is far over the
1.5 bar, which is why I checked that no finding rests on a timing number: none
does.

---

## D8-01 — ThermalState constructor defaults published as temperatures

### My own number, my own metric

The finder counts publications whose `reading_ok[field]` flag is False. That is
a **proxy**: it trusts the coordinator's own freshness map to say what is a
default. I never read `reading_ok`. Instead:

> **Metric (mine, one line).** The number of distinct
> (entity_id, state-or-attribute-leaf) publications whose numeric value
> *changes* when exactly one `ThermalState` constructor default is moved by a
> known delta with the cell's configuration unchanged — i.e. published numbers
> that are causally downstream of a constructor default rather than of a
> measurement.

Harness `causal.py`, 5 topologies × 11 features = 55 cells, one solved cycle,
`ThermalState.__init__.__defaults__` rewritten one field at a time.

```
RESULT field=dhw_temperature 55.0->50.0
RESULT causal_temp_leaks=4033 publications   cells_holding=50 of 55  holds_fraction=0.909
RESULT per_cell_min=0 per_cell_max=198       loo_drop_max=3835

RESULT field=outdoor_temperature 5.0->0.0
RESULT causal_temp_leaks=26 publications     cells_holding=5 of 55   holds_fraction=0.091
RESULT per_cell_min=0 per_cell_max=6         loo_drop_max=20
```

### Perturbation: the number moves

Executed, both directions the finding states.

- **(b) production edit.** `dhw_temperature` 55.0 → 50.0 moves
  `climate.heat_pump_optimizer|attr.dhw_temperature` 55.0 → 50.0 **in
  `coord_minimal`, where hot water is not configured at all**, and moves 87
  distinct publication sites in `coord_dhw+none` including
  `mixed_hot_water|state`, `|attr.litres_40c`, `|attr.shower_minutes`,
  `|attr.tank_temperature` and `thermal_battery_charge|attr.components[]`.
- **(a) config.** In all five `probes` cells exactly **one** leaf moves and it
  is `optimization_status|attr.solve_time_ms` — measurement noise, not a value.
  The null control passes cleanly.
- `outdoor_temperature` 5.0 → 0.0 moves `outdoor_temperature_optimizer|state`,
  `climate|attr.outdoor_temperature`, `estimated_cop|state`,
  `thermal_battery_charge|state` and 15 further battery attributes — **only** in
  the five `weather_only` cells. In the other 50, again only `solve_time_ms`.

Not computed from constants.

### Scope across the feature space

| axis varied | dhw default leaks | outdoor default leaks |
|---|---|---|
| none, dhw, two_zone, valve_storage, wood, ecl110, pv, capacity_tariff, tuya, weather_only | holds | holds only in `weather_only` |
| probes (control) | 0 | 0 |
| **fraction** | **50/55 = 0.909** | **5/55 = 0.091** |

The dhw/slab/buffer/lower-floor paths are feature-independent: they hold in
every cell that lacks the corresponding probe, across all eight axes I was
asked to vary. The **outdoor and indoor** paths hold in 1 feature column of 11.

That 0.091 is a **grid artefact in the repo's favour, not the finder's**:
`matrix.py:cell_config` adds `ROOM_CONFIG` (indoor + outdoor thermometers) to
16 of the 17 features, so the grid exercises the no-outdoor-thermometer install
in exactly one column. The code is ungated in all 55 cells; it simply has a
reading in 50 of them. The rate is a property of the grid, not of the field.

**Leave-one-out.** Dropping the single most favourable cell: 4033 → 3835 (dhw),
26 → 20 (outdoor). The finder's own LOO (1132 → 1108) reproduces from its
results file. No cell carries the finding.

### Attacks I ran

1. **Contention** — all counts; two runs identical; `thread_factor` 1.000.
2. **Reachability in real HA vs the stub** — `FakeHass.async_add_executor_job`
   only affects *when* the solve runs, not what `_build_data_dict` writes. The
   leak is in property getters read synchronously; no executor boundary is
   involved. It is reachable.
3. **The repo's own baseline corroborates it, with no matrix at all.** A live
   `tests/golden.py:_capture_coordinator(coord_dhw)` returns
   `reading_ok = {upper_floor: False, lower_floor: False, floor_return: False,
   slab: False, buffer_tank: False, dhw_temperature: False}` **in the same
   payload as** `dhw_mixed = {litres_40c: 300.0, tank_temperature: 55.0,
   shower_minutes: 37.5}`. The committed fixture `tests/golden/coord_dhw.json`
   records `dhw_temperature: 55.0`, `buffer_tank_temperature: 40.0`,
   `slab_temperature: 22.0` as the expected payload.
4. **Severity by consequence** — earned, and if anything understated.
   `README.md:317` states the contract the code breaks: *"Mixed Hot Water | L |
   … | Unavailable without mixed-water data"*, and the entity is available
   publishing 300 L on a `VOLUME_STORAGE` device class from a tank nothing
   measures. I reproduced the outdoor consequence exactly:
   `coord_minimal+weather_only` publishes `outdoor_temperature_optimizer = 5.0`
   and `estimated_cop = 3.32` while `space_plan.forecast[0].outdoor = -5.0`;
   the same cell with the thermometer publishes `-3.0` and `2.62`. The README's
   framing ("Outdoor temperature *as the optimizer sees it*") does not defend
   it — the optimizer sees −5.0.
   The finder's own note that "no money is decided on these publications" is
   conservative: under the same perturbation `predicted_cost|state`,
   `predicted_savings|state`, `savings_percentage|state`,
   `dhw_heating_cost|state` and 21 further money-bearing leaves move too (via
   the solve, which is legitimate modelling — but it means the default is not
   cosmetic).
5. **Sites the finder missed** (all executed): `dhw_heating_plan|attr.forecast[].dhw_temp`,
   `dhw_heating_schedule|attr.dhw_schedule[].dhw_temp`,
   `optimization_schedule|attr.schedule[].{room,upper,lower}_temp`,
   `thermal_battery_charge|attr.components[].{stored_kwh,soc_percent,standing_loss_kw}`,
   `thermal_battery_energy|attr.*`, `estimated_cop|state`. The finding
   understates its own site list.

### The proposed fix against the repo's gates

I executed two of the proposed gates as real production edits and ran
`tests/entities.py` on each.

| edit | `tests/entities.py` | effect on the metric |
|---|---|---|
| `IndoorTempSensor.available` gated on `reading_ok["upper_floor_temperature"]` | **ALL 538 ENTITY CHECKS PASSED** | `default_temperature_leaks` 188 → 186 on `coord_minimal` (exactly the 2 indoor publications) |
| `MixedHotWaterSensor.available` also gated on `reading_ok["dhw_temperature"]` | **ALL 538 ENTITY CHECKS PASSED** | `default_temperature_leaks` 272 → 208 on `coord_dhw` |

Working tree restored from backup after each; `git diff` clean.

Two things the fixer must be told, neither fatal:

- **The Indoor gate collides with an argued standing decision.**
  `tests/entities.py` records, in its own words, *"a stale indoor thermometer
  publishes the model default, as before"* with the rationale *"Indoor
  Temperature is deliberately left ungated here: it is the integration's primary
  entity and its staleness already has a home in the Input Problem binary sensor
  and the repair issues."* My edit does not **fail** that check — the assertion
  is on the payload key, and the only entity case in the suite has the indoor
  thermometer configured and reading. But the suite has **no case at all for the
  thermometer being unconfigured**, which is precisely the leak. The fix must
  either engage that argument or scope itself to the unconfigured case.
- **The payload-side half drifts goldens.** Gating `coordinator._dhw_mixed_water`
  (rather than the entity) moves `tests/golden/coord_dhw.json` and
  `coord_all_features.json` — both carry the `dhw_mixed` block with
  `tank_temperature: 55.0`. The finder declared this conditionally ("only if the
  coordinator changes what it publishes"), which is honest. The **entity-side**
  variant, which I executed, drifts nothing.

### Vote

**`verify` (severity `high`).**
Decisive number: `causal_temp_leaks=4033` publications causally downstream of
`ThermalState.dhw_temperature`'s constructor default, holding in **50 of 55**
cells (0.909) and falling to **one noise leaf** in all five `probes` control
cells.

Title is accurate but understates: I measured more than five ungated paths.
Suggested: *"ThermalState constructor defaults are published as temperatures
through the climate entity, Mixed Hot Water, the thermal-battery view, both
plan sensors and the Indoor/Outdoor sensors."*

---

## D8-02 — numpy scalars reach entity attributes at "three sites"

### My own number, my own metric

> **Metric (mine, one line).** The set of distinct (entity, attribute-root)
> sites carrying an `np.generic`/`np.ndarray` in `extra_state_attributes` after
> one solved cycle, plus states that are numpy scalars — and how many of those
> sites survive each **single** one-line production fix applied on its own.

Harnesses `numpy_probe.py` (spies on `HeatPumpOptimizer.optimize`, walks the
result dataclass and every entity) and `numpy_scope.py` (55 cells).

```
cell=coord_minimal+valve_storage  fix=none
RESULT result_numpy_fields=3
   result.deferred_energy_cost::float64
   result.predicted_savings::float64
   result.solar_gain_trajectory[]::float64 (92/96)
RESULT numpy_attribute_sites=3      RESULT numpy_states=1
```

At 12:00 (`--noon`) there are **4** attribute sites: the daylight
`heat_pump_action|attr.solar_gain_kw` the finder verified out of band appears,
`float64`.

### The seat-3 question: are the three sites distinct, or does one path feed the others?

**They are not three causes. They are two, and one of them feeds two sites.**
Measured by applying each one-line fix *alone*:

| single edit | attribute sites left | numpy states left |
|---|---|---|
| baseline (00:00) | 3 | 1 |
| `float()` on `HeatPumpOptimizer._deferred_energy_cost`'s return | **1** | **0** |
| `float()` on `ThermalModel.compute_solar_gain`'s return | **2** | 1 |
| both | 0 | 0 |
| baseline (12:00) | 4 | 1 |
| `compute_solar_gain` alone (12:00) | **2** | 1 |

- **Cause A** — `_deferred_energy_cost` returns numpy (declared `-> float` at
  `optimizer.py:5061`). `savings = baseline_cost - predicted_cost - deferred_cost`
  (`optimizer.py:2910` and `:4847`) inherits it, so `predicted_savings` is
  numpy *only because* `deferred_cost` is. One edit kills two of the three
  reported attribute sites **and** the state.
- **Cause B** — `compute_solar_gain` returns numpy for `sr > 0`
  (`thermal_model.py:1440`), feeding the single construction of
  `solar_gain_trajectory` at `optimizer.py:1534`. That list is read again at
  `optimizer.py:5697` for `solar_gain_kw`; `grep` confirms 1534 is the only
  construction site in the package. One edit kills both solar sites.

Further, `sensor.heat_pump_optimizer_predicted_savings|state` is **not
independent evidence**: `numpy_scope.py` shows it and
`climate|attr.predicted_savings` present in exactly the same 5 cells — it is the
same payload key `predicted_savings` read by a second entity. `numpy_state=30`
is a second reading of site 3, not a fourth site.

### Perturbation and scope

Perturbation executed, `to_zero` reached: `--fix both` gives
`numpy_attribute_sites=0`, `numpy_states=0`.

```
RESULT cells=55
RESULT site_fraction optimization_schedule|attr.schedule[].solar_gain = 55/55 = 1.000
RESULT site_fraction climate|attr.predicted_savings                   =  5/55 = 0.091
RESULT site_fraction predicted_savings|state                          =  5/55 = 0.091
RESULT site_fraction savings_percentage|attr.deferred_energy_cost     =  5/55 = 0.091
RESULT cells_with_any_numpy=55/55 = 1.000
RESULT loo_drop_max_cell=66 (of 70 site-occurrences)
```

One site holds everywhere; the other three hold in 9 % of my grid, always the
same cells (my grid carries `valve_storage` as its only buffer-store feature;
the finder's 15/85 = 0.176 adds `two_tank` and `coil` — same phenomenon at
higher grid density). Leave-one-out barely moves the aggregate because the
dominant site is universal: the finding does not rest on one cell.

### Attacks

1. **Severity by consequence — I executed what could be executed here.**
   `isinstance(np.float64(1.25), float)` is `True` and stdlib `json.dumps`
   serialises it **natively, with no hook**; `np.int64` is not an `int` subclass
   and does raise. Every site I measured is `float64` — the type every encoder
   handles. The dangerous type is not present at any measured site.
2. **Nobody on this box can execute the real consequence.** There is no
   `homeassistant` package in the venv (only `tests/hastub`) and no `orjson`.
   The claim about `json_encoder_default` is an argument, not a number, for the
   finder and for me. The finder said so and set `low` — correctly.
3. **Golden drift.** `golden.py:r()` maps `np.floating` → `round(float(v),
   PRECISION)`, so the fix is byte-inert for the fixtures. "No golden drift
   expected" holds by construction, not by luck.
4. **Internal consistency** — the same `OptimizationResult(...)` call converts
   its neighbours explicitly (`valve_target_schedule=[float(v) for v in …]`,
   `wood_temp_trajectory=[float(v) for v in …]`, `.tolist()` on four arrays) and
   skips `solar_gain_trajectory` three lines later. `_plain_types` exists at
   `coordinator.py:416` with the exact policy the finding quotes, applied at
   exactly one call site (`coordinator.py:7048`, `predictive_info`). The claim
   about the stated policy is correct.

### The proposed fix against the repo's gates

**The `optimizer.py` branch of the proposal is wrong on both halves.** The
finding proposes "`optimizer.py` lines 1534 and 5697":

- `:5697` is **redundant** — it reads the list built at `:1534`; fixing 1534
  fixes it (measured at noon: `compute_solar_gain` alone takes 4 sites → 2,
  killing both solar sites).
- The pair is **incomplete** — measured, it leaves `numpy_attribute_sites=2`
  and `numpy_states=1`, because neither line touches `_deferred_energy_cost`.

Only the `_plain_types` branch (wrapping *both* the schedule list and the result
scalars) or a `float()` at `optimizer.py:5061` closes cause A. A fixer following
the `optimizer.py` route as written would ship a fix for one third of the
finding and mark it done.

### Vote

**`verify` (severity `low`, class `hygiene`)** — the count is real, reproduced
by two independent metrics, the perturbation reaches zero, and the repo's own
stated policy is bypassed. Severity stays at the floor: every measured value is
a `float` subclass that serialises natively.

Corrected title: *"numpy scalars reach entity attributes from two ungated
returns (`_deferred_energy_cost`, `compute_solar_gain`), surfacing at three
attribute sites at night and four in daylight."* "Three sites" counts
publications, not causes, and "the Predicted Savings state" is the same payload
key as the climate attribute already counted.

---

## D8-03 — the legacy schedule sensors describe 6 of the plan's 24 hours

### My own number, my own metric

> **Metric (mine, one line).** The wall-clock span of
> `optimization_schedule.attrs.schedule` against the span of
> `space_plan.forecast`, read off the timestamps rather than counted.

```
schedule len 24  first 2026-01-15T00:00:00+00:00  last 2026-01-15T05:45:00+00:00
plan     len 96  first 2026-01-15T00:00:00+00:00
dhw_schedule len 24
```

24 steps × 15 min = **5 h 45 m of published schedule** against a 24 h plan, and
`README.md:286` reads *"| Optimization Schedule | — | The whole 24 h schedule,
in attributes | Not recorded |"*. The grammar claim also holds:
`sensor.py:998` is `f"{active_steps} heating periods"` and `sensor.py:1232` is
`f"{len(slots)} slots planned"`, neither with a singular branch.

### Perturbation: executed as a real production edit

I edited `coordinator.py` lines 7023–7094 in place, `[:24]`→`[:96]`,
`[1:25]`→`[1:97]`, `[0.0] * 24`→`[0.0] * 96`:

```
baseline  coord_minimal subset:  RESULT schedule_truncated=34
perturbed coord_minimal subset:  RESULT schedule_truncated=0
```

`to_zero` reached. Working tree restored from backup, `git diff` clean.

### Scope

Feature-invariant: `(schedule_len, plan_len) = (24, 96)` in **85 of 85** cells,
and 45 of 45 in my own grid across all eight axes. That is a hold fraction of
1.000 — but it also means the 85-cell matrix contributes nothing here. **The
count 170 is a cell counter, not a measurement**: its informative content is
entirely the pair (24, 96), obtainable from one cell. It moves under its own
perturbation, so it is not voided; but it should not be read as a magnitude.

### The proposed fix against the repo's gates

**The declared golden drift does not occur.** The finding declares
`expected_golden_drift: tests/golden/coord_*.json (schedule, dhw_schedule
length) if the slice changes`. Measured:

```
coord_minimal schedule 0  dhw_schedule 0
coord_dhw     schedule 0  dhw_schedule 0
coord_all_features schedule [] dhw_schedule [] optimization_status "not_run"
```

`_capture_coordinator` never calls `async_run_optimization`, so every committed
`coord_*` fixture stores an empty schedule. Changing the slice drifts nothing.
This is an **over**-declaration — harmless to safety, but it would send a fixer
hunting a drift that does not exist, and it is the kind of unverified claim the
protocol exists to catch.

**A real cross-finding hazard the report does not name.** On the same subset the
D8-03 perturbation took `unserialisable_attributes` from **726 to 3140** —
quadrupling D8-02's numpy exposure, because the schedule grows from 24 to 96
entries each carrying a numpy `solar_gain`. **D8-02 cause B must be fixed before
or with D8-03**, or the slice fix multiplies the hygiene defect by four.

### Vote

**`verify` (severity `low`, class `hygiene`).**
Decisive number: the published schedule spans `00:00 → 05:45` against a 96-step
24 h plan, in 85/85 cells, against a README row promising "the whole 24 h
schedule"; the perturbation takes `schedule_truncated` 34 → 0.

---

## D8-04 — alphabetical order splits the hot-water family

### My own number, my own metric

> **Metric (mine, one line).** Per hand-listed family, the contiguous runs it
> occupies in the sorted sensor order minus one — reported additionally with
> multi-family entities de-duplicated, with families separated into
> prefix-coherent and purely semantic, and under leave-one-out over families.

Harness `ordering.py`:

```
RESULT sensors=55
RESULT family_splits_entity_id=15
   dhw=2 tariff=2 learning=2 accuracy=1 ecl110=0 pv=0
   card_headline=3 lifetime=2 two_zone=3 thermal_battery=0
RESULT entities_in_multiple_families=4 ['hot_water_cost','hot_water_energy','optimization_score','prediction_accuracy']
RESULT splits_prefix_families=7
RESULT splits_semantic_families=8
RESULT loo_drop_worst_family=12 (dropped card_headline=3)
RESULT families_with_zero_splits=3 of 10
RESULT family_splits_after_rename=13
   dhw: 2 -> 0
```

Reproduces 15 exactly, from my own recomputation.

### Perturbation

Executed on the translation keys (`hot_water_energy`→`dhw_energy`,
`hot_water_cost`→`dhw_cost_lifetime`, `mixed_hot_water`→`dhw_mixed_water`):
**15 → 13, with `dhw` 2 → 0.** Direction `down`, as stated. Not a constant.

### Scope — where this finding is weakest

Across 45 cells varying all eight axes I was given, the result is
`(55 sensors, 15 splits, dhw 2)` in **45 of 45**. Every sensor is always
constructed; only availability varies. So the finding holds in 100 % of cells
**and the matrix is decorative for it** — it is a static property of `sensor.py`
plus the three translation files, readable from one roster.

The real attack is on the aggregate, and it lands:

1. **The 15 double-counts.** Four entities sit in more than one family;
   `hot_water_cost` and `hot_water_energy` generate splits in *both* `dhw` and
   `lifetime`. `accuracy` = {`prediction_accuracy`, `optimization_score`} is
   entirely a subset of `learning` ∪ `card_headline` — it is not an independent
   family, and its 1 is counted anyway.
2. **8 of the 15 splits are family-definition artefacts.** `card_headline` (3),
   `tariff` (2), `learning` (2) and `accuracy` (1) are semantic groupings that
   *no* naming scheme sorts adjacent: `card_headline` is {`predicted_savings`,
   `savings_percentage`, `optimization_score`, `plan_narrative`} — four
   unrelated user-facing names. Demanding contiguity there measures the
   hand-list, not the naming.
3. **Leave-one-out over families:** dropping the single most favourable family
   (`card_headline`, 3) takes 15 → 12, a 20 % swing on one arbitrary list entry.
   Three of ten families are already at zero.
4. Only **7 of 15** splits sit in prefix-coherent families, and the finder's own
   perturbation removes only **2** of them.

The finder pre-declared this limitation ("Ordering families are hand-listed; a
different grouping gives a different split count"), which is why I weaken the
aggregate rather than the finding.

### Vote

**`verify` (severity `low`, class `hygiene`)** — the claim the title actually
makes is executed and true.
Decisive number: the DHW family occupies **3 contiguous runs** in the sorted
entity-id order (`dhw_* | hot_water_cost, hot_water_energy | mixed_hot_water`),
and the stated rename collapses it to **1** (`dhw` 2 → 0).

Corrected title: *"Alphabetical order splits the hot-water family into three
runs (`hot_water_*`/`mixed_hot_water` vs `dhw_*`); five other hand-listed
families also split, but 8 of the 15-split aggregate comes from groupings no
naming scheme could sort adjacent."* Two corrections to the current title: it
says "and four others" where six other families are non-zero, and the headline
15 should not be quoted without the double-counting and the semantic-family
caveat.

---

## Nothing voided

Every one of the four findings moved under its own stated perturbation, executed
by me:

| finding | perturbation | measured |
|---|---|---|
| D8-01 | `ThermalState.dhw_temperature` 55.0 → 50.0; `probes` config | 87 sites move in `coord_dhw+none`; 1 noise leaf in all 5 `probes` cells |
| D8-02 | `float()` on the two numpy returns | `numpy_attribute_sites` 3 → 0, `numpy_states` 1 → 0 |
| D8-03 | `[:24]` → `[:96]` in `coordinator.py` | `schedule_truncated` 34 → 0 |
| D8-04 | rename three translation keys | `family_splits_entity_id` 15 → 13, `dhw` 2 → 0 |

No harness is measuring a constant. The one number that is *effectively*
constant across the grid — D8-03's 170 — nonetheless moves under a production
edit, so it is not void; it is simply a cell counter and should not be read as a
magnitude.

## Fix defects to carry forward

1. **D8-02's `optimizer.py` fix route is redundant at one line and incomplete at
   both** — measured, it leaves 2 of 3 sites and the numpy state alive.
2. **D8-03's declared golden drift does not exist** — the `coord_*` fixtures
   store `schedule: []` because `_capture_coordinator` never solves.
3. **D8-01's Indoor gate contradicts an argued standing decision** recorded in
   `tests/entities.py`, though it passes all 538 checks; the suite has no case
   for an unconfigured indoor thermometer, which is the leak.
4. **D8-03 must be sequenced after D8-02 cause B**, or the slice fix quadruples
   the numpy exposure (measured 726 → 3140).

## Incidental, outside D8's scope

The committed `tests/golden/coord_dhw.json` carries 149 payload keys where a
live `_capture_coordinator` produces 152, and the fixture lacks `reading_ok`
entirely. The fixtures are behind the coordinator on that key. I did not pursue
it; it belongs to whoever owns fixture freshness.
