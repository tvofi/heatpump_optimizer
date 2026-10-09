A live v6.7.17 install never produced a COP sample. It has a 14 kW nameplate maximum, and its pump really draws 1.9-2.55 kW. The COP learner's duty floor was `max(0.3 x max_electrical_power, 0.2)` = 4.2 kW, above every draw. So `cop_samples` stayed 0 and the observed-COP sensor stayed unavailable. The flow-lift fold reads the same floor, so it was starved too. All numbers below are synthetic. This is the round-3 body, re-taken whole.

**Stacked on #2065 (7a): this PR merges after #2065.** Its branch contains #2065's head `325960ef6`, and its diff over that head is this fix. The stack follows the #201 decision taken on round 2's remedy (a).

1. **Floor.** `ThermalParameters.flow_lift_power_floor_kw` is `max(0.8 x min_electrical_power, 0.2)` when a modulation floor is configured; with no floor (0) the nameplate third stands. Both readers, `_fold_measured_cop` and `_fold_flow_lift`, take it.
2. **Off-ask refusal** (rounds 1-2). Once the floor admits a pump that sets its own power, its intervals fold as a COP shortfall.
   - `accuracy.MeasuredCop.judge_ratio(ratio, ewma, draw)` refuses an interval with `COP_REFUSED_OFF_ASK` when the metered draw departs from the ask by more than `COP_ASK_TOLERANCE` (0.15), unless `draw_range.follows_ask(draw)` says the draw follows the ask.
   - `follows_ask` reads #2065's running-draw window. It returns `None` (no evidence) until `MIN_SAMPLES` running samples asked at or above the floor exist and their asks span `FOLLOW_ASK_SPAN` (1.15). After that it returns whether the slope of log drawn on log asked reaches `FOLLOW_SLOPE_MIN` (0.5).
   - A draw proportional to its ask has slope 1, and an efficiency shift scales every draw alike, so the shift still folds. A self-set draw has slope 0 whatever its level. A flat ask is no evidence either way, so departures stay refused.
   - Round 2's ratio-spread statistic is removed: the concept has one owner, `draw_range`. The core caller hands the window in (`_learn_measured_cop(self._accuracy.draw)`), so no seam is crossed.
   - **The evidence persists across a restart.** It is #2065's `draw/samples` in the accuracy store. The harness row `true_0.7_reload150` round-trips it through its store form mid-run and folds the same count as the run without the reload.
3. **Refusal reason.** `MeasuredCop.refusal` holds an `accuracy.COP_REFUSED_*` code. `accuracy.diagnostics_view` writes the `cop_learner` row (`last_refusal`, `measured_cop`, `power_floor_kw`), registered in #2065's `diagnostics._VIEWS`. The diagnostics dump is available whether or not the sensor is.
4. **Persistence.** The measured COP, its curve and the tank temperature persist under `thermal_learning/measured_cop/*`, declared in `store.DOMAINS`, at store version 1. An unreadable record loads as no measurement, as a whole.

**Behaviour changes (disclosed).**
- **Fixed-speed pumps.** The floor rises over the base where `min > 0.375 x max`, for both readers. A fixed-speed 3 kW pump whose plan and meter both average part duty refuses 50 % and 70 % duty intervals (it folds them at the base) and folds 85 % at both ends.
- **Evidence wait.** A departure beyond 15 % now waits for `follows_ask`'s evidence, one day of running at the default cadence. It waits once per configuration, not per restart.
- **Noise and lag.** A ±20 % noisy or a lagging meter loses some folds; see Figures.

**Not in this PR.** An overstated modulation floor still refuses a pump drawing under 0.8 x it. That is carried to 7b in `dev/programme/carries/carry-2065.json`.

## Head

`cdf37977ad17994fc5d1b30033433096338ccdff` (code head). Its parents are #2065's head `325960ef6` (merged in at `7b4bc7dfc`) and origin/main `bd59a4af1`. Measured on this tree: the test block, the mutation proof, the harness head column and the predictor. The harness base column is #2065's head, the base this diff stacks on.

## Mutation proof

Each mutant deletes or weakens one production line, in its own worktree at `c1f6b73c3` (production identical to the head). It runs against the `features.py` section "COP learner duty floor keys on the modulation floor (live v6.7.17)", filtered and run alone (17 checks), and against the harness's probe rows. Failing checks and harness rows per mutant:

