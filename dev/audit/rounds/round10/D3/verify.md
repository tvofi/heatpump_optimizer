# D3 verification, round 10 (single verifier, three lenses)

**Vote basis: reasoning only** (owner ruling tvofi 2026-10-15). No test, gate or mutant re-run.
Executed number cited: intake quiet window, dev/audit/rounds/round10/QUIET.tsv (rc of full gate on each mutant):
M08 rc=0 1442 s (load1 3.99->3.86); M01 rc=0 1613 s (3.79->6.10); M03 rc=0 1654 s (6.10->3.79);
M35 rc=0 1438 s (3.79->3.05); M26 rc=0 1462 s (3.29->5.09); NULL rc=0 1520 s. thread_factor not recorded in QUIET.tsv.
Timings are provisional (concurrent seats); only rc is load-bearing.

Worktree note: audit-r10-verify-D3 already existed at 9355f107d with an uncommitted mutant in
optimizer.py:5483 (`and`->`or` on dhw_power_at_i), not mine; left untouched. Code read at HEAD lines cited.

## D3-s1-01 (coordinator.py:6522, M08) -- verify
Equivalence: not equivalent. With `or`, a non-empty prior forecast plus a live weather state now enters
the branch and overwrites it with `_fabricated_forecast(state)` (48 rows) and zeroes solar. Original keeps it.
Should a check catch it: yes, the comment states the intent ("Nothing better exists"), no test pins it; QUIET rc=0.
Reachable: any fetch that raises after one successful fetch (transient service error). Severity medium:
plan degrades from a real forecast to a constant trajectory, though already marked stale.

## D3-s1-02 (optimizer.py:5541, 5557; M01, M03) -- verify, severity low
Not equivalent: `or` indexes past the end when the optional list is shorter than power_schedule (IndexError),
and on an empty list `[] or i<0` ... short/empty both diverge. QUIET rc=0 for both. Reachability in production is
narrow: solver output normally emits equal-length schedules, so the guard is defensive; the gap is a test gap on a
live guard (12 sites), not a demonstrated field fault.

## D3-s2-01 (ledger.py:306, snapshots.py:239; M35, M26) -- verify, severity low
Not equivalent: negation suppresses the warning when records are dropped and emits "Quarantined 0" on every clean
load. Data handling unchanged; observability-only. QUIET rc=0 for both. Reachable on any corrupted store load.
Class: new (log-content pin gap), consistent with finder.
