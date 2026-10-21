Fix review: merge 802b38503eb5de20e87c278ba7923508a50c0f1f

Round 6 (re-review of the frozen head; the head has not moved since review 7adab9fd's merge verdict). Measured at 802b38503eb5de20e87c278ba7923508a50c0f1f, still the PR head when written (ev/HEAD.txt). dev/governance/roles/ unchanged between the merge base and origin/main, so this contract copy is current.

Carry: dismissed: the body was re-taken whole at this head and no longer says 18 to 20 (item d4da81d2)
Carry: dismissed: the stage stays done and only the commit pin moves, as the re-taken body states (item a406c960)
Carry: R10-ROSTER-OPS (item 7f85b089)

Carry evidence:
- d4da81d2: the body contains neither "18 to 20" nor "19 to 20" (ev/body-grep-18-20.txt, count 0); it now says "R10-BRIEFS-FOLD 18 to 21", which jq re-derives (18 at merge base 5d433771a, 21 at head).
- a406c960: the body lists R10-OPENPR-SILENT under "Resume-note edits at an unchanged stage"; the stage is `done` at both ends. Exactly: resume.commit moves 7ab3030bbfff -> dbea71db76f1 and resume.note gains the #2525 follow-up clause, both covered by the body's "resume-note edits" line. The stale `next_step` ("PR #2422 is open ... review and merge it") predates this PR, as the original item said (ev/carry-items.txt).
- 7f85b089: R10-ROSTER-OPS exists on origin/main e7c664856's roster (stage in-progress). The note is stale: at the head, R10-MERGE-PR-MANDATE is `done` with commit 22615537a, the merge commit of PR #2555 (fix/r10-merge-pr-mandate, merged 2026-10-21T13:10:40Z), yet resume.note says the handoff "has no pull request. Owed: recarry and open" and next_step reads "recarry". To be rewritten in R10-ROSTER-OPS's next roster burst (ev/carry-items.txt).

RESULT lines (jq/python over wave-r10-groups.json, merge base 5d433771a -> head; ev/figures.txt):
RESULT groups 91 -> 108, 17 new, 0 removed (matches body)
RESULT done 43 -> 52 (matches body; 43 + 2 + 9 - 2 = 52)
RESULT carries 201 -> 257, +56 = 23 on new groups + 33 on 14 existing groups; per-group counts match the body's list; 0 carries rewritten at unchanged count (matches body)
RESULT stage changes on existing groups 19: 9 to done, 8 to in-progress, 2 done -> in-progress; names match the body
RESULT text edits 16 groups; same-stage resume edits 12 groups incl. R10-OPENPR-SILENT and R10-REGISTRY-LEAK (matches body)
RESULT carry-201.json carries 16 -> 17 (+1, matches body); critical-path.json new and parses
RESULT R10-CI-LAYOUT findings names four pull requests with P1/P2 split (matches body)

Other steps:
- Step 7 head chain: 802b3850^1 = 892169c30, ^2 = 5d433771a (= merge base); the roster files are byte-identical between code head 2c76c3128 and the PR head; the diff from the merge base lists the body's four files.
- Steps 1/2/3/6: n/a, roster state only, no production or test code; one seam, no enumeration rule owed.
- Steps 4/5: VERSION, manifest, RELEASE_NOTES.md, tests/golden/ and both claim files untouched (0 diff).
- Step 13: `git merge-tree --write-tree origin/main(e7c664856) 802b3850` rc 0, tree cc8a8f757, no conflict (ev/merge-tree.txt).
- Step 11: 55 check runs on the head, all completed: 37 success, 16 skipped, 1 neutral, 1 failure = nightly-status, which grades main and whose inputs this diff does not reach; the body answers it. pr-contract success on all four runs, the last started 14:32:20Z after nightly-status concluded 14:03:36Z (ev/check-runs.tsv).
- Step 10: body's forward-carry is none; carries in the roster are the roster's content, reviewed in round 5.

carry_audit (run before this verdict is posted, so it cannot yet see these markers): CARRY-AUDIT #2559: 5 finding item(s): 2 routed, 3 unrouted, 0 bad destination(s)

bus-nonce: 8ddeb923d0afccbb941906ea350d89f1
