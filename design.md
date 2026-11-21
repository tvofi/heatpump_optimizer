# Design: R11-SEAM-learners (round 11, size L), revision 2

Architect note, extended (`dev/governance/roles/designer.md`). Base
9d65fe80b0cc76f4a65c1963fe244f8c296bdd26; revision 2 re-read at `origin/main`
78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f, whose production diff from the base
touches `optimizer.py` and `plan_slots.py` only, so every `coordinator.py`,
`heat_energy.py`, `dhw_learning.py`, `draw_range.py` and `sysid.py` anchor below
holds at both. The
predecessor `R11-SEAM-plant-model` merged as #3731 (an ancestor of the base);
its handoff head 3bd933a0d482829a3e60eab0cc3cc7b14198228a, so the code read is
its merged state. Plan of record `plan/r11` at 1a2ff62c9aea96989f7f5c511e53b95d96667027:
ADR-008 (the predicate), ADR-003 part 2 (the switch), ADR-001 arm `fdjac`.
Revision 2 revises 429223e1974b9a142fab3cc28d04fb230065ab15 against
design-verdict 6b72a4ab211b2ab72ea0c51236ca8517dbb42f97 (revision 1 answered
702ffcc59f1c0a369dbe8d3a552a9d4938152a40); §8 maps each revise point to its
answer. Sections the verdict approved are unchanged except where a fixer note
changes what the fixer builds. No production code on this ref.

## 1. Findings

