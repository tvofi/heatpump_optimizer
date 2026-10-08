Fix review: merge e4fa486c0ce36463091b26b09f4fd318ebd1d228
bus-nonce: 0ca5a0ba02de751487d6c2e79aa96438

Round 2. Measured at e4fa486c0ce36463091b26b09f4fd318ebd1d228, the live head, which I re-read before posting. Merge base 9cac1947 (#2055). Detached worktree /Users/timmalmstrom/hpo-seats/review-2053/wt; evidence /Users/timmalmstrom/hpo-seats/review-2053/evidence/r2, with round 1 in the parent directory. The roles directory is current with origin/main.

## Round-1 items

- a. `## Red checks` now names `closures` 113217602310 and answers it: main's red from #2051, repaired by the bot commit `6ddb8c4c` and by #2055, with no cheaper detector because the inert dimension is recorded only under Linux strace. It also names both `pr-contract` reds as body staleness. Done.
- b. `## Head` names the live head `e4fa486c`, the code head `5d4d30a7`, the main merge `9cac1947`, and the bot commit `6ddb8c4c` with its content. Done.
- c. `stale_run` now re-runs every red `pull_request` run at the head (`5d4d30a7`). Done; verified below.
- d. The carry is corrected: GitHub's ruleset blocked #2009, and the remedy is to re-run every non-success run. Done.

## The stale_run change

- Self-test at the head: `budget_raise_gate self-test: 206 checks, 0 failed` (`selftest-head.txt`).
- Failing test first, which is also mutation 1: the red list taken over `same[-1:]`, the old newest-only rule, gives `3 failed`. The failures are the two-red-twins case, the older-red-beside-newer-green case, and the end-to-end two POSTs.
- Mutation 2, the `going` wait removed: `4 failed`.
- Mutation 3, POST only the first id: `1 failed` (the end-to-end two-POST case).
- Null control: both twins green re-runs nothing (`('none', [])`), and that check passes.
- No caller depends on the old `(action, int)` shape. `rerun_stale` is the only caller. `entities.py`, `pr-contract-rerun.yml` and `governance_cost.py` name the job or the flag, not the return value.
- Can it loop? No. A re-run keeps the run's original event, `pull_request`, and `stale_run` returns `none` for any trigger that is not a passing `pull_request_review` run of the gate (self-test: "a pull_request trigger re-runs nothing"). `budget-raise-gate-rerun.yml` fires on `workflow_run` completion only. Each review completes once, so it causes at most one re-run per red run.
- Can it re-run a run that is red for a real reason? Yes, and that is harmless. A re-run re-grades from nothing: the program is restored from the base and the reviews are read live. A raise without a valid owner approval at the head re-runs red. A run whose payload carries an older base (a retarget) re-runs against that base and stays red. Both fail closed. It never writes a verdict itself and cannot turn a red green.
- Residual, not blocking. Two passing review runs completing close together (two approvals) can each POST a re-run of the same run. The second POST is refused while that run is in progress, so `rerun_stale` returns 1 and leaves the rest of the list unposted in that job. That job is not a required context, the first job's re-runs proceed, and main's single-run version already had the same exposure.

## CI at the head (CI's own runs, not re-run)

- 42 check runs. The only reds are `delivery-status` 113276056314 and `nightly-status` 113276056343.
  - Both are main's. The three-dot diff touches neither `tests/nightly*` nor delivery history beyond its own row, so by step 11 neither is this PR's.
  - `pr-contract` is green on its newest run (113288006697, 11:29:13Z), so the body is not refused for leaving `nightly-status` unnamed.
- `closures` is green (113276154073).
- `budget-raise-gate`: two `pull_request` runs at this app_push head, 113276055172 and 113276056125, both `success`, none cancelled. This is the third live head showing the fix.
- `git merge-tree --write-tree origin/main HEAD` exits 0. The `tests/closures.json` three-dot diff is the two `seconds` figures plus a re-sort of one `inert_reads` entry (`r9_ro12_batch_mutants.sh`), set-equal.
- VERSION, the manifest, RELEASE_NOTES and the claim files are untouched.

Round-1 findings that still stand at this head: the mechanism census, the workflow invariants, and the entities mutation results (the workflow and `entities.py` diff is unchanged since round 1; CI's `fast` at this head is green).

## RESULT

RESULT selftest head=206 checks 0 failed
RESULT mut newest-only=3 failed; no-wait=4 failed; post-first-only=1 failed
RESULT live_head_twins e4fa486c budget-raise-gate=2 success, cancelled=0
RESULT reds_at_head delivery-status, nightly-status (main's, unrequired); pr-contract newest=success
RESULT merge_tree rc=0
