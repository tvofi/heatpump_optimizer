# Round 9, D7, seat s2 -- steps M2, M3, M4

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, export `/home/claude/audit-r9-baseline`,
box B7 (cloud container, linux, `/home/claude/venv314/bin/python`). Every number below is a
count, a ratio or an exact difference (no wall/CPU/RSS number is claimed). Every harness
runs from the export root with `PYTHONPATH=tests/hastub`; root rule: `sys.path` from the
working directory, so each measures the tree it is run from.

Exposure: none (no `docs/`, no GitHub, no earlier-round files read).

## Method

- **M2 (the sysid plant).** `sysid_plant.py` builds the three stress presets (`light_new`,
  `heavy_old`, `typical_slab`; `tests/stress.py:BUILDINGS` through `presets.derive`,
  single zone), and drives the production `SystemIdentification` state machine end to end
  (`arm(plant=declared)` -> `step` every 30 min -> `_finish` -> `identify_slab`), then
  `adoption_decision`. The truth plant is the production `ThermalModel` with EXACTLY the
  declared parameters; only its integration is varied (1, 2, 6, 30 sub-steps per 30-min
  sample). On the same samples it also runs the one-state regression (`identify`,
  harness-only) and a free two-state (two-exponential) fit.
- **M3 (learner freeze vs COP flow).** `learner_table.py` drives eight learners (six through
  their own ingest counters, two through the gate they consult) on one interval under each
  of nine contaminations. `learner_gates.py` isolates the one divergence found.
- **M4 (`last_buffer_trajectory`).** The stash no longer exists at this baseline;
  `objective_order.py` captures the real space-stage objective from `_scoped_minimize` and
  tests order dependence of the objective, the terminal-cost closure and the remaining
  per-step scratch (`ThermalModel._step_buffer_refused`), with a positive control.

## Findings

### D7-s2-01 (M2) -- the production sysid fit integrates the candidate plant with one Euler step per 30-min sample; on a noise-free, parameter-exact continuous house it is biased 17-25 % low or refused, and adopts on 0 of 3 presets

`sysid:identify_slab` rolls the candidate through `_simulate_slab_path` -> `_valve_drive`
-> `ThermalModel.simulate_step(dt_hours=<sample interval>)`: one explicit-Euler step of
0.5 h per sample (the coordinator cadence). A physical house is continuous; the fit's model
class is the Euler map at 0.5 h -- not even the optimizer's own 0.25 h step.

`PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/s2/sysid_plant.py`

