R10-STORE-RACES. Part of #2248, Part of #2249, Part of #2674 (the roster's `fixes` is empty, so no closing keyword here). Every defect this group was briefed to fix is already fixed on `main`, by two earlier pull requests. This PR measures that at both ends and adds the class's missing enumerator. That enumerator is a census of the setup refresh against every store read the constructor spawns. It is red at the tree before #2817 and green at this head.

- **#2248** (N-restore-race, finding L3): #2675 (R10-LIVESTATE) fixed it. The finder's harness reads 3 of 3 interleavings differing before #2675 and 0 of 3 at this head.
- **#2249** (N-order-coupling, D7-s4-8x-fabric): #2817 (R10-PARAMS-OWNER) fixed it with one `_close_fabric_interval`. In the swapped order, the lower-floor learner's samples after 12 intervals read 0 before #2817 and 12 at this head.
- **#2674** (seven per-cycle store-load leads): #2817 fenced the two writers that reach the setup refresh (the price shape, and the legionella observer `async_track`). The other six are closed by a first-refresh gate. Each reads `fresh_call_writes=0`, and each gate-open arm reads lost=1 with null=0, so each is closed by that gate and not by a dead probe. The issue's own recipe says such a reading closes the lead, and its carry refuses a fix without a reproducing probe.
- **The class enumerator** (fixer.md step 8; #2248 and #2249 both say `Enumerator: none`). The census is in `tests/features.py`, beside the `_RACES` block. It holds each store read the constructor spawns, alone, across the setup refresh. It then compares the coordinator against the serial order (read first) over every attribute, or per-coordinator side table, that a load assigns. That state is found by diffing, not from a list.

  A held read is alone because reads land in no fixed order. A first all-reads-at-once version passed both fence-deletion mutants: the legionella read's fence held the refresh until every read had landed. The census also asserts its own preconditions. Every store built is read at startup, every read lands a previous run's payload, and the loads assign state.

  The census covers the setup-refresh window only. A later cycle could race only a read still in flight one update interval after setup. The six gated leads' gate-open arms show what that would cost; this PR builds nothing for it.

**Carries handed back, not worked (out of this seam).** This group is ordered "after R10-BUFFER-STORE (same store seam)". That group's store is the buffer tank as a heat store in `optimizer.py`. It is not the persistence store. Its three carries are optimizer work, so they are outside this group's seam and its ~400-line bound, and I have not worked them. The #2499 residual still reproduces at this merge base: the owner arm books 5.48 kWh against the DP's 4.12 (learned model) and 3.88 (true house), and the flat-price null arm reads plan/deliv 1.198. They are re-routed in the carry section at the end of this body, each to an open group on `handoff/audit-r10-roster` that owns `optimizer.py`, or to the issue's own owner. The orchestrator re-routes any a group declines.

## Head

1e4284bb5 (code head; measured on it and on its parents as stated per figure). Merge base 88c6ad5bbec69bfe157e04597a74d0c9c3e4775c, `origin/main` at measurement.

## Mutation proof

No production line changed, so the mutants delete the production fences the census pins. They were run with the census harness at 1e4284bb5 in a separate checkout, restored after each:

- M1: delete `await self._price_model_store.async_wait_for_read()` in `_async_learn_price_shape` (coordinator.py, 0 added / 1 deleted). Red: `no write in the setup refresh is lost to a store read still in flight (#2248, #2674)`, with `census_lost heatpump_optimizer_test_entry_price_model -> _price_learner`.
- M2: delete `await self.store.async_wait_for_read()` in `LegionellaGuard.async_track` (legionella.py, 0/1). Red: the same check, with `census_lost heatpump_optimizer_test_entry_dhw_legionella -> _ctx`.
- Failing first: at c78df2b86, `main` before #2817 merged, the same check is red on both stores at once (`census_lost_total=2 of 12`).

## Null control

- The serial arm is the reference every held arm is compared against: the read lands before the refresh.
- The census's own null control is the third check: every read held at once with `QuarantiningStore.async_wait_for_read` removed must differ. It reads `census_unfenced_differs=_ctx,_price_learner` at 1e4284bb5, so the window reaches writers, and a 0 on the second check is not blind.
- The census compares no field named `*_cache` or `*_memo` (fixer.md step 14: the key is the field-name suffix). 9 fields match today, all memoisation: `_buffer_ua_cache`, `_dhw_inlet_cache`, `_dhw_pattern_cache`, `_dhw_ua_cache`, `_factor_memo`, `_grid_fee_cache`, `_layout_cache`, `_simulation_cache`, `_wood_ua_cache`. Without the exclusion, three held reads differed only in `_dhw_*_cache` and `DefrostDerate._factor_memo`. A state field given one of these suffixes would be blinded; that is the entry's risk, stated here.
- The finder harnesses carry their own nulls: l3 `serial_vs_serial differ_total=0 of 3`, and `r10_store_load_leads.py` `null=0` on every arm.

## Figures

- census at the head, with the rule "per held store key, load-assigned state differing from the serial order": `census_stores_held=12`, `census_lost_total=0 of 12`, `census_unfenced_differs=_ctx,_price_learner`. Command: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_store_races_census.py` at 1e4284bb5.
- census before #2817: `census_lost_total=2 of 12` (price_model -> `_price_learner`, dhw_legionella -> `_ctx`). Command: the same harness from a checkout of c78df2b86, with `--features` pointing at this head's `tests/features.py`.
- #2248 L3, rule "of 3 interleavings, those whose final state differs from the serial order": 3 of 3 at d5dc3e26a (before #2675), null 0 of 3. Command: `PYTHONPATH=tests/hastub:custom_components python3 $EXPORT/dev/audit/rounds/round10/catchup/leads/l3_restore_race.py` (sha1 18240ea0d63509a2a9025ebbc635857c2835c307); it cannot drive the head's restore signature. At the head, its port reads `l3_differ_total=0 of 3`, `l3_null_differ_total=0 of 3`, `probe_lost_midload=0`. Command: `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_livestate_restore_race.py` (sha1 929edc4603d76757d7b471b8f5411e3b6e3f4384).
- #2249, rule "lower-floor samples after 12 intervals, swapped order house,lower": 0 at c78df2b86, 12 at 88c6ad5bb (both orders 12). Command: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-b/v2_s4_fabric.py` (sha1 0bcd55bf73ced3cb8aab6faeb44bee4eea8e2f3c).
- #2674, rule "per lead, writer's increment absent after the load resolves", at 88c6ad5bb (production code identical at 1e4284bb5): `price_shape_lost=0 null=0` and `extra_legionella_observer_lost=0 null=0`. Six leads are `closed_by` their gate with `fresh_call_writes=0`: buffer_cooling, dhw_dynamics, legionella_cycle, energy_totals, ledger and accuracy. Their gate-open arms read `lost=1 null=0`. Command: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_store_load_leads.py` (sha1 9b69a689bda785ea14769dc8d42858a493cacbde).
- Class seams, by the census's enumeration (the stores the constructor builds = the reads held = 12): accuracy, away, boost, dhw_draws, dhw_legionella, dhw_profile, energy, ledger, manual_plan, price_model, snapshots, thermal_learning. Disposition: every one reads 0 lost at the head. Of these, price_model and dhw_legionella are closed in #2817, and away, boost and manual_plan are fenced by #2675. The rest are closed by a gate the setup refresh cannot open, or touched by no setup-refresh writer. User-command writers are item ls-r1, closed in #2817's `_RACES` checks. Same command as the first figure.
- #2499 carry, at merge base 88c6ad5bb: `owner_i01` plan_kwh 5.48 against dp_learned dp_kwh 4.12 and dp_true 3.88; the `null` arm plan/deliv 1.198 (scale 0.993 against a true 1.0). Command: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py --dp null owner_i01`.
- Gate at 1e4284bb5: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/features.py). Command: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. Both scripts pass, and so do the run_always scripts (env_drift `--claims-only`, `closure.py selftest`, layout, harness_headers). `tests/structure.py`: STRUCTURE RATCHET PASSED. `env_drift.py --all` against the merge base: NO UNCLAIMED DRIFT. `tools/pr/ci_predict.py --base origin/main`: no red predicted after `--apply-inert`.
- Census cost inside features.py: one previous run of four full cycles, plus 14 setup refreshes. Instrument: `time` around the census harness command above.

## Red checks

none

## Forward-carry

- The 2.5x CPU cost of the live buffer store, and the 272 s owner-box outlier: a bound or warm start on the planner must earn it (R10-BUFFER-STORE carry, `optimizer.py`). Carry: R10-COP-PARTLOAD
- The inline 35 L buffer fallback in the two-zone and batch steps, left to the group that next prices that family in `optimizer.py`. Carry: R10-COP-PARTLOAD
- The #2499 demand over-booking residual, which still reproduces at this merge base (figure above: owner arm 5.48 kWh against the DP's 4.12 and 3.88; null arm plan/deliv 1.198). Carry: #2499

## Friction

finding-propagation: contradiction: R10-BUFFER-STORE's three optimizer carries were routed to R10-STORE-RACES because both briefs say "store", but one means the buffer tank as a heat store and the other the persistence store. Carry: dismissed: a one-off routing slip, re-routed in this body's Forward-carry
