# BLOCKED: r10-body-contract-p3 (second dispatch, head 86f9e729f)

Reproduced: main's copy of tools/policy/field_coverage.mjs over the head tree, `--only registry`, prints

    REFUSED  registry: `pinned tools/pr/figure_block.py` is unregistered: DECLARED names neither an arm for its input nor none

The head already registers the key (field_coverage.mjs, commit 86f9e729f); the head's own copy is green. The refusal is the BASE's copy
(policy-docs restores the grader from the base), so no edit in this branch can clear it. This is the bootstrap the earlier BLOCKED
note (acb41eeef) named; the brief's task ("register it") is already done and does not change the result.

Needed from the orchestrator, none mine to take: (a) land first on main the DECLARED entry for 'pinned tools/pr/figure_block.py' with
`pending:` (the ee2974270 precedent), then this part drops `pending`; (b) accept the one-time policy-docs red; (c) stop pinning figure_block.py
(loses the governance self-test step's CI coverage). No code or body pushed.
