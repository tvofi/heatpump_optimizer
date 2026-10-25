Fix review: merge ead46b94930085862f9f21811747cd586d138df2

bus-nonce: d8073ade74cdfa35ffbb22b9c5b60c64

## Summary

Round 1 review of #2793 (roster batch, record lane) at head ead46b94930085862f9f21811747cd586d138df2, re-read at post time and unchanged. Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

none

## Evidence

- RESULT three-dot diff (merge base 65233813c): two files, dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2793.md (this PR's own row). No other path.
- RESULT ops: `git rev-list --count c57fa3768..8c9da6653` = 9; each op commit touches only the roster file (ev/ops.txt). The roster blob at the head, at origin/handoff/audit-r10-roster and at 8c9da6653 is the same, 711deb853817. Main's roster blob (65233813c, ab3aade49, 21a1e04a7) equals c57fa3768's, 64bf29ca58ca, so nothing main wrote is overwritten.
- RESULT ops vs diff: 5 append-carry, 2 set-resume on R10-FLOW-ROSTER-FREEZE (one net change), 1 set-stage, 1 append-group; JSON diff by group id shows exactly 6 changed groups and 1 new, none dropped, every changed carry list keeps its old entries as a prefix (ev/carry_diff.txt).
- RESULT JSON valid: loads, 189 groups, no duplicate ids. Stage counts main then head: done 114/115, in-progress 13/12, not-started 49/50, queued 6/6, carries-open 5/5, absorbed 1/1; matches the body.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at the head: TOTAL: 0 error(s), rc 0 (ev/brief_lint.txt).
- RESULT carry text: each of the five triage carry texts (s6-batch20.md P96 (a), (b); s6-batch21.md P97, P98, P100) is contained verbatim in its roster entry, prefixed only by a source citation (ev/carry_text_cmp.txt). P98 adds the orchestrator's routing-note prefix (arm (b2) after arm (a)). P96 (b) names R10-TRAIN-UPGRADE in the triage, but that group is done (#2772, ac0a616a2, an ancestor of origin/main); the carry lands in R10-FLOW-AUTOTRAIN, whose after list includes R10-TRAIN-UPGRADE and whose existing carry already says to build on Train.admit_add, with a suffix saying it may be a pin only. That reroute reaches the stage that will do the work; I accept it.
- RESULT set-stage: R10-FLY-YIELD-GUARD done at 8a11b8bdd6bfdca0b5f6bd356638fad2b234525f = "Merge pull request #2765", an ancestor of origin/main. Its two #2765 forward-carries are on R10-ORCH-DISPATCH-REG, as the body says.
- RESULT ROSTER-FREEZE resume note: #2779 merged as c01d54b98 (ancestor of origin/main); "six carries ride arm (a)" = 7 carries less the P98 arm (b2) carry.
- RESULT new group R10-MERGE-SUBJECT-CASEARM: its after group R10-MERGE-SUBJECT-HARDEN exists (in-progress, #2697); stage not-started.
- RESULT merge: `git merge-tree --write-tree origin/main ead46b94930085862f9f21811747cd586d138df2` with origin/main 21a1e04a7 exits 0, tree 8c66aba6c4ea (ev/merge-tree.txt). No claim-file conflict and no claim file touched.
- RESULT CI on the head (check-runs API, 43 runs): no failure; most completed success or skipped; governance / env-matrix, governance / instrument-self-tests and one prelude still in progress when read. No red check, so no root-cause answer is owed.
- Mutation proof, harness, null control at both ends: n/a, roster state only, no production or test code; VERSION, manifest and notes heading untouched.
- Body figures re-derived: 9 ops, blob 64bf29ca58cab83d366faef6519c219096c0a7cc, 188 to 189 groups, 6 changed, stage counts, authored head 4a18b96b1 and the row-only commit f486320b6. The body's Red checks section is about main's tip at ab3aade49, not this head.
