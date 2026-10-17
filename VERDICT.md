Fix review: blocked b8639bc20d5b2310ee25853831d5a4280accf231 harness: class-open optimizer.py:2982

bus-nonce: 06f138f3f7e1611b53d19d9a504e1052

Round 1. Measured at head `b8639bc20d5b2310ee25853831d5a4280accf231` in a fresh detached worktree (`/private/tmp/rv-2347-r1`), baseline `e3f3b312fff572904f24d78a44a2c4492b1a8ddb`, which is still the merge base after `origin/main` advanced to `b254b5b069c27921aa124372f5abd11f014ceb37` during the review. Two blocking findings; the fix's own numbers all reproduced.

## Block 1 -- class-open: `optimizer.py:2982`

The body's second enumeration rule is `grep -rn "heat_loss_coefficient" custom_components/heatpump_optimizer/*.py`, stated as widening the class to "every site that builds a house UA from one field". That rule returns `optimizer.py:2982`:

```
typical_heat_loss = (  # the learned scale too, as the dynamics (D2-s2-01)
    self.model.params.heat_loss_coefficient
    * self.model.params.house_heat_loss_scale
    * (self.config.target_temp - np.mean(outdoor_temps))
)
```

`heat_loss_coefficient` is the configured zone total on a preset two-zone house: `presets.py` sets `house_heat_loss_coefficient = loss`, `upper_floor_heat_loss = loss * upper_ratio`, `lower_floor_heat_loss = loss * lower_ratio`. So this scalar is the same configured-total shape `_space_demand_kw` was before this diff, missing `lower_floor_heat_loss_learned`. Measured on a derived two-zone preset (timber slab, 1980-2005, 150 m2, radiators up / floor down, split 0.65/0.35):

RESULT `seam(2982)/dynamics-1=-17.3554%` at ratio 1.6; `+0.0000%` at ratio 1.0 (the null arm, where the two bases agree).

The seam is in neither the diff nor the body's dispositions: the body lists 13 rule-2 sites and states "One seam is open, and it is not this group's: `coordinator.py:10403`". Neither the roster nor #2239 dispositions it (`grep -n "2982\|typical_heat_loss" dev/programme/rosters/wave-r10-groups.json` is empty). `optimizer.py` is outside this group's `files`, so the repair is a disposition plus a carry or a new issue, not a fix here -- but the body must say which.

## Block 2 -- carry-missing: not carried to R10-SCORES' brief

The appended text exists only in the roster's `carry` array. R10-SCORES' `brief` -- the string the wave runner hands the fixer (`web-fix-wave.js:307-308`, "Your brief ... `${g.brief}`") -- still ends its `Forward-carried (finding-propagation.md)` list at (3), with no envelope-score entry. Ten of the eleven groups holding a `From R10-` carry entry mirror it in their `brief`; R10-SCORES is the only one that does not:

RESULT `R10-SCORES: carry_FromR10=1 brief_has_FromR10=False`; the other ten, including `R10-SOLVER`, `R10-UX-HEALTH` and `R10-CONFIGFLOW-PAGES`, `brief_has_FromR10=True`.

`brief_lint.mjs` lints a roster's `brief` and does not read the in-group `carry` array, so the record is neither linted nor delivered. The commit's own message (`aa7dac5b4`) says "carry the envelope score's UA basis to R10-SCORES' brief". `finding-propagation.md`: the stage's brief is the live group's `brief` string. The entry (with its split-1.0 null arm and its precondition) must go there too.

## Reproduced at both ends

Step 1, mutation. M0 at the unmutated head: `ALL 4156 FEATURE CHECKS PASSED`. M1 (`params.lower_floor_heat_loss_learned` -> `params.lower_floor_heat_loss` in `_space_demand_kw`, two-line anchor with a count==1 assertion, restored with `git checkout --`):

RESULT `1 of 4156 FEATURE CHECKS FAILED`; the single red is the #2239 check, got `(True, 1.922, 7.74098, 11.121751)`. Nothing else moved.

Step 2, the finder's harness (`dev/audit/rounds/round10/study-reseed/reparam_sites.py`; the body's "blob `7c49087f39bb`" is this file's raw sha1, the git blob id is `7647e3d2aa`):

RESULT `space_demand_rel_diff=0.4367` (A 7.741, B 11.122, model-consistent 11.122 kW) -> `0.0000` (11.122, 11.122). Every other row flat at both ends: `model_rollout_48h_max_abs_diff_c=0.000e+00`, `effective_ua_rel_diff=0.000e+00`, `sysid_prior_ua_rel_diff=0.4367`, `sysid_adopt_effective_rel_err_A=0.4367`, `_B=0.0000`, `newton_step` rows unchanged -- the refuted D-2 seams were not touched.

