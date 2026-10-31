Fix review: merge 9d304c2d6ff746077a967cd9f0433f548bd701b5

bus-nonce: 067d3118634498e38a675b7b1b3ef38b

Round 4 delta review: the merge-main resolution alone (c3801fd6f -> 9d304c2d6ff746077a967cd9f0433f548bd701b5). The merge verdict at c3801fd6f stands for the branch's own code. review_carry.py prints FRESH-REVIEW because 0d47d35cc is not an automatic merge of its parents, so the resolution delta is mine (step 12).

## Evidence
- RESULT claims.py re-run at 9d304c2d6ff746077a967cd9f0433f548bd701b5 (PYTHONPATH=tests/hastub): claims.json and claims.md byte-identical (git status clean after the run).
- RESULT git diff origin/main 9d304c2d6ff746077a967cd9f0433f548bd701b5 -- dev/audit/rounds/round4/D6/: 2 files, only C108 83->84 and C111 19->20; no C110 or image line moved (ev/d6-diff.txt).
- RESULT cause: the branch's three-dot diff adds one relative link (README.md, docs/automations.md's blueprint list gains the new blueprint; docs/configuration.md adds an automations.md#blueprints link) and one external link (the blueprint's raw.githubusercontent.com source URL), matching +1 C108 and +1 C111.
- RESULT git merge-tree --write-tree origin/main 9d304c2d6ff746077a967cd9f0433f548bd701b5: exit 0, stderr empty, no MERGE-CLAIM lines (clean merge); origin/main is 2fc0e95b2, the merge base.
- RESULT env_drift.py --all at the head: NO UNCLAIMED DRIFT: 56 scenario(s); NO STALE FIXTURE: 56. Claim files against origin/main differ by the one config_flow line in claimed_drift.txt (and the config_flow.json fixture), the branch's own claim.
- Body ## Head names the merge: 0d47d35cc merged origin/main, 9d304c2d6 merges origin/main 2fc0e95b2; the D6 resolution and its control are described there. Its prose "C108 84 -> 85" describes the pre-merge tree, and the final delta against main is 83 -> 84 as measured here.
- CI at the head: all check-runs read (45, every run); no red. classify: GREEN (ev/classify.txt). Nothing red owes an answer.
- Head re-read: refs/pull/3016/head is still 9d304c2d6ff746077a967cd9f0433f548bd701b5.
- Not re-run: the branch's own mutation and figure claims (covered by the merge verdict at c3801fd6f).

## Findings
none