| truth sub-steps / 30 min | light_new | heavy_old | typical_slab |
|---|---|---|---|
| 1 (the fit's own Euler step) | aborted (excursion) | +0.00000, adopted w=0.682 | +0.00000, adopted w=0.428 |
| 2 (the optimizer's 15-min step) | -0.08878, refused | -0.10911, refused | -0.23301, refused |
| 6 | -0.14573, refused | -0.20714, refused | refused (implausible params) |
| 30 (continuous) | -0.16823, refused | -0.25461, refused | refused (implausible params) |

`RESULT continuous_presets_bias_gt5pct=3`, `RESULT continuous_presets_adopted=0`,
`RESULT continuous_presets_adopted_biased=0` (the gate refuses every biased fit: interval
"unbounded" or plausibility), thread_factor 1.000, load1 1.49.

Comparators on the 30-sub-step truth: the one-state `identify` refuses all three
("fitted parameters outside plausible bounds" / "fit gave implausible signs"); the free
two-state fit with a fine rollout recovers UA to +0.00000 on all three.

**Perturbation** (`--substep-rollout`, in memory: `_valve_drive` split into 6 equal
sub-steps, a one-line edit): `continuous_presets_bias_gt5pct` 3 -> 0,
`continuous_presets_adopted` 0 -> 2 (heavy_old -0.0085 w=0.572, typical_slab -0.0187
w=0.165; light_new -0.0089, refused at +-16 %). The same edit moves the step sizer
(`_predict_step_excursion_plant` also goes through `_valve_drive`), which is why light_new's
coarser-truth arms then abort on excursion.

Consequence: the experiment the button arms can never be adopted on the presets the
integration derives, and the result published under `system_identification`
(`heat_loss_kw_per_c`) carries the 17-25 % low value beside a reason that blames the window
("heat-loss interval (unbounded)"), not the model. Severity medium: the gate prevents a
wrong adoption; the feature is inert and its diagnostic is wrong.

Property: every parameter fit that rolls a candidate `ThermalModel` over recorded samples
must integrate the candidate at a resolution whose discretization error is small against the
adoption bar, independent of the coordinator's sample cadence. Seam rule:
`grep -n "_valve_drive(\|simulate_step(" custom_components/heatpump_optimizer/sysid.py`.

### D7-s2-02 (M3) -- the defrost derate's fallback estimator folds draw-distorted intervals that `_cop_fold_blocked` refuses to the COP learner

`coordinator:_record_accuracy` gates `_settle_defrost` on `_learning_frozen(power) in (None,
"defrosting")` only. On an install with a power meter and no legible defrost flag, in the
frost band, `_settle_defrost` -> `DefrostDerate.observe(delivered_ratio)` folds
`predicted_power / measured_power`, the same meter ratio `_learn_measured_cop` reads -- but
the COP learner (and its health watch and capacity envelope) refuse an interval where
`_cop_fold_blocked` is True: the immersion latch, the pump's own backup heater or DHW
booster, or night-mode capacity capping. The derate folds all three.

`PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/s2/learner_gates.py`

| arm | `_cop_fold_blocked` | derate folds | COP learner folds (7 C) |
|---|---|---|---|
| clean | False | 1 | 1 |
| immersion latch (+3 kW on the meter) | True | 1 | 0 |
| pump backup heater (+3 kW) | True | 1 | 0 |
| capacity limited (0.6x draw) | True | 1 | 0 |

`RESULT derate_ingests_distorted=3` (of 3). After 24 intervals (12 h) at 2 C / 85 % RH the
published `factor()` is 0.8738 (bucket raw 0.6814) under the immersion latch or the backup
heater against 1.0000 clean; a bucket that had learned a real 0.80 is walked to raw 0.9416
(published 0.9769, vs 0.9208 untouched) by capped intervals. thread_factor 1.000, load1 1.02.

**Perturbation** (`--gate-derate`, in memory: `_settle_defrost` returns when
`_cop_fold_blocked(self)`): `derate_ingests_distorted` 3 -> 0; every contaminated arm's factor
stays 1.0000 (capped arm stays at 0.9208), the clean control still folds.

Consequence: the derate multiplies the frost-band COP every plan is priced with, so a backup
heater running through a cold snap -- the intervals it exists for -- teaches a phantom
defrost loss (-12.6 % COP after 12 h), and night-mode capping erases a real one. Severity
medium (bounded by `DERATE_MIN` 0.55 and the band; persisted). Class P2.

Property: every learner that folds the meter's commanded/measured ratio must refuse the
intervals `_cop_fold_blocked` marks. Seam rule:
`grep -n "_measured_power\|actual_power_kw" custom_components/heatpump_optimizer/coordinator.py`
(each reader of the meter, checked for the predicate).

## Non-findings

- **M2, adoption of a biased fit.** `continuous_presets_adopted_biased=0`: no fit with
  |bias| > 5 % is admitted by `adoption_decision` on any preset or truth resolution; the
  #1410 interval plus the D7-01 prior term refuse all of them (`sysid_plant.py`).
- **M2, one-state regression.** `identify` refuses all three presets on the continuous
  truth; it cannot adopt a biased fit because it cannot complete (`sysid_plant.py`,
  `one_state_bias_*` = nan).
- **M2, two-exponential fit.** A free four-parameter two-state fit with a 1-min rollout
  recovers UA to 1e-5 on every preset (`twoexp_bias_*`), so the bias in D7-s2-01 is the
  rollout's resolution, not the information in the 5 h window.
- **M3, the freeze table** (`learner_table.py`; 1 = ingests):

  | learner | clean | ext. heat | defrost | offline | fault | cooling | ventilation | away | immersion |
  |---|---|---|---|---|---|---|---|---|---|
  | house heat loss | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
  | internal gains #53 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
  | measured COP | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
  | defrost derate fallback | 1 | 0 | 1 (by design, #944) | 0 | 0 | 0 | 0 | 1 | **1** |
  | curve comfort #2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
  | sysid experiment | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
  | freq map #61 (gate) | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 0 |
  | DHW dynamics (gate) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |

  External heat, defrost, offline, fault, cooling and ventilation freeze every heat-balance
  learner. Away freezes only the curve tracker (`away_ingesting_learners=3` of 3
  heat-balance learners); no away-specific contamination of the heat balance was
  established (away changes the comfort target, not the modelled gains), so it is recorded,
  not claimed. The freq map deliberately gates only on draw distortion and cooling; no
  mechanism by which a defrost/offline/fault interval corrupts a kW-per-Hz point was
  established. Immersion reaching sysid/curve/DHW is correct: those do not read the meter.
- **M4, call order.** The `last_buffer_trajectory` stash is gone: `_terminal_cost`'s closure
  takes `buffer_temps` as an argument. `objective_order_maxdiff=0.000e+00`,
  `terminal_order_maxdiff=0.000e+00`, `refused_order_maxdiff=0.000e+00 kW` over 26
  schedules evaluated fresh, reversed and with a second objective call interleaved
  (two-zone, smart_read valve, 200 L store, tank at 68 C so the cap refuses 331 kW-steps).
  Positive control `--sticky-scratch` (a missing reset of `_step_buffer_refused`):
  `refused_order_maxdiff` 0 -> 2.873 kW, objective unchanged (the objective does not read the
  scratch; the buffer-cap repair does). The solve builds its own `ThermalModel` over copied
  parameters (`_solve_snapshot`), so no cross-thread writer shares the scratch.

## Harnesses

- `tools/audit/round9/D7/s2/sysid_plant.py` (M2; `--substep-rollout`)
- `tools/audit/round9/D7/s2/learner_gates.py` (M3; `--gate-derate`)
- `tools/audit/round9/D7/s2/learner_table.py` (M3 table; `--away-freezes`)
- `tools/audit/round9/D7/s2/objective_order.py` (M4; `--sticky-scratch`)

## Unfinished

- M2: noise-bearing arms (sensor noise, gains different from the prior) were not run on top
  of the discretization result; two-zone presets were not driven.
- M3: the lower-floor loss learner (needs a two-zone install with a lower-floor sensor), the
  flow-lift bias (#1067), buffer cooling and the comfort learner were not driven; freq map
  and DHW dynamics were measured at their gate, not their counter.

## Leads (outside my cells)

- D5-s2: `optimizer.py` `OptimizationResult.buffer_temp_trajectory` comment says "the model
  stashes the series on itself for the terminal-cost term" -- no such stash exists.
- D7-s3: `ThermalModel._step_dhw_refused`, `_step_dhw_floor_injected`, `_step_dhw_draw_kw`,
  `_step_wood_refused` are written by production and read only by `tests/features.py`.
