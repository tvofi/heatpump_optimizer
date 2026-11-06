Fix review: merge 2d7d46af8afc0f5cbef40772758f1ab7d625bc48

bus-nonce: 1fce2db81be12ada99c57cdef759c376

Round 1. Measured at head 2d7d46af8afc0f5cbef40772758f1ab7d625bc48 (detached), roster/triage record PR, no production or test code. Handoff tip c516cf0f (the brief's 32911ca1 is its code head, as the body says) is an ancestor of the head.

## Evidence
- RESULT files: three-dot vs origin/main = 2 files, dev/programme/rosters/wave-r10-groups.json (+280/-25 incl. the delivery row; body's 279/25 is the tip, one-file figure excludes dev/programme/delivery/3258.md, which the body mentions) and dev/programme/delivery/3258.md. No production/test code.
- RESULT groups: added 5 (R10-CARRY-RESIDUE-2, R10-HOTFIX-GATE-BUSY-DEFER, R10-REF-PRIVACY-CLOUD, R10-REPLAY-COST-2, R10-TRAIN-MERGE-LOOP-2), removed 0, changed 13. Matches body (337 -> 342, 13 changed).
- RESULT carries (check 1): no group lost a carry; gained R10-PLANTED-DEFECT-AUDIT +3, R10-CLONE-2238 +2, R10-PROCESS-SLIM +1. Null control: groups unchanged except resume/carry per ev/roster-diff.txt.
- RESULT stages (check 2): 12 stage changes (8 in-progress, 3 carries-open, 1 done). done = R10-HOTFIX-STAMP-BASE, #3236 merged (33e60b5b in origin/main). carries-open commits 5421413b (#3243) and a2240924 (#3240) and 862affd0 (#3247) are merged merge commits; in-progress rows name open draft PRs 3245, 3248-3250, 3252, 3253, 3255, 3256, 3251. No absorbed stage.
- RESULT merge-tree: git merge-tree --write-tree origin/main HEAD exit 0, no conflict.
- RESULT brief_lint: TOTAL: 0 error(s) across 1 file(s). tests/structure.py: STRUCTURE RATCHET PASSED. JSON parses.
- RESULT overlap (check 3): no other open PR's branch touches dev/programme/rosters (all fix/r10-* branches 0 files); nothing to order. Fix PRs name their group in the roster by PR number only here.
- RESULT CI: merge_train.py classify -> GREEN, pending none, red none. Check-run listing (68 runs, all pages) has no failure; governance / instrument-self-tests succeeded at 18:04 (not cancelled), pr-contract success. Body's Red checks says "none yet", which is true of nothing now: no red exists, so no answer owed.
- RESULT ref_privacy: on this cloud seat (uid 0, HOME=/root) --check refuses roster lines 17201 and 17209 as home-directory (3 lines incl. account-name with HOME=/nonexistent) and scrub reports 1 file would change; the body's "0 refused" and the brief's "scrub changes 0 files" are true off a cloud seat only. The flagged text is the roster's own record of this false positive (R10-REF-PRIVACY-CLOUD, in PR #3251); CI's governance and policy checks are green. See finding.
- Body figures not re-derived: blob ids f78ea1b1/0c869e6a (not needed; counts reproduced). VERSION, manifest, RELEASE_NOTES untouched (not in diff).
- Check 5 (ready): nothing else blocks marking it ready: CI green at this head, body complete, merge clean, no conflicting roster PR. Body Red-checks line and "1 file" are cosmetic; title names ebf92ea7 (cosmetic, per brief).

## Findings
- ref_privacy --check/scrub report false positives on this PR's roster lines 17201/17209 when run as uid 0 / HOME=/root (cloud seat), so a cloud seat's pre-handoff check of this PR reads 2 refusals while CI reads 0; the cure is the group this PR adds. Carry: R10-REF-PRIVACY-CLOUD
- Body's "Red checks: none yet" was written before any check ran and is stale; it was not refreshed after the checks all concluded green. Carry: dismissed: no red exists to answer, pr-contract passed on this head
