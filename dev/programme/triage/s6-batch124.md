# Proposal triage, session s12, batch 124 (P389)

## P389: the newest `Carry:` marker for an item supersedes earlier ones

Verdict: REJECT, already delivered by `s6-batch65.md#P296`: `Carry: <dest> (item <id>, supersedes <old>)`.

Source: the orchestrator's queue line of 2026-11-04T21:43:27Z, withdrawn by the orchestrator as its own mistake.

Instances: #3185 item a2e21972. `carry_audit.py pr 3185` prints `#2259 superseded by R10-FLY-ARCHSCORE-STMT-PACKING` and 4 routed, 0 bad.

Cost: the binding cost is losing P296's guard: newest-wins would let a later marker undo a live routing, which a supersede of a valid destination is refused for today.

Binding: none.
