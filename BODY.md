R10-OVERBOOK-RESIDUAL refutes the #2499 residual. The over-booking was in the reference, not in the plan. The harness's DP reference (`dev/audit/harnesses/r10_demand_overbook.py`, `_dp_reference`) priced comfort against one flat band, `target_temp` 21 with floor `min_temp` 20, at every step. The solve prices the day/night schedule that `OptimizationConfig.get_comfort_temp` / `get_temp_bounds` return: target 19.5 and floor 19.5 outside 07:00-22:00. So the reference read the night setback the solve is allowed as a breach and a pull deficit, and it priced the plan's pre-heating ahead of 07:00 as waste. With the reference reading the solve's own per-step schedule from `HeatPumpOptimizer._build_comfort_bounds`, the one site that builds it, the flat-price arm's plan reads plan_kwh at the DP's and the plan's cost equals the DP optimum. The owner arm's plan costs less than the relaxed DP on the same objective.

No production code changes. The diff corrects the instrument and adds the cross-check that would have caught it: `_production_cost` scores the plan on the optimizer's own full objective (`_solve_objectives`, captured from a real `optimize`), and the row prints it as `prod_cost` beside the reconstruction's `plan_cost`. When the two disagree, the reference measures a different problem.

Refs #2499. The group's roster entry (`R10-OVERBOOK-RESIDUAL` on `handoff/audit-r10-roster`) lists #2499 in `fixes`, but main's in-tree roster does not carry that entry yet. Until it lands, `tools/pr/prepr.sh` step 7's preflight, which derives its intended list from `dev/programme/rosters`, refuses a closing keyword on that issue because no group there names #2499 in `fixes`. The closing keyword is the orchestrator's to restore once the roster merges.

Carry 1 is answered by refutation. That is the brief's carry from R10-STORE-RACES / #2887, null 11.78 against 9.88 and owner_i01 5.37 against 3.88. Both arms were re-run at this merge base before any figure here was quoted, and `## Figures` shows them at both ends. The flat-price arm now reads plan_kwh within the DP's. The owner arm's remaining kWh difference costs no more on the same objective, so it is not price-side either. The precondition on `valve_charge_demand` does not bind here, because both arms are unvalved and this diff quotes no savings figure.

## Head

Code head `91a7c9c2e727c59e523af81faae212dd3aa17b50`, cut from origin/main `c3a279e3252a8b57bb00b5a677318cd4fe20387f`, which is also the merge base. Every figure below was measured at this head or at that base, on numpy 2.5.4 / scipy 1.18.1: the `tests/requirements-ci.txt` pins, after `tools/audit/seat/cloud-setup.sh` refreshed the environment's venvs, which had been behind them (numpy 2.4.6 / scipy 1.17.1 before the refresh). origin/main had not moved at the handoff, so `prepr.sh` was not re-run after a merge.

## Mutation proof

The fix is the harness's comfort schedule. Mutant: the per-step `targets, floors, ceilings, bands` in `_dp_reference` replaced by the flat `cfg.target_temp` / `cfg.min_temp` / `cfg.max_temp` band they replaced, from a scratch copy, run as `--one null --dp`. The mutant reproduces the base reading exactly: `dp_learned` gap 0.2601, dp_kwh 8.62 against plan_kwh 10.74. Its own cross-check flags it: `plan_cost` 20.384 against `prod_cost` 17.801. Restored, the head reads gap 0.0 with `plan_cost` = `prod_cost` = 17.801. No `custom_components/` line changes, so there are no production mutants and no golden claims.

## Null control

