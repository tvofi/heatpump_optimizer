Fix review: merge a3f7c328d826430776c61b036551a21c3c08bfe2

bus-nonce: 20b2c34720b00d4029c0007235f83abd

RESULT delta: 67b8659d..a3f7c328d826430776c61b036551a21c3c08bfe2 is 3 added files, 18 insertions, all under tests/mutation_ledger/killed_by/ledger.py/; no code, test or body change.
RESULT pins: three MonthlyLedger._coverage_factor pins (BOOLOP, CMP_BOUND covering 2 sites, GUARD_OFF) = the four ledger.py:328 sites the body lists under Unpinned sites; each "old" line matches ledger.py:328 at the head. killed_by is tests/features.py, which exists and carries the PR's new coverage tests (diff 4a3cbcf6..67b8659d adds 39 lines there). Pin reasons were recorded by --pin-killed at ratchet base 4a3cbcf6, an ancestor of the head.
RESULT mutation_table: tests/mutation_table.py --scope changed --max 0 at the head exits 0, MUTATION TABLE PASSED (empty pool), ledger agrees with the inventory.
RESULT merge-tree: git merge-tree --write-tree origin/main a3f7c328d826430776c61b036551a21c3c08bfe2 exits 0, no conflicts.
RESULT ci: 59 check-runs at the head, none red; 8 pending (in_progress): coverage x2, fast (3.14) x2, Analyze (python) x2, mutation x2. The body's ## Red checks answers mutation (predicted red until the pin commit, which this delta is); it says no other check has run, so the other pending ones have no red to answer. Pending mutation must go green on this pin head; the merge gate must wait for it.
Round: delta review after round-1 pass (probe/rev-2463-c275b564).
