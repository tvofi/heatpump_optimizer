Fix review: blocked a36a6a7337caace6620468df55fdc1aca2dcc0ec regression: legionella.async_observe no longer runs the disinfection follower, so a cycle that raises before the step tail leaves the boost bound and the disabled-disinfection switch-off unenforced once the plan is stale

bus-nonce: 276ff1485f820e9addbbd9cc7ab9a895

## Block

- Path: `custom_components/heatpump_optimizer/legionella.py` `async_observe` (the line `await self.async_track_cycle(dhw_temp)` replaced by `self.tank_c = dhw_temp`). The follower now runs only from `coordinator._async_step_tail`: in the cycle at coordinator.py:6057, after `_fetch_tibber_prices`, the solve and `_apply_action`; and from the step tick, which `pump_arbiter.step_gate` refuses on a stale plan.
- Risk: at the base the follower ran on every poll from `_update_current_state`, before any fetch could raise. At the head a cycle that raises before line 6057 runs no follower. That covers the Tibber outage latch's `UpdateFailed`, and any solve or weather exception the generic handler turns into `UpdateFailed`. Once the plan goes stale the tick runs none either. While a disinfection boost is commanded, the switch the follower owns then stays on. Three things go unenforced: `DHW_LEGIONELLA_BOOST_MAX_HOURS`, the switch-off when disinfection is disabled, and the idle switch-off retry. They stay unenforced until a cycle succeeds again. `off_restore`'s stale-plan hand-back does not cover the legionella switch (`_plan_let_go` names the supply, the space pump, the frequency and the valve).
- CI would not catch this. The PR changed the follower tests' driver `_g5_tick` (tests/features.py:62407-62414) so that it calls `async_track_cycle` itself after `_update_current_state`, with the comment "The follower runs in the step tail since observe stopped driving it". The coordinator's own cycle path, which those checks used to pin, is no longer exercised, and no check drives a failed cycle. The body names no release for this path (fix-review.md step 16).
- Evidence: `ev/obs_probe.out`. The same probe drives `LegionellaGuard.async_observe(55.0, …)` at each end. Base: the follower ran (`('cycle', 55.0)` recorded). Head: it did not run. `ev/cycle_order_head.txt` shows the head's cycle order. `ev/observe_and_g5_tick.diff` shows the moved call and the adapted test driver. I did not complete a full-cycle run that makes the price fetch raise (`ev/failed_cycle_probe_block.py`): `features_block.py --emit-prelude` was still resolving names after 30 minutes and was stopped. The failure path is established from the code order and the direct probe.
- What would resolve it, for the fixer to judge: keep the follower on the observe path, or in a best-effort step that runs whether or not the fetch succeeds, with the step tail not running it twice per cycle. Add a check that drives `_async_update_data` with `_fetch_tibber_prices` raising past the boost bound and expects the switch off.

## Findings

- Residual: the departure from the approved design for D16-s1-05 (no `FakeServices` stub change and no `tests/ha_contract.py` row; production refuses before the call through `inputs.delivers_to`, which block A pins) is raised by the body for a ruling. This review did not rule on it, and it was not reached as a block. Carry: dismissed: the body's own item, routed by the body to the orchestrator's ruling

## Evidence

- Round: the first verdict on this PR. The packet's `## Review scope` reads `full`: no verdict on `verdict/3897` names the reviewed head 0362d010.
- Merge with origin/main d9100de781: `git merge-tree --write-tree origin/main a36a6a73` rc 0. Each driver reported `LEDGER-MERGE: resolved` for `tests/structure_budgets.json` and `tests/closures.json` (`ev/merge_tree.txt`). GitHub's `mergeable_state: dirty` is the driverless computation.
- CI: `merge_train.py classify a36a6a73 --pr 3897` printed `WAIT a36a6a7337caace6620468df55fdc1aca2dcc0ec pending: gate red: none` from 22:33 to 23:12 UTC (`ev/classify.txt`). The only check run at the head is `arm` (skipped). No owed red exists to answer.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden are untouched over the three-dot diff (`ev/version_claims_untouched.txt`). `tests/structure_budgets.json` only lowers rows (class_excess_loc, max_class_loc, module_excess_loc, seam_cut_total). No budget is raised.
- Production diff read in full: arbiter_record.py, circulation.py, coordinator.py, inputs.py, legionella.py, pump_arbiter.py, setpoint_check.py and store.py.
- Not re-run because the block stands first: the body's mutation proof, its targeted mutants, and its finder-harness figures (cells.py, repairs_surfaces.py, the r11_* ports). They are not verified by this review.
