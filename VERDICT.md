Fix review: merge 2e952437192cd9e5fe0a59101b3b586c47bd6909

bus-nonce: 8e37ffa613d832c24654eefc2b8097ad

Delta review of PR #2041 (R9-DBG-2, closes #1940) from the round-2 merge verdict at `a102be64` to head `2e952437192cd9e5fe0a59101b3b586c47bd6909`. Evidence: `/Users/timmalmstrom/hpo-seats/review-2041-delta/evidence` (`mt.out`, `checks-final.tsv`). The head did not move during the review (checked at the end: `gh pr view` returns `2e952437`).

## (a) No non-bot commits since a102be64 on the branch side
`git log a102be64..HEAD` is one first-parent commit: merge `2e952437`, parents `a102be64` and `0c25836e`. `0c25836e` is origin/main's tip (`merge-base --is-ancestor` true). Everything else in the range is main's own history (#2049, #2050, and the bot's `ci: record delivery rows`). No authored commit on the branch.

## (b) The merge resolved nothing by hand
`git merge-tree --write-tree a102be64 0c25836e` gives rc 0 and tree `7523a15b…`. `git diff` between that tree and the head's tree is empty: IDENTICAL. The only conflict is `tests/closures.json`, resolved by the `LEDGER-MERGE` driver: `recorded.tests/harness_headers.py.seconds` takes the larger of 129.0 and 167.0, and `inert_reads.tests/harness_headers.py` merges as a set. I checked both in the parsed JSON against base `6b91e238`, branch `a102be64` and main `0c25836e`. The head's `inert_reads` set equals the union of the branch's and main's, with nothing dropped from either. It carries main's addition (`dev/audit/harnesses/r9_ro12_batch_mutants.sh`) and the branch's (`dev/audit/harnesses/r9_dbg2_selftest_price.py`), and `seconds` is 167.0. Every other key of the file equals whichever side changed it, with zero mismatches.

## (c) CI at the head, read from the check-runs API after it settled
Nothing is pending. `closures` (job 113199311221) is **success** and `closures-autofix` (113217100278) is skipped because there was nothing to re-record. This is the red that blocked round 2, and main's #2049 fixed it. `fast (3.14)`, `mutation`, `coverage`, `typing`, `pr-contract` and `Analyze` are success. `CodeQL` is neutral. Two non-green runs remain, and both are named in the body's `## Red checks`:
- `budget-raise-gate` 113199191915 is cancelled, and its twin 113199198325 is **success**.
- `delivery-status` 113199193151 is failure: `DELIVERY STATUS UNCHECKED — 72 rowed, 0 pending, 0 overdue (overdue at 12 commits)`. The body answers this check (`delivery-status` bullet): it grades main's record, which this PR's own row `dev/programme/delivery/2041.md` does not affect. The count there (64) is older than the run's (72), but the failure line is the same. The body's `## Head` names `2e952437`.

Round-2 findings and the residual (real-install snapshot size, owed by DBG-1) are unchanged by a main-only merge.
