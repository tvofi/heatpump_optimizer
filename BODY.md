R11-SEAM-solver: the start set brackets the all-off and wood-covered optima, the risk premium stays in the objective and out of every published money figure, and a slot's reason tie is ordered. Findings D0-s2-01, D0-s3-02, D2-s3-01, D1-s1-51; all four reproduce at the base (none has an issue number).

- D0-s3-02: both solve paths' first multi-start carries `_lower_bound_start(bounds)`. The space-only path also hands that plan to `_commit_runs` beside the descent's run. Its descent ranks on the start-blind relaxed pair, which left 3 flow-setpoint cells shipping a plan the true objective scores above all-off.
- D0-s2-01: the space-only start set moves into the module-level `_space_only_starts`. A wood-covered reference (share > 0) also draws the price-ranked seeds at the reference's own energy, so a fully covered reference no longer collapses the set onto zero.
- D2-s3-01: `_Horizon.raw_prices` carries the input prices, and `money_prices` reads them. `_solve_objectives` returns the cost closure on them. The plan's cost, the reference's cost, both settlement prices and the published `prices` are booked on that closure. `prices` (premium included) stays the objective's.
- D1-s1-51: `plan_slots.close` picks the tie with `max(dict.fromkeys(codes), key=codes.count)`, so a tie goes to the slot's first code.
- `_space_only_starts` keeps one copy of each byte-identical start. A tank covering the reference whole collapses the scaled seeds and the all-off start onto one zero schedule, and each copy paid a full descent and polish to reach the same plan.
- `tests/stress.py`: one recorded, self-expiring simulate allowance for `summer/2z/space/wood-two-tank` in `tests/stress_budgets.json` (`simulate_allowance`), a budget raise under mandate 6893738184; see `## Raise justification`. `STRESS_WORK_FACTOR` is unchanged.
- `_space_only_starts` draws the reference-energy seeds unconditionally. With no wood cover they are byte-identical to the scaled seeds, so the filter drops them; the `covered > 0.0` guard was dead and is removed.
- Since the first handoff, after merging origin/main: `docs/how-it-works.md` names the five starts each space solve runs, and `tests/features.py`'s R11-OUTSIDE-HONEST-STARTS-RUNS block reads candidate 1 of the space-only commit stage as the descent's plan.

Alternatives considered:
- D2, rename `prices` to the raw series and add an objective field: every objective site would change, and a missed one would silently drop the premium from the solve. Rejected for the money-side field, which defaults to `prices` when no premium applied.
- D0-s2-01, the finder's own perturbation (share 0): it drops the wood-scaled seed that brackets the covered optimum from below. Rejected for the added unscaled starts.
- D0-s2-01, adding the unscaled reference schedule as a start: measured, and it moved no race cell. Not kept.

## Head

0b7b2296149f43b06939d5790d62dad02b9969a4, measured against merge base 7ae05284d5bceb254230b471a4eb936c2b072174. `origin/main` was 7ae05284d5bceb254230b471a4eb936c2b072174 at 2026-11-19. The last merge (`Merge origin/main 7ae05284d5`) was taken without a conflict: prepr's machinery ratchet reads its cap from the head's copy of the policy budgets, which predated main's re-record. Main's side of that merge changes no file under `custom_components/`, `tests/golden/`, `tests/stress.py`, `tests/stress_budgets.json` or `tests/features.py` (`git diff --stat fd847a550c..7ae05284d5 -- <those paths>` prints nothing), so the figures below, taken before it, describe the same product code.

## Mutation proof

Each mutant deletes one fix line in a worktree at the head, then runs `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" "# --- R11-SEAM-solver: the start set brackets"`. The prelude comes from `features_block.py --emit-prelude <prelude> "<same marker>"`. Each mutant exited 1; the failing check per mutant:

