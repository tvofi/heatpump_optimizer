# D8 — verifier seat 1 (stance: OWN-HARNESS)

- baseline: `c398fc84eec25fc44b60d74aae05b9a2da205884`
- worktree: `/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D8-1`
- scratch: `/private/tmp/claude-501/audit-scratch/D8-1`
- machine: MacBookAir10,1 (Apple M1, 8 GB), numpy 2.4.6 / scipy 1.17.1 on
  OpenBLAS, five BLAS thread variables pinned to 1 before any numpy import.
  `thread_factor=1.000` on every run. `load1` 8.16–17.85 throughout: the box
  was under a full fan-out, so **every number in this report is a count, a
  dtype or a published value — no timing, CPU or RSS number is reported or
  relied on.**
- Python: `tvofi-bookish-pancake/.venv/bin/python` (3.11.5). Chosen because it
  is the only interpreter on this box with **orjson (3.12.0)** installed
  alongside the same numpy/scipy as the framework python. That matters: the
  finder's report states "orjson is not installed in the venv: serialisability
  is checked by a walk that applies orjson's rules". D8-02 is re-measured here
  against the real library.
- No `git checkout/commit/fetch/push`. The worktree is clean; the finder's
  harness was copied in to run it and removed afterwards (a copy is kept at
  `scratch/finder_matrix_copy.py`).

## 0. Re-run of the finder's harness

```
PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python tools/audit/round2/D8/matrix.py
```
(log: `scratch/rerun_full.log`)

**Every RESULT reproduced exactly, to the digit**, against the header's stated
expectations:

| RESULT | header | my re-run |
|---|---|---|
| `cells` / `entities` / `snapshots` | 85 / 65 / 11050 | 85 / 65 / 11050 |
| `default_temperature_leaks` | 1132 | **1132** |
| `outdoor_default_published` | 10 | **10** |
| `numpy_attribute_sites` / `unserialisable_attributes` / `numpy_state` | 3 / 3630 / 30 | **3 / 3630 / 30** |
| `schedule_truncated` | 170 | **170** |
| `family_splits_entity_id` / `_name_en` / `_name_sv` | 15 / 15 / 16 | **15 / 15 / 16** |
| every zero-valued check (`exceptions`, `type_violations`, `metadata_violations`, `nonfinite_attributes`, `stale_entities`, `follows_payload_mismatch`, `unknown_where_data_exists`, `duplicate_unique_ids`, `bad_entity_ids`, `no_icon`, `translation_key_mismatch`, `sv_untranslated`) | 0 | **0** |

`RESULT thread_factor=1.000`, `RESULT load1=8.16`. All 85 cells solved
`optimal` in both cycles. Reproduction is not in question for any of the four
findings; what follows attacks the *meaning* of the numbers, not their
arithmetic.

## 1. My own harnesses and their metric definitions

Three harnesses, all in `scratch/`, all deliberately on a different route from
`matrix.py`. Where the finder built 85 hand-specified cells over
`golden.py:coordinator_scenarios()` and asked the coordinator's **own
`reading_ok` self-report** whether a number was a reading, I build installs
from `tests/entities.py:_honest_coordinator` — the repository's own real
coordinator fixture — and decide the same question **causally**, by perturbing
the `ThermalState` dataclass defaults and observing which published values
move. That distinction is the whole point of this seat: `reading_ok` is part of
the code under audit, so a metric that consults it cannot detect the case where
`reading_ok` says "measured" and the number is still a default.

- **`own_matrix.py`** — *Metric: over five documented, config-flow-reachable
  installs, the number of (install, entity, state-or-attribute) publications
  that are visible to a user (`available is True`) and provably caused by a
  `ThermalState` constructor default, proved by re-running the identical
  install with `ThermalState.__init__.__defaults__` rebound one field at a time
  and diffing every published leaf.* Entities come through the real
  `async_setup_entry` of all five platforms (`sensor`, `binary_sensor`,
  `climate`, `switch`, `button`), via `entities.py:collect`'s pattern.
