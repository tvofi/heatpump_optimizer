Fix review: merge 86258e159d6e18b41aa0edafc79c6b8921d5c4dc

bus-nonce: 59d82ae446918d31cd3e4a5b5c6a5422

Round 2. Round 1 (comment 6253502824) blocked c3a25d2ae: ci-red on the ftol check, steps 2 and 4 pending, and the calls_floor soundness defect. All three are resolved at this head. Measured head: 86258e159d6e18b41aa0edafc79c6b8921d5c4dc (ev/HEAD); it is still the PR head at posting. Merge base: 07a09406a. The roles contract is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## RESULT lines (mine)
- **Finder's harness**: dev/audit/rounds/round10/D2/s2/cop_laws.py, the head's copy run in each tree (ev/finder_*.txt, ev/finder_*.RESULT). Base 07a09406a: `dhw_mode_ratio_max=1.4346` at (7,65), `dhw_mode_dev_cells=41 max=0.4346`, `dhw_below_ref_boost_max=1.2000`. Head: `1.0000`, `max=0.0000`, `1.0000`. Every other RESULT line is identical at both ends.
- **Mutation proof, D2-s2-01**: done in a `git archive` export of the head with base thermal_model.py put back. Result: `3 of 10 FEATURES BLOCK FAILED`, with the body's three FAIL lines and figures (1.4346; 2.66 vs 1.8541518628970441; boost 1.2000). The unmutated export prints `ALL 10 FEATURES BLOCK PASSED` (ev/features_M*.txt).
- **Mutation proof, ftol check** (tests/optimality.py, each in an export; ev/opt_*.txt):
  - M0: `stop-prod 80.22`, `stop-rule 81.60`, `ALL 84 PASSED`.
  - MA (all three sites at 1e-3): ftol FAIL, `81.60 vs 81.60 (0.00% gap, bound 0.84%)`, 2 of 84.
  - MB (the multi-start refinement site, optimizer.py:836, at 1e-3): FAIL, `81.54 vs 81.60 (0.07%)`, 2 of 84. The second failure here is the two|winter_typical|winter_cold gap check, not the iteration-budget one.
  - MC (all three at 1e-2): FAIL, `83.10 vs 81.60 (-1.84%)`, 4 of 84.
  - All match the body.
- **Observation (not blocking)**: optimizer.py:4318 (`_optimize_space_only`) at 1e-3 alone leaves the check green (ev/opt_MB_site4318_inert.txt). The check is a DHW-enabled two-zone solve and does not route through the space-only path. That scope predates this PR, and the body's mutants do not claim that site.
- **Kernel matrix (step 2)**:
  - k1725 at this head, native here: `stop_prod_cost=80.22`, `stop_both_1e3_cost=81.60`, `stop_loose_1e3_cost=81.54`, `stop_both_1e2_cost=83.10`, `stop_tight_1e8_cost=80.22` (objective 106.4690 both), `stop_check_gap_pct=+1.687`, `stop_repeat_identical=1` (ev/k1725_head_native.txt).
  - The CI kernel-points matrix on this push (native = AMD EPYC 9V45, Haswell, Sandybridge, Nehalem; jobs 117791480222/203/037/263; ev/kp_*.log) reads the same seven values on every leg. That settles the body's Pending CI-native item: +1.687 against the 0.84 bound. The body's other Pending item, Accelerate on a Mac seat, remains disclosed and open.
- **calls_floor bound (round-1 defect)**: a driver that execs the head's `coverage_floors` (ev/calls_floor_driver.txt), with floor 18 and calls_floor 6/7/10/14/absent:
  - Head: (18,6), (18,7), (18,7), (18,7), (18,7).
  - Mutant reverting the predicate to share(literal): (18,10) and (18,14). That is the round-1 defect.
  - The stress self-check feeds share(18)+3=10 and requires the share rule, so it fails under that mutant by construction.
