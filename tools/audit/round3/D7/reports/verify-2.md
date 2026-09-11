# D7 verifier 2 of 3 — refute-first, line of attack: CONSEQUENCE and REACHABILITY

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1` (VERSION 6.3.20), export at
`.../audit-r3/verify/D7-2`, run from that root with `PYTHONPATH=tests/hastub`.
8-core Apple M1, python3 3.11.5 / numpy 2.4.6 / scipy 1.17.1, five BLAS thread
vars pinned to `"1"` before any numpy import in every harness.

**Everything below is a count, a ratio, a byte figure or a frequency in Hz.
No wall, CPU or RSS number appears, so contention cannot move any of it.** The
box was heavily shared throughout (`load1` between 5.29 and 41.78, quoted per
run below); `thread_factor` never exceeded 1.005. No `tests/stress.py`, no
`./tests/run.sh`, no gate lock was taken. Nothing in the tree under audit was
modified: both spot mutations ran in rsync copies under private temp roots, and
my own guard mutation is applied at the instance level.

Root rule for every harness I ran: **`Path.cwd()` / relative `sys.path`
inserts**, run from this export's root, so all of them measured *this* tree and
not some other checkout. (`tools/audit/README.md` warns that round-2's
`D7/sysid_plant.py` resolved from `__file__`; the round-3 harness does not —
it does `sys.path.insert(0, "tests")` and `subprocess ... cwd=dst`, both
cwd-relative. I confirmed the numbers move under a temp-copy mutation, which a
`__file__`-rooted harness could not have done.)

---

## 1. Re-run of the finder's three harnesses

Every RESULT line reproduced. Not one number differed.

| harness | `load1` | `thread_factor` | outcome |
|---|---|---|---|
| `tools/audit/round3/D7/sysid_plant.py` | 5.29 | 1.000 | **all 22 RESULT lines identical** to the header's expected values |
| `tools/audit/round3/D7/model_state_sentinel.py` | 5.60 | 1.005 | **all RESULT lines identical**, incl. `sentinel_total_writes=27062` to the digit |
| `tools/audit/round3/D7/learner_freeze_matrix.py` | 5.60 | 1.000 | **all RESULT lines identical**; the 6×7 arm table matched cell for cell |

Key reproductions, for the record:

```
excursion_ratio_worst=0.092   cells_below_stated_noise_0.10=6   admitted_cells=0
null_excursion_ratio_worst=0.996  null_admitted_cells=9  null_ua_bias_pct_worst=0.00
secondorder_ua_bias_pct_worst=0.000
perturb_massless_slab_ratio_worst=0.816  perturb_massless_slab_admitted=9
dead_instance_writes=1  dead_attr_bytes_retained=880  ast_readers_last_dhw_refused=0
guard_subject_present_before=0  guard_subject_present_after=0
perturb_deadwrite_removed_dead_instance_writes=0
freq_map_ingests_contaminated=5  clean_arm_ingests_freq_map=2
accuracy_ingests_contaminated=0  cop_scale_ingests_contaminated=0
perturb_gated_freq_map_ingests_contaminated=0  perturb_gated_clean_arm_ingests_freq_map=2
```

Raw output kept at `tools/audit/round3/D7/verify-2/rerun_*.txt`.

Instruments are sound. Every attack below is about what the numbers *mean*,
not about whether they are real.

---

## D7-01 — sysid: one-state identifier, two-state plant

**Finder severity `high`. My vote: `weaken` to `medium`.**

### My own number and metric

Harness: `tools/audit/round3/D7/verify-2/sysid_consequence.py`
(`load1` 5.93, `thread_factor` 1.000).

> **`adopted_scale_error_pct` = 100 × (`coordinator._house_heat_loss_scale`
> after the real `HeatPumpOptimizerCoordinator._adopt_system_identification()`
> has consumed the experiment's own `SysIdResult`, − 1.0), on a plant whose
> parameters ARE the coordinator's configured `_thermal_params`, so an honest
> experiment must return exactly 1.0 and every departure is error the feature
> injected into the parameter the plan actually uses.**

The finder's metric stops at `excursion_ratio` — how much of the allowance the
experiment spends. Mine continues the chain to the only place the experiment
touches anything persistent.

| arm | adopting cells (of 9) | worst `adopted_scale_error_pct` |
|---|---|---|
| production plant, noise-free (the default) | **0** | **0.00 %** |
| production plant, 0.10 °C sensor noise | **2** | **5.70 %** (both −, i.e. UA under-estimated; other 5.42 %) |
| NULL CONTROL — the one-state plant sysid assumes | 9 | **0.00 %** |
| PERTURBATION — `slab_thermal_mass` × 0.01 | 9 | 14.03 % |
| POSITIVE CONTROL — synthetic result at 1.5 × base UA, confidence 1.0 | — | `instrument_positive_control_scale = 1.5000` |

The positive control is load-bearing: the adoption call **does** move the scale
when handed a wrong answer, so the `0.00 %` on the noise-free arm is a
measurement and not a dead call path.

### Attack 1 — reachability (executed, not read)

`tools/audit/round3/D7/verify-2/sysid_consequence.py::reachability`, through the
real coordinator and the real `arm()`:

```
reach_default_install_arms = 0     # press the button on a default install: nothing arms
reach_default_const        = 0     # DEFAULT_SYSID_ENABLED is False
reach_opted_in_arms        = 1     # only after CONF_SYSID_ENABLED is set
reach_second_arm_same_day  = 0     # min_days_between_runs = 30
reach_second_arm_day31     = 1
reach_max_runs_per_year    = 12.17
reach_entry_points         = 1     # button.py:109 is the ONLY caller of async_arm_system_identification
```

It is off by default, it needs an explicit config opt-in *and* a button press,
and it can run at most ~12×/year — the UI string calls it "a one-off measurement
experiment" (`strings.json:799`). The finder said this; I have now executed it.

### Attack 2 — does it fail closed? (the crux of my assignment)

**Yes, on the default install.** `_adopt_system_identification` is the only
writer of the experiment's result, and what it writes is
`_house_heat_loss_scale` — *the same quantity the passive learner learns*
(`coordinator.py:3885`, `_apply_house_heat_loss_scale(new_scale)` from the
Newton step). When the experiment does not adopt, the passive learner's value
simply stands: `scale_unchanged_cells_noise0.00 = 9` of 9,
`adopted_scale_error_pct_worst_noise0.00 = 0.00`.

So on the noise-free default plant the feature is a **no-op**, not a
corruption. That is a materially smaller defect than the report implies.

**But it does not fail closed everywhere.** At 0.10 °C sensor noise — the level
`SysIdConfig`'s own docstring names as the case the fit must survive, and a
realistic figure for a 0.1 °C-resolution HA temperature sensor — 2 of 9 cells
adopt and write a **5.42 % and 5.70 % under-estimate** of the house UA. That is
a genuine fail-open path and it is why I do not drop below `medium`.

Three bounds on that 5.70 %, all executed or read from the code it lives in:

- clamped to `[HOUSE_HEAT_LOSS_SCALE_MIN, MAX] = [0.3, 3.0]` — 0.943 is far inside;
- confidence-weighted blend, not an overwrite (`coordinator.py:10614-10618`);
- the passive learner keeps taking Newton steps afterwards —
  `_house_heat_loss_samples` is set to `max(samples, int(20 × confidence))` = 7,
  and nothing in `_async_learn_house_heat_loss` gates on the sample count, so a
  7-sample seed is washed out by ordinary operation.

### Attack 3 — what the user pays for the night

```
experiment_kwh_delta_worst = 2.306 kWh   (heavy_old@-4C; the sign is NEGATIVE:
experiment_kwh_delta_best  = 0.087 kWh    the experiment spends LESS than the
experiment_override_hours  = 4.0 hours    plan, because the 2 h relax at zero
                                          power dominates a step the slab damps)
