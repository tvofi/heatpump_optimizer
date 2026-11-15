Fix review: merge 15bd225fe18f78c3b57772e13b05f4a6e1583671

bus-nonce: ecda057386ef6a142784d4b74824a43a

Round 1 (first review; no --reviewed-head).

## Evidence

- Head: `15bd225fe18f78c3b57772e13b05f4a6e1583671`. The remote branch still points there. The body's measured head is 91164e63, and `review_carry.py 91164e63 15bd225f` prints CARRY: a main merge (7ccb1835) plus the delivery-row record commit (15bd225f). `ev/HEAD.txt`.
- Merge with main: `git merge-tree --write-tree origin/main 15bd225f` exits 0 at origin/main 31117b10, with empty stderr. `ev/merge-tree.err`.
- CI: `merge_train.py classify 15bd225f --pr 3629` prints `GREEN 15bd225fe18f78c3b57772e13b05f4a6e1583671 pending: none red: none` (rc 0). The review packet listed no reds and no refusals. `ev/classify.txt`.
- Role contracts: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contracts are current.
- Artifact: run 43741911544 artifact 14174287444. I downloaded it through the MCP `download_workflow_run_artifact`. Its zip sha256 is `21243679cf94a01cb833960c4284ab52db371963081a12c6ff6f690d4b0645da`, which matches the body.
- Null control (step 3), using the body's drift one-liner (`selftest_scope.drift`, the in-tree logic of the CI drift step), with the head's `workflow_steps`: the base table 98847b99 prints exactly the four UNDER-SCOPED refusals the body names (policy-lint-mutants, dependency-graph-census, prepr, selftest-scope-mutants), `4 refusal(s)`. The head table prints `0 refusal(s)`. `ev/drift-null-control.txt`.
- Re-record reproduction: the body's union one-liner run on the base table reproduces the head table byte for byte (`git diff --quiet` rc 0). `ev/union-reproduce.txt`.
- Mutation proof (step 1): I enumerated every entry the head table has and the base table lacks. That came to ten entries, exactly the ten reads the body names. Deleting each one alone from the head table and driving drift gives `1 refusal(s)` every time: 10 of 10 killed, 0 survivors. `ev/mutants.txt`.
- Diff scope: three files (governance.yml timeout and comment, selftest_closures.json, the delivery row). VERSION, the manifest and RELEASE_NOTES are untouched (step 5). The claim files are untouched and no golden fixture moved, so step 4 has nothing to compare.
- Cheap self-tests at the head: `selftest_scope.py static` gives 119 gated step(s), 0 problem(s). `selftest_scope.py --self-test` gives 128 checks, 0 failed. `selftest_scope_mutants.sh --self-test` prints "SELFTEST-SCOPE MUTANTS: every mutant refused". All three match the body. `ev/static-selftests.txt`.
- Job-duration figures (step 8): I re-derived them from the jobs of the eleven listed runs via `list_workflow_jobs`. Six were cancelled at 60.2-60.3 min, and the other five ran 34.5-52.9 min. The mutant step started at 57.2-59.8 min in the capped runs. All of this matches the body. The ~67 min projection is 59.8 + 1.4 + 6.0 = 67.2. The two step spreads in that sum are the body's numbers; I re-derived the mutant-step start but not the per-step durations. `ev/job-durations.txt`.
- Not re-derived (step 8): the host regions and the ~2.3x host slowdown (I did not read the job-log `Region:` lines), the per-step min-max table, and the CodeQL 52.9-75.1 min durations. All of these are rationale for a cap or for a recommendation; none of them is a gated number.
- Python line counts at the head: dev 1151/191421, tests 84/216677, custom_components 92/74071 and tests/features.py 92325 all match the body. tools is 288/109953 against the body's 109906. The difference is +47 lines that the main merge 91164e63..15bd225f brought into `tools/*.py`, so the body figure is correct at its stated measured head. `ev/python-lines.txt`.
- Class (step 6): the enumeration rule is the drift check against main's latest measurement. It returns 0 refusals at the head, so there is no open seam. The timeout is a single seam: one cap, raised for push only, with the pull-request leg kept at 30.
- Harness (step 9): the finder's detector is the in-tree CI drift step, `selftest_scope.drift`, which I ran at both ends above. The one-liner wrappers are the fixer's and are disclosed in the body.
- Metric movement (step 14): the movement in `tools/ci/selftest_closures.json` is earned. It is the measured artifact unioned by the instrument's own `union_record`, and removing any added read makes drift refuse.
- Red checks (step 11): none on this branch. The owed-reds set is not engaged.
- Forward-carry: the body says none, and I found nothing to carry.
- Closing self-audit: `carry_audit.py check` rc 0, 0 finding item(s). The --body file held the PR body's Red checks, Forward-carry and Friction sections verbatim; the packet's head run over the full body also printed 0. `ev/carry-audit.txt`.
