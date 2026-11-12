Fix review: merge 071f551147a95b22b8591f2a0cb354e1fac6342f

bus-nonce: 6c07ed6c68b765570781ef215f0b598c

Round 1, handoff review before the pull request opens. Data-file deletions only (carry-1774.json, carry-201.json entry 5, three closure-table lines); no production code.

## Findings

- Owed after the merge: the body leaves carry-1645, carry-2065, carry-2066, carry-2075, carry-1922 and 23 carry-201 entries for the closeout's final pass, so the dispatch's Carry 0 control (`git ls-tree`) does not yet hold at this head; the body discloses this. Carry: dismissed: owned by the closeout preparation's later deliverables per the dispatch, disclosed in the body; no tree stage receives it from this review.

## Evidence

- No review packet and no CI exist before the pull request opens; nothing from CI is cited. Head measured: 071f551147a95b22b8591f2a0cb354e1fac6342f (ev/HEAD.txt).
- Merge: `git merge-tree --write-tree origin/main <head>` rc=0 (ev/merge-tree.txt); origin/main is now 19baca7618, ahead of the body's 6e100ef698, and merges cleanly.
- Diff re-derived against merge base 6e100ef698: 4 files, 29 deletions, none added (ev/diffstat.txt). VERSION and RELEASE_NOTES.md untouched.
- Claim "carry-1774 discharged by 4efdd6cea1": that commit adds CYCLE_HUB_WRITERS and the pre-solve plant 14_hub_write_presolve.py; tests/arch_score_head.py:48 holds CYCLE_HUB_WRITERS and tools/audit/archscore/metrics/hub_solve_writes.py:51 has ROOTS including _async_update_data, as the carry's own discharge note states. Holds.
- Claim "carry-201 entry 5 answered by 57a47dd9aa and d176dd1435": both are ancestors of the head; I did not re-derive their content or re-run prepare_baseline.sh at round 98/99. Taken from the body and the entry's own removal justification.
- Count: carry-201.json has 25 entries at the merge base and 24 at the head (len of its carries list); the body says "the other 23 entries", which the tree does not give (24 remain). Immaterial to the deletion, which is correct; the body figure is off by one and not re-derivable under any definition I tried.
- Checks run at the head: `PYTHONPATH=tests/hastub python3 tests/entities.py` exit 0; `python3 tests/layout.py` self-test ok; `node tools/policy/brief_lint.mjs` clean through its self-tests; `carry_audit.py sweep` 0 findings, 0 unrouted. No remaining reference to carry-1774.json in the tree other than tests/layout.json's historical move-map line (`since`: null), which layout.py accepts.
- Null control (deleting both carry files without the closure-table lines fails entities.py): not re-run; the head passing entities.py with the lines removed is what I measured.
- Mutation proof, claim files, budgets, structure, archscore: n/a, no production code, golden fixture, budget or score file moved. The only moved tracked figures are closures.json and selftest_closures.json lines, each a deleted path.
- Red checks: none owed (no PR, no CI). Forward-carry: body says none; the removed carries' discharge is in the tree.
