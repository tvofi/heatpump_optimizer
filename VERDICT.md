Fix review: blocked 6ddb8c4c44d2851dabf6f9f3c19baa1d815d9dbf root-cause-unanswered: closures went red at 3362e0f0, unanswered
bus-nonce: e0926707adc49fb6201f6d40e1a18a24

Round 1. Measured at 6ddb8c4c44d2851dabf6f9f3c19baa1d815d9dbf (live head re-read before posting, unchanged), merge base 470bbd60. Detached worktree /Users/timmalmstrom/hpo-seats/review-2053/wt; evidence /Users/timmalmstrom/hpo-seats/review-2053/evidence.

## What holds

- Mechanism, re-derived. Fresh fetch of 300 `budget-raise-gate.yml` runs (2026-10-07T00:51Z..10-08T08:46Z) with `run_twins.py`: `same-sha-twin=80 other=2`. My own classifier (`mycensus.py`, different rule: any same-SHA `pull_request` sibling, no window) gives 81 of 82 cancelled runs with a sibling. All 82 were sent by `hpo-author[bot]`, the median gap to the sibling is 1 s, and 74 of 81 cancelled runs have the lower id. No `pull_request_review` run was cancelled. `app_push.sh` pushes and then PATCHes the body (line 257). The body's 85/2 is a sliding window that I re-derived only in shape, not the exact count.
- The fix works live. At `e7bb6f19` and `3362e0f0`, both app_push heads under the PR's own workflow file, there are two `budget-raise-gate` check runs each, both `success`, and none `cancelled`.
- Header invariants hold: one job, no job-level or step-level `if:`, and the events are `pull_request`, `pull_request_review` and `merge_group` (`header-invariants.txt`).
- Failing test first, mutation and null control, re-run myself (venv-ci 3.14, `PYTHONPATH=tests/hastub`):
  - head: `ALL 2212 ENTITY CHECKS PASSED`
  - `cancel-in-progress: false` changed to `true`: `2 of 2212 ENTITY CHECKS FAILED`
  - group changed back to `pull_request.number`, still no cancel (my own planted mutant, the serialised shape): `2 of 2212 FAILED`, with `groups='Budget raise gate-7'/'Budget raise gate-7' cancel='False'`
  - main's workflow block under the new checker: `2 of 2212 FAILED`
- Key risk (2), a stale run overwriting the verdict. No wrong green is possible. #2009's head (`55169727`) shows a `cancelled` run in the older suite 101794775588 that blocked the merge ("base branch policy prohibits the merge") even though the newer suite 101794777398 was green. The merge went through 27 s after that older suite was re-run. So the ruleset does not take the newest run: a non-success latest run in any suite blocks, which is fail-closed. Review-event runs already got per-run groups on main (`event_name == 'pull_request'` gated the shared group), so the review-versus-push race is unchanged by this diff.
- `git merge-tree --write-tree origin/main HEAD` exits 0, and `LEDGER-MERGE: resolved tests/closures.json`. GitHub's DIRTY comes from the missing driver. VERSION, the manifest and RELEASE_NOTES are untouched, and the claim files are unchanged.

## Blocking

1. **root-cause-unanswered / body staleness.** `closures` went red at `3362e0f0` (check run 113217602310: `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/git_auto_maintenance_race.sh`, inherited from #2051 on main). `## Red checks` does not name it, and the contract itself refuses the body for that reason: `pr-contract` 113229290002 at 08:51Z says "check `closures` is red and `## Red checks` does not name it". `## Head` names `3362e0f0` as the top and never mentions the live head `6ddb8c4c` (`ci: re-record closures`, the bot commit that adds `git_auto_maintenance_race.sh` to `inert_reads` and moves two `seconds` figures).
2. **harness: class-open `tools/policy/budget_raise_gate.py:stale_run`.** Its docstring says "Only the NEWEST of those matters -- it is the one the pull request shows", and it re-runs only the newest red `pull_request` run at the head (`stale-run-twins.txt`: given two red twins and a passing review run, it returns `('rerun', 2, ...)`, and run 1 stays red). This diff makes the older twin complete. So on every raise PR pushed by app_push.sh, both twins are red before approval, and after approval one red stays that `budget-raise-gate-rerun.yml` never re-runs. By the #2009 evidence the ruleset reads it. This is not a regression against main, where that twin was `cancelled`, `RERUN_CONCLUSIONS` excludes `cancelled`, and a hand re-run was equally needed. But the body's safety sentence "`budget-raise-gate-rerun.yml` still re-runs a stale red after an approval" is false for the twin, and the seam is neither in the diff nor dispositioned.

## One-pass fix list

- a. `## Red checks`: name `closures` (113217602310 at `3362e0f0`). Answer it as main's inherited red from #2051's missing `inert_reads` entry, repaired on this branch by the bot's `ci: re-record closures` (`6ddb8c4c`) and separately by the main fix PR, and say which cheaper detector exists or that none does. Also name the two `pr-contract` reds (113212898963 at `e7bb6f19`, 113229290002 at `3362e0f0`) as body staleness that the re-take clears.
- b. `## Head`: lead with `6ddb8c4c44d2851dabf6f9f3c19baa1d815d9dbf`, the bot commit `ci: re-record closures`, its content (one `inert_reads` line and two `seconds` figures), and its cause.
- c. Close the `stale_run` seam with one of these two:
  - (i) Change it to re-run every red `pull_request` run of the gate at the head, and add a self-test case "two red twins at one head, both re-run". The program is restored from the base, so this takes effect after merge.
  - (ii) Disposition it in the body as an R9-CI-2 carry and correct the sentence about the re-run workflow.
- d. Correct the carry "Merge scripts reading cancelled-before-success as blocking". On #2009 GitHub's ruleset itself refused the merge, not only the scripts, so "the readers should judge each context by its newest run" would not unblock anything. Every red run at the head has to be re-run green.

## RESULT

RESULT twins_fresh_window same-sha-twin=80 other=2 (run_twins.py, 300 runs)
RESULT cancelled_by_author_app 82/82, median sibling gap 1 s
RESULT live_head_twins e7bb6f19=2 success, 3362e0f0=2 success, cancelled=0
RESULT entities head=ALL 2212 PASSED; mut-cancel=2 FAILED; mut-group=2 FAILED; base-workflow=2 FAILED
RESULT stale_run two red twins -> reruns id 2 only
RESULT merge_tree rc=0 (LEDGER-MERGE resolved tests/closures.json)
