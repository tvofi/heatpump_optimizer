Fix review: merge 81ee61752cff8ba51d41546f540e50ff1c950fac

bus-nonce: 56d82b5f4474218a23d510301be43ba9

Body-and-CI delta check at the unmoved head 81ee61752cff8ba51d41546f540e50ff1c950fac. The code verdict (p-3223-d3: 62 offline controls, 0 mismatches, all mutants killed) stands; this is not a re-measurement of code.

## Evidence

- Head: `git merge-base origin/main HEAD` = 8b49d50b0a4c3eebee0edeb6ec98aa365e3d004f (= origin/main at fetch); 81ee61752's first parent is 4404f5e74, whose parents are efb957882 and 8b49d50b0. `git diff 88d809f84 81ee61752` is exactly .github/workflows/tests.yml, dev/programme/delivery/3228.md, tests/ci_budgets.json (ev/resolution-delta.txt). `## Head` names all three correctly.
- Code unchanged: head equals the head p-3223-d3 reviewed. Claim files byte-identical to origin/main; the three-dot diff touches no golden, *budgets.json, VERSION or RELEASE_NOTES.md; no budget raise. `git merge-tree --write-tree origin/main HEAD` rc 0.
- Check-runs read over all 8 pages (30 per page, filter=all): 240 runs, 0 pending (ev/check-runs-all-240.tsv). Concluded non-green: tests / nightly-status x4 (failure), governance / delivery-status x4 (failure), governance / instrument-self-tests job 127449840281 (cancelled). Nothing else red or cancelled: arch-score and budget-raise-gate are green at every attempt of this head, so their body entries are correctly "earlier head".
- nightly-status and delivery-status: the diff touches neither their scripts nor workflows, plan, HANDOVER or a row it did not add (its one row is its own, delivery/3223.md); not this PR's per defect-root-cause.md.
- instrument-self-tests: attempt 1 job 127449840281 18:35:08Z to 19:05:21Z (30 min 13 s), cancelled in step "Show the CI predictor ..." (started 19:03:46Z, cancelled 19:05:19Z). Attempt 2 job 127491624532, 19:49:53Z to 20:16:30Z = 26 min 37 s, success, no non-success step. Matches the body.
- pr-contract after the last red: 127558241838 success 21:53:54Z-21:54:51Z. `merge_train.py classify` reads GREEN (ev/classify.txt).
- Carries: body Carry 1-4 present; roster ref handoff/audit-r10-roster (87826bec0) holds R10-RAISE-GATE-SHIM carries for items 870f6b21, aae60647, e70400f3 and 35c84a90, each ending Carry: R10-RAISE-GATE-SHIM. Packet carry_audit: 4 routed, 0 unrouted.
- Not re-derived: the body's "31 jobs (min 19 s, median 28 s, max 48 s)" for budget-raise-gate; the roster's carry for 870f6b21 says "the 40 most recent ci.yml" runs. I did not re-measure either; the discrepancy does not change the dismissed carry.

## Findings

- Follow-up: the body's `## Red checks` says of attempt 1 of governance / instrument-self-tests "no self-test step failing". The API and log say otherwise: step "Show the PR opener (delivery_row.sh's and pr_args.sh's self-tests) ..." concluded failure at 18:51:22Z (log: `FAIL mutant mut:unlock (its line deleted): the holder is still alive when the run returns`, `pr_args self-test: 174 checks, 1 failed`), then the predictor step was cancelled at the limit. That self-test is in open_pr.sh/update_pr.sh and passed unchanged on attempt 2 (same step, 3 min 12 s); this diff touches neither file, so it is a timing-sensitive instrument mutant (mut:unlock), not this PR's. The cancel's stated cause (limit) stands but the attempt had a prior flaky failure; the carry is the flaky mut:unlock row. Carry: dismissed: the diff does not touch open_pr.sh, pr_args.sh or update_pr.sh and the row passed on attempt 2; recorded here for the orchestrator's next read of instrument-self-tests.

## Block

none
