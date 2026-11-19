Fix review: merge 946d1ae1acc94568f87a027d70ee111431f7a646

bus-nonce: 342a8ed39ead0fb47515cae72c9847e1

Round 2, delta review (tvofi 2026-11-09): `git diff d9ed60f70f7b 946d1ae1ac`. d9ed60f70f7b is a CI main merge over the round-1 merge verdict at 54b8b9d469 (probe/rev-3742-40fae36d), so the review carries to it. The round-1 verdict had no findings; its two Notes (a body figure and the M8 equivalent mutant) were paperwork and need no resolution. The delta is 780b75f25f (one new check and one ledger pin) plus the merge of origin/main at cb8edb65a5. No production line of this branch moved apart from the conflict resolution, so the scope does not widen.

## Evidence

- New check (tests/config_flow_steps.py, "a listed field cleared on the setup pre-fill page re-renders empty, not with the stored value"). At the head, `PYTHONPATH=tests/hastub:. python3 tests/config_flow_steps.py` prints `ALL 609 checks PASSED`, rc=0 (`ev/cfs_head.log`).
- Mutation proof, re-run by this seat in the detached worktree at the head. `config_flow.py:2257` `_prefill_fields` BOOLOP (`key not in keys and key in in_force` -> `or`) gives `1 of 609 checks FAILED`, rc=1. The one failure is the new check (`fraction=0.6`, where None is expected). The source was then restored (`ev/cfs_mut_boolop.log`). The pin `killed_by/config_flow.py/_prefill_fields.BOOLOP.7bbbd327.json` quotes the live line exactly and names the suite that kills it.
- Merge resolution, read with `git show --remerge-diff 946d1ae1ac` (`ev/merge_resolution.diff`). In config_flow.py imports, main's `thermal_model` import block is kept (`dhw_enabled_from_config`, `two_zone_from_config`) and the branch's `from .entry_config import placed` is kept. No `_dhw_enabled_from_config` reference remains in custom_components/ or tests/. In thermal_model.py, the branch's inline two-zone block is replaced by main's `two_zone_from_config(config)` / `dhw_enabled_from_config(config)` calls. The function body equals the dropped inline block: mode ON -> True, OFF -> False, else presence of the same four keys. `git diff origin/main HEAD -- thermal_model.py` shows only the docstring sentence reworded (`ev/thermal_vs_main.diff`). Both files compile. No behaviour changes.
- Merge with current main: `git merge-tree --write-tree origin/main 946d1ae1ac` rc=0, and stderr is empty.
- `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched in the three-dot diff from merge base cb8edb65a5. The only structure-budget move is `class_excess_loc` 17356 -> 17344, a lowering.
- PR body `## Head` names 946d1ae1acc94568f87a027d70ee111431f7a646, and the figure-block scope line names the same head.
- Live check-runs at the head: 56, none failing or pending (`ev/checks.txt`). pr-contract / pr-contract is success, so the round-1 red (alerts 59/60 unnamed) is answered. tests / mutation is success.

## Notes

- Note: mutation-inconclusive: the `tests / mutation` job at this head printed `MUTATION TABLE INCONCLUSIVE`. Its baseline `tests/features.py` was red (rc=1 failed=2) on main's room-lift check ("the lift may raise the plan's peak ...", peak lift=20.453 vs none=20.241), so the green tick evaluated no mutants (`ev/mutation_job_tail.log`). At the same head the `tests / fast (3.14)` job ran features.py `ok` (`ev/fast_features_ok.txt`), so this red is not reproducible and it comes from main's #3803 check, not this diff. The delta's one new production-adjacent site was mutated by hand above. Carry: dismissed: evidence, not a finding
