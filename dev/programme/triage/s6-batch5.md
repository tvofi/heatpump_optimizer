# Proposal triage, session s6, batch 5 (P63)

One re-ruling, S6-V4 of the s6 orchestrator's out-of-tree `proposals.md`, recurred
2026-10-24T14:07Z. Numbering continues after `s6-batch4.md` (P62). GitHub calls: 0.

## P63: two writers on one standing seat's queue across a rotation (S6-V4 recurrence)
Verdict: ACCEPT narrowed -> R10-ORCH-BEATD (owns seat liveness); carry: a generation token, `seat_gen.py bump|check`, checked by the tracked queue writers before each write
Source: s6 proposals.md S6-V4 and its 2026-10-24T14:07Z recurrence. Supersedes the DEFER in P57 (`s6-batch4.md`).
Instances: 3 independently logged (4 filed), each cited, none carried. Files are in the s6 orchestrator's out-of-tree directory `/Users/timmalmstrom/hpo-orch/r10s6/`; counts re-taken 2026-10-24T14:40Z.
- Dispatch w14/w15, two live writers: `grep -n 'w14 stopped' seat-ledger.md` prints line 93 (14:07:45Z, "two-writer V4 recurrence"); `grep -n 'V4 recurrence 2026-10-24T14:07:45Z' proposals.md` prints line 86 (w14 reported completion with work live, w15 started).
- Merge w3/w4, two live writers: `grep -n 'merge w3' seat-ledger.md` prints line 92 (14:06:36Z, "merge w3 ended after train s11 ... w4 started") and line 94 (14:11:33Z, "merge w3 stopped (lingering)"). The ledger says "stopped"; it does not name the stop tool, so no TaskStop is claimed here.
- Earlier V4, filed with 2 instances: `grep -n '^- V4 two writers' proposals.md` prints line 64 (roster w5/w6; the #2698 fixer against an update). Only the #2698 one is corroborated in the ledger: `grep -n '#2698: I did not fire the repair fixer' seat-ledger.md` prints line 86 (the local update_pr stays the single writer). The roster w5/w6 overlap rests on the filing alone, so it is not counted; this is why 3 and not 4.
Cost: S -- one small script with a self-test, a `check` call in each tracked writer.
Binding: a barrier is owed at three instances. The proposed seat-rotate helper that kills the old task is rejected: killing a seat is an agent-tool action, not scriptable from a shell, so the helper would be prose. A generation token binds the superseded seat itself. Null control: the current generation passes `check`.