- **`own_serialise.py`** / **`probe_numpy3.py`** — *Metric: the number of
  entity attribute dicts and states that Home Assistant's own serialisation
  path fails to serialise, where that path is the real
  `orjson.dumps(payload, option=OPT_NON_STR_KEYS, default=json_encoder_default)`
  that `homeassistant.helpers.json.json_bytes` is and that the recorder and the
  websocket API call — reported with the exact dtype of every numpy leaf.*
- **`attacks.py`**, **`persist.py`**, **`order_fix_check.py`** — the
  perturbations, the decay test, the mitigation check and the proposed-fix
  check.

---

## D8-01 — `ThermalState` constructor defaults published as temperatures

**Severity claimed: high. My vote: `verify` (high), with the title corrected.**

### Re-run
`RESULT default_temperature_leaks=1132`, `RESULT outdoor_default_published=10`
— both exact.

### My own number
`RESULT default_leak_publications=116` over 5 installs × 1 cycle, of which
`RESULT default_leak_states=17` are user-visible **states** (not attributes).
Per install: `ordinary_dhw_no_tank_probe` 23, `no_dhw` 15, `weather_only` 42,
`fully_probed` 13, `probes_gone_stale` 23.

The two numbers are **not comparable as totals** — 1132 is over 85 cells × 2
cycles under a flag-based definition, 116 is over 5 installs × 1 cycle under a
causal definition — so both are recorded, as the contract requires. What is
comparable is the **site list**, and there my harness independently confirms
**every site the finder names**, by a route that never reads `reading_ok`.

### The one that matters, stated as a user would read it

Install: hot water configured (tank volume set), no tank thermometer. The
repository's own test file calls this "the ordinary install, not a corner case"
(`tests/entities.py:727`); `config_flow.py:975-989` makes every probe field
`vol.Optional`; `README.md:144` says "indoor and outdoor thermometers, tank
probes, a power meter — is optional".

```
  binary_sensor.input_problem.is_on   = False
  input_problem attrs                 = {'summary': 'ok', 'stale_inputs': [], 'problems': [], ...}
  sensor DHW Temperature .available   = False          <- correctly gated
  sensor Mixed Hot Water .available   = True
  sensor Mixed Hot Water .state       = 270.0          (device_class VOLUME_STORAGE, unit L)
  sensor Mixed Hot Water .attributes  = {'litres_40c': 270.0, 'tank_temperature': 55.0,
                                         'shower_minutes': 33.8}
RESULT ordinary_install_is_warned=0
```

A user reading this dashboard believes their tank holds **270 litres of 40 °C
shower water, 33.8 minutes of shower**, measured, right now. Nothing measures
it. The 55.0 is `ThermalState.dhw_temperature`'s constructor default
(`thermal_model.py:988`) and `coordinator._dhw_mixed_water` divides it straight
into litres. The entity that publishes the *same tank temperature* — DHW
Temperature — is correctly unavailable two rows above it.

**It does not decay.** `persist.py` ran 20 real
`_update_current_state` + `async_run_optimization` cycles on that install:

```
  cycle  1  dhw_temperature=55.0  mixed={'litres_40c': 270.0, 'shower_minutes': 33.8}
  cycle 20  dhw_temperature=55.0  mixed={'litres_40c': 270.0, 'shower_minutes': 33.8}
RESULT tank_default_decays=0
```

**Reachability, which the seat was asked to settle.** Not a
test-stub artefact and not a pre-first-publish default:

1. `_update_current_state` writes `dhw_temperature` only under `if dhw.ok`
   (`coordinator.py:5141-5144`). With no configured entity there is no reading,
   ever, so the default is what is published on cycle 1 and on cycle 20.
2. The config flow permits it: all of `CONF_INDOOR_TEMP_ENTITY`,
   `CONF_OUTDOOR_TEMP_ENTITY`, `CONF_DHW_TEMP_ENTITY` are `vol.Optional`
   (`config_flow.py:975, 976, 989`). The README documents them as optional.
