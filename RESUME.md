# RESUME: R10-DIAG-REPLAY round 2 (PR #2399)

- Round 1's `Fix review:` blocked on two counts. Both are answered.
- **carry-missing.** The D15 forward-carry is in `R10-BRIEFS-FOLD`'s `carry` list on `handoff/audit-r10-roster` at `2020978559ef37e9e22ae0926a5f685622da65f5` (`roster_edit.py append-carry`, fast-forward from `9a487b73`). Read back from origin byte for byte. `brief_lint.mjs` from an `origin/main` checkout prints `TOTAL: 0 error(s)` with rc 0. The roster branch's own copy of `brief_lint.mjs`, run on its own tree, reports one error in `R10-SCORES` (`coordinator.py:10281` anchor); it is there with or without this carry, and main's linter does not report it.
- **CodeQL.** `ff914f548` makes the three `replay_doc` leak checks' details count instead of echo (`_unrecorded`); conditions unchanged, MA to MD still red, planted credentials in FAIL lines 1/1/2/1 to 0/0/0/0. The alert is neither dismissed nor suppressed.
- Code head `ff914f548f3eda308b02d3834913319c1155f766` on `handoff/r10-diag-replay` (fast-forward from `f32ad027`). It merges `origin/main` at `07a09406`, no conflict. `prepr.sh` on the branch checkout: `PRE-PR` rc 0, ancestry reds all answered.
- The PR branch itself was not pushed; moving it is the orchestrator's.
