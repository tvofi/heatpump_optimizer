merge a80453d1877cbf7a5cb24e5b79ca46878c7e8a67

# R9-F1.7 fix review, PR #1788 (round 2)

Head a80453d1: the v2 code head 94a34b01 (fix commit c066af3b, plus the pins from 351b5ce7) merged onto
351b5ce7, then origin/main 48786f65 merged in. Round 1 blocked at 351b5ce7; its evidence is in
F1.7-review-858baeb2. Following tvofi's 19:59Z instruction, relayed by the coordinator, I stopped my
local gate and mutation-table runs part-way, and CI run 36763969584 at this exact head is the gate evidence.

## Round-1 blockers
1. **briefs: fixed.** c066af3b re-anchors carry-1395.json to sysid.py:1422, the call's line at the head.
   `node .claude/workflows/brief_lint.mjs` exits 0 (brief_lint_a80453d1.log), and CI `briefs` is success.
2. **nightly-ha (stable): fixed.** The contract's entry gains `async_start_reauth_if_available`, which counts
   as one reauth start, and the cite names both upstream versions. `tests/ha_contract.py --contracts-only`
   on real homeassistant 2026.9.3 reads `ALL 59 contracts PASSED` (ha_contract_real_2026.9.3_a80453d1.log).
   Its null control is round 1's head, where the same run read 1 of 59 failed. The stub reads
   `ALL 89 contracts PASSED` (ha_contract_stub_a80453d1.log). CI's nightly-ha job is skipped on this push,
   so the local 2026.9.3 run is the only evidence for the current release.
3. **carry-1644 conflict: resolved.** All five carries are kept (F3.2, F1.3, D12-s2-01, RCA-1747, F1.7).
   `git merge-tree --write-tree origin/main a80453d1` exits 0 at main 48786f65.

## Delta since round 1
`git diff 858baeb2 a80453d1` touches no file under custom_components/, and none of tests/features.py,
entities.py, replay.py, golden.py, harness.py or hastub. So round 1's mutants still apply (12 of 12 killed,
covering the barrier arms, reauth, the heat-loss scale seams and the #1655 prior), as do the finder
harness figures and the enumerator counts. The three-dot diff 48786f65...a80453d1 has no handoff/ path and
does not touch VERSION, the manifest or the notes heading. The claim file drops main's five inherited
EG-B8 claims, as in round 1.

## CI at a80453d1 (run 36763969584 and siblings)
All completed checks are success or skipped: fast (3.14), typing, mutation, closures, coverage,
coverage-ratchet, briefs, policy-docs, pr-contract, budget-raise-gate, delivery-status, nightly-status,
env-matrix, instrument-self-tests, hassfest, validate-hacs and CodeQL. None is red.
Mutation lane log (ci_mutation_job.log), read and not just its conclusion:
`3569 unpinned site(s) of 4113 candidate sites, 3573 at the ratchet base 48786f65` and `MUTATION TABLE PASSED`.
Every changed-scope site sampled is killed; coordinator.py:606 NULL_COMMENT is the lane's null control.
The stress.py CPU judgement stands from round 1: the rows go red at base alone on this box, so it is noise.

## Non-blocking
- carry-1644.json's `_comment` still calls F1.7's entry "the fourth carry", but it is now the fifth.
- Round-1 observations stand. The worker-side sysid logs no longer reach HA's log. The body's `## Head`
  labels e151e57c as the merge.
- The PR touches code-owned tests/golden.py and tests/harness.py, so it merges on the code-owner approval.
