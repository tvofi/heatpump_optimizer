Fix review: merge 488c30d0c504b09104cbbf7f86ffd31057e220c7

bus-nonce: 44d118eea2512424fc93f5ca3efba628

## Summary
Roster PR #2613, head 488c30d0c504b09104cbbf7f86ffd31057e220c7 (code tip d7e1f9fc0, main 752f697cc). Data-only; first review round. Measured this head.

## Evidence
- Item 1: set-stage SHAs 49018a8be (#2584), 9af4664c1 (#2606), 2c0c47494 (#2605) are all ancestors of origin/main. Roster diff vs main: R10-FLOW-MAIN-GATE, R10-RCA-INSTALL-RATELIMIT, R10-NIGHTLY-PYSPY-RETRY done with those commits; R10-FLY-GH-READ-RETRY in-progress (its carry still states PR 2 and PR 3 owed); R10-FLOW-RELAY-HOLD unchanged not-started. The three done groups' carries owe no PR 2/2; MAIN-GATE's carry b87aa9e4 (reviewer-refusal arm) is built in #2584 (classify CLI for reviewer dispatch, K15 (d) in the merged diff).
- Item 2: git rev-list --count 59eb73ac5..d7e1f9fc0 = 23 (ev/revlist.txt). Re-derived: 151 groups on main and on head, none removed, none new, 17 changed (my own python equivalent of the body's jq; the jq itself not run).
- Item 3: the five open bodies (#2612 #2580 #2579 #2528 #2524) carry no Carry: line to a done group; #2612 mentions R10-TARIFF and #2580 R10-RCA-ORCH-CONTINUITY only in prose, not as carries.
- Item 4: brief_lint TOTAL: 0 error(s) (ev/brief_lint.txt). carry_audit check run against an empty body only (PR body text not saved locally); the body has no Carry: lines and Forward-carry: none, so 0 unrouted is by inspection. merge-tree with origin/main rc=0, clean (ev/merge-tree.txt). VERSION untouched.
- CI on the head (one check-runs read): pr-contract, briefs, closure-scope, mutation, policy-docs, delivery-status, wave-script, scope success; fast, closures, env-matrix, instrument-self-tests, CodeQL analyses still queued or in progress when read. The only red is nightly-status (failure); it is not this PR's, as the diff reaches nothing it reads (defect-root-cause.md). The body's Red checks section read main's tip, not this head, and names none.
- Mutation proof, null control: n/a, roster data only.