- M1, the min-keyed floor branch deleted: `a 14 kW nameplate pump drawing 1.9-2.55 kW teaches the COP learner`, `the duty floor is 0.8 x the modulation floor, never below 0.2 kW`, `the flow-lift fold takes the same floor: a 14 kW nameplate at 2.2 kW folds` and 4 more (round-2 run; the floor line is unchanged since).
- M6, the off-ask return deleted: `a draw that ignores the ask (varying or flat) is refused as off-ask; ...`. Harness: `selfset_flat=93/96_scale=0.500`, `selfmod_independent=66/96_scale=0.549`.
- M7, `follows_ask` always True: the same check fails. Harness: `selfset_three_hour=40/96_scale=0.648`.
- M9, the ask-span check deleted: the off-ask check and `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not`. Harness: `selfset_flat=3/96_scale=0.971`.
- M10, `MIN_SAMPLES` lowered to 2: `follows_ask: ...`. It survived the off-ask check alone, which is why the boundary check was added.
- Round 2's M2-M5 and M8 (refusal recording, the load line, the whole-record drop, the diagnostics row, the key name) touch lines this round did not change. They are not re-run.

## Null control

- The harness at #2065's head (base column) is the null for every row. The matched-draw control `selfmod_matched` is 96/96 at scale 1.000 at the head.
- The test block cannot run at #2065's head, because it imports `MeasuredCop`, which this diff adds. Round 2's run at the main merge base failed 14 of 16 checks, and the two that passed are behaviour the fix keeps.

## Figures

Every row comes from `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py` (sha1 `9587bead80b5f4b103c510a9f46a4c70e3ea2a91`), run at #2065's head `325960ef6` and at this head. Each row reads base -> head, "folded/intervals" and the scale. **The harness is the fixer's own instrument, not the finder's:** the finding committed none. The `selfmod_*`, `selfset_*` and `p4_*` rows reproduce the round-1 and round-2 reviewer probes 3, 5 and 4 as controls. Each interval feeds #2065's running-draw fold before the learner, as the cycle does. The reviewers' own scripts drive only the learner, so at this head their window is empty and every departure is refused for want of evidence.

- **Probe 5, a self-set 2.2 kW draw (right scale 1.000):**
  - `selfset_hourly`: 0/96 1.000 -> 7/96 0.978
  - `selfset_three_hour`: 0/96 1.000 -> 0/96 1.000
  - `selfset_flat`: 0/96 1.000 -> 0/96 1.000

  Round 2's head read 0.927, 0.778 and 0.533 on the same three shapes.
- **Probe 3:** `selfmod_independent` 0/96 1.000 -> 9/96 0.976; `selfmod_independent_4kw` 62/96 0.636 -> 9/96 0.976.
- **Matched control:** `selfmod_matched` 0/96 -> 96/96, scale 1.000 at both ends.
- **Real efficiency change**, closed loop with ±5 % noise:
  - `true_0.6`, `true_0.7`, `true_0.8` and `true_1.3`: 0/288 (the old floor) -> 241/288 each, learning 0.604, 0.704, 0.805 and 1.307.
  - `true_0.7_4kw`: 285/288 0.704 -> 241/288 0.704. The 44 fewer folds are the evidence wait.
  - `true_0.7_reload150`: 241/288 0.704, the same count as without the reload.
- **Probe 4** (6 kW, 1.5 kW floor, asks 2-5 kW, open loop, so its absolute scales are not the truth):
  - `p4_follow_noise10`: 96/96 1.028 -> 96/96 1.028
  - `p4_follow_noise20`: 95/96 1.118 -> 83/96 1.079
  - `p4_follow_lag1tick`: 50/96 0.998 -> 29/96 1.025
  - `p4_eff0.8_noise5`: 96/96 0.563 -> 49/96 0.746
  - `p4_eff0.8_noise10`: 96/96 0.563 -> 57/96 0.712
