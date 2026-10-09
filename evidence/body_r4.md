A live v6.7.17 install never produced a COP sample. It has a 14 kW nameplate maximum, and its pump draws 1.9-2.55 kW. The duty floor was `max(0.3 x max_electrical_power, 0.2)` = 4.2 kW, above every draw, so the observed-COP sensor stayed unavailable and the flow-lift fold was starved too. All numbers below are synthetic. This is the round-4 body, a minimal re-cut (`fixer.md`): only the headings, the arms that fire, and figures re-taken in this pass.

**Stacked on #2065 (7a): this PR merges after #2065.** The branch contains #2065's head `325960ef6`, and its diff over that head is this fix.

**The fix**, decided under tvofi's mandate and the #201 decisions:

1. **Floor.** `ThermalParameters.flow_lift_power_floor_kw` is `max(0.8 x min_electrical_power, 0.2)`, or the nameplate third (`nameplate_power_floor_kw`) when no modulation floor is configured. It always applies, to both the COP fold (`MeasuredCop.judge_floor`) and the flow-lift fold.
2. **Departure from the ask** (`MeasuredCop.judge_ratio`). An interval whose metered draw departs from the plan's ask by more than `COP_ASK_TOLERANCE` (0.15) is judged on #2065's running-draw evidence, `draw_range.follows_ask`:
   - **Evidence that the draw follows the ask** (the log-log slope of drawn on asked is at least 0.5): it folds, as an efficiency shift.
   - **Evidence that it does not:** it is refused as `draw_off_ask`, a pump that sets its own power.
   - **No evidence yet** (fewer than `MIN_SAMPLES` = 48 running samples asked at or above the floor, or asks that never vary by 15 %): it folds only where base would have, with the ask and the draw both clearing the nameplate third. Otherwise it is refused as `awaiting_draw_evidence`.

   So no install folds a departure that base refused before the evidence exists, and an install whose asks never vary keeps base's reach for its departures (round 3's blocker, probe 7).
3. **Refusal reason.** `MeasuredCop.refusal` holds an `accuracy.COP_REFUSED_*` code. The `cop_learner` diagnostics row (`last_refusal`, `measured_cop`, `power_floor_kw`, `draw_follows_ask`) is registered in #2065's `diagnostics._VIEWS`. The dump is available whether or not the sensor is.
4. **Persistence.** The measured COP, its curve and the tank temperature persist under `thermal_learning/measured_cop/*` (declared in `store.DOMAINS`, store version 1). The draw evidence is #2065's `draw/samples` in the accuracy store, so it persists across a restart too.

**Corrections to earlier bodies.**
- Round 3 said the evidence wait is "one day". It is 48 running samples asked at or above the floor, whose asks span at least 15 %. At the default half-hour cadence that is at least 24 hours of such running. An install whose asks never span 15 % never gets the evidence at all, and with this round it learns departures as base did.
- The `judge_ratio` docstring no longer claims that no error is beyond reach.

**Behaviour change, disclosed.** A fixed-speed pump (min = max) gets a higher floor wherever `min > 0.375 x max`: 50 % and 70 % duty-averaged intervals are refused, and 85 % folds at both ends.

## Head

`9d77a97b1edc5ea02b808ab4cee0f4c630f119b3` merges the authored code head `42920d3c56a511a1f7e02d094dc2abc377cd05d0` and then merges origin/main `bd59a4af1` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`2876e01cef49acf81524dcf637962b912fe1c633` merges the authored code head `42920d3c56a511a1f7e02d094dc2abc377cd05d0` and then merges origin/main `bd59a4af1` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`42920d3c56a511a1f7e02d094dc2abc377cd05d0` (code head). Its parents include #2065's head `325960ef6` and origin/main `bd59a4af1`. The base column below is #2065's head; the head column is this commit.

## Mutation proof

Each mutant is applied in its own worktree at `2808a8a94` (production identical to the head). It runs against the filtered `features.py` block "COP learner duty floor keys on the modulation floor (live v6.7.17)" (18 checks) and against the harness and probe 7 rows.

- M11, the no-evidence branch made to fold always: `with no draw evidence a departure folds only past the nameplate third: it waits for evidence on 14 kW and folds on 4 kW, as base` and the off-ask check fail. Harness `selfset_hourly` drops to 0.719.
- M12, the no-evidence branch made to refuse always: the same no-evidence check fails. Probe 7's `narrow_config_true0.75` reads 0/400 at 1.000, round 3's deadlock.
- M13, evidence that the draw does not follow made to fold: `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach` fails. Harness `selfmod_independent_4kw` drops to 0.565.
- These round-3 mutants were not re-run, since their lines are unchanged: M6, M7, M9 and M10 on `follows_ask` and the off-ask return. Nor were the round-2 mutants M1-M5 and M8.