3. **The stated mitigation does not cover it.** `tests/entities.py:800` defends
   the ungated Indoor sensor with "its staleness already has a home in the
   Input Problem binary sensor and the repair issues". That defence is
   `InputHealth.missing_keys` (`inputs.py:126-133`), which filters on
   `r.entity_id` — so an *unconfigured* input is structurally invisible to it.
   Measured above: `input_problem.is_on = False`, `summary: 'ok'`,
   `problems: []`, while Mixed Hot Water reads 270 L. The user is not warned by
   anything, anywhere.
4. `FakeHass.async_add_executor_job` running inline is irrelevant here: this
   path is a property read on a data dict, not an executor hand-off.

### Attacks run

**(a) Does the finder's stated config perturbation hold? No — not on the first
cycle.** The finding says "(a) Config: add the `probes` sensors — the count is
0 in all five `probes` cells (to_zero)". Under my causal metric,
`fully_probed` (tank 48.2, buffer 36.5, floor return 27.5, downstairs 20.1, all
reading OK) still shows **13** publications that move with a `ThermalState`
default — all of them via `slab_temperature`, which drives
`sensor.slab_temperature_estimated`'s state, the climate `slab_temperature`
attribute and 8 thermal-battery numbers **including the Thermal Battery Charge
state**. `SlabTempSensor` is `available` there, because
`reading_ok["slab_temperature"] = floor_return_ok = True`. So the coordinator's
own map says "measured" while the number provably still carries the
constructor seed. **The finder's flag-based metric cannot see this class at
all**; it is the payoff of measuring causally.

**(b) But is it a standing defect or a transient? Transient.** `attacks.py`
ran the slab integrator forward:

```
  cycles= 1  slab(default 22.0)=26.5500  slab(default 17.0)=25.0500  gap=1.5000
  cycles= 2  gap=0.4500
  cycles= 5  gap=0.0122
  cycles=10  gap=0.0000
  cycles=30  gap=0.0000
RESULT slab_seed_gap_cycle1=1.5000 C
RESULT slab_seed_gap_cycle30=0.0000 C
```

`update_slab_from_return_temp` washes the seed out inside ten cycles. So the
finder's "probes → 0" is right in steady state and wrong on the first cycle by
1.5 °C. Recorded as a correction to the perturbation, not as a defeater: it
weakens the *perturbation's* wording and does not touch the tank, buffer,
indoor or outdoor cases, which never decay.

**(c) The title over-states by 45%.** Bucketing the finder's own 1132 by field
(`matrix_results.json`):

| field | count | of which `weather_only` |
|---|---|---|
| `components.slab` | 160 | 10 |
| `slab_temperature` | 160 | 10 |
| `lower_floor_temperature` | 160 | 10 |
| `components.lower_floor` | 64 | 2 |
| `dhw_temperature` | 160 | 10 |
| `components.buffer_tank` | 160 | 10 |
| `components.dhw_tank` / `tank_temperature` | 76 / 76 | 4 / 4 |
| `state` | 86 | 14 |
| `current_temperature` / `upper_floor_temperature` | 10 / 10 | 10 / 10 |
| `components.house` / `components.upper_floor` | 8 / 2 | 8 / 2 |

In every cell **except** `weather_only`, `slab_temperature` is
`room + 1.0 = 22.4` and `lower_floor_temperature` is the live indoor reading
21.4 — not the 22.0 / 21.0 constructor defaults. My causal test agrees: in
`ordinary_dhw_no_tank_probe` neither climate `slab_temperature` nor
`lower_floor_temperature` nor `components.slab` / `components.lower_floor`
moved when I perturbed *any* default; they appear only in `weather_only`,
where the room temperature genuinely is the default. So

> **512 of the 1132 (45.2%) are a live thermometer reading re-labelled, not a
> `ThermalState` constructor default. 620 are constructor defaults.**

The finding's `claim` field is broad enough to cover both ("the constructor
default … **or a number derived from it**"), and both are the same defect class
— a published number that is not a measurement of the thing it is named after —
so this corrects the **title**, not the finding.

