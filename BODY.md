R10-DRAW-MAP-EVIDENCE, part 1 (#3106 item 4). Restored from its archive tag `archive/handoff/r10-draw-map-evidence` (3533ba12b817b3d10218d5dee27db10933e28ab8, `Fix review: merge` at that head) with origin/main merged in (9e358a2a52). R10-COP-LEARNER-DRAW-FLOOR, on which it was stacked, is on main, so this diff is part 1's own: `git diff origin/main HEAD` over its four files, hunk headers aside, is byte-identical to `git diff d7839aee81 3533ba12b8` over the same files (`## Null control`). One commit is new: f3b7139899 deletes the two mutation-ledger pins main recorded on the base's `ask_evidence` return line after the draw-floor merge, which `ci_predict.py` names `STALE PIN`.

The evidence is one owner diagnostics download, measured out of tree by a separate seat. No row, entity id, timestamp or name from it is in this diff, this body or a commit message: only derived numbers, and synthetic fixtures that reproduce the derived shape.

- **(b) The ask judgement reads the level.** `draw_range.ask_evidence`, the one place the draw-floor design makes the judgement, returns `ASK_FOLLOWS` only where the slope of log drawn on log asked is at least `FOLLOW_SLOPE_MIN` **and** the fitted ratio of drawn to asked at the asks' 90th percentile and at their 10th are within `DISAGREE_FACTOR` of each other: `(high / low) ** abs(1 - slope) <= DISAGREE_FACTOR`, from the percentiles and slope the function already computed. No new constant: `DISAGREE_FACTOR` is the factor at which the same window already calls one sample a disagreement.
- **(a) The empty ceiling store: the store is right to refuse, nothing built here.** The cause is upstream of the store, in when the experiment runs; the approved design builds it in part B (`## Forward-carry`).
- **(c) The measurement as a harness**, `dev/audit/harnesses/draw_map_linearity.py`, on a seeded synthetic fixture, with a `--bundle` reader that touches only store and cycle rows.

Roster carries 0 to 4 are each built by a split part the approved design (`design/R10-DRAW-MAP-EVIDENCE` 9aa450f5, approved at f10dd418) names, already handed off and archived: part A `archive/handoff/r10-draw-map-evidence-a` (cc335482ae, `Fix review: merge`), part B on it (8c1508d9c1, no verdict yet), part F on part 1 (880b015c8b, `Fix review: merge`); none is built in this diff (`## Forward-carry`).

Not in scope, by the brief: any change to the open-loop map `thermal_model.flow_setpoint_for_level` (the data is closed-loop, the band's middle was never held, one install fits a constant), `diagnostics.py`, and the experiment mode.

### (b) Why the level is read across the span, not as one figure

A bound on the whole window's level (drawn summed over asked within some factor of 1) was refused: the COP learner reads a departure as an efficiency shift on `ASK_FOLLOWS`, and a pump whose true COP scale is 0.6 draws 1/0.6 = 1.67 x every ask, a level the owner's 1.70 cannot be told from. `cop_duty_floor.py`'s `true_0.6` row is that install and learns the same scale at both ends of this diff (`## Figures`); a whole-window level bound would refuse it every interval (`COP_REFUSED_OFF_ASK`) and its scale would never learn. What separates the two is that an efficiency shift is one ratio at every ask and the owner's draw is not: on the synthetic shape the fitted draw is 2.1 x the ask at the span's low end and 1.4 x at its top.

Downstream, the verdict has three readers (`git grep -n -e ask_evidence -e follows_ask -- custom_components` returns only `draw_range.py` and `accuracy.py`): `MeasuredCop.judge_ratio` (on `ASK_IGNORED` every interval reads `COP_REFUSED_OFF_ASK`), `MeasuredCop.release` (held departures are dropped, not folded), and `accuracy.diagnostics_view` (`draw_follows_ask` False). `judge_ratio` runs only where no heat reading exists (`heat_kw is None` in `_fold_measured_cop`). No solve, optimizer or arbiter path reads the verdict, so no cost figure moves at a fixed learned state, flat price or not; the verdict reaches cost only through which intervals train `cop_scale` on an install with no heat reading.

### (a) Why the ceiling store holds 0 samples

`draw_range.fold` sends an interval to the ceiling store only when all of: `is_running_space`, `experiment_s` not `None` (the interval's own action ran the system-identification experiment), and `DrawRange.takes_ceiling`. Every other interval goes to the window, where a ceiling-written draw is only overdraw evidence against an existing store (`DrawRange._overdrawn`). The experiment is armed only by the **Run System Identification** button (`async_arm_system_identification`, whose one caller is `button.py`), and `sysid.armable` arms the fit, not the probe, while the house learner is unconverged. On the owner's download the experiment gate alone drops every interval, and the window's ceiling-written running samples fall short of `CEILING_MIN_SAMPLES` (counts in `## Figures`), so relaxing the store's rule would not have filled it. The fix belongs to the experiment's arming: owner ruling S3 (2026-11-14) has the button arm the ceiling probe before the fit where the pump's top is unlearned, built in part B.

## Head

f3b713989931007f1802dbe0d669f313373a00fd, on origin/main f9b680fee43bb519996fc107c5f1c65df02683d7 (merged at 9e358a2a52; the merge base is that tip). Measured 2026-11-16 05:40 UTC.

## Mutation proof

Failing test first: the head's `tests/features.py` block run on main's production tree (a `git archive` of f9b680fee4 with the head's `tests/features.py` copied in) prints `2 of 20 FEATURES BLOCK FAILED`: "the measured shape (slope 0.70, ...) does not follow its ask" with states `('follows', 'follows', 'follows', 'does_not_follow')`, and "a flat draw over asks spanning 1.2 fails on the slope, a square-law draw over asks spanning 1.5 fails on the level" with `('does_not_follow', 'follows')`. At the head: `ALL 20 FEATURES BLOCK PASSED`.

The block: `tests/features.py` from the line `` # `follows_ask`'s own thresholds `` to `# MeasuredCop.judge_ratio holds a departure only while`, run by `tools/audit/seat/features_block.py` with the prelude its `--emit-prelude` writes (14 statements).

- `python3 tools/audit/seat/mutant_run.py --diff f9b680fee4...HEAD --cmd '<the block>'`: the 4 mutants `--list` names (`CONST_SWAP` and `STMT_DEL` on the `level_moves` line, `RETURN_DEL` and `CMP_BOUND` on the return), no `SURVIVED` line, rc 0. Diff mode prints only survivors; its baseline arm is the control (`--cmd false` prints `BASELINE FAILS`, rc 3).
- `python3 tools/audit/seat/mutant_run.py --spec <5 mutants> --cmd '<the block>'`, the operators diff mode does not draw: `SURVIVED NULL`; `KILLED level_bound_exclusive` (`<=` to `<`), `KILLED level_conjunct_dropped`, `KILLED slope_conjunct_dropped`, `KILLED and_to_or`, `KILLED abs_dropped`; rc 0.

## Null control

- Own diff unchanged by the merge: `diff <(git diff d7839aee81 3533ba12b8 -- <4 files> | grep -vE '^(index|@@)') <(git diff origin/main 9e358a2a52 -- <4 files> | grep -vE '^(index|@@)') && echo OWN-DIFF-IDENTICAL` prints `OWN-DIFF-IDENTICAL`; d7839aee81 is the first parent of part 1's first commit e6a48c09b0.
- Same asks, one ratio: the synthetic shape's asks drawn at 1.70 x with the same ripple follow; a draw within tolerance of its ask follows; a self-set draw (2.2 kW whatever the ask) does not, on the slope (checks in the block).
- `cop_duty_floor.py` reads identically on main's tree and at the head: `diff` of the two outputs `&& echo CDF-IDENTICAL` prints `CDF-IDENTICAL`.
- The harness's own nulls, synthetic, at the head: `ask_null_proportional=follows` beside `ask_evidence=does_not_follow`; shuffled set-points read `store_null_p95=0.045` against `store_r2=0.392`; the planted curvature reads `8/50` at c=0 and `49/50` at c=1.0.

## Figures

<!-- figure-block: scope-line mb=f9b680fee43bb519996fc107c5f1c65df02683d7 head=f3b713989931007f1802dbe0d669f313373a00fd -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

### (b) the judgement, both ends

- `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_linearity.py` (synthetic), at the head: `RESULT ask_pairs=116 ask_slope=0.620 ask_level_sum=1.873 ask_level_moves=1.488`, `RESULT ask_evidence=does_not_follow`, `RESULT ask_null_proportional=follows`. The same file run on main's production tree (a `git archive` of f9b680fee4): `diff` of the two `RESULT` sets differs in one line only, `ask_evidence=follows` on main.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, main and head: identical output, including `true_0.6=282/288_scale=0.603` and `true_0.7=285/288_scale=0.704`.
- Both ends of the input range: an empty window and 47 pairs read pending, a full window with no run-asked pair reads unobtainable (draw-floor checks, unchanged, in the gate's `tests/features.py`); at the bound, slope exactly 0.5 with level exactly 1.25 follows, and `<` on either bound fails the check (`level_bound_exclusive`, diff-mode `CMP_BOUND`).

### (a) and the owner download, not re-taken in this pass

The download is out of tree and not on this seat, so the `--bundle` figures could not be re-measured at f9b680fee4; they were taken at 3533ba12b8 (merge base 5b8f05ba4e), and every production line they exercise (`draw_range.ask_evidence`, `draw_range.fold`, `DrawRange.takes_ceiling`) is unchanged by the merge (`git diff --stat 3533ba12b8 HEAD -- custom_components/heatpump_optimizer/draw_range.py custom_components/heatpump_optimizer/sysid.py custom_components/heatpump_optimizer/button.py` prints nothing). Re-measure with `python3 dev/audit/harnesses/draw_map_linearity.py --bundle <download>`:

- at 3533ba12b8: `RESULT ask_pairs=115 ask_slope=0.630 ask_level_sum=1.807 ask_level_moves=1.509`; `ask_evidence=follows` at its base, `does_not_follow` at its head.
- at 3533ba12b8: `RESULT store_rows_at_ceiling=2` (of `store_rows=116`), `RESULT ceiling_store_rows=0 cycles=561 experiment_cycles=0`.

### Ratchets

- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`; no budget touched.
- `python3 tools/audit/archscore/score.py --diff f9b680fee4`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/pr/ci_predict.py --base origin/main` at the head: `no closures, fast, governance or instrument red predicted`; before f3b7139899 it predicted the two `STALE PIN` reds that commit repairs. Three `ADDED UNPINNED` lines, under `## Unpinned sites`.
- `PYTHONPATH=tests/hastub GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh` at the head: `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, exit 0 (the run reads its diff off the working tree, which held f3b7139899's two deletions from the start; the scope `closure.py select` prints is the same before and after that commit).

## Unpinned sites

Each is this part's own line `draw_range.ask_evidence`'s return (the level judgement), killed locally by the block of `## Mutation proof` and left to `mutation-autofix` to pin (`ci-autofix.md`).

- custom_components/heatpump_optimizer/draw_range.py:511 CMP_BOUND*2: pinned by mutation-autofix; killed locally (diff-mode `CMP_BOUND` on the slope bound, `level_bound_exclusive` on the level bound)
- custom_components/heatpump_optimizer/draw_range.py:511 BOOLOP: pinned by mutation-autofix; killed locally as `and_to_or`
- custom_components/heatpump_optimizer/draw_range.py:511 RETURN_DEL: pinned by mutation-autofix; killed locally in diff mode

## Red checks

- `tests / mutation`: red by construction on the three sites under `## Unpinned sites` until mutation-autofix pins them after the push. No cheaper detector exists: a pin is that lane's measurement of each site against every driver whose closure reaches it; the sites are killed locally (`## Mutation proof`).

No CI run exists at this head; `ci_predict.py` (`## Figures`) predicts no other red.

## Forward-carry

- Carry 0 (D15 collection and download): part F's (the debug-week trace, the bundle shape marker). Its one input from here: the harness's `--bundle` reads store and cycle rows only, because the replay is keyed by entity id. Carry: R10-DRAW-MAP-EVIDENCE
- Carry 1 (body item 19509d31, the ceiling store fills only from the probe): part B's, the ceiling-evidence change. Precondition it carries: a learned top on such an install needs the probe armed without a press or ahead of an unconverged fit; ordinary ceiling-written intervals do not rescue it. Re-measure with `draw_map_linearity.py --bundle` (`experiment_cycles`, `ceiling_store_rows`). Carry: R10-DRAW-MAP-EVIDENCE
- Carry 2 (owner rulings S1 to S4 on the design): S1 and S3 are part B's, S2 and S4 part F's; r12 to r18 ride the part whose lines they land on, r14 binding part B. Carry: R10-DRAW-MAP-EVIDENCE
- Carry 3 (the sweep kind to a sweep origin in `pump_arbiter.pass_origin`) and carry 4 (the sweep routing invariant in `draw_range.fold`): part B's. Carry: R10-DRAW-MAP-EVIDENCE

## Friction

none
