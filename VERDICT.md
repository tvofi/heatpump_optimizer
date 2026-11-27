Fix review: merge 0f85c8a9701ee14a718d4eef7a812f33e0faca9b
bus-nonce: fb001e9569334ef7dbad9a550d146236

Measured from a detached worktree at 0f85c8a9701ee14a718d4eef7a812f33e0faca9b (base 43ec8e3273, = origin/main).
- Site gone: `return_temp is not None and np.isfinite` occurs 0 times in flow_lift.py at origin/main and at the head.
- Class open: completeness_problems over the whole inventory (8234 sites) returns 0 at the head, so no other stale pin from #3931 (or anywhere) remains; one-seam class.
- `tests/mutation_table.py --scope changed --base origin/main` at the head: MUTATION TABLE PASSED (empty scope), rc 0; ledger agrees with inventory; unpinned 1394 = 1394 at base.
- Null control: restoring the deleted JSON re-refuses with exactly the CI line (BOOLOP 04143c3f: disposition names no site the inventory generates).
- Mutation proof: no production line in the diff; the deletion is the fix, so the null control is its proof.
- VERSION, manifest version, notes heading, claim files untouched (diff: ledger JSON + delivery row only).
Note: checks-pending: prelude/cancel-superseded were still queued at review time; no red read.
