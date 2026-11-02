Fix review: merge d56bc66d3d9d46b889e2f94f58bb352ef8a31048

bus-nonce: 8a0a8c7b691381d85f1a51d0866ae98d

## Head
Reviewed head d56bc66d3d9d46b889e2f94f58bb352ef8a31048 (round 4 delta re-check; last verdict aa6148d4ff35c457e83310337760e075cb823a14, merge). The PR body's Head section names this head.

## Findings
none

## Evidence
- review_carry.py aa6148d4 d56bc66d3d9d46b889e2f94f58bb352ef8a31048: FRESH-REVIEW (4 branch-only commits: three merges and the orchestrator.md trim). So the delta was re-reviewed, not carried.
- bus.sh conflict resolution: bash -n ok. The branch's own bus.sh delta against origin/main (three-dot) is byte-identical to its delta at aa6148d4 (header ordering comment, h2c comment, h2c commit, dispatch at $h2c); the file at this head equals the 180fd9fc3 parent. Main's P348 arms (C3-C6, vc) are present, no duplicated block (h2c defined once). bash tools/audit/seat/bus.sh --self-test: "bus self-test: 115 checks, 0 failed", so main's added signals and this branch's null control at $h2c both fire.
- git merge-tree --write-tree origin/main d56bc66d3d9d46b889e2f94f58bb352ef8a31048: rc 0 at origin/main 78dd34354e83 (main moved past the merged 0166aefd7 and still merges clean).
- Claim files: three-dot diff of tests/golden/claimed_drift.txt and card_claimed_drift.txt is empty (branch claims nothing). VERSION, manifest and RELEASE_NOTES untouched. Delivery row dev/programme/delivery/3077.md is in the three-dot diff.
- python3 tests/structure.py: STRUCTURE RATCHET PASSED. Scoped gate: MODE: SCOPED -- 2 script(s) run.
- Red checks: all 39 check-run entries read at the head; none concluded failure. The body's "Red checks: none" holds; its sentence "the new head has no runs yet" is stale wording only. Not a required-check matter and does not block.
- CI: merge_train.py classify d56bc66d3d9d46b889e2f94f58bb352ef8a31048 --pr 3077: "GREEN d56bc66d3d9d46b889e2f94f58bb352ef8a31048 pending: none red: none", rc 0.
- carry_audit at the head (packet): 4 finding items, 4 routed, 0 unrouted.
- Round: 4 of this group, a delta re-check of a merged-forward head. Round-3 checks touching the resolved hunks (bus.sh) re-run as above; no other file changed in the resolution besides the orchestrator.md trim, whose policy_lint count the body quotes (0 errors).
