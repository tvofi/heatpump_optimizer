Fix review: blocked 2e77ed3e6aa2f03565bd02274ac847227bc619b5 head-moved: measured 2e77ed3e6aa2f03565bd02274ac847227bc619b5, head is 802b38503eb5de20e87c278ba7923508a50c0f1f

bus-nonce: a3eee38c3144cc46f38b3f801f78f093

Round 4 (cloud reviewer seat) on PR #2559, a roster PR with group none, reviewed against the PR body. I measured 2e77ed3e6 from a detached worktree. The roles contract is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## Head moved (step 12)
While the review was waiting for CI, the PR head moved to 802b38503. That commit is 2e77ed3e6 plus:
- 2c76c3128, `roster_edit set-stage R10-MERGE-PR-MANDATE`, authored roster content that moves that group from in-progress to done and its commit to 22615537a;
- a merge of origin/main at 5d433771a.

Because the move includes authored content, step 12 makes it a re-review, not a carry. The superseded Tests run cancelled ci-ratchet, closures, composed-proof, coverage-ratchet, graders-head-copy and lane-proofs on the measured head, so those never concluded there. Evidence: ev/head-moved.txt and ev/head-move-roster.diff. A re-review needs only that delta plus the notes below; everything else held.

## Verified at 2e77ed3e6 (finder harness: jq over the roster, ev/harness.sh)
RESULT 22615537a groups=91 done=43 carries=201
RESULT 31e162fd3 groups=108 done=51 carries=254
RESULT 2e77ed3e6 groups=108 done=51 carries=257
RESULT 17 new groups, 0 removed, 18 stage changes, text edits on 16 existing groups (my definition: any of brief/issues/fixes/findings differs)
RESULT carries appended to existing groups: 32 over 14 groups at 31e162fd; 33 at the head. New groups' carries: 21 at 31e162fd; 23 at the head.
RESULT 31e162fd -> head: R10-BRIEFS-FOLD 20->21, R10-CI-LAYOUT-P1 2->3, R10-CI-LAYOUT-P2 1->2. R10-OPENPR-SILENT only moves its resume.commit; its stage stays done.

The checks:
- merge-tree against origin/main 5d433771a: rc 0, no conflict (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES and goldens are untouched, and no claim file is touched.
- `brief_lint.mjs` exits 0 on the roster and on carry-201.json.
- The P1/P2 carries name a control, and it reproduces: `selftest_wiring.py --check` reads 37/37/0 with rc 0, and deleting the governance.yml tmp_paths self-test line gives 37/36/1 with rc 1.
- CI on 2e77ed3e6: pr-contract succeeded twice and coverage succeeded. nightly-status is red, but it grades main, not this PR: the diff does not reach what it reads.

## Notes for the re-review (non-blocking)
- The body's figures are dated at 31e162fd. The head has 257 carries, not 254, and 23 carries on new groups, not 21. "R10-BRIEFS-FOLD 19 to 20" is not re-derivable at any commit: it reads 18->20 at 31e162fd and 18->21 at the head. The round-3 reviewer flagged the same line. Carry: R10-ROSTER-OPS
- The new R10-BRIEFS-FOLD carry (617ce131, ev/new-carry-briefs-fold.txt) states its precondition and control, matching #2563's verdict, and D2.md is in that group's file list. But it cites its harness as `dev/audit/rounds/round10 r10_night_folds_learners.py`, a path that exists in no tree. The file is at `dev/audit/harnesses/r10_night_folds_learners.py` on #2563's head 829ea7c72 (ev/harness-location-2563.txt). The carry also gives no instruction to re-measure the 1.9800 figure. brief_lint does not lint carry entries, so nothing catches either gap. Carry: R10-BRIEFS-FOLD
