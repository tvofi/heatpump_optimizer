Fix review: merge 72ea40aa3a30dbd5b59fc16354f55f136367ece3

bus-nonce: 97b87360d92c0e4b7eee50f1892a621e

## Round

This is the fourth review round. It is a scoped re-check of round 3's block (`blocked 72ea40aa3a30 root-cause-unrecorded`, refs/heads/verdict/3051 at 410ff4f1ca8e). The head has not moved since round 3. The only repair is in the body, so round 3's code evidence at this head stands, as the brief says. I re-checked only the brief's three items. `fix-review.md` at origin/main e4c9e2016a45 is the contract I read. Since the merge base, main changed it in three places: it dropped a step-9 sentence, dropped a head-moved sentence, and added the closing self-audit. None of those affects this re-check, and I ran the self-audit (Evidence).

## Evidence

- (3) The head has not moved. At 15:05:24Z, `git ls-remote origin refs/pull/3051/head` gave `72ea40aa3a30dbd5b59fc16354f55f136367ece3`, and the PR API gave the same `head.sha` (`ev/head-reread.txt`).
- (1) Round 3's one block is answered.
  - The body's `## Red checks` now names `governance / instrument-self-tests`. It gives the cause: the uutils multicall `sleep` on `ubuntu-26.04` refuses the `unrelated-sleep` symlink at `tools/audit/seat/pr_args.sh:625`. It shows the check is not this diff's: the runner-image comparison, the other red PRs, and a three-dot diff that touches no instrument file. It points to #3086 for the fix.
  - It also records that no cheaper detector exists, with process state (d) and a cost test. That is the answer defect-root-cause.md's second trigger asks for.
  - The body does not claim the check is green.
- The whole check-run set, re-read from the PR check-runs API: 81 runs on one page of 100 (`ev/check-runs-latest.txt`).
  - `governance / instrument-self-tests` (124884844562, run 41291451430, concluded failure at 09:30:04Z) is still red. It is named and answered in `## Red checks`, as above. The body cites the job id 124803472179 for the same run, 41291451430, and the same 09:30:04Z conclusion; the API now lists that run under a new id.
  - Two `pr-contract / pr-contract` reds, 124884845369 and 124884848846, ended at 09:38Z and 09:40Z. That was before the body edit (PR `updated_at` 14:47:27Z). Their log carries the round-3 refusal.
  - Both pr-contract runs after the edit are success: 124881603541 at 14:47Z and 124884358912 at 14:58Z. The 14:58Z log reads `red checks the body must answer: ,governance / instrument-self-tests` and then `PR-BODY: 0 error(s)`.
  - Every `gate` run is success, the newest at 15:00:32Z, and so is `tests / fast (3.14)` (124884845022). Every other run is success or skipped.
- `python3 tools/audit/seat/merge_train.py classify 72ea40aa3a30dbd5b59fc16354f55f136367ece3` prints `GREEN ... pending: none red: none`, rc 0 (`ev/ci-classify.txt`).
- (2) `python3 tools/audit/carry_audit.py pr 3051` prints `2 routed, 0 unrouted, 0 bad destination(s)`, rc 0, as the brief expected. Both items, 8452abc0 and afa29e3c, are routed as dismissed evidence lines (`ev/carry-audit-pr.txt`). In CI, pr-contract's carry_audit on the body gives `3 routed, 0 unrouted, 0 bad`: carries 5 to 7, all routed to R10-PREPR-CAP.
- The review packet rendered with `Refusals: none` and `FIGURES: 22 resolved, 1 not verified, 0 refused` (`ev/review-packet.md`). Its gate digest was read at render time and showed the pre-edit pr-contract reds. My live re-read above supersedes it.
- I ran `git merge-tree --write-tree origin/main 72ea40aa3a30` against origin/main e4c9e2016a45. It gives rc 0, tree 52e53444f453, and no conflict: the `tests/closures.json` ledger driver merged `inert_reads` as a set (`ev/merge-tree.txt`).
- I did not run the finder's harnesses. No item in this re-check needs them, and round 3's code evidence at this unmoved head covers them.
- Round 3's two findings remain the orchestrator's to route, as round 3 recorded. The body now routes the instrument defect to #3086 and leaves the `ci_predict` arm with the root-cause seat. This verdict does not re-raise either.
