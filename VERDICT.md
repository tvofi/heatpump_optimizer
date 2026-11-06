Fix review: merge 6bca687e48b8fe68ddb49ca0bac866add51e1078

bus-nonce: 6af5145a0cf1f9dfab324bb71e470cc2

## Round

Round 2 of the fix review of #3249 (R10-DISPATCH-AT-HANDOFF), at head 6bca687e48b8fe68ddb49ca0bac866add51e1078 (handoff code 5c85b096 merged into the PR). Round 1 blocked 520550ce, mutation-vacuous: bus-14, `select(.status != "completed")` -> `select(true)`. Detached worktree at the head; dev/governance/roles/ is unchanged between the merge base and origin/main.

## Evidence

- RESULT mutation: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py bus-1 ... bus-16 review_packet-own` at the head: 17 of 17 KILLED, RESULT survivors=0 (ev/mutants.txt). bus-14, round 1's mutant, is now KILLED: bus self-test 149 checks, 2 failed. bus-10 3, bus-11 1, bus-13 3, bus-15 1, bus-16 1 failed, and review_packet-own 2 failed. Each matches the body's figures.
- Null control: the harness runs the unmutated step before it plants any mutant, and it marks a mutant NOT RUN if that run fails. No mutant was NOT RUN, so bus.sh --self-test (149 checks) and review_packet.py --self-test (69 checks) pass at the head.
- The self-test now exercises the status filter: the HPO_BUS_CHECKS stub prints check-run JSON, and jq's `select(.status != "completed")` runs on it (a completed job dispatches, and an in_progress or queued job holds with rc 3). A failed read prints the "NOT checked" line and proceeds, which keeps the 2026-10-24 ruling that dispatch never waits for CI.
- bus-7 (a pre-existing mutant from the base) is KILLED with rc 1. Its tail line is a git usage message, not the self-test summary, so the self-test probably died rather than failed a check. A mutant that crashes the self-test still reddens it, so it counts as killed.
- Merge: `git merge-tree --write-tree origin/main 6bca687e48b8fe68ddb49ca0bac866add51e1078` exits 0 against origin/main 862affd0 (tree 5c9b0afa).
- Untouched: custom_components/, VERSION, RELEASE_NOTES.md, every *_budgets.json and tests/closures.json are absent from the three-dot diff. The delivery row dev/programme/delivery/3249.md is in the diff.
- Carries: `carry_audit.py landed` prints CARRY-LANDED: 0 missing (ev/carry-landed.txt). The roster entry (origin/handoff/audit-r10-roster) has 16 carries, and the body's 1-based numbers map onto them: 3 is P344, the autofix hold; 6 is card 3; 14 is P368; 15 is P354; 16 is P374. Every unbuilt carry is named under Forward-carry.
- CI: `merge_train.py classify 6bca687e48b8fe68ddb49ca0bac866add51e1078 --pr 3249` returns GREEN, pending: none, red: none (rc 0). The head has 68 check-runs, all completed: 43 success and 25 skipped (ev/check-runs.tsv). The previous head 520550ce also has 43 success and 25 skipped and no red. So the body's `## Red checks: none` holds at this head.
- Head: the body's `## Head` names 6bca687e48b8fe68ddb49ca0bac866add51e1078, which is the head I measured.
