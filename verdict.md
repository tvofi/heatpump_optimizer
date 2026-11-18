Design review: approve 221c246eceaaf173d75140abc16600f489721667

Base judged: 8751943e17ef4d3ec699e7859ae829b4528d8ce7; plan of record 819aa2e354b4 (ADR-007, COMPONENTS.md, PLAN.md). Design ref unmoved from the handoff SHA at review.

1. Seam: a learners-seam module importing `const` and `thermal_model` only matches COMPONENTS.md "learners read plant model and kernel"; `learner_newton_step` and `reanchor_heat_loss` are at thermal_model.py:3044 and :3138; the coordinator keeps clock, freeze, baselines, apply, counters and store write. No new write path into another module's state. Pass.
2. Shape: no finding (ADR-007 refactor). The two behaviour moves (re-anchor log records under the new module's logger; gains fold returning a new list) are each stated with why they move. tests/entities.py:2824-2839 pins `house_loss_confidence is coordinator_module.house_loss_confidence` and `HOUSE_LOSS_MAX_STEP`; the note's re-import under today's names keeps it. Pass.
3. Sibling sites: `git grep -E '^    (async )?def (_async_learn_|_fold_|_reanchor_|_close_fabric)'` on coordinator.py at the base prints 13, as the note states; the two same-form folds left out are routed `decision: orchestrator` (§5). No other design/* ref names `fabric_learning` or any moved method. Pass.
4. Evidence plan: harness drives `_async_learn_house_heat_loss(c._close_fabric_interval())` and `_async_learn_buffer_cooling(temp)` (m3_learner_freeze.py:177, :210 at 819aa2e354b4), which the shape keeps with their signatures, so it runs at both ends; goldens and both claim files byte-identical is right for a no-arithmetic move. Pass.
5. D7 / siblings in flight: hot files overlap only by the PLAN.md hot-file order; no open design claims the learners seam's fabric folds. Pass.
6. Cost: one new module, coordinator.py, tests/features.py, structure files and closures, one PR as fixer note 3 requires; fits L. Pass.

decision: orchestrator — ADR-007 Consequences expects `coordinator_attrs` to fall; this cut leaves the baselines in the class (design.md §4, first alternative), so it does not. The plan's consequence or the cut is the orchestrator's to settle; the measured F = 48 against ADR-007 part 4's 28 is the figure the running budget takes.

Notes for the fixer
- design.md §1 says m3_learner_freeze is "in neither this tree nor plan/r11"; its source is at dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py on 819aa2e354b4 (`git ls-tree 819aa2e354b4 dev/audit/rounds/round11/D7/s2/`); run it from there at both ends. Carry: R11-ARCH-fabric-learner (item 7b2e1d01)
- tests/mutation_ledger/killed_by/coordinator.py/ holds rows anchored on the moved units (`_async_learn_buffer_cooling`, `_async_learn_house_heat_loss`, `_fold_internal_gains`, `_house_heat_loss_anchor`, `_reanchor_house_heat_loss_scale`, `_house_loss_terms`, `_learned_zone_temperature`, `_zone_capacity`, `house_loss_confidence`); the move re-keys or drops them, so read the drain's result for those rows and the new module's kill rate against ADR-007's fitness function. Carry: R11-ARCH-fabric-learner (item 7b2e1d02)
- tests/seam_map.json:119 maps `_house_heat_loss_anchor`, which the design deletes; reseed or drop the entry with the deletion and confirm `tests/structure.py` reads the map clean. Carry: R11-ARCH-fabric-learner (item 7b2e1d03)
- `_buffer_cooling_bounds` (coordinator.py:5465), one of ADR-007's thirteen, stays in the class as the fold's `bounds` argument (spike/arm.py:64 at 63adc6a4a1); §5 does not list it among the methods read and left whole. State it in the PR body. Carry: R11-ARCH-fabric-learner (item 7b2e1d04)
