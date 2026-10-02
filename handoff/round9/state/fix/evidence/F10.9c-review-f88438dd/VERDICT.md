Fix review: blocked f88438ddbf41cf11ceeacf60a5314e77832ffefa stack: rides on c5102ea7, which is blocked; own merge_group delta judged sound

Round 1, stage 2 (not yet opened as a PR). This PR's own delta (c5102ea7..f88438dd) is sound. It cannot merge
because its ancestry carries stage 1's blocked fast path and the orchestrator.md conflict with main. Once
stage 1 is repaired and this branch merges that repair in, I judge only the resolution delta.

CHECKED
- All 17 recorded required contexts (fixtures/required-contexts.json) have a producer that lists merge_group,
  and the job-level if: runs there (the new entities check, with its null control).
- No step inside a required job is skipped on merge_group in a way that would let the job pass without
  measuring. The steps still gated on pull_request are autofix pin measurement, nightly-status,
  graders-head-copy, delivery-status and the coverage pair, none of which produce a required context.
- Second parent: fast, pr-contract and budget-raise-gate use HEAD^2 under set -e. fetch-depth: 0 is set in all
  three. A squash or rebase queue therefore fails closed. pr-contract and budget-raise-gate also check that
  the API's PR head equals HEAD^2.
- Every PINNED on merge_group is pull_request.base.sha || merge_group.base_sha (|| github.sha only where it
  was before). Nothing restores from merge_group.head_sha.
- Scoping reads three-dot from base_sha to the queue commit. For entry k it may include the entries ahead of
  it, which is a superset and so conservative. GOLDEN_REF=HEAD^1 and CLAIM_HEAD=HEAD^2 match a PR's
  synthetic merge.
- codeowners_gap --check: uncovered_files=0. merge_fastpath --self-test: 0 failed.

NOTE: no PR run exercises the merge_group path. The first queue entry is its first real test, so the
orchestrator should watch that run's fast and pr-contract logs.
UNRUN: CI on this head (not opened), typing, real-HA.
