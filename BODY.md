R10-DRAW-MAP-EVIDENCE, part 1 (#3106 item 4). Stacked on R10-COP-LEARNER-DRAW-FLOOR's code handoff (`handoff/r10-cop-learner-draw-floor` at a827c3d985b240fabcc83215e0d35a9692e8fca9, design approved at 94d2c9f06576693b31996d21d18af241d41640b2 of `design/R10-COP-LEARNER-DRAW-FLOOR`): this pull request opens only after that group merges, and its diff is measured against the merge of that tip into main (d7839aee81).

The evidence is one owner diagnostics download, measured out of tree by a separate seat. No row, entity id, timestamp or name from it is in this diff, this body or a commit message: only derived numbers, and synthetic fixtures that reproduce the derived shape.

- **(b) The ask judgement reads the level.** `draw_range.ask_evidence`, the one place the draw-floor design makes the judgement, now returns `ASK_FOLLOWS` only where the slope of log drawn on log asked is at least `FOLLOW_SLOPE_MIN` **and** the fitted ratio of drawn to asked at the asks' 90th percentile and at their 10th are within `DISAGREE_FACTOR` of each other: `(high / low) ** abs(1 - slope) <= DISAGREE_FACTOR`, from the percentiles and slope the function already computed. No new constant: `DISAGREE_FACTOR` is the factor at which the same window already calls one sample a disagreement. The owner's window read slope 0.630 and passed; its level moves by 1.509 across its span and now does not follow.
- **(a) The empty ceiling store: the store is right to refuse, nothing built.** The cause is upstream of the store, in when the experiment runs (the experiment mode, out of this part's scope); carried to part 2.
- **(c) The measurement as a harness**, `dev/audit/harnesses/draw_map_linearity.py`, on a seeded synthetic fixture, with a `--bundle` reader that touches only store and cycle rows.

Not in scope, by the brief: any change to the open-loop map `thermal_model.flow_setpoint_for_level` (the data is closed-loop, the band's middle was never held, one install fits a constant), `diagnostics.py`, and the experiment mode. Part 2 (data collection and an experiment-mode sweep) is designed by another seat.

### (b) Why the level is read across the span, not as one figure

The brief's case is "slope fine, level far above the ask". A bound on the whole window's level (drawn summed over asked within some factor of 1) was measured and refused: the COP learner reads a departure as an efficiency shift on `ASK_FOLLOWS`, and a pump whose true COP scale is 0.6 draws 1/0.6 = 1.67 x every ask, a level the owner's 1.70 cannot be told from. `cop_duty_floor.py`'s `true_0.6` row is that install and learns 0.603 at both ends of this diff (`## Figures`); a whole-window level bound would refuse it every interval (`COP_REFUSED_OFF_ASK`) and its scale would never learn. What separates the two is that an efficiency shift is one ratio at every ask and the owner's draw is not: on the synthetic shape the fitted draw is 2.1 x the ask at the span's low end and 1.4 x at its top. That is the level judgement built.

Downstream, the verdict has three readers (`git grep -n -e ask_evidence -e follows_ask -- custom_components` returns only `draw_range.py` and `accuracy.py`): `MeasuredCop.judge_ratio` (on `ASK_IGNORED` every interval reads `COP_REFUSED_OFF_ASK`, within the tolerance or not), `MeasuredCop.release` (held departures are dropped, not folded), and `accuracy.diagnostics_view` (`draw_follows_ask` False). `judge_ratio` runs only where no heat reading exists (`heat_kw is None` in `_fold_measured_cop`); the owner's install has a thermal power entity, so there the change is the diagnostics field, and a cycle whose heat reading is unavailable. No solve, optimizer or arbiter path reads the verdict, so no cost figure moves at a fixed learned state, flat price or not; the verdict reaches cost only through which intervals train `cop_scale` on an install with no heat reading.

### (a) Why the ceiling store holds 0 samples

`draw_range.fold` sends an interval to the ceiling store only when all of: `is_running_space` (a running draw with no hot water asked), `experiment_s` not `None` (the interval's own action ran the system-identification experiment), and `DrawRange.takes_ceiling` (the ceiling written, the draw above idle). Every other interval goes to the window, where a ceiling-written draw is only overdraw evidence against an existing store (`DrawRange._overdrawn`). Per gate, on the owner's download (rules in `## Figures`):

- experiment gate: 0 of 561 cycle rows ran the experiment (`action_mode` never `system_identification`); the experiment view reads phase idle, no run and no attempt since start. This gate alone drops every interval.
- command gate, on what reached the window: 2 of 116 running samples were written at the ceiling.
- running-space gate: of the replay's steady, running, ceiling-written minutes (24 h), 264 of 405 ran in the pump's combined heating and hot-water mode, the minutes a plan asking hot water drops (a mode proxy; the plan's per-interval split is not in the download).

The experiment is armed only by the **Run System Identification** button (`async_arm_system_identification`, whose one caller is `button.py`), and `sysid.armable` arms the fit, not the probe, while the house learner is unconverged (`house_heat_loss_samples` 21 against `converged_samples` 200 on that install). So the probe never ran. The store refusing ordinary ceiling-written intervals is its documented rule (`docs/how-it-works.md`, "The ceiling probe"; the comment above `CEILING_WINDOW`), and relaxing it would not have filled this store: the week's window held 2 ceiling-written running samples against `CEILING_MIN_SAMPLES` 12. The fix belongs where the cause is, the experiment's arming, which this part may not edit: `## Forward-carry`.

## Head

3533ba12b817b3d10218d5dee27db10933e28ab8, on d7839aee81 (origin/main 5b8f05ba4e merged with a827c3d985). Measured 2026-11-14 19:33 UTC. At that time origin/main is 4058469d79a3b43d840921b82b23f31494ba14b2 and `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so main is not merged in.

## Mutation proof

Failing test first: e6a48c09b0 adds the check "the measured shape (slope 0.70, ...) does not follow its ask" on the base's production files; the block below prints `1 of 18 FEATURES BLOCK FAILED`, the states read `('follows', 'follows', 'follows', 'does_not_follow')`. At the head: `ALL 19 FEATURES BLOCK PASSED`.

The block: `tests/features.py` from the line `` # `follows_ask`'s own thresholds `` to `# MeasuredCop.judge_ratio holds a departure only while`, run by `tools/audit/seat/features_block.py` with the prelude its `--emit-prelude` writes.

- `python3 tools/audit/seat/mutant_run.py --diff d7839aee81...HEAD --cmd '<the block>'`: 4 mutants (`CONST_SWAP`, `RETURN_DEL`, `CMP_BOUND` on the slope bound, `STMT_DEL`), no `SURVIVED` line, rc 0.
- `python3 tools/audit/seat/mutant_run.py --spec <5 mutants> --cmd '<the block>'`, the operators the diff mode does not draw: `SURVIVED NULL`; `KILLED level_bound_exclusive` (`<=` to `<`), `KILLED level_conjunct_dropped`, `KILLED slope_conjunct_dropped`, `KILLED abs_dropped`, `KILLED and_to_or`. The last two were survivors at a64209289d; ad611dde72 adds the check that kills them (a flat draw over asks spanning 1.2 refused by the slope alone, a square-law draw over asks spanning 1.5 by the level alone).

## Null control

- Same asks, one ratio: the synthetic shape's asks drawn at 1.70 x with the same ripple follow; a draw within tolerance of its ask follows; a self-set draw (2.2 kW whatever the ask) does not, on the slope (check in the block).
- Every other ask-evidence fixture of `tests/features.py` reads as at the base: `features_block.py` from `R.section("COP learner duty floor keys` to `R.section("early cut-off`, `ALL 246 FEATURES BLOCK PASSED`; from `R.section("duty-switch restart learning, part A` to `R.section("R10-PROD-RESIDUE-PINS`, `ALL 146 FEATURES BLOCK PASSED`.
- One existing fixture changed: the slope-bound pin used asks 1.0 and 2.0 drawn 1.0 and sqrt(2), whose level moves by 1.41 and now does not follow. It moves to asks 1.0 and 1.5625 drawn 1.0 and 1.25: slope 0.5 and level 1.25, both exact doubles on their bounds, so the one fixture pins both bounds inclusive.
- Harnesses that drive the judgement read identically at base and head: `cop_duty_floor.py`, `draw_range_evidence.py` and `r10_cop_gate_vent.py` (`diff` of the two outputs exits 0 for each). `r10_cop_gate.py` raises `TypeError` at both ends (`cop_observability()` has no `follows` argument): frozen evidence keyed to an earlier signature; the ask arm of the new harness covers what it read.
- The harness's own nulls, synthetic: `ask_null_proportional=follows` beside `ask_evidence=does_not_follow`; shuffled set-points read `store_null_p95=0.045` against `store_r2=0.392`; the planted curvature reads `8/50` at c=0 and `49/50` at c=1.0.

## Figures

<!-- figure-block: scope-line mb=5b8f05ba4e30d248b9b4a1f4c44fd8e62148c5db head=3533ba12b817b3d10218d5dee27db10933e28ab8 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

### (b) the judgement, both ends

- `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_linearity.py` (synthetic), at the head: `RESULT ask_pairs=116 ask_slope=0.620 ask_level_sum=1.873 ask_level_moves=1.488`, `RESULT ask_evidence=does_not_follow`, `RESULT ask_null_proportional=follows`. The same file run on the base's production tree (a `git archive` of d7839aee81): `RESULT ask_evidence=follows`, `RESULT ask_null_proportional=follows`.
- `python3 dev/audit/harnesses/draw_map_linearity.py --bundle <the owner's download, out of tree>`, both ends: `RESULT ask_pairs=115 ask_slope=0.630 ask_level_sum=1.807 ask_level_moves=1.509`; `RESULT ask_evidence=follows` at the base, `RESULT ask_evidence=does_not_follow` at the head; `RESULT ask_null_proportional=follows` at both. The 115 run-asked pairs are the production window's (`DrawRange._run_asked`); the measuring seat's slope 0.70 and level 1.70 were over its 90 heating-set-point rows.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, base and head: identical output, including `true_0.6=282/288_scale=0.603`, `true_0.7=285/288_scale=0.704`, `p4_eff0.8_noise5=96/96_scale=0.634`, `selfmod_independent=5/96_scale=0.987`.
- Both ends of the input range: an empty window and 47 pairs read pending, a full window with no run-asked pair reads unobtainable (draw-floor checks, unchanged); at the bound, slope exactly 0.5 with level exactly 1.25 follows, and `<` on either bound fails the check.

### (a) per-gate counts, owner download

- `python3 dev/audit/harnesses/draw_map_linearity.py --bundle <the owner's download, out of tree>`: `RESULT store_rows_at_ceiling=2` (of `store_rows=116`), `RESULT ceiling_store_rows=0 cycles=561 experiment_cycles=0`.
- The running-space count (264 of 405 ceiling-written steady running minutes in the combined mode) came from an out-of-tree probe over the download's replay, which this harness does not read: the replay is keyed by entity id. Rule: set-point at or above the ceiling less `CEILING_TOLERANCE_K`, draw above `RUNNING_FLOOR_KW`, the run switch on, at least 3 minutes since the last set-point or mode change. No enumerator in the tree; the figure is the probe's.

### (c) the harness, reproducing the measuring seat

`--bundle` on the owner's download prints `RESULT store_gain_kw_per_k=0.0667 store_r2=0.179 store_null_p95=0.047 store_null_p=0.0010`, the measuring seat's store fit (0.0667 kW/K, R2 0.179) to the digits it reported; curvature `13/50`, `25/50`, `46/50` at c = 0, 0.35, 1.0. Synthetic: `map_rms_kw=1.466 map_resid_floor_end_kw=+1.585 map_resid_ceiling_kw=-0.786`, `fit_gain_kw_per_k=0.0472 fit_r2=0.483 fit_null_p95=0.043`, `steps_n=15 step_gain_kw_per_k=0.057 step_null_p97_5=0.032 step_planted_0.27_recovered=0.270`.

### Ratchets

- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`; no budget touched.
- `python3 tools/audit/archscore/score.py --diff d7839aee81`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/pr/ci_predict.py --base d7839aee81` at the head: `no closures, fast, governance or instrument red predicted`; the one INERT READS entry it predicted for the new harness is committed in 3533ba12b8. Three `ADDED UNPINNED` lines for this part's line, under `## Unpinned sites`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`.
- Not run locally (by the dispatch brief, red on this Mac at main; CI on Linux judges): `tests/entities.py`, `tests/stress.py`, `tests/optimality.py`, the card scripts and `tests/golden.py`. A golden `coord_*` fixture whose window had a slope at or above 0.5 with a level moving more than 1.25 would change its `cop_refusal`; none was measured here.

## Unpinned sites

Sites on `draw_range.py:511` are this part's own line (the level judgement); each is killed locally by the block of `## Mutation proof` and left to `mutation-autofix` to pin (`ci-autofix.md`): none is pinned by hand.

- custom_components/heatpump_optimizer/draw_range.py:511 CMP_BOUND*2: pinned by mutation-autofix; killed locally (`>` on the slope bound in diff mode, `<` on the level bound as `level_bound_exclusive`)
- custom_components/heatpump_optimizer/draw_range.py:511 BOOLOP: pinned by mutation-autofix; killed locally as `and_to_or`
- custom_components/heatpump_optimizer/draw_range.py:511 RETURN_DEL: pinned by mutation-autofix; killed locally in diff mode

Every other site below is on a line the stacked R10-COP-LEARNER-DRAW-FLOOR diff adds (a827c3d985), not this part; it is listed because this branch is measured against main until that group merges, and its body answers each. Once it merges they leave this diff.

- custom_components/heatpump_optimizer/accuracy.py:874 CLAMP_DROP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:874 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:922 CLAMP_DROP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:922 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:922 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:936 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:942 CLAMP_DROP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:942 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:942 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:970 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:975 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:977 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:980 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:997 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:999 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:1001 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:1004 BOOLOP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:1004 CMP_BOUND*3: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:1004 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/accuracy.py:1009 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:962 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:962 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5345 BOOLOP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5345 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5371 BOOLOP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5371 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5378 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5423 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/coordinator.py:5895 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:247 BOOLOP: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:247 CMP_BOUND*2: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:247 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:496 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:499 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:499 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:500 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:502 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:502 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:523 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:545 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:545 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:548 CMP_BOUND: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:548 GUARD_OFF: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:551 CLAMP_DROP*2: pinned by mutation-autofix; added by the stacked a827c3d985
- custom_components/heatpump_optimizer/draw_range.py:551 RETURN_DEL: pinned by mutation-autofix; added by the stacked a827c3d985

## Red checks

- `mutation`: red by construction on the sites under `## Unpinned sites` until mutation-autofix pins them after the push. No cheaper detector exists: a pin is that lane's measurement of each site against every driver whose closure reaches it; this part's own sites are killed locally (`## Mutation proof`).

No CI run exists at this head; `ci_predict.py` (`## Figures`) predicts no other red.

## Forward-carry

- (a) The ceiling store fills only from the system-identification ceiling probe, which runs only when the user presses Run System Identification and, while the house learner is unconverged, arms the fit instead: on the measured install 0 of 561 cycles ran the experiment and the store held 0 samples while the plan booked the configured 4.0 kW against a measured 3.21 kW mean at the ceiling. Precondition for part 2: a learned top on such an install needs the probe armed without a press, or ahead of an unconverged fit; ordinary ceiling-written intervals do not rescue it (2 of 116 window samples). Re-measure with `draw_map_linearity.py --bundle` (`experiment_cycles`, `ceiling_store_rows`). Carry: R10-DRAW-MAP-EVIDENCE
- (c) `dev/audit/harnesses/` has no `README.md`, so the harness is indexed nowhere but its own header; an index of one of 296 files would read as complete. Carry: dismissed: no index exists to extend

Roster carries of this group, both part 2's:

- Carry 0 (owner scope addition 2026-11-14: what the debug-week collection and the diagnostics download must carry for a D15 seat): part 2's collection design; part 1 builds no collection and does not edit `diagnostics.py`. Its one input from here: the harness's `--bundle` reads store and cycle rows only, because the replay is keyed by entity id; a bundle shape a D15 seat can debug from would let the map and step arms run without an out-of-tree extraction. Carry: R10-DRAW-MAP-EVIDENCE
- Carry 1 is body item 19509d31 above, landed on the roster from this body; not built here, the experiment arming is part 2's. Carry: R10-DRAW-MAP-EVIDENCE

## Friction

none
