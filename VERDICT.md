Fix review: merge 2688f4c854350142cca0af33207717064eb8e5df

bus-nonce: 5bfda5e6e5db4d4095b82998aabe338b

Round: first review, done at 2688f4c8; head d08845107b161cb1ffbbaaa0684a4ab8d1240eca adds only dev/programme/delivery/3482.md (1 line) on top, so the review stands. No pull request, no review packet and no CI exist yet, so there are no live checks to cite.

## Evidence

- Key question answered: at this head, `selftest_scope` check passes on the merged tree, and it still refuses a read set the table misses. This head also does not need #3446 to be on main. The merge of 745a936201ac brings #3446's table edits in (the diff to origin/main includes the `-c`, `.gitattributes`, env_drift, ledger_merge, fix-review.md entries), so the head is self-sufficient. When #3446 lands first, the identical hunks merge cleanly.
- Finder's harness at the head: `python3 -I tools/ci/selftest_scope.py record` ran all gated steps under strace (111 steps, 0 failed, 0 broken traces). I compared each step's files/probes/dirs/index/objects against the committed table with my own script. RESULT head: refusals 0 (ev/cmp_head.txt).
- Same recording against origin/main 61afd4f2 table: RESULT main: refusals 3 (review-packet and verdict-bus miss dev/governance/roles/fix-review.md; selftest-wiring misses tools/audit/seat/remerge_main_selftest.py). This matches the body's null control (ev/cmp_main.txt).
- Perturbation: the head's table with only the selftest-wiring remerge_main_selftest.py entry removed gives refusals 1, naming exactly that file (ev/cmp_pert.txt). So the check is not vacuous.
- #3446's head 745a936201ac table alone gives 7 refusals against this recording (ev/cmp_p1only.txt). So #3446 by itself does not turn main green, and this part 2 is needed. The body's "one table entry" undercounts: the diff against 745a936 adds 7 lines to selftest_closures.json (remerge_main_selftest.py in several steps, gh_read.py, throwaway_git.py), because the drift step measured them after main moved. This is a body wording slip; every added line is a measured read the recording confirms.
- `selftest_scope.py --self-test`: 117 checks, 0 failed (ev/selfcheck.txt).
- Mutation proof: n/a, no production code; the perturbation above is the null control. No VERSION, manifest, RELEASE_NOTES, golden or claim file is in the diff to origin/main.
- Merge: `git merge-tree --write-tree origin/main <head>` exit 0, no conflict (ev/mergetree.txt). Head is behind main only in the sense of a clean merge.
- Red checks: governance / instrument-self-tests on main is not in my reading of the owed set for this branch (the body states it is not); the head has no CI yet. Nothing is owed or blocking.
- Caveat: my comparison script is my own subset test (files/probes/dirs, index/objects flags), not the CI `check` code itself. Measurement was on cloud Linux with strace; cloud-unmeasurable reads (prepr's .gitattributes, tests/env_drift.py, tools/merge/ledger_merge.py, probe `-c`) are part 1's and are present in the table. Carry: dismissed: the subset test does not change the verdict, since the null control and the perturbation both behave as predicted

## Findings

- Follow-up: the body says part 2 is "one table entry" while the table delta against #3446's head is 7 lines; correct the PR body wording when the pull request opens (no code effect). Carry: dismissed: wording only, every added entry is confirmed measured by the re-recording
