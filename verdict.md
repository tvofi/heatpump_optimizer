Fix review: blocked 9851d39de867653f4fdc4412c3a1eea8dcb5f7b3 vacuous-test: deleting the pending-prediction "solar" write (coordinator.py:9796) passes all 4284 feature checks, and the M09 equivalent mutant has no survivor_triage entry, so the required mutation check stays red

PR #2563, group R10-NIGHT-FOLDS, fix review round 2 (cloud reviewer seat). The head I measured is 9851d39de867653f4fdc4412c3a1eea8dcb5f7b3: the round-2 code head 749f28387 merged with origin/main e7c664856. Its production files are byte-identical to 749f28387. The diff to `dev/governance/roles/` between the merge base and origin/main is empty, so the contract is current. I used detached worktrees at the head and at the merge base e7c664856, with Python /opt/hpo/venv-ci (numpy 2.4.6, scipy 1.17.1). The evidence is in ev/; ev/HEAD.txt names the head.

## Blocking

1. Step 1: the mutation proof is vacuous on one production line the fix adds. The refit arm only works if `_record_accuracy` stages the interval's irradiance into `_pending_prediction`. That is `"solar": ctx._current_state.solar_radiation` at `coordinator.py:9796`. I deleted that line alone, in a worktree at the head:
   - `tests/features.py` reads `ALL 4284 FEATURE CHECKS PASSED`, rc=0 (ev/mutants/R14_pending_solar_line_deleted.log).
   - Setting the value to `None` also passes all 4284 (R08).
   - The check `#2223: an accuracy sample records the sun its prediction was made under` hand-builds `_pending_prediction`, so it never runs the staging write.
   - The companion `r10_night_folds_learners.py` builds `AccuracySample(... solar_radiation=...)` directly, so it never runs the write either.
   - CI's mutation table has no operator for a dict entry, so `mutation` cannot see this.

   With the line broken, every refit sample reads as dark, and the refit gate turns off silently in production while every check stays green. To fix it, in the same check call `_record_accuracy()` with `_current_state.solar_radiation = 640.0` and assert that the newly staged `_pending_prediction["solar"] == 640.0`. The method stages the next pending at its end, at line 9770. A second `_record_accuracy()` with the sample's sun at 640.0 would also do. Then re-run the deletion mutant.

2. Step 11: the required `mutation` check cannot go green at this head. It is red at 9851d39 (job 119307477218) and at the moved head 56297e44 (job 119313674771). Both runs print the same thing:
   - `ADDED UNPINNED custom_components/heatpump_optimizer/coordinator.py:9041 CMP_BOUND: or settled < INTERNAL_GAINS_MIN_UA_CONFIDENCE`
   - `MUTATION TABLE REFUSED -- ... 1 of them added by this diff`

   The body's answer gives M09 a "written triage", but that triage exists only in the body. `tests/mutation_ledger/survivor_triage/` holds no entry for `_fold_internal_gains` at the head (ev/survivor_triage_fold_internal_gains.txt). CI never triages a survivor (`tests.yml`: "Survivors are listed for a human verdict, never triaged here"; ev/tests_yml_survivors_never_triaged.txt). So no bot commit will come, and `mutation` is in main's required contexts (ev/required_contexts.txt). The triage itself is correct, and I re-derived it:
   - `house_loss_confidence(n)` equals 0.9 for no integer n below 10^6.
   - `h(113) < 0.9 < h(114)` is True.
   - The null control at `t = h(114)` returns `[114]`.

   Record it as an `equivalent` verdict under `survivor_triage`, with the body's reason, pinned to the line text.

## Verified at base e7c664856 and head 9851d39 (RESULT lines are mine)

