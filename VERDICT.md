Fix review: blocked 1134fe365519ce1334aa95960e19f908bb2b4f53 class-open: the heat-ask probe latches follows on a self-setting pump whose draw swings on its own, and the scale walks to the 0.500 clamp as at base

bus-nonce: e230047bc24bb37e571195634ac2042c

## Block

Step 6 (attack at other configurations the finding's harness accepts), a predicate's unguarded domain. The probe's verdict, `draw_range.draw_response` on (drawn, `asked_kw x cop_scale`) rows, takes its regressor's span from the scale's own moves, and the scale is folded from drawn over asked. So on a pump that sets its own power, any swing of the draw within the probe's first `MIN_SAMPLES` admitted rows reaches the heat ask through the fold. That makes the slope of log drawn on log heat ask near 1, and the probe latches `follows` on a pump that ignores the ask. Once `follows` is latched, every admitted interval folds and the verdict persists (`as_dict`), so the scale walks to `COP_SCALE_MIN`. That is the #3593 residual the owner ruled (D4) must be fixed rather than accepted. The PR's own self-setting rows all use a draw of `kw` ±3 % i.i.d., so none of them reaches this domain. Neither the body nor the approved design note (`design.md` at b31718e618) dispositions a self-setting draw that varies on its own.

Instrument: the head's `dev/audit/harnesses/cop_duty_floor.py` (sha1 09e6f53dfa, the same file the body cites), driven through its own `flat_row`/`run` with flat 1.5 kW ±2 % asks on the 4 kW nameplate, open loop, exactly as the PR's `selfset_*` rows. Only the draw changes: 2.2 kW x (1 + Σ a·sin(2πt/p + φ)) x U(0.97, 1.03). The rows are the reviewer's own (builder: fix reviewer, not the finder): `ev/attack_drift_rows.py`, `ev/attack_drift_map.py`, `ev/attack_drift_sweep.py`. Base rows are from the base production tree (367c3b9cac) with the head's harness file copied in, as the body did.

| row (seed 1, 672 intervals) | base | head |
|---|---|---|
| `selfset_2.2_swing0_control_s1` (null control: no swing) | 668/672 0.500, off5 625 | 48/672 1.000, does_not_follow |
| `selfset_2.2_swing0.15_p64_s1` (±15 %, 64 cycles) | 667/672 0.500, off5 625 | 667/672 0.500, off5 625, **follows** |
| `selfset_2.2_swing0.15_p80_s1` (±15 %, 80 cycles) | 668/672 0.500 | 668/672 0.500, **follows** |
| `selfset_2.2_swing0.3_p96_s1` (±30 %, 96 cycles) | 665/672 0.500 | 665/672 0.500, **follows** |
| `selfset_2.2_mix_daily0.1_5day0.2_phasepi_s1` (±10 % over 48 cycles plus ±20 % over 240, phase π) | 670/672 0.500 | 670/672 0.500, **follows** |
| `selfset_2.2_swing0.15_p120_s1` | 668/672 0.500 | 48/672 1.000, does_not_follow |
| `selfset_2.2_mix_daily0.1_5day0.2_phase0_s1` | 666/672 0.500 | 47/672 1.000, does_not_follow |

Domain map at the head, seeds 1 to 5 (`ev/attack_map_head.txt`, `ev/attack_sweep_head.txt`). Latched `follows`, every one ending at scale 0.500:
- 64 and 80 cycles: 5/5 seeds at ±15 %, ±20 % and ±30 %.
- 96 cycles: 5/5 at ±30 % and ±40 %, 2/5 at ±25 %, 0/5 at ±15 % and ±20 %.
- 48 cycles: 1/5 at ±40 %.
- 120 and 144 cycles: 0/5.
- The weather-like mix: 5/5 at phase π, 0/5 at phases 0, π/2 and 3π/2.

At the default half-hour cadence (`draw_range.WINDOW` comment), 64 to 96 cycles is 1.3 to 2 days, which is a weather front's timescale. A weather-compensated pump's draw moves that much with outdoor temperature while a pinned plan's ask stays flat.

The harness moves under its own perturbation: amplitude 0 latches `does_not_follow` and ends at 1.000, and ±15 % at 64 cycles latches `follows` and ends at 0.500. So the item is not void (`judge.md`). On these rows the head is byte-for-byte the base's outcome (the same folded count and scale), so the fix does not hold there.

What closes it is the fixer's (and the design's) to choose. A rule that settles the class has to separate draw-driven scale moves from heat-led ones, for example a regressor span the draw's own variation cannot create. Re-measure with the rows above at both ends and with the PR's `selfset_*`/`heatled_*` rows as controls. The heat-led rows have to keep latching `follows`.

