Fix review: merge d48018b80be11a2029e8492590a1a9e4b3a2eae9

bus-nonce: 9673b15ad16b13d7f26a5d5645464077

PR #2563, group R10-NIGHT-FOLDS. Fix review by the cloud reviewer seat. This is the third fix review of the PR: round 1 was blocked carry-missing at 829ea7c72, round 2 was blocked vacuous-test at 2f4758109. The body counts the fix's rounds separately and says it was re-cut at round 4. Head measured: d48018b80be11a2029e8492590a1a9e4b3a2eae9. refs/pull/2563/head was still that SHA at 23:17Z, when this was written. Merge base 1ebc737e7e187a1d45c62069ae8ab69c465db928. origin/main is now 5a755f53e. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current. Python is /opt/hpo/venv-ci (3.14.7). Worktrees were detached under one mktemp directory: head, base at the merge base, and one worktree per mutant.

## Findings

- The roster carry names the wrong directory for its control. The R10-BRIEFS-FOLD carry entry (origin/handoff/audit-r10-roster at c9905c607, carry[20], ev/carry-briefs-fold.txt) says the control is "dev/audit/rounds/round10 r10_night_folds_learners.py". The harness is at `dev/audit/harnesses/r10_night_folds_learners.py`, and no file by that name exists under dev/audit/rounds/round10 at the head. The precondition and its threshold are correct. A seat that follows the path as written will not find the control. Correct the path when the carry is folded into the D2 brief. Carry: R10-BRIEFS-FOLD
- The class enumerator still reads two of the four instances as open at this head. `dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py` prints `PROBE _async_learn_house_heat_loss FAIL ua_scale=0.925` and `PROBE heat_loss_refit FAIL refit_scale=0.937` at both ends (ev/enum.base.txt, ev/enum.wt.txt). The reasons are that `_ua_walk` re-implements the learner, and `probe_refit` builds samples with no `solar_radiation`, so neither probe reads the gate this diff adds. Separately, `probe_internal_gains` raises TypeError at the head (rc=1). A later D14 or D2 sweep that re-runs this enumerator as its barrier would read the class as still open. The probes need to drive the production symbols, or the barrier needs to name the companion instead. Carry: R10-BRIEFS-FOLD
- The body's `## Red checks` says "This head has not run in CI yet". It describes the check runs at 2f4758109. At this head every workflow has concluded. The only red is `nightly-status`: the same main red, from scheduled run 39563978649 (`slow` and `mutation-nightly`), and the body answers it by name. Carry: dismissed: the answer holds at this head, only the tense is stale
- The title says the fix will "net the solar term out of the replay", but the mechanism is a dark gate: sunlit intervals are excluded, and nothing is subtracted. The body's text describes the gate correctly. Carry: dismissed: title wording, the body states the mechanism

## Evidence

Item (1), the vacuous-test block from round 2, is closed. Each mutant was applied alone in its own detached worktree of the head and run as `PYTHONPATH=tests/hastub python3 tests/features.py` (ev/mut.*.diff, ev/features.*.summary.txt):
- unmutated head: `ALL 4290 FEATURE CHECKS PASSED`, rc=0
- coordinator.py:9796 `"solar": ctx._current_state.solar_radiation` -> `"solar": None`: `1 of 4290 FEATURE CHECKS FAILED`, rc=1. The failing check is "#2223: the coordinator's sunlit prediction settles with its sun, and the refit refuses it", which read `sunlit: sun None pair (0.0, 23.0)`.
- coordinator.py:9796 -> `"solar": 0.0` (my extra zeroing mutant): 1 FAILED, rc=1. Same check, `sun 0.0 pair (0.0, 23.0)`.
- coordinator.py:9718 `solar_radiation=pending.get("solar")` -> `None`: 2 FAILED, rc=1. That check plus "an accuracy sample records the sun its prediction was made under".

`tests/features.py` is in this diff's scoped selection: `closure.py select --diff 1ebc737e7` prints `MODE: SCOPED -- 29 script(s) run, 4 scoped out` with `RUN tests/features.py` (ev/closure-select.txt). So each mutant turns the scoped gate red.

