Fix review: merge 06a3478fdbf386278952d741985e5da5ee28bd5c

bus-nonce: 3c4a0045147c80113970455bcfc1bfc1

## Evidence
- Round 1 for this seat. Head measured: 06a3478fdbf386278952d741985e5da5ee28bd5c (ev/HEAD.txt); CI classify: GREEN, pending none, red none. delivery-status was red in the digest but is not a required check (defect-root-cause.md).
- Merge: git merge-tree --write-tree origin/main HEAD exit 0 (LEDGER-MERGE: resolved tests/closures.json). Main changed fix-review.md since the merge base (8 lines); it still merges cleanly.
- Self-tests re-run: survivor_list --self-test 20 checks, 0 failed; bus.sh --self-test 162 checks, 0 failed.
- Mutants (all restored, tree clean): (1) removing the survivor_list call from push_verdict fails the bus self-test "push-verdict refuses a mutation-vacuous verdict naming one of two survivors"; (2) breaking the CLASS regex fails "a verdict naming one of two is refused"; (3) dropping the whole-token lookbehind fails the two token-boundary checks.
- No VERSION, manifest, RELEASE_NOTES or golden/claim file in the three-dot diff. closures.json adds only survivor_list.py to the measured closure.
- Finder's harness: none named. This is a governance and instrument change, so the null control is the other-class pass in the self-test, which I confirmed present.
- Policy file fix-review.md is edited: it needs the owner's approving review at merge (CLAUDE.md), which follows this verdict.
- carry_audit at head: 0 finding items. No red required check, so no root-cause answer is owed.