```

The plan override is **4.0 hours**, not the five the report's prose claims
(1 h settle returns `None` and leaves the plan running — `sysid.py` `PHASE_SETTLING`
returns `None` on both exits). The whole experiment spans 5 h. Minor, but the
report body overstates it.

Comfort cost: the largest room excursion anywhere on the grid is 0.5832 °C
against a 0.8 °C allowance, and `sysid._over_excursion` aborts the experiment
before the allowance is breached. The user loses one night's heating *shape*,
bounded at 2.31 kWh redistributed, and gets nothing back.

### Attack 4 — is the aggregate a grid artefact?

Re-aggregated from my own executed base table with each preset dropped in turn
(`tools/audit/round3/D7/verify-2/out_grid_dropout.txt`):

| subset | cells | worst ratio | below 0.10 °C | completed | **ADMITTED** |
|---|---|---|---|---|---|
| full grid | 9 | 0.092 | 6 | 1 | **0** |
| drop `heavy_old` | 6 | 0.092 | 3 | 1 | **0** |
| drop `light_new` | 6 | 0.092 | 6 | 0 | **0** |
| drop `typical_slab` | 6 | 0.099 | 3 | 1 | **0** |
| only `light_new` | 3 | 0.660 | 0 | 1 | **0** |
| only `heavy_old` | 3 | 0.099 | 3 | 0 | **0** |
| only `typical_slab` | 3 | 0.092 | 3 | 0 | **0** |

The load-bearing number (**0 adopted**) is invariant to every preset drop — it
is 0 in all seven subsets. The *headline* "6 of 9 below the noise level" **is**
composition-dependent (3/3 in each heavy preset, 0/3 in `light_new`), and a
judge should read it as "both heavy presets, never the light one" rather than
as a two-thirds rate. The finder's leave-one-out drops a single cell and does
not surface this.

### Attack 5 — reachable in real HA, or only through the stub?

The adoption path I drove is synchronous coordinator code with no executor
hop; `FakeHass.async_add_executor_job`'s inline behaviour cannot be masking
anything here. `_spawn(self._async_save_thermal_learning())` is the only async
call in `_adopt_system_identification` and the stub closes the coroutine —
which affects only *persistence*, not the in-memory scale I measured. Real HA
would additionally persist the 5.70 % error to disk, so the stub is
conservative, not permissive.

### Verdict

Mechanism: **fully confirmed**, and confirmed twice over — the null control
(one-state plant, 9/9 adopted at 0.00 % error) and my own positive control
(1.5000) together show the effect is plant-order and not instrumentation.

Severity: `high` on this repo's scale is "a user-visible defect or a wrong
published value". What I measured is: unreachable on a default install; when
reached, a no-op in 9 of 9 cells on the default noise-free plant, costing one
night and ≤ 2.31 kWh of redistributed heating; and a 5.70 % wrong value written
in 2 of 9 cells only when 0.10 °C sensor noise is present, into a clamped,
confidence-blended parameter that ordinary passive learning corrects. That is
"a defect with a workaround or a bounded cost" — **`medium`**.

---

## D7-02 — vacuous guard, live dead attribute

**Finder severity `medium` (filed as hygiene). My vote: `weaken` to `low`.**
The assignment asked whether it deserves to be a `bug`. My number says the
opposite: it is not a leak.

### My own numbers and metrics

Harness: `tools/audit/round3/D7/verify-2/dead_state_cost.py`
(`load1` 6.86, `thread_factor` 1.002).

> **Metric A — `dead_attr_retained_bytes_growth` = bytes retained by
> `ThermalModel.last_dhw_refused` after 20 consecutive
> `simulate_trajectory_with_dhw` calls on ONE long-lived model instance, minus
> the bytes retained after 1 call.** A rebind gives 0; an accumulation gives > 0.

```
dead_attr_bytes_after_1_call        = 496 bytes
dead_attr_bytes_after_20_calls      = 496 bytes
dead_attr_retained_bytes_growth     = 0        <-- NOT a leak
model_instance_bytes_growth         = 0
dead_attr_ids_distinct_over_20      = 20       (20 arrays created, 1 alive: a rebind)
dead_attr_arrays_alive_at_end       = 1
control_accumulator_bytes_growth    = 7296     POSITIVE CONTROL -- a real
                                               accumulator over the SAME 20
                                               calls does grow, so the 0 is a
                                               measurement
