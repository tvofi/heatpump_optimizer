R10-COP-GATE fixer (cloud seat, resumed) state

Part 1 (topic r10-cop-gate): code head 309f44882 on handoff/r10-cop-gate.
- 718768025 merges origin/main beb570c81 (no conflicting hunk; ledger driver
  merged structure_budgets.json and closures.json).
- a90db5e2b merges the PR head d4ec6fcce (tree-identical), so fix/r10-cop-gate fast-forwards.
- 309f44882 fixes tests/finite_boundary.py's MeasuredCop.record seed (the fast (3.14) red;
  coverage-ratchet's store.py 93.28 % follows from it).
- Owed after the push: mutation-autofix pins (its earlier skip-measure-failed was the red
  finite_boundary baseline). A local --pin-killed at 309f44882 was still running at handoff;
  no pins committed. The reviewer re-checks `## Red checks`' mutation line once the bot pins.
- Not re-taken: the owner-bundle arms of r10_cop_gate.py and owner_rows.py (bundle not on this seat).

Part 2 (topic r10-cop-gate-p2): unchanged from the previous RESUME; not touched by this seat.
