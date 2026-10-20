Fix review: merge 3451d97273f75ad114a00f92e355647f427e7c53

bus-nonce: 97e7f7117c406089d362169ee6912f70

Round 2 (round 1 blocked body-figures-stale at 84326c5ca). Measured at head 3451d97273f75ad114a00f92e355647f427e7c53, still the PR head at posting; origin/main 2bd48adfa.

Diff (ev/stat.txt, ev/diff.txt): origin/main...HEAD touches only dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2471.md. Group-by-group comparison of the JSON: one new group (R10-UPDATE-PR-LOCK), R10-SAVINGS-NEGATIVE resume changed (done, commit 73a6ca86), R10-CEILING-PROBE carry 0 to 1, R10-ROSTER-OPS carry 1 to 2. Nothing else differs.

Figures recounted from the JSON at origin/main and at HEAD: groups 89 to 90; stage done 42 to 43; carries 196 to 198. Body states exactly these, plus 1 new group, 1 stage change and 2 carries appended (CEILING-PROBE 0 to 1, ROSTER-OPS 1 to 2). All re-derive. The Head section lists several superseded heads before the real one, which are history and not figures.

Carry text: the CEILING-PROBE paragraph was verified against #2465's body in round 1 (unchanged, same diff lines). The ROSTER-OPS carry records the round-1 finding (open_pr.sh reusing #2467's body, regenerating only the Head paragraph, with the fix or refusal proposal) and matches the body's Forward-carry item in substance; the carry is longer than the body item (it adds the proposed remedy), not contradicted by it. It is routed with Carry: R10-ROSTER-OPS, an existing group.

Merge: git merge-tree --write-tree origin/main HEAD exits 0, no conflicts, no MERGE-CLAIM lines (ev/mt.out, ev/mt.err).

CI (ev/checks.tsv, check-runs API at this head, read after all runs concluded): 28 success, 20 skipped, 1 neutral, 0 red, 0 pending. Body states Red checks: none, which is correct.