- M1, `plan_slots.close` back to `max(set(codes), key=codes.count)`: FAIL `a plan slot's reason tie reads the slot's first code, whatever the hash seed (D1-s1-51)`.
- M2, `_Horizon.money_prices` returns `self.prices`: FAIL `lambda=1 books no premium as money: ... (D2-s3-01)`.
- M3, `_solve_space` drops `starts.append(_lower_bound_start(bounds))`: FAIL `the first multi-start of each solve path starts one run at the lower bound, the all-off plan (D0-s3-02)`.
- M4, `_space_only_starts` drops the lower-bound start: FAIL, same check as M3.
- M5, `_space_only_starts` drops the reference-energy starts (the `if covered > 0.0` branch at 261a3998; unconditional since f769d50c7f): FAIL `a reference the wood tank covers whole still leaves the space-only start set a nonzero energy-anchored start beside the initial guess (D0-s2-01)`.
- M6, the space-only `_commit_runs` call drops `_lower_bound_start(bounds)`: FAIL `the space-only solve commits the all-off plan beside the descent's run, so the true objective, not the start-blind descent, ranks it (D0-s3-02)`.

- M7, `_space_only_starts` returns `starts` without the identical-start filter (the tree at 320c063489): `tests/stress.py` FAIL `no scenario's solver work grew on an unchanged plan`, summer/2z/space/wood-two-tank 54 evaluations against main's 26 = 2.08x.

The allowance, each mutant applied in a worktree at the head and run as `PYTHONPATH=tests/hastub python3 tests/stress.py` up to its `Combination sweep` section:

- MA, `simulate_work_factor` returns `SCENARIO_WORK_FACTOR` where the allowance applies: FAIL `a simulate allowance excuses its scenario while the baseline predates the change`.
- MB, the `base_sim < allow["baseline_below"]` condition dropped: FAIL `...and is inert once the baseline carries the change`.
- MC, `work_drift_compare` calls `work_over_verdict` without the scenario's factor: FAIL `a simulate allowance excuses its scenario while the baseline predates the change`.
- MD, `budget_table_problems` skips the allowance's validation: FAIL `a malformed simulate allowance is refused by the budget table check`.

At the base, the block read 4 of 5 FAIL before the fix; the commit-stage and duplicate-start checks were added later.

The five sites `prepr.sh` drew as added and unpinned at the first handoff, each mutated as its mutator does, against the same block at 261a3998, where it reads ALL 7 PASSED unmutated:

- `optimizer.py:2123 RETURN_DEL`: 2 FAIL, the lower-bound start check and the commit-stage check.
- `optimizer.py:2166 CMP_BOUND` (`>=`): FAIL `a space-only solve no wood covers hands the multi-start no duplicate start ... (D0-s2-01)`.
- `optimizer.py:2166 GUARD_OFF`: FAIL, the same check as CMP_BOUND.
  Both 2166 sites are gone at this head: once identical starts are filtered, the CMP_BOUND mutant was equivalent, and `tests/mutation_table.py` read it as a survivor. So commit f769d50c7f removes the guard, a branch the filter already made dead.
- `optimizer.py:2172 RETURN_DEL` (now 2178, the filtered return): 4 FAIL.
- `optimizer.py:3051 RETURN_DEL` (now 3058): the block exits 1 on `TypeError: object of type 'NoneType' has no len()`. `prepr.sh` draws added-line mutants on CI; `MUTANT_CMD` was not set locally.

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
- Architecture, `python3 tools/audit/archscore/score.py --diff 7ae05284d5bceb254230b471a4eb936c2b072174`: dS +0.0000 NULL.
- Stress, `PYTHONPATH=tests/hastub python3 tests/stress.py` at 6a09ed087ac57b9e516d5e56c45cb0b95c4ff08b: ALL 120 STRESS CHECKS PASSED. summer/2z/space/wood-two-tank reads 38 solver evaluations against main's 26 (1.46x, under the 1.80x factor) and 122592 simulate step-equivalents against 37824 (3.24x, under its 3.25x allowance). The objective is 21423.23656 at both ends.
- Stress counts per tree, `PYTHONPATH=tests/hastub:tests python3 -c` calling `stress.capture_work_rows(<tree>, <out>, labels=["summer/2z/space/wood-two-tank"])`: evals 54 and simulate 122592 at 320c063489, evals 38 and simulate 122592 with the identical-start filter.
- D0-s2-01 at the head, `python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --race` over the finding's 7 cells, run from the head worktree: summer_cool gap_abs 0.0000, 0.0000, 0.0004, 0.0077 and 0.0000 (winter_narrow, winter_extreme, winter_typical, winter_moderate, flat). winter_typical/shoulder reads 1.7852 and flat/shoulder 0.0001, the same as at the first handoff.
- The identical-start filter is not bit-identical on every cell. winter_moderate/summer_cool reads 0.0065 at 320c063489 and 0.0077 at the head, deterministically, on the same harness. A stderr probe in `_space_only_starts` on that cell shows the filter drops only the four duplicate zero starts (9 starts -> 5), so the start set is the same. The 0.0012 J (0.009 %) moves with the float path: the dropped descents no longer leave their entries in the shared evaluation memo. The probe ran in a throwaway worktree, and its edit is not in this diff.
- Gate scope, `python3 tests/closure.py select --diff bc658f9d`: MODE: SCOPED, run by CI per the brief's scoped-prepr rule.

