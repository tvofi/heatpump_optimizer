Fix review: blocked d4f8914e6772d5fd3c68eb5a002244f87ff9f8cd figure: body says the 17 new groups are 7 done, 5 in-progress, 1 not-started, 3 queued (16); the roster has 6 in-progress (R10-ROSTER-OPS, R10-RCA-NIGHTLY-PYSPY, R10-MERGE-PR-MANDATE, R10-FOLLOWER-DEBOUNCE, R10-SETPOINT-BOOST, R10-SAVINGS-NEGATIVE)

bus-nonce: 90589286a7efe02f4779b4fe0e8eab30
RESULT head=d4f8914e6772d5fd3c68eb5a002244f87ff9f8cd measured, still the head at post
RESULT diff-scope: origin/main...HEAD touches only dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2467.md; JSON valid; top-level keys other than groups identical
RESULT groups: 72 -> 89, 17 new, none removed (re-derived)
RESULT moved-to-done: 8 existing groups, exactly the body's list (re-derived)
RESULT new-group-stages: done 7, in-progress 6, not-started 1, queued 3 = 17; BODY STATES 5 in-progress (sums to 16): NOT CONFIRMED, the one defect
RESULT carries: 38 appended across 9 existing groups, each list a strict prefix-preserving extension (counts match body); 2 on new groups (SEAT-SELFTESTS-CI 1, ROSTER-OPS 1) confirmed
RESULT data-loss: field-by-field diff of all 72 existing groups: no field dropped, no list element lost; changed fields only resume (8 stage moves + CI-LAYOUT next_step), carry (appends), brief (VENT-DETECTOR, SCORES, CI-LAYOUT), owner_gate (CI-LAYOUT), architect note per body; no unlisted change
RESULT lint: brief_lint from fresh origin/main d1db05dfc with this roster: TOTAL 0 errors (1 warning R10-RCA-FRICTION fix-review.md:29, no anchor); main's own roster lints 1 error (R10-SCORES coordinator.py:10281), which this PR fixes
RESULT after-edges: every after names an existing group (none dangling)
RESULT carry_audit pr 2467 at head: 0 finding items, 0 unrouted, 0 bad destinations
RESULT merge-tree: git merge-tree --write-tree origin/main d4f8914e exit 0, tree 37f15ba2, clean
RESULT ci: at read time no completed red check-run; closures, fast (3.14), instrument-self-tests, env-matrix, CodeQL analyze still in_progress, so ## Red checks "none" is unconfirmed for them; CodeQL neutral
RESULT fix-needed: change "5 in-progress" to "6 in-progress" in the Head/body stage sentence (and re-take the body, then carry); nothing else in the roster needs changing. This is a body-only fix, no code head move.
