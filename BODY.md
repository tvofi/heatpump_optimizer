R10-SOLVER, wave 17. One value-neutral performance fix (D9-s1-01) and a recorded disposition for the P4 class issue (D0-s1-01, D0-s2-01), which this PR measures and does not change in production.

Closes #2240.
Part of #2250.

**1. N-solve-recompute (#2250, D9-s1-01).** L-BFGS-B asks for the value and the gradient at every point it visits. The multi-start's own runs already took both from one batch (R9 D9-s1-02). The two runs that move a start did not: the two-zone half-price continuation (`_optimize_space_only.move_starts`) and the relaxed duty-cycle candidate (`_relaxed_starts`). They passed the scalar `objective` as `fun` and a jac that called it again as the difference's base, so each gradient cost two scalar horizons on top of the batch. All four run sites (the multi-start start, its polish in `_lbfgsb_restart`, the continuation and the relaxed candidate) now go through one driver helper, `_lbfgsb_run(objective, fused, x0, bounds, args, maxiter)`. It uses `fused` with `jac=True` wherever `_bounds_supported_by_batch` serves the bounds, and scipy's own estimate otherwise, exactly as before. The stop (`ftol 1e-6`, `eps 1e-4`) is now spelled once instead of four times. A batched row is bitwise the scalar objective (#97), so no iterate moves: the plan is bit-identical, and no golden or stress scenario moves (Figures).

This is the architect note's shape: "one fused objective call" in the driver, touching only the minimiser driver and the objective-evaluation seam. Alternatives considered:
- Fuse only the two start-moving sites with a second helper. Rejected: it added a fourth spelling of the same run shape, and `tools/audit/archscore/score.py --diff` read `duplication_copies 40 -> 41`, inadmissible. One helper for all four reads `dS +0.0000 NULL`, and `class_excess_loc` falls 18272 -> 18269.
- The finder's own rewrite (`cont_fuse.py`'s fused arm, which wraps only the continuation). Rejected for the same reason, and it leaves the relaxed candidate unfused.

**2. P4 (#2240): seeds and stop tolerance. Disposition: duplicate of the owner's refusals #1293 (stop) and #1294 (seeds), re-measured at this merge base. No production change.** The owner refuted tightening the L-BFGS-B stop on #1293 (2026-09-22): "improves the objective (-0.332%) but loses +6.4% money on the backtest shoulder cell ... no intermediate ftol (3e-7..1e-9) captures the win without the loss, and the tighter rule costs 2.4x thread CPU". #1294 refused the production anchor ladder on cost. RCA-BULK-1 section 4 records both refusals as the class disposition: "A gap closable only by a refused knob is a duplicate of that refusal." This PR measures which knob each finding needs, at merge base `738d950aa`:
- **D0-s2-01 is the stop.** The finder's `ftol_race.py` reads `polish_gap_winter_mean=0.0343 pct` (max 0.2281, drop-max mean 0.0066) at this merge base, down from 0.2025 % at the finding's baseline. Closing it means a tighter stop, which is #1293. The round's own closed loop at ftol 1e-10 (`dev/audit/rounds/round10/D0/s2/mpc_mask_ftol.out`) realises worse money in 3 of 4 cells (-0.80 %, -1.50 %, flat -0.65 %).
- **D0-s1-01 is the seeds.** `dev/audit/harnesses/r10_solver_seed_or_stop.py` splits `race.py`'s c1 into a seeds-only arm and a restart-only arm (a fresh run from the shipped x). Over the 23 cells `race.py` reports above 1e-3, restart-only recovers at most 1.008e-4 in 22 of them, so the stop is not their cause. The 23rd, tz0 summer_typical/summer_cool, is a stop cell: restart-only recovers its whole 1.829e-3 (a 0.43 SEK bill, dSEK 0.005 in race.py; under the D0 brief's money bar). Seeds-only recovers more than 9e-4 in 22 of 23 cells, and is 5.976e-3 worse than production in the other one. That is the seed ladder #1294 refused, and #1294's own "seeds alone: 17 better/21 WORSE" shape recurs.
- **The one narrower stop change #1293 did not measure was priced and lost.** It is a single extra `_lbfgsb_restart` of the multi-start's winner at ftol 1e-9, adopted only past `_LBFGSB_RESTART_KEEP_REL`. It costs one polish per call (104 polishes, 25 adopted, 5396 polish nfev over the 8 cells), not 2.4x. `dev/audit/harnesses/r10_solver_winner_polish.py` measured its realised one-day closed-loop money: the non-flat mean is +0.1462 % cheaper, but 1 of 6 non-flat cells is worse (winter_typical/winter_mild, -0.99 %, bought with comfort: below-17 degree-steps 1.99 -> 1.24). The flat-price null is -0.7893 % (flat/winter_mild -1.48 %). A stop change that loses money on a flat price is #1293's mechanism, the objective trading money it cannot see, so it is not shipped.

