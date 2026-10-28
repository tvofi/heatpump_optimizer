Fix review: merge 3541137e8998aa0b2c609d4429feb37e5999140d

bus-nonce: 744dbd9b5d8b7ecc44e43aaae5d22d82

## Evidence
- Delta re-review of head 3541137e8998aa0b2c609d4429feb37e5999140d. The previous verdict was merge at 808137a94.
- The branch tip is origin/main 752f697cc, so the merge base is main's tip. The PR diff against it is 4 files, +130/-2.
- The fix files (cloud_relay.sh, INSTRUMENTS.md, the harness) match the approved diff at 808137a94. The only differences are index hashes, hunk offsets and the harness docstring wording, which main reworded in #2584. No change to the fix code.
- Every conflict resolution kept both sides: main's merge_train-N, tick_loop-N and heartbeat-N mutants sit beside cloud_relay-1..11, and the docstring takes main's wording.
- `cloud_relay.sh --self-test` prints 189 checks, 0 failed.
- RESULT survivors=0: the harness run on cloud_relay-1..11 killed each one, with the per-id failure counts the body quotes (36, 49, 2, 3, 18, 2, 1, 1, 27, 1; -1 dies on the self-test's own 'updated' file).
- `git merge-tree --write-tree origin/main` head exits 0, clean. dev/governance/roles/ has no diff since the merge base.
- `carry_audit check --body` prints 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s).
- Head check-runs on 3541137e8: nightly-status is the only red, and it is the one `## Red checks` names as main's red, not this PR's. CodeQL is neutral. The other runs were still in progress when read.
- Round 2 of re-review, so no re-cut owed.
- Not re-run, because I measured only what the delta touches: the full 80+ row harness and the gate figures the body quotes (entities, structure, etc.). I read them as the fixer's, unchanged by merges that touch neither the PR's code nor the instruments.

## Findings
- nightly-status is a red check at this head. It is main's red, not this PR's, and it is answered in the body's Red checks section. Nothing owed. Carry: dismissed: main's nightly red, answered in body Red checks