Step 2, the finder's harness. I ran `dev/audit/rounds/round10/study-ident/run_q1.sh` at both ends, and each end has 20 of 20 `rc=0` (ev/q1base, ev/q1head, ev/spread.both.txt). Every `fixed_arm_spread` in the body re-derives exactly:
- P0 to P5 autumn: 0.2691->0.0147, 0.3790->0.0219, 0.1405->0.0074, 0.3383->0.0205, 0.2383->0.0101, 0.2894->0.0168.
- The delivery arms: P1 g0.4 0.3962->0.0224, P1 g0.6 0.3925->0.0218, P0 g0.4 0.2677->0.0154, P0 g0.6 0.2757->0.0150.
- The indep arms, P1 to P5: 0.3918->0.0230, 0.1432->0.0078, 0.3432->0.0218, 0.2474->0.0116, 0.2902->0.0178.
- P1 ua_bias: fix2.00 +0.2474->+0.0157, learn -0.0262->-0.0001, learn+gains -0.0332->-0.0111, none -0.0900->-0.0038.
- P1 g0.4 fix1.00 +0.4423->+0.5833, against the base's dark1.00 +0.5946.

Step 3, the null control. The flat-irradiance arm reads 0.0000 on P1 to P5 at both ends.

Step 14, the perturbation. At the head with `HEAT_LOSS_MAX_SOLAR_W_M2 = 1.0`, P1 autumn reads `fixed_arm_spread=0.0000` and fix2.00 +0.0026 (ev/thr1.P1.autumn.out). So the movement is the gate's.

The other harnesses:
- **Companion `r10_night_folds_learners.py`:** house.sunlit 8->0, lower.sunlit 1->0, refit.sunlit 192->0, gains.unconverged 0.0990->0.0000. The dark arms read 8 / 1 / 192 at both ends, and gains.converged reads 1.9800 at both ends.
- **`r10_night_folds_alternatives.py`:** identical at both ends. Ridge 1.00 reads 0.0500 / 0.0476 (6.7 % of 0.7143), and net_of_ua_part reads 0.0000 / 0.0000.
- **`r10_vent_sun_transient.py`:** identical at both ends. Check bias 1.0 reads `[0, 20, 0, 0]`, census bias 1.0 reads `[0, 39, 38, 30]`, and every arm reads `end_tripped=False`.
- **`r10_vent_bias_window.py`, 120 arms:**
  - The four no-window arms read `false_share` 0.000 at both ends.
  - The 300 W/K windows are detected on 60 of 60 at both ends, and `detect_h` moves by at most 0.25 h.
  - The 150 W/K x 4 h window is detected on 14 of 20 at the base and 13 of 20 at the head. The one change is `seed1.onoff.g1.0.ua1.0.vent150x4h`, 3.75 -> nan.

Step 1, my other mutants. I applied each alone to a worktree at the head (ev/mutants/summary.txt). The unmutated head and a comment-only null mutant both read ALL 4284 PASSED. Every mutant below is killed:
- house sunlit gate off: 3 checks
- lower sunlit gate off: 1
- `_refit_pair` sunlit gate off: 3
- convergence clause deleted: 1 ("the hour shape waits for the heat-loss level")
- threshold 0.9 -> 0.0: 1
- gauge `>` -> `>=`: 2
- gauge 50 -> 1000: 9
- `solar_radiation=pending.get("solar")` dropped: 1
- `from_dict` field dropped: 1
- `to_dict` field dropped: KeyError, rc=1
- house gate moved above `_fold_solar_aperture`: 1
- house gate moved above the vent CUSUM feed: 3, including #2241's `a bias scaling with the sun never trips the detector`

Step 6, the class. The enumerator (sha1 9f7e1637…) returns the same 13 SEAM lines at both ends, and the body dispositions all 13. Its controls pass at both ends. At the head, lower moves FAIL->PASS (`gated=True`), while house and refit still FAIL at 0.925 / 0.937. I confirmed the body's reason by reading the probes: they re-implement the walk and build samples without irradiance. `probe_internal_gains` raises TypeError at the head (ev/enum.head.out), as the body states. No seam is class-open.