<!-- figure-block: scope-line mb=7ae05284d5bceb254230b471a4eb936c2b072174 head=0b7b2296149f43b06939d5790d62dad02b9969a4 -->
~~~text
MODE: SCOPED -- 28 script(s) run, 5 scoped out.
~~~
<!-- /figure-block -->

## Raise justification

The raise: `summer/2z/space/wood-two-tank` gets `"simulate_allowance": {"factor": 3.25, "baseline_below": 68093}` in `tests/stress_budgets.json`, under mandate 6893738184 (scope all), as the orchestrator directed in this group's dispatch. The D0-s2-01 start set steps that scenario's simulation 122592 step-equivalents against main's 37824 = 3.24x, on an unchanged plan. That is over the 1.80x `STRESS_WORK_FACTOR`, and every narrower start set reopens the finding's race. The allowance covers that one scenario and only the simulate channel. It applies only while the live baseline reads below 68093 steps, the geometric mean of the two counts. So once main carries the start set, the global factor judges the scenario again, and a 2x regression there is still seen. `STRESS_WORK_FACTOR` is unchanged.

Payments tried: five, each measured on the scenario against main's 26 evaluations and 37824 simulate steps:

- Keep one copy of each identical start (taken, commit d1e3701d13). Evaluations 54 -> 38 (2.08x -> 1.46x), simulate unchanged at 122592 (3.24x), because the duplicates were served from the shared evaluation memo. It clears the evaluation channel but not the simulate channel.
  Architecture score: dS 0 NULL
- Draw the extra seeds only when the wood tank covers the reference (variant F, gate on covered >= 1.0). The counts are identical to the head, 54 evaluations and 3.24x simulate, because the scenario is itself fully covered. Not taken: it changes nothing here.
- Narrow the reference-energy seeds to f = 1.0 (variant A). It passes stress (116/116) but reopens the race, with gap_abs 1.3571, 0.1287 and 0.1292 on winter_moderate, winter_extreme and flat over summer_cool. Not taken: the orchestrator ruled it out.
- Narrow them to the low-energy fractions only (variant B). Simulate 94368/37824 = 2.49x, still over 1.80x. Not taken.
- Drop the space-only all-off start (variant L). 50/26 evaluations = 1.92x and simulate 3.24x. Not taken: it is D0-s3-02's fix, and it moves no simulate step.

The second raise, the same scenario's recorded CPU `ratio` 2.2 -> 7.46 (commit d63daa072e). The solve CPU follows the simulate steps. `tests/mutation_table.py`'s stress baseline read the scenario at 6.7x its reference against its 6.6x budget (2.2 x 3), confirmed at a median of 6.9x over 3 re-solves. 7.46 is that row from a clean `PYTHONPATH=tests/hastub python3 tests/stress.py --record-budgets` at this head. The row's memory fields pass at their records and are not re-recorded. The payments above are the ones open to this ratio too, because the cost is the same three descents.

No payment brings the scenario under its current budget. The simulate cost is the three reference-energy descents themselves.

Architecture score: dS +0.0000 NULL

