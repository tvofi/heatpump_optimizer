Fix review: blocked cf9de4e2a50332c608d854de900108afe890039a root-cause-unanswered: mutation went red, unanswered

bus-nonce: e4e73143a901614343e524123b70ad30

Round 4. A conflict with main is resolved by merge. Measured detached at cf9de4e2a50332c608d854de900108afe890039a. Parents 205943f950645b72866385d8c852e61a70cd3413 and a28fd0aee6651a24161fa38e3295d4ac2d906d57. The body names this head. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/` is empty. The three-dot diff does not touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading.

## Resolution

`git merge-tree --write-tree origin/main cf9de4e2a50332c608d854de900108afe890039a` exits 0. `git merge-tree --write-tree 00da22db537a688efe6a7a9518a9fc91767c3a5a 205943f950645b72866385d8c852e61a70cd3413` exits 0 and its tree equals that commit. `git merge-tree --write-tree 205943f950645b72866385d8c852e61a70cd3413 a28fd0aee6651a24161fa38e3295d4ac2d906d57` exits 0 and its tree `2352acb5e248fc6068d0753813d24e67bc940b50` equals this commit. No conflict markers in the eight files.

None of the eight is byte-identical to either parent. Added lines from ec401ab3 and from 00da22db are in the result, except the census sentences, which were rewritten to 72 modules and 27 module-level `homeassistant` importers, naming both `debugger.py` and `quiet_windows.py`. `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` exits 0 and leaves `claims.json`, `claims.md` and `claims.py` unchanged.

RESULT claims_false=0 count
RESULT arch_modules_on_disk=72 count
RESULT ha_module_level_importers=27 count

`tests/debug_collect.py` is still recorded: 81 files, the same list and order as at 33f6e8edfbee922929a61d7bbd3f665e52f624d8, `recorded` `{"seconds": 2.2, "rc": 0}`. `tests/derive_closures.sh` line 174 is `rec tests/debug_collect.py`, after `guard_pins.py` at line 169.

RESULT closure_files=81 count
RESULT closure_list_equal_33f6=1 count

`python3 tests/structure.py` exits 0. `HeatPumpOptimizerCoordinator` is 9048 LOC. The cap is 9048. origin/main records 9104. The body's `seam_cut_total=765` is not this head: the run printed 766, and the cap at 205943f9 is already 766, equal to origin/main.

RESULT max_class_loc=9048 count
RESULT seam_cut_total=766 count

## Mutation

Job 112484566102 on this head: `ADDED UNPINNED custom_components/heatpump_optimizer/quiet_windows.py:370 RETURN_DEL: return out`, then `MUTATION TABLE REFUSED -- 4696 unpinned site(s) against 4695 at the ratchet base a28fd0aee6651a24161fa38e3295d4ac2d906d57, 1 of them added by this diff`, then `NOT RUN` that site for `--budget-minutes`. The three-dot diff adds those 53 lines, including `configured_specs` and that `return out`. The body's `mutation` paragraph answers job 112303713384 on `9da596f2`. Job 112486109066 printed `AUTOFIX: skip-no-measurement` and `THE REPAIR DID NOT HAPPEN.` The pull request head at measurement was this SHA.

evidence: /Users/timmalmstrom/hpo-seats/r9-dbg-1-review-cf9d/evidence
