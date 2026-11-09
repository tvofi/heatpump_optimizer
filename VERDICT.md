Fix review: merge 62f90fcb3bd8a45775642d290bf86b3274cb040d

bus-nonce: b13ae49b9ed8f643e6efc43803dd6ff9

Round: later round. Scope per the owner ruling: the delta from the previous reviewed head aff9f1393aec11bc0f5fc745d34a9161c09b695a to 62f90fcb3bd8a45775642d290bf86b3274cb040d, the previous verdict's finding, and the live check state.

## Evidence

- The delta since aff9f139 is main merges plus the base shift. The PR's own three-dot diff against origin/main is identical at aff9f139 and at the head (+/- lines compared, only hunk offsets and index hashes differ; ev/pr-diff-delta.txt). The PR diff touches no file under custom_components/ (ev/custom_components-stat.txt), so no production code of the PR is at risk and no wider review was owed.
- Previous verdict (merge at aff9f139, probe rev-3304-46157511): its one finding, the record-sweep `self.critical` latency follow-up at merge_train.py, was carried with a dismissal in that verdict; the code it concerns is unchanged in the PR diff, so it is neither reopened nor re-reported.
- `git merge-tree --write-tree origin/main 62f90fcb3bd8a45775642d290bf86b3274cb040d`: clean, rc 0 (ev/merge-tree.txt).
- Live checks at the head: `merge_train.py classify` printed RED, pending none, red: gate. The review packet lists reds on gate, tests / fast (3.14) and pr-contract; every other context is green or skipped.
- The red is inherited from main, not this PR's. tests / fast (3.14) failed in two units: tests/entities.py (3 failures, all de.json: key parity and the two flow-field labels for options.entities.sections.indoor flow_heat_c / flow_min_lift_k) and tests/harness_headers.py (dev/audit/rounds/round4/D6/claims.py claims_true 122 not 123, claims_false 1 not 0, and its output drifting). I re-ran both at origin/main 2f6d699e5 in a separate worktree: the same three entities failures and the same claims_true=122 / claims_false=1 (ev/main-fails.txt against ev/head-fails.txt). The de.json failure is the one #3378 fixes. gate is the roll-up of that red. pr-contract failed on the packet's red-unanswered refusal for tests / fast (3.14); it follows from the inherited red, not from the PR's body or code. Per the CI settle ruling none of these blocks this PR.
- Figures: the body's counts are per-head snapshots; the packet's figure_lint shows 5 resolved, 1 not verified (tiers.py, a one-off fixture the body discloses). I did not rebuild them. The PR code is unchanged since the previous round, whose mutants and self-tests I ran then.

## Findings

- Residual: main's own red (tests/fast: the de.json parity and labels, and the D6 claims count 122 true / 1 false against the header's 123 / 0) is reproduced at origin/main, not at this PR; it must clear before the train merges this PR. Carry: dismissed: inherited from main and outside this PR's diff; the merge train's classify reads the head again when it merges
