Fix review: merge 0d5680f7ad275fde1ab33b2a1124ce948e271682

bus-nonce: 8d0004004a8700a53502baef78ebf494

Delta re-check (sonnet) of 0d5680f7ad275fde1ab33b2a1124ce948e271682 against reviewed head 54f7f234ce4f0191ae32bc1609f1f8929162a618 (verdict merge). Head is still the PR head; origin/main is 0ae75bf, equal to the merge base, and `git merge-tree --write-tree origin/main <head>` exits 0.

## Evidence

- RESULT closures.json resolution delta: the tree of a clean merge of 54f7f234 onto origin/main (`merge-tree`, LEDGER-MERGE resolved tests/closures.json, tree 379966aed) differs from the head in tests/closures.json alone (ev/tree_vs_cleanmerge.txt, ev/closures_delta.diff). No other file changed beyond the merge of main.
- Entries that differ, all from commit 4bda0d525 (github-actions bot "ci: re-record closures"): (a) the arch_score closure gains tools/audit/archscore/planted/redteam/54_footprint_ifexp_body_chain.py and 55_footprint_boolop_control.py, which are this PR's own added files (both in the PR's three-dot diff); (b) recorded seconds for tests/arch_score_head.py, backtest.py, card.mjs, edge.py, optimality.py, plan_view.py, stress.py, a timing re-record with rc 0 throughout, not a closure membership change. Nothing is explained by main's newer commits. I did not re-run the closure driver (heavy; CI's `tests / closures` run on this head is green per ev/checks_full.tsv).
- review_carry.py reads FRESH-REVIEW only for that closures.json bot re-record, as the dispatch said; the two commits are the bot commit and the merge of main.
- Check-runs of the head over all pages: 55 runs (35 success, 17 skipped, 2 failure, 1 cancelled). merge_train classify: GREEN, pending none, red none (ev/classify.txt).
  - governance / delivery-status (run 42008148411, job 127180326711): failure, log reads "DELIVERY STATUS OVERDUE — 10 rowed, 11 pending, 13 overdue" and states it is not a required context. A main-ancestry grade; this diff touches no script it reads except its own row dev/programme/delivery/3218.md.
  - tests / nightly-status (job 127180326601): failure, log reads "NIGHTLY FAILED: slow failed last night" for scheduled run 41943946464 at head 499162c; not a required context, not this PR's.
  - governance / instrument-self-tests (job 127180326851): cancelled. Log and annotation: "The job has exceeded the maximum execution time of 30m0s" (governance.yml timeout-minutes: 30), the job started 10:11:00Z and was cancelled 10:41:17Z during the last step, `ci_predict.py --self-test`. This is the job timeout, not a red assertion, and not ci_priority's pause. main at 0ae75bf ran the same job in 23.7 min, so the head ran about 6 min over a near-cap job; the PR diff touches neither governance.yml nor tools/pr/ci_predict.py. It is not a required context (classify GREEN). Not re-run by me.
  - Every duplicated check name (arch-score, budget-raise-gate, pr-contract, gate, prelude, kernel-points, refresh, cancel-superseded) has only success/skipped runs. pr-contract has two successes, the later (10:52:40Z) started after the last red/cancel concluded (10:41:17Z).
- PR body: `## Head` names 0d5680f7ad275fde1ab33b2a1124ce948e271682 (and its merge of main 0ae75bf, 54f7f234). `## Red checks` answers tests / closures (cheaper detector ci_predict.py), pr-contract, and delivery-status / nightly-status as main's own. It does not mention this head's instrument-self-tests 30-minute timeout cancel; that conclusion is cancelled, not red, and pr-contract is green on this head.
- Step 3: this head contains #3208 (dev/governance/config/machinery_budgets.json exists at the head, the PR merged main 0ae75bf); governance / policy-docs is success, and instrument-self-tests failed by timeout, not by a missing file.
- This is a delta re-check; the code verdict of 54f7f234 is not re-judged. No mutation or measurement re-run.

## Findings

- Follow-up: governance / instrument-self-tests exceeded its 30 min timeout-minutes at this head (main took 23.7 min on the same job), so the job's margin is thin and a normal-speed runner can cancel it; not this PR's change. Carry: dismissed: job timeout on a near-cap main lane, outside this PR's diff and not a required context
