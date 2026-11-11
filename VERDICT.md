Fix review: merge 9c5485e367c7ce78d54a31155d31f43f8fe9f58b

bus-nonce: 731821ba9d866aa538f8513fd035473a

## Evidence
- Scope: delta 4c24160f..9c5485e367c7ce78d54a31155d31f43f8fe9f58b. Its own commits are 03047e42 (ci: re-record handoff-push closure in tools/ci/selftest_closures.json), 9c5485e3 (tests/gate_lock.py), plus merges of origin/main. No custom_components/ line of the delta is the branch's own (they arrive via the main merges), so nothing widens the scope.
- No pull request exists, so no review packet and no CI at this head; the reds below are as the body records them at dd70a4bd0.
- Merge: `git merge-tree --write-tree origin/main 9c5485e367c7ce78d54a31155d31f43f8fe9f58b` exits 0 (tree 2b9dc9e8).
- gate_lock repair (re-run, ev/prio_cases_head.txt): at head the `priority:` cases "an urgent waiter takes before an older normal one" and "the heavy-slot pool orders by the same rule" print ok, order=['urgent','normal'], under HPO_GATE_PRIORITY=2, 1, 0 (the unset run was captured too, see the file).
- Null control (ev/null_mutant.txt): tests/gate_lock.py from 03047e42 under HPO_GATE_PRIORITY=2 gives FAIL order=['normal','urgent'] on both checks, matching the body.
- Mutation (ev/null_mutant.txt): at head, changing the urgent arm _Env("2") to _Env("0") in both functions (2 sites) under HPO_GATE_PRIORITY=2 gives FAIL on both checks. Restored; tree clean.
- python3 tests/structure.py: STRUCTURE RATCHET PASSED. tests/closure.py select against the merge base: MODE: FULL.
- Not re-derived: the handoff-push run_sha re-record in tools/ci/selftest_closures.json. selftest_scope.py check needs a strace trace dir that this seat did not produce. The diff is coherent with the body: the delivery_row.sh file and its dir entry leave the recorded closure, which matches the dropped self-test line. CI's instrument-self-tests stays the check for it.
- Body `## Red checks`: it answers tests / fast (3.14) (main's combi census, #3466), budget-raise-gate (designed refusal on the deleted proposal-triage.md key; only tvofi's review clears it) and gate. instrument-self-tests is the stale closure re-recorded at this head. The owed set also names tests / coverage-ratchet, mutation, typing and validate-hacs, none of which the body records red, and no CI run exists at this head to show otherwise.