The unmodified tree (origin/main's harness, sha1 `f0575c58b587d9a41e922fb5393e1a30a7ddba0b`) at the merge base: the null arm reads `dp_learned` dp_kwh 8.62 against plan_kwh 10.74 (gap 0.2601) and `dp_true` dp_kwh 9.00 (gap 0.2928). The owner_i01 arm reads dp_kwh 3.75 against plan_kwh 5.27 (gap 0.158; `dp_true` gap 0.1598). The plan is the control for the reference: plan_kwh, plan/deliv, the learned scale and the per-day series are identical at both ends (null 10.74, 1.165, 0.98; owner 5.27, 0.854, 0.616), because only the reference changed. The perturbation that shows the corrected reference still detects a worse plan is the base reference's own DP schedule. Scored on the production objective it costs 19.744 against the plan's 17.801. So the plan beats it, and the flat-band "optimum" was not optimal on the solve's objective. That figure comes from a scratch probe and not from an in-tree instrument. The in-tree equivalent is the `prod_cost` cross-check above.

## Figures

All rows: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py --one <arm> --dp`. Head harness sha1 `edc0b3c076a8fd4ad62db1defcb5a8a79ddc0281`; base sha1 `f0575c58b587d9a41e922fb5393e1a30a7ddba0b`. A field name below is the name the harness prints. gap = (plan_cost - dp_cost) / dp_cost on the DP's relaxed objective, and is >= 0 up to the (room, slab) grid's interpolation error.

- null (flat prices, unvalved), base: dp_learned dp_kwh 8.62, plan_kwh 10.74, gap 0.2601; dp_true dp_kwh 9.00, gap 0.2928.
- null, head: dp_learned dp_kwh 10.75, plan_kwh 10.74, gap 0.0, plan_cost 17.801 = prod_cost 17.801; dp_true dp_kwh 11.00, plan_kwh 10.74, gap 0.0. This is the brief's close condition: the flat-price arm's plan_kwh is within the DP's.
- owner_i01 (flat prices, owner pump shape, idle 0.1 kW), base: dp_learned dp_kwh 3.75, plan_kwh 5.27, gap 0.158.
- owner_i01, head: dp_learned dp_kwh 4.50, plan_kwh 5.27, gap -0.0006, plan_cost 10.087 = prod_cost 10.087; dp_true dp_kwh 4.12, gap -0.0012. The plan books more kWh than the DP's rollout at a lower cost on the same objective. The extra energy buys pull and terminal value that the objective prices, so it is not over-booking against the reference. A negative gap is the DP grid's interpolation error, which is the bound the docstring states.
- plan/deliv, the closed-loop ratio the carry quoted, reads 1.165 (null) and 0.854 (owner) at both ends. It compares two 12-hour plans with the energy one day delivered under receding-horizon replanning. It is not measured against any optimum, and its sign differs between two flat-price arms, so it is not an over-booking measure. It is left as printed.
- The carry's figures (null 11.78 against 9.88; owner 5.37 against 3.88) were snapshots at #2887's head on the stale toolchain. Re-taken at this merge base, they are the base rows above.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The four `tests/run.sh` `run_always` lines were run by hand and passed: `tests/env_drift.py --claims-only origin/main`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py`. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Class census (fixer step 8). Rule: `git grep -nE "target_temp ?- ?[a-z_.]*min_temp" -- dev/ tools/ tests/*.py` (a flat comfort band rebuilt outside the solve) and `git grep -n "_COMFORT_PULL_SINGLE_ZONE\|_COMFORT_PULL_TWO_ZONE" -- ':!custom_components'` (the pull rebuilt outside the solve). At the base, the first returns this harness's `band = max(cfg.target_temp - cfg.min_temp, 1.0)`. At the head it returns nothing. The second returns: this harness, closed in this diff; `dev/audit/rounds/round9/D9/s1/comfort_rowloop.py`, already guarded because it takes `comfort_band` as the solve's per-step array and builds none; and `dev/audit/rounds/round3/D0/reports/verify-2.md` and `dev/audit/rounds/round5/D0/seat-a/patch_f1b.diff`, which are records, not instruments.

## Architecture score

n/a: no production file changes. The diff is one audit harness.

## Unpinned sites

n/a: no `custom_components/` or `tools/` site added. The harness's `_production_cost` is its own cross-check and is exercised by every `--dp` run above.

## Red checks

none

## Forward-carry

n/a: the finding is the harness's own correction and lands in this diff, in the `_dp_reference` and `_production_cost` docstrings, which every later seat that re-runs or copies the reference reads. The census in `## Figures` returns no other reference that needs it, so no later stage's brief changes.

## Friction

none
