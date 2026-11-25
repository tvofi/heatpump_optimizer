Fix review: merge d3c3822391902e517e24c0c2ccb18948a7e709d2

bus-nonce: 02eb7d64e37c709095ac14472eab7523

Round 4. This is a delta review over the reviewed head 4f0f2a8cc648f63395e36c795f11f8c9b63efbb4. Scope: `git diff 4f0f2a8c d3c38223` and the round-3 items.

## Evidence

- What moved the head: `a56c67a363 ci: pin killed mutants` (github-actions bot) and `a586328d78 ci: pin killed mutants (supply_hold.py:181 RETURN_DEL)`, merged as d3c3822391. The delta is nine new files under tests/mutation_ledger/killed_by/, `{anchor, killed_by, old, reason}` each. It touches no production, test, docs or policy file (ev/delta.stat).
- Each pin's `old` line matches exactly one line of its anchored file at the head (ev/pin_sites.txt, 9 of 9). Each `reason` records the `mutation_table.py --pin-killed` rc 0 -> 1 transition of its named killer.
- The PR's own diff against its merge base is line-identical to 4f0f2a8c's for custom_components, tests/features.py and docs (ev/pr_diff_compare.log). So round 2's production and test findings and its mutation proof carry unchanged. Items 1-3, resolved in round 2, stay resolved.
- Round 3 left `tests / mutation` red as `MUTATION TABLE REFUSED -- 9 added by this diff`. These nine pins are its repair. `merge_train.py classify --pr 3864 d3c38223` printed `GREEN ... pending: none red: none` (rc 0; ev/classify.log).
- supply_write RETURN_DEL (`return None` -> `pass`) is pinned to tests/typing_ruler.py, not to a behaviour test. Deleting an explicit `return None` changes no behaviour (the function returns None either way), so the mutant is equivalent at runtime and only the return-annotation ruler can see it. Main carries 24 typing_ruler pins of the same kind. This is not a finding.
- An independent re-run of three pinned mutants through tools/audit/seat/features_block.py was not possible. `--emit-prelude` raises `TypeError` at a module-level statement of tests/features.py at this head (ev/prelude.log, ev/mutants.txt), and the base run fails the same way, so those mutant lines are void. A full tests/features.py run per mutant takes 1.3-2.5 h on this host under load. The CI mutation job at the head is the pin's check of record.
- `git merge-tree --write-tree origin/main d3c38223`: rc 0, with tests/structure_budgets.json resolved by its driver (ev/merge-tree.txt).
- Head moved while this was under review: af0a65d34c is two bot `ci: merge main` commits over d3c38223. The PR's own diff at af0a65d3 against its merge base dc5face1f6 differs from d3c38223's only in tests/structure_budgets.json's rebased values. The same downward moves apply (class_excess_loc -7, max_class_loc -7, module_excess_loc -11) plus recorded_at. Live classify at af0a65d3: `WAIT ... pending: gate red: none`.
Carry: dismissed: evidence, not a finding
