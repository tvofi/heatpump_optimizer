Fix review: merge e0fca1fa0684609776d519c37a4e08b32a86121f

Full review of stage 2 (merge_group triggers), now standing on main d536fb4d, which carries #1823.
- The tree of e0fca1fa equals git merge-tree d536fb4d f88438dd: clean.
- The diff against main (8 files) is byte-identical in +/- lines to the delta I judged sound in round 1
  (c5102ea7..f88438dd). Round 1's only block was the stack it sat on, which is now cleared.
- Re-scan on the merged tree, which includes #1822, #1808 and #1816:
  - Each of the 17 required contexts has a producer that lists merge_group, and its job-level if: runs there.
  - The pull_request-only steps and jobs that remain are all non-required: coverage and coverage-ratchet,
    autofix pin measurement, nightly-status, graders-head-copy, the three autofix jobs and delivery-status.
- HEAD^2 is enforced with fetch-depth 0 in fast, pr-contract and budget-raise-gate, so a non-MERGE queue
  fails closed. No PINNED reads merge_group.head_sha.
- At e0fca1fa: codeowners_gap uncovered_files=0, and merge_fastpath --self-test 25/25.
NOTE: no CI exists yet (stage 2 is not opened). The first queue entry is the first real run of the
merge_group path, so watch its fast and pr-contract logs.
UNRUN: CI, typing, real-HA.
