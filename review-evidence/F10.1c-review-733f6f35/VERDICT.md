Fix review: merge 733f6f35

Merge-delta check, after round 2. I measured head 733f6f35a42c78758b3478d296987f526eca1b81, a merge commit with parents e26fa13b (reviewed, merge verdict in round 2) and main 404a5fb0, which is main's tip.

RESULT tree: 733f6f35^{tree} = e285975d is byte-identical to `git merge-tree --write-tree e26fa13b 404a5fb0` (rc 0, no conflicts). The merge adds nothing by hand.
RESULT overlap: of this PR's files, main 6793659c..404a5fb0 touches only tools/audit/bugclasses.json. Per class (34 at both ends), each entry at the head equals main's version where only main changed it and the branch's version where only the branch changed it, and no entry changed on both sides. P7 carries the round-2 barrier and barrier_gap text unchanged.
RESULT dst_checks at 733f6f35: ALL 78 DST / QUARTER-GRID CHECKS PASSED, 57.5 s wall.
RESULT census rg "\bnow (\+ timedelta|- self\._)" at 733f6f35: 10. Main's F1.9 and F10.2 added no raw site, so barrier_gap's count still holds.
RESULT structure.py at 733f6f35: STRUCTURE RATCHET PASSED. bugclasses.json parses.
The PR body's Head line names code head e26fa13b and PR head 733f6f35 as the merge with 404a5fb0.

CI at 733f6f35 when posted: typing, briefs, closure-scope, pr-contract, policy-docs, budget-raise-gate, delivery-status, nightly-status, hassfest, validate-hacs, env-matrix, instrument-self-tests and wave-script are green. fast (3.14), mutation, coverage, closures, browser and CodeQL python were still running. The merge seat merges on all-green CI.
