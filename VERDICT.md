Fix review: blocked 705c3be37fe94feb37be1600b57403e129c382f8 root-cause-unanswered: env-matrix went red, unanswered

bus-nonce: ef5cdfa1b9f91bcefdc38e8899928d8e

Round 5. Measured detached at 705c3be37fe94feb37be1600b57403e129c382f8. Parents 19391406563cf785e723be51ceb7b9b34a850511 and 6001b09a557259f37319b400d219cf83e02c563f. The body names this head. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/` is empty. The three-dot diff does not touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading.

## Pin

`configured_specs` ends at `quiet_windows.py:370` with `return out`. Replacing that line with `pass`, `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` exited 1: `FAIL configured_specs returns the stored rows and the not-enforced marker` `got None`, `1 of 129 manual plan checks FAILED`. Restoring the line, the same command exited 0: `ALL 129 manual plan checks PASSED`. The ledger reason says `failed=2`. This tree printed `failed=1`.

The inventory calls in `tests/mutation_table.py` (`inventory`, `unpinned_sites`, `added_unpinned`), stopped before the drive: 4695 unpinned of 5687, 4695 at the ratchet base `6001b09a557259f37319b400d219cf83e02c563f`, 0 added. The line-370 site is `configured_specs RETURN_DEL a8227ccf` and is not unpinned. The body's 4695-against-`a28fd0ae` is that earlier base; this head's `ratchet_base` is `6001b09a`.

RESULT manual_plan_mutant_failed=1 count
RESULT manual_plan_restored_failed=0 count
RESULT unpinned=4695 count
RESULT unpinned_base=4695 count
RESULT unpinned_added=0 count

`python3 tests/structure.py` exits 0.

RESULT max_class_loc=9048 count
RESULT seam_cut_total=766 count

`git merge-tree --write-tree origin/main HEAD` exits 0. `git merge-tree --write-tree 19391406563cf785e723be51ceb7b9b34a850511 6001b09a557259f37319b400d219cf83e02c563f` exits 0 and its tree `4a947fb10030ca4eaf1dc82c46c2434f61ea40fd` equals this commit. stderr: `LEDGER-MERGE: resolved tests/closures.json`. `tests/debug_collect.py` is still 81 files, the same list as at `cf9de4e2`, `rc` 0, and `tests/derive_closures.sh` line 174 still records it.

## env-matrix

Job 112529653069 on this head failed. The log's first failure is `pr / policy_lint rc=0 and every pin earned -- rc=1`, and the shallow arm is `Cannot find module .../.claude/workflows/policy_lint.mjs`. `## Red checks` does not name `env-matrix`. The later `pr-contract` job 112530277746 exited 1 with `check env-matrix is red and ## Red checks does not name it`. An earlier `pr-contract` job on this commit, 112529650505, succeeded. The pull request head at measurement was this SHA.

evidence: /Users/timmalmstrom/hpo-seats/r9-dbg-1-review-705c/evidence
