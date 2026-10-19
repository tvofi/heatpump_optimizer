Fix review: merge 91a3f77c9f968341a578d46277c0ff0e08c20dcc

bus-nonce: 09edb010cc4f5e5095efed4f71dd5d97

Round 3. Round 1 (comment 6253502824) blocked c3a25d2ae. Round 2 (comment 6255525601) returned merge at 86258e159. This head is 86258e159 plus merges of origin/main (#2408, #2411, #2399, then 913ce1ff5). Measured head: 91a3f77c9f968341a578d46277c0ff0e08c20dcc (ev/HEAD). It was still the PR head after CI concluded. Merge base: 913ce1ff5. The role contract is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## Resolution delta (the only new authored content since round 2)
- I re-merged 86258e159 with origin/main using `git merge-tree` and the claimnotes driver installed. Only one path differs from the head: `tests/golden/claimed_drift.txt`. The driver printed `MERGE-CLAIM: refused` on it (both sides rewrote the claim list), and `LEDGER-MERGE: resolved tests/closures.json` (ev/remerge.stderr). Every other path the main merges touched merged cleanly. That includes #2411's optimizer.py, which is 339 lines of main's change.
- The hand resolution (ev/claims_resolution.txt):
  - The head claims 41 fixtures. These are exactly 86258e159's 41, with 0 missing and 0 added.
  - 0 of main's comment lines and 0 of the branch's comment lines are missing.
  - `claims-for: 7.0.0` equals VERSION.
  - CI fast at this head prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 913ce1ff5` and `NO STALE FIXTURE: 56`. env-matrix is green. Locally, `env_drift.py --claims-only` prints `claims hygiene: origin/main ok`.
  - So every moved fixture is claimed, and every claim moved.
- `git merge-tree --write-tree origin/main 91a3f77c9` exits 0 (ev/merge-tree.txt).

## RESULT lines (mine)
- **Finder's harness** `dev/audit/rounds/round10/D2/s2/cop_laws.py`. I ran the head's copy in each tree; it is byte-identical to main's (ev/finder_*.txt).
  - main 913ce1ff5: `dhw_mode_ratio_max=1.4346` at (7,65), `dhw_mode_dev_cells=41 max=0.4346`, `dhw_below_ref_boost_max=1.2000`.
  - head: `1.0000`, `max=0.0000`, `1.0000`.
  - `--perturb` reads 1.0000 at both ends.
  - The flat companions are identical at both ends: monotone violations 0/0, derate 0.55..1.0, `batch_scalar_cop_mismatch=0 of 63570`.
- **Mutation proof, D2-s2-01.** I put main's thermal_model.py back into a `git archive` export of the head.
  - Result: `3 of 10 FEATURES BLOCK FAILED`, with the body's figures (1.4346; direct 2.66 vs law 1.8541518628970441; boost 1.2000).
  - The unmutated export prints `ALL 10 FEATURES BLOCK PASSED` (ev/features_block_M*.txt).
- **Mutation proof, ftol check.** Each mutant is an export of this head, edited at the ftol sites, which are now at optimizer.py:855 (restart), 1004 (multi-start refinement) and 4486 (space-only) (ev/opt_M*.txt).
  - MA (all three sites at 1e-3): `FAIL ... [ftol 1e-6 81.60 vs loosened 1e-3 both sites 81.60 (0.00% gap, bound 0.84%)]`.
  - MB (1004 alone at 1e-3): `FAIL ... 81.54 vs 81.60 (0.07% gap)`.
  - MC (all three at 1e-2): `FAIL ... 83.10 vs 81.60 (-1.84% gap)`.
  - The ftol figures match the body to the digit. The total failure counts do not: I got 3, 2 and 3 of 84, and the body quotes 2, 2 and 4. The body says its mutants were taken at e4f5a41e2's tree, before #2411's optimizer changes merged, so the companion failures differ. The ftol check fails in every mutant, and that is the claim.
  - M0 (the head, unmutated): `stop-prod 80.22`, `stop-rule 81.60`, `ALL 84 OPTIMALITY CHECKS PASSED`.
- **Kernel points.** CI kernel-points at this head (jobs 117907732276/085/296/253) all succeeded. The native leg (AMD EPYC 7763, core Haswell) reads:
  - `stop_prod_cost=80.22`, `stop_both_1e3_cost=81.60`, `stop_loose_1e3_cost=81.54`, `stop_both_1e2_cost=83.10`, `stop_tight_1e8_cost=80.22`.
  - `stop_check_gap_pct=+1.687` against the 0.84 bound, and `stop_repeat_identical=1` (ev/kernel_points_native_ci.txt).
  - Accelerate is still owed by a Mac seat, as the body discloses.
- **calls_floor bound.** I exec'd the head's `coverage_floors` with floor 18 and calls_floor 6/7/10/14/absent (ev/calls_floor_driver.txt).
  - Head: (18,6), (18,7), (18,7), (18,7), (18,7). With no override: (40,15).
  - Mutant `share(SCENARIO_WORK_MIN_COVERED)`: (18,10) and (18,14). That is the round-1 defect, and it is closed here.
- **Class.** I ran each tree's own `enumerate_p2.py` (ev/p2.txt).
  - `F3_cop_law_fork`: 3 at main (compute_cop, compute_cop_dhw, _batch_cop) and 2 at head (compute_cop, _batch_cop).
  - `--perturb`: before=2, after=3, moved=1.
  - No `dhw_penalty` is left. The remaining `cop_flow_carnot` sites are on the space circuit (ev/seam_rule_head.txt). The class is closed.
- **Step 4, re-derived on this Linux runner.** Local stress at head against 913ce1ff5 (ev/stress-head.log, ev/step4_ratios_head.txt):
  - `solver work: 18 of 54 ... 36 re-planned by this branch, 0 new here, 0 dropped` and `production calls: 6 of 20`. CI fast prints the same two lines.
  - 36 re-planned scenarios. The largest ratio is 1.282 (light_new/winter, 646 vs 504) and the smallest is 0.454. All are under 3.0x.
  - I could not re-derive the body's per-scenario evaluation counts (e.g. flat/1z/dhw 628 vs 558; here 570 vs 452). They come from the fixer's arm64 seat against 0dac0bf87, and evaluation counts depend on the platform. I verified the bound, not those numbers.
- **Other checks at this head:**
  - `Architecture score: dS +0.0000 NULL`.
  - budget_raise_gate prints `RAISE ... calls_floor: override added at 6`, `... floor: override added at 18`, `budget_raises=2`, `REFUSED: no decisive review by tvofi`.
  - VERSION, the manifest and RELEASE_NOTES are untouched in the three-dot diff.

## The body's arm64 attribution, verified on Linux x86_64 (Intel Xeon, numpy 2.4.6, Python 3.14.7)
- `tests/optimality.py`:
  - main 913ce1ff5: `ALL 84 OPTIMALITY CHECKS PASSED`.
  - head: `ALL 84 OPTIMALITY CHECKS PASSED`.
  - `one|summer_negative|shoulder` reads `ladder +10.5539% claimed=True` and `ok ... a recorded claim still has a gap (not stale)` at both ends (ev/optimality-*.log).
- `tests/stress.py` with GOLDEN_REF=913ce1ff5:
  - head: `ALL 113 STRESS CHECKS PASSED`, `ok shoulder: cheaper than holding the setpoint`.
  - main: `ok shoulder: cheaper than holding the setpoint`. Main has 7 failures, and they are exactly the self-baseline ones the body names: `913ce1ff5 IS this commit`, no worktree, 0 of 54 judged.
- Both reds are absent on Linux at main and at head, and they read identically between main and head on the fixer's arm64 seat. The attribution to arm64 and not to this diff holds.

## CI at this head (ev/check-runs.tsv, check-runs API; every run has concluded)
- `fast (3.14)` succeeded with `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT AND NOT RUN` (ev/fast.log). Its lines include `ALL 84 OPTIMALITY`, `stop-prod 80.22`/`stop-rule 81.60`, `ALL 113 STRESS` and NO UNCLAIMED/NO STALE 56.
- mutation, coverage, closures, env-matrix, browser, typing, CodeQL, wave-script, delivery-status, instrument-self-tests and the kernel-points ×4 all succeeded.
- The only red is `budget-raise-gate` (two runs), at `REFUSED: no decisive review by tvofi`. It is red by design. It is named and answered in `## Red checks` and `## Raise justification`. A `pr-contract` run started at 05:40:26Z, after that red concluded at 05:39:10Z, and succeeded. Rule 11 is met.

## Step 14: the two raises (floor 18, calls_floor 6)
- Earned by the change: the measured counts at this head are 18 and 6, on CI and on this runner, against main's literal (40,15), with zero headroom. CI ties every uncovered scenario to "re-planned by this branch", with none new and none dropped. If the mechanism is removed (main's thermal_model.py restored), nothing re-plans and the override is unneeded. So the movement is the fix's.
- The payments:
  - (1) narrowing the law is the accepted defect.
  - (2) splitting moves all 36 to whichever half carries the law.
  - (3) the baseline is computed beside the run.
  - (5) the share rule alone cannot hold 18 and 6.
  - (4) a per-scenario work statement in stress.py instead of a floor is the one real alternative. The ruling (#201 6240984157 step 3, under mandate 6175172275) chose the override, and the body states step 4 by hand. I accept the refusal as the ruling's.
  - archscore reads only custom_components, so dS 0 is honest.
- I hunted for a missed payment and found none that improves the code.
- I judge the justification unpayable. The raise still needs tvofi's approving review, as do the code-owned tools/policy/budget_raise_gate.py and the workflow files. That is not a reviewer block.
- Observation (not blocking): nothing expires the override at merge. `stress.py`'s docstring says "for THIS branch", but on main it keeps every later PR's floors at (18,6) until the next stress re-record drops it. That is the #1207 override's precedent (HANDOVER: "dropped by the next re-record"), so this is the existing rule, not a defect of this diff.

## Other rules
- The head SHA in the body equals the measured head.
- Forward-carry is `none`, and that is plausible: the cell re-selection is the check's own.
- The architecture of the added lines is sound: one call, `_cop_law(outdoor, humidity, dhw_temp)`, and `_cop_law`'s `max(cop, 1.0)` keeps the #928 resistive floor.
- Instrument disclosure: the ev/calls_floor_driver.txt driver and ev/step4_ratios_head.txt parser are mine. The finder's harness and the body's harnesses were used as committed.
