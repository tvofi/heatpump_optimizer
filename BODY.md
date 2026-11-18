R11-SEAM-solver: the start set brackets the all-off and wood-covered optima, the risk premium stays in the objective and out of every published money figure, and a slot's reason tie is ordered. Findings D0-s2-01, D0-s3-02, D2-s3-01, D1-s1-51; all four reproduce at the base (none has an issue number).

- D0-s3-02: both solve paths' first multi-start carries `_lower_bound_start(bounds)`. The space-only path also hands that plan to `_commit_runs` beside the descent's run. Its descent ranks on the start-blind relaxed pair, which left 3 flow-setpoint cells shipping a plan the true objective scores above all-off.
- D0-s2-01: the space-only start set moves into the module-level `_space_only_starts`. A wood-covered reference (share > 0) also draws the price-ranked seeds at the reference's own energy, so a fully covered reference no longer collapses the set onto zero.
- D2-s3-01: `_Horizon.raw_prices` carries the input prices, and `money_prices` reads them. `_solve_objectives` returns the cost closure on them. The plan's cost, the reference's cost, both settlement prices and the published `prices` are booked on that closure. `prices` (premium included) stays the objective's.
- D1-s1-51: `plan_slots.close` picks the tie with `max(dict.fromkeys(codes), key=codes.count)`, so a tie goes to the slot's first code.

Alternatives considered:
- D2, rename `prices` to the raw series and add an objective field: every objective site would change, and a missed one would silently drop the premium from the solve. Rejected for the money-side field, which defaults to `prices` when no premium applied.
- D0-s2-01, the finder's own perturbation (share 0): it drops the wood-scaled seed that brackets the covered optimum from below. Rejected for the added unscaled starts.
- D0-s2-01, adding the unscaled reference schedule as a start: measured, and it moved no race cell. Not kept.

## Head

261a399887c3554ef77154607a9fb66c5a3da9e1, measured against merge base bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f. `origin/main` was ae0ed64af898d8923ac35afe6e9c031ac1e6b111 at 2026-11-18T14:32Z; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

Each mutant deletes one fix line in a worktree at the head, then runs `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" "# --- R11-SEAM-solver: the start set brackets"`. The prelude comes from `features_block.py --emit-prelude <prelude> "<same marker>"`. Each mutant exited 1; the failing check per mutant:

- M1, `plan_slots.close` back to `max(set(codes), key=codes.count)`: FAIL `a plan slot's reason tie reads the slot's first code, whatever the hash seed (D1-s1-51)`.
- M2, `_Horizon.money_prices` returns `self.prices`: FAIL `lambda=1 books no premium as money: ... (D2-s3-01)`.
- M3, `_solve_space` drops `starts.append(_lower_bound_start(bounds))`: FAIL `the first multi-start of each solve path starts one run at the lower bound, the all-off plan (D0-s3-02)`.
- M4, `_space_only_starts` drops the lower-bound start: FAIL, same check as M3.
- M5, `_space_only_starts` drops the `if covered > 0.0` reference-energy starts: FAIL `a reference the wood tank covers whole still leaves the space-only start set a nonzero energy-anchored start beside the initial guess (D0-s2-01)`.
- M6, the space-only `_commit_runs` call drops `_lower_bound_start(bounds)`: FAIL `the space-only solve commits the all-off plan beside the descent's run, so the true objective, not the start-blind descent, ranks it (D0-s3-02)`.

At the base, the block read 4 of 5 FAIL before the fix; the commit-stage and duplicate-start checks were added later.

The five sites `prepr.sh` draws as added and unpinned, each mutated as its mutator does, against the same block at 261a3998, where it reads ALL 7 PASSED unmutated:

- `optimizer.py:2123 RETURN_DEL`: 2 FAIL, the lower-bound start check and the commit-stage check.
- `optimizer.py:2166 CMP_BOUND` (`>=`): FAIL `a space-only solve no wood covers hands the multi-start no duplicate start ... (D0-s2-01)`.
- `optimizer.py:2166 GUARD_OFF`: FAIL, the same check as CMP_BOUND.
- `optimizer.py:2172 RETURN_DEL`: 4 FAIL.
- `optimizer.py:3051 RETURN_DEL`: the block exits 1 on `TypeError: object of type 'NoneType' has no len()`. `prepr.sh` draws added-line mutants on CI; `MUTANT_CMD` was not set locally.

