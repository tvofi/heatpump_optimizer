Design review: revise 429223e1974b9a142fab3cc28d04fb230065ab15 class-open

Group R11-SEAM-learners, note design.md at 429223e197 (revision 1, answering verdict 702ffcc59f at 31ba57ec6c). Second design-review note of three. Code read at origin/main 0ae95e4c9b. Its production hot files are byte-identical to the note's base 9d65fe80b0 (`git diff --stat 9d65fe80b0 0ae95e4c9b` touches only `tests/features.py` and `tests/structure_budgets.json`, class_excess_loc down), so every base anchor holds at main. Full re-read, for a named reason: the delta rewrites most of the note (271+/170- on a 227-line file).

## Revise point

1. class-open: `coordinator.py:936` `_fold_flow_lift` is a site of N-confounded-learner (#3760) that the note does not list. §5 says "every reader of the attribution (§3.2, with the two safe ones named)" is covered, but this one is not. At `:979` it reads `meter_of(coord).attribution(coord._commanded_split())`. On an unobserved interval that is the plan split, so `dhw_share(a)` is 0 on an unplanned charge, and `:989` folds `last_supply_c` into `FlowCurveBias`. That learner is persisted (store key `flow_bias`, `store.py:394`). Its own docstring says "a hot-water interval runs the supply at the tank's charge temperature". Fix wanted: add a §3.2 row (space-heat ask with the cycle's unplanned-charge evidence, beside the outdoor ask at `:975`), a §6 failing test (an unobserved space-only cycle with a tank rise does not move `bias_k`; with no rise, or with a planned charge, it does) and its mutation target. Or give a reason, citing the code, why the site is safe. The smallest approvable shape is this one row, its test and its target. Nothing else in the note needs to change.

## Prior revise points (verdict 702ffcc59f), each checked against the tree

- 1 (class-open, `_fold_measured_cop` and the `:9998` gate): resolved. §3.2 has rows for `_fold_measured_cop` (`:5290`, ask at `:5308`), the draw-range gate (`:9998`), `_interval_measured_heat_kw` (`:1000`, the lower-floor instance) and `_interval_space_power` (`:4994`, read at `:5014`). The two "safe" claims are true: `bridges_hot_water` (`heat_energy.py:530-540`) returns `ran_hot_water`, which is `a.observed and a.dhw > 0.0` (`:262`), and `cop_duty` is reached only past `mode_observed` (`coordinator.py:5278-5279`).
- 2 (class-open, P5 `step[cop]` and `step[outdoor_temp]`): resolved. Both are priced through `_told_path_error` (`sysid.py:966`) and `_slab_ua_told_halfwidth` (`:1132`) the way the slab pair is, and `_declared_night_halfwidth` (`:1218-1222`) reads the same told function. The two widths are routed `decision: owner`, as for `SLAB_PAIR_PRIOR_LOG_SD` (`:589`).
- 3 (architecture-unsound, what crosses each boundary): resolved. §3.1's table matches `dhw_learning.py:166`, its binding at `coordinator.py:3765`, `draw_range.fold` (`:665`, `frozen: bool`) and `_settle_defrost` (`:9931`). The `power_frozen` split (`:9993`) stays one read for window, idle and the `:10080` defrost gate. It adds a ceiling ask and a delivered-ratio ask.
- 4 (architecture-unsound, the per-hour count): resolved by dropping it. §3.4 deletes the ridge term at `:9431` and adds no attribute and no store key. The extracted signature of design/R11-ARCH-fabric-learner fits as written.
- 7 (architecture-unsound, two definitions of the running floor): resolved. "The floor in force: its learned floor where set, else the configured minimum" is `draw_range.floor_in_force_kw` (`draw_range.py:589`), which #3714 has already merged. See note 9b3d1e10.
- 5 (harness, D12 null arm): resolved. The plan-no-DHW conjunct is `space_heat_kw`'s rule (`heat_energy.py:252`). Re-run here, the `--plan-only` arm reads `space_spans_folded=2`, `inflated_space_spans=0` and `cop_records=4`, matching the note's acceptance figures.
- 6 (harness, carry 3): resolved. §3.5 designs against `dev/audit/harnesses/cop_dither_fabric.py`. Re-run here, the dither rows read 578 and 646 against 671 on `null_dither0_*`, with `house_scale=1.1000` throughout, exactly the note's figures. The added refusal-code row is a stated instrument gap.
- Routed decision (carry 2, c25b53cc): carried as `decision: owner` (§7). The note's two-owner stop agrees with the approved design/R11-OUTSIDE-SELF-SETTING-PUMP option table (c1: "L, two owners (planner and learner)"). The owner ruling of 2026-11-18 (`dev/programme/RULINGS.md`) re-homes the carry to this group but does not settle which seam moves the plan's ask. Still owed to the owner.

## Checked and holding

- The nine reasons: `_learning_frozen` (`coordinator.py:6850-6929`) has six branches and `_tail_freeze` (`:3460-3475`) has three.
- `_track_curve_comfort` away test at `:9222`; the occupancy and comfort sites at `:9394`, `:10958` and `dhw_learning.py:441` / `:494`.
- sysid anchors `:811-817`, `:995-999`, `:1019-1022`, `:1040-1045`, `:1155`, `:1291`, `:1458`, `:1776-1796`, `:2389` (holds `rooms`) and `:2475`.
- Budgets at main: `coordinator_attrs` 136 and `seam_cut_total` 415, both at cap. The note adds no attribute and puts the seam measurement on the fixer (item 5e1a0c05).
- Re-runs at main: `m5_crosscov.py` cells 0.5401-0.5687, and 0.7298-0.8017 with `--perturb-ridge0`; `scale_bias_nogain_mean` +0.0201 / +0.0186, as the note states.
- The class enumerator (`sweep_N_confounded_learner.py`) and `probe_N_unobserved_dhw.py` are on no ref and in no local directory, so the class was grepped by hand (§5's commands plus every `_commanded_split()` and `attribution(` reader). `:1105` (slab state estimate), `:1146`/`:1184` (span gate and close, `heat_energy`-owned and covered), `:1292` (diagnostics) and `:10316` (energy totals) are not learner ingests. See note 9b3d1e14.

## Compatibility with design/R11-ARCH-fabric-learner (221c246ece, approved)

The two designs do not contradict each other at the shared seam.
- Fabric extracts `fold_internal_gains(profile or None, parameters, start, residual, hours) -> profile`. This note changes only the step expression inside it and adds no argument, attribute or store key.
- Fabric's invariant "the freeze answer is asked by the coordinator before a fold is called, wherever ADR-008 puts the predicate" is this note's §3.1. Fabric keeps the class-side gates of `_fold_internal_gains`, which is where the occupancy ask belongs (note 9b3d1e11).
- The two new modules are distinct: the freeze module imports `const` only, and `fabric_learning.py` imports `const` and `thermal_model`.
- The only effect on fabric is mechanical. Its exact-text arm stops at `coordinator.py:9431` (already carried, item 9b3d1e01), and its mutation target "ridge" in the gains fold no longer exists once this group lands (item 9b3d1e12).

## Hot-file order

- #3737 (R11-CARRY-DRAWMAP) edits three of this note's sites: `_fold_measured_cop` (`coordinator.py:5312`, the experiment refusal and `owed_scale(read=)`), `accuracy.py:1280` next to `scale_response`, and `draw_range.fold` (`:690`, `draw.map.commit_runs(keep=not (frozen or distorted))`). §7 does not name it. The `frozen=` companion ask this note adds at `:9998` will also drop map runs under #3737. That is consistent, but it is behaviour, so it needs a test (item 9b3d1e13).
- #3812 adds `_plan_let_go` above `_tail_freeze` (`:3451`), which is adjacent text only.
- #3711, #3728 and #3738 touch none of this group's sites.

## Notes for the fixer

- Read the floor in force through `draw_range.floor_in_force_kw` (`draw_range.py:589`), merged by #3714. §3.2's fallback to `power_floor_kw` no longer applies at main. Carry: R11-SEAM-learners (item 9b3d1e10)
- Put the occupancy ask with the class-side gates at the top of `_fold_internal_gains`, never between `y` and the step: fabric extracts the arithmetic and keeps the gates. Carry: R11-SEAM-learners (item 9b3d1e11)
- Once this group deletes the ridge, fabric's mutation target "ridge" in the gains fold goes away. Re-list its gains-fold targets as clip, hour and the unridged step. Carry: R11-ARCH-fabric-learner (item 9b3d1e12)
- Fork after #3737 merges, or rebase onto it: `_fold_measured_cop`, `draw_range.fold` and the `accuracy.py` neighbourhood move. Add one test that an unplanned-charge interval, refused at `:9998`'s `frozen=`, commits no map run. Carry: R11-SEAM-learners (item 9b3d1e13)
- `coordinator.py:10316` books `_energy_totals` space and DHW energy by the plan split on an unobserved interval, so an unplanned charge books as space. That is a statistic, not a learner ingest. Either read the same evidence or state why not in the PR body. Carry: R11-SEAM-learners (item 9b3d1e14)
- `ceiling_frozen` must drop the experiment sample. It must not fall through to `draw.observe`: `fold`'s docstring promises no experiment draw reaches the window. Test that a ceiling-frozen experiment interval folds into neither store. Carry: R11-SEAM-learners (item 9b3d1e15)
- The delivered-ratio ask inside `_settle_defrost` must keep #944's exemption (the caller admits "defrosting" at `coordinator.py:10080`). Test that a defrosting inference interval still folds. Carry: R11-SEAM-learners (item 9b3d1e16)
- `INTERNAL_GAINS_RIDGE` (`const.py:1214`) is read by `dev/audit/harnesses/r10_night_folds_alternatives.py` and `dev/audit/rounds/round10/study-ident/eta_rolling.py`. Deleting the constant breaks the second harness, and keeping it unread may trip `tests/structure.py`'s `const.py` symbol check. Settle this in the PR. Also rewrite `_fold_internal_gains`'s docstring ("the ridge term keeps every hour tethered"). Carry: R11-SEAM-learners (item 9b3d1e17)
- On this seat (macOS, venv-ci) the D12 finding arm reads `inflated_spans_folded=2`, `space_spans_folded=3` and `cop_records=4`, against the note's 1, 2 and 3 (Linux). `--plan-only` reads `spans_plan_dhw_share=4` against 2. The plan solve differs by platform, so record both ends on one platform and state acceptance as "-> 0" and "equal at both ends", never as the literal counts. Carry: R11-SEAM-learners (item 9b3d1e18)
- `HeatEnergyMeter.observe_cycle` gains the tank reading. Its one caller is `coordinator.py:1129`; grep `tests/` for direct calls before changing the signature. Carry: R11-SEAM-learners (item 9b3d1e19)
