A live v6.7.17 install never produced a COP sample. It has a 14 kW nameplate maximum, and its pump really draws 1.9-2.55 kW. The COP learner's duty floor was `max(0.3 x max_electrical_power, 0.2)` = 4.2 kW, above every draw. So `cop_samples` stayed 0, the observed-COP sensor stayed unavailable, and HA hid its `waiting_for`. The flow-lift fold reads the same floor, so it was starved too. All numbers below are synthetic; the user's diagnostics file was not used.

The fix was decided under tvofi's mandate 5951564627 and follows the live-fix design note (out of tree; sections 1 S5, 3, 4 and 5). Round 1 was blocked, and this is the round-2 body, re-taken whole.

1. **Floor.** `ThermalParameters.flow_lift_power_floor_kw` is now `max(0.8 x min_electrical_power, 0.2)` when a modulation floor is configured. When the floor is 0 ("no floor"), the old nameplate third stands. Both readers, `_fold_measured_cop` and `_fold_flow_lift`, take this property.
2. **Ratio gates** (round 1, blocker 1). Once the floor admits a self-modulating pump, the pump's mismatched intervals fold. The reviewer's probe has the plan asking 1-2 kW while the pump draws 1.9-2.55 kW, and `cop_scale` went from 1.000 to 0.549. `accuracy.MeasuredCop.judge_ratio(ratio, ewma)` takes plain values and owns both ratio gates:
   - the v4.0.5 tracking gate, moved here unchanged;
   - a new `COP_REFUSED_OFF_ASK` refusal: the metered draw departs from the ask by more than `COP_ASK_TOLERANCE` (0.15), while the ratio's walking relative spread exceeds `COP_RATIO_SPREAD_MAX` (0.1).

   The spread term is what keeps v4.0.5's deadlock away. A gate on the ask level alone would never fold a pump whose true efficiency sits more than the tolerance from the current scale. A real efficiency shift moves every interval's ratio alike, so its spread falls and it still folds. A draw that ignores the ask scatters the ratio, so it is refused. There is no `DrawRange` dependency.
3. **Refusal reason.**
   - `MeasuredCop.refusal` holds one of the `accuracy.COP_REFUSED_*` codes. `_fold_measured_cop` returns the code and `_learn_measured_cop` records it.
   - `accuracy.diagnostics_view` writes the `cop_learner` row: `last_refusal`, `measured_cop`, `power_floor_kw` and `ratio_spread`. `power_floor_kw` was `duty_floor_kw`; round 1 renamed it, because the optimizer's `duty_floor_kw` is a different quantity.
   - The row is registered in a per-module view loop in `diagnostics.py` and read through a public `measured_cop` view. The diagnostics dump is available whether or not the sensor is.
4. **Persistence.** The measured COP, its curve and the tank temperature persist under `thermal_learning/measured_cop/*`. The keys are declared in `store.DOMAINS`, and every store stays at version 1. An unreadable record loads as no measurement, as a whole.

**Behaviour change on fixed-speed pumps (disclosed).** The floor rises over the base wherever `0.8 x min > 0.3 x max`, that is `min > 0.375 x max`, and both readers (COP and flow-lift) take it. A fixed-speed pump (min = max = 3 kW) whose plan and meter both average part duty now refuses intervals under 2.4 kW. At 50 % and 70 % duty the base folded those, and with a duty-average meter the head does not; at 85 % duty both fold. Round 1's reviewer measured an instantaneous-metered variant that the base folded down to `cop_scale` 0.834/0.827, a sub-floor duty average read as efficiency. The head refuses those intervals, which is the floor's own purpose: to reject part-duty and standby averages.

**Not in this PR.** An overstated modulation floor still refuses a pump that draws less than 0.8 x it: at 3 kW options only the 2.55 kW draw folds. Capping the floor at the observed running draw is the power-clamp seat's 7b, after #2065. It is carried as a precondition with its control row (Forward-carry).

## Head

`24b945f0a18d3e8e7bde2cd14325c1f633e26554` (code head). It merges origin/main `bd59a4af1b2616a7f00761a3769d22a335e4df7c` into the round-2 commits `e118dbe1c` (the gates, the rename, the moved harness, the carry) and `fbc9400a9` (the closures entry). The merge from main brought governance documents only, with no production file. The test block, the mutation proof and the harness head column were run on this tree. The harness base column is merge base `4dbe5aace7440d0a7d43a249892fc63da890338c`, whose production tree equals `bd59a4af1`'s.

## Mutation proof

Each mutant deletes or weakens one production line, in its own worktree at `e118dbe1c` (production identical to the head). The test block is the `features.py` section "COP learner duty floor keys on the modulation floor (live v6.7.17)", run as an extracted runner over the same block, 16 checks. Failing checks per mutant:

