# Design: R11-SEAM-learners (round 11, size L), revision 1

Architect note, extended (`dev/governance/roles/designer.md`). Base
9d65fe80b0cc76f4a65c1963fe244f8c296bdd26 (`origin/main`); code read there. The
predecessor `R11-SEAM-plant-model` merged as #3731 (an ancestor of the base);
its handoff head 3bd933a0d482829a3e60eab0cc3cc7b14198228a, so the code read is
its merged state. Plan of record `plan/r11` at 1a2ff62c9aea96989f7f5c511e53b95d96667027:
ADR-008 (the predicate), ADR-003 part 2 (the switch), ADR-001 arm `fdjac`.
Revises 31ba57ec6c0ba6df06310bf1ae6d8a51fe8fb036 against design-verdict
702ffcc59f1c0a369dbe8d3a552a9d4938152a40; §8 maps each revise point to its
answer. No production code on this ref.

## 1. Findings

D7-s2-01, D12-s3-03, D2-s3-08, D2-s3-09 (the freeze); D2-s3-10, D7-s2-02,
D5-s4-02 and the `fdjac` arm (sysid); D2-s3-11 (the gains fold). Harnesses: each
finding's own, named under its class in `dev/audit/rounds/round11/ISSUES.json`.
Sweep instances beyond the findings, now covered: N-confounded-learner (#3760)
`_fold_measured_cop` and `_async_learn_lower_floor_loss` (§3.2); P5 (#3767)
`SystemIdentification.step` `cop` and `outdoor_temp` (§3.3). Carries 0-1
designed (§3.2); carry 3 designed against its harness (§3.5); carry 2 is a
two-owner stop (§7).

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
(delivered-ratio). A plant or room-air ask gets none of the additive ones.

**No learner holds a facts value.** The coordinator is the only builder of
facts, per call. What crosses each boundary:

| boundary | today | after |
|---|---|---|
| `HeatPumpOptimizerCoordinator._learning_frozen` | `*keys, room_air: bool` | `*keys`, keyword `sample` (default room-air), keyword `evidence` (default none); body: build facts, call the function |
| `DhwProfileLearner` (`dhw_learning.py:166`) | `frozen: Callable[[str], str \| None]`, bound at `coordinator.py:3765` to `_learning_frozen(room_air=False)` | the same callable typed as key plus the two keywords, bound to `_learning_frozen` unpartialled; the learner passes plant (standby dynamics, `dhw_learning.py:441`), occupancy (draw statistics) or tank-draw with its own charge-open evidence (draw booking) |
| `draw_range.fold` (`draw_range.py:665`) | `frozen: bool` | `frozen: bool` unchanged (window and idle), plus keyword `ceiling_frozen: bool` that gates `observe_ceiling` alone |
| `_settle_defrost` (`coordinator.py:9931`) | no freeze of its own; the inference branch reads `delivered_ratio` | the inference branch asks delivered-ratio with ask-ignored evidence before `self._defrost.observe`; the duty branch unchanged |

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

### 3.2 Who asks what (every site that reads the unplanned-charge evidence included)

The unplanned-charge evidence, owned by `heat_energy.py`: an interval or span
whose attribution is **not observed**, whose plan split put **no hot water** in
it (`a.dhw <= 0.0 < a.space`, the whole-unit rule `space_heat_kw` applies at
`heat_energy.py:239`), and over which the configured tank thermometer **rose** by
more than a design band (a named constant, the fixer's; the harness tank rises
4 K a charging cycle and falls 0.5 K otherwise). The meter takes the tank reading
in its per-cycle observe call and keeps the cycle's and the open span's first
reading, runtime only, so no store key moves; a cycle with no previous reading,
or an install with no tank thermometer, reads false: today's behaviour.

| site | today | after |
|---|---|---|
| `_fold_internal_gains` (house fold) | the house fold's room-air answer | occupancy ask before the step (D7-s2-01) |
| `_record_quiet_comfort_period` | room-air | occupancy (D7-s2-01) |
| `_track_curve_comfort` | private away/recovery test + room-air | comfort; `coordinator.py:9222-9223` deleted |
| `DhwProfileLearner` draw statistics, draw booking | external heat only (`dhw_learning.py:494`) | occupancy; tank-draw with charge open (D7-s2-01, D2-s3-08) |
| `_interval_measured_heat_kw` (`coordinator.py:1000`): house and lower-floor folds, slab estimate | room-air; `space_heat_kw` on the plan split | space-heat ask with the cycle's unplanned-charge evidence (#3760 sweep, lower-floor instance) |
| span close, house and lower-floor (`span_heat`, `heat_energy.py:325-326`) | room-air | space-heat ask with the span's evidence (D12-s3-03) |
| `_interval_space_power` (`coordinator.py:4994`) | `ran_hot_water` only | space-heat ask with the cycle's evidence |
| `_fold_measured_cop` (`coordinator.py:5290`) | `_learning_frozen(...)` then, unobserved mode, `space_ref` | the same ask as space-heat with the cycle's evidence: an unplanned charge refuses as frozen instead of folding as a space sample (#3760 instance) |
| draw-range gate (`coordinator.py:9998`) | `not ran_hot_water(...)` | the same, and `power_frozen`'s companion ask (space-heat, the pending split's evidence) joins `frozen=`: an unplanned charge is not a running space sample |
| `draw_range.fold` ceiling store | `frozen=` | `ceiling_frozen=` with at-running-floor evidence (D2-s3-09) |
| `_settle_defrost` inference | `power_frozen` at the caller | delivered-ratio with ask-ignored (carries 0-1) |

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
  the running floor; this group reads it and defines none. If that group has not
  merged at this group's fork, the predicate reads `power_floor_kw`
  (`draw_range.py:556`), which that design keeps bit for bit, and the rebase
  swaps the read. Neither reads `DrawRange.observed()`, so its None (too few
  samples) does not arise; the floor's own fallback is the configured figure.
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

## 5. Sibling sites

`git grep -n -E '_learning_frozen\(|_away_state\.active|recovery_active|ran_hot_water\(|space_heat_kw\(|attribution\(' -- custom_components/heatpump_optimizer`
and `git grep -n -E 'frozen|_external_heat_active' -- custom_components/heatpump_optimizer/dhw_learning.py custom_components/heatpump_optimizer/draw_range.py`
and `git grep -n -E 'cop=|outdoor_temp' -- custom_components/heatpump_optimizer/sysid.py`.
Covered: every `_learning_frozen` caller (keyword map, §3.1), every reader of
the attribution (§3.2, with the two safe ones named), the told inputs (§3.3).
`coordinator.py:6307` (`rooms.gate(..., away=...)`) is a planner gate, not an
ingest. `slab_seed`, `wear`, `learner_progress`, `external_heat` fold no
interval sample or already ask `_learning_frozen`. The fixer re-runs the
commands at the merge base.

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

| finding | harness, both ends | null control |
|---|---|---|
| D7-s2-01 | `dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py` contaminated_ingest 3 -> 0 | home arm ingests; `m3_away_drift.py` gains at g0 |
| D12-s3-03 | `dev/audit/rounds/round11/D12/s3/counter_spans.py --sees-dhw --no-mode`: `inflated_spans_folded` 1 -> 0 | `--sees-dhw --no-mode --plan-only`: `space_spans_folded` equal at both ends (`## Figures`), `inflated_space_spans` 0 |
| #3760 sweep | the same file, the finding arm's `cop_records` loses the inflated span; a features value probe for the cycle path | the plan-only arm's `cop_records` unchanged |
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
told member; the deleted ridge (restoring it must fail the gains test).

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

Carry 2 (item c25b53cc, the heat-ask dither c1): **a stop for that part.**
design/R11-OUTSIDE-SELF-SETTING-PUMP (0acbbc8b91) sizes c1 "L, two owners
(planner and learner)": it moves the plan's ask, which the planner owns, to
identify a parameter the learner owns; `designer.md` step 2 makes two owners a
design finding, report and stop. The owner ruling of tvofi 2026-11-18 keeps it
in round 11, so only the owner can re-home it. Carry: R11-SEAM-learners (items
c25b53cc) `decision: owner` which seam owns c1, or that this group takes both.

## 8. Revise points answered

1 §3.2 rows for `_fold_measured_cop`, the `coordinator.py:9998` gate,
`_interval_measured_heat_kw`, `_interval_space_power`; `bridges_hot_water` and
`cop_duty` safe, with code. 2 §3.3, priced, widths `decision: owner`. 3 §3.1
boundary table and the `power_frozen` split. 4 §3.4, no count. 7 §3.2, the
floor in force. 5 §3.2 plan-no-DHW conjunct; §6 the null arm's figure.
6 §3.5. Routed decision: §7, `decision: owner`.

## Figures

Measured at the base on this seat (Linux, venv-ci python3), each by its command:
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