**(d) Severity by consequence.** Not `critical`: I checked whether the
published outdoor default reaches the money. `_current_state.outdoor_temperature`
feeds the solve horizon only through `coordinator.py:5837`, which is the
`if not self._weather_forecast:` branch — and a weather entity is *required* by
the config flow and the README's Requirements section. With a forecast present
the plan is solved on the forecast, so the 5.0 is published but not spent. The
finder's own reasoning here is correct. `high` is earned by the brief's own
rubric ("a wrong published value"): Mixed Hot Water is a `VOLUME_STORAGE`
measurement that a user reads as litres in their tank, it is wrong, it never
moves, and nothing warns.

### Vote
**`verify` (high).** Decisive number: `Mixed Hot Water` available, state
**270.0 L / 33.8 shower minutes / tank_temperature 55.0, unchanged over 20
solve cycles**, while `DHW Temperature` is unavailable and
`RESULT ordinary_install_is_warned=0`, in a config the README calls optional.

Two corrections for the register: the title should say "constructor defaults
and seeded stand-ins" (512/1132 are the latter), and the `probes → 0`
perturbation holds only from cycle ~10 (`slab_seed_gap_cycle1=1.5000 C`).

---

## D8-02 — numpy scalars reach entity attributes at three sites

**Severity claimed: low (hygiene). My vote: `verify` (low).**

### Re-run
`RESULT numpy_attribute_sites=3`, `unserialisable_attributes=3630`,
`numpy_state=30` — all exact.

### My own number, by real serialisation
The seat's instruction was to serialise the way the recorder does rather than
inspect types. `own_serialise.py` calls the real orjson 3.12.0 with a faithful
`json_encoder_default`, over every attribute dict and state of every entity of
every platform on four **solved** coordinators (prices, weather and irradiance
injected `_capture_coordinator`-style; all four `optimal`):

```
RESULT payloads_serialised=496
RESULT ha_orjson_failures=0
RESULT numpy_attribute_sites_mine=2
RESULT numpy_leaf_values=100
RESULT numpy_dtypes={"float64": 100}
```

The two sites there are `optimization_schedule|attrs|schedule[].solar_gain` and
`heat_pump_action|attrs|solar_gain_kw`. The finder's third site needs the
buffer-store solve path, which my first configuration missed; `probe_numpy3.py`
reproduces it with the finder's own `_VALVE` overlay
(`CONF_MIXING_VALVE_MODE="manual"`, buffer 750 L, two-zone masses):

```
  payload[predicted_savings]     = np.float64(4.697857096423019)   is_float_subclass=True
  payload[deferred_energy_cost]  = np.float64(-0.08137158372786032) is_float_subclass=True
  NUMPY predicted_savings|state                        float64  ha_orjson=ok
  NUMPY savings_percentage|attrs.deferred_energy_cost  float64  ha_orjson=ok
  NUMPY climate|attrs.predicted_savings                float64  ha_orjson=ok
  NUMPY heat_pump_action|attrs.solar_gain_kw           float64  ha_orjson=ok
  NUMPY optimization_schedule|attrs.schedule[].solar_gain  float64  ha_orjson=ok  (×24)
RESULT numpy_leaves_in_buffer_store_cell=28
```

So **all three sites reproduce, and all of them are `np.float64` — zero of
them raise.** 0 failures in 496 payloads.

### The control that decides the severity
```
  ORJSON-CONTROL np.float64 -> {"v":1.5}
  ORJSON-CONTROL np.float32 -> RAISES TypeError: Type is not JSON serializable: numpy.float32
  ORJSON-CONTROL np.int64   -> RAISES TypeError: Type is not JSON serializable: numpy.int64
  ORJSON-CONTROL np.ndarray -> RAISES TypeError: Type is not JSON serializable: numpy.ndarray
  ORJSON-CONTROL np.bool_   -> RAISES TypeError: Type is not JSON serializable: numpy.bool
```
`np.float64` subclasses Python `float`, so orjson hands it to the `default`
hook and HA's `if isinstance(obj, float): return float(obj)` converts it. Every
other numpy type on that path raises. The finder's own severity note said
exactly this and asked the judge to confirm the installed core's hook; **it is
confirmed**. The finding is a latent-hazard/hygiene item, not a live defect —
which is what `low` + `hygiene` means, so nothing to weaken.

