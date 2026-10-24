Part of #2499.

The unsensed slab (no floor-return sensor) was moved forward open-loop along the previous plan's
`slab_temp_trajectory`, which assumes the heat the plan COMMANDED was delivered. When a pump drew
less (setpoint-driven, capped or modulating down), the slab estimate kept heat that never arrived.
The house heat-loss learner then replayed the next interval from that too-warm slab, found the room
colder than it predicted, and booked the gap as fabric loss. `house_heat_loss_scale` climbed and the
plan booked more heat each day: the brief's over-booking.

The fix: where a power entity exists, `coordinator._propagated_slab` replays the elapsed interval
through `_replay_interval` (the house learner's own replay, same model, and the flow-meter
substitution where a heat meter exists) at the metered space draw `draw_range.space_draw_kw`.
Standby below `draw_range.running_kw`'s floor counts as no heat. A resistive element on the meter,
no reading, no previous sample, or a gap past `HOUSE_LOSS_MAX_SAMPLE_HOURS` falls back to the plan's
trajectory, which is the old behaviour. No heat meter is needed. **An install with no power entity
at all is unchanged**: with no draw reading, the delivery shortfall cannot be told apart from UA
(see Null control and Forward-carry).

The fix sits on its own seam. The draw arithmetic (running floor, space share) goes in
`draw_range.py`, which owns the draw concept and has no HA import. The coordinator only orchestrates
(`_propagated_slab` is mapped `core` in `tests/seam_map.json`). Alternatives that lost:
(a) reuse `_interval_space_power` for the slab. It returns `None` under `COP_TRACKING_ERROR_GATE`
exactly when the pump draws far less than commanded, so the slab would fall back to the commanded
trajectory in the very intervals that cause the bias. (b) Correct the learner instead, by skipping
samples after an under-delivery. That starves the learner and leaves the slab wrong for every other
reader. (c) Use a heat-meter-only path. The brief forbids it (every install, no heat meter).

To pay the budgets, the DHW tracking block in `_update_current_state` moved to
`_track_dhw` (seam `dhw`), and `_settle_interval_diag`'s inline space share now calls
`draw_range.space_share`.

## Head

d6ab12b4b7f0554f6fd18915ddc6b71b54acf1db. The figures below were measured at 428a758e545669c6ce5c1e8dcb8cdcf46b0128ea
(merge of origin/main 145bfe197; re-measured after main moved from 50af6174f to 145bfe197, whose 11 later commits touch no `custom_components/` file, no test fixture and no budget leaf, only `tests/ci_ratchet.py`, `tests/entities.py` and delivery rows, so the base column of the Figures table is the production tree both times), against merge base 145bfe197b9e7c09eb90bedadec44c6bc19d679d. d6ab12b4b
changes no production or test code. It adds one `tests/closures.json` INERT-READS entry for the
harness (`tools/pr/ci_predict.py --apply-inert`) and deletes the stale ledger pin
`killed_by/coordinator.py/_settle_interval_diag.CMP_BOUND.611f0784.json`, which named the inline
space share that moved to `draw_range.space_share`.

## Mutation proof

Run from detached worktrees at the head, `PYTHONPATH=tests/hastub python3 tests/features.py`:

- M1, the predicate of the closed-loop branch in `_propagated_slab`:
  `if kw is not None and ...` -> `if False and kw is not None and ...`. Red:
  `FAIL #2499: a metered pump that drew nothing leaves the slab cooling, not at the plan's commanded 25 degC [slab=25.000]`,
  `FAIL #2499: the slab rises with the metered draw, below the commanded trajectory while the pump draws less than 4 kW [slab off/1kW/4kW=25.000/25.000/25.000]`
  (`2 of 4356 FEATURE CHECKS FAILED`, rc=1).
- M2, the standby floor in `draw_range.running_kw`:
  `drawn_kw > floor` -> `drawn_kw > 0.0`. Red:
  `FAIL #2499: a standby draw under the running floor heats nothing [slab standby=22.907 off=22.840]`
  (`1 of 4356 FEATURE CHECKS FAILED`, rc=1). Both restored; worktrees discarded.

Failing test first: the head's `tests/features.py` against the merge base's production tree
(`cp` into a base worktree, then restored) failed
`#2499: a metered pump that drew nothing leaves the slab cooling, not at the plan's commanded 25 degC [slab=25.000]`
and `#2499: the slab rises with the metered draw, below the commanded trajectory while the pump draws less than 4 kW [slab off/1kW/4kW=25.000/25.000/25.000]`,
then raised `AttributeError: module 'heatpump_optimizer.draw_range' has no attribute 'space_draw_kw'`.
At the head, all 6 `#2499` checks pass and `ALL 4356 FEATURE CHECKS PASSED`.

