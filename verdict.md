Fix review: merge 95ad6344e2c5507975b6c154d04065be4ecce059

bus-nonce: 3fa1ebd6ecd60a833a7b71ba8d6a8c1d

## Evidence

- Round: first review of this head. Reviewed head 95ad6344e2c5507975b6c154d04065be4ecce059 (ev/HEAD.txt), from a detached worktree; the body's `## Head` names it.
- State on GitHub: this head already reached main through #3445 (merged 2026-11-11T17:52Z, PR head 206a0ee1c6 = this head plus an automatic main merge). The dispatch said no pull request exists; that was stale. `git merge-tree --write-tree origin/main 95ad6344e2c5507975b6c154d04065be4ecce059`: exit 0, and the head is an ancestor of origin/main.
- No review packet and no CI were waited on, per the dispatch (handoff review). Red checks: none read for this head; `merge_train.py owed-reds` prints tests / mutation, tests / typing, validate / validate-hacs.
- Diff a7628041dc..95ad6344e2c5507975b6c154d04065be4ecce059: tools/audit/seat/review_packet.py only (+131/-32). VERSION, the manifest and RELEASE_NOTES.md are untouched (empty diff). There are no golden or claim files in the diff, so env_drift was not run: a tools-only diff cannot move solver fixtures.
- Figures re-derived at the head: `review_packet self-test: 108 checks, 0 failed`; `body_patch self-test: 109 checks, 0 failed`; the body_patch `MUTANT --commits-file dropped` line is present (Carry 4); the trailer grep over a7628041dc..HEAD gives 0. Not re-derived: the `prepr.sh` EXIT 0 figure (heavy gate, not re-run per fix-review step 11), and the fixer's /tmp/mut.out, which I replaced with my own driver.
- Mutation proof (my own driver, ev/mut_driver.py, output in ev/mutants.txt): the core logic of every carry fails the self-test when mutated. Killed: M1 1-based range (5 failed), M2 live-only count (1), M3 round-scope dropped (1), M4 no tip ancestry (2), M5 no head ancestry (1), M6 WAIT/GREEN skip dropped (2), M7 REQUIRED scope dropped (1), M8 GREEN dropped (1), M9 PROMPT line anchor dropped (2). Null control (docstring edit): survived, 0 failed.
- Live end-to-end, which the self-test does not cover: `dispatch_prompt('r10-review-dispatch-residue-p4')` reads the real PROMPT and returns carries [4, 15, 16, 18, 19]. `roster_lib.round_ref` resolves to origin/handoff/audit-r10-roster. `review_packet.py handoff --topic r10-review-dispatch-residue-p4 --body BODY.md` prints `R10-REVIEW-DISPATCH-RESIDUE at 95ad6344e2c5, 31 live, 5 dispatched carries, 0 refused`. Under the old live-count rule the same run would demand 31 carries, so carry 15's wiring works in practice.
- Class: each carry is one seam, and the body names no enumeration rule. Carry 18 is dismissed as superseded by 19, and the diff confirms 19's change covers it. Forward-carry: none claimed and none owed.
- Architecture: the change stays inside review_packet.py. It adds no new write path, and `gather` adds no second classify call.

## Findings

- Four wiring mutants survive the self-test. M10: `dispatch_prompt` always returns None. M11: `gather` drops the snapshot advisory. M12: `gather` passes no round topic. M13: `handoff()` uses the live count. Each one would make a carry's fix inert in production while the self-test stays green. They do not block: the decision functions are killed, the live run above shows the M10 and M13 paths working, and `gather`'s git/gh I/O was already untested at the base. A self-test seam over `handoff()` and `gather` would close the gap. Carry: dismissed: I/O wiring, proven by the live end-to-end run in Evidence; the head already merged as #3445
