R10-SOLVER, wave 17, round 2. One value-neutral performance fix (D9-s1-01) and a recorded disposition for the P4 class issue (D0-s1-01, D0-s2-01). This PR measures P4 and does not change it in production.

Closes #2240.
Part of #2250.

**1. N-solve-recompute (#2250, D9-s1-01).** L-BFGS-B asks for the value and the gradient at every point it visits. The multi-start's own runs already took both from one batch (R9 D9-s1-02). The two runs that move a start did not. These are the two-zone half-price continuation (`_optimize_space_only.move_starts`) and the relaxed duty-cycle candidate (`_relaxed_starts`). Each passed the scalar `objective` as `fun`, plus a jac that called it again as the difference's base, so every gradient cost two scalar horizons on top of the batch. All four run sites now go through one driver helper, `_lbfgsb_run(objective, batch_objective, x0, bounds, args, maxiter, memo=None)`: the multi-start start, its polish in `_lbfgsb_restart`, the continuation and the relaxed candidate. Wherever `_bounds_supported_by_batch` serves the bounds, the helper builds the fused, memoized `fun` itself and passes `jac=True`. Otherwise it leaves the estimate to scipy, as before. The stop (`ftol 1e-6`) and the finite-difference step (`_LBFGSB_FD_EPS = 1e-4`) are each spelled once. `_lbfgsb_run` reads the step both for the fused batch gradient and for the `eps` option, so the two cannot disagree (review O2). `_multi_start_minimize` loses its `fd_eps` keyword, and its shared evaluation memo is passed as `memo`. A batched row is bitwise the scalar objective (#97), so no iterate moves. The plan is bit-identical, and no golden or stress scenario moves (Figures).

This is the architect note's shape: "one fused objective call" in the driver, touching only the minimiser driver and the objective-evaluation seam. Alternatives considered:
- Fuse only the two start-moving sites with a second helper. Rejected because it added a fourth spelling of the same run shape: `tools/audit/archscore/score.py --diff` read `duplication_copies 40 -> 41`, which is inadmissible. One helper for all four reads `dS +0.0000 NULL`.
- Use the finder's own rewrite, `cont_fuse.py`'s fused arm, which wraps only the continuation. Rejected for the same reason, and it leaves the relaxed candidate unfused.
- Keep round 1's shape, where the callers build the fused callable and pass it in. Rejected on review O2: the step was spelled at each start-moving call site, in `_multi_start_minimize`'s `fd_eps` and in the options, and mutant J (a call-site step 1e-4 -> 1e-3) survived every check.

**2. P4 (#2240): seeds and stop tolerance. Disposition: duplicate of the owner's refusals #1293 (stop) and #1294 (seeds), re-measured at merge base `738d950aa` in round 1. No production change.** The owner refuted tightening the L-BFGS-B stop on #1293 (2026-09-22): "improves the objective (-0.332%) but loses +6.4% money on the backtest shoulder cell ... no intermediate ftol (3e-7..1e-9) captures the win without the loss, and the tighter rule costs 2.4x thread CPU". #1294 refused the production anchor ladder on cost. RCA-BULK-1 section 4 records both refusals as the class disposition: "A gap closable only by a refused knob is a duplicate of that refusal."
- **D0-s2-01 is the stop.** The finder's `ftol_race.py` read `polish_gap_winter_mean=0.0343 pct` (max 0.2281, drop-max mean 0.0066), down from 0.2025 % at the finding's baseline. Closing it means a tighter stop, which is #1293. The round's own closed loop at ftol 1e-10 (`dev/audit/rounds/round10/D0/s2/mpc_mask_ftol.out`) realises worse money in 3 of 4 cells (-0.80 %, -1.50 %, flat -0.65 %).
- **D0-s1-01 is the seeds.** `dev/audit/harnesses/r10_solver_seed_or_stop.py` splits `race.py`'s c1 into a seeds-only arm and a restart-only arm (a fresh run from the shipped x). Over the 23 cells `race.py` reports above 1e-3, restart-only recovers at most 1.008e-4 in 22, so the stop is not their cause. The 23rd, tz0 summer_typical/summer_cool, is a stop cell: restart-only recovers its whole 1.829e-3 (a 0.43 SEK bill, dSEK 0.005, under the D0 brief's money bar). Seeds-only recovers more than 9e-4 in 22 of 23 cells and is 5.976e-3 worse than production in the remaining one. That is the seed ladder #1294 refused.
- **The narrower stop change #1293 did not measure was priced and lost.** This is a single extra `_lbfgsb_restart` of the multi-start's winner at ftol 1e-9, adopted only past `_LBFGSB_RESTART_KEEP_REL`. `dev/audit/harnesses/r10_solver_winner_polish.py` measured its realised one-day closed-loop money:
  - non-flat mean +0.1462 % cheaper, but 1 of 6 non-flat cells worse (winter_typical/winter_mild -0.99 %, bought with comfort);
  - flat-price null -0.7893 %.

  A stop change that loses money on a flat price is #1293's mechanism, so it is not shipped.

The finder harnesses therefore read identical at both ends (Figures). This PR leaves the measured quantity alone on purpose.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HpiHWwkH7UCPNpZbWu4JbC

## Head

`7527c746d9df8e4cd9f9171521f5f5557dc857e4`. Merge base `58730d09f61f3c26c86dad79387b0c2ffa739d66` (the branch is not re-merged; origin/main read `50808a755ce300fac4b19b7cfe7f89c795b8387b` at 2026-10-22T18:07Z; `git merge-tree --write-tree origin/main HEAD` exits 0 (`LEDGER-MERGE: resolved tests/closures.json`), and that move touches none of this diff's files). The round-2 commits sit on the reviewed head `47b6768c7` plus the bot's `a6e53320b` (`ci: pin killed mutants`):
- `ec321cb76`: `_lbfgsb_run` builds the fused fun from the batch objective with the one `_LBFGSB_FD_EPS` (O2). It adds the O1 bounds-gate check, the reference arm's own literal step and `class_excess_loc` 18269 -> 18268, recorded.
- `d8220dfc5`: `_memoized_value_and_gradient` takes a batch objective. Its `None` arm became unreachable once `_lbfgsb_run` builds the fun only with a batch, and it typed the result Optional, which `tests/typing_ruler.py` read as +1 `assignment` error at `ec321cb76`. The commit also deletes three `killed_by` pins that named removed or edited lines (`_lbfgsb_run` BOOLOP/GUARD_OFF `cddbb8d3`, `_memoized_value_and_gradient` GUARD_OFF `b306a38e`); `ci_predict.py` refused them as `STALE PIN`.
- `7527c746d`: deletes the survivor triage `_memoized_value_and_gradient` GUARD_OFF `a5f6c7fe` (verdict `equivalent`, "memo is None never happens"). That triage is now false: the start-moving runs pass `memo=None`, and the mutant is killed (Mutation proof).

The scoped gate was taken at `d8220dfc5`. `7527c746d` differs from it by one ledger file, re-checked with `tests/entities.py` and `tests/structure.py`. The block, the mutants and the flat null were taken at `d8220dfc5`/`7527c746d` (same `optimizer.py`), and `cont_fuse.py` at `ec321cb76`. Figures marked as round 1's are round 1's.

## Mutation proof

The block run is `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# -- R10-SOLVER: N-solve-recompute" "# -- R9 N-fit-integrator (#1672)"`. At head it prints `ALL 5 FEATURES BLOCK PASSED`. Each mutant was written to `optimizer.py` by a scratch runner and restored after its run; `filecmp` against the saved copy read `restored True`.
- A, `_lbfgsb_run`'s guard without `_bounds_supported_by_batch` (review O1): rc=1. FAIL `R10-SOLVER (O1): bounds _bounds_supported_by_batch refuses run on scipy's own estimate -- no batch call, the plain scalar run's point` [batch calls refused=3 served=4].
- J1, `_LBFGSB_FD_EPS = 1e-3`: rc=1. FAIL `(null, exact)` [max |dP| 2.146e+00 kW] and FAIL `(O1)`.
- J2, the fused gradient's step only -> 1e-3 (the review's mutant J, now at its one site): rc=1. FAIL `(null, exact)` [max |dP| 2.146e+00 kW].
- J3, the `eps` option only -> 1e-3: rc=1. FAIL `(O1)` [x 0.6995 vs plain 0.69995]. A fused run never reads that option, so only the scalar arm sees it.
- Review J as written (a start-site step) has no site left: `git grep -n "1e-4" -- custom_components/heatpump_optimizer/optimizer.py` names one step literal, the `_LBFGSB_FD_EPS` assignment.
- GUARD_OFF (`if False:`): rc=1. FAIL census precondition [{}] and FAIL `(O1)`.
- BOOLOP (`and` -> `or`): rc=1. FAIL `(O1)` [batch calls refused=3 served=4].
- The continuation passes `None` for the batch: rc=1. FAIL census precondition and FAIL `(positive control)`.
- The relaxed candidate passes `None` for the batch: rc=1. FAIL census precondition and FAIL `(positive control)`.
- Review G (`_lbfgsb_restart` passes `None` for the batch) passes the block: rc=0, `ALL 5 FEATURES BLOCK PASSED`, multi-start (6, 0). It is killed in the whole of `tests/features.py`: `PYTHONPATH=tests/hastub python3 tests/features.py` rc=1, `1 of 4306 FEATURE CHECKS FAILED`: FAIL `R9-F2.2 D9-s1-02: a batched solve never evaluates the scalar objective inside L-BFGS-B` [scalar calls inside minimize: batched 78, unbatched (null arm) 299].
- `_memoized_value_and_gradient`'s `if memo is None:` -> `if False:` (the site the deleted triage called equivalent): rc=1. FAIL census precondition [{'relaxed': (1, 0)}], FAIL `(null, exact)` [max |dP| 3.656e+00 kW], `AttributeError: 'NoneType' object has no attribute 'get'`.

Test first: the O1 check was written against the round-1 guard shape and goes red under A (above). The round-1 block on `738d950aa`'s `optimizer.py` read `{'relaxed': (1, 134), 'continuation': (1, 234), 'multi-start': (12, 0)}` and FAILed `... no L-BFGS-B run with a supplied jac simulates the scalar trajectory` (round 1's figure, reproduced by the reviewer's `ev/testfirst_revert.out`).

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` names three added sites:
- `custom_components/heatpump_optimizer/optimizer.py:784 GUARD_OFF` (`_lbfgsb_run`'s guard): left for `mutation-autofix`. Killed locally by the block (GUARD_OFF above).
- `custom_components/heatpump_optimizer/optimizer.py:784 BOOLOP` (`_lbfgsb_run`'s guard): left for `mutation-autofix`. Killed locally by the block (BOOLOP above).
- `custom_components/heatpump_optimizer/optimizer.py:735 CONST` (`_LBFGSB_FD_EPS`): left for `mutation-autofix`. Killed locally by the block (J1 above).
- `custom_components/heatpump_optimizer/optimizer.py:846 GUARD_OFF` (`_memoized_value_and_gradient`'s `if memo is None:`), unpinned by deleting its false triage: left for `mutation-autofix`. Killed locally by the block (above).

The three stale `killed_by` pins are deleted by hand, as `ci_predict.py` instructs (`mutation-autofix` never drops one).

## Null control

- Flat-price null, both arms, re-run in the reviewer's shape: `probe/rev-2612-b73e3ccc:ev/flat_null.py` (sha1 be8f89b66fd9ac33845bd19cbe9bacc4236a8eb4; the head adaptation, sha1 4c3c86476bfef42d2955db16f13d8e3d4db0476a, is a scratch probe). At the head, its `scalar_valued` arm takes the head's `_lbfgsb_run` signature and builds the gradient with `_fused_value_and_gradient(batch_objective, bounds, 1e-4)`. Its other three lines are unchanged. Run as `PYTHONPATH=tests/hastub python3 flat_null.py` at `a6e53320b` (the reviewer's file) and at `ec321cb76` and `7527c746d` (the adapted file), in this seat:
  - `prices=flat weather=winter_cold two_zone=True`: `identical=True max_dP=0.000e+00`, sha `282f8b7c5a56` in both arms at both heads.
  - `prices=flat weather=winter_mild two_zone=True`: `identical=True`, `f81494aeb061` in both arms at both heads.
  - `prices=flat weather=winter_cold two_zone=False`: `identical=True`, `e47e0996094f` in both arms at both heads.
  - Non-flat companion `winter_typical`: `identical=True`, `9b27e4b3a20d` in both arms at both heads.
  - The plan is byte-identical across O2 and between the arms. The hashes differ from the reviewer's (`f09d318e5598`, ...) because they were taken in another environment. Both ends here ran in this one: `/opt/hpo/venv-ci`, `OPENBLAS_CORETYPE=Haswell`.
- The block's own null, exact: its reference arm runs the pre-fusion shape and spells the 1e-4 step itself, and the solve ships the same plan bit for bit (`np.array_equal`). Positive control of the meter: the scalar-valued arm reads `{'relaxed': (1, 67), 'continuation': (1, 117), 'multi-start': (12, 491)}`.
- O1's null: on refused bounds, `_lbfgsb_run` returns the plain scalar run's point (`np.array_equal`) with 0 batch calls. Its positive control, the same run on finite bounds, makes 4 batch calls.
- The carried D9 null (equal total SSE on the single-zone no-hot-water case): `winter_single_no_dhw` reads horizons 1367.0 = 1367.0, scalar steps 864 = 864 and rows 1358 = 1358 at the merge base and at head.
- The carried P4 null (round 1's figures, at `738d950aa`, which is value-identical): `race.py` `flat_gap_rel_max=2.4769e-03` against `nonflat_gap_rel_max=1.0958e-01`, and `ftol_race.py` `polish_gap_max[flat]=0.0025 pct` against a winter max of 0.2281 %. The winner-polish arm's flat cells read -0.7893 % money.

## Figures

Seat venv `/opt/hpo/venv-ci` (python 3.14.7, numpy 2.4.6, scipy 1.17.1), linux x86_64, `PYTHONPATH=tests/hastub`. Base is the merge base `58730d09f` in its own worktree. Counts and objectives are deterministic. CPU was not re-taken quiet (load1 3.25 and 3.44), so this body states no CPU figure.
- D9 finder harness `dev/audit/rounds/round10/catchup/d9/cont_fuse.py` (sha1 434fa53cad1b3b84df7e4a87d112e96640261c66), run as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/d9/cont_fuse.py --reps 1` at base and at head:
  - base, `winter_two_zone_no_dhw`: prod 35757.0 horizon-equivalents against fused 35713.0 (delta 44.0); scalar steps 10080 -> 1632; rows 35652 -> 35696; `rewrites fused=1`; `plan_identical=True`.
  - head: prod 35713.0 = fused 35713.0 (delta 0.0); scalar steps 1632 both; `rewrites fused=0`. The shipped tree is the base's fused arm.
  - Nulls: `winter_single_no_dhw` 1367.0 = 1367.0 and `winter_two_zone_dhw` 38428.0 = 38428.0 at both ends.
  - Honest unit (the roster carry): per-gradient horizons. The saving is 44 of 35757 horizon-equivalents, which is 0.12 % of the solve's simulated horizons.
  - The relaxed candidate runs only under `clamp_planned_levels`, which this harness does not drive. The features block counts it: 0 scalar simulations at head, against the reference arm's 67.
- P4 step-8 enumerator `dev/audit/rounds/round10/D14/sweep-P4/p4_seams.py` (sha1 ddd96e1be09b730d89d5fa70311ef0ed5f2f1e69), run as `python3 dev/audit/rounds/round10/D14/sweep-P4/p4_seams.py` at head: `seams=12 stop=4 seed=8` and `positive_control={'D0-s2-01 main': False, 'D0-s2-01 restart': False, 'D0-s1-01 seeds': True}`. Round 1 and the reviewer read `seams=15 stop=7 seed=8` at the base.
  - Named route (fixer.md step 14): the two False rows are keyed on the enclosing function. The stop moved, unchanged at `ftol=1e-06`, into `_lbfgsb_run` (`STOP optimizer.py:_lbfgsb_run ... ftol=1e-06`). The instance is not closed.
  - Disposition of every head seam:
    - `_lbfgsb_run` STOP: D0-s2-01, duplicate of #1293.
    - `_scoped_minimize` x2: not applicable (the thread-scope wrapper).
    - `dhw_planner._plan_dhw_min_cost` linprog: not applicable (an LP).
    - `_optimize_space_only` SEED x3: D0-s1-01, duplicate of #1294.
    - `_solve_space` SEED x5: beyond the finding (sweep-P4), duplicate of #1294; its detector is carried (Forward-carry).
- P4 finder harnesses, round 1's figures at `738d950aa`, which this round does not re-run. Production is value-identical across round 2: the flat null above is byte-identical at `a6e53320b` and `ec321cb76`, and `env_drift.py` moves no scenario.
  - `dev/audit/rounds/round10/D0/s1/race.py` (sha1 8689b3208ce48451edb5f8e6c7fb5d9eec62384b): `cells=80`, `cells_gap_gt_1e-3=23`, `gap_rel_max=1.0958e-01`, identical at both ends.
  - `dev/audit/rounds/round10/D0/s2/ftol_race.py` (sha1 c8581979b9c3bad06f6190ba276ae7fcc782fcad): `polish_gap_winter_mean=0.0343 pct n=8 range=0.0000..0.2281`, identical at both ends.
- Seed-or-stop split `dev/audit/harnesses/r10_solver_seed_or_stop.py` and winner-only polish `dev/audit/harnesses/r10_solver_winner_polish.py`: round 1's figures (sha1 8181cc25 and 762c2aa1 at `f11459ced`; Description section 2). Round 2 changes only their call into the solver, for the dropped `fd_eps` keyword and `_lbfgsb_restart`'s batch-objective argument. The new sha1s are 0ef519d4bbfe25bd6a9de425ce98859733462b1f and 3d63c3fb2cbd3cb68b22e24d4e4ca0601430a0e2. They are not re-run this round.
- Scoped gate: `python3 tests/closure.py select --diff 58730d09f` gives `MODE: SCOPED -- 27 script(s) run, 6 scoped out`. Run as `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=58730d09f61f3c26c86dad79387b0c2ffa739d66 PYTHONPATH=tests/hastub bash tests/run.sh` at `d8220dfc5`: rc=0, every script `ok`. In detail:
  - `tests/features.py`: `ALL 4306 FEATURE CHECKS PASSED`.
  - `tests/env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 58730d09f...`. Nothing is claimed, and neither claim file is touched.
  - `tests/stress.py`: `54 of 54 scenarios judged ... 0 re-planned by this branch`; production calls `re-planned: []`.
  - `tests/optimality.py`: `ALL 84 OPTIMALITY CHECKS PASSED`. `tests/backtest.py`: `ALL 25 BACKTEST CHECKS PASSED`. `tests/entities.py`: `ALL 2388 ENTITY CHECKS PASSED`. `tests/typing_ruler.py`: `ALL 9` and `ALL 12`.
  - An earlier run at `ec321cb76` went red on `tests/entities.py` and `tests/typing_ruler.py` (Red checks); `d8220dfc5` answers both.
  - At `7527c746d`: `tests/entities.py` `ALL 2388 ENTITY CHECKS PASSED` (rc=0), `tests/structure.py` `STRUCTURE RATCHET PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `class_excess_loc` 18269 -> 18268, a decrease recorded in `ec321cb76`, and no raise.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL` (origin/main = `58730d09f` when run, at `7527c746d`).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted against 58730d09f61f`. It lists 4 unpinned sites (above) and no stale pin.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body> 2240 2250` at `7527c746d`: rc=0, `PRE-PR: 7527c746d9df8e4cd9f9171521f5f5557dc857e4 000000000000000000000000000`, with the unpinned-sites WARN answered above.
- `python3 -I tools/audit/carry_audit.py check --body <this body>`: `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`.

## Architecture score

n/a: no metric rises (`dS +0.0000 NULL`).

## Red checks

Every red check run on this branch's pushed heads, read through the check-runs API:
- `pr-contract` (on `2c9934737` and `47b6768c7`): the carry audit read 5 unrouted items in the round-1 body (the review's block). It is answered in this body: each Forward-carry and Friction item now carries a routable `Carry:`, and the satisfied R10-TARIFF precondition has moved under Evidence. Cheaper detector: `carry_audit.py check --body` runs in seconds before the body push. The predictor `body_push.sh` runs (`ci_predict.py`) reads the branch, not the body, so it cannot see this. Nothing new is owed beyond running the audit first, which this seat did (Figures).
- `mutation` (on `47b6768c7`): the two `_lbfgsb_run` sites round 1 added unpinned, which `mutation-autofix` pinned in `a6e53320b`; `mutation` is green there. This head adds four unpinned sites (Unpinned sites), so `mutation` is expected red at the push until the autofix pins them. Cheaper detector: `ci_predict.py` prints them before the push, so none is owed.
- `nightly-status` (on `47b6768c7`): not this PR's. It reads the nightly run's state, which this diff does not reach, and it is skipped on `a6e53320b`.
- Locally, round 1's scoped `tests/entities.py` red on four stale `killed_by` rows was answered in `c0b264338`.
- Locally, this round's first scoped run at `ec321cb76` had two reds. `tests/entities.py` went red on the two `cddbb8d3` stale pins. `tests/typing_ruler.py` went red on +1 `assignment` error: the Optional `_memoized_value_and_gradient` result was assigned to `fun`. Both are answered in `d8220dfc5`. Cheaper detectors: `ci_predict.py` (seconds) named the stale pins, and `tests/typing_ruler.py` (35 s) names the type error. Running both before the full scoped run would have caught both, at no new standing cost. Neither reached CI.
- To be expected at this push: `mutation`, for the 4 unpinned sites (Unpinned sites).

## Evidence

- R10-TARIFF's carry (`PeakBilling` via `HeatPumpOptimizer._peak_billing`) holds as a precondition: `git diff 58730d09f...HEAD -- custom_components | grep -c peak_cost` gives 0.
- Review O4: `Closes #2240` stays, on the orchestrator's decision. The roster's `fixes: [2240]` stands, and a re-measured duplicate disposition closes the class issue.
- Review O3 (mutant G) was already killed by the R9 D9-s1-02 block in the full suite. This round re-reads that kill (Mutation proof).

## Forward-carry

- **D0 (price optimality) brief, the next round's D0 seats.** A stop-tolerance change is refused on money (#1293). That covers the narrower winner-only polish measured here too: non-flat +0.15 %, but the flat null -0.79 % and 1 of 6 cells worse. A D0 challenger that tightens the stop, on all runs or only on the winner, is a duplicate of #1293 unless it shows realised closed-loop money that does not fall on a flat price (the `r10_solver_winner_polish.py` shape, flat null included). Re-measure at your merge base. Destination: `dev/governance/dimensions/D0.md` (Traps), which is policy and not in that group's file list yet. Carry: R10-BRIEFS-FOLD
- **D0/D14 detector (from sweep-P4, re-confirmed by `p4_seams.py` at head).** `_solve_space`'s DHW seed set is unguarded, because `tests/optimality.py`'s `_CERT_CELLS` holds space-only cells. The D0 brief should tell its detector seat to add DHW cells to `_CERT_CELLS` before reading a seed gap as closed. Carry: R10-BRIEFS-FOLD

## Friction

- fixes-vs-disposition: contradiction: the roster lists the P4 class issue under fixes, while RCA-BULK-1 section 4 and the owner's two refusals leave no shippable fix for either finding. Carry: dismissed: orchestrator decided Closes #2240 stands (review O4)
- finding-propagation: unenforced: a seat with handoff-only write access cannot land a carry into a policy brief (D0.md) or a roster, so both carries above go to the brief-fold group. Carry: R10-BRIEFS-FOLD