- **tests/entities.py conflict union** (ev/entities_union.txt), over the merge base 106af95a3 of 8100b5e55 and 07a09406a:
  - Branch side +19/-0, main side +42/-0. 0 lines missing from the merged file on either side.
  - Merged over base: +61/-0, and the added lines equal the union of both sides' added lines (multiset).
  - Merged vs main: +19. Merged vs branch: +42.
  - `tests/entities.py` at head: `ALL 2350 ENTITY CHECKS PASSED`. Both sides' checks are kept.
- **Class**:
  - enumerate_p2: `F3_cop_law_fork` is 3 at base (compute_cop, compute_cop_dhw, _batch_cop) and 2 at head (compute_cop, _batch_cop). `--perturb before=2 after=3 moved=1` (ev/p2.txt).
  - The seam grep has no `dhw_penalty` left; the remaining `cop_flow_carnot` hits are space-circuit sites (ev/seam_rule_head.txt).
- **Claims**: `env_drift.py --all 07a09406a`: `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56` (this dev box's value-only differences are reported, never failed). `--claims-only`: ok. CI env-matrix is green.
- **Other checks at head**:
  - closure select: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
  - `Architecture score: dS +0.0000 NULL`.
  - budget_raise_gate self-test: `239 checks, 0 failed`.
  - RULES-SYNC ok.
  - VERSION, the manifest and RELEASE_NOTES are untouched.
- **Merge check**: `git merge-tree --write-tree origin/main(07a09406a) <head>` exits 0. No MERGE-CLAIM line.

## CI at this head (ev/check-runs.tsv, read from the check-runs API)
- **`fast (3.14)` is green** (ev/fast.log):
  - `30 TEST SCRIPT(S) PASSED; 4 SCOPED OUT`.
  - optimality: `ALL 84`, `stop-prod 80.22` / `stop-rule 81.60`.
  - features: `ALL 4179`. entities: `ALL 2350`. stress: `ALL 113`.
  - `solver work: 18 of 54 … 36 re-planned by this branch, 0 new here, 0 dropped`.
  - `production calls: 6 of 20 … against 07a09406a`.
- **Step 4 re-derived from this head's log** (ev/stress_ratios_head.txt): 36 re-planned scenarios, largest ratio 1.310 (winter/pv, 938 vs 716), smallest 0.422; 15 grew, 12 shrank, 9 equal. All are under the 3.0x factor. The body's per-scenario table cites c3a25d2ae's log and says so; its counts at this head match.
- **mutation green**: `0 survivor(s) of 1 evaluated` (thermal_model.py:2217 RETURN_DEL killed by env_drift.py). coverage and CodeQL are green.
- **Reds, none of them this PR's to fix**:
  - `wave-script`: the merge-subject-pr DIVERGENT on "#2401"/"#2379" merge subjects, which is main's 5756f2b1 cause.
  - `pr-contract` (run 117792232969): only error is `wave-script is red and ## Red checks does not name it`, the same cause.
  - `delivery-status`: OVERDUE on main's #2413/#2412/#2407 rows.
  - `budget-raise-gate`: `RAISE coverage_floor_override.calls_floor: None -> 6`, `floor: override added at 18`, `REFUSED: no decisive review by tvofi`. This is red by design. The body's `## Red checks` and `## Raise justification` answer it, and it waits on tvofi's approving review, which is not a reviewer block. tools/policy/budget_raise_gate.py and the two workflow files are code-owned, so they also need tvofi.

## Step 14
The raise's counts (18, 6) are the fast lane's measured counts at this head, with zero headroom, and are earned by the re-plans. CI ties every uncovered scenario to "re-planned by this branch". The payments the body lists are as judged in round 1, and I found no missed one. The ftol bound (0.84 = half of +1.687) is re-derived on all five kernels measured.

## Nit (optional)
coordinator.py's docstring states "0.62x the space curve" and "1.35x higher" without an outdoor temperature. Those hold at 7 °C and above (ev/coordinator_docstring_figs.txt). At 0 / -5 / -15 °C the ratio is 0.678 / 0.710 / 0.761 and old/new is 1.240 / 1.183 / 1.104.