## Null control

Each finding's own perturbation, run at the base, reads the fixed value. Each harness's control arm reads flat at both ends.

- D1-s1-51: `slot_reason_hashseed.py --perturb` at the base gives distinct_tie=1. The 3:1 arm distinct_null=1 at both ends.
- D2-s3-01: `m3_risk.py --perturb-raw` at the base gives savings_inflation_lambda1_price_risk=0.0000. The lambda 0 cell is 0.0000 at both ends.
- D2-s3-01, in the test block: the check `the premium still prices the objective: lambda=1 moves the plan` passes at the head, so the premium was not removed from the solve.
- D0-s3-02: offstart's flat-price arm gives flat_gap_cells=0/60 at both ends.
- D0-s2-01: the race's flat/shoulder cell reads 0.0001 at base and head. Under `WOOD_SHARE_OFF=1` at the base, winter_moderate/summer_cool reads 0.0000.

## Figures

The harness figures were taken at 661c624cea62c17f063d98e0d3551b7fb7cad62f. The one commit after it adds a check to the test block and deletes two ledger files, and changes no production line (`git diff --stat 661c624c 261a3998 -- custom_components` prints nothing). Harnesses run from the plan/r11 export at 819aa2e354b4e5baaf824b8568fd72bea8168a75 (`$EXPORT` = `git archive 819aa2e3 dev/audit/rounds/round11`), with `PYTHONPATH=tests/hastub` under venv-ci's python3. Base is a worktree at bc658f9d; head is a worktree at 661c624c. sha1: `slot_reason_hashseed.py` dbc550cfc04f3c83744441c3b9c20bc2e47e6bb2, `m3_risk.py` ddd7566360f2ce85f8c2a5935748b3e025fa7f23, `offstart.py` ec26555d319fabd83e7713348d08b8511fd1b9bf, `wood_seeds.py` 1b03dd54ee64a4f6067982001f1abe3dbbdd4fcc.

Reproduction trap: the export ships `D0/s3/offstart_out/cells.jsonl`, and `offstart.py` resumes from it. A run from `$EXPORT` therefore prints the finder's cells at any tree; this seat's first base and head runs both read 16/60 that way. Copy `D0/s3` per tree and delete `offstart_out` first.

- D1-s1-51, `python3 $EXPORT/dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py`: distinct_tie 2 at base, 1 at head.
- D2-s3-01, `python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m3_risk.py`: savings_inflation_lambda1_price_risk 10.2015 at base, 0.0000 at head. savings_inflation_max 30.8631 at base, 0.0000 at head.
- D0-s3-02, `python3 $EXPORT/dev/audit/rounds/round11/D0/s3/offstart.py --workers 2`, run from a per-tree copy of `D0/s3` with `offstart_out` deleted: summer_negative_gap_cells 17/60 at base, 0/60 at head. With the lower-bound start alone, before the commit-stage change, it read 3/60, and all 3 were flow-setpoint no-DHW cells.
- D0-s2-01, `python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --census`: census_cells_all_but_one_start_zero[prod] 32 at base, 4 at head. The 4 left are summer_warm/6h cells whose reference energy is 0, where the all-off plan is the optimum (kWh_shipped 0.000).
- D0-s2-01, `python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --race` over the finding's 7 cells (its ISSUES.json command): summer_cool gap_abs at base 2.0292, 1.6782, 1.6310, 1.4675 and 1.6782 (flat), all ≤ 0.0065 at head. winter_typical/shoulder: 1.7251 at base, 1.7852 at head, 0.5765 under the finder's `WOOD_SHARE_OFF=1` at base. See Forward-carry.
- Golden, `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`: NO UNCLAIMED DRIFT and NO STALE FIXTURE over 56 scenarios, with two claims:
  - `price_risk`: every key outside the money figures and `prices` is byte-identical. The sha1 of the capture less those keys is the same at both ends.
  - `start_below_band`: objective_value drops by about 0.0055 on all four OpenBLAS kernel classes (SkylakeX, Haswell, Sandybridge, Nehalem). It was read through `tools/audit/seat/cloud-setup.sh --kernels` with an out-of-tree driver that spies `HeatPumpOptimizer.optimize` under `golden.capture`. This figure rests on that run, not on a command in this body.
