Fix review: merge abebbedcd4acf859f2313d63ac1b8c9520749487

bus-nonce: a529b04404868c552ade79fbf6da5202

## Evidence
- Head measured: abebbedcd4acf859f2313d63ac1b8c9520749487 (PR head at read time, mergeable_state blocked only by review). Diff vs merge base: 2 files (roster json, delivery/2619.md); delivery row is the PR's own.
- RESULT ops: exactly 4 groups changed (R10-CURRENCY, R10-FLOW-RELAY-HOLD, R10-FLOW-YIELD-PROBE, R10-PREPR-CAP); 151 -> 151 groups, none removed, none new (jq from the body).
- RESULT stages: YIELD-PROBE done a9db4784 (#2579), RELAY-HOLD done 50808a75 (#2580), PREPR-CAP done f0724675 (#2528), CURRENCY in-progress; all three SHAs are ancestors of origin/main (is-ancestor rc 0).
- RESULT owed-PR: the three done groups have after=[] and no "PR 2/2", "P2b" or "follow-up" text in their entries.
- RESULT ops-count: git rev-list --count origin/main..324b6d312 = 4 = the body's count; merge base d7e1f9fc is the roster as #2613 landed it.
- RESULT brief_lint: TOTAL: 0 error(s) across 47 file(s). carry_audit check --body (body's Forward-carry/Friction sections): 0 finding items, 0 routed, 0 unrouted, 0 bad.
- RESULT merge-tree: origin/main vs head clean (rc 0; ev/merge-tree.txt).
- Role files on main unchanged since the merge base (empty diff of dev/governance/roles/).
- Mutation proof, null control and claim drift: n/a, roster-only diff, no production or test code. VERSION, manifest and notes heading untouched.
- CI at the head (41 check-runs, one read): the required checks pr-contract, delivery-status, closures, fast, briefs, mutation, arch-score, budget-raise-gate and hassfest are success; skips are by scope. One failure: nightly-status. It reads the nightly workflow's history, not the roster or delivery rows this diff changes, so it is not this PR's (defect-root-cause.md). The body's Red checks names main's six cancelled rerun-stale-contract runs and does not mention nightly-status, so this is not a finding.
- Not verified: the body's open-PR body reads (#2612, #2524, #2617) for carries to the three done groups; I did not re-read those PR bodies, sparing the API. The roster entries show no owed PR.

## Findings
none
