# merge-3872: stopped on orchestrator STOP (CMD 1) and NOTE (CMD 2)

Question: none -- superseded by local fixer

- Stopped after the merge commit, before the gate: the scoped gate, structure.py and brief_lint were NOT run.
- Nothing pushed to handoff/r11-owner-fault-hold or any fix/ branch.
- Merge of origin/main 6a58ba5cb3 into d6a54399a6, committed unpushed-to-handoff as 98864c6f06c432961a4a1ad11f85f024696d2002
  (this ref's parent), for reuse if wanted; its message lists the resolution per conflicted file.
  Resolution delta: d6a54399a63b76d43c4f3a84e1d2ac518da28ed0..98864c6f06c432961a4a1ad11f85f024696d2002
- Semantic point a reuser should judge: main's #3812 moved the unload baseline-row write out of
  pump_arbiter.release into off_restore's _release_row, which off_restore runs before AND after
  coordinator shutdown (where fault_hold.release drops the latch). The branch's "a faulted pump takes no
  row" guard is therefore carried in _release_row: held -> spent unwritten at "unload", owed otherwise.

## Observed about the superseding head (fact, measured 2026-11-25T10:16:50Z)
- handoff/r11-owner-fault-hold = 79265fe95b. git merge-base --is-ancestor d6a54399 79265fe95b: false
  (merge-base e3cb5c019b); its main parent is 5594a34a49, and origin/main is now 6a58ba5cb3
  (not an ancestor), so main has since landed #3875, #3868, #3887, #3738 (solve_gate.py), #3877, #3871, #3889, #3888.
  Its D6 count of 102 modules predates solve_gate.py; at 6a58ba5cb3 plus fault_hold.py, claims.py measures 103.