The new check does not re-implement production code. It drives `_record_accuracy` twice under `dt_util.freeze`: a capture at 640 W/m2, then a settle in the dark. It then calls production `accuracy._refit_pair` on the stored sample. Its dark arm (capture at 0.0) must form a pair, so a refusal that comes from anything other than the sun fails the check.

I took the production code as unchanged since round 2 from three diffs, all at this head:
- `git diff --quiet 5860e02e4 HEAD -- custom_components tests/features.py` exits 0.
- `git diff --stat 2f4758109 HEAD -- custom_components` is empty.
- `git diff --name-only 57f0c9c77 1ebc737e7 | grep -E '^custom_components|^tests/features|^dev/governance/roles'` exits 1, as the body says.

Item (2), the physics:
- The fix is a gate. `thermal_model.is_sunlit_interval` returns `float(solar_radiation or 0.0) > HEAT_LOSS_MAX_SOLAR_W_M2`, with the gauge at 50.0 W/m2. That is the same gauge `_fold_internal_gains` already used as a literal `> 50.0`.
- The replay's modelled solar term is unchanged and is not subtracted a second time. A sunlit interval is simply not folded. That rules out a double count. It also rules out a sign error in the heat-loss step, which this diff does not touch.
- `_fold_solar_aperture` still runs before the gate, so the aperture learner keeps the daylight. P1 autumn `solar_scale.learn` reads 1.359 at both ends (ev/q1*.p1.txt).
- Units re-derived from production constants. 50 W/m2 x 10 m2 x 0.7 x 0.7 / 1000 = 0.245 kW. Over 0.5 h at 10 kWh/K that is 0.0123 K, matching const.py's 0.012 K. In two-zone mode it is 0.245 kW x 0.4 upper fraction x 0.5 h / 3.0 kWh/K = 0.0163 K, which is still under the 0.02 K the comment cites.
- `_zone_capacity` returns `_house_loss_terms(params)[1]`: the upper floor's mass in two-zone mode, else the room's. That is the ternary it replaces in both folds.
- `INTERNAL_GAINS_MIN_UA_CONFIDENCE` 0.9 against `1 - 0.98**n`: n=113 gives 0.898 and n=114 gives 0.9002, consistent with the body's 113-sample control arm.

The flat-irradiance null control, my run of the finder's harness `run_q1.sh` with irradiance identically 0 (ev/q1*.flat_uabias.txt):
- 55 of the 60 `flat.*.ua_bias` lines are identical at both ends. That covers every fix*, dark* and learn arm on P1..P5.
- The five that move are all `learn+gains` (P1 +0.0017 -> +0.0018, P2 +0.0017 -> +0.0018, P3 -0.0033 -> -0.0023, P4 +0.0088 -> +0.0078, P5 -0.0025 -> -0.0020). That is the internal-gains convergence gate, the only change in this diff that can act with no sun.
- `fixed_arm_spread` on the flat arms reads 0.0000 on P1..P5 at both ends.

The finder's harness, `dev/audit/rounds/round10/study-ident/run_q1.sh`, is the same file at both ends. I ran it at the base and at the head worktree, and each run printed 20 lines of rc=0 (ev/q1*.spread.txt). Every body figure re-derives exactly:
- autumn, P0..P5: 0.2691/0.3790/0.1405/0.3383/0.2383/0.2894 -> 0.0147/0.0219/0.0074/0.0205/0.0101/0.0168
- P1 at delivery 0.6: 0.3925 -> 0.0218; P1 at 0.4: 0.3962 -> 0.0224
- P0 at delivery 0.6: 0.2757 -> 0.0150; P0 at 0.4: 0.2677 -> 0.0154
- indep, P1..P5: 0.3918/0.1432/0.3432/0.2474/0.2902 -> 0.0230/0.0078/0.0218/0.0116/0.0178
- P1 autumn ua_bias: fix2.00 +0.2474 -> +0.0157, learn -0.0262 -> -0.0001, learn+gains -0.0332 -> -0.0111, none -0.0900 -> -0.0038
- P1 g0.40: fix1.00 +0.4423 -> +0.5833, with dark1.00 +0.5946 at both ends

