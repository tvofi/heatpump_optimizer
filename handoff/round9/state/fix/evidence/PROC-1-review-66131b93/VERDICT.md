Fix review: merge 66131b936db4c55a4c7fbc7da931f0d8a7c97ddb

PR #1818, R9-PROC-1, round 2. Delta judged only: git diff 5aaef98e 66131b93 (orchestrator.md only; delta_5aaef98e_66131b93.patch). Round 1 is PROC-1-review-5aaef98e.

- The round-1 block is closed. orchestrator.md section 11 again requires "CI green at a head containing current origin/main: if main moved, merge it in (a carry or resolution delta) and wait". That is the barrier fix-review.md step 11 held at 90335cbd. It now sits with the carry rule, which governs the verdict after that merge.
- The cut that pays for it is section 0's "*Coordinator* is coordinator.py". No other line in orchestrator.md at 66131b93 uses the word "coordinator", and fixer.md:99 still carries the disambiguation, so nothing is lost.
- The background-task CI watch survives, merged into the new bullet with the fixer.md reference.
- Cheap checks at 66131b93: policy_lint `TOTAL: 0 error(s) across 40 policy file(s)`; policy_lint --budgets rc 0; brief_lint rc 0; git merge-tree against origin/main is clean.
- CI on the PR head is cited, not re-run; the orchestrator merges on it green. The Mac's delivery row commit (e63b9884) on the PR head is outside this review.
