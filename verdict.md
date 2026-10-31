Fix review: merge a6be5baa55e41507a7dec1ffec7b88a660167e15

bus-nonce: cac6419868d56fedccaf3c4e7b31aa7e

## Round

This is the fourth round, a delta review from the last merge verdict at 958b4af8eee134728986d92d2220f1dfadbab255 (comment 6537528874) to a6be5baa55e41507a7dec1ffec7b88a660167e15. `review_carry.py 958b4af8e a6be5baa5` prints FRESH-REVIEW. It names 7 branch-only commits: five main merges, `29a1742cd` (structure record) and `e6d64bd43` (ledger pin deletion). Neither authored commit touches production code. The PR's three-dot diff differs from round 3's only by the deleted a5d8d969 ledger file and by the structure numbers. So the body needed only its delta (the Head, Figures and Red checks entries), and no re-cut is owed under `fixer.md`.

## Findings

- The merge-main automation composed two equal one-line budget edits into a stale `class_excess_loc` (17656 recorded, 17654 measured) and pushed without running `tests/structure.py` on the merged tree. That turned `tests / fast (3.14)` and `instrument-self-tests` red at `9033a595`. The body answers it under Red checks and names the cheaper detector, `structure.py` on the merged head. It places the cause in the orchestrator's merge path, not this diff, and owes no countermeasure here. Carry: dismissed: the orchestrator's merge-main path, not this diff; answered in the body's Red checks per defect-root-cause.md
- The body's two forward-carry items (linear valuations under a convex cost; mean-draw pricing) still await their append to `$.groups[88].carry` on `handoff/audit-r10-roster`, owed to the standing-roster seat (`roster_edit.py`). This is unchanged from round 3's merge verdict. Carry: R10-COP-PARTLOAD

## Evidence

- (a) Structure re-record at `29a1742cd`: `tests/structure.py` at each tree (ev/structure_round3_trees.txt):
  - a5cf3b6f5: RESULT class_excess_loc=17658, max_class_loc=8063, PASSED
  - 76d96ac77 (branch side): 17656 / 8062
  - be7584c49 (main side): 17656 / 8061
  - 9033a5958: 17654 / 8060, `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`
  - 29a1742cd: 17654 / 8060, PASSED
  - At this head: RESULT class_excess_loc=17654, max_class_loc=8060, STRUCTURE RATCHET PASSED.
  - At the merge base 2fc0e95b2: 17656 / 8061, PASSED.
  - These match every figure in the body and in the commit message.
- (a) Step 14, earned: the per-class span diff, merge base to head, is HeatPumpOptimizerCoordinator 8061->8060 (-1), HeatPumpOptimizer 3408->3409 (+1), DhwPlanner 1896->1898 (+2), ThermalModel 1879->1875 (-4). That nets -2, exactly the body's split, and every class span is the branch's own code diff, judged in rounds 1-3.
  - Removing the mechanism: at the merge base, which carries main's half and none of the branch's code, the measured value is 17656, so the -2 lives entirely in the branch's code.
  - Planting the same move with nothing improved: `structure.py` at be7584c49 and at 2fc0e95b2 prints PASSED with nothing IMPROVED, so a `--record` there moves no number.
  - The record lowers both metrics and raises none.
- (b) Anchor mutant, re-run by this seat: coordinator.py:9076 `i < len(humidity)` -> `i <= len(humidity)` (ev/mutant_f3835ba8.diff), in a separate worktree at the head.
  - `PYTHONPATH=tests/hastub python3 tests/features.py`: `1 of 4652 FEATURE CHECKS FAILED`, rc=1. The failing check is `FAIL the capacity envelope prices a step past short humidity at the ambient [raised IndexError ...]` (ev/features_mutant_f3835ba8.txt).
  - Clean head: `ALL 4652 FEATURE CHECKS PASSED`, rc=0, with the same check `ok` (ev/features_clean.txt). The mutant is killed.
  - The ledger file's reason text says `failed=2` and this run counts 1 failing check. That is a difference in counting, not in the verdict.
  - CI's mutation lane at this head also prints `coordinator.py:9076 CMP_BOUND -- killed by tests/features.py` and `MUTATION TABLE PASSED` (ev/mutation_lane.txt).
  - `ci_predict.py --only mutation --base origin/main` predicts no red, so no stale pin remains (ev/ci_predict_mutation.txt). The a5d8d969 anchor now appears only in the historical `dev/audit/harnesses/r10_mutant_skip/matrix.tsv`, as data.
- (c) Merges: `git merge-tree --write-tree origin/main a6be5baa5` rc=0 (ev/merge_tree.txt); origin/main is 2fc0e95b2, the head's merge base.
  - Every merge in the range (76d96ac77, 9033a5958, f996be1d5 with 3759d49a5, 6674eb695, a6be5baa5 with 2fc0e95b2) equals git's automatic merge tree byte for byte (ev/merge_resolution.txt), so no resolution delta is hand-made.
  - Both claim files, VERSION, RELEASE_NOTES.md and manifest.json are byte-identical to origin/main (ev/claims_identity.txt), and the branch claims nothing.
  - `env_drift.py --all 2fc0e95b2`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc=0 (ev/env_drift_all.txt).
- Enumeration rule at the head: `r10_cop_conversions.py` prints RESULT hits=95, plain=54, matching the body (ev/conversions_head.txt).
- (d) Check-runs at the head, all 55 runs, not one per check (ev/check_runs_all.txt). The four reds are:
  - budget-raise-gate ×2 (124531257194, 124560376869): `REFUSED: tvofi's approval is on 9033a59583eb, not this head`, from the D2 policy_budgets raise (51->53 lines, 644->683 tokens).
  - gate ×2 (124560298588, 124560780988): each prints only `FAIL budget-raise-gate / budget-raise-gate` (ev/gate_red.txt).
  - The body's Red checks answer budget-raise-gate as the owner-approval mechanism with no cheaper detector. pr-contract 124560607702 started 14:15:09, after budget-raise-gate's last red concluded at 14:14:58, and is green.
  - Every other gate check is green: fast, closures, coverage, mutation, instrument-self-tests, arch-score and the rest.
  - The orchestrator gives the approval at this head after this verdict, under mandate 6329234399. D2.md and coordinator.py are code-owned and tvofi approves them at merge.
- `merge_train.py classify a6be5baa5`: `RED ... red: gate`, rc=1 (ev/classify.txt), from budget-raise-gate alone as above.
- Step 5: VERSION, manifest and the notes heading are untouched (the three-dot diff is empty).
- Step 7/12: the body names a6be5baa55e41507a7dec1ffec7b88a660167e15 as its head. The PR head re-read before posting is a6be5baa55e41507a7dec1ffec7b88a660167e15 (ev/head_at_post.txt).
- The roles diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
