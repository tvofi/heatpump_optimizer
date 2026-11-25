Fix review: merge f9aaa2ea4c40391a30d9f63981982be6fe23a5d3

bus-nonce: 3b336fd99eb7c4c3d5737ebf490d2773

## Scope

This is round 2, a delta review over the reviewed head d1a25459a7efd3673aa8ec7c75da793ea4d3e3dc. The packet's `## Review scope` reads `delta`. The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

The delta d1a25459..f9aaa2ea is four merges of main. The one hand resolution is `tests/golden/card_claimed_drift.txt` in b4333db5, a test fixture claim file, so it does not widen the review. No `custom_components/` line differs from git's own merge.

## Evidence

- RESULT resolutions: `ev/merge-resolutions.txt` diffs each merge in the delta against `git merge-tree --write-tree` of its two parents.
  - b4333db5 (d1a25459 + 24e3f376) differs only in `tests/golden/card_claimed_drift.txt`.
  - 044f90d0, bf185985 and f9aaa2ea differ in no file.
- RESULT claim file: the head's `card_claimed_drift.txt` is main's dc2b2bab file plus this PR's block.
  - Main's file is the stamp-emptied one, `claims-for: 10.1.3`, equal to `VERSION` 10.1.3 on both sides.
  - The PR's block is the R11-OWNER-CARD-EXTERNAL-HEAT comment and 41 state lines, counted by `grep -c '^[a-z_]* # R11-OWNER-CARD-EXTERNAL-HEAT'`.
  - The R11-SEAM-card reasons the reviewed head carried were dropped. That change is on main and its claims were emptied by the 10.1.3 stamp.
- RESULT card drift: `node tests/card_drift.mjs dc2b2bab316419ced8f919c256908275a2cc3e25` at this head printed `card_drift: 41 state(s) moved and claimed, 4 identical`, rc 0. That is the same footprint the previous verdict measured against e3cb5c01 (`ev/card_drift-vs-main.txt`), after `tests/plan_view.py` rc 0 (`ev/plan_view.txt`).
- RESULT card.mjs: the local run was killed by a V8 out-of-memory abort on this host, rc 134 (`ev/card.txt`), after 1424 `ok` lines and no FAIL. This is not a result. CI's `tests / fast` at this head is part of the GREEN classify below.
- RESULT CI: `merge_train.py classify f9aaa2ea4c40391a30d9f63981982be6fe23a5d3 --pr 3871` printed `GREEN f9aaa2ea4c40391a30d9f63981982be6fe23a5d3 pending: none red: none`, rc 0 (`ev/classify.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0 with tree dd50a5ce (`ev/merge-tree.txt`).
- RESULT version: neither `VERSION` nor the manifest version is changed by any of this PR's own resolutions.
- RESULT previous findings: the previous verdict's two notes, the null-control figure and the features.py test-control conjunct, were dismissed as paperwork with their reasons. The delta touches neither the body figure nor `tests/features.py`'s check beyond git's merge, so nothing is owed.
- RESULT head: the PR head read f9aaa2ea4c40391a30d9f63981982be6fe23a5d3 when I checked (`gh pr view 3871`).

## Findings

none

## Friction

none