## Unpinned sites

none: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main` pinned the three sites the diff adds (commit a2236e189f, PIN KILLED: 3 pinned, 0 left unpinned). `optimizer.py` `_lower_bound_start` RETURN_DEL is killed by tests/features.py, `_space_only_starts` RETURN_DEL by tests/doc_claims.py and `_Horizon.money_prices` RETURN_DEL by tests/plan_view.py.

## Red checks

- `budget-raise-gate`: red by construction, because the diff raises a `tests/stress_budgets.json` leaf (`summer/2z/space/wood-two-tank`'s `simulate_allowance`, its two numbers). Under decision 0013 it turns green on an approving review at the head. Here that is the orchestrator's under mandate 6893738184 (scope all), which reads `## Raise justification`. Cheaper detector: `prepr.sh`'s body check, which ran here and named the raise before the push. Its standing cost is that step's run.
- `tests / fast (3.14)` at the first handoff (261a3998, PR #3736's run 44332199301): `tests/stress.py`, summer/2z/space/wood-two-tank over the work factor on an unchanged plan. This head passes: `PYTHONPATH=tests/hastub python3 tests/stress.py` reads ALL 120 STRESS CHECKS PASSED at 6a09ed087a, and the CPU ratio is re-recorded at d63daa072e (`## Raise justification`). Cheaper detector: `tests/stress.py` run locally before the handoff, which prepr leaves to CI (`closures: left to CI: tests/stress.py`). The three commits after 6a09ed087a re-record the scenario's CPU ratio, remove a dead branch with an unchanged start set, and pin mutation sites. Its standing cost is about 25 minutes of CPU per solver handoff. This fire ran it.
- `tests / mutation-autofix` at the first handoff: `skip-measure-failed`, so the bot pinned nothing. This head pins the killed sites with `tests/mutation_table.py --pin-killed --base origin/main` (commit a2236e189f; see `## Unpinned sites`). Cheaper detector: that same command before the handoff, which the first handoff did not run.
- `tests / replay` at the first handoff: `owner-2026-10-30-away.json: cycle_cost`, cpu_ratio 443.7 over its budget 332.8. The PR's run was on base 9fe63d00, before main's #3725 (the replay-cost fix for #3602), which this head's merge base fd847a55 carries. Not re-measured at this head, because the lane takes about 30 minutes on the runner. It is not in `merge_train.py owed-reds`.
- `tests / nightly-status`: main's own nightly `slow` lane failed in dispatch run 44270682877 (head f567988), which this diff does not touch. It is not in `merge_train.py owed-reds`, and the owner of the nightly lane is main's.
- `mutation` at the first handoff: red on its 5 unpinned sites. At this head the three sites the diff adds are pinned (`## Unpinned sites`), and the two 2166 sites no longer exist. Cheaper detector: `tests/mutation_table.py --pin-killed` before the handoff. Its standing cost is about an hour of CPU here.

## Forward-carry

- winter_typical/shoulder wood race cell. gap_abs reads 1.7251 at base, 1.7852 at head and 0.5765 under the finder's own `WOOD_SHARE_OFF=1`. The challenger basin is not the seed collapse D0-s2-01 names: the cell ships 0.002 kWh at every end, and adding the unscaled reference schedule as a start left it unchanged. Carry: dismissed: outside D0-s2-01's mechanism by the finding's own perturbation; class P4's RCA, marked owed in ISSUES.json, is the seat that reads it

## Friction

- fixer-brief-inline: contradiction: the brief line "Do your work inline, with no subagents" and the frugal routing guard, which refuses inline reads past 5 per prompt, stopped the first fire. inbox/r11-seam-solver line 1 (mandate 6893738184) corrected it. Carry: dismissed: corrected by the orchestrator's ruling before this fire
- harness-export-cache: stale: the plan/r11 export at 819aa2e3 ships `D0/s3/offstart_out/cells.jsonl`, and `offstart.py` resumes from it, so a re-run from `$EXPORT` reads the finder's cells at any tree. Carry: dismissed: the reproduction recipe is in this body's Figures, the reviewer's own surface