The other steps:
- **Steps 4 and 5:** `env_drift.py --claims-only` prints `claims hygiene: origin/main ok`. No golden or claim file is touched, and VERSION, the manifest and RELEASE_NOTES are untouched.
- **Step 10, the forward-carry:** R10-BRIEFS-FOLD (stage not-started) carries the gains-arm precondition with its control. It is there at the body's SHA 617ce13160e7 and at the roster head 2c76c3128bf6 (ev/roster_carry_R10-BRIEFS-FOLD.txt). The round-1 block is cleared.
- **Step 13:** `git merge-tree --write-tree origin/main 9851d39` exits 0 with origin/main at b6a38f858 (ev/merge_tree_origin_main.txt).
- **Structure:** seam_cut_total reads 718 at the base and 716 at the head, and the ratchet passes.
- **Step 14 on that drop:** I removed the mechanism by restoring the two inline capacity blocks in place of `_zone_capacity`, and the count goes back to 718. Restoring the dt guard or the zone-temperature helper leaves it at 716. A planted local alias of `ctx._thermal_params` with nothing improved also leaves it at 716. So the drop is earned by the dedup.
- **`score.py --diff e7c664856`:** `dS +0.3110 IMPROVES` (duplication_copies 41->40, coord_footprint 2494->2493).
- **Body figures:** the solar figure re-derives (`gain50_kW=0.2450 dT_halfhour_K=0.0122`). Both round-1 corrections, the const.py figure and the companion header, are in 749f28387.

Step 11, the other red checks:
- `nightly-status` grades main, and the diff reaches no replay-status input.
- `pr-contract` (both runs, at both heads) refuses only in `carry_audit.py check`: `UNROUTED body item 1492c8f9`. The routing below answers it. Preflight reads "clean no refusal", and prepr reads "no version edit".
- At 56297e44 every other check concluded green, except `closures`, which was still in progress when I wrote this. This verdict does not turn on it.

Step 12, the head moved. refs/pull/2563/head is now 56297e445e024470f5816c3a3bcedcefd01b1e12, which is 9851d39 merged with origin/main b6a38f858 by the orchestrator's merge. Its tree, 25af6333…, equals the automatic `git merge-tree` of the two parents, so the resolution delta is empty. That delta touches only `.github/workflows/governance.yml`, delivery rows and `tools/audit/seat/*`, none of which this fix or its harnesses read (ev/head_move_delta.txt). Every figure above stands for 56297e44.

## Carry routing

- Body item 1492c8f9, `## Figures`, "Residual net of the UA fold's ΔT part". I judged it on its merits. It is the measured rejection of an RCA alternative the fix does not ship: net_of_ua_part reads 0.0000 at both ends, and the shipped shape is the convergence gate. It is not a lead. Carry: dismissed: measured rejected alternative, not shipped (item 1492c8f9)
- Review 6317463517 item b29dfdfd ("Round: first review by this seat."). Carry: dismissed: review metadata line, not a finding (item b29dfdfd)
- Review 6317463517 item f2a90213 (the bus-nonce trailer). Carry: dismissed: bus nonce metadata, not a finding (item f2a90213)
- The R10-BRIEFS-FOLD carry names its control's path as `dev/audit/rounds/round10 r10_night_folds_learners.py`. The file is `dev/audit/harnesses/r10_night_folds_learners.py`. The seat that picks up that stage should use that path. Carry: R10-BRIEFS-FOLD
- In `r10_vent_bias_window.py`, the delivery-1.0 mean |ua_bias| rises from 0.0155 to 0.0195. The largest arm is the undetected 100 W/K x 8 h window, 0.0563 -> 0.0709. That harness plants no aperture error, so night-only folds take fewer samples with no confound to remove. The window's extra loss is real heat loss, and the delivery-1.0 mean stays inside the RCA's 5 % bar. Carry: dismissed: measured consequence within class bar

## Round

Round 2 of review for this PR. This is this seat's first review of this head. A third round still owes a repair, not a re-cut.

bus-nonce: 4004edbfe5086f63375b4065c95e4a1d
