Fix review: merge 7a3e640d01ffdfe3e74c64fc4e3ede06c087489c

bus-nonce: 279700e0b22d4a13777ed23c6b7936a3

## Summary

Roster-only PR (round 1 for this PR). Head re-read: 7a3e640d01ffdfe3e74c64fc4e3ede06c087489c, matches the brief; origin/main is e45fc34fb145, equal to the merge base. Diff against origin/main is dev/programme/rosters/wave-r10-groups.json plus dev/programme/delivery/2635.md. No production or test code, so no mutant exists; the mutation proof is n/a as the body says.

## Evidence

- RESULT counts (ev/counts.json): 154 -> 165 groups, removed [], 11 new, 18 changed; the new and changed names match the body.
- RESULT stages (ev/stages.txt): main done 84, in-progress 15, not-started 49, queued 6; head done 86, in-progress 13, not-started 59, queued 6, absorbed 1. Matches the body.
- RESULT carry re-cut (ev/carrymap.txt): all 45 old R10-ORCH-MACHINERY carries matched by exact text. The 12 kept ones are the design section 4 no-build set (2,3,4,5,6,7,19,20,21,28,29,31). Carry 13 sits in LEDGER, DISPATCH-REG, BEATD and PLANPAGE, as design A, B, C and E require. Every other carry lands in exactly one group, per the design table: A 12,22,35,36; B 14,18,30,41,42,43; C 15,39,40; D (ROSTER-SCHEMA) 23,24,25,32,37; E 17,44; F 1,38 to FLY-CARRY-DISPOSITION; G 0,8,10,11,16,26,33,34 to the six FLY groups; 9 to UPDATE-PR-SIGNALS; 27 to FLY-CAP-LINE. None lost, none duplicated. Other-group matches of carries 19 and 20 are pre-existing copies.
- The body's "34 carries dropped" is 34 drop-carry commits (198970538..03acbf981) against the 46 carries the branch held after 224dfb4ed appended one; main held 45, so the net difference against main is 33. Both figures re-derive. The appended routing carry for R10-BRIEFS-FOLD ended up on R10-POLICY-FIXER-MD.
- RESULT after-edges (ev/graph.txt): no missing refs, no cycle, nothing is `after` the absorbed R10-ORCH-MACHINERY. R10-FLOW-TOOLKIT-MODEL is after PLANPAGE and TOOLKIT-MEASURE; R10-ROUND-PLAYBOOK is after LEDGER, DISPATCH-REG, BEATD and PLANPAGE. Chain LEDGER -> DISPATCH-REG -> BEATD -> PLANPAGE is rooted in done groups, so every blocker can finish.
- RESULT lint: `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at the head prints `TOTAL: 0 error(s) across 1 file(s)` (ev/lint_roster.txt).
- RESULT null control (ev/nullcontrol.txt): planting an after-ref naming no group in a copy of the roster makes the same lint print 1 error and `TOTAL: 1 error(s)`, so the 0 above is a real check. Worktree restored.
- RESULT ref_privacy --check at head: `87 line(s) added since e45fc34fb145 judged, 0 refused` (ev/refpriv.txt). The body says 86 since cccbf4fb508c, which differs by the merge base and the delivery row; 0 refused holds.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` rc 0, clean (ev/mt.txt). VERSION, manifest and notes are untouched (diff is the two files above).
- RESULT CI (ev/checks.txt, check-runs API at the head): all completed checks are success or skipped, including pr-contract (2), budget-raise-gate, arch-score, mutation, closures, env-matrix. `nightly-status` is completed failure; it grades main's scheduled Tests run and this diff touches nothing it reads (the body says the same). `fast (3.14)` was in progress at the first read; `instrument-self-tests` was still in progress at the last read. Neither was reachable from a JSON roster change; not re-run, cited from CI.
- Forward-carry: body says none. The re-route of the #2627 and #2629 bodies after merge is an orchestrator task the body states; see Findings.

## Findings

- Post-merge task owed: re-route the toolchain bullets in the bodies of #2627 and #2629 from R10-ORCH-MACHINERY to R10-FLY-CLOUD-SETUP-TOOLCHAIN once this merges (body, "Re-route owed"). Carry: R10-FLY-CLOUD-SETUP-TOOLCHAIN | dismissed: recorded by the PR body as an orchestrator action, with the carries already on the group.
- `instrument-self-tests` and `fast (3.14)` had not concluded when read; the merge train should confirm both are green at this head before merging. Carry: dismissed: a CI state the merge train reads itself, and a roster-only diff cannot move either.