D7-s2-01, D12-s3-03, D2-s3-08, D2-s3-09 (the freeze); D2-s3-10, D7-s2-02,
D5-s4-02 and the `fdjac` arm (sysid); D2-s3-11 (the gains fold). Harnesses: each
finding's own, named under its class in `dev/audit/rounds/round11/ISSUES.json`.
Sweep instances beyond the findings, now covered: N-confounded-learner (#3760)
`_fold_measured_cop` and `_async_learn_lower_floor_loss` (§3.2), and, from
revision 2's enumeration (§5), `_fold_flow_lift` and the sysid experiment's
freeze ask (§3.2); P5 (#3767)
`SystemIdentification.step` `cop` and `outdoor_temp` (§3.3). Carries 0-1
designed (§3.2); carry 3 designed against its harness (§3.5); carry 2 is its
own bounded part, `pending owner decision` (§9): nothing else waits on it.

## 2. Owning seam

Learners: the components table on `plan/r11` gives "may a learner ingest this
interval" to this group. Owner of the predicate: a new pure learners-seam module,
the freeze module (no `homeassistant` import; reads `const.py` only): the closed
set of reasons, their order, which sample kind each refuses, and the two value
types below. Each piece of local evidence is computed by the module that holds
its inputs, as a pure function; the coordinator only carries the value to the
ask. `sysid.py` owns its gate and Jacobian. No concern needs two owners.

## 3. Shape

### 3.1 The predicate and what crosses each boundary

Freeze module, values only (ADR-005):

- the cycle's facts, a frozen dataclass: external heat active, the pump
  signals' freeze reason, defrosting, the unusable configured readings (key to
  problem), ventilation tripped, the boost freeze, the tail freeze
  (`_tail_freeze`'s answer), away active, away recovery active;
- the evidence, a second frozen dataclass of four booleans, all default false:
  unplanned charge, at running floor, charge open, ask ignored;
- an enum of sample kinds: plant (today's `room_air=False`), room-air (today's
  default), occupancy, comfort, space-heat, ceiling, tank-draw, delivered-ratio;
- one function: facts, keys, kind, evidence -> reason string or None.

Reasons, enumerated from the code (fixer note 1): `_learning_frozen`
(`coordinator.py:6850-6929`) answers external heat, the signals' reason,
defrosting, the unusable key, ventilation (room-air and wider), boost; then
`_tail_freeze` (`coordinator.py:3460-3475`) answers the early cut, the supply
hold and the unmetered power: nine, strings and order kept. Then the additive
ones: away (occupancy, comfort), away recovery (comfort only: the check at
`coordinator.py:9222`, `recovery_active`, moved, not widened), unplanned charge
(space-heat), at running floor (ceiling), charge open (tank-draw), ask ignored
(delivered-ratio). A plant or room-air ask gets none of the additive ones. A
space-heat ask answers room-air's reasons first, then the unplanned charge, so a
room-air ask that becomes space-heat keeps every answer it gives today.

**No learner holds a facts value.** The coordinator is the only builder of
facts, per call. What crosses each boundary:

| boundary | today | after |
|---|---|---|
| `HeatPumpOptimizerCoordinator._learning_frozen` | `*keys, room_air: bool` | `*keys`, keyword `sample` (default room-air), keyword `evidence` (default none); body: build facts, call the function |
| `DhwProfileLearner` (`dhw_learning.py:166`) | `frozen: Callable[[str], str \| None]`, bound at `coordinator.py:3765` to `_learning_frozen(room_air=False)` | the same callable typed as key plus the two keywords, bound to `_learning_frozen` unpartialled; the learner passes plant (standby dynamics, `dhw_learning.py:441`), occupancy (draw statistics) or tank-draw with its own charge-open evidence (draw booking) |
| `draw_range.fold` (`draw_range.py:665`) | `frozen: bool` | `frozen: bool` unchanged (window and idle), plus keyword `ceiling_frozen: bool` that gates `observe_ceiling` alone; a ceiling-frozen experiment sample is dropped, never handed to `draw.observe` (`fold`'s docstring: no experiment draw reaches the window) |
| `_settle_defrost` (`coordinator.py:9931`) | no freeze of its own; the inference branch reads `delivered_ratio` | the inference branch asks delivered-ratio with ask-ignored evidence before `self._defrost.observe`; the caller's #944 exemption (`power_frozen in (None, "defrosting")`, `coordinator.py:10080`) stays, so a defrosting interval still reaches it; the duty branch unchanged |

**The one `power_frozen` read splits** (`coordinator.py:9993`). It stays one read
of the plant answer for `CONF_POWER_ENTITY`, passed as `frozen=` to the window
and idle paths exactly as today. Where `experiment_s` is set, the coordinator asks
again with ceiling kind and the at-running-floor evidence, and passes that as
`ceiling_frozen=`. The delivered-ratio ask is a third, separate call inside
`_settle_defrost`'s inference branch; the defrost settlement's existing gate
keeps reading `power_frozen`.

```
coordinator -> _learning_frozen(keys, sample, evidence) -> facts -> freeze.reason
dhw_learning -> frozen(key, sample=TANK_DRAW, evidence=charge open) ----^
coordinator -> draw_range.at_running_floor(...) -> evidence -> _learning_frozen(CEILING) -> fold(ceiling_frozen=)
coordinator -> heat_energy meter: unplanned charge (cycle | span) -> evidence -> _learning_frozen(SPACE_HEAT)
coordinator -> MeasuredCop.scale_response() == ASK_IGNORED -> evidence -> _learning_frozen(DELIVERED_RATIO)
```

### 3.2 Who asks what (every site the enumeration of §5 lists)

The unplanned-charge evidence, owned by `heat_energy.py`: an interval or span
whose attribution is **not observed**, whose plan split put **no hot water** in
it (`a.dhw <= 0.0 < a.space`, the whole-unit rule `space_heat_kw` applies at
`heat_energy.py:239`), and over which the configured tank thermometer **rose** by
more than a design band (a named constant, the fixer's; the harness tank rises
4 K a charging cycle and falls 0.5 K otherwise). The meter takes the tank reading
in its per-cycle observe call and keeps the cycle's and the open span's first
reading, runtime only, so no store key moves; a cycle with no previous reading,
or an install with no tank thermometer, reads false: today's behaviour. The
meter is observed in `_update_current_state` (`coordinator.py:6775`, called at
`:6043`) before any fold of the cycle and before `_record_accuracy` (`:6097`),
so every reader below sees the evidence of the interval it folds.

| site | today | after |
|---|---|---|
| `_fold_internal_gains` (house fold) | the house fold's room-air answer | occupancy ask at the top, with the class-side gates (`coordinator.py:9411-9423`), never between `y` and the step, which R11-ARCH-fabric-learner extracts (D7-s2-01) |
| `_record_quiet_comfort_period` | room-air | occupancy (D7-s2-01) |
| `_track_curve_comfort` | private away/recovery test + room-air | comfort; `coordinator.py:9222-9223` deleted |
| `DhwProfileLearner` draw statistics, draw booking | external heat only (`dhw_learning.py:494`) | occupancy; tank-draw with charge open (D7-s2-01, D2-s3-08) |
| `_interval_measured_heat_kw` (`coordinator.py:1000`): house and lower-floor folds, slab estimate | room-air; `space_heat_kw` on the plan split | space-heat ask with the cycle's unplanned-charge evidence (#3760 sweep, lower-floor instance) |
| span close, house and lower-floor (`span_heat`, `heat_energy.py:325-326`) | room-air | space-heat ask with the span's evidence (D12-s3-03) |
| span close, COP (`close.cop`, `coordinator.py:1192-1194`, the span's `reference` attribution) | the per-cycle `clean["cop"]` AND only | the same span evidence refuses the span's COP fold; the per-cycle AND already drops a span with one refused cycle, and this covers a rise spread under the band per cycle |
| `_interval_space_power` (`coordinator.py:4994`) | `ran_hot_water` only | space-heat ask with the cycle's evidence |
| `_fold_flow_lift` (`coordinator.py:936`; persisted `flow_bias`, `store.py:394`) | `_learning_frozen(CONF_OUTDOOR_TEMP_ENTITY)` (`:975`), then the attribution's share at `:979-980`, plan split when unobserved | the `:975` ask becomes space-heat with the cycle's evidence: an unplanned charge, whose supply is the tank's charge temperature, never folds into `bias_k` (#3760 instance, revision 2) |
| `_fold_measured_cop` (`coordinator.py:5290`) | `_learning_frozen(...)` then, unobserved mode, `space_ref` | the same ask as space-heat with the cycle's evidence: an unplanned charge refuses as frozen instead of folding as a space sample (#3760 instance) |
| draw-range gate (`coordinator.py:9998`) | `not ran_hot_water(...)` | the same, and `power_frozen`'s companion ask (space-heat, the pending split's evidence) joins `frozen=`: an unplanned charge is not a running space sample |
| `draw_range.fold` ceiling store | `frozen=` | `ceiling_frozen=` with at-running-floor evidence (D2-s3-09) |
| `_settle_defrost` inference | `power_frozen` at the caller | delivered-ratio with ask-ignored (carries 0-1) |
| sysid experiment (`_run_system_identification`, `coordinator.py:11042`) | `_learning_frozen(indoor, outdoor)` into `sysid.hold_reason`; the step books the plan's power as delivered (`sysid.py:1782`, `:1792`) | the same ask as space-heat with the cycle's evidence: an unplanned charge stands the experiment down through the existing `stand_down` path, so no row of heat that went to the tank enters `identify()` (#3760 instance, revision 2) |
| `_accumulate_energy` totals (`coordinator.py:10316`; a statistic, not a learner) | plan split when unobserved | with the cycle's evidence the interval books as hot water, the whole-unit rule; no freeze reason, since nothing is refused (fixer note 9b3d1e14 answered by reading the evidence) |

Safe and unchanged, with the reason: `bridges_hot_water` (`heat_energy.py:540`)
answers true only on an observed charge; an unobserved one answers false, which
keeps the cycle gating the span as before: the error is conservative. `cop_duty`
is reached only past `mode_observed` (`coordinator.py:5278-5279`), so it never
sees an unobserved attribution.

Other evidence, each by its owner:
- D2-s3-08, `dhw_learning.py`: charge open when the interval starts or ends on a
  heated sample of an open charge; `ChargeSettle` keeps its take-back.
- D2-s3-09, `draw_range.py`: at running floor when the experiment's draw is
  within `AGREE_TOLERANCE` of the **floor in force** that
  design/R11-OUTSIDE-HONEST-METERED-FLOOR (080231bbfd) defines: its learned
  floor where set, else the configured `min_electrical_power`. That design owns
  the running floor; this group reads it and defines none. #3714 merged it:
  the predicate reads `draw_range.floor_in_force_kw` (`draw_range.py:589`), and
  revision 1's `power_floor_kw` fallback is void. It does not read
  `DrawRange.observed()`, so its None (too few samples) does not arise.
- Carries 0-1, `accuracy.py`: ask ignored when `MeasuredCop.scale_response`
  (`accuracy.py:1278`) reads `ASK_IGNORED`; pending folds as today.

### 3.3 sysid

- ADR-003 part 2: `SystemIdentification.arm` takes the switch keyword-only;
  `arm_from_config` passes `config.system_identification_enabled`; the copy
  onto the collaborator (`sysid.py:2475`) is deleted, `sysid.py:1458` reads the
  argument. Shape: the plan's prototype arm sysid.
- `fdjac` (ADR-001): one private forward-difference helper (residual, x, value
  -> Jacobian, step `1e-6 * max(|x_i|, 1)`), read by `_lm_solve`
  (`sysid.py:811-817`) and `_slab_ua_profile_halfwidth` (`sysid.py:1040-1045`).
- D7-s2-02: the ridge has one spelling. `_slab_ua_profile_halfwidth`'s inner
  residual (`sysid.py:1019-1022`) calls `_ridged` (`sysid.py:995-999`), and
  `_ridged` takes the width as an argument. The width: `SLAB_INTERCEPT_PRIOR_SD_KW`
  when the plant carries a learned internal-gains profile, else a second
  constant at 0.3 kW (the finder's perturbation). `night_gains_prior_kw`
  (`sysid.py:1291`) stays one float; the signal is the plant's own profile field
  (the one `internal_gains_at` branches on), read beside it in arm, carried into
  the gate's three readers (profile, prior, told).
- D2-s3-10: the regressor-noise term is computed where the series is,
  `_slab_outcome` (`sysid.py:2389`, holds `rooms` and the error), and handed to
  `slab_ua_adoption_halfwidth` as a fourth argument, which stays a pure combiner.
  Reading variance: the larger of the fitted white variance and `d^2/12`, `d`
  the window's smallest non-zero room step; its attenuation of UA is added
  linearly (a bias). The profile width is multiplied by `sqrt((1+r)/(1-r))`
  with `r` clamped to `[0, R_MAX]`, `R_MAX` a named constant of 0.9 (factor at
  most `sqrt(19)`): a negative `r` never narrows and `r -> 1` never diverges.
- **P5 told quantities (#3767, beyond the findings): priced.** The fit is told
  the COP (`step`'s `cop`, `sysid.py:1778-1795`, scaling every power row) and the
  outdoor reading (`sysid.py:1776`). `_told_path_error` (`sysid.py:966`) gains a
  heat scale `c` (multiplying the power series) and an outdoor offset `o` (added
  to the outdoor series), defaults 1 and 0; `_slab_ua_told_halfwidth`
  (`sysid.py:1132`) moves each by one width either way and re-solves from the
  converged point, exactly as it moves the slab pair, the four members' largest
  shifts in quadrature. Widths: a COP log width and an outdoor offset in K, two
  design constants like `SLAB_PAIR_PRIOR_LOG_SD` (`sysid.py:589`), whose value
  is priced by the same table (nights kept of those adopted without the term, on
  the derived presets, noise-free, plant equal to the declaration).
  `_declared_night_halfwidth` (`sysid.py:1218-1222`) reads the same told
  function, so a night the widths alone put past the bar is refused before the
  step, not after. The COP moves UA about one for one, so a COP width near 0.05
  alone spends the bar: the widths are a liveness trade. decision: owner (the
  two widths, from the fixer's keep table), as for the slab pair.
- D5-s4-02: the comments at `sysid.py:1984` and `sysid.py:2073` rewritten on the
  names the code uses.

### 3.4 D2-s3-11, the gains fold (point fix, coordinator)

`coordinator.py:9431` pulls each hour toward `g0` by `INTERNAL_GAINS_RIDGE`, so the
fixed point is `alpha/(alpha+ridge)` of the gain. The fix deletes the ridge term:
the step is `INTERNAL_GAINS_ALPHA * y` alone, its expected value zero only at a
zero residual. **No per-hour count**: the earlier draft's shrink is dropped, so
nothing new persists, no coordinator attribute is added (`coordinator_attrs`
unchanged), the store's `internal_gains_profile` key and `store.DOMAINS` are
unchanged, and design/R11-ARCH-fabric-learner's extracted signature (profile or
None, parameters, start, residual, hours -> profile) fits as written. The tether
that remains is the existing clip and the convergence gate
(`internal_gains_gate_open`). Measured at the base with the harness's own
ridge-zero arm (`## Figures`): recovery rises, the drifting arm's spurious gain
doubles; that is the acceptance and its stated cost.

`INTERNAL_GAINS_RIDGE` (`const.py:1214`) has three harness readers at main:
`dev/audit/rounds/round10/study-ident/eta_rolling.py:195` reads it (deleting the
constant raises there), `dev/audit/harnesses/r10_night_folds_alternatives.py:75`
and `dev/audit/rounds/round11/D2/s3/m5_crosscov.py:60` assign it (inert once no
production code reads it, so m5's `--perturb-ridge0` arm equals its default arm
after the fix: that equality is the acceptance, not a fault). Shape: the constant
is deleted with the term and `eta_rolling.py` keeps its figure by a local
`0.02` named in its own file; if `tests/structure.py`'s `const.py` symbol check
or the closures disagree, the fixer keeps the constant instead, documented as
the round-10 value the study harnesses reproduce, and says which in the PR body.
`_fold_internal_gains`'s docstring loses "the ridge term keeps every hour
tethered": the tether is the clip and the gate.

### 3.5 Carry 3 against `dev/audit/harnesses/cop_dither_fabric.py`

The harness gives the house learner's sample count and stored value per arm
with a null twin: at the base the dither rows lose samples against
`null_dither0_*` with `house_scale` equal to four decimals (`## Figures`). It
does **not** give which refusal took each lost cycle. Designed: the fixer first
adds one row per arm tallying the house fold's refusal codes (the instrument, in
the same file); a lost cycle whose code is a freeze reason is this group's and is
scoped by sample kind (the dither moves the COP scale, not room air); any other
code is routed with its row. Acceptance: the dither rows' `house_samples` within
the null twin's count less the pre-dither loss the carry records, value
unchanged. The lower-floor learner stays unreached (the harness docstring: its
two-zone driver pins the house scale at its clamp).

## 4. Alternatives (lost on the code)

- A freeze test per learner kept equal by a test: the measured state (three
  learners, three answers).
- Facts handed to each learner module: a learner would hold coordinator state it
  does not own, and `dhw_learning.py` would import the coordinator's input health.
- The predicate as a coordinator method with an `away` branch only: keeps the
  two-owner row, adds statements to the class, leaves four local reasons unordered.
- Local evidence computed by the coordinator: reads draw-range, span and charge
  internals across the seam (`private_cross_module`).
- D2-s3-08 by holding every charge-affected fall provisional: `ChargeSettle`
  gains state across heated intervals and a second settle path.
- D2-s3-10 by a whiteness refusal: refuses the quantised arm instead of pricing it.
- D2-s3-11 by a count-shrunk rate: a new persisted per-hour count, a coordinator
  attribute at zero `coordinator_attrs` headroom, and a changed fabric signature.
- P5 by routing to another group: the told terms are this file's gate (`sysid.py`
  is this group's hot file); pricing reuses the told mechanism unchanged.

## 5. Sibling sites: the class enumeration

The tracked enumerator `sweep_N_confounded_learner.py` and the probe
`probe_N_unobserved_dhw.py` are on no ref, so revision 2's enumerator is these
greps at `origin/main` 78d3b40221 (the fixer re-runs them at the merge base;
a line they print that the tables below do not name is a new site):

- E1, every reader of the attribution or the plan split:
  `git grep -n -E 'attribution\(|_commanded_split\(\)|_planned_split\(|dhw_share\(|space_heat_kw\(|ran_hot_water\(|bridges_hot_water\(|space_draw_kw\(|space_share\(' -- custom_components/heatpump_optimizer`
- E2, every learner fold in the coordinator, checked against the persisted keys
  of `store.DOMAINS` (`store.py:340`):
  `git grep -n -E '\.(observe|observe_[a-z_]+|fold|record|update)\(|def _(fold|learn|async_learn|record|track|observe)' -- custom_components/heatpump_optimizer/coordinator.py`
- E3, the plan's own channel flags read as attribution:
  `git grep -n -E 'get\("(dhw_power|dhw_heating_active|power)"' -- custom_components/heatpump_optimizer/coordinator.py`
- revision 1's freeze greps (`_learning_frozen\(|_away_state\.active|recovery_active`;
  `frozen|_external_heat_active` in `dhw_learning.py` and `draw_range.py`;
  `cop=|outdoor_temp` in `sysid.py`) cover the freeze callers and the told inputs.

**Listed, 10 sites (§3.2 rows):** `_fold_flow_lift` (`coordinator.py:979`,
revision 2); `_interval_measured_heat_kw` (`:1011`); span close house and
lower-floor (`:1184`, `heat_energy.py:325-326`); span close COP (`:1192`);
`_interval_space_power` (`:5014`); `_fold_measured_cop` (`:5276`); the
draw-range gate (`:9998`); the energy totals (`:10316`); the sysid experiment
(`:11042`, revision 2); and, measured first, `DhwProfileLearner`'s heated flag
(below).

**Covered downstream, 6, no read of their own:** the window detector
(`_vent_cusum.update`, `:5787`), the solar aperture (`:5810`) and the gains fold
(`:5814`) run only on an interval `_interval_space_power` or the span close
handed the house fold; `MeasuredCop.record`, `_observe_cop_health` and
`_fold_capacity_envelope` (`:5398-5401`) run only inside `_fold_cop_evidence`,
past the two COP rows.

**Excluded, 20, each with its reason:**

| site | reason |
|---|---|
| `bridges_hot_water` (`heat_energy.py:540`, read at `:612` and `coordinator.py:1146`) | observed charges only; an unobserved one answers false, the conservative side |
| `cop_duty` (`coordinator.py:5279`) | reached only past `mode_observed` |
| slab estimate (`coordinator.py:1105`, `draw_range.py:455`) | runtime state, no store key; accepted by the verdict (note 9b3d1e14) |
| diagnosis record (`coordinator.py:1292-1293`) and diagnosis inputs (`:10637`) | diagnostics, never folded |
| `_commanded_power` (`:4991`) | the whole sum, no split |
| the pending prediction's `split`, `space_power`, `dhw_power` (`:10090-10094`) | writers, not readers |
| `attribution` itself (`heat_energy.py:420`, `:509`) | the owner of the choice; the evidence sits beside it |
| buffer cooling (`:5600`) | reads the plan's space ask as the buffer's heated flag; an unplanned hot-water charge leaves the space buffer unheated, so its standby sample is genuine |
| power headroom (`:8913`) | a planner read, not a fold |
| accuracy sample (`:10034-10070`) and the snapshot bias (`:9662`) | whole-plan power against the whole meter: no split, and the error an unplanned charge leaves there is real |
| defrost inference (`:9971`) | whole draw against the whole ask, no split; listed in §3.2 for ask-ignored |
| defrost duty (`:9962`) | the defrost flag, no power |
| kW-per-Hz map (`:10817`) | the compressor's electrical operating point, whichever duty |
| realised peaks (`:8657`, `:8770`) | the whole meter |
| duty switch (`pump_arbiter.py:1945`, `duty_switch.py:557`) | run or not, on the whole plan |
| external-heat detector (`:5213`) | judges a tank rise against the pump's own maximum rise, so a pump charge is not external heat by construction; runtime |
| operation score (`:10304`) | a grade of the ledger |
| price shape (`:8600`), comfort weight, curve learner | no plant power read; the curve learner is the comfort row |
| `rooms.gate(..., away=...)` (`:6307`) | a planner gate, not an ingest |
| `slab_seed`, `wear`, `learner_progress` | fold no interval sample, or already ask `_learning_frozen` |

**`DhwProfileLearner`'s heated flag, measured first** (E3, `coordinator.py:3766`,
`dhw_learning.py:419`). It reads the plan's `dhw_heating_active`, not the
attribution, and its own tank reading is its input. On an unplanned charge
every rise is refused already (`async_learn_cooling` `:540`, `async_learn_usage`
`temp_drop < 0.15`, `async_fold_draw_stats`' `max(0.0, ...)`); the one exposure
is the charge's start dip in a net-falling interval, booked as a draw and not
provisionally, because `ChargeSettle.classify` keys on the plan's flag. The fixer
adds a plan-flag-off charge arm to `dev/audit/rounds/round11/D2/s3/m5_tankfall.py`
first. If it books under the D2-s3-08 band (0.05 kWh), the site is excluded with
that figure in the PR body. Otherwise it is this group's own-seam instance,
built in the PR: an unheated interval whose tank rose past the evidence band
with the settle closed opens `ChargeSettle` with its dip credit, so
`ChargeSettle.advance`'s existing rise branch takes the dip back from the open
draw occurrence, as for a planned charge. The usage hour the dip folded already
stays, a stated residual. No new state, no store key.

**Coverage, corrected:** every reader E1 prints and every fold E2 prints is a
listed row, covered downstream, or excluded above. Revision 1's "every reader of
the attribution" claim missed `_fold_flow_lift`, the sysid ask and the span COP
fold.

## 6. Evidence plan

Failing tests first, `tests/features.py`: the freeze module's table (each reason
by sample kind; the nine unchanged); away freezes gains, draw stats and comfort
quiet and not tank standby; the curve learner's recovery freeze kept; an
unobserved space-only span with a tank rise refused, with no rise kept, with a
plan charge kept; the same three for the measured-COP fold and the draw-range
window; a ceiling sample at the floor in force refused, at 4.0 kW kept; a
60-minute charge books no dip; `arm` with the switch off writes nothing to the
collaborator; the R9-P5 sweep gains the learned-profile arm and the COP and
outdoor arms; the gains step's expectation is zero at the genuine gain.

Added by revision 2, each failing on today's code where it says so:
- `_fold_flow_lift`, on the `_fl_coord` fixture (`tests/features.py:34994`):
  an unobserved, plan-space-only cycle whose tank rose past the band leaves
  `bias_k` and `samples` unchanged (fails today: `:989` folds); the same cycle
  with no rise folds (null); a cycle whose plan carries a hot-water share under
  `_COP_CURVE_SHARE` (0.15) with the same rise folds, because the plan put hot
  water in it and the evidence's plan-no-DHW conjunct reads false (the
  conjunct's null); an observed cycle is untouched by the evidence.
- the sysid experiment: an unplanned-charge cycle during a step stands the
  experiment down, and no sample of it reaches `identify()` (fails today); no
  rise, the step runs (null).
- the span COP fold: a span whose rise is spread under the band per cycle but
  past it over the span folds no COP (fails today).
- the energy totals: an unplanned-charge interval books to `dhw_energy_kwh`;
  no rise, to space (null).
- `ceiling_frozen`: a ceiling-frozen experiment interval folds into neither the
  ceiling store nor the window (note 9b3d1e15).
- #944 kept: a defrosting inference interval still folds through the
  delivered-ratio ask (note 9b3d1e16).
- after #3737: an unplanned-charge interval refused by `:9998`'s `frozen=`
  commits no map run (`draw.map.commit_runs(keep=...)`, note 9b3d1e13).
- the DHW heated-flag arm of §5 in `m5_tankfall.py`, measured before any change.
- before changing `HeatEnergyMeter.observe_cycle`'s signature (one caller,
  `coordinator.py:1129`), the fixer greps `tests/` for direct calls: none at
  main 78d3b40221 (note 9b3d1e19).

| finding | harness, both ends | null control |
|---|---|---|
| D7-s2-01 | `dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py` contaminated_ingest 3 -> 0 | home arm ingests; `m3_away_drift.py` gains at g0 |
| D12-s3-03 | `dev/audit/rounds/round11/D12/s3/counter_spans.py --sees-dhw --no-mode`: `inflated_spans_folded` -> 0, both ends recorded on one platform (the plan solve differs by platform, note 9b3d1e18) | `--sees-dhw --no-mode --plan-only`: `space_spans_folded` equal at both ends (`## Figures`), `inflated_space_spans` 0 |
| #3760 sweep | the same file, the finding arm's `cop_records` loses the inflated span; a features value probe for the cycle path; the flow-lift and sysid tests above | the plan-only arm's `cop_records` equal at both ends |
| D2-s3-08 | `dev/audit/rounds/round11/D2/s3/m5_tankfall.py` long_a/long_b under 0.05 kWh | the short shape unchanged |
| D2-s3-09 | `dev/audit/rounds/round11/D2/s3/m5_drawrange.py` narrowing -> 0 | uncensored top 4.0 still learns 4.0 |
| D2-s3-10 | `dev/audit/rounds/round11/D2/s3/m5_sysid.py` miss share per noisy arm at most 0.10 | white_0.005 and noise-free still admit |
| D7-s2-02 | `dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py` biased_admitted 3 -> 0 | told cells admitted |
| P5 (#3767) | `probe_told.py` at handoff/audit-r11-sweep-SW9 32a372faae, path `dev/audit/rounds/round11/sweep/P5/D14/sweep-P5/`: past_bar -> 0 | its `--null` 0; the keep table |
| D2-s3-11 | `dev/audit/rounds/round11/D2/s3/m5_crosscov.py`: `gain_recovery_mean` to its `--perturb-ridge0` figure | `scale_bias_nogain_mean` not worse |
| D5-s4-02 | `dev/audit/rounds/round11/D5/s4/comments.py --file custom_components/heatpump_optimizer/sysid.py` unresolved 2 -> 0 | other units unchanged |
| carries 0-1 | `dev/audit/harnesses/cop_duty_floor.py` `defrost_inferred_*` toward 1.000 | draw-equals-ask stays 1.000; `selfset_2.2_swing*` unchanged |
| carry 3 | `dev/audit/harnesses/cop_dither_fabric.py` dither rows' `house_samples` | `null_dither0_*`, `no_probe_*` unchanged |

Goldens: none expected to move; any that does is claimed with its direction in
`tests/golden/claimed_drift.txt`, else both claim files byte-identical. Mutation
targets: each reason's kind row; the order; the plan-no-DHW conjunct and the tank
band; the floor tolerance; the heated-bound test; the verdict string;
`sysid.py:1458`'s read; the noise term, the clamp, the prior-width branch, each
told member; the deleted ridge (restoring it must fail the gains test); revision
2: the space-heat kind at `_fold_flow_lift`'s ask (reverting it to room-air must
fail the flow-lift test), the evidence passed at the sysid ask, the span COP
refusal, the energy totals' evidence branch.

## 7. Hot files, serial position, carries

Hot files: `sysid.py`, `accuracy.py`, `dhw_learning.py`, `heat_energy.py`,
`draw_range.py`, `coordinator.py`, `dhw_draws.py`, `tests/features.py`, the
harness file of §3.5, and the new module, put in a measured closure in
`tests/closure.py` by the same pull request. After `R11-SEAM-plant-model`
(merged); before R11-ARCH-fabric-learner. `draw_range.py` is shared with
R11-OUTSIDE-HONEST-METERED-FLOOR: whichever merges second rebases the floor read
(§3.2). No p1/p2 split. Budgets: `coordinator_attrs` and `seam_cut_total` read
at their caps at the base; the fixer measures both before and after moving the
reasons out (fixer note 5); a rise is paid in the pull request, else stop and
ask before pushing.

Order with open pull requests: #3737 (R11-CARRY-DRAWMAP, open at
2b95078faf) moves `_fold_measured_cop` (`coordinator.py:5312`), the
`accuracy.py:1280` neighbourhood and `draw_range.fold` (`:690`): the fixer forks
after it merges, or rebases onto it before step 2, and names which in the PR
body. #3812 adds `_plan_let_go` above `_tail_freeze`: adjacent text only.
#3714 (the floor in force) has merged. Carry 2 is §9, outside this order.

## 8. Revise points answered

1 §3.2 rows for `_fold_measured_cop`, the `coordinator.py:9998` gate,
`_interval_measured_heat_kw`, `_interval_space_power`; `bridges_hot_water` and
`cop_duty` safe, with code. 2 §3.3, priced, widths `decision: owner`. 3 §3.1
boundary table and the `power_frozen` split. 4 §3.4, no count. 7 §3.2, the
floor in force. 5 §3.2 plan-no-DHW conjunct; §6 the null arm's figure.
6 §3.5. Routed decision: §7, `decision: owner`.

Revision 2, against 6b72a4ab21. 1 (class-open, `_fold_flow_lift`): verified at
main (`:975` room-air ask, `:979` plan split when unobserved, `:989` folds the
supply into the persisted `flow_bias`); §3.2 row, §6 test, mutation target. The
class closed, not the instance: §5's enumeration (10 listed, 6 downstream, 20
excluded) added the sysid ask and the span COP fold, and states the DHW heated
flag as measured first. Fixer notes folded into the body: 9b3d1e10 (§3.2,
`floor_in_force_kw`), 9b3d1e11 (§3.2 gains row), 9b3d1e13 (§6, §7), 9b3d1e14
(§3.2 totals row), 9b3d1e15 (§3.1, §6), 9b3d1e16 (§3.1, §6), 9b3d1e17 (§3.4),
9b3d1e18 (§6), 9b3d1e19 (§6). 9b3d1e12 is R11-ARCH-fabric-learner's. Carry 2:
§9, `pending owner decision`.

## 9. Carry 2 (item c25b53cc), pending owner decision

Bounded: c1 of design/R11-OUTSIDE-SELF-SETTING-PUMP (0acbbc8b91), the dither of
the plan's heat ask, and the closed-loop planner harness it needs. Nothing in
§1-§7 reads or waits on it; the fixer builds all of that without this answer,
and this part ships in a second pull request of this group once ruled. The
owner ruled on 2026-11-18 (`dev/programme/RULINGS.md`) that it stays in this
group. That ruling did not say which seam moves the plan's ask, and §3.3's two P5
widths are also the owner's.

| option | what moves | cost |
|---|---|---|
| A, learner owns the probe | `MeasuredCop` decides the excitation owed this cycle (a bounded heat-ask offset with a seeded coin), as a2 already decides the scale owed; the optimizer reads it as one more input bound, like a comfort bound, and owns nothing new | `optimizer.py` joins this group's hot files (planner groups rebase), one new optimizer input, the closed-loop harness built here first; L. Visible as plan steps off the optimum, within comfort bounds |
| B, planner owns it | a planner group designs and builds c1; this group keeps only the verdict reader it has | needs the owner to name the planner group and add the edge; this group's carry closes as moved. The planner then moves an ask to identify a learner's parameter, the two-owner shape the self-setting design priced |
| C, measure first | this group builds only the closed-loop harness mode (`cop_duty_floor.py` re-pricing the ask against the dithered scale, the self-setting design's "open risk"), and the next design picks A or B on its figure | no plan behaviour changes this round; the a2 open risk is measured, not guessed; c1 itself waits for the figure |

Recommendation: A, built after C's harness. One owner keeps the decision to
probe (the learner, which owns the parameter and already owns a2's dither), and
the planner's change is an input it obeys, not a decision it makes. The harness
is needed under A and B alike, so C's step is never wasted. `decision: owner`
(the seam, A, B or C; and the two P5 widths of §3.3).

## Figures

Measured at the base by revision 1's seat (Linux, venv-ci python3), each by its
command. The verdict's macOS seat read the D12 finding arm as
`inflated_spans_folded=2`, `space_spans_folded=3`, `cop_records=4`, and
`--plan-only` as `spans_plan_dhw_share=4`; acceptance is therefore "-> 0" and
"equal at both ends" on one platform, never these literals:
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D12/s3/counter_spans.py --sees-dhw --no-mode --plan-only`:
  `space_spans_folded=2`, `inflated_space_spans=0`, `spans_plan_dhw_share=2`, `cop_records=4`.
- the same without `--plan-only`: `inflated_spans_folded=1`, `space_spans_folded=2`, `cop_records=3`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s3/m5_crosscov.py`:
  `gain_recovery_mean=0.5573`, `gain_spurious_max=0.0293`, `scale_bias_nogain_mean=+0.0201`;
  with `--perturb-ridge0`: `0.7748`, `0.0571`, `+0.0186`.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_dither_fabric.py`:
  `dither_true0.8_2C` 578 house samples against `null_dither0_true0.8_2C` 671;
  `dither_true0.8_9C` 646 against 671; true1 rows 671 at both; `house_scale=1.1000` on every row.

### Notes for the fixer

- `coordinator.py:9431` is an exact-text anchor of the fabric group's spike;
  its revalidation stops on it after this merge. Carry: R11-ARCH-fabric-learner (item 9b3d1e01)
- Keep today's reason strings: `learner_progress.py` and the freeze notes
  display them. Carry: R11-SEAM-learners (item 9b3d1e02)
- Carries 0-1: key on `ASK_IGNORED`; if the pending arm still learns below
  1.000, report it, do not widen to pending (ADR-008 T8). Carry: R11-SEAM-learners (item 9b3d1e03)
- Move each reason's comment with it out of `_learning_frozen`. Carry: R11-SEAM-learners (item 9b3d1e04)
- `SysIdConfig.enabled` is removed only if no other reader or stored payload
  reads it. Carry: R11-SEAM-learners (item 9b3d1e05)
- D2-s3-11: the ridge-zero arm recovers 0.7748, not 1.0; the remaining
  shortfall is not this finding's mechanism and is reported with its row, not
  chased in this pull request. Carry: R11-SEAM-learners (item 9b3d1e06)
- The probe of #3760 (`probe_N_unobserved_dhw.py`) is not in the tree at the
  base; the features value probe of §6 stands in for it. Carry: R11-SEAM-learners (item 9b3d1e07)
- The span COP refusal and the per-cycle `clean["cop"]` AND must not double-log
  one span's refusal in `_learner_freezes`; note the reason once. Carry: R11-SEAM-learners (item 9b3d1e20)
- The sysid stand-down on an unplanned charge costs an experiment on a pump that
  self-charges often; state that cost in the PR body with the features arm's
  figure, and do not widen the band to buy liveness. Carry: R11-SEAM-learners (item 9b3d1e21)
- Re-run §5's E1-E3 at the merge base and paste the line count of each; a line
  no table names stops the PR until it is listed or excluded. Carry: R11-SEAM-learners (item 9b3d1e22)
