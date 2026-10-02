Fix review: merge e37cefc60a41b2cf2f134672b40dc02478dcd5a9

PR #1838, R9-F10.4. This is a delta review of a main merge. The last verdict was the carry at 46a70815. I measured e37cefc6, which is the PR head at posting: 46a70815 merged with main 492d8401 (#1839, R9-EG-B2).

## The merge is not a carry, so I judged its resolution delta

- `git merge-tree --write-tree 492d8401 46a70815` exits 1. It conflicts in coordinator.py, tests/features.py and tests/structure_budgets.json, where the ledger driver refused `coordinator_loc`.
- doc_claims.py, entities.py and seam_map.json changed on both sides but auto-merged.
- `git diff <merge-tree tree> e37cefc6` touches only the three conflicted files. See merge_check.txt.

**The three resolutions:**
- **coordinator.py:** the merge removes `last_optimization` and `next_optimization` (EG-B2's) together with `current_action` (this PR's). Nothing in custom_components, features.py or entities.py still loads any of them, or `floor_return_temp`.
- **features.py `_T6_PROPERTY_PAIRS`:** the union of both sides' deletions plus EG-B2's three views. That makes 7 pairs: mode, prices, dhw_temperature, optimization_running, thermal_params, thermal_model and away_state. The check's wording, "seven published properties and views", matches.
- **structure_budgets.json:** this PR's metric set, re-recorded with `--record`. At this head structure.py measures exactly the recorded values. Four rows fell and none rose:
  - coordinator_private_reach 89→74
  - dead_methods 3→0 (EG-B2 deleted the three)
  - max_class_loc 9003→8989
  - seam_cut_total 777→776

  recorded_at is c168ec0a, the merge base, and the ratchet accepts it.

## Measured at e37cefc6 (Linux, python3.13, strace closure recordings)

- structure.py: STRUCTURE RATCHET PASSED, with 41 counting rules. dead_methods=0, coordinator_multiassigned_attrs=120, 112 name-kept (113 before EG-B2's deletions).
- My field-collision probe: field_collision_unprinted=0. mutants.py: unmutated rc=0; 13 of 13 mutants red.
- doc_claims ALL 112 PASSED; deployment_shape PASSED; entities ALL 2060 PASSED.
- features ALL 3649 PASSED, including R9-F2.1 P3. The Mac's P3 failure (110.4366 vs 110.1297, the same on main) does not reproduce here, which is consistent with BLAS.
- `closure.py check --partial` over fresh recordings of those five scripts: rc=0, "committed closures cover every file this run touched".

Outputs are in this directory.

## For the orchestrator

- #1842 (verdict: merge b69961d7) is to merge first. Once it does, this PR conflicts with main in `.claude/workflows/brief_lint.mjs`, because #1842 conditions the pin line that this PR deletes. Either resolution keeps this tree's `briefs` green: #1842's linter passes on e37cefc6's tree, as 1842-review-b69961d7 measures. That merge comes back to this thread as a resolution delta.
- tvofi reviews #1838 himself. The four budget rows only fell, but budget-raise-gate reads the file, and tvofi's earlier approval at 46a70815 does not carry to this head.
