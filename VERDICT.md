Fix review: merge ab236e012dedd0c24039a4b530dcc83ebd20d3b3

bus-nonce: 3fd4a5f5f050c817eef725629e3f83dc

Round: re-check at an unchanged head (previous verdict blocked root-cause-unrecorded on codeql / Analyze (actions)).

## Evidence
- CI: merge_train.py classify at this head prints GREEN, pending none, red none (ev/classify.txt).
- codeql / Analyze (actions): the infrastructure claim holds. The head's check-runs show id 129066897216 concluding success (started 08:54:43Z, after the 08:10Z start of the sibling jobs). No required check is red.
- Only red check-run: governance / delivery-status (129066899659). It grades main and is not required (defect-root-cause.md, 2026-11-07), and the body answers it under Red checks.
- merge-tree against origin/main: rc 0, clean (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES, claim files, *_budgets.json and goldens are absent from the three-dot diff. Commit messages hold no Claude footer or trailer.
- Mutation proof, re-run by me: r10_outside_intake_p2_mutants.py prints M0 verdict=null, every mutant verdict=killed, RESULT survived=0, including state-of-kind-only (ev/mutants.txt).
- Self-tests at the head: bottleneck_check ok, roster_lib 72 checks 0 failed, merge_throughput ok. tests/entities.py prints ALL 2668 ENTITY CHECKS PASSED, matching the body.
- arch-score check-run is success (the body quotes dS +0.0000 NULL). I did not re-derive the structure and score figures locally; I rely on CI's green runs.
- carry_audit at the head (review packet): 2 routed, 0 unrouted.
- Not independently derived: the replan figures (49 vs 48 batches, 6075.0 vs 5962.5 CI minutes) depend on a roster ref at a past time and a past tree; not re-derived.

## Findings
- Residual: carry 2 (plan-page note under the Projected open issues chart: pluralise the count, drop the zero clause) stays owed, as the body states. Carry: R10-OUTSIDE-INTAKE
