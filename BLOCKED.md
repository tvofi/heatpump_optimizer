# r11-pre-token-ledger: repair seat stopped before its handoff

Question: handoff/r11-pre-token-ledger is already at c892a81941. A concurrent seat handed off 2aa2169254 (body da7488bfa5), and the orchestrator added ab3ac69097 and merged main. The handoff is frozen, so this seat pushed neither handoff/ nor handoff-body/. Does the orchestrator take the two ledger_unread window-bound arms below onto the PR head (`--carry`, or a cherry-pick of 035ae800d6), or drop them?

Evidence, all measured at the named heads:

- prepr.sh (`MUTANT_IN_PLACE=1 PREPR_SKIP_CLOSURES=1`, MUTANT_CMD the check_scopes and beat_jobs self-tests) at 2aa2169254 reported 3 diff survivors. The one that is not a self-test arm is `tools/audit/check_scopes.py` `ledger_unread` CMP_BOUND, `a <= at(r["t"]) < b` changed to `a < ...`.
- On the PR head c892a81941, `check_scopes.ledger_round_self_test()` returns no false arm under either `a < ...` or `... <= b`, so both bound mutants still survive there. ab3ac69097 pins a row that predates the window, not the boundary second.
- d85e0c5ab1 (this ref's parent, on 2aa2169254) adds two arms: a seat class whose only row is at the window's first second is read, and one whose only row is at the window's end prints unread. Each arm fails on its own bound's mutant and passes at the head. `check_scopes.py --repo . --self-test` passes, and so does `tests/structure.py`.
- 035ae800d6 (this ref's second parent) is the same commit cherry-picked onto c892a81941, where it applies cleanly. Under each mutant it returns the false arm named above, and `check_scopes.py --repo . --self-test` prints `SELF-TEST passed`.
- prepr.sh at d85e0c5ab1 has rc=0. Its 2 remaining survivors are self-test-arm deletions in `self_test` (the `--round reads its token ledger` arm's assignment STMT_DEL, and the `cov.update(ledger_round_self_test())` CALL_DEL), the same category the round-1 body already dispositions under `## Unpinned sites`.
