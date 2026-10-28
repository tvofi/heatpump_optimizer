# Proposal triage, session s6, batch 5 (P63)

One re-ruling, S6-V4 of the s6 orchestrator's out-of-tree `proposals.md`, recurred
2026-10-24T14:07Z. Numbering continues after `s6-batch4.md` (P62). GitHub calls: 0.

## P63: two writers on one standing seat's queue across a rotation (S6-V4 recurrence)
Verdict: ACCEPT narrowed -> R10-ORCH-BEATD (owns seat liveness); carry: a generation token, `seat_gen.py bump|check`, checked by the tracked queue writers before each write
Source: s6 proposals.md S6-V4 and its 2026-10-24T14:07Z recurrence. Supersedes the DEFER in P57 (`s6-batch4.md`).
Instances: 3 (roster w5/w6; the #2698 fixer against an update; dispatch w14/w15, where w14 reported completion with background work still live). Orchestrator's account; not re-counted from logs.
Cost: S -- one small script with a self-test, a `check` call in each tracked writer.
Binding: a barrier is owed at three instances. The proposed seat-rotate helper that kills the old task is rejected: killing a seat is an agent-tool action, not scriptable from a shell, so the helper would be prose. A generation token binds the superseded seat itself. Null control: the current generation passes `check`.
