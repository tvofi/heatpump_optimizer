# Design: R11-SEAM-learners (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Base
9d65fe80b0cc76f4a65c1963fe244f8c296bdd26 (`origin/main`); code read there. The
predecessor `R11-SEAM-plant-model` merged as #3731 (merge 1850e2e0da, an
ancestor of the base); its handoff head is 3bd933a0d482829a3e60eab0cc3cc7b14198228a,
so the code read is the predecessor's merged state. Plan of record `plan/r11` at
1a2ff62c9aea96989f7f5c511e53b95d96667027: ADR-008 (approved design of the
predicate), ADR-003 part 2 (the switch), ADR-001 arm `fdjac`. No production code
on this ref.

## 1. Findings

D7-s2-01, D12-s3-03, D2-s3-08, D2-s3-09 (the freeze); D2-s3-10, D7-s2-02,
D5-s4-02 and the `fdjac` arm (sysid); D2-s3-11 (the gains fold's arithmetic).
Each harness is the finding's own, named in `dev/audit/rounds/round11/ISSUES.json`
under its class; all are on `origin/main`. Carries 0-1 are designed here (§3.4);
carries 2-3 are not (§7, a stop for that part).

## 2. Owning seam

Learners (`COMPONENTS.md`: "parameters fitted from observed intervals, and which
intervals count"; its two-owner row "may a learner ingest this interval" names
this group). Owner of the predicate: a new pure learners-seam module, the freeze
module (no `homeassistant` import; reads `const.py` only). It owns the closed set
of reasons, their order and which reason refuses which kind of sample. Callers
only: `coordinator.py` (gathers the cycle's facts, keeps every learner call),
`dhw_learning.py`, `draw_range.py`, `heat_energy.py`, `accuracy.py` (each hands
its own local evidence as a value). `sysid.py` owns its gate and Jacobian. No
concern needs two owners.

## 3. Shape

### 3.1 The predicate (ADR-008 part 2)

In the freeze module, all values, no handles (ADR-005):

- a frozen dataclass of the cycle's facts: external heat active, the pump
  signals' freeze reason, defrosting, the unusable configured readings
  (key to problem), ventilation tripped, the boost freeze, the tail freeze
  (`_tail_freeze`'s answer), away active, away recovery active; and four local
  evidence fields, default false, that only the owning learner sets with
  `dataclasses.replace`: charge open on a heated sample (dhw_learning), probe
  draw at the running floor (draw_range), tank rose in an unobserved span
  (heat_energy), pump does not follow the ask (accuracy's scale verdict);
- an enum of sample kinds: PLANT (today's `room_air=False`), ROOM_AIR (today's
  default), OCCUPANCY (room air carried by occupants: internal gains, DHW draw
  statistics, comfort quiet evidence), COMFORT (OCCUPANCY plus the recovery
  window: the curve learner), SPACE_HEAT, CEILING, TANK_DRAW, DELIVERED_RATIO;
- one function, facts + keys + sample kind -> reason string or None.

Reasons and order: today's eight in today's order and strings (external heat,
pump reason, defrosting, unusable key, ventilation for ROOM_AIR and wider, boost,
tail), then `away` (OCCUPANCY, COMFORT), `away_recovery` (COMFORT only, the curve
learner's private check at `coordinator.py:9222` moved, not widened),
`unplanned_charge` (SPACE_HEAT), `load_limited_probe` (CEILING),
`charge_start_dip` (TANK_DRAW), `ask_not_followed` (DELIVERED_RATIO).

`HeatPumpOptimizerCoordinator._learning_frozen` keeps its name and `*keys`; its
body becomes "build the facts, call the function". `room_air: bool` becomes the
sample-kind keyword (default ROOM_AIR); `room_air=False` callers pass PLANT.
The body's reasons leave the class, so `coord_footprint` falls or holds; the
comments explaining each reason move with it (fixer note 4).

```
cycle -> _learning_frozen(keys, sample) -> facts (coordinator state) -> freeze.reason
learner module -> replace(facts, <own evidence>) -> freeze.reason -> skip | ingest
```

### 3.2 Who asks what

| site | today | after |
|---|---|---|
| `_fold_internal_gains` (inside the house fold) | the house fold's ROOM_AIR answer | its own OCCUPANCY ask before the step (D7-s2-01) |
| `_record_quiet_comfort_period` | ROOM_AIR | OCCUPANCY (D7-s2-01) |
| `_track_curve_comfort` | private away/recovery test + ROOM_AIR | COMFORT; lines 9222-9223 deleted |
| DHW draw statistics (`DhwProfileLearner.async_fold_draw_stats`) | external heat only | the injected freeze callable with OCCUPANCY, and TANK_DRAW with charge evidence (D7-s2-01, D2-s3-08); standby dynamics keep PLANT so the tank keeps learning while away |
| house and lower-floor folds via `_replay_gate` | ROOM_AIR | SPACE_HEAT evidence from the span (D12-s3-03), then as today |
| `draw_range.fold` ceiling store | `frozen=` bool | CEILING with floor evidence before `observe_ceiling` (D2-s3-09) |
| `_settle_defrost` with `accuracy.delivered_ratio` | power freeze | DELIVERED_RATIO with the scale verdict (carries 0-1) |

Local evidence, each computed by its owner:
- D12-s3-03: heat_energy gains a pure function, the span's unobserved charge:
  true when the attribution is not observed (no mode dwell) and the configured DHW
  tank thermometer rose over the span by more than its standby band. The
  coordinator hands the tank reading at span open and close (it already holds
  both); `heat_energy.py` reads no tank today.
- D2-s3-08: dhw_learning sets charge evidence when the interval starts or ends on
  a heated sample of an open charge (the finder's perturbation); `ChargeSettle`
  keeps its take-back for the unheated rise.
- D2-s3-09: draw_range sets floor evidence when the draw is within
  `AGREE_TOLERANCE` of `DrawRange.observed()[0]`, the metered running floor.
- Carries 0-1: accuracy's `MeasuredCop.scale_response` verdict reads
  `does_not_follow`; while pending the fold is as today (fixer note 3).

### 3.3 sysid

- ADR-003 part 2: `SystemIdentification.arm` takes the switch as a keyword-only
  argument; `arm_from_config` passes `config.system_identification_enabled`;
  `sysid.py:2475`, the copy onto the collaborator, is deleted and `sysid.py:1458`
  reads the argument. `prototypes.py --only sysid` is the shape.
- `fdjac` (ADR-001): one private forward-difference helper (residual, x, value
  -> Jacobian, step `1e-6 * max(|x_i|, 1)`), read by `_lm_solve`
  (`sysid.py:811-817`) and `_slab_ua_profile_halfwidth` (`sysid.py:1040-1045`).
  `prototypes.py --only fdjac` is the shape.
- D7-s2-02: the intercept prior carries its own width. When arm seeds the prior
  from the learned night profile (`night_gains_prior_kw`) the width stays
  `SLAB_INTERCEPT_PRIOR_SD_KW`; when it is the configured constant the width is a
  second constant at 0.3 kW (the finder's perturbation), read by
  `_slab_ua_prior_halfwidth` and the ridge alike.
- D2-s3-10 ("the adoption interval covers quantised readings"):
  `slab_ua_adoption_halfwidth` gains a regressor-noise term. Reading variance is
  the larger of the fitted white variance and `d^2/12`, `d` the smallest non-zero
  step among the window's room readings (measured, not configured); its relative
  attenuation of UA (variance over the room-temperature regressor's variance) is
  added to the quadrature width linearly, being a bias; the profile width is
  inflated by `sqrt((1+r)/(1-r))`, `r` the residuals' lag-1 autocorrelation.
- D5-s4-02: the comments at `sysid.py:1984` and `sysid.py:2073` are rewritten on
  `s_noise`, `prior_sd` and `usable[i - 1].room_temp`.

### 3.4 D2-s3-11, the gains fold (point fix, coordinator)

`coordinator.py:9431` pulls the target toward `g0` (`INTERNAL_GAINS_RIDGE`), so the
fixed point is `alpha/(alpha+ridge)` of the gain. The ridge moves onto the step:
`g += alpha_n * y` with `alpha_n` shrunk by the hour's sample count, so the
expected step is zero only at a zero residual; with no ridge on the target the
joint fixed point of the profile and the scale is the truth (both folds zero their
mean residual; day-to-day spread in the driving difference separates them).

**Invariants.** Every reason today's predicate returns is returned for the same
inputs, same string, same rank (`tests/features.py` freeze checks unedited).
Store keys and `store.DOMAINS` unchanged. The new reasons are additive and scoped:
a PLANT or ROOM_AIR caller gets none of them.

## 4. Alternatives (lost on the code)

- A freeze test per learner kept equal by a test: the state D7-s2-01 measures
  (three learners, three answers).
- The predicate as a coordinator method with an `away` branch only (D7-s2-01's
  proposal): keeps the two-owner row of `COMPONENTS.md`, adds statements to the
  class that ADR-007 must then pay, and leaves the four local reasons in four
  modules with no shared order.
- The local evidence computed by the coordinator: it would read draw-range,
  span and charge internals across the seam (`private_cross_module`).
- D2-s3-08 by holding every charge-affected fall provisional until the charge
  closes: `ChargeSettle` gains state across heated intervals and a second settle
  path; the refusal is one predicate answer on evidence the learner already has.
- D2-s3-10 by a residual-whiteness refusal alone: refuses the quantised arm
  wholesale (liveness) instead of pricing it.

## 5. Sibling sites

`grep -n '_learning_frozen(\|_away_state.active\|recovery_active' custom_components/heatpump_optimizer/coordinator.py`
and `grep -n 'frozen\|_external_heat_active' custom_components/heatpump_optimizer/dhw_learning.py custom_components/heatpump_optimizer/draw_range.py`.
Covered: every `_learning_frozen` caller (by the keyword map of §3.1), the rows
of §3.2. `coordinator.py:6307` (`rooms.gate(..., away=...)`) is a planner gate on
room lift, not an ingest: out of scope. `comfort_learning.py` quiet evidence is
reached through `_record_quiet_comfort_period`. The learners `COMPONENTS.md`
lists and §3.2 does not (`slab_seed`, `wear`, `learner_progress`, `external_heat`)
fold no interval sample or already ask `_learning_frozen`; the fixer re-runs the
command at the merge base and covers any new caller.

## 6. Evidence plan

Failing tests first, `tests/features.py`: the freeze module's table (each reason
for each sample kind; today's eight unchanged); away freezes gains, draw stats and
comfort quiet and not the tank standby; the curve learner's recovery freeze kept;
a mode-less counter span with a tank rise refused, the same span without the rise
kept; a ceiling sample at the floor refused, at 4.0 kW kept; a 60-minute charge
books no dip, a real draw on an unheated interval inside the charge still books;
`arm` with the switch off refuses without writing the collaborator's config; the
R9-P5 sweep gains the `learned=False` arm; the gains fold's expected step is zero
at the genuine gain.

| finding | harness, both ends | null control |
|---|---|---|
| D7-s2-01 | `dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py` contaminated_ingest 3 -> 0 | its home arm ingests; `m3_away_drift.py` gains 1.0000 g0 |
| D12-s3-03 | `dev/audit/rounds/round11/D12/s3/counter_spans.py --sees-dhw --no-mode` inflated 1 -> 0 | `--sees-dhw` and `--plan-only` keep their space spans |
| D2-s3-08 | `dev/audit/rounds/round11/D2/s3/m5_tankfall.py` long_a/long_b -> under 0.05 kWh | the short shape stays at its 0.039 |
| D2-s3-09 | `dev/audit/rounds/round11/D2/s3/m5_drawrange.py` narrowing 4.1 -> 0 | uncensored top 4.0 still learns 4.0 |
| D2-s3-10 | `dev/audit/rounds/round11/D2/s3/m5_sysid.py` miss share per noisy arm to at most 0.10 | white_0.005 and noise-free still admit |
| D7-s2-02 | `dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py` biased_admitted 3 -> 0 | told cells still admitted |
| D2-s3-11 | `dev/audit/rounds/round11/D2/s3/m5_crosscov.py` gain_recovery up from its base, scale bias toward 0 | the no-gain arm unchanged |
| D5-s4-02 | `dev/audit/rounds/round11/D5/s4/comments.py --file custom_components/heatpump_optimizer/sysid.py` unresolved 2 -> 0 | the other units unchanged |
| carries 0-1 | `dev/audit/harnesses/cop_duty_floor.py` `defrost_inferred_*` toward 1.000 | the draw-equals-ask control stays 1.000; `selfset_2.2_swing*` unchanged |
| fdjac, ADR-003 | `prototypes.py --only fdjac`, `--only sysid`; `score.py --diff` | `tests/features.py` arming checks unchanged |

Goldens: none expected to move (the gains fold runs only with internal-gains
learning on; the freezes add refusals no golden trace contains). Any that moves is
claimed with its direction in `tests/golden/claimed_drift.txt`, else both claim
files byte-identical. Mutation targets: each reason's scope row in the freeze
module; the reason order; the evidence predicates (tank-rise band, floor
tolerance, heated-bound test, verdict string); `sysid.py:1458`'s read; the
regressor-noise term and the autocorrelation factor; the prior-width branch; the
gains step's shrink.

## 7. Hot files, serial position, carries

Hot files as the roster: `sysid.py`, `accuracy.py`, `dhw_learning.py`,
`heat_energy.py`, `draw_range.py`, `coordinator.py`, `dhw_draws.py`,
`tests/features.py`; plus the new module, a measured closure in
`tests/closure.py` in the same pull request (`tests/entities.py` otherwise
refuses it). After `R11-SEAM-plant-model` (merged in the base); before
`R11-ARCH-fabric-learner`, whose fixer waits on this group. No p1/p2 split: no
pinned grader changes.

Carries received: 0-1 (designed, §3.2). Carries 2-3 (the heat-ask dither (c1)
and the closed-loop planner harness): **not designed, a stop for that part.**
The behaviour no finding names, and design/R11-OUTSIDE-SELF-SETTING-PUMP's note
lists owner decisions it needs and a closed-loop harness that does not exist, so
no failing test can be stated. Carry: R11-SEAM-learners (items c25b53cc, 4a5e147b)
`decision: orchestrator` whether a design group takes them.

### Notes for the fixer

- `coordinator.py:9431` is an exact-text anchor of the fabric group's spike;
  its revalidation stops on it after this merge. Carry: R11-ARCH-fabric-learner (item 9b3d1e01)
- Keep today's reason strings: `learner_progress.py` and the freeze notes
  display them. Carry: R11-SEAM-learners (item 9b3d1e02)
- Carries 0-1: read the verdict names at `accuracy.py:1278` before keying on
  `does_not_follow`; if the pending arm still learns below 1.000, report it, do
  not widen the freeze to pending (ADR-008 T8). Carry: R11-SEAM-learners (item 9b3d1e03)
- Move each reason's explanatory comment with it out of `_learning_frozen`.
  Carry: R11-SEAM-learners (item 9b3d1e04)
- `SysIdConfig.enabled` is removed only if no other reader or stored payload
  reads it; otherwise it is set at construction and never after. Carry: R11-SEAM-learners (item 9b3d1e05)
