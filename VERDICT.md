Fix review: merge fe4af42579764bb8010e875ac5adb56ac542b3a0

bus-nonce: e4817cade2f2526a2aa14840ab5a0232

Round 2 (delta over round-1 reviewed head 815039200ac5c5e353dc918e35443eb658830125, which blocked mutation-vacuous). Head fe4af42579764bb8010e875ac5adb56ac542b3a0 = merge of main over code head 8d176a6f7; `git diff 815039200 8d176a6f7` is 34 insertions in tools/plan/replan.py's self-test only (three rows, three mutation-table rows). Reviewed from detached worktrees.

## Findings

None. The three round-1 survivors are killed, no new survivor found.

## Evidence
- Finder's harness (round-1 plants), each run on a copy of tools/plan/replan.py with `--self-test` (ev/plants.txt). Null control at 815039200: unplanted "self-test: 0 failed"; P3 (drop `plan["stamps"][-1] is not closes[0]`), P4 (accept "minor"), P5 (`round_n: int = 10`) each still print "self-test: 0 failed" (SURVIVE), so the harness fires. At the head: unplanted 0 failed; P3 KILLED by "FAIL --check refuses a round-close stamp that is not the last stamp" (its assertion looks for "expected one, and last", so it is not answered by the zero-closure or cadence arms); P4 KILLED by "FAIL --check refuses a minor stamp beside a correct round close" (row also requires no "round close" refusal, so only the stray-kind arm answers); P5 KILLED by "FAIL build_plan without round_n refuses: it planned a closure". In each case the matching mutation-table row (round-close-last, round-close-stray-kind, round-n-required) also fails on its mutant, so the table pins them.
- My own plant P6 (swap `[-1]` for `[0]`): killed at the head (stray-minor row now also reports the closure arm, plus mutation row). At 815039200 P6 was also reported killed, by the old table's anchor, not by a row for this arm.
- Rows read: (a) copies a correct round-close stamp after the last stamp; (b) inserts a minor stamp before a correct closure and requires no "round close" refusal; (c) calls build_plan without round_n and expects TypeError naming round_n. None passes for an unrelated reason.
- Still holding at the head: stamp.next_version at VERSION 10.0.0 and 11.0.0 refuses "not above the current major"; replan.closure_version refuses identically and refuses a missing round ("no round to close"); next_version('7.1.0',None,10,10) = 10.0.0 (ev/misc.txt). P1/P2 and the three body-listed mutants are killed by the unchanged self-test (0 failed at head, which runs the full table).
- Self-tests at head: replan 0 failed, plan_page 61 checks 0 failed, state_docs all passed (ev/selftests.txt). tests/structure.py: RATCHET PASSED. archscore `--diff 8fec54ee2`: dS +0.0000 NULL (ev/archscore.txt). Packet figure_lint: 15 resolved, 1 not verified (the git grep flag list), 0 refused.
- Diff is 4 files (replan.py, plan_page.py, state_docs.py, delivery row); VERSION, manifest, RELEASE_NOTES.md, goldens and claim files untouched. Role-contract diff against main empty. `git merge-tree --write-tree origin/main` exit 0, clean. carry_audit: 0 items. Forward-carry: none claimed.
- Red checks: body says none; at render and at each classify run no gate check had concluded red.
- CI: `classify` returned WAIT ("pending: gate red: none") on every run over the whole session (ev/classify.txt); codeql python, instrument-self-tests, tests/closures, coverage and fast (3.14) were still in_progress when I stopped. This verdict is therefore given with those checks unconcluded, not green. Success on the rest (mutation, arch-score, closure-scope, entities-adjacent briefs, typing) was read from the packet. Cheap checks and mutants were mine; I did not re-run the gate or mutation table.
- Not re-derived: the body's replan before/after stamp figures at roster e71a089e (round 1 reproduced them; replan.py's production code is unchanged since); prepr rc=0 is the body's claim, not re-run.