- M1, the min-keyed branch in `thermal_model.py` deleted: 7 of 16 fail. They include `a 14 kW nameplate pump drawing 1.9-2.55 kW teaches the COP learner`, `the duty floor is 0.8 x the modulation floor, never below 0.2 kW`, and `the flow-lift fold takes the same floor: a 14 kW nameplate at 2.2 kW folds`.
- M2, `self._measured_cop.refusal = ...` reduced to the bare call: 3 fail, including `each guard has its own code: a freeze and a missing reading`.
- M3, the `MeasuredCop.from_dict(...)` load line deleted: `the last measured COP and its curve are restored on restart`.
- M4, `(dhw and temp is None)` dropped from `from_dict`: `an unreadable stored COP record loads as no measurement, whole`.
- M5, the `cop_learner` diagnostics row deleted: `a refused COP interval names its guard and the floor in the diagnostics` and `a folded COP interval clears the refusal`.
- M6, the off-ask return deleted: `a draw that ignores the ask is refused as off-ask; a matched draw and a consistent 0.7 shift still teach`. On the harness the probe returns to `selfmod_independent=66/96_scale=0.549`.
- M7, the spread term dropped, a gate on the ask level alone: the same check fails, and the harness shows the deadlock, `true_0.7=0/288_scale=1.000`.
- M8, the key renamed back to `duty_floor_kw`: `a refused COP interval names its guard and the floor in the diagnostics`.

## Null control

- The same test block at merge base `4dbe5aace` fails 14 of 16. The two that pass are `idle and standby draws under the modulation floor still teach nothing` and `with no modulation floor configured the nameplate floor still applies`. Both are behaviour the fix keeps.
- The matched-draw control `selfmod_matched` reads 96/96 at scale 1.000 at the head. A correctly sized 4 kW pump with a real 0.7 efficiency shift (`true_0.7_4kw`) learns 0.704 at both ends, so the off-ask gate does not cost the base its reach.
- `liveness_folded` reads 3/3 at both ends: a 4 kW nameplate whose old 1.2 kW floor admitted 2.2 kW. So a zero at the base is the floor, not a learner that cannot fold.

## Figures

Every row below comes from `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py` (sha1 `b7794b439965086051cf978594dbeb07d52607fb`), run from a worktree root at merge base `4dbe5aace` and at the head. Each row reads as base -> head, "folded/intervals" and the learned scale. **The harness is the fixer's own instrument, not the finder's:** the live-install finding committed no harness. Its `selfmod_*` rows reproduce round 1's reviewer probe 3 (the reviewer's out-of-tree probe script) as a control.