## Null control

#2065's head is the null for every harness and probe row below. The matched-draw control is 96/96 at 1.000 at the head (harness) and 400/400 at 1.000 (probe 6).

## Figures

**Reviewer probes, re-run from `hpo-seats/review-2066/ev3` at #2065's head and at this head.** Base -> head, as folded/intervals and scale:

- **Probe 5** (a self-set 2.2 kW draw; drives only the learner):
  - `hourly_steps`: 0/96 1.000 -> 7/96 0.978
  - `three_hour_steps`: 0/96 1.000 -> 0/96 1.000
  - `flat_day`: 0/96 1.000 -> 0/96 1.000
- **Probe 7:**
  - `narrow_config_true0.75`: 398/400 0.751 -> 398/400 0.751
  - `wide_config_steady_week_true0.75`: 399/400 0.750 -> 399/400 0.750
  - `wide_config_varied_true0.75`: 345/400 0.750 -> 397/400 0.749
- **Probe 6:**
  - `matched`: 356/400 -> 400/400, at 1.000
  - `heat_led_0.7_noise20`: 355/400 0.706 -> 391/400 0.705
  - `heat_led_0.7_lag1`: 259/400 0.686 -> 288/400 0.688
  - `selfset_hourly`: 231/400 1.600 -> 70/400 1.170
  - `partial_b0.3`: 317/400 1.600 -> 152/400 1.375
  - `heat_led_0.7_narrow_ask`: 397/400 0.700 -> 397/400 0.700

**The fixer's own harness** (not the finder's): `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py` (sha1 `9587bead80b5f4b103c510a9f46a4c70e3ea2a91`), base -> head:

- `min1_running_folded`: 0/15 -> 15/15
- `selfmod_matched`: 0/96 -> 96/96, at 1.000
- `selfmod_independent`: 1.000 -> 0.976
- `selfmod_independent_4kw`: 62/96 0.636 -> 33/96 0.780. The orchestrator's acceptance asked for 0.81 or above, the reviewer's prototype figure. This head reads 0.780: better than base, below the prototype. The four variants I tried read 0.758 or 0.780, so I do not know what the prototype did differently.
- `true_0.7` (14 kW): 0/288 -> 241/288 0.704
- `true_0.7_4kw`: 285/288 0.704 -> 285/288 0.704
- `true_0.7_reload150`: 241/288 0.704
- `p4_follow_noise10`: 96/96 1.028 at both ends
- `p4_follow_noise20`: 95/96 1.118 -> 96/96 1.123
- `p4_follow_lag1tick`: 50/96 0.998 -> 37/96 1.002
- `fixed3_duty50` and `fixed3_duty70`: 5/5 -> 0/5; `fixed3_duty85`: 5/5 at both ends
- `min3_running_folded`: 0/15 -> 3/15, carried to 7b

