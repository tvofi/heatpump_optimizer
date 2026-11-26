Fix review: merge 60076fe6ed636474d399c570111222d05c547d9a

bus-nonce: e3ce36c5c338e6be552ec567a5ec51e5

## Scope

Delta review: 724cef08de0ca20c182f3ade904a2a02361e17c8 (last reviewed head, verdict/3835 3a44484af1: merge) to 60076fe6ed636474d399c570111222d05c547d9a. The rendered packet reads `full` only because the brief's render names the head itself as the reviewed head; verdict/3835 names 724cef08 as the last reviewed head, so the delta is the scope. The delta holds no PR-authored production change. It is two main merges: 2045c8a2a8 (724cef08 + main e91329c2) and 060c62be8b (+ main 1d307773). 60076fe6 joins 724cef08 to 060c62be8b, and its tree is byte-identical to 060c62be8b's.

## Evidence

- Resolutions are unions. `git merge-tree` re-run of 2045c8a2a8's parents conflicts only in dev/audit/rounds/round4/D6/claims.py and tests/deployment_shape.py (ev/remerge_2045c8a2.txt). The committed resolution keeps both sides' provenance entries in every conflicted hunk: R11-SEAM-learners's learning_freeze.py from this branch, and main's "merge joining R11-OUTSIDE-3848's dhw_start.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py" plus "186 on #3863's branch". It then raises the counts by the one module the union adds (105 to 106 modules, 124 to 125 files, 190 to 192 pairs). The other files that differ from the auto-merge are regenerated outputs: claims.md, claims.json and docs/architecture.md (105 to 106, 68 to 69). Re-merging 060c62be8b's parents gives a tree byte-identical to the commit (ev/remerge_060c62be.txt, an empty diff), and so does re-merging 60076fe6's parents (ev/remerge_head.txt).
- The re-derived counts reproduce at the head, run in a detached worktree at 60076fe6 under venv-ci python3:
  - `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` exits 0 with RESULT claims_true=123, claims_false=0, arch_modules_on_disk=106, arch_map_listed=106 and arch_map_missing=0 (ev/claims_py.out). The tree is clean after the run, so the committed claims.md/claims.json match the regeneration: claims.md has 123 true and 0 false, and claims.json has 125 entries (123 true, 2 unverifiable).
  - The package has 106 .py files and 125 tracked files. 37 modules import homeassistant (35 at column 0, plus currency.py and inputs.py indented), and 106 - 37 = 69 HA-free, which matches architecture.md's "36 at module level, one more inside a function, the other 69".
  - tests/deployment_shape.py: ALL DEPLOYMENT SHAPE CHECKS PASSED, rc=0 (ev/deployment_shape.out).
- The removed SysIdConfig.enabled has no reader at the head. `git grep` at 60076fe6 finds no `SysIdConfig(enabled` in custom_components/ or tests/, and SysIdConfig declares no `enabled` field. The only `config.enabled` reads left are pv.py:68, coordinator.py:9737 (the PV config) and external_heat.py:505 (the external-heat detector config), none of which is SysIdConfig. origin/main still carries the field and 32 test constructions of it in features.py and 3 in dst_checks.py, but the merge result carries none, so main's side did not reintroduce a reader.
- No budget rises. The only `*_budgets.json` change in the delta is tests/structure_budgets.json, and every metric at the head is at or below both the last reviewed head and origin/main: class_excess_loc 17227/17221 to 17220, max_class_loc 7766/7817 to 7762, module_excess_loc 21752/21647 to 21646, and the rest are equal (ev/budgets_compare.txt, RESULT rises_vs_both_parents=[]). tests/structure.py at the head prints STRUCTURE RATCHET PASSED with rc=0 (ev/structure.out).
- Merges with main: `git merge-tree --write-tree origin/main 60076fe6` is clean, rc=0 (ev/merge_tree_main.txt).
- CI: `merge_train.py classify 60076fe6ed636474d399c570111222d05c547d9a --pr 3835` gives `GREEN 60076fe6ed636474d399c570111222d05c547d9a pending: none red: none`, rc=0 (ev/classify_poll.log, ev/classify_last.txt). No red is owed an answer.
- Mutation: the delta adds no PR-authored production code. The mutation-ledger records it moves come from main's merged modules and their re-anchored hashes, and CI's tests / mutation is green at this head.

## Findings

None.
