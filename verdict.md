Fix review: blocked 2f47581094ad66bd76ccfa6efff92aef90036aeb vacuous-test: the refit's irradiance record (coordinator.py:9796 pending "solar") survives features.py and the whole scoped gate

PR #2563, group R10-NIGHT-FOLDS. Fix review, round 2 by the cloud reviewer seat; the PR's round 1 block is the hpo-approver comment at 829ea7c72. Head measured: 2f47581094ad66bd76ccfa6efff92aef90036aeb. Its tree, df75d6ebc, is identical to the body's measured code head 9f0ed12e7, so the body's figures apply to this head. Merge base 57f0c9c77 = origin/main. The diff to `dev/governance/roles/` from the merge base to origin/main is empty, so the contract is current. Python is /opt/hpo/venv-ci. Worktrees: head /home/user/rev, base /home/user/base, one mutant worktree each under /home/user/mut_*.

## Blocking

Step 1, the mutation proof. The body says `accuracy.heat_loss_refit` "records the interval's irradiance on `AccuracySample` and refuses a sunlit pair". The refusal is tested, but the recording is not. This diff adds the recording in two places:
- coordinator.py:9796 captures `"solar": ctx._current_state.solar_radiation` into the pending interval.
- coordinator.py:9718 writes it to the sample as `solar_radiation=pending.get("solar")`.

