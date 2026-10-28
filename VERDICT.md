Fix review: blocked b5cf12dfe83705acaf5726b8e018e84174ac8883 record-contradicts-diff: R10-RCA-CI-RATCHET-RUN-NAME.md section 5 says the 4 assembly defects are not registered in bugclasses.json, which this PR's 35a535f51 registers as N-p2b-assembly-reader

bus-nonce: 0afd3158490326156c258487e56444d7

## Round

1 (no earlier verdict on #2696). Measured head b5cf12dfe83705acaf5726b8e018e84174ac8883, still the PR head when written. Contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

- `dev/audit/rca/R10-RCA-CI-RATCHET-RUN-NAME.md:141` (section 5, "What I did not establish") reads: "They are not registered in `bugclasses.json`; I did not register them." Commit 35a535f51 in this PR registers exactly those four (`N-p2b-assembly-reader`, `non_round_instances` bd0d4d603, 69a26d2a2, 168365196, d5dc3e26a) with `rca: [R10-RCA-CI-RATCHET-RUN-NAME]` and the note "Triage P52 (2026-10-24) rejected a barrier". The RCA file was written in 776d37392 and not touched after, so the durable record this PR lands states the opposite of the register row it lands beside, and never mentions triage P52. A later seat reading the RCA as fact would conclude the class is unregistered and owes registration. Fix: rewrite that bullet (and the section 4 / section 5 text on whether the 4 defects make a class) to say the class was registered listed-not-counted and triage P52 rejected a barrier.
- While re-cutting the body: `## Red checks` should also name `pr-contract / pr-contract` on the body-edit run 40089109084 at this head (see Findings); it is not this PR's, but it is red on the head and the body is silent on it.

## Findings

- `pr-contract / pr-contract` is red at this head on the `CI edit` run 40089109084 (job 120861590328, attempt 2, carried unchanged into attempt 3 as job 120863615751). The failing step is "Wait for code scanning and list its open alerts": `codescan_wait.py` exited 1 at 11:34:15, and its `FAIL closed:` reason went to stdout, which the step redirects into /tmp/pr-alerts.txt, so the log does not show it. The timing matches step 1's "no run at this head owns a finished codeql unit": the code run 40089109480's `codeql / Analyze (python)` did not finish until 11:38:20. The code run's pr-contract (job 120863373662, started 11:42:26) passed, and its red-history record listed only coverage/coverage-ratchet. So this is an instrument race, not this PR's defect. There is a separate instrument gap: the `FAIL closed` reason is not shown in the log, and attempt 3 did not re-run the failed pr-contract job. Carry: dismissed: not this PR's (an instrument race between an edit run's codescan_wait and the code run's codeql), and naming it in the body's ## Red checks on the next push is enough for this PR; the instrument gap needs no PR here

## Evidence

- RESULT mutation (schema): I removed `N-p2b-assembly-reader` from finding.schema.json's class_guess enum, and `agreement_py.py --run` printed `DIVERGENT finding-class-id "N-p2b-assembly-reader"` and `AGREEMENT REFUSED`. Restored.
- RESULT mutation (rca row): I deleted the `R10-RCA-CI-RATCHET-RUN-NAME` _rca entry from bugclasses.json, and `fold_ledger.py check` printed `UNKNOWN-RCA: N-p2b-assembly-reader cites R10-RCA-CI-RATCHET-RUN-NAME` and 1 violation. Restored. This matches the body's mutation account.
- RESULT head: `fold_ledger.py check` gives 0 violations (46 classes, 121 rca entries). `agreement_py.py --run` gives `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`, which is the body's claim. `fold_ledger.py sync` reports that audit-find.js already carries the schema (no drift).
- Merge: `git merge-tree --write-tree origin/main b5cf12dfe83705acaf5726b8e018e84174ac8883` exits 0 against origin/main e8a08cf9e. No conflict.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched (three-dot diff is empty). CI's prepr version-edit step agrees.
- Figures, re-derived: `ci.yml` runs created 2026-10-23T06:00Z..2026-10-24T06:00Z total_count = 113, which matches. Red push runs on main: 5 (d5dc3e26a, 94bec976b, 15f0b5924, 88744e573, 50af6174f), which matches. "6.0 h (02:36 to 08:35Z)" is a floor, taken at the doc's read time, and the doc says so. The actual red lasted until 9fd5eb107's push run went green at 10:19:58Z, about 7.7 h. A larger cost(defect) lowers the break-even to P > ~0.0047/day, which does not change the verdict of the cost test as argued. 1.14 s per job call and 129 runner-s/day were not re-derived (they come from job 120752118657 timestamps, which I did not open).
- Class search re-run: I grepped for `["name"] ==`, `.get("name") ==`, `.name == "CI"|"Tests"` and `select(.name ==` over tools, tests/*.py, tests/*.sh and .github. Every other hit keys a job, check-run, ruleset, artifact, device or fixture name, not a workflow run's `.name`. That agrees with "one affected reader". This is my own grep, not a committed harness. The RCA names none, and a docs-only RCA owes none.
- No mutation table is owed: the diff changes no production code line.
- CI at this head, from the check-runs API: the code run 40089109480 is green across every required lane, including pr-contract (red checks the body must answer: none; red-history record: tests / coverage, tests / coverage-ratchet, both answered in the body as a pip ConnectionResetError on 7ad01d0f1). The edit run 40089109084 has pr-contract red, covered under Findings. Its gate failed on attempts 1 and 2 and passed on attempt 3.
