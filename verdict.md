Fix review: blocked 829ea7c7238d62293a58bb9d9625e844ac7fd09d carry-missing: not carried to R10-BRIEFS-FOLD

PR #2563, group R10-NIGHT-FOLDS, fix review (cloud reviewer seat). Head measured: 829ea7c7238d62293a58bb9d9625e844ac7fd09d (refs/pull/2563/head still points there when this was written). Merge base 3688cf25977ca71b4406be942df9592577d9b42e = origin/main. The diff to `dev/governance/roles/` between the merge base and origin/main is empty, so the contract is current. Detached worktrees: head /home/user/rev, base /home/user/base. Python is /opt/hpo/venv-ci (numpy 2.4.6, scipy 1.17.1).

## Blocking

Step 10, the forward-carry. The body's `## Forward-carry` line 1 (`Carry: R10-BRIEFS-FOLD`) records a finding this PR produced: the D2 step-5 class barrier "must drive the learners together: the gains arm needs a converged level and a genuine gain". That finding is real and changes the later stage:
- At this head, a gains probe driven at an unconverged level no longer measures anything. The sweep enumerator's own `probe_internal_gains` dies with `TypeError: 'NoneType' object is not iterable` (ev/enumerate.rev.out).
- The companion's `gains.converged` arm is the control that works (1.9800; ev/r10_night_folds_learners.rev.out).

So the precondition must reach the stage's brief before this PR merges (`finding-propagation.md`, Enforcement). It is not there:
- The body names `dev/programme/rosters/wave-r10-groups.json` as the destination but gives no `handoff/audit-r10-roster` SHA.
- At roster head 31e162fd3a1207db596539b2330af1d274c36c85, R10-BRIEFS-FOLD (stage not-started) has 20 carry entries and a brief. Its brief carries only the generic "D2 step 5 tests learners under error in the other covariate" (from the group brief, which predates this PR). No carry states the converged-level / genuine-gain precondition or its control (ev/roster_R10-BRIEFS-FOLD_at_31e162fd3.json).
- `git grep -i -E "converged level|genuine gain|drive the learners together"` over dev/programme, dev/governance and .claude/workflows finds nothing on the roster branch, on origin/main or at the head.

To clear it: append the carry to R10-BRIEFS-FOLD on `handoff/audit-r10-roster` (tools/audit/seat/roster_edit.py append-carry). Write it as a precondition with its control: the gains arm runs at a converged heat-loss level with a genuine gain, and the control is `r10_night_folds_learners.py`'s `gains.converged.rel_dev` > 0.05 with `gains.unconverged.rel_dev` 0.0000. Then name the roster SHA in the body. Everything else below verified, so a re-review after the carry lands needs only step 10 plus the carry predicate.

## Verified (RESULT lines are mine, at base 3688cf259 and head 829ea7c72)

Step 2, the finder's harness. I ran `dev/audit/rounds/round10/study-ident/run_q1.sh` at both ends: 20/20 `rc=0` each (ev/q1base, ev/q1head, ev/q1*.spread.txt). Every `fixed_arm_spread` in the body re-derives exactly:
- P0 autumn 0.2691 -> 0.0147
- P1 autumn 0.3790 -> 0.0219
- P2 autumn 0.1405 -> 0.0074
- P3 autumn 0.3383 -> 0.0205
- P4 autumn 0.2383 -> 0.0101
- P5 autumn 0.2894 -> 0.0168
- delivery arms: P1 g0.4 0.3962 -> 0.0224, P1 g0.6 0.3925 -> 0.0218, P0 g0.4 0.2677 -> 0.0154, P0 g0.6 0.2757 -> 0.0150
- indep: P1 0.3918 -> 0.0230, P2 0.1432 -> 0.0078, P3 0.3432 -> 0.0218, P4 0.2474 -> 0.0116, P5 0.2902 -> 0.0178
- P1 ua_bias: fix2.00 +0.2474 -> +0.0157, learn -0.0262 -> -0.0001, learn+gains -0.0332 -> -0.0111, none -0.0900 -> -0.0038
- P1 g0.4: fix1.00 +0.4423 -> +0.5833, against base dark1.00 +0.5946, so the body's commanded-power-confound reading holds.

Step 3, the null control. The flat-irradiance arm reads `fixed_arm_spread` 0.0000 on P1..P5 at both ends.

