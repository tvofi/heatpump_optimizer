Fix review: merge 805f5759c9f396a3fa7e88b2605cee0164685906

bus-nonce: d3c8522b5bbbef4a4eb8e5389a2a8f83

Round: repair round after the earlier blocked mutation-vacuous verdict. Measured head 805f5759c9f396a3fa7e88b2605cee0164685906, re-read as the PR head at posting.

## Evidence
- CI: merge_train.py classify exits 0, "GREEN 805f5759c9f396a3fa7e88b2605cee0164685906 pending: none red: none" (ev/classify.log). Earlier gate reds at this head were deferral runs, superseded by the green outcome; no required check is red, so no root-cause answer is owed.
- Merge: git merge-tree --write-tree origin/main head, rc=0, no conflict (ev/mergetree.txt).
- Version/manifest/notes/claim files untouched: diff touches only the harness, delivery/3337.md, tests/closures.json (one inert entry), roster_queue.py (ev/diffstat.txt).
- Self-test at head: "roster_queue self-test: 62 checks, 0 failed" (ev/selftest.txt). The body's Figures say 56 in one place and 62 in its merge-round paragraph; 62 is the head figure, 56 predates the merge from main.
- Harness at base roster_queue.py: stale, cascade, follow all RESULT: FAIL; at head all RESULT: PASS (ev/harness_base.txt, ev/harness_head.txt).
- Mutants M1-M7 re-applied by me as one-line edits and restored by cmp (ev/mutants.txt): M1 harness FAIL + self-test 3 failed; M2, M3, M4, M7 harness FAIL; M5 self-test 2 failed; M6 self-test 1 failed. 7 of 7 killed under the body's rule.
- Class rule: the body names a single seam (roster_queue._run_op's lint refresh and refusal cleanup); I found no further site and treat the class as one seam.
- Forward-carry: body says none; nothing in the diff changes a later stage's work.

## Findings
none
