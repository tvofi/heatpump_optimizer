Fix review: merge 5017b5660ab6eb9ddc96f609ba642e404af9cbc3

bus-nonce: fedd5b0252c8e6ef74a299f0796c1863

CI-only re-check of the earlier ci-red block (head 1fca63cb1, cancelled by the 2026-11-04T22:51Z close). Content not re-reviewed.

## Evidence

- RESULT: review_carry 1fca63cb1 -> 5017b5660ab6eb9ddc96f609ba642e404af9cbc3: CARRY (one branch-only commit, a merge of origin/main). ev/review_carry.txt
- RESULT: merge_train classify: GREEN, pending none, red none. ev/classify.txt
- RESULT: check-runs, all pages (55 total, one page of 100): gate success (run 42133294182 at 01:15Z and run 42133294519 at 01:15Z), pr-contract, budget-raise-gate, arch-score, hassfest, codeql, tests/*, governance/* all success or skipped. No cancelled and no pending run remains. The 22:5xZ cancelled run of 41923437389 is superseded by runs 42133294182 and 42133294519 of the same checks.
- RESULT: two failures, both read in their job logs and both unrequired: "governance / delivery-status" (job 127618080236: overdue delivery rows, log says "NOT a required context and a red here blocks no merge") and "tests / nightly-status" (job 127618080432: nightly lane red, log says not a required context on main-protect). Neither concerns this diff, a triage markdown file.
- RESULT: body `## Head` names 5017b5660ab6eb9ddc96f609ba642e404af9cbc3. PR open, draft, mergeable_state blocked (awaiting review).
- RESULT: git merge-tree origin/main vs head: see ev/merge-tree.txt.
- Not re-run: mutation and null controls from the body; content unchanged since the first verdict.