Independent oracle (`dev/audit/rounds/round10/catchup/study/ratio_v2.py`; raw sha1 `d185b178b8a2`, git blob `76650e8779`), `--scale 1.0 --ratio 1.6`:

RESULT `D1.r1.600.space_demand_vs_dynamics=-0.2213` (4.940 vs 6.344 kW) -> `+0.0000` (6.344 vs 6.344); `D1.r1.000` `-0.0000` at both ends; `D2` `-0.0007` / `-0.0008` at both ends; `D3` rows unchanged.

Step 3, null control. Finder harness `--ratio 1.0`: `0.0000` at both ends, so the baseline's `0.4367` is the split and nothing else. Other split arms, head vs base: ratio 1.6 `0.0000` vs `0.2842`; ratio 0.8 `0.0000` vs `0.0947` -- the fix is not one-direction.

Step 4, claims and drift. `env_drift.py --all e3f3b312f`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE`; every fixture byte-identical or may-drift. Both claim files are byte-identical to the merge base; the diff moves no fixture.

Step 5: `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched (the diff is six files and contains none of them).

Step 7 and 12: the body names `b8639bc20...`; the head re-read at post time is `b8639bc20...` (`gh pr view headRefOid` and `git ls-remote origin fix/r10-ratio-sites`).

Step 8, the label's numbers re-derive. Configured zone total `190.0000 W/K`; effective `(U + L*r) * scale` `244.0000 W/K` at split 1.6 (`rel -22.1311%`), both `190.0` at split 1.0. `ratio_v2` prints fit `189.9 W/K` (the fitted value; the configured total is 190.0) against true `244.0` at split 1.6 and `190.0` at split 1.0. The label's stated basis (configured total, not the effective UA) is the arithmetic the code shows.

Step 11, red checks. The head has 45 check runs: 30 success, 15 skipped, zero failure/timed-out/action-required. The earlier PR head `96bab6f67` carries only cancellations. No gate check went red on a branch commit, so the second trigger does not fire; the body still answers its `tests/structure.py` account. That account does not reproduce at the pushed first commit `9cdb7c987` (`max_class_loc=8635`, `STRUCTURE RATCHET PASSED`), so the 8643 reading was the fixer's pre-push cut, not a branch commit -- harmless, but the body's attribution is imprecise.

Step 13. `git merge-tree --write-tree origin/main HEAD` exits 0 against both `e3f3b312f` and the current `b254b5b0`; no conflicting path, so the claim files are not the question.

Step 14. Structure and score at both ends: `max_class_loc 8635 <= 8635` (base and head identical), `coordinator_attrs 151`, `seam_cut_total 752`, `STRUCTURE RATCHET PASSED`, `Architecture score: dS +0.0000 NULL`. The coordinator change is line-neutral, so the first cut's +8 was paid rather than absorbed, and no metric moved by an unimproved change.

Step 15. The coordinator hunk stays in the owning seam `_space_demand_kw` and reads the model's own property (no parallel mechanism, no HA import, no computation added to the coordinator). The label lands at the value's owner (`SysIdResult.heat_loss_kw_per_c`) and its published contract (`SysIdResultView`), with the alternative (publishing the effective figure) named and refused as duplicating `house_heat_loss_effective`. The architect note (position 3 of 24, `_space_demand_kw` only) is followed.

## Notes, not blocks

- The body's "blob `7c49087f39bb`" / "`d185b178b8a2`" are raw file sha1s, not git blob ids (`7647e3d2aa` / `76650e8779`). Instrument identity is pinned either way; the word "blob" is what does not resolve.
- The roster entry's `architect_note` ("position 4 of 25") and its `brief` ("position 3 of 24") still disagree. The body's Friction section records it; this review bound to the brief, 3 of 24.
- `prepr`'s `FIGURES: 12 resolved, 1 not verified` was not re-run here (heavy; `pr-contract` and `briefs` are green at the head).

Evidence: `/private/tmp/rv-2347-r1-evidence/` (`head.txt`, `M0-features-head.log`, `M1-features-head.log`, `mutation.txt`, `finder-*.log`, `ratio_v2-*.log`, `env-drift-head.log`, `structure-head.log`, `archscore-head.log`, `label-probe.txt`, `class-open-optimizer-2982.txt`, `carry-destination.txt`, `enumeration-head.txt`, `check-runs-head.txt`, `merge-tree-and-first-commit.txt`).
