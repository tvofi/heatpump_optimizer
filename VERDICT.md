Fix review: merge 1a0d13512588f35397993818aad8d566bf96afbc

bus-nonce: 5f4b62ab32292f4dc741daadb5451479
pending-ci: gate

## Scope

Delta round over the previous merge verdict at 2c1ab82218a2859fde885beb590db3a279651756. The rendered packet read `## Review scope: full` only because the dispatch passed the head itself as `--reviewed-head`; the scope taken is the brief's: `git diff 2c1ab822 1a0d1351`, which is main merges (through dbdc520e86, #3841, and 3ee06864da, #3900) and their resolutions. The production (custom_components/) delta is nil, so the scope is not widened.

## Evidence

- Production lines unchanged: the PR's own +/- lines under custom_components/ (merge-base..head) are byte-identical at 2c1ab822 (merge-base bb6377b4) and 1a0d1351 (merge-base 3ee06864): 596 lines each, `cmp` equal (ev/prod-2c1ab822.lines, ev/prod-1a0d1351.lines). Both heads: 13 production files, +526/-70.
- tests/closures.json resolution is the union: for every one of the 34 scripts, the head's closure equals main's closure ∪ the previous branch head's closure; 0 non-union entries (ev/union.py, ev/pairs.txt).
- tests/deployment_shape.py's selection-cost count, re-derived with tests/entities.py's `_d308_pairs` predicate (Jaccard >= 0.80 over custom_components closures, 34 scripts, 561 pairs): head 1a0d1351 = 181; main (merge-base 3ee06864 and origin/main edac5f72) = 182; previous head 2c1ab822 = 182; #3872's head 3ec83def = 184 (ev/pairs.txt). The one pair lost is config_flow_steps.py/wood_advisor.py, now at 87/109 = 0.798. The union closure puts both main's additions and this branch's fault_log.py in config_flow_steps.py's closure, and wood_advisor.py's does not reach fault_log.py. The note's "181 on the merge joining main's 182 to this branch's 182" is correct, and the main-side history it carries over (184 on main and 180 on R11-SEAM-entity-service's branch; 182 before R11-OWNER-FLOWCAP's flow_limit.py) is main's own text kept beside the branch's, so the note resolves as the union too.
- Package counts at head: 104 .py modules and 123 tracked files under custom_components/heatpump_optimizer/. These match the resolved docs/architecture.md, D6 claims, arch_map and deployment_shape figures (103 on main plus fault_log.py; 122 plus fault_log.py).
- Budgets: the PR's only `*_budgets.json` change is still a decrease, `module_excess_loc` 21762 -> 21754 (-8). At 2c1ab822 it was 21774 -> 21766 (-8). No raise.
- tests/config_flow_steps.py resolution: main moved the stored-seed construction into `_stored_seed(row, tag)`. The branch's list-slot seed (a one-element list where `widget.config["multiple"]`) moved into that helper, and its comment moved with it; nothing else changed in the PR's own diff for that file (ev/cfs-old.diff, ev/cfs-new.diff).
- Re-runs at head in a detached worktree: `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` passes all 697 checks; tests/deployment_shape.py passes all checks; tests/structure.py prints STRUCTURE RATCHET PASSED (ev/cfs-head.txt, ev/deployment_shape.txt, ev/structure.txt).
- Mutant, resolution: deleting the list-slot branch from `_stored_seed` fails 22 of 697 checks. Killed (ev/cfs-seed-mutant.txt).
- Mutant, production at the new base: `> FAULT_TEXT_ENTITIES_MAX` changed to `> FAULT_TEXT_ENTITIES_MAX + 1` in config_flow.py `_fault_text_errors` fails 1 of 697 checks, "five fault-text entities are refused with their own error". Killed (ev/cfs-cap-mutant.txt).
- Merge with main: `git merge-tree --write-tree origin/main 1a0d1351` reports no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify 1a0d1351... --pr 3870` was polled about every 90 s for about 30 minutes (18 runs, through 03:39 UTC). Every run printed `WAIT 1a0d13512588f35397993818aad8d566bf96afbc pending: gate red: none`. Nothing is red; `gate` is still pending, hence the `pending-ci: gate` line. review_packet's `introduced-red: unreadable` refusal was an in-progress instrument-self-tests job, which classify supersedes.

## Findings

None.
