Fix review: merge 4792a3d14df943c588a3a374ae5fbf8590bf01c6
bus-nonce: ff59e4cfe48140f2ed7c356abe7992f3

Round 2. I measured head 4792a3d14df943c588a3a374ae5fbf8590bf01c6. It is the authored code head 0c439ce78 plus two merges of main, and the merges leave tools/pr/merge_main_bot.py byte-identical to 0c439ce78 (git diff 0c439ce78 4792a3d14 on that file is empty). The roles diff from the merge base to origin/main is empty. git merge-tree against origin/main d4c94f9a4 exits 0. Evidence dir: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2297/evidence2

RESULT selftest head 40 checks 0 failed (base 24)
RESULT mutants 22 planted (my round-1 seventeen plus five aimed at the delta), 20 killed, 2 survived (mutants2.txt, runner mutants.py)
RESULT round-1 survivors: M9 (pin-plan dropped) KILLED, 2 FAIL; M16 (TypeError dropped from the except) KILLED, by an uncaught crash, which the body discloses; M11 deletion forms KILLED: plan_pr's pins= read deleted (3 FAIL), plan_pr's api not passed through (3 FAIL), plan_one's default back to lambda: [] (1 FAIL)
RESULT new arms: page-1-only runs read (M18) KILLED
RESULT survivor M11 (rewrite form): run() rewritten to bypass plan_pr and call plan_one with an explicit pins=lambda: []. That is a deliberate fail-open rewrite, not a deletion. Every deletion of the wire now fails closed (default lambda: None -> skip-pins-unread), so this residual does not block.
RESULT survivor M19: the overflow arm (more than ten full pages of 100 runs -> None) changed to pass. It is reachable only with more than 1000 runs at one head, and does not block.
RESULT guard order: M12 and M17 still killed; decide() refusals are unchanged and come first.
RESULT required contexts at the head (17, from ruleset rules/branches/main): every one success, none red or pending among the 45 check-runs (checkruns-4792a3d14df943c588a3a374ae5fbf8590bf01c6.json). wave-script, which runs this self-test, is success.

## Delta review
- plan_pr is now run()'s single per-PR step. For a fork it returns skip-fork with the listed head sha, as before. The branch-name guard in run() is unchanged.
- The pagination stops on a short page. A malformed page (workflow_runs None) raises TypeError and is caught, so it reads as None (unread). More than 10 full pages returns None, which fails closed.
- The tests.yml arm keys on two-space job ids and refuses a job-level name: override. A rename of any of the four jobs, or a renamed display name, now reddens the self-test (body M19/M20; I did not re-plant these).
- The docstring now states the transition-gap residual and the quiet-period wait. The body corrects the base count (24) and the bound.

## Residuals (not blocking, stated in the docstring)
A deferred head merges only on the next push to main or a dispatch. For a few seconds between one chain stage concluding and the next being created, no chain job is listed.

Not re-run: the gate and the mutation table (CI's).