## Findings

- Follow-up: the defrost carry routed to R11-INTAKE-R10-RESIDUE (roster at 5e4fdcb7cd, `wave-r11-groups.json`, item 0116e1a6) tells a fix it "needs this PR's verdict (`MeasuredCop.scale_response`)". Under the block above, that verdict can read `follows` on a self-setting pump. A defrost fix keyed on it inherits the same false latch, so the carry should state the control: the swing rows in `ev/attack_drift_rows.py` must read `does_not_follow` before the verdict is trusted. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Head and merge base: `ev/HEAD.txt`. The body's `## Head` names this head. `git merge-tree --write-tree origin/main 1134fe3655` reports rc 0 against origin/main e352724335 (`ev/merge_tree.txt`), so there is no conflict, and neither claim-file merge driver was invoked.
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched in the three-dot diff, and so are both claim files.
- Harness at both ends: the body's 16 moved rows reproduce exactly (`ev/harness_diff.txt`), as does the head harness file's sha1, 09e6f53dfaf95ef5d961eff047b002f96c93784b. 63 RESULT rows at each end. Only `held_full`, `held_filling` and the 14 R11 flat rows differ. The heat-led `held_*` controls read 96/96 0.811 and 0.810, and the defrost rows (factor 0.684 against 1.000) are identical at both ends.
- Failing test first: the head's block, from `R.section("COP learner duty floor keys` to `R.section("R10-COP-GATE (#2262)`, run on base production stops at `AttributeError: 'MeasuredCop' object has no attribute 'scale_response'` (`ev/failfirst_base_tail.txt`). At the head it prints `ALL 88 FEATURES BLOCK PASSED`.
- Full suite at the head: `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 5736 FEATURE CHECKS PASSED` (`ev/features_head_tail.txt`), matching the body.
- Hand mutants, the reviewer's own driver (`ev/hand_mutants.py`, `ev/block_driver.sh`, `ev/hand_mutants_result.txt`). Each was applied alone to the head's production code, run through the block, and restored. 9 of 10 were killed:
  - admission state guard
  - measured-heat guard
  - restore statement deleted
  - restore target set to the current scale
  - the judge_ratio latch made to fold
  - release reset dropped
  - `from_dict` not reading the verdict
  - clamp re-seed dropped
  - `draw_response`'s slope comparison flipped
- The tenth hand mutant, `judge_floor`'s `drawn_kw is not None` guard rewritten to refuse a `None` draw (`min(asked_kw, drawn_kw or 0.0)`), survived the block, which drives no heat-counter install. A `None` draw reaches `judge_floor` only on a heat-counter install with no power entity. The full `tests/features.py` kills it: `4 of 5736 FEATURE CHECKS FAILED`, rc 1 (`ev/features_mut_judge_floor_none.txt`). The first failure is "a heat counter with the electric counter and no power entity folds its span's COP ...": refusals `['duty_floor', ...]`, 0 samples. So the guard is pinned, and the payment's no-draw arm is reached and checked.
- Owed reds, from the head's own check runs. `tests / mutation` is red and in the `owed-reds` set. The body's `## Red checks` answers it: 47 unpinned added sites are left to `mutation-autofix` by `ci-autofix.md`, and the local diff-mutant run is named as the cheaper detector that already ran. `gate` is red as the aggregate. `tests / nightly-status` is red, not in the owed set, and owes nothing. I did not re-run the gate or the mutation table (step 11).
- CI: `merge_train.py classify ... --pr 3662` printed `WAIT 1134fe3655... pending: gate red: none` on every run from 15:03 UTC (`ev/classify.log`), with `tests / mutation-pins (3)` and `(4)` still in progress. The block above is on code, so it stands whatever CI concludes. For that reason this verdict carries no `pending-ci:` line: the brief has the relay refuse a verdict carrying one over a red, and that would drop a code block on a CI colour it does not depend on. The last classify, at return time, still printed WAIT. The head was re-read at return: `refs/pull/3662/head` is still 1134fe365519ce1334aa95960e19f908bb2b4f53.
- Forward-carry (step 10): the body's one routed finding (e98d0ab9) is on the roster branch at 5e4fdcb7cd with its control (the matched draw at 1.000). The other four body items are owner-ruled or design-stated residuals, dismissed with reasons.
- Round: first review of this PR.