- Class P4 seams, `grep -rn "_multi_start_minimize(" custom_components/heatpump_optimizer/*.py`. The finder's sweep-P4 enumerator named in ISSUES.json is absent from the plan export and from the 26 refs searched, so this grep enumerates the class instead.
  - optimizer.py `_relaxed_plans` scope call: closed in this diff, since `_solve_space`'s first solve hands it the lower-bound start.
  - optimizer.py `_relaxed_plans` free-room re-run: closed in this diff, since its starts are the same list clipped to the free room.
  - optimizer.py space-only call in `_optimize_space_only`: closed in this diff, by the start set plus the commit stage.
  - Warm-started `_solve_space` calls in the DHW alternation take a single warm start by design, and the all-off start is not added there. offstart's DHW cells read 0/60 at the head.
- Structure, `python3 tests/structure.py`: green. class_excess_loc is re-recorded down (17382 to 17360), and the commit says why.
- Architecture, `python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`: dS +0.0000.
- Gate scope, `python3 tests/closure.py select --diff bc658f9d`: MODE: SCOPED, run by CI per the brief's scoped-prepr rule.

<!-- figure-block: scope-line mb=bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f head=261a399887c3554ef77154607a9fb66c5a3da9e1 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

- `custom_components/heatpump_optimizer/optimizer.py:2123 RETURN_DEL`: killed by features.py's R11-SEAM-solver block (Mutation proof). The ledger pin is `mutation-autofix`'s.
- `custom_components/heatpump_optimizer/optimizer.py:2166 CMP_BOUND`: killed by the block's duplicate-start check. The pin is `mutation-autofix`'s.
- `custom_components/heatpump_optimizer/optimizer.py:2166 GUARD_OFF`: killed by the block's duplicate-start check. The pin is `mutation-autofix`'s.
- `custom_components/heatpump_optimizer/optimizer.py:2172 RETURN_DEL`: killed by the block. The pin is `mutation-autofix`'s.
- `custom_components/heatpump_optimizer/optimizer.py:3051 RETURN_DEL`: killed by the block (TypeError). The pin is `mutation-autofix`'s.

## Red checks

- `mutation` at 261a399887c3554ef77154607a9fb66c5a3da9e1: red by construction on the 5 sites under `## Unpinned sites`, and each is killed by the block (Mutation proof). `mutation-autofix` pins killed sites after the push. Cheaper detector: `prepr.sh`'s ci-predict step, which ran here and listed all five before the push; its standing cost is that step's run.

## Forward-carry

- winter_typical/shoulder wood race cell. gap_abs reads 1.7251 at base, 1.7852 at head and 0.5765 under the finder's own `WOOD_SHARE_OFF=1`. The challenger basin is not the seed collapse D0-s2-01 names: the cell ships 0.002 kWh at every end, and adding the unscaled reference schedule as a start left it unchanged. Carry: dismissed: outside D0-s2-01's mechanism by the finding's own perturbation; class P4's RCA, marked owed in ISSUES.json, is the seat that reads it

## Friction

- fixer-brief-inline: contradiction: the brief line "Do your work inline, with no subagents" and the frugal routing guard, which refuses inline reads past 5 per prompt, stopped the first fire. inbox/r11-seam-solver line 1 (mandate 6893738184) corrected it. Carry: dismissed: corrected by the orchestrator's ruling before this fire
- harness-export-cache: stale: the plan/r11 export at 819aa2e3 ships `D0/s3/offstart_out/cells.jsonl`, and `offstart.py` resumes from it, so a re-run from `$EXPORT` reads the finder's cells at any tree. Carry: dismissed: the reproduction recipe is in this body's Figures, the reviewer's own surface
