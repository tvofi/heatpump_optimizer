R10-COP-GATE part 5: the residual carries, items A and C of the brief. Part of #2262. Its core (the not-measurable state, the draw-follows-plan check, the latch time, the draw pairing) landed in #2917 and #2975, and item A makes that state reach the card in production. The brief asks this body to resolve the issue once A lands, but the group's roster `fixes` list is empty, and `body_push.sh`'s preflight refuses the closing keyword for it ("not in the intended list"). Resolving it is the orchestrator's call: add the issue to the group's `fixes`, or resolve it by hand after the merge.

**A. Model status copy (carry 18/19).** `ModelStatusSensor`'s `cop` attribute now also carries `cop_observability`, `cop_refusal` and `measured_cop_at`. Each is copied under its own name from the learning view (`data.get(...)`), with no boolean and no second derivation. The observed-COP sensor is unavailable exactly when the install is `not_measurable`, and Home Assistant hides an unavailable entity's attributes. The card's `copState` (heatpump-optimizer-card.js) already reads these three keys from this row, so its not-measurable branch can now fire in production.

**C. Flow-bias duty gate (carries 12 and 16).** `_fold_flow_lift` read the commanded split. Its duty gate now reads `heat_energy.meter_of(coord).attribution(coord._commanded_split())`, which is the mode dwell where observed and otherwise the commanded split, through `heat_energy.dhw_share`, at the same `_COP_CURVE_SHARE`. This is the existing owner of the choice, so no parallel rule is added. `_cop_reference_curve` already reads the same attribution, so the two gates now agree.

