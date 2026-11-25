# RESUME: R11-OWNER-FAULT-HOLD merge repair (PR #3872, topic merge-fault-hold)

- Code: handoff/r11-owner-fault-hold at 0c8d0bd41e6ba209371052fb874129d2ec1cbc1a, the merge of origin/main 91773476edb3 into the PR head 3c89b84f7bd8 (taken from mm/3872, per orchestrator NOTE 2).
- Measured there: structure.py PASSED (every metric at its budget); entities.py ALL 2766 PASSED; harness mutants=41 survived=0; scoped gate 31 scripts, all pass (stress and harness_headers re-run directly after a lease-label fault); ci_predict: no red, 42 unpinned sites listed under ## Unpinned sites.
- Resolution delta: git diff 3c89b84f7bd8 0c8d0bd41e6b.
- Next: the orchestrator updates the PR from the handoff ref.
