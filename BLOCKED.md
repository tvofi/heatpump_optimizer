# BLOCKED: R11-OUTSIDE-SELF-SETTING-PUMP, fix review 1 repair (PR #3662)

Question: The heat-ask probe has no regressor movement the draw cannot cause: its only span is the scale steps the learner folds from that same draw. A guard on the probe's existing rows therefore cannot separate a self-setting draw that varies on its own from a heat-led one across the whole swing domain; no slope rule tried, on levels or on row-to-row changes, does. Closing the class needs a design change beyond this PR's seam. Which one does the designer and owner want: (a) an exogenous step (the learner moves the scale by a known amount, or treats the configured-scale restore as the probe's step), or (b) a hold on folds while the verdict is undecided, plus a significance rule that may stay undecided? (b) replaces the approved note's "while pending, an admitted row keeps base's outcome".

Code state, not handed off: ab0960f62f8052e420698dbdd5aebc6d1fd561ef. It is PR head e78ef18efd plus the partial repair (511e53a8e0, d2384f13ad), a merge of origin/main 6f422812d5 (b7a77e86dd, which resolves a draw_range.py conflict with R10-DRAW-MAP-EVIDENCE (b) through one shared `draw_range._verdict`), and the deletion of seven stale ledger pins. Nothing was pushed to handoff/r11-outside-self-setting-pump or handoff-body/.

## What was tried, and what it measured

The repair: `draw_range.step_response` judges the probe on row-to-row changes of log drawn on log heat ask, so a slow drift is left only its per-row increment. `CopInterval.cop_scale` is now read before the cycle's release moves the scale, which is the scale the interval's ask ran under, as its docstring already states. Without that alignment a heat-led draw responds one row late, and the differenced slope reads every heat-led row `does_not_follow`: measured, with `heatled_true_0.68_flat_x672` and `heatled_true_0.8_flat_x672` both reading does_not_follow before the alignment.

On the reviewer's rows (evidence/attack_drift_rows.py at ba984f3567, run at b7a77e86dd) every row reads `does_not_follow` and ends at 1.000: the null control, ±15 % over 64 and 80 cycles, ±30 % over 96, ±15 % over 120, and the mix at phases π and 0. Every PR `selfset_*`/`heatled_*` row keeps its head verdict. The new features.py checks (s) fail at 1134fe3655 production (the swing rows read 0.500 follows, and a heat-led pump of true 0.68 under a weather swing reads does_not_follow there too) and pass before the merge (`ALL 91 FEATURES BLOCK PASSED` at the pre-merge tip, whose production code is 511e53a8e0's). The block was not re-run unmutated at the merged tip. Of 9 applicable hand mutants (`blocked-evidence/hand_mutants_at_b7a77e86dd.txt`), 9 are killed. The 3 marked NOT-APPLIED were anchored on pre-merge text and were not re-run.

The class check fails. `blocked-evidence/sweep.py` drives `cop_duty_floor.py`'s `flat_row` and coordinator over 1830 self-setting rows (1.6, 2.2 and 3.0 kW; periods 8 to 240 cycles; amplitudes ±15/30/40 %; seeds 1 to 5; four phases; plus scale0 0.5 and 0.7) and 360 heat-led rows (true 0.45 to 1.3; a ±15/30 % weather swing of the true COP; meter noise 0/5/10 %; scale0 1.0 and 0.5). Per-cell counts are in `blocked-evidence/sweep_cells.txt`, and the raw lines in `sweep_wt_head.txt` (1134fe3655) and `sweep_wt_fix.txt` (b7a77e86dd):

- Self-setting rows latching `follows`: head 397 of 1830, fix 122 of 1830.
  - Closed at the fix, 0 of 20 in every cell: 2.2 kW and 3.0 kW at 64 to 240 cycles, the reviewer's domain.
  - Open at the fix: a daily swing (48 cycles) at ±40 %, 4 of 20 at 2.2 kW and 7 of 20 at 1.6 kW.
  - Opened by the fix, where the head read 0: fast swings at 2.2 kW (8 cycles ±30 %, 10 of 20; 16 cycles ±40 %, 8 of 20) and 3.0 kW (8 cycles ±40 %, 6 of 20).
  - Mechanism: where the draw's own row-to-row change is the size of the scale's step, differencing cannot separate it either.
- Heat-led rows not latching `follows`: head 154 of 360, fix 128 of 360. The fix worsens true 1.3 with no swing from 6 of 18 to 14 of 18, and true 0.45 under ±30 % over 48 cycles from 9 of 18 to 16 of 18.

The trade is visible on both sides: any threshold on this regressor moves false latches between slow and fast swings, and between self-setting and heat-led rows. Shipping the tip would be the partial guard the brief forbids.

## Why it is beyond the seam

Measured trace (`blocked-evidence/trace.py`, 2.2 kW flat control, at the pre-repair head): rows are held while the window is pending (ticks 0 to 46, all at scale 1.000). The window turns unobtainable at tick 47, the release folds 44 held rows at once (scale 1.000 to 0.758), and the probe latches 5 rows later. So the regressor's span is one step at one moment, and the test compares the draw before and after a time split. A draw with independent variation at that moment is indistinguishable from following, whatever statistic reads the rows. The two remedies above each change what the learner does, which the approved design (`design.md` at b31718e618) fixes:

- (a) an active or exogenous step;
- (b) refusing folds while undecided and waiting for decisive evidence. Base's pending folds walk the scale to the clamp in about 75 rows, faster than evidence accrues.

## Findings for the next seat

- The priced-scale alignment is needed by any regressor that pairs the draw with the scale: `CopInterval` built after `MeasuredCop.release` carries the post-release scale, against its own docstring. Measured above. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- The merge with origin/main conflicts semantically in draw_range.py: R10-DRAW-MAP-EVIDENCE (b) added the level rule inside `ask_evidence`, which this PR had split into `draw_response`. b7a77e86dd resolves it with one `_verdict` (slope plus level), bit-identical for `ask_evidence`. The PR head e78ef18efd still conflicts with main (`git merge-tree --write-tree origin/main e78ef18efd` rc 1). Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- Orchestrator NOTE 1 (16:05Z, the `prepr: passed` line in BODY.md) is not applied: no body was produced, and prepr.sh was not run on a blocked tree.

Instruments: `blocked-evidence/sweep.py` (run from a worktree root as `PYTHONPATH=tests/hastub:custom_components:tests python3 sweep.py 4`) and `blocked-evidence/sum.py`.