**Not in this pull request, reported as the remainder:**
- **D (learned top reaching the plan, carry 15).** `DrawRange.planned` returns `None` unless `engaged`, by design. The module docstring of `draw_range.py` says "a pump that realizes what it is asked must plan exactly as before", and the latch is what keeps the clamp from re-booking. Letting a learned top reach the plan while the latch is off changes what the plan books on every install with 48 or more full-command samples. That is a threshold and behaviour change, but the group's architect note fixes the shape as "a published reason, no threshold change". The brief's "eleven and twelve stored samples" also do not match `draw_range.MIN_SAMPLES` (48). They read as the CEILING-PROBE store's count, a module this seat did not measure. So D needs the orchestrator's (or a designer's) ruling on which surfaces may read the learned top, and on whether the plan's clamp may engage without the latch. Carry: R10-COP-GATE's brief (orchestrator).
- **B (heat-pump grade drivers, carries 5, 6, 13, 17).** This was not started. It mirrors `presets.house_grade`'s driver interface, publishes `machine_drivers`, extends the card renderer and adds hover strings. It is the largest item, and the brief already names it as the remainder if the diff would exceed an L. This seat's session also had a per-turn inline-read cap (see Friction), which made an L-sized pass impractical. Carry: R10-COP-GATE's brief (orchestrator).
- **E** is the designer's, not this seat's (brief).
- B and D are already carries 5, 6, 13, 15 and 17 in the group's roster brief, so nothing new is propagated. This seat writes no roster. The step-8 enumeration's two leads (`_interval_space_power`, and `_record_accuracy`'s `split` into `draw_range.fold`, under Figures) are unmeasured, and placing them is left to the orchestrator.

## Head

a35f5524f7c31ffe818c7bfa0d95590b5e5429ef (handoff/r10-cop-gate-p5), measured 2026-10-30T13:41Z against origin/main 507a9ec26. Base: origin/main 507a9ec264eb373b132248d752259254d8a9fa4d (merge base 507a9ec26).

## Mutation proof

- **A**: `sed -i '/^                "cop_refusal": data.get("cop_refusal"),$/d' custom_components/heatpump_optimizer/sensor.py`, then `PYTHONPATH=tests/hastub python3 tests/entities.py`. Result: `1 of 2485 ENTITY CHECKS FAILED`: `FAIL the model status sensor's cop row carries cop_observability, cop_refusal and measured_cop_at as the learning view publishes them, while the not-measurable observed-COP sensor is unavailable` (`cop_refusal: '<absent>'` on all three fixtures). Before the fix, the same check failed with all three keys `<absent>`. Restored afterwards.
- **C**: the tree with the fix lines absent, which restores the commanded-split gate (run before the fix was applied, with the test already in place), then `PYTHONPATH=tests/hastub python3 tests/features.py`. Result: `1 of 4606 FEATURE CHECKS FAILED`: `FAIL a hot-water-dominant window under a space plan folds no flow-bias sample; an all-space window folds one (null)  [switch-back ((2.2, 0.0), Attribution(space=0.05, dhw=0.45, observed=True), 1) / all-space (... 1)]`. This is carry 12's residual reproduced: plan split (2.2, 0.0), dwell 0.45 h hot water and 0.05 h space (dhw share 0.9 against 0.15), and one sample folds.

## Null control

- **A**: the heat-metered and draw-follows-plan fixtures in the same check carry the same three values on the model status row. The existing check `a COP not measurable here waits for a heat meter; ...` (tests/entities.py), which pins the observed-COP sensor's attributes for all three observabilities, passes unchanged, so the observed-COP sensor's attributes did not move.
- **C**: the all-space window (dwell 0.5 h space) folds one sample both before and after the fix. With no dwell, attribution falls back to the commanded split. The existing check `the flow-lift fold takes the same floor: a 14 kW nameplate at 2.2 kW folds` covers that no-mode-entity plan and still folds one sample after the fix (`ALL 4606 FEATURE CHECKS PASSED`).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2485 ENTITY CHECKS PASSED` at the head. The mutant above gives 1 of 2485 failed.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4606 FEATURE CHECKS PASSED` at the head. Without the C fix, 1 of 4606 failed (above).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`. Every script `scope.run` names was run with `PYTHONPATH=tests/hastub` and `GOLDEN_MODE=drift`, and each exited 0 at the head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `class_excess_loc` moved down by one, because module-level helper lines count in the coordinator's span and the `_fold_flow_lift` gate is one line shorter. The change is recorded by `python3 tests/structure.py --record` in this branch's last commit, with the row named in the commit message.
- `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py`: `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` (56 each). Five `coord_*` fixtures gained the three keys under `sensors.model_status.extra_state_attributes.cop`. Each key was grafted from that fixture's own committed `data` block, so no float was re-recorded on this host. The five are claimed in `tests/golden/claimed_drift.txt` as additions only.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, wave-script or instrument red predicted`, and 2 unpinned sites (below).
- The finder's instrument for C (the round-4 fixer's 5-check probe cited in #2854's body) is not in the tree. Its switch-back arm and both null arms are ported into `tests/features.py` (`_cf_fl_window`, plus the existing no-dwell check), and the before and after results are the mutation and null figures above.
- Class enumeration (fixer.md step 8): the rule is `grep -n "_commanded_split()" custom_components/heatpump_optimizer/coordinator.py`. At this head it returns 8 sites, each with a disposition. `_fold_flow_lift` is closed in this diff. Already attributed through `heat_energy`: `_interval_measured_heat_kw` (`meter.attribution(split)`), `_replay_gate` (`heat_energy.close_span(meter, ..., split, ...)`, where the meter splits by its own dwell) and `_cop_reference_curve` (`meter_of(self).attribution(...)`). Not a duty gate: `_commanded_power` (the total, space plus hot water). Gated on the live mode instead: `_propagated_slab`'s `draw_range.space_draw_kw(...)` (`space_served=signals.space_heat or not signals.mode_observed`). Two distinct leads, carried and not fixed here: `_interval_space_power` splits a metered draw by the plan's split, and `_record_accuracy`'s pending `split` feeds `draw_range.fold`'s running-space filter. Both are the same plan-versus-dwell shape on a power attribution rather than a curve duty, and both lie outside this group's owning seam (the architect note: COP eligibility and its published state).

## Unpinned sites

- `custom_components/heatpump_optimizer/coordinator.py:883 GUARD_OFF`: killed. Replacing the whole gate condition with `if False:` (run by hand on `tests/features.py` at the head, since `tests/mutation_table.py --scope changed` refuses on the ratchet count) fails `a hot-water-dominant window under a space plan folds no flow-bias sample; an all-space window folds one (null)`: 2 of 4606 FEATURE CHECKS FAILED against a green baseline.
- `custom_components/heatpump_optimizer/coordinator.py:883 CMP_BOUND*2`: lives, both mutants. `<=` to `<` on `a.space + a.dhw <= 1e-6` and `>` to `>=` on `dhw_share(a) > _COP_CURVE_SHARE` each left `ALL 4606 FEATURE CHECKS PASSED` (run by hand on `tests/features.py`, mutant applied to a copy of the head). Both bounds are exact-equality edges (a zero-length dwell sum, a share exactly at the curve threshold) that no fixture constructs, and the line they sit on replaces one that carried the same two comparisons, so no behaviour on those edges changed. Carry: pinning needs fixtures at those two equalities; left to `mutation-autofix` and the nightly, which mutate `custom_components/`.

## Red checks

- `mutation` at d480c8cfce87: red by construction on the 2 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

none

## Friction

none
