Fix review: merge bdf096245858f5a381b67719c4174d7a2880974d

bus-nonce: 52ad522da9fdbc591c3200100caa48da
pending-ci: gate

## Summary

Round 1 (first review; full scope). Head bdf096245858f5a381b67719c4174d7a2880974d is the PR head and the body's head; merge base 9fe63d00b59f100aea67267ddddc95522e164aa1. `git merge-tree --write-tree origin/main bdf09624` exits 0 with no conflict. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Evidence

- Mutation proof (step 1), run against the R11-SEAM-solver features block at the head (ev/mutation/). Unmutated: ALL 7 FEATURES BLOCK PASSED, rc=0. Each of the body's M1-M6 exits 1 on the named check. I added four mutants on the money path and all were killed by the D2-s3-01 check: M7 (`_solve_objectives` cost closure on `h.prices`), M8 (all three `_settle_horizon` prices back to `h.prices`), M9 (published `prices=h.prices`) and M10 (drop `raw_prices=raw_prices` from the `_Horizon` construction). M1's check covers both orderings of the 2:2 tie, so whatever the hash seed, one ordering fails under `max(set(...))`.
- Finder's harnesses (step 2), from the plan/r11 export at 819aa2e3. All four sha1s match the body. Each ran from a worktree at base 9fe63d00 and at head bdf09624, and offstart ran from a per-tree copy of D0/s3 with `offstart_out` deleted (ev/harness/):
  - slot_reason_hashseed distinct_tie: 2 at base, 1 at head. Null distinct_null: 1 at both ends.
  - m3_risk savings_inflation_lambda1_price_risk: 10.2015 at base, 0.0000 at head. savings_inflation_max: 30.8631 at base, 0.0000 at head. The lambda=0 cell reads 0.0000 at both ends.
  - offstart summer_negative_gap_cells: 17/60 at base, 0/60 at head. Null flat_gap_cells: 0/60 at both ends.
  - wood_seeds --census census_cells_all_but_one_start_zero[prod]: 32 at base, 4 at head. The 4 are the summer_warm/6h cells at kWh_shipped 0.000.
  - Every figure matches the body. The body measured against bc658f9d and 661c624c; I measured against the current merge base and head, with the same result.
- Golden (step 4): `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 9fe63d00...` at the head prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. Both claims moved: `CLAIMED price_risk: 50 leaves moved` and `CLAIMED start_below_band: 218 leaves moved` (ev/env_drift_all.txt). This ran under the Haswell kernel pin only. I did not re-derive the body's four-kernel objective_value figure.
- Version (step 5): the three-dot diff does not touch VERSION, manifest.json or RELEASE_NOTES.md.
- Metrics (step 14): `tests/structure.py` at the head prints STRUCTURE RATCHET PASSED. The class_excess_loc re-record (17382 to 17360) is earned: the start-set block moves out of the `HeatPumpOptimizer._optimize_space_only` method into the module-level `_space_only_starts`. `archscore --diff 9fe63d00` reads dS +0.0000. The two deleted ledger pins are lines this diff rewrote, `return energy_cost_of` and the `if two_zone_enabled:` statement; see Findings for the second.
- Class (step 6): the body enumerates `_multi_start_minimize(` call sites by grep, because the finder's sweep-P4 enumerator is absent. Three are closed in the diff, and the DHW warm-started calls are dispositioned, with offstart DHW cells at 0/60 at the head. A scout listing of every `h.prices` reader left in optimizer.py finds only objective-side reads: run candidates (`_run_plans`), reason classification and objective construction. No money figure reads the premium.
- Actuator (step 16): the diff adds no refusal on any actuator write.
- Not re-derived: the wood_seeds `--race` gap_abs figures (7 cells) and the four-kernel `start_below_band` objective drop. I cite both from the body.
- CI: ev/classify.log holds the `merge_train.py classify bdf09624 --pr 3736` lines read during this review.

## Findings

- Follow-up: the two-zone deep low-energy anchor's gate is now pinned by no ledger entry and killed by no test. I mutated `(_DEEP_LOW_ENERGY_START_FRACTION,) if model.params.two_zone_enabled else ()` to `if False`. At the head, tests/optimality.py reads ALL 84 OPTIMALITY CHECKS PASSED and tests/golden.py reads NO UNCLAIMED DRIFT, so the mutant survives (ev/targeted/). The same mutant at the base, the single `if self.model.params.two_zone_enabled:` at optimizer.py:5543 set to `if False:`, also passes all 84 optimality checks. So the deleted pin's claim, "killed by tests/optimality.py", was already stale before this PR, and the PR does not cause the survivor. The ternary also draws no GUARD_OFF mutant from the mutator, so nothing will report it. Carry: dismissed: pre-existing at the base, not this diff's; carry_audit names no live roster group after R11-SEAM-solver to receive it (R10-LEDGER-RESIDUE is done), so the orchestrator routes it at the next roster