The companion, `r10_night_folds_learners.py` (the head's copy, run from each worktree), exits rc=0 at both ends (ev/companion.*.txt):
- house.sunlit 8 -> 0, lower.sunlit 1 -> 0, refit.sunlit 192 -> 0
- dark arms 8/1/192 at both ends
- gains.unconverged 0.0990 -> 0.0000; gains.converged 1.9800 at both ends

The enumerator (ev/enum.*.txt):
- It prints 13 SEAM lines at each end, and the two lists are identical (`diff` rc=0).
- Its three CONTROL lines and PROBE-NULL read PASS at both ends.
- Probes: lower FAIL 0.925 gated=False -> PASS 1.000 gated=True. The house and refit probes read the same at both ends.
- Every seam is dispositioned in the body: 4 closed, 3 already guarded, 6 not applicable. No class-open seam.

Item (3), the carries:
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md` prints `CARRY-AUDIT: 8 finding item(s): 8 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (ev/carry_audit.txt). The roster ref was at c9905c607; the body's 23ef06dc6 is an ancestor of it.
- R10-BRIEFS-FOLD (stage not-started) carry[20] states the D2 step-5 gains-arm precondition with its control, cites #2563, and ends "Carry: R10-BRIEFS-FOLD". The body's verify command prints 1.
- R10-POLICY-FIXER-MD (stage not-started) carry[8] holds the fixer.md#2 Friction from #2563.
- Both owners are live groups on the roster.
- #2223 lists four sweep instances: `_async_learn_house_heat_loss`, `_async_learn_lower_floor_loss`, `heat_loss_refit` and `_fold_internal_gains`. All four are gated in this diff and measured by the companion. The issue's owed RCA, `dev/audit/rca/R10-N-confounded-learner.md`, is in the tree at the head. So the fix settles #2223.

Item (4), figures at this head:
- `structure.py`: `STRUCTURE RATCHET PASSED`, `seam_cut_total 716 <= 716` (ev/structure.txt). The budget file goes 718 -> 716 in the three-dot diff. That is a lowering, recorded in 6fda3166e with its reason.
- `score.py --diff 1ebc737e7`: `Architecture score: dS +0.3110 IMPROVES`, with duplication_copies 41 -> 40 and coord_footprint 2494 -> 2493 (ev/archscore.txt).
- Claims and version, three-dot against the merge base:
  - The diff names no VERSION, manifest, RELEASE_NOTES.md, golden or claim file.
  - `env_drift.py --claims-only`: `claims hygiene: origin/main ok`, rc=0.
  - `env_drift.py 1ebc737e7 --all`: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, rc=0 (ev/env_drift_*.txt).
- Merge: `git merge-tree --write-tree origin/main d48018b8` (origin/main 5a755f53e) exits 0 with tree 5cb6d6bf7. Its stderr is `LEDGER-MERGE: resolved tests/closures.json`, and no MERGE-CLAIM line appears (ev/merge-tree.txt).
- I did not re-run the body's scoped-gate count (`31 TEST SCRIPT(S) PASSED`), per the contract: cite CI's heavy runs. I re-derived its selection line (29 run, 4 scoped out). CI's `fast (3.14)` and `coverage` are success at this head.
- I did not re-run the alternatives, vent-window or sun-transient harnesses this round. Round 2 re-derived them at 2f4758109, and the production code and those harnesses are unchanged since.

CI at this head, from the commit's check-runs API, read after every run had concluded (ev/check_runs.txt, 49 runs):
- `nightly-status` is the one red. It grades main's scheduled run 39563978649 (`slow`, `mutation-nightly`), and the body names and answers it. It is not a required check and does not block.
- Everything else is success or skipped, including fast (3.14), coverage, coverage-ratchet, typing, browser, pr-contract x2, arch-score x2, budget-raise-gate x2, env-matrix, policy-docs and closure-scope.
- The `mutation` log reads `MUTATION TABLE PASSED`: 0 survivors of 6 evaluated, PIN RE-VERIFICATION 6 reproduced, baselines rc=0 for env_drift, features and entities, and the null control survived (ev/mutation_lane.txt). So the green is not an inconclusive table.

VERSION, the manifest version and the RELEASE_NOTES.md heading are untouched.
