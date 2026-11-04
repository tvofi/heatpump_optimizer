Fix review: merge bb730c1eeeb63880bc42336f347f6587564a57b1

bus-nonce: 212affcdc97940d8e5b9a01ba6e4575c

## Round
Classify-only re-check of #3181 (R10-CI-RUNNER-FIXES) at bb730c1eeeb63880bc42336f347f6587564a57b1. This is the same head that the previous fix review (verdict/3181, 8903ffbaf) reviewed. That review found the code clean and blocked only on ci-red, because codeql / Analyze (python) was cancelled by the infrastructure (job 126550446352). The head did not move, so per the brief I did not re-review the code. The previous review's code findings carry below, unchanged.

## Findings
- Follow-up: the outer `if [ "$rc" -ne 0 ]` guard at the lane report (tests/run.sh:809) is pinned by no check. `_failed_marker_self_test` lifts only the inner block, and it sets rc=1 itself. Inverting the guard to `-eq` (M8), or replacing it with `true` (M9), leaves the self-test at 442 checks and 0 failed (verdict/3181 evidence/mutants_head.txt). The pre-PR one-liner was equally unpinned, so this is not a regression. The repair is to widen the lifted block to include the outer guard, and drive it at rc=0 as a null case that must print nothing. Carry: R10-CI-RUNNER-FIXES
- Residual: the group's first carry (the owner's "Build it now" item, plan-regain card 9: an edit run exits without holding a runner, and the code run's gate re-dispatches the body units) is still not built at this head. It stays at carry[0] of R10-CI-RUNNER-FIXES in dev/programme/rosters/wave-r10-groups.json. The orchestrator must not close the group when this PR merges. Carry: R10-CI-RUNNER-FIXES

## Evidence
- RESULT classify: `python3 tools/audit/seat/merge_train.py classify bb730c1eeeb63880bc42336f347f6587564a57b1 --pr 3181` printed `GREEN bb730c1eeeb63880bc42336f347f6587564a57b1 pending: none red: none`, exit 0 (ev/classify-1.txt).
- Head unmoved: `git ls-remote origin refs/pull/3181/head` gives bb730c1eeeb63880bc42336f347f6587564a57b1, both at the start of the review and before the return (ev/HEAD.txt).
- Check runs: I read the whole set through the commit's check-runs API with every page paginated (ev/check_runs.tsv). There are 55 runs: 37 success, 17 skipped and 1 failure.
  - codeql / Analyze (python), run 126585714800, re-ran and concluded success at 13:36:53Z.
  - Both gate runs, 126608789598 and 126608243068, concluded success. Both pr-contract runs concluded success.
  - The one failure is tests / nightly-status. It is inherited: it grades main's nightly, the diff reaches nothing it reads, and the body answers it, as the previous verdict recorded.
- Merge: `git merge-tree --write-tree origin/main bb730c1ee` exits 0, giving tree 39b7069d87f3 against origin/main 8e90d8144. That is the same tree and the same main as the previous review (ev/merge-tree.txt).
- Role contracts: the three-dot diff of dev/governance/roles/ between the merge base and origin/main is empty.
- Review packet: rendered with `review_packet.py render --pr 3181 --head bb730c1ee...`, exit 0 (ev/packet-render.txt).
- Not re-derived in this re-check: the mutation results, the class enumeration and the body's figures. They were verified at this same head by the previous review (verdict/3181), and are cited, not re-taken. Carry: dismissed: evidence, not a finding
