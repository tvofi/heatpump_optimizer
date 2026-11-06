Design review: revise 964d7611a4d73a658ae7fe5428170a664393fa4b class-open

Reviewed design.md at 964d7611a from a detached worktree; base read at 28482eceeb6b9809e44b12d80fc994282cc21645. Note 2 of at most 5 (owner ruling tvofi 11-06 for R10-COMBI-TANK; the note's header still says "of at most 3").

Round-1 revise points, each answered:
- (1) class-open, answered. I re-ran `grep -n "dhw_tank_heat_loss_coefficient\|dhw_tank_thermal_mass\|c_dhw" custom_components/heatpump_optimizer/*.py` at base and got 55 hits. Every one is dispositioned:
  - battery.py:327/331;
  - coordinator.py:4232/4268/4277/4919;
  - dhw_learning.py:421;
  - dhw_planner.py:96/101 (`_tank_decay`), 247 (the context field), 373, 583-649, 691/720, 817-924, 972/1022/1086, 1367-1387, 1625-1723, 1817/1818, 2062-2148;
  - optimizer.py:5431/5665;
  - thermal_model.py:718/738/758 (the owner properties), 3119-3128, 3157/3194;
  - binary_sensor.py:273, a substring false positive.
  
  One combi-aware accessor (`ThermalParameters.dhw_store`) is owned by thermal_model.py, and the exo series is carried through `_DhwPlanContext`. A5 (aliasing the properties) is rejected for sound in-code reasons (the aggregators would double-count, and the `_dhw_ua_cache` key would change).
- (2) answered. battery.py:322-333 drops `dhw_tank` in combi. optimizer.py:5425-5433 and 5640-5665 skip the dhw term when the `two_zone_enabled` branch already counted the buffer; I read both branches at base and the rule is correct. coordinator.py:4206 litres_40c reads `store.volume_l`, and the standby readers 4232/4268/4277 read `store`. The "dhw_tank_volume unused" claim is withdrawn after a check of coordinator.py:2477 and services.py:478.
- (3) answered. The `lp_flux` arm checks that P_dhw moves with the space flux, with an off-arm null control. Invariant 2 is extended to `battery.build` and `_stored_thermal_energy`. The P2 census (tests/entities.py:4130 `_P2_CENSUSES`) gains `combi_store_view` (0 readers outside thermal_model.py) and `combi_flux_live`, which counts the five planner recursion sites.
- (4) answered. The re-estimate is +480-650 lines across 11 modules, so the note splits it: PR A R10-COMBI-TANK-STORE (L, unreachable parameter) and PR B R10-COMBI-TANK (M, after A). The learner gate rides with the option in B, which is sound by the note's own argument.

Revise point:
1. class-open, carry 0 (owner scope addition, D12-s1-01). The no-probe buffer bug is not designed, only deferred.
   - **Where it fails.** coordinator.py:6563-6567 in `_update_current_state` sets `state.buffer_tank_temperature` only on `buffer_reading.ok`. Without a probe the value is never advanced. The note lists this only as "Carry: orchestrator (item buffer-open-loop-seed)", with no fix shape, no tests and no size effect. The owner ruling makes the item scope, not a carry.
   - **Fix shape.** Add a §-section that names the site. The fix advances the buffer open-loop when no buffer probe reads ok, by the same mechanism the DHW branch above it already uses (coordinator.py:6555-6562): `_open_loop_plan_value(self._optimization_result, "buffer_temp_trajectory", dt_util.now())`. That helper is at coordinator.py:2315, and `OptimizationResult.buffer_temp_trajectory` is at optimizer.py:1886. The fix must be expressed through, or consistent with, `combi_tank_seed`'s order (buffer, else DHW, else open-loop), so that combi and non-combi share one seed path rather than two.
   - **Tests.** A failing test first: the fixture has no buffer probe and a prior plan whose buffer trajectory moves, and today `state.buffer_tank_temperature` stays at its default or its last value across cycles. A null control: the same arm with a buffer probe present must be unchanged. A mutation target: drop the open-loop branch.
   - **Placement and size.** Say which PR carries it. PR B is the natural home, because the edit lands in `_update_current_state` beside the seed after r10-livestate. If PR A carries it, say why it is safe before the option exists. Give its effect on the size estimate (about +15-25 lines, plus test). Ordering after r10-livestate then binds whichever PR carries it.

Fixer notes (carries, not revise points):
- Carry: R10-COMBI-TANK (item buffer-open-loop-nonstore). Decide whether the open-loop buffer seed applies to every two_zone buffer or only to `buffer_is_store`. A buffer whose trajectory is not planned has an empty `buffer_temp_trajectory`, so the helper returns None and the value must stay as it is, not be fabricated.
- Carry: R10-COMBI-TANK (item exo-sign-check). `_dhw_window_floors` is said to take space flux "through the recursions that check the floor, not needed_delta". The fixer should assert in `lp_flux` that a large valve draw before a window raises the floor-repair energy, so that a floor computed without exo cannot under-plan silently.

decision: orchestrator, after edges and hot files.
- PR A hot files: thermal_model.py, dhw_planner.py, optimizer.py, battery.py, coordinator.py (readers at 4206-4277 and 4919), dhw_learning.py, sensor.py.
- PR B hot files: config_flow.py, entry_config.py, const.py, topology.py, sensor.py, coordinator.py (`_update_current_state`, learners), tests/features.py, tests/entities.py.
- PR A edges: serialise A with R10-COP-GATE and R10-ADVISOR-WHATIF (optimizer.py, coordinator.py) and with R10-HEAT-METER (thermal_model.py).
- PR B edges: B goes after A, after R10-CONFIGFLOW-PAGES and after r10-livestate; carry 0 adds to the last of these if B carries it.
- No edge to R10-UX-HEALTH or r10-ceiling-probe.
- No open design/* note claims the tank seam (r10-livestate and R10-HEAT-METER do not mention buffer_tank_temperature or D12-s1-01).

The harness reports no token count for this seat.