- `duty_floor_kw`: 4.200 -> 0.800 (14 kW max, 1.0 kW min).
- `min1_running_folded` (1.0, 1.2, 1.9, 2.2, 2.55 kW, drawn as asked): 0/15 -> 15/15.
- `min1_idle_folded` 0/9, `min1_standby_folded` 0/9 (0.2-0.5 kW, at or under `on_threshold_kw` 0.5) and `min1_duty_cycled_folded` 0/6: 0 at both ends. The same holds for the min3 rows.
- `min3_running_folded`: 0/15 -> 3/15. This is the overstated-floor gap carried to 7b.
- `selfmod_independent` (the reviewer's probe: asked 1.0-2.0 kW, drawn 1.9-2.55 kW, right scale 1.000): 0/96 scale 1.000 -> 9/96 scale 0.976. Round 1's head read 66/96 scale 0.549. On a 4 kW nameplate (`selfmod_independent_4kw`): 62/96 scale 0.636 at the base (the hazard already existed there) -> 9/96 scale 0.976.
- `selfmod_matched` (draw == ask): 0/96 -> 96/96, scale 1.000 at both ends.
- `true_0.6`, `true_0.7`, `true_0.8` and `true_1.3` (a heat-led pump of that true scale, +-5 % meter noise, 288 intervals): 0/288 at the base (the floor) -> 257, 259, 260 and 259 of 288, learning 0.604, 0.704, 0.805 and 1.307.
- `fixed3_duty50` and `fixed3_duty70`: 5/5 -> 0/5. `fixed3_duty85`: 5/5 at both ends.
- The constants were chosen by a sweep on the same intervals: tolerance 0.10/0.15/0.20 x spread 0.05/0.10/0.15. Every cell kept the probe at 0.976-0.995 and learned all four true shifts. 0.15/0.10 is a middle cell, not an edge one. With the spread term removed, a 0.15 ask gate alone deadlocks every true shift (M7). The 0.8 floor constant is the round-0 sweep, the formula on synthetic draw classes: k=0.8 is the smallest k that refuses every standby and 70 %-duty draw while every running draw still folds.
- `python3 tests/structure.py`: the ratchet passes. Re-recorded rows, all improvements with no raise, the reason in the commits: `coordinator_attrs` 153 -> 151, `coordinator_multiassigned_attrs` 120 -> 118, `max_class_loc` 8817 -> 8807, `seam_cut_total` 760 -> 758.
- `python3 tools/audit/archscore/score.py --diff 4dbe5aace7440d0a7d43a249892fc63da890338c`: `dS +0.0246 IMPROVES`.
- Floor readers, from `git grep -n flow_lift_power_floor_kw -- custom_components`: `_fold_flow_lift`, `_fold_measured_cop` and `accuracy.diagnostics_view`, the last of which only reports it.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 4dbe5aace7440d0a7d43a249892fc63da890338c`: no closures or fast red predicted, and 22 unpinned sites, listed below.
- Heavy scripts are left to CI at the owner's instruction. These cheap checks ran locally at the head and passed: `layout`, `structure`, `typing_ruler`, `finite_boundary`, `debug_collect`, `brief_lint` on the new carry file, and the test block. The round-1 local runs of `features`, `entities`, `guard_pins`, `doc_claims` and `validate` were not repeated; CI runs them.

## Red checks

- `fast (3.14)`, round 1 at `d65c68c96`: `tests/layout.py` refused the harness at the retired `tools/audit/harnesses/` path (it lives at `dev/audit/harnesses/` since #2015). The harness has moved; `python3 tests/layout.py` reads rc 0 at the head and rc 0 at the merge base. **Cheaper detector:** `tests/layout.py` itself, a seconds-long script that my local cheap list did not include. The standing cost is running it before every push that adds a path, which `prepr.sh` does not do today. No new countermeasure is built here: the detector already exists, and this was my omission, not a gap in it.
- `mutation`, round 1: `MUTATION TABLE REFUSED`, unpinned sites added by this diff. These are answered under Unpinned sites, and `mutation-autofix` owns the pins (`ci-autofix.md`).
- `nightly-status`: this reports main's last scheduled run, not this diff.

## Forward-carry

`dev/programme/carries/carry-2065.json` carries to stage live-7b, the power-clamp seat's observed-draw consumer after #2065. It states a precondition: the floor both readers take is capped by the observed running draw, never below `on_threshold_kw`. Its control is the harness row `min3_running_folded` (3/15 at this head) with the min3 idle, standby and duty-cycled rows as nulls. `brief_lint.mjs` reads it with 0 errors. Round 1's blocker 1 is closed in this diff rather than carried. The refusal codes a later learner fix adds extend `accuracy.COP_REFUSED_*`, as the list's own comment says. Not touched: `_fold_capacity_envelope` learns only at >= 0.95 x nameplate, so an overstated maximum still starves the envelope; the design note records the envelope as out of S3's scope.

## Unpinned sites

Each site `tools/pr/ci_predict.py` lists, by key, with its disposition. "Value check" names the `features.py` check its mutant fails; the rest are left to `mutation-autofix`, which pins a killed mutant (`ci-autofix.md`).

- `custom_components/heatpump_optimizer/accuracy.py:639 CONST`: value check `a draw that ignores the ask is refused as off-ask; a matched draw and a consistent 0.7 shift still teach`.
- `custom_components/heatpump_optimizer/accuracy.py:644 CONST`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:688 CLAMP_DROP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:690 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:690 GUARD_OFF`: `mutation-autofix` (the moved v4.0.5 tracking gate, which the existing v4.0.5 tracking checks drive).
- `custom_components/heatpump_optimizer/accuracy.py:692 BOOLOP`: value check, mutant M7.
- `custom_components/heatpump_optimizer/accuracy.py:692 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:692 GUARD_OFF`: value check, mutant M6.
- `custom_components/heatpump_optimizer/accuracy.py:694 RETURN_DEL`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:702 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/accuracy.py:717 BOOLOP`: value check, mutant M4.
- `custom_components/heatpump_optimizer/accuracy.py:717 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:717 GUARD_OFF`: value check `an unreadable stored COP record loads as no measurement, whole`.
- `custom_components/heatpump_optimizer/accuracy.py:719 BOOLOP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:719 GUARD_OFF`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:721 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/coordinator.py:4509 GUARD_OFF`: value check, the off-ask check (the refusal return the guard selects).
- `custom_components/heatpump_optimizer/coordinator.py:4515 RETURN_DEL`: value check, the off-ask check.
- `custom_components/heatpump_optimizer/coordinator.py:6573 RETURN_DEL`: `mutation-autofix`. This is the existing `return None` after "No published prices cover the planning horizon", which this diff does not touch; the predictor lists it because the lines above it moved.
- `custom_components/heatpump_optimizer/thermal_model.py:667 CMP_BOUND`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:667 GUARD_OFF`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:668 CLAMP_DROP`: value check `the duty floor is 0.8 x the modulation floor, never below 0.2 kW` (min 0.1 gives 0.2).

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