The finder harnesses therefore read identical at both ends (Figures). That is stated rather than implied: this PR leaves the measured quantity alone on purpose. The P4 enumerator is the step-8 instrument, and every seam it returns is dispositioned below.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Jpb69gUnGU2uJzhv4zv4oP

## Head

`7bf34026d51ac9f528e8cf65447f3f2b41f8f1bd` (this body rides on the orphan ref, not the code head). Merge base `738d950aa981efbdf866ff369942a69c5ae7d205`. `origin/main` moved to `58730d09f` (at 2026-10-22T15:15Z) after the figures were taken. That move is #2589 (`tools/pr/app_approve.sh`, its harness, a delivery row, one closures line, INSTRUMENTS.md), disjoint from this diff, so the branch is not merged and every figure is at `738d950aa`. Commits:
- `f11459ced`: the fix, the test, structure re-record, winner-polish harness.
- `c0b264338`: the test block imports its own names, the ledger drops four moved guards, and the seed-or-stop harness.
- `7bf34026d`: `ci_predict.py --apply-inert` entries for the two harnesses.

## Mutation proof

The block run is `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# -- R10-SOLVER: N-solve-recompute" "# -- R9 N-fit-integrator (#1672)"`. At head it prints `ALL 4 FEATURES BLOCK PASSED`. Each mutant was applied to `optimizer.py` in the worktree and restored after its run (`cmp` against the saved copy: identical):
- M1, the predicate in `_lbfgsb_run` (`if fused is not None and _bounds_supported_by_batch(bounds):` -> `if False:`, the inventory's GUARD_OFF): rc=1. FAIL `R10-SOLVER D9-s1-01 (census precondition): the metered solve runs the continuation, the relaxed candidate and the multi-start's own runs on the batched jac` [{}].
- M2, `fun, jac = fused, True` -> the scalar value with the batch's gradient (the pre-fix shape): rc=1. FAIL `R10-SOLVER D9-s1-01: no L-BFGS-B run with a supplied jac simulates the scalar trajectory -- the value rides in the gradient's batch` [{'relaxed': (1, 67), 'continuation': (1, 117), 'multi-start': (12, 491)}].
- M3, the continuation passes `None` for `fused`: rc=1. FAIL census precondition [{'relaxed': (1, 0), 'multi-start': (12, 0)}], and FAIL `(null, exact)`.
- M4, the relaxed candidate passes `None` for `fused`: rc=1. FAIL census precondition, FAIL `(positive control)` and FAIL `(null, exact)`.

Test first: the same block on `origin/main`'s `optimizer.py` (`738d950aa`) reads `{'relaxed': (1, 134), 'continuation': (1, 234), 'multi-start': (12, 0)}` and FAILs `... no L-BFGS-B run with a supplied jac simulates the scalar trajectory`. The census precondition, the positive control and the null pass there.

## Unpinned sites

`tools/pr/ci_predict.py --base 738d950aa` names two added sites, both at `_lbfgsb_run`'s guard, and gives each a disposition:
- `custom_components/heatpump_optimizer/optimizer.py:774 GUARD_OFF` (`_lbfgsb_run`'s guard -> `if False:`): left for `mutation-autofix` to pin. Measured killed locally by the features block (M1 above).
- `custom_components/heatpump_optimizer/optimizer.py:774 BOOLOP` (`and` -> `or`): left for `mutation-autofix` to pin. Its predecessor rows at the old spellings were `killed_by` `tests/features.py`.

Four `killed_by` rows (`_lbfgsb_restart` BOOLOP/GUARD_OFF `854e7632` and `_multi_start_minimize` BOOLOP/GUARD_OFF `c70e3723`) named the guard at the spellings this diff deletes, and `mutation_table` refused them ("disposition names no site the inventory generates"). They are removed. After that, `completeness_problems` and `ledger_form_problems` return `[]`, and `--normalize` reports `0 retired key(s) naming no site`.

## Null control

- The fix's own null, exact: the block patches `_lbfgsb_run` to take `f` from the scalar objective (the pre-fix shape), and the solve ships the same plan bit for bit (`np.array_equal`). The finder harness agrees: `plan_identical=True` with the same plan hash at base and head on all three scenarios.
- Positive control of the meter: the scalar-valued arm reads `{'relaxed': (1, 67), 'continuation': (1, 117), 'multi-start': (12, 491)}`, so the zero at head is not a blind meter.
- The carried null (D9-s1-01: "equal total SSE on the single-zone no-hot-water case"): `winter_single_no_dhw` reads horizons 1367.0 = 1367.0, scalar steps 864 = 864 and rows 1358 = 1358 at base and at head. It has no continuation and nothing to fuse. `winter_two_zone_dhw` is likewise identical (38428.0 horizons both ends).
- The carried P4 null ("the gap on a flat-price cell is solver basin, not money; report both"). At this merge base, `race.py` gives `flat_gap_rel_max=2.4769e-03` against `nonflat_gap_rel_max=1.0958e-01`, and `ftol_race.py` gives `polish_gap_max[flat]=0.0025 pct` against a winter max of 0.2281 %. In money, the winner-polish arm's flat cells read -0.7893 % mean: the flat-price objective gap is not money.
- `score.py --diff origin/main` on a tree with the fix alone, as a second helper: `duplication_copies 40 -> 41`. With the one helper: `dS +0.0000 NULL`.

## Figures

Seat venv python 3.14.7, numpy 2.4.6, scipy 1.17.1, linux x86_64, 4 cores, `PYTHONPATH=tests/hastub`. The base is the merge base `738d950aa` (its own worktree) and the head is the branch. Counts and objectives are deterministic; CPU is marked provisional.
- D9 finder harness `dev/audit/rounds/round10/catchup/d9/cont_fuse.py` (sha1 434fa53cad1b3b84df7e4a87d112e96640261c66), run as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/d9/cont_fuse.py --reps 3`, quiet box (load1 0.20 base, 0.48 head; thread_factor 1.000 both), base then head in sequence:
  - base, `winter_two_zone_no_dhw`: prod 35757.0 horizon-equivalents against fused 35713.0 (delta 44.0); scalar steps 10080 -> 1632; rows 35652 -> 35696; `rewrites fused=1`.
  - head, same scenario: prod 35713.0 = fused 35713.0 (delta 0.0); scalar steps 1632 both; `rewrites fused=0`. The shipped tree is the base's fused arm.
  - Honest unit (the roster carry): per-gradient horizons. The headline "192 -> 97 sse/grad" counts a batch row as 1. In horizon-equivalents the saving is 44 of 35757, which is 0.12 % of the solve's simulated horizons; 88 scalar horizons became 44 batch rows.
  - CPU, provisional (median of 3 interleaved reps): base `solve_cpu_ms prod=1766 fused=1645` (ratio 1.074) and `scalar_step_cpu_ms prod=122 fused=18`; head `prod=1666 fused=1633` (1.020, same code both arms) and `19/17`. The head's same-code ratio of 1.020 is this box's noise floor, and the null scenarios read 0.907-1.091 at the base, so only the scalar-step CPU (122 -> 19 ms) clears the noise.
  - The relaxed candidate runs only under `clamp_planned_levels`, which this harness does not drive. The features block counts it: 134 scalar simulations at base, 0 at head.
- P4 finder harnesses, base and head, compared with every line except `load1`, `thread_factor` and `swapins`:
  - `dev/audit/rounds/round10/D0/s1/race.py` (sha1 8689b3208ce48451edb5f8e6c7fb5d9eec62384b), run as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s1/race.py`: identical at both ends. `cells=80`, `cells_gap_gt_1e-3=23`, `cells_gap_gt_1e-2=3`, `gap_rel_max=1.0958e-01`, `gap_rel_mean=2.8198e-03`, `gap_rel_mean_drop_max=1.4684e-03`, `flat_gap_rel_max=2.4769e-03`.
  - `dev/audit/rounds/round10/D0/s2/ftol_race.py` (sha1 c8581979b9c3bad06f6190ba276ae7fcc782fcad), run as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D0/s2/ftol_race.py`: identical at both ends. `polish_gap_winter_mean=0.0343 pct n=8 range=0.0000..0.2281 drop_max_mean=0.0066`, `polish_gap_max[flat]=0.0025`.
- Seed-or-stop split `dev/audit/harnesses/r10_solver_seed_or_stop.py` (sha1 8181cc258c5ecb969afa27aea64223a8bd78b16f), run as `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_solver_seed_or_stop.py race.out` over the base's `race.py` output. The rule is: every `cell` line with `gap_rel > 1e-3`.
  - 23 cells. `restart_only` exceeds 2.5e-6 in 2: tz0 summer_typical/summer_cool (1.829e-3, equal to seeds_only: a stop cell) and tz1 flat/winter_cold (1.008e-4). The other 21 are at or below 2.443e-6.
  - `seeds_only` is above 9e-4 in 22 of 23 cells (max 1.096e-1, tz0 summer_negative/shoulder) and is -5.976e-3 on tz1 winter_moderate/winter_cold.
  - Null: restart_only is the stop's own arm. It would carry the gap if the stop were the cause.
- Winner-only polish `dev/audit/harnesses/r10_solver_winner_polish.py` (sha1 762c2aa15f244f4a831958662bd9400d1767c9b0), run as `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_solver_winner_polish.py` at `f11459ced` (production value-identical to the base). Default 8 cells, ftol 1e-9:
  - `money_pct_nonflat_mean=0.1462 worse_cells=1/6`; `money_pct_flat_mean=-0.7893 (null)`.
  - Per cell: winter_typical/cold +0.1648, winter_narrow/cold +1.0407, winter_moderate/cold +0.6588, winter_extreme/mild 0.0000, winter_typical/mild/dhw0 -0.9868, shoulder/cold/tz0 0.0000, flat/cold -0.1000, flat/mild -1.4786.
  - `polish=104 adopted=25 polish_nfev=5396`; thread_factor 1.000, load1 1.52.
- Backtest under the same winner-only polish (scratch wrapper around `tests/backtest.py`, the same `_lbfgsb_restart` call as the harness's `winner`): 11 polishes, 4 adopted, and every scenario's optimizer row unchanged to two decimals (23.28 / 59.10 / 3.72 SEK). Not landed: the closed-loop harness above is the instrument for money.
- Step-8 enumerator `dev/audit/rounds/round10/D14/sweep-P4/p4_seams.py` (sha1 ddd96e1be09b730d89d5fa70311ef0ed5f2f1e69), run as `python3 dev/audit/rounds/round10/D14/sweep-P4/p4_seams.py`:
  - base: `seams=15 stop=7 seed=8`.
  - head: `seams=12 stop=4 seed=8`.
  - head `positive_control`: `{'D0-s2-01 main': False, 'D0-s2-01 restart': False, 'D0-s1-01 seeds': True}`. Named route (fixer.md step 14): the two False rows are keyed on the enclosing function. The stop moved, unchanged at `ftol=1e-06`, from `_multi_start_minimize` and `_lbfgsb_restart` into `_lbfgsb_run`, which the head lists as `STOP optimizer.py:_lbfgsb_run ... ftol=1e-06`. The instance is not closed.
  - Disposition of every head seam:
    - `_lbfgsb_run` STOP ftol 1e-6, which now carries the base's `_multi_start_minimize`, `_lbfgsb_restart`, `_relaxed_starts` and `move_starts` stops: instance, D0-s2-01, duplicate of the #1293 refusal (above).
    - `_scoped_minimize` x2: not applicable (the thread-scope wrapper, as the sweep ruled).
    - `dhw_planner._plan_dhw_min_cost` linprog: not applicable (an LP, as the sweep ruled).
    - `_optimize_space_only` SEED x3: instance, D0-s1-01, duplicate of the #1294 refusal.
    - `_solve_space` SEED x5: instance beyond the finding (sweep-P4), duplicate of the #1294 refusal. Its countermeasure, `_CERT_CELLS` DHW cells, is carried (Forward-carry).
- Scoped gate: `python3 tests/closure.py select --diff 738d950aa` gives `MODE: SCOPED -- 27 script(s) run, 6 scoped out`. Run as `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=738d950aa... bash tests/run.sh` at `f11459ced`: every script in scope `ok` except `tests/entities.py` (1 of 2388, the four stale ledger rows, fixed in `c0b264338`). In detail:
  - `tests/features.py`: `ALL 4305 FEATURE CHECKS PASSED`.
  - `tests/env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 738d950aa`, so nothing is claimed in either claim file.
  - `tests/stress.py`: `ALL 113 STRESS CHECKS PASSED`. Solver work: `54 of 54 scenarios ... 0 re-planned by this branch`. Whole-solve CPU median 0.997x of the baseline beside the run. Production calls `re-planned: []`.
  - `tests/optimality.py`: `ALL 84`. `tests/backtest.py`: `ALL 25`.
  - At `c0b264338`, re-run: `tests/entities.py` `ALL 2388 ENTITY CHECKS PASSED` and the features block `ALL 4 FEATURES BLOCK PASSED`.
  - At `7bf34026d`: `tests/harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, with `class_excess_loc` 18272 -> 18269 recorded in `f11459ced`.
- `python3 tools/audit/archscore/score.py --diff origin/main` (origin/main = `738d950aa` when run): `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 738d950aa`: `no closures or fast red predicted`, and 2 unpinned sites (above).

## Architecture score

n/a: no metric rises (`dS +0.0000 NULL`).

## Red checks

- `mutation` (expected red at the push): the ratchet refuses the two sites this diff adds unpinned (`optimizer.py:774` BOOLOP and GUARD_OFF, under Unpinned sites) until `mutation-autofix` pins them, which `ci-autofix.md` says to wait for, not duplicate. Cheaper detector: `tools/pr/ci_predict.py` and `prepr.sh` step 6d already print both sites before the push, so none is owed.
- None else at the push. Locally the scoped gate's `tests/entities.py` went red on the four `killed_by` rows that named the moved guard. It is answered in `c0b264338`. Cheaper detector: `tools/pr/ci_predict.py` / `prepr.sh` step 6d read the ledger's completeness statically in seconds, and running it before the gate would have caught this. None is owed beyond running it first, which the seat now does.

## Forward-carry

- **D0 (price optimality) brief, the next round's D0 seats.** A stop-tolerance change is refused on money (#1293). That covers the narrower winner-only polish too, measured here: non-flat +0.15 %, but the flat null -0.79 % and 1 of 6 cells worse. A D0 challenger that tightens the stop, on all runs or on the winner, is a duplicate of #1293 unless it shows realised closed-loop money (the `r10_solver_winner_polish.py` shape, flat null included) that does not fall on a flat price. Re-measure at your merge base. Carry: `dev/governance/dimensions/D0.md` (Traps). That file is policy in the owner's words, so this seat does not edit it. It goes to the orchestrator to land.
- **D0/D14 detector (from sweep-P4, re-confirmed).** `_solve_space`'s DHW seed set is unguarded, because `_CERT_CELLS` holds space-only cells. Carry: `tests/optimality.py` `_CERT_CELLS`, a group outside this one's file list. It goes to the orchestrator for a roster group.
- R10-TARIFF's carry (`PeakBilling` via `HeatPumpOptimizer._peak_billing`) is satisfied: this diff calls no capacity charge and passes no loose tariff argument (`git diff 738d950aa...HEAD -- custom_components | grep -c peak_cost` gives 0).

## Friction

- `fixes-vs-disposition: contradiction: the roster lists the P4 class issue under fixes, while RCA-BULK-1 section 4 and the owner's two refusals (stop, seeds) leave no shippable fix for either finding. The closing line above records a re-measured duplicate disposition; if the orchestrator reads that as not a fix, the closing line becomes Part of. Carry: dev/programme/rosters/wave-r10-groups.json (R10-SOLVER)`
- `finding-propagation: unenforced: a seat with handoff-only write access cannot land a carry into a policy brief (D0.md) or a roster; both go to the orchestrator in this body. Carry: orchestrator`