### Perturbation
Stated: wrap in `_plain_types` → to_zero.
```
RESULT numpy_before=27
RESULT numpy_after_plain_types=0
  values unchanged: True
```
The number moves, in the stated direction, to zero, with identical values. The
proposed fix is therefore not algebraically the shipping code, and it changes
no published value (so no golden drift on `r()`-rounded fixtures).

### Attacks run
- Contention: not applicable — counts and dtypes.
- Grid artefact: the number is not a grid aggregate; it is a site list, and I
  reproduced the site list on a different set of configurations (2 of 3 in the
  first set, 3 of 3 with the buffer-store overlay). Dropping any one of my four
  cases leaves the two solar sites intact in all of them.
- Reachability in real HA vs the stub: this is the one place where the stub
  could have mattered, and it does not — the payload is built by
  `_build_data_dict` and read by property accessors; no executor boundary is
  involved. The real-HA question was "does the recorder choke", and the real
  library answers no.
- Harness gap named: the finder's `unserialisable_attributes=3630` is a
  per-value count under a hand-applied rule set and reads as "3630 things HA
  cannot serialise". The real library serialises all 3630. The count should be
  restated as "3630 numpy leaves, 0 of them unserialisable".

### Vote
**`verify` (low).** Decisive number: `RESULT ha_orjson_failures=0` over 496
payloads through the real `orjson.dumps(..., default=json_encoder_default)`,
with every one of the 100+28 numpy leaves an `np.float64` that the hook
converts — the phenomenon is real, the consequence today is nil, and the
severity already assigned is the honest one.

---

## D8-03 — the legacy schedule sensors describe 6 of the plan's 24 hours

**Severity claimed: low (hygiene). My vote: `verify` (low), with the aggregate
restated.**

### Re-run
`RESULT schedule_truncated=170` — exact.

### My own number
From `attacks.py`, on a solved ordinary install, reading the published
attributes rather than a length comparison:

```
  len(schedule)=24  len(dhw_schedule)=24  len(space_plan.forecast)=96
  schedule[0]  time = 2026-09-02T18:15:00
  schedule[-1] time = 2026-09-03T00:00:00
  plan[0]      t    = 2026-09-02T18:15:00
  plan[-1]     t    = 2026-09-03T18:00:00
```

*Metric: the wall-clock span the `optimization_schedule` attribute actually
covers, versus the span `space_plan.forecast` covers, on the same payload.*

**The 24 schedule entries span 5 h 45 min. The plan spans 23 h 45 min.**
`README.md:286` says of Optimization Schedule: "The whole 24 h schedule, in
attributes". The README claim is wrong by a factor of ~4. Confirmed
independently of the finder's length-ratio metric.

### Perturbation and the method attack
The finding's perturbation ("replace the `[:24]` slices with the horizon
length → to_zero") is a source edit whose effect is arithmetically certain, and
I did not spend a gate run on it. What I did test is the harder question the
contract asks: **is the harness measuring a constant?** `len(schedule)` is 24
and `len(space_plan.forecast)` is 96 in every cell of my four solved
configurations and in all 85 of the finder's, both cycles. So

> `schedule_truncated=170` carries exactly one bit: 85 cells × 2 cycles × "24 <
> 96, always". The 85-cell grid contributes nothing to it; leave-one-out is
> meaningless because every cell is identical.

That is not enough to void the finding — the harness does drive the real
`_build_data_dict` and reads real published lengths, and the doc/code mismatch
is genuine and measured — but the aggregate should be recorded as
**"24 steps / 5 h 45 min versus a documented 24 h, in 85/85 cells (100%)"**,
not as a count of 170, which invites the reader to think a rate was measured.