**Gates.**
- `python3 tests/structure.py` passes, with no raise in this PR.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 325960ef672e` predicts no closures or fast red, with 44 unpinned sites over #2065's head. Against the main merge base it lists 86, 42 of them #2065's; all are listed below.
- `node tools/policy/brief_lint.mjs` reads both carry files with 0 errors.
- Heavy scripts are left to CI. This pass ran only the filtered test block, the harness, the three probes, `structure`, `layout` and the predictor.

## Red checks

- `fast (3.14)`, red at round 1 (`d65c68c96`): `tests/layout.py` refused #2066's harness at the retired `tools/audit/harnesses/` path. The harness has been at `dev/audit/harnesses/` since round 2. At this head `python3 tests/layout.py` still refuses one path: #2065's `tools/audit/harnesses/draw_range_evidence.py`, inherited through the stack, which #2065 owes the move for, so `fast (3.14)` will stay red here until #2065 moves it. The cheaper detector is `tests/layout.py` itself, a seconds-long script; its standing cost is one run before every push that adds a path, and `prepr.sh` does not run it today.
- `mutation`: `MUTATION TABLE REFUSED` on unpinned sites. These are answered below, and `mutation-autofix` owns the pins.
- `nightly-status`: this reports main's last scheduled run, not this diff.

## Forward-carry

- `dev/programme/carries/carry-2066.json`: to fix 3 (live learners), hold-then-replay. A departure seen before the evidence is held, then folded or dropped once `follows_ask` decides. The control is probe 6 `selfset_hourly` (1.170 here, right value 1.000) and the harness row `selfmod_independent_4kw` (0.780 here). The nulls are `selfmod_matched` and `true_0.7_4kw`.
- `dev/programme/carries/carry-2065.json`: to 7b, capping the floor at the observed running draw. The control is `min3_running_folded`.

## Unpinned sites

The sites `tools/pr/ci_predict.py` lists, by key. "Value check" names the `features.py` check the mutant fails; the rest are left to `mutation-autofix`.

**This diff's, over #2065's head:**

- `custom_components/heatpump_optimizer/accuracy.py:648 CONST`: value check `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach`.
- `custom_components/heatpump_optimizer/accuracy.py:678 CLAMP_DROP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:678 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:678 GUARD_OFF`: value check `idle and standby draws under the modulation floor still teach nothing`.
- `custom_components/heatpump_optimizer/accuracy.py:680 RETURN_DEL`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:701 CLAMP_DROP`: `mutation-autofix` (the moved v4.0.5 tracking gate).
- `custom_components/heatpump_optimizer/accuracy.py:701 CMP_BOUND`: `mutation-autofix` (the moved v4.0.5 tracking gate).
- `custom_components/heatpump_optimizer/accuracy.py:701 GUARD_OFF`: `mutation-autofix` (the moved v4.0.5 tracking gate, driven by the v4.0.5 tracking checks).
- `custom_components/heatpump_optimizer/accuracy.py:703 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:703 GUARD_OFF`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:706 GUARD_OFF`: value check `with no draw evidence a departure folds only past the nameplate third: it waits for evidence on 14 kW and folds on 4 kW, as base`.
- `custom_components/heatpump_optimizer/accuracy.py:707 CLAMP_DROP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:707 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:707 GUARD_OFF`: value check `with no draw evidence a departure folds only past the nameplate third: it waits for evidence on 14 kW and folds on 4 kW, as base` (mutants M11, M12).
- `custom_components/heatpump_optimizer/accuracy.py:709 RETURN_DEL`: value check `with no draw evidence a departure folds only past the nameplate third: it waits for evidence on 14 kW and folds on 4 kW, as base`.
- `custom_components/heatpump_optimizer/accuracy.py:710 RETURN_DEL`: value check `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach` (mutant M13).
- `custom_components/heatpump_optimizer/accuracy.py:718 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/accuracy.py:733 BOOLOP`: value check `an unreadable stored COP record loads as no measurement, whole` (mutant M4).
- `custom_components/heatpump_optimizer/accuracy.py:733 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:733 GUARD_OFF`: value check `an unreadable stored COP record loads as no measurement, whole`.
- `custom_components/heatpump_optimizer/accuracy.py:735 BOOLOP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:735 GUARD_OFF`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:737 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/coordinator.py:4459 GUARD_OFF`: value check `idle and standby draws under the modulation floor still teach nothing`.
- `custom_components/heatpump_optimizer/coordinator.py:4509 GUARD_OFF`: value check `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach`.
- `custom_components/heatpump_optimizer/coordinator.py:4515 RETURN_DEL`: value check `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach`.
- `custom_components/heatpump_optimizer/coordinator.py:6573 RETURN_DEL`: `mutation-autofix`. This is the existing `return None` after "No published prices cover the planning horizon", which this diff does not touch; the predictor lists it because the lines above it moved..
- `custom_components/heatpump_optimizer/draw_range.py:67 CONST`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not`.
- `custom_components/heatpump_optimizer/draw_range.py:72 CONST`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:207 GUARD_OFF`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not`.
- `custom_components/heatpump_optimizer/draw_range.py:211 BOOLOP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:211 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:213 CMP_BOUND`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not` (47 samples give None, 48 give True).
- `custom_components/heatpump_optimizer/draw_range.py:213 GUARD_OFF`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not` (mutant M10).
- `custom_components/heatpump_optimizer/draw_range.py:216 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/draw_range.py:216 GUARD_OFF`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not` (mutant M9).
- `custom_components/heatpump_optimizer/draw_range.py:221 CMP_BOUND`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not`.
- `custom_components/heatpump_optimizer/draw_range.py:221 RETURN_DEL`: value check `follows_ask: no evidence without the window, before MIN_SAMPLES, or on a flat ask; a proportional draw follows, a self-set one does not`.
- `custom_components/heatpump_optimizer/thermal_model.py:669 CMP_BOUND`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:669 GUARD_OFF`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:670 CLAMP_DROP`: value check `the duty floor is 0.8 x the modulation floor, never below 0.2 kW` (min 0.1 gives 0.2).
- `custom_components/heatpump_optimizer/thermal_model.py:671 RETURN_DEL`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:681 CLAMP_DROP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:681 RETURN_DEL`: value check `with no modulation floor configured the nameplate floor still applies` (4.2 kW).

**#2065's, which the predictor lists against the main merge base because this branch contains #2065:**

- `custom_components/heatpump_optimizer/coordinator.py:9745 GUARD_OFF`: #2065's, inherited through the stack; disposed in #2065's own body.
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
- `custom_components/heatpump_optimizer/thermal_model.py:1280 RETURN_DEL`: #2065's, inherited through the stack; disposed in #2065's own body.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