I changed line 9796 to `"solar": None` (ev/mut.m6_plumb.diff):
- `tests/features.py` reads `ALL 4289 FEATURE CHECKS PASSED`, rc=0 (ev/mut.m6_plumb.out).
- The whole scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=57f0c9c77 PYTHONPATH=tests/hastub bash tests/run.sh`, reads `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`, rc=0 (ev/mut.m6_plumb.gate.out).

Under that mutant every production accuracy sample carries `solar_radiation=None`. `is_sunlit_interval(None)` reads as dark, so the drift refit admits every sunlit pair again: exactly the base behaviour #2223 closes. Every refit check (`_refit_pair`, `heat_loss_refit`) builds `AccuracySample` by hand, and so does the companion's `refit.*` arm (`r10_night_folds_learners.py` lines 114-123). So the companion's `refit.sunlit.pairs` 192 -> 0 measures the pair gate, not the production refit. `mutation` cannot see this either: the diff's ledger pins cover only CMP_BOUND, GUARD_OFF and RETURN_DEL sites, and this is a value in a dict literal. The lane was still in progress when written.

To clear it, add a check that drives the coordinator's own path: prediction capture, then settle into `_accuracy_tracker` with a sunlit `_current_state.solar_radiation`. It must assert that the stored sample carries the irradiance, or that `heat_loss_refit` over the tracker's samples refuses the pair. It must fail under the mutant above and under `solar_radiation=None` at line 9718. Carry: R10-NIGHT-FOLDS

## Prior blocking items

- Round 1's `carry-missing: not carried to R10-BRIEFS-FOLD` is repaired. At origin/handoff/audit-r10-roster 23ef06dc6cc719917e593174b3a12977cd054071, R10-BRIEFS-FOLD's carry list holds the D2 step-5 gains-arm precondition, written as a precondition with its control: `gains.converged.rel_dev > 0.05` with `gains.unconverged.rel_dev 0.0000`. The body's verify command prints 1. The body still names no roster SHA, only the ref. Name it in the next body push. Carry: R10-NIGHT-FOLDS
- The pr-contract / CARRY-AUDIT refusal at baa01ed85 is repaired. Both `pr-contract` runs at this head are success. My own run, `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md`, prints `7 routed, 0 unrouted, 0 bad destination(s)`.
- Round 1's two non-blocking notes are repaired. const.py now reads 0.245 kW and 0.012 K, which matches my 0.2450 kW. The companion header no longer expects `gains.unconverged ~1.0`. Carry: dismissed: repaired at this head (item 4116031f)

## Verified (my RESULT lines, base 57f0c9c77 and head 2f4758109)

Step 2, the finder's harness. `run_q1.sh` ran 20/20 with rc=0 at each end (ev/q1.base, ev/q1.rev, ev/q1.*.spread.txt). Every `fixed_arm_spread` the body quotes re-derives exactly:
- autumn P0..P5: 0.2691/0.3790/0.1405/0.3383/0.2383/0.2894 -> 0.0147/0.0219/0.0074/0.0205/0.0101/0.0168;
- delivery arms: P1 0.6 0.3925 -> 0.0218, P1 0.4 0.3962 -> 0.0224, P0 0.6 0.2757 -> 0.0150, P0 0.4 0.2677 -> 0.0154;
- indep P1..P5: 0.3918/0.1432/0.3432/0.2474/0.2902 -> 0.0230/0.0078/0.0218/0.0116/0.0178;
- P1 ua_bias: fix2.00 +0.2474 -> +0.0157, learn -0.0262 -> -0.0001, learn+gains -0.0332 -> -0.0111, none -0.0900 -> -0.0038;
- P1 g0.40: fix1.00 +0.4423 -> +0.5833, with dark1.00 +0.5946 at both ends.

Step 3, the null controls:
- The flat arms read 0.0000 on P1..P5 at both ends.
- The companion (ev/learners.*.out, rc=0 both ends) reads:
  - house.sunlit 8 -> 0, lower.sunlit 1 -> 0, refit.sunlit 192 -> 0;
  - dark arms 8/1/192 at both ends;
  - gains.unconverged 0.0990 -> 0.0000, gains.converged 1.9800 at both ends.
- The alternatives harness is identical at both ends (`cmp` rc=0), with net_of_ua_part 0.0000 and ridge0.02 1.0000/0.7143, ridge1.00 0.0500/0.0476.
- Carry controls:
  - vent: no-window 4/4 `false_share=0.000` at both ends; 300 W/K `nan` 0/60 at both ends; 150x4h `nan` 6/20 -> 7/20. The one arm that moves, `seed1.onoff.g1.0.ua1.0.vent150x4h`, goes from `detect_h=3.75` to `nan`, as the body says.
  - sun transient: identical at both ends, `end_tripped=False` 6/6.

Steps 1 and 14, the mutants. Each ran alone in its own head worktree through `PYTHONPATH=tests/hastub tests/features.py`. The unmutated head reads ALL 4289 PASSED (ev/mut.*.out, ev/mut.*.diff).
- Killed:
  - 9041 `<` -> `<=`, the body's site: 1 FAIL, "on the threshold False, one sample under False", as the body says;
  - convergence clause deleted: 2 FAIL;
  - house sunlit gate off: 3 FAIL;
  - lower sunlit gate off: 1 FAIL;
  - refit `_refit_pair` gate off: 3 FAIL;
  - internal-gains sunlit gate off: 1 FAIL;
  - dark gauge 50 -> 1000: 9 FAIL.
- Survived: the pending `"solar"` capture, which is the blocking item above.

Step 6, the class. My run of the base's own enumerator copy (sha1 9f7e1637…) returns 13 SEAM lines, and the head's list is identical (`diff` rc=0). Its CONTROL lines and PROBE-NULL read PASS. The probes match the body:
- base: house 0.925, lower 0.925 gated=False, refit 0.937, gains 0.820;
- head: lower PASS 1.000 gated=True, house and refit unchanged, and `probe_internal_gains` raises TypeError (rc=1).

Every seam is dispositioned in the body.

Steps 4 and 5:
- `env_drift.py --claims-only` reads ok, rc=0.
- The three-dot diff names no VERSION, manifest, RELEASE_NOTES, golden or claim file.

Step 13. `git merge-tree --write-tree origin/main 2f47581` exits 0 with tree df75d6ebc; the head already contains origin/main.

Step 14, structure and score:
- `structure.py` passes, with seam_cut_total 718 at the base and 716 at the head. The budget is lowered 718 -> 716, not raised.
- `score.py --diff 57f0c9c77` prints `dS +0.3110 IMPROVES`: duplication_copies 41 -> 40, coord_footprint 2494 -> 2493.

Step 11, CI at this head, from the commit's check-runs API (ev/check_runs.txt, read 19:40Z):
- `nightly-status` is the only red. It is main's, and the body answers it.
- `mutation` and `closures` were still in progress, so I did not re-measure the mutation table (the contract: cite CI's heavy runs). This verdict does not turn on them.
- Everything else concluded green or skipped, including fast (3.14), coverage, typing, browser, policy-docs, env-matrix, pr-contract x2, arch-score and budget-raise-gate.

Step 12: the PR head was 2f47581094ad66bd76ccfa6efff92aef90036aeb when written.

Round: second review by this seat. The body counts this as round 4 of the fix.

bus-nonce: 7e7638c43a22772a346ee4c2283f8832
