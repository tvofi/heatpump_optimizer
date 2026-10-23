Fix review: merge bd74ad8c23f88c5a1ef19565d1eb9b38e2bde210

bus-nonce: 6d30140f90503ca22c2def0ea6b1c122

Round 1. Group none (roster batch 20, roster ops only); reviewed against the PR body. Measured head: bd74ad8c23f88c5a1ef19565d1eb9b38e2bde210 (still the PR head at post time).

RESULT roster_changed_groups=11 (the 11 the brief names): FLOW-ARCH-PLANNER done @ f38f9185; RECORD-API-BUDGET done @ 97b4fddf; LOOP-CPU resume (fix/r10-loop-cpu, 577ec62d = PR 2632 head); 4 toolkit-measure carries (CI-LAYOUT-P2, FLOW-JIDOKA, FLOW-TOOLKIT-MODEL, FLY-YIELD-GUARD); FLY-NO-FOOTERS carry; P-D/P-E/P-F carries on FLY-OPENPR-ATOMIC, FLY-RELAY-REVIEW-FF, POLICY-LINT-FAMILY. No other field of the file (top level, other groups) differs; no carry removed. The three-dot diff of the repo is the roster plus dev/programme/delivery/2646.md only.
RESULT groups=167 -> 167, added/removed none (finder: my own python comparison of the roster at merge base f38f9185 vs head).
RESULT stages(head) done=90 in-progress=10 not-started=60 queued=6 absorbed=1.
RESULT done_commits_ancestor_of_origin_main: f38f9185 yes, 97b4fddf yes. (577ec62d is an in-progress resume on a live PR branch, not a done claim; it equals refs/pull/2632/head and fix/r10-loop-cpu.)
RESULT main_roster_equals_merge_base: git diff merge-base origin/main -- roster is empty (origin/main now a7cf60cf; it added only delivery/2643.md and tools/policy/field_coverage.mjs).
RESULT brief_lint TOTAL: 0 error(s) across 47 file(s) (the ERROR lines printed are fixture self-test output); ref_privacy --check: 0 refused.
RESULT merge-tree origin/main + head: rc 0, no conflict.
RESULT VERSION/manifest/RELEASE_NOTES/golden/claim files: untouched.
Mutation: n/a, no production or test code. Null control from the body (roster on main equals merge base) reproduced.
Forward-carry: the carries are the change itself; none owed by this PR.

CI at head (one bulk check-runs read, 41 runs): all gate checks success or skipped. nightly-status is failure; it grades main and this diff does not reach what it reads, so it is not this PR's. instrument-self-tests was still in_progress when I read; I cannot cite a conclusion for it, but this diff touches no instrument code. Evidence in ev/.

