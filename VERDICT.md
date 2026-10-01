Fix review: merge 103f0ff8cced94a4c8c87ba7e9f75b7d0811cd77

PR #1834, R9-F1.11, second delta review. The earlier verdicts on this branch cover de27770e and 89572df0.
Head 103f0ff8 = 89572df0 + merges of main 480a6911 and 8f496ce1 (#1835). There is no branch-authored commit.

RESULT diff 89572df0..103f0ff8 == diff 1aefd2d0..8f496ce1 (main's own 20 files: workflows, card JS/tests/images, card claims, delivery rows, tests/entities.py +42)
RESULT tree 103f0ff8 = 48e87d65 = git merge-tree --write-tree 8f496ce1 89572df0 (clean)
RESULT tests/entities.py, both-sides file: main adds one block, the merge-queue required-context check with its null control (entities.py ~23285). It does not touch the P2 or P6 sections.
RESULT entities.py at 103f0ff8: ALL 2053 ENTITY CHECKS PASSED, rc 0 (venv-ci Python 3.14.7). Every P2 and P6 check passes.
RESULT 89572df0..103f0ff8 leaves these unchanged: tests/closures.json, custom_components/*.py, tests/features.py, tests/golden/claimed_drift.txt. The bot-recorded closure from the previous delta stands.
Round-1 measurements and the first delta's findings stand. CI on 103f0ff8 is the merge gate: merge only on green.