- **Floor:** `duty_floor_kw` 4.200 -> 0.800. `min1_running_folded` 0/15 -> 15/15. `min3_running_folded` 0/15 -> 3/15 (carried to 7b). Idle, standby and duty-cycled rows are 0 at both ends. `fixed3_duty50`/`70` 5/5 -> 0/5, `fixed3_duty85` 5/5 at both ends. `liveness_folded` 3/3 at both ends.
- `python3 tests/structure.py`: the ratchet passes at the head with no re-record in this round. The rows recorded in earlier commits are improvements with no raise.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 325960ef672e`: no closures or fast red predicted. 32 unpinned sites over #2065's head, and 74 over the main merge base, the difference being #2065's own; all are listed below.
- Heavy scripts are left to CI at the owner's instruction. This round ran locally only the filtered test block, the harness, `structure` and the predictor; a full `features.py` run was started and stopped unfinished.

## Red checks

- `fast (3.14)`, round 1: `tests/layout.py` refused the retired `tools/audit/harnesses/` path. The harness moved to `dev/audit/harnesses/` in round 2. The cheaper detector is `tests/layout.py` itself, a seconds-long script my local list did not include.
- `mutation`: `MUTATION TABLE REFUSED` on unpinned sites. These are answered below, and `mutation-autofix` owns the pins (`ci-autofix.md`).
- `nightly-status`: this reports main's last scheduled run, not this diff.

## Forward-carry

`dev/programme/carries/carry-2065.json` carries to live-7b (the observed-draw consumer after #2065): the floor both readers take must be capped by the observed running draw, never below `on_threshold_kw`. Its control is the harness row `min3_running_folded` (3/15 here) with the min3 idle, standby and duty-cycled rows as nulls. Not touched: `_fold_capacity_envelope` learns only at >= 0.95 x nameplate. The design note records the envelope as out of S3's scope.

## Unpinned sites

The sites `tools/pr/ci_predict.py` lists, by key. "Value check" names the `features.py` check the mutant fails; the rest are left to `mutation-autofix` (`ci-autofix.md`).

**This diff's, over #2065's head:**

- `custom_components/heatpump_optimizer/accuracy.py:647 CONST`: value check `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach`.
- `custom_components/heatpump_optimizer/accuracy.py:685 CLAMP_DROP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:685 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:685 GUARD_OFF`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:687 BOOLOP`: value check, the off-ask check (mutant M6 class).
- `custom_components/heatpump_optimizer/accuracy.py:687 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:687 GUARD_OFF`: value check, the off-ask check (mutant M6).
- `custom_components/heatpump_optimizer/accuracy.py:689 RETURN_DEL`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:697 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/accuracy.py:712 BOOLOP`: value check `an unreadable stored COP record loads as no measurement, whole` (mutant M4).
- `custom_components/heatpump_optimizer/accuracy.py:712 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:712 GUARD_OFF`: value check `an unreadable stored COP record loads as no measurement, whole`.
- `custom_components/heatpump_optimizer/accuracy.py:714 BOOLOP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:714 GUARD_OFF`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:716 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/coordinator.py:4510 GUARD_OFF`: value check, the off-ask check.
- `custom_components/heatpump_optimizer/coordinator.py:4516 RETURN_DEL`: value check, the off-ask check.
- `custom_components/heatpump_optimizer/coordinator.py:6574 RETURN_DEL`: `mutation-autofix`. This is the existing `return None` after "No published prices cover the planning horizon", which this diff does not touch; the predictor lists it because the lines above it moved..
- `custom_components/heatpump_optimizer/draw_range.py:67 CONST`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:72 CONST`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:207 GUARD_OFF`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not`.
- `custom_components/heatpump_optimizer/draw_range.py:211 BOOLOP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:211 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:213 CMP_BOUND`: value check `follows_ask: ...` (47 samples give None, 48 give True).
- `custom_components/heatpump_optimizer/draw_range.py:213 GUARD_OFF`: value check `follows_ask: ...` (mutant M10).
- `custom_components/heatpump_optimizer/draw_range.py:216 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:216 GUARD_OFF`: value check `follows_ask: ...` and the off-ask check (mutant M9).
- `custom_components/heatpump_optimizer/draw_range.py:221 CMP_BOUND`: value check `follows_ask: ...` (a self-set draw gives False).
- `custom_components/heatpump_optimizer/draw_range.py:221 RETURN_DEL`: value check `follows_ask: ...`.
- `custom_components/heatpump_optimizer/thermal_model.py:667 CMP_BOUND`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:667 GUARD_OFF`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:668 CLAMP_DROP`: value check `the duty floor is 0.8 x the modulation floor, never below 0.2 kW` (min 0.1 gives 0.2).

**#2065's, which the predictor lists against the main merge base because this branch contains #2065:**

- `custom_components/heatpump_optimizer/coordinator.py:9746 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:45 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:48 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:51 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:54 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:55 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:58 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:60 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:63 CONST`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:97 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:97 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:101 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:108 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:111 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:112 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:113 CLAMP_DROP`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:113 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:122 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:125 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:127 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:127 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:134 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:139 BOOLOP`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:139 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:139 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:146 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:149 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:151 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:178 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:186 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:186 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:192 BOOLOP`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:192 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:196 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:251 CMP_BOUND`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:296 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:301 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:304 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:305 CLAMP_DROP`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:306 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/draw_range.py:317 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.
- `custom_components/heatpump_optimizer/thermal_model.py:1268 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