Severity check: the card and the plan sensors carry the full 96-step horizon
(`space_plan.forecast` above), so nothing a user acts on is truncated; only two
legacy attribute payloads and one README row are wrong. `low` / `hygiene` is
correct.

### Vote
**`verify` (low).** Decisive number: schedule span
`18:15 → 00:00` = **5 h 45 min** against `README.md:286`'s "the whole 24 h
schedule", with `len(space_plan.forecast)=96` on the same payload.

---

## D8-04 — alphabetical order splits the hot-water family

**Severity claimed: low (hygiene). My vote: `verify` (low) — and no executed
number supports more than hygiene.**

### Re-run
`RESULT family_splits_entity_id=15`, `family_splits_name_en=15`,
`family_splits_name_sv=16` — exact. I also recomputed the finder's metric
from **my own roster**, enumerated through my own `async_setup_entry` sweep
(`order_fix_check.py`): **15 / 15 / 16**, with the identical per-family
breakdown `{dhw 2, tariff 2, learning 2, accuracy 1, card_headline 3,
lifetime 2, two_zone 3}`. Independent agreement.

### My own number: what a user actually sees
"Runs − 1" says *that* a family is split. It does not say how far. My metric:
*for a family, the number of foreign entities a user scrolls past between its
first and its last member in the sorted list.*

```
RESULT sensor_roster=55
  ORDER entity_id  hot water  members=9  span=18  intruders=9
  ORDER name_en    hot water  members=9  span=18  intruders=9
  ORDER name_sv    hot water  members=9  span=46  intruders=37
RESULT max_foreign_entities_inside_a_family_span=37
```

In English, the nine hot-water sensors occupy rows 7–24 of 55, with these nine
strangers wedged inside: ECL110 Displace, ECL110 Effective Displace, Estimated
COP, Floor Heating Return Temperature, Heat Pump Action, Indoor Temperature
(Optimizer), Last Optimization, Lower Floor Temperature, Measured Power.
`Hot Water Cost (lifetime)` and `Hot Water Energy (lifetime)` sit at 18–19 and
`Mixed Hot Water` at 24, cut off from `DHW …` at 7–12.

In Swedish it is worse and *differently* worse: `Blandat varmvatten` at row 7,
`Rådgivare för varmvattenbörvärde` at 32, `Schema för varmvatten` at 33, and
the remaining six contiguous at 47–52.

### Attacks run

**(a) Is the metric a constant? Effectively yes.** The roster is identical
across every install I built:
```
  ordinary  sensors=55 ;  probed  sensors=55 ;  no_dhw  sensors=55
RESULT roster_identical_across_installs=1
RESULT distinct_rosters=1
```
So `family_splits_*` is a pure function of `sensor.py`'s translation keys and
three static JSON files. It cannot move with any payload, topology, feature
toggle or cycle. The finder's 85-cell × 2-cycle matrix contributes **nothing**
to this number, and its "perturbation" is a rename — i.e. editing the very text
the metric reads. That is the weakest evidence shape in the toolkit. It does
not void the finding (the roster is genuinely enumerated through
`sensor.async_setup_entry`, not asserted), but it caps what the finding can
claim.

**(b) Does the proposed fix work? Partly, and not in Swedish.** I applied the
finding's own rename (`hot_water_energy → dhw_energy`,
`hot_water_cost → dhw_cost_lifetime`, `mixed_hot_water → dhw_mixed_water`) to
my roster and recomputed the finder's metric:

```
== BASELINE                 id=15  en=15  sv=16
== AFTER-PROPOSED-RENAME    id=13  en=13  sv=15   {dhw: 1 (not 0), ...}
```

The finder's claimed "15 → 13" is confirmed for id and English order. But the
Swedish order only goes 16 → 15 and **the DHW family stays split**, because
Swedish display names sort by `Blandat…`, `Rådgivare…`, `Schema…` — words a
key rename cannot touch. Half the shipped locales get no benefit from the
proposed naming release. Worth putting in front of whoever costs it: this is a
breaking rename of three entity ids (the suggested object id follows the
translation key) for 2 of 15 splits in one language.