dead_attr_bytes_worst_case_48h      = 880 bytes (96 steps; matches the finder's 880)
perturb_deadwrite_removed_bytes_after_20 = 0   (write deleted in a temp COPY: 496 -> 0)
```

**It is a rebind, bounded at 880 bytes for the longest horizon, with exactly
zero growth.** On a Raspberry-Pi-class target that is nothing. It does not
deserve `bug`.

> **Metric B (the guard's worth) — `guard_kills_new_sidechannel` = does
> `tests/rolling.py:577`'s predicate, `not hasattr(model,
> "last_buffer_trajectory")`, go False when a NEW simulation side-channel of
> exactly the class it claims to forbid appears on the instance?**

```
guard_kills_new_sidechannel   = 0    <-- the guard cannot see the defect it names
guard_kills_the_named_channel = 1    POSITIVE CONTROL (the predicate DOES fire
                                     on the one name it checks: my instrument works)
guard_coverage_fraction       = 0.00
guard_attrs_written_by_one_solve = 5 (_step_buffer_refused, _step_dhw_draw_kw,
                                     _step_dhw_floor_injected, _step_dhw_refused,
                                     last_dhw_refused)
```

The finder said the assertion is over an empty set. I went one step further and
**priced it**: added `last_room_trajectory` — precisely the class of side
channel the assertion's own text forbids — and the predicate still passes.
The guard would not catch the defect it is named after. With the positive
control at 1, that 0 is a measurement.

### Attack — is it even in the default gate?

Executed against `tests/run.sh`'s own expression:

```
default_gate_runs_guard     = 0   (SLOW unset)
slow_gate_runs_guard        = 1   (SLOW=1)  POSITIVE CONTROL
rolling_slow_wired_in_run_sh = 1  (tests/run.sh:402-404)
```

Confirmed: the vacuous assertion does not run in the default gate at all. The
guard is worth even less than the report says — but that cuts **both** ways: a
check that never runs also costs nothing when it is wrong.

### Attack — is `last_dhw_refused` an accidental stash?

No. Whole-tree grep (not the finder's Python-AST pass, which counts only
`self.X = …` stores) finds a **second** occurrence the report does not mention:

```
custom_components/heatpump_optimizer/thermal_model.py:1328
    #: Per-step refused DHW heat of the last `simulate_trajectory_with_dhw`.
    last_dhw_refused: np.ndarray | None = None
```

`dead_attr_is_declared_class_attr = 1`. It is an **annotated, commented class
attribute** — a deliberate publication with no consumer, the same shape as
`_step_dhw_draw_kw` and `_step_dhw_floor_injected`, which the finder itself
classifies as "test-only assertion channels, deliberate and documented". The
only difference is that those two have readers and this one has none. The
finder's `ast_writers_last_dhw_refused=1` is correct *as defined* but hides
this; a judge reading the report alone would picture an accidental stash.

### Verdict

Mechanism: **confirmed**, and independently re-priced. My whole-tree grep found
no reader the AST pass could have missed (0 readers in `.py`, `.mjs`, `.json`,
`.md` anywhere outside the declaration and the write).

Severity: `medium` on this scale is "a defect with a workaround or a bounded
cost"; `low` is "hygiene". This is 880 bytes with 0 growth, written by a
declared class attribute, plus a test assertion that never runs by default and
could not catch its own subject if it did. There is no user-visible cost at
all. That is **`low`**. The finder's own reasoning for `medium` — "a guard that
cannot fail is worse than no guard" — is sound and my `guard_kills_new_sidechannel
= 0` supports it, but it argues for *fixing* the guard, not for a `medium`
severity on a consequence-graded scale.

---

## D7-03 — the frequency map ingests what the freeze predicate rejects

**Finder severity `medium`. My vote: `verify` at `medium`, with a scope
correction the judge should carry.**

### My own numbers and metrics

Harness: `tools/audit/round3/D7/verify-2/freq_map_harm.py`
(`load1` 41.78 — every number below is a count or a frequency, so contention
cannot touch them; `thread_factor` 1.001).

> **Metric A — `commanded_hz_delta[arm]` = |Hz that the REAL
> `HeatPumpOptimizerCoordinator._command_frequency()` writes to the number
> entity after one interval folded under contamination arm `arm`| − |the Hz it
> writes after the identical interval folded clean|, at the same commanded
> power (2.0 kW) and the same entity range ([20, 120] Hz, one duty point in
> every decile so the write's quantisation is one decile and not a rig artefact).**

> **Metric B — `freq_map_folds_arm_consistent[arm]` = does `FrequencyMap.observe`
> actually fold when that arm's OWN sensors carry the values the arm physically
> implies, instead of being pinned at heating values?**

```
  arm             _learning_frozen       folds  buckets  written_Hz   delta
  clean           None                      60       10        65.0     +0.0
  external_heat   external_heat_source      60       10        65.0     +0.0
  open_window     ventilation               60       10        65.0     +0.0
  pump_offline    heat_pump_offline          0        0        None        -
  pump_fault      heat_pump_fault            0        0        None        -
  pump_cooling    heat_pump_cooling         60       10        55.0    -10.0

freq_map_folds_arm_consistent_total  = 3   (of 5, not 5)
arms_that_move_the_write             = 1   (of 5)
commanded_hz_delta_pump_cooling      = 10.0 hz     <-- one full decile
cooling_kw_ratio_to_move_the_write   = 1.05        <-- a 5 % kW distortion suffices
cooling_contamination_clean_folds_to_recover = 12  clean intervals (~6 h at the
                                                   30-minute cadence)
control_clean_write_hz               = 65.0 hz     POSITIVE CONTROL
control_gross_contamination_hz_delta = 30.0 hz     POSITIVE CONTROL (kW x 3)
control_empty_map_writes             = 0           (recommend() refuses no evidence)
freq_control_default_mode_is_control = 0           (DEFAULT_FREQ_CONTROL_MODE = "observe")
perturb_gated_contaminated_folds     = 0           (finder's perturbation, direction held)
perturb_gated_clean_folds            = 60
perturb_gated_clean_write_hz         = 65.0 hz     (the clean arm survives the gate)
```

### Attack 1 — the "5 of 5" is a rig artefact

The finder's harness pins `sensor.freq` at 55 Hz and `sensor.hp_power` at
2000 W on **every** arm, including the two that assert the pump is dead. Driven
with arm-consistent sensors instead:

- **`pump_offline`, `pump_fault`: 0 folds.** An offline pump's entity reads
  `unavailable`, so `_freq_entity_reading` returns `None` and `_observe_frequency`
  returns before the fold; a stopped compressor reads 0 Hz / 0 W and
  `FrequencyMap.observe` rejects it twice over (`hz < max(1.0, hz_min)` and
  `kw <= 0.05`). These two arms cannot fold in the physical state they name.
- **`external_heat`, `open_window`: 60 folds, `commanded_hz_delta = 0.0`.**
  These fold *true* data. `_learning_frozen` protects learners that relate the
  *room's thermal response* to *the pump's heat*; a wood stove or an open window
  corrupts those. The frequency map relates **reported Hz to measured
  electrical kW** — a property of the compressor alone, which neither a stove
  nor a window touches. Folding these intervals is arguably correct, not a gap.

So the finder's `freq_map_ingests_contaminated = 5` (which I reproduced
exactly) overstates the blast radius **5×**. The metric measures ingestion,
which is what it says on the tin, and the finder's own text already concedes
"the cooling arm is the one with teeth" — but a judge reading the number
without the prose would price this wrong.

### Attack 2 — but on the one arm that matters, the write DOES move

This is why I do not weaken. A reverse-cycle compressor at a fixed frequency
draws a different electrical power; at a deliberately conservative 1.15×,
the map's bucket that clears 2.0 kW shifts down one decile and
`_command_frequency` writes **55.0 Hz instead of 65.0 Hz**. The threshold scan
says only **1.05** is needed to move the write by
`FREQ_WRITE_EPSILON_HZ` — `recommend()` is a threshold crossing, so any
distortion near a bucket boundary flips it. My positive control (kW × 3 →
30.0 Hz) proves the instrument can see harm; the four 0.0 Hz readings are
therefore measurements.

Recovery is bounded: **12 clean intervals** (≈ 6 h of heating operation)
restore the clean answer, because `FREQ_EWMA_ALPHA = 0.1` decays the
contamination geometrically. That bound is what keeps this at `medium` and out
of `high`.

### Attack 3 — a sixth arm the finder did not test, where the gap bites harder

`_learning_frozen`'s docstring names two failure modes: "trains on a flatline"
**or** "on heat it did not supply". The finder's five arms are all the second
kind. The first kind — a stale/pinned power reading — is the `health.readings`
branch of the same predicate, and the finder's harness never opens it:

```
stale_power_arm_freeze_reason = stale:power_entity
stale_power_arm_folds         = 60        <-- folds every one
```

`_update_current_state` deliberately **pins** the last good value on a failed
read, so `_measured_power` is not `None` and `_observe_frequency`'s only power
guard passes. A pinned kW against a live, moving Hz teaches a wrong ratio in
every bucket it touches. This is the same gap as filed, on a mechanism the
report does not mention, and the coordinator's own comment at that branch
records a prior incident of exactly this shape ("A flat battery or a dropped
Zigbee sensor walked the house heat-loss scale from 1.0 to ~0.37 inside 48 h").
The finding is *stronger* than filed here, not weaker.

### Attack 4 — is the write path reachable at all?

`freq_control_default_mode_is_control = 0`: `DEFAULT_FREQ_CONTROL_MODE` is
`"observe"`, and `_command_frequency` returns before touching anything unless
the user opts into `control`. `control_empty_map_writes = 0` confirms the
finder's stated mitigation that a map with no evidence writes nothing. Both are
real bounds; both are already in the finder's severity paragraph. Note also
that `_freq_mode()` stands control down entirely once the watchdog trips — but
the watchdog compares *reported* against *commanded*, so a pump that obeys a
**wrong** command never diverges and the watchdog is no protection against this
particular defect.

### Verdict

Mechanism: **confirmed**, and carried one stage further than filed — the
un-gated fold does reach hardware, by one full decile, at a 5 % distortion.

Scope: **corrected** — harm reaches 1 of the 5 filed arms, not 5; two cannot
physically fold and two fold true data. And it reaches a **sixth**, un-filed
arm (`stale:power_entity`) where it folds 60 of 60.

Severity: `medium` stands. Opt-in write path, an empty-map refusal, one-decile
magnitude and a ~6 h EWMA washout are exactly "a defect with a workaround or a
bounded cost".

---

## Summary of votes

| id | vote | severity I would give | my executed number | metric |
|---|---|---|---|---|
| D7-01 | `weaken` | `medium` (from `high`) | `adopted_scale_error_pct_worst` = **0.00 %** noise-free (0/9 adopt), **5.70 %** at 0.10 °C noise (2/9 adopt); null control 0.00 % at 9/9; positive control 1.5000 | 100 × (`_house_heat_loss_scale` after the real `_adopt_system_identification()` − 1.0) on a plant equal to the configured params |
| D7-02 | `weaken` | `low` (from `medium`) | `dead_attr_retained_bytes_growth` = **0 bytes** over 20 solves (496 → 496; 880 at a 48 h horizon); control accumulator +7296; `guard_kills_new_sidechannel` = **0** with positive control 1 | bytes retained by `last_dhw_refused` after 20 solves minus after 1, on one long-lived model instance |
| D7-03 | `verify` | `medium` (as filed) | `arms_that_move_the_write` = **1 of 5**; `commanded_hz_delta_pump_cooling` = **10.0 Hz**; `cooling_kw_ratio_to_move_the_write` = **1.05**; `stale_power_arm_folds` = **60** | \|Hz written by the real `_command_frequency()` after a contaminated fold\| − \|after the identical clean fold\|, same demand and range |

## Files

- `tools/audit/round3/D7/verify-2/rerun_sysid_plant.txt`
- `tools/audit/round3/D7/verify-2/rerun_model_state_sentinel.txt`
- `tools/audit/round3/D7/verify-2/rerun_learner_freeze_matrix.txt`
- `tools/audit/round3/D7/verify-2/sysid_consequence.py` + `out_sysid_consequence.txt`
- `tools/audit/round3/D7/verify-2/dead_state_cost.py` + `out_dead_state_cost.txt`
- `tools/audit/round3/D7/verify-2/freq_map_harm.py` + `out_freq_map_harm.txt`
- `tools/audit/round3/D7/verify-2/out_grid_dropout.txt`

## Exposure

None beyond the tree as exported. No `gh`, no GitHub, no other verifier's
output, no audit register. I read `tools/audit/briefs/verifier.md`,
`tools/audit/README.md`, `tools/audit/briefs/COMMON.md` (severity scale only,
lines 58-62), `tools/audit/finding.schema.json` and the finder's `REPORT.md`,
plus the production and test files named above. `tools/audit/briefs/D7.md` line
5 and 29 surfaced in one grep for `last_buffer_trajectory`; I read those two
lines and did not open the brief.