## Null control

- No power entity (`nometer_half` arm): the row is identical at both ends (scale 1.828,
  plan/deliv 1.936, plan_kwh [15.6, 16.8, 20.4, 24.9, 27.3]). The meter is what moves the result,
  so the fix leaves a no-meter install alone. This is also the residual: the shortfall cannot be
  seen there.
- Flat price, ideal delivery (`null`, `true0.5`, `owner_ideal`): the learned scale stays on the
  truth at both ends (null 1.015 -> 0.992 against true 1.0; true0.5 0.512 -> 0.509 against 0.5;
  owner_ideal 0.607 -> 0.608 against 0.6). With no shortfall, the fix has nothing to correct.
- Slab oracle (`*_oracle` arms seed the TRUE slab): the rows are identical at both ends, by
  construction. They are the upper bound: owner_i01_oracle scale 0.62, plan/deliv 1.193.
- In-test null: `#2499: without a power meter the slab follows the plan (null control)` and
  `with no previous sample time the slab follows the plan` hold at the base and at the head.

## Figures

Harness `dev/audit/harnesses/r10_demand_overbook.py` (sha1 f0575c58b587d9a41e922fb5393e1a30a7ddba0b,
this head's copy). Run at both ends from the same copy:
`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py --dp`.
The run is synthetic: 30-min closed loop, real coordinator learners and real optimizer, no heat
sensor, flat price unless `spread`, days 2..end. `scale` is the learned `house_heat_loss_scale`.
`plan/deliv` is the 12-h plan energy at 00:00 and 12:00 summed per day, over the electric energy
delivered. `samples` is the count of accepted house-learner samples.

| arm (true scale) | base scale | head scale | base plan/deliv | head plan/deliv |
|---|---|---|---|---|
| owner_i01 (0.6; 1.5-5 kW clamp, delivers min(3, 0.4c), 0.1 kW idle) | 1.185 | 0.628 | 1.634 | 1.18 |
| owner_i01_spread (0.6; same, price spread) | 1.572 | 0.724 | 1.866 | 0.688 |
| owner_i03 (0.6; 0.3 kW idle) | 1.0 (0 samples) | 1.0 (0 samples) | 1.639 | 1.091 |
| meter_half (1.0; delivers 0.5c) | 2.102 | 1.247 | 1.67 | 1.095 |
| meter_sat3 (1.0; caps at 3 kW) | 1.302 | 1.099 | 1.34 | 1.162 |
| slab3x (1.0; 3x slab mass) | 0.88 | 0.861 | 0.944 | 0.943 |
| nometer_half (1.0; no power entity) | 1.828 | 1.828 | 1.936 | 1.936 |
| owner_i01_oracle (0.6) | 0.62 | 0.62 | 1.193 | 1.193 |
| meter_half_oracle (1.0) | 1.05 | 1.05 | 0.986 | 0.986 |

The head reaches the slab-oracle bound on owner_i01 (0.628 against 0.62). meter_half still sits
above its oracle (1.247 against 1.05), which is the share of bias this fix does not remove.

DP reference (`--dp`, owner_i01's last 12-h window). This is a DP over a (room, slab) grid on the
optimizer's own objective with cycling and capacity relaxed (`_dp_reference` docstring), on the
learned model and on the true house:

- learned model: base plan_kwh 5.97 / DP 4.25 (cost gap 0.0613); head plan_kwh 5.37 / DP 3.88 (cost gap 0.1703)
- true house from its true slab: base DP needs 1.38 kWh against plan 5.97 (gap 0.658); head DP needs 3.75 against plan 5.37 (gap 0.1652)

This is one window, and the two ends start from different states. It is a reference, not an
optimality proof (see Forward-carry).

Architecture: `python3 tools/audit/archscore/score.py --diff 145bfe197b9e7c09eb90bedadec44c6bc19d679d HEAD`
prints dS +0.3168 (duplication_copies 40 -> 39, coord_footprint 2470 -> 2472).
`python3 tests/structure.py` passes. Every re-recorded `tests/structure_budgets.json` row moves down
(class_excess_loc 18217 -> 18215, duplication_copies 17 -> 16, max_class_loc 8457 -> 8433,
seam_cut_total 710 -> 708). Nothing is raised.

Golden: `GOLDEN_MODE=drift GOLDEN_REF=145bfe197b9e7c09eb90bedadec44c6bc19d679d PYTHONPATH=tests/hastub python3 tests/golden.py` prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `no committed fixture is stale`. Nothing is claimed, and both claim files are untouched.

Class census (step 8). Rule: `grep -n "_open_loop_plan_value(" custom_components/heatpump_optimizer/*.py`
lists each place a plan prediction stands in for an unsensed state. It returns the definition and two call sites:
`slab_temp_trajectory` (closed in this diff, via `_propagated_slab`) and `dhw_temp_trajectory`
(the tank seed in `_update_current_state`). The tank seed is a distinct case: it seeds only while
no tank reading exists, and no learner replays from it. It is left open here and listed under
Forward-carry.

## Architecture score

- `coord_footprint` 2470 -> 2472: `_propagated_slab` adds the orchestration statements that read the meter, call `draw_range.space_draw_kw` and replay through `_replay_interval`. The arithmetic itself is in `draw_range`, and moving the DHW block to `_track_dhw` paid for the rest.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` lists 13 sites added by the diff. Dispositions:

- `custom_components/heatpump_optimizer/draw_range.py:296 CMP_BOUND`: value check `#2499: a standby draw under the running floor heats nothing` (kills the M2 mutant above); pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:324 GUARD_OFF`, `custom_components/heatpump_optimizer/draw_range.py:326 RETURN_DEL`, `custom_components/heatpump_optimizer/draw_range.py:305 CMP_BOUND`, `custom_components/heatpump_optimizer/draw_range.py:305 RETURN_DEL`: value check `#2499: a resistive element sharing the meter gives no space draw; a pump not serving rooms gives 0 kW` (None / 0.0 / 2.0 for a (2, 1) split); pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/coordinator.py:6505 GUARD_OFF`: value checks `#2499: a metered pump that drew nothing ...` and `the slab rises with the metered draw ...`; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/coordinator.py:1011 RETURN_DEL`: value checks `without a power meter the slab follows the plan` and `with no previous sample time the slab follows the plan` (25.0 expected); pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/coordinator.py:1007 CMP_BOUND*2` (the `0.0 < dt_h <= HOUSE_LOSS_MAX_SAMPLE_HOURS` bounds): no local value check drives dt_h to either bound (the test uses 0.5 h). Pinned by `mutation-autofix` if killed; a survivor gets a written triage on this PR. M1 mutates the same predicate's `kw` conjunct, not these bounds.
- `custom_components/heatpump_optimizer/draw_range.py:295 CLAMP_DROP`, `custom_components/heatpump_optimizer/draw_range.py:296 RETURN_DEL`, `custom_components/heatpump_optimizer/coordinator.py:6468 GUARD_OFF`, `custom_components/heatpump_optimizer/coordinator.py:7659 GUARD_OFF`, `custom_components/heatpump_optimizer/coordinator.py:7670 RETURN_DEL` (the last three are the moved `_track_dhw` block): pinned by `mutation-autofix` where CI's mutation check kills them; a survivor gets a written triage, never an automated one.

## Red checks

- `mutation`: predicted red at this head, because prepr step 6d lists the 13 unpinned sites above, and `mutation` fails on a mutant no pin kills until `mutation-autofix` pins it after the push (`ci-autofix.md`). The cheaper detector is that step-6d prediction itself, which runs in seconds and named every site before the handoff. The answer is the per-site disposition above.
- Before the repair commit d6ab12b4b, `ci_predict.py` also predicted `tests / closures` (INERT READS) and `ledger` (STALE PIN). Both are repaired at this head. The static predictor `body_push.sh` runs is the cheaper detector that caught them.

## Forward-carry

- No-power-meter installs cannot tell a draw shortfall from UA. Harness `dev/audit/harnesses/r10_demand_overbook.py`, arm `nometer_half` (true scale 1.0, the pump delivers half of what is commanded, no power entity): the learned scale stays 1.828 and plan/deliv stays 1.936, byte-identical at base 145bfe197 and head 428a758e5. Against that, the metered arms move (owner_i01 1.185 -> 0.628, true 0.6; meter_half 2.102 -> 1.247). The ideal-delivery null arms stay on the truth at both ends (null 1.015 -> 0.992, true 1.0). So the residual is unobservability, not an unfixed bias. On such an install the health surface must report the learned heat-loss scale as unobservable, not as trustworthy. Carry: R10-UX-HEALTH (orchestrator ruling under mandate 6329234399).
- House learner gets zero evidence on a standby-drawing, under-delivering pump: owner_i03 accepted 0 samples in 10 days at both ends, because `COP_TRACKING_ERROR_GATE` in `_interval_space_power` refuses every interval. Carry: R10-LEARNER-DEFAULT
- Optimality: on its own learned model, the plan books 38-40% more kWh than the relaxed DP optimum, at both ends (one window). Carry: R10-SETPOINT-BOOST
- `dhw_temp_trajectory` open-loop tank seed (class census): Carry: R10-PUMP-MODEL

## Friction

none
