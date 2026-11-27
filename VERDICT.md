Fix review: merge 9bc1e9b9927a2a73c13d8dcc66a3288e48c03177
bus-nonce: 2565461bf6194f3ea8b92548f3ab5746

Round 1, full scope (no prior reviewed head). Measured in a detached worktree at 9bc1e9b992; merge base d380053b01. Roles diff against origin/main is empty, so the contract is current. Head 9bc1e9b992 is cc280c0449 plus three mutation-ledger pins only (`git diff --stat cc280c0449 HEAD`: 3 files, all under tests/mutation_ledger).

RESULT duty-block: ALL 5 FEATURES BLOCK PASSED (features_block.py over the N-solve-recompute block, prelude emitted from this tree)
RESULT mutation: 5 targeted mutants, each fails 1 block check, then restored: switch press back to publish_then_refresh; `_actuate_plan` dropped from async_apply_held; `not refreshing` dropped from overlay_only; the `_entry_released` guard dropped; the cycle's `_actuate_plan` call deleted
RESULT enumeration: enumerate.py prints seams=27 at the base and seams=28 at the head; the added seam is async_apply_held's fallback request, which the body dispositions; every head seam has a disposition in the body
RESULT structure: STRUCTURE RATCHET PASSED; the two budgets move down because the write tail moved into `_actuate_plan` and the diagnose publish now shares `_publish_uncycled`
RESULT version: VERSION, the manifest and RELEASE_NOTES untouched; no golden or claim file in the diff
RESULT merge-tree: `git merge-tree --write-tree origin/main HEAD` exit 0
RESULT live-checks: every owed check is green at the head; only tests / nightly-ha (2025.2.0, stable) and nightly-status are red, and none of them is owed (merge_train.py owed-reds)

Note: harness-host: the finder's tree probe (sweep N-solve-recompute probe.py) reads recompute=0 on this host for every arm at both ends, the null `refresh` arm included (reproduced=1 of 2, dist_to_reference 0.304). So it does not discriminate here, and I could not re-derive the body's null-control figure (refresh recompute=1). It drives the request path by hand and cannot measure the switch anyway, so the entity-driven duty block plus the mutants above are the evidence I rely on. Carry: dismissed: evidence, not a finding
Note: nightly-red: nightly-ha fails on a5:pages_ok (grid:InvalidData, an options-flow page) and run:exit_status. That is not the duty-switch path this diff touches, and the check is not owed. Carry: dismissed: a non-owed red with a cause outside this diff
Note: concurrency: two duty toggles pressed close together now run two actuation chains as background tasks, outside PARALLEL_UPDATES and the debouncer. Both read the shared `_current_action` after boost.apply, so the last write carries the newest overlay. Same exposure as the existing step-tick writer between cycles; no defect found. Carry: dismissed: examined, converges to the newest overlay