Step 14, whether the gain is earned by the mechanism:
- Perturbation: the head with HEAT_LOSS_MAX_SOLAR_W_M2 set to 1.0 reads P1 autumn spread 0.0000 and fix2.00 +0.0026 (ev/thr1.P1.autumn.out).
- The base's study dark arm at IDENT_DARK_W_M2=50 reads -0.0062 / +0.0011 / +0.0157, exactly the head's fix0.50 / 1.00 / 2.00 (ev/base.dark50.P1.autumn.out).
- So the head's movement is the gate's, and the residual 0.0219 spread (against the brief's "at most 0.0001") is wholly the 50 W/m² choice. The RCA prescribes that threshold ("the irradiance gate `_fold_internal_gains` already uses"), and the residual sits within the RCA's 5 % bar: the largest delivery-1.0 |bias| at the head is 1.6 %. The body does not state this attribution; it is recorded here.

The companion `r10_night_folds_learners.py` (copied into the base worktree) re-derives at both ends:
- house.sunlit 8 -> 0, lower.sunlit 1 -> 0, refit.sunlit 192 -> 0
- gains.unconverged 0.0990 -> 0.0000
- dark arms identical (8 / 1 / 192), gains.converged 1.9800

`r10_night_folds_alternatives.py` output is identical at both ends and matches the body's figures. `r10_vent_sun_transient.py` is identical at both ends and matches the body.

Steps 1 and 14, mutants (mine). Each was applied alone to a detached worktree of the head and driven through `PYTHONPATH=tests/hastub tests/features.py`; the unmutated head reads ALL 4284 FEATURE CHECKS PASSED. All five are killed:
- house sunlit gate -> if False: rc=1, 3 checks (sunlit takes no sample / still the aperture learner's / detector fed)
- lower sunlit gate -> if False: rc=1, 1 check
- refit `_refit_pair` sunlit gate -> if False: rc=1, 3 checks
- convergence clause `or settled < INTERNAL_GAINS_MIN_UA_CONFIDENCE` deleted: rc=1, 1 check ("the hour shape waits for the heat-loss level")
- dark gauge 50 -> 1000: rc=1, 9 checks

Step 6, the class. The enumerator (sha1 9f7e1637…) returns an identical 13-SEAM list at both ends. Every seam is dispositioned in the body: 4 instances closed in the diff, 3 guarded, 6 not applicable. Its house and refit probes still FAIL at the head, and I confirmed the body's reason by reading the probes: `_ua_walk` is a re-implementation, and `probe_refit` builds samples with no `solar_radiation`. No class-open seam.

Steps 4 and 5. `env_drift.py --claims-only`: ok. No golden or claim file is touched. VERSION, the manifest and RELEASE_NOTES are untouched.

Step 13. `git merge-tree --write-tree origin/main 829ea7c72`: rc=0 (tree fae4bfcc2), no conflict.

Structure: `tests/structure.py` passes at the head. seam_cut_total reads 718 at the base and 716 at the head; this is a lowering, earned by the guard merge and the helper moves. `score.py --diff 3688cf259` prints `dS +0.3110 IMPROVES`: duplication_copies 41->40 (two identical capacity choices became one helper) and coord_footprint 2494->2493. `_zone_capacity` returns the same values as the code it replaces (`_house_loss_terms`: upper mass in two-zone, else room).

Step 11, CI at this head (check-runs API, ev/check_runs.txt). Two checks are red, and the body answers both:
- `mutation`: the log reads `MUTATION TABLE REFUSED … 13 of them added by this diff`. That matches the body's twelve sites / thirteen mutants under `## Unpinned sites`. The M09 equivalent-mutant triage holds: `1-0.98**n` never equals 0.9.
- `nightly-status`: main's, per the role file. The diff reaches no replay-status input.

Everything else that has concluded is green, including fast (3.14), coverage, typing, browser, pr-contract (×2) and arch-score. Still in progress when written: closures and mutation-pins (1..3). This verdict does not turn on them.

Step 12: refs/pull/2563/head = 829ea7c72 when written.

## Non-blocking (each with a destination)

- const.py's comment and the body say "at the shipped aperture product the modelled solar gain at 50 W/m² is 0.30 kW". That does not re-derive. Production `ThermalModel(ThermalParameters()).compute_solar_gain(50.0)` = 0.2450 kW (10 m² × 0.7 × 0.7), which over a half hour at 10 kWh/K is 0.0122 K (ev/solar50.txt). The conclusion, under 0.02 K, still holds; the quoted figure is wrong by 22 %, in the conservative direction. Fix the figure in the same push as the carry SHA. Carry: R10-NIGHT-FOLDS
- `r10_night_folds_learners.py`'s header expects "gains.unconverged ~1.0" at the baseline; the base measures 0.0990, which the body itself reports correctly. Correct the header's expectation. Carry: R10-NIGHT-FOLDS

Round: first review by this seat.

bus-nonce: 4781a1280f18f8b3240d780b7dc421bf