**(c) Does anything executed support more than hygiene?** No. I checked the
adjacent dimensions on the same roster: `type_violations=0`,
`metadata_violations=0`, `bad_entity_ids=0`, `duplicate_unique_ids=0`,
`translation_key_mismatch=0`, `sv_untranslated=0`, `first_hour_disabled=0`. No
state is wrong, no entity is unavailable, no unit or device class is affected,
no value a user or the card reads changes. The entire finding is the order of
rows in a list. `hygiene` at `low` is the ceiling, and it is where the finder
put it.

### Vote
**`verify` (low, hygiene).** Decisive number: **9 unrelated entities interleaved
into the 9-member hot-water family across rows 7–24 of a 55-row list** in both
entity-id and English-name order (37 of 55 in the Swedish span) — real, and
cosmetic. Recorded caveat: `distinct_rosters=1` means this metric is static
text and cannot move with any input, and the proposed rename leaves the Swedish
split standing (`sv: 16 → 15`, `dhw: 2 → 1`).

---

## Summary of votes

| id | claimed | vote | the number that decides it |
|---|---|---|---|
| D8-01 | high | **verify (high)** | Mixed Hot Water available at 270.0 L / 33.8 shower min / tank 55.0, unchanged over 20 solve cycles, `DHW Temperature` unavailable, `ordinary_install_is_warned=0` |
| D8-02 | low | **verify (low)** | `ha_orjson_failures=0` over 496 payloads through real orjson + HA's `json_encoder_default`; all 128 numpy leaves `np.float64`; `numpy_before=27 → numpy_after_plain_types=0` |
| D8-03 | low | **verify (low)** | schedule span `18:15 → 00:00` = 5 h 45 min vs README's "whole 24 h"; `space_plan.forecast=96` on the same payload |
| D8-04 | low | **verify (low)** | `family_splits 15/15/16` reproduced from my own roster; 9 foreign entities inside the hot-water span; `distinct_rosters=1` (static-text metric) |

Nothing voided. Four corrections carried to the judge:

1. **D8-01 title** over-states: 512 of 1132 (45.2%) are a live thermometer
   reading re-labelled, not a `ThermalState` constructor default.
2. **D8-01 perturbation** "`probes` → 0" holds only from ~cycle 10;
   `slab_seed_gap_cycle1=1.5000 C`, and 13 publications on a fully probed
   install still trace to the slab seed — a class the finder's `reading_ok`-based
   metric structurally cannot see.
3. **D8-02** `unserialisable_attributes=3630` should be restated as "3630 numpy
   leaves, 0 unserialisable"; the real library was run and it does not raise.
4. **D8-03** `schedule_truncated=170` is 85 × 2 × a constant; restate as a
   span (5 h 45 min vs 24 h documented) in 85/85 cells.

## Harnesses (all under `/private/tmp/claude-501/audit-scratch/D8-1/`)

| file | what it produces |
|---|---|
| `own_matrix.py` | `default_leak_publications`, `default_leak_states`, per-install causal leak lists, the ordering spans; writes `own_matrix_results.json` |
| `own_serialise.py` | `ha_orjson_failures`, `numpy_attribute_sites_mine`, `numpy_dtypes` over four solved coordinators |
| `probe_numpy3.py` | the buffer-store third numpy site, with per-leaf dtype and orjson verdict |
| `attacks.py` | the mitigation check, the slab decay series, the `_plain_types` perturbation, the schedule span, the roster invariance |
| `persist.py` | the 20-cycle tank-default persistence series |
| `order_fix_check.py` | the finder's metric recomputed on my roster, before and after the proposed rename |
| `rerun_full.log` | the finder's harness, re-run verbatim |

Run each as
`PYTHONPATH=tests/hastub <venv-python-with-orjson> <file>` from the repository
root, with the five BLAS thread variables pinned.
