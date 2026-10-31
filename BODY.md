R10-ORCH-REVIEW-PACKET: the open carries of the packet seam (9, 10, 11, 12, 13 of the prompt; roster indexes 10-14 below).

## Head

df25f62e476f63eed3722f0a69c373f18c975447

## Mutation proof

Mutants added to dev/audit/harnesses/r10_seat_selftests_mutants.py, run with `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py review_packet-6 through review_packet-15`: all KILLED, survivors=0.

## Null control

Each signal has its null in the self-test: a branch that cannot be read prints today's head-note refusal with no command; a verdict whose notes are all routed gives carry_audit rc 0; a body citing no carry as landed passes; the same carry once landed passes; nightly-status stays owed for a workflow diff.

## Figures

- `python3 tools/audit/seat/review_packet.py --self-test` -> 0 failed.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py review_packet-6 review_packet-7 review_packet-8 review_packet-9 review_packet-10 review_packet-11 review_packet-12 review_packet-13 review_packet-14 review_packet-15` -> RESULT survivors=0.
- `node tools/policy/policy_lint.mjs --budgets` -> fix-review.md within its cap (paid by cutting the #290 harness clause and the re-measure sentence).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> ALL ENTITY CHECKS PASSED; `python3 tests/structure.py` -> PASSED. Scope: SCOPED, entities.py. origin/main unmoved (7539d1675) since the work started.

## Approval

Pending: this diff edits dev/governance/roles/fix-review.md, which is policy. It merges only on tvofi's approving review or the mandate in force; it is not self-approved.

## Red checks

none

## Forward-carry

- Carry 1: landed. Carry: dismissed: already landed by #2870, nothing to carry
- Carry 2: landed. Carry: dismissed: already landed by #2870, nothing to carry
- Carry 3: landed. Carry: dismissed: already landed by #2870, nothing to carry
- Carry 4: landed. Carry: dismissed: already landed by #2870, nothing to carry
- Carry 5: dispatch-at-handoff, see Carry 6. Carry: R10-ORCH-REVIEW-PACKET
- Carry 6: dispatch at the handoff ref (prompt carries 4 and 5) is NOT built here; it re-keys the topic record in open_pr.sh, adds a relay that posts a held verdict, and edits standing-dispatch.md and fix-review.md step 7, with no sound cut inside this group's scope. Stopped for the orchestrator. Carry: R10-ORCH-REVIEW-PACKET
- Carry 7: handoff-not-applied landed by #2939. Carry: dismissed: already landed by #2939, nothing to carry
- Carry 8: brief-carries landed by #2939. Carry: dismissed: already landed by #2939, nothing to carry
- Carry 9: the relay-format statement (P200) is already in fix-review.md line 7. Carry: dismissed: already in the tree, nothing to carry
- Carry 10: closing self-audit step in the packet and one fix-review sentence (P275), built here. Carry: dismissed: built in this diff
- Carry 11: the red-path mutants (prompt carries 10 and 13), built here. Carry: dismissed: built in this diff
- Carry 12: head-note repair (prompt carry 11), built here. Carry: dismissed: built in this diff
- Carry 13: carry-landed refusal at dispatch and at the handoff, built here; body_push.sh already runs ci_predict.py and prepr --fill-red/--body-check before the push. The before/after count of mechanical block classes over the next 10 verdicts is owed after merge. Carry: R10-ORCH-REVIEW-PACKET
- Carry 14: the harness additions are owed to this group and done. Carry: dismissed: built in this diff

## Friction

none
