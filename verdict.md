Fix review: merge d2877bb236f0b79ceb4e8a6b21143e2b12a42f41

bus-nonce: 5a0522f2a36303fea9089b1981d3b0c3

## Evidence
- RESULT delta: head tree f8d794aa9d9327c0ead0896c1149341d58e1335b is byte-identical to the tree of `git merge-tree --write-tree a361e454 043b111d` (the approved head merged with main). No production line is authored on top of the merge; the only branch-only commit is the main merge d2877bb23.
- RESULT merge-tree: `git merge-tree --write-tree origin/main d2877bb236f0b79ceb4e8a6b21143e2b12a42f41` exits 0, no conflict (origin/main 043b111d). Driver notes: LEDGER-MERGE resolved tests/closures.json (inert_reads merged as a set).
- RESULT claim file: tests/golden/claimed_drift.txt at head is byte-identical to a361e454's (sha1 b666993f); main's side is unchanged since the merge base, so the three-way result is the branch's own claim set (five coord_* R10-COP-GATE claims, six may-drift entries restored). card_claimed_drift.txt is identical on all three. `env_drift.py --check` at the head worktree exits 0: "NO STALE FIXTURE: 5 committed fixture(s) still match"; five coord_* claims report "not captured in this mode" (unjudged), the same as at a361e454.
- review_carry.py prints FRESH-REVIEW because it keys on "resolves claimed_drift.txt to other than the union of the parents"; that is the branch's own prior resolution (commit 3f33c6796 message), which the approved a361e454 already carried, not new content. Hence this delta review.
- RESULT VERSION: 7.0.5 at main, a361e454 and head; VERSION, manifest and notes heading untouched.
- CI at head (check-runs API): gate success (both runs), pr-contract success, arch-score success, budget-raise-gate success, tests fast/closures/coverage/replay/typing/browser/arch-instrument/lane-proofs success, CodeQL success; skipped jobs are the scoped-out ones. No red check, so no root-cause answer is owed.
- Not re-run: the full gate and mutation table (cited from CI per the role). The mutation proof of the substantive fix was reviewed at a361e454 and the head adds no production change.
