Fix review: merge 419fd6d2c455601cebe473bd1b8ec77e0090daa0

bus-nonce: 1b06e6d6000af7cef1034da0f115336d

## Summary

Round 1 (first review; full scope). Reviewed from a detached worktree at 419fd6d2c455601cebe473bd1b8ec77e0090daa0, merge base 646352ff1364bcbc25875b949072f98e7a53b5fe. Every production line the body names, deleted alone, fails the self-test with the count the body states. CI on this head is GREEN. The head merges cleanly with current origin/main e0ad8b2bd3.

## Findings

- Equivalent survivor M9 (my own mutant, not in the body): dropping `rc == 0 and` from `outside_contract`'s admission predicate in `tools/audit/seat/merge_pr.sh` leaves `merge_pr self-test: 50 checks, 0 failed`. It is equivalent under the current contract: the only line `tools/pr/outside.py` emits starting `OUTSIDE: ` is at outside.py:446, inside its `return 0` statement, so no rc-1 answer can carry it. The conjunct is defence in depth and mirrors `Train.outside_contract`'s predicate (merge_train.py:2741). Carry: dismissed: equivalent mutant, because outside.py:446 is the only `OUTSIDE: ` line and it is emitted only with rc 0

## Evidence

- RESULT head self-tests (ev/head-*.txt): `merge_train self-test: 825 checks, 0 failed`, `merge_pr self-test: 50 checks, 0 failed`, `outside self-test: 266 checks, 0 failed`, `queue_pre_flight self-test: 57 checks, 0 failed`. All four match the body's figures.
- RESULT mutation proof (ev/mutants.txt, ev/mut-*.txt/.log, driver ev/mutant-driver.sh). Each mutant was applied alone at the head:
  - M1 `fork_head` compare→`pass`: 3 failed.
  - M2 `land` fork guard→`if False:`: 1 failed.
  - M3 merge_pr `outside_contract` call→`:`: 4 failed.
  - M4 drop `at {sha}` predicate: 1 failed.
  - M5 `outside_is_mains outside`→`:`: 4 failed.
  - M6 `outside_is_mains contract`→`:`: 2 failed.
  - M7 drop `[ "$want" = "$have" ]`: 6 failed.
  - Every count and FAIL name from M1 to M7 matches the body's Mutation proof.
  - These mutants are my own and not in the body:
    - M8 (admit a fork head in owner mode): 1 failed.
    - M10 (treat every unadmitted head as cross-repository): 1 failed.
    - M9 survived, as equivalent (see Findings).
- Null control. M1 and M2 restore each production line's merge-base behaviour, and each makes the new cases FAIL. The null-control cases ("a head of ours ... never asks the contract", "head of ours on a batch/ base ... is merged") pass at the head. I did not re-run the body's base-tree runs, which use the new tests on the old code. The count `825 checks, 4 failed` at the merge base is the body's figure and was not re-derived.
- Class rule, step 6 (ev/class-rule.txt). I ran the body's `git grep -n "outside\.py" -- '*.sh' '*.py' '*.mjs' '*.yml' '*.js'` less outside.py's own lines: 80 lines in 9 files.
  - Sites that execute outside.py: bus.sh adopt (main's throwaway checkout, `MAIN-COPY-RAN` case); policy_lint.mjs (the base's copy); governance.yml (self-test only); merge_train.py and merge_pr.sh (closed in this diff).
  - The other hits (tests.yml, pr-contract.yml, queue_pre_flight.py:508, remerge_main.sh:16) are comments and execute nothing.
  - No open seam.
- Merge with main (ev/merge-tree.txt): `git merge-tree --write-tree origin/main 419fd6d2c4` exits 0, tree 2a759890c8. No conflict, and no claim file is touched.
- CI (ev/classify.txt): `GREEN 419fd6d2c455601cebe473bd1b8ec77e0090daa0 pending: none red: none`. No red check, so no `## Red checks` answer is owed; the body's `none` is correct.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff. No claim drift is owed.
- Step 7: the body's head 419fd6d2c4 equals the live `refs/pull/3619/head` read before this verdict.
- Step 14 (figures not re-derived):
  - `tools/ci/selftest_closures.json` adds `tools/policy/policy_lint.mjs` and `tools/pr/outside.py` to merge-train's `files`. That widens selection, the conservative direction. I did not re-record it: an strace recording is the fixer's and CI's lane.
  - Structure ratchet, archscore `dS +0.0000` and the closure selftest are cited from CI's green `gate` and `arch-score`, not re-run (tvofi 2026-09-30).
- Step 10, forward carries. The body's two items carry to the PR's own group, R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3, on origin/handoff/audit-r10-roster. carry_audit reports both resolved. They are status lines on the group's existing carries:
  - The live fork checks are the group's roster carries 2 and 8. A seat without an App key, `gh` or a fork pull request cannot run them.
  - The decision-0017 text is owner policy: roster carry 7 says "not written by a fixer". That is the fixer.md exception for a pending owner ruling.
  - So this is not `carry-missing: own-group`.
- Policy currency: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
